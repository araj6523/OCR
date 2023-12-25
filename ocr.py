from collections import namedtuple
import re
import os
import cv2
import sys
import yaml
import base64, binascii
import numpy as np
import pytesseract
import easyocr
from PIL import Image
from pathlib import Path
from enum import Enum
import cv2
import numpy as np


class Language(Enum):
    THAI = 'tha'
    ENGLISH = 'eng'
    MIX = 'mix'

    def __str__(self):
        return self.value


class Provider(Enum):
    EASYOCR = 'easyocr'
    TESSERACT = 'tesseract'
    DEFAULT = 'default'

    def __str__(self):
        return self.value

class Card(Enum):
    FRONT_TEMPLATE = 'front'
    BACK_TEMPLATE = 'back'

    def __str__(self):
        return self.value


def convertScale(img, alpha, beta):
    """Add bias and gain to an image with saturation arithmetics. Unlike
    cv2.convertScaleAbs, it does not take an absolute value, which would lead to
    nonsensical results (e.g., a pixel at 44 with alpha = 3 and beta = -210
    becomes 78 with OpenCV, when in fact it should become 0).
    """

    new_img = img * alpha + beta
    new_img[new_img < 0] = 0
    new_img[new_img > 255] = 255
    return new_img.astype(np.uint8)


# Automatic brightness and contrast optimization with optional histogram clipping
def automatic_brightness_and_contrast(image, clip_hist_percent=25):
    gray = image

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum / 100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size - 1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    auto_result = convertScale(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)

def remove_horizontal_line(image):
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Remove horizontal
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (255, 255, 255), 2)
    # Repair image
    repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 6))
    result = 255 - cv2.morphologyEx(255 - image, cv2.MORPH_CLOSE, repair_kernel, iterations=1)
    return result

def remove_dot_noise(image):
    _, blackAndWhite = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, None, None, None, 4, cv2.CV_32S)
    sizes = stats[1:, -1]  # get CC_STAT_AREA component
    img2 = np.zeros((labels.shape), np.uint8)

    for i in range(0, nlabels - 1):
        if sizes[i] >= 8:  # filter small dotted regions
            img2[labels == i + 1] = 255
    res = cv2.bitwise_not(img2)
    kernel = np.ones((3, 3), np.uint8)
    res = cv2.erode(res,kernel, iterations=1)
    return res
	
from google.colab.patches import cv2_imshow
class PersonalCard:
    def __init__(self,
                 lang: Language = Language.MIX,
                 provider: Provider = Provider.DEFAULT,
                 template_threshold: float = 0.7,
                 sift_rate: int = 25000,
                 save_extract_result: bool = False,
                 path_to_save: str = None):

        self.lang = lang
        self.provider = provider
        self.root_path = self._get_root_path()
        self.template_threshold = template_threshold
        self.image = None
        self.save_extract_result = save_extract_result
        self.path_to_save = path_to_save
        self.index_params = dict(algorithm=0, tree=5)
        self.search_params = dict()
        self.good = []
        self.cardInfo = {
            "mix": {
                "Identification_Number": "",
                "FullNameTH": "",
                "PrefixTH": "",
                "NameTH": "",
                "LastNameTH": "",
                "PrefixEN": "",
                "NameEN": "",
                "LastNameEN": "",
                "BirthdayTH": "",
                "BirthdayEN": "",
                "Religion": "",
                "Address": "",
                "DateOfIssueTH": "",
                "DateOfIssueEN": "",
                "DateOfExpiryTH": "",
                "DateOfExpiryEN": "",
                "LaserCode": "",
            },
            "tha": {
                "Identification_Number": "",
                "FullNameTH": "",
                "PrefixTH": "",
                "NameTH": "",
                "LastNameTH": "",
                "BirthdayTH": "",
                "Religion": "",
                "Address": "",
                "DateOfIssueTH": "",
                "DateOfExpiryTH": "",
                "LaserCode": "",
            },
            "eng": {
                "Identification_Number": "",
                "PrefixEN": "",
                "NameEN": "",
                "LastNameEN": "",
                "BirthdayEN": "",
                "Religion": "",
                "Address": "",
                "DateOfIssueEN": "",
                "DateOfExpiryEN": "",
                "LaserCode": "",
            }
        }


        if save_extract_result == True:
            if path_to_save == None or path_to_save == "":
                raise ValueError("Please define your path to save extracted images.")

        self.flann = cv2.FlannBasedMatcher(self.index_params, self.search_params)
        self.sift = cv2.SIFT_create(sift_rate)

        if str(provider) == str(Provider.EASYOCR) or str(provider) == str(Provider.DEFAULT):
            self.reader = easyocr.Reader(['en', 'th'], gpu=True)
        self.__loadSIFT()
        self.h, self.w, *other = self.source_image_front_tempalte.shape

    def __loadSIFT(self):
        self.source_image_front_tempalte = self.__readImage('/content/sample_data/datasets/identity_card/personal-card-template.png')
        #self.source_image_back_tempalte = self.__readImage(os.path.join(
            #self.root_path, 'content/sample_data/datasets', 'identity_card/personal-card-back-template.jpg'))
        self.source_front_kp, self.source_front_des = self.sift.detectAndCompute(self.source_image_front_tempalte, None)
        #self.source_back_kp, self.source_back_des = self.sift.detectAndCompute(self.source_image_back_tempalte, None)
        with open(os.path.join(self.root_path, 'content/sample_data', 'datasets/config.yaml'), 'r') as f:
            try:
                self.roi_extract = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise ValueError(f"Can't load config file {exc}.")

    def __readImage(self, image=None):
        try:
            try:
                # handler if image params is base64 encode.
                img = cv2.imdecode(np.fromstring(base64.b64decode(image, validate=True), np.uint8), cv2.IMREAD_COLOR)
            except binascii.Error:
                # handler if image params is string path.
                img = cv2.imread(image, cv2.IMREAD_COLOR)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if img.shape[1] > 1280:
                scale_percent = 60  # percent of original size
                width = int(img.shape[1] * scale_percent / 100)
                height = int(img.shape[0] * scale_percent / 100)
                dim = (width, height)
                img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            return img
        except cv2.error as e:
            raise ValueError(f"Can't read image from source. cause {e.msg}")

        
        
    def __compareTemplateSimilarity(self, queryDescriptors, trainDescriptors):
        self.good = []
        matches = self.flann.knnMatch(queryDescriptors, trainDescriptors, k=2)
        for x, y in matches:
            if x.distance < self.template_threshold * y.distance:
                self.good.append(x)


    def __findAndWrapObject(self, side: Card = Card.FRONT_TEMPLATE):
        if len(self.good) > 30:
            processPoints = np.float32([self.process_kp[m.queryIdx].pt for m in self.good]).reshape(-1, 1, 2)
            sourcePoints = None
            if str(side) == str(Card.FRONT_TEMPLATE):
                sourcePoints = np.float32([self.source_front_kp[m.trainIdx].pt for m in self.good]).reshape(-1, 1, 2)
            
            M, _ = cv2.findHomography(processPoints, sourcePoints, cv2.RANSAC, 5.0)
            self.image_scan = cv2.warpPerspective(self.image, M, (self.w, self.h))
        else:
            self.image_scan = self.image

        if self.save_extract_result:
            cv2.imwrite(os.path.join(self.path_to_save, 'image_scan.jpg'), self.image_scan)


    def __extractItems(self, side: Card = Card.FRONT_TEMPLATE):
        for index, box in enumerate(
                self.roi_extract["roi_extract"][str(side)] if str(self.lang) == str(Language.MIX) else filter(
                    lambda item: str(self.lang) in item["lang"],
                    self.roi_extract["roi_extract"])):
            imgCrop = self.image_scan[box["point"][1]:box["point"][3], box["point"][0]:box["point"][2]]
            imgCrop = cv2.adaptiveThreshold(imgCrop[:,:,0], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 8) + cv2.adaptiveThreshold(imgCrop[:,:,1], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 8) + cv2.adaptiveThreshold(imgCrop[:,:,2], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 8)

            if str(side) == str(Card.BACK_TEMPLATE):
                imgCrop = remove_dot_noise(imgCrop)

            if str(self.provider) == Provider.DEFAULT.value:
                if str(box["provider"]) == str(str(Provider.EASYOCR)):
                    self.cardInfo[str(self.lang)][box["name"]] = " ".join(str.strip(
                        "".join(self.reader.readtext(imgCrop, batch_size=4 ,detail=0, paragraph=False , width_ths=1.0, blocklist=box["blocklist"]))).split())
                elif str(box["provider"]) == str(Provider.TESSERACT):
                    self.cardInfo[str(self.lang)][box["name"]] = str.strip(
                        " ".join(pytesseract.image_to_string(imgCrop, lang=box["lang"].split(",")[0],
                                                             config=box["tesseract_config"])
                                 .replace('\n', '')
                                 .replace('\x0c', '')
                                 .replace('-', '')
                                 .replace('"', '')
                                 .replace("'", '')
                                 .split()))
            elif str(self.provider) == str(Provider.EASYOCR):
                self.cardInfo[str(self.lang)][box["name"]] = " ".join(str.strip(
                    "".join(self.reader.readtext(imgCrop, batch_size=4 ,detail=0, paragraph=False , width_ths=1.0, blocklist=box["blocklist"]))).split())
            elif str(self.provider) == str(Provider.TESSERACT):
                self.cardInfo[str(self.lang)][box["name"]] = str.strip(
                    " ".join(pytesseract.image_to_string(imgCrop, lang=box["lang"].split(",")[0],
                                                         config=box["tesseract_config"])
                             .replace('\n', '')
                             .replace('\x0c', '')
                             .replace('-', '')
                             .replace('"', '')
                             .replace("'", '')
                             .split()))

            if self.save_extract_result:
                Image.fromarray(imgCrop).save(os.path.join(self.path_to_save, f'{box["name"]}.jpg'), compress_level=3)

        if str(self.lang) == str(Language.MIX) and str(side) == str(Card.FRONT_TEMPLATE):
            extract_th = self.cardInfo[str(self.lang)]["FullNameTH"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixTH"] = str("".join(extract_th[0]))
            self.cardInfo[str(self.lang)]["NameTH"] = str(
                "".join(extract_th[1] if len(extract_th) > 2 else extract_th[-1]))
            self.cardInfo[str(self.lang)]["LastNameTH"] = str("".join(extract_th[-1]))

            extract_en = self.cardInfo[str(self.lang)]["NameEN"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixEN"] = str("".join(extract_en[0]))
            self.cardInfo[str(self.lang)]["NameEN"] = str("".join(extract_en[1:]))
        elif str(self.lang) == str(Language.THAI) and str(side) == str(Card.FRONT_TEMPLATE):
            extract_th = self.cardInfo[str(self.lang)]["FullNameTH"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixTH"] = str("".join(extract_th[0]))
            self.cardInfo[str(self.lang)]["NameTH"] = str(
                "".join(extract_th[1] if len(extract_th) > 2 else extract_th[-1]))
            self.cardInfo[str(self.lang)]["LastNameTH"] = str("".join(extract_th[-1]))
        elif str(self.lang) == str(Language.ENGLISH) and str(side) == str(Card.FRONT_TEMPLATE):
            extract_en = self.cardInfo[str(self.lang)]["NameEN"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixEN"] = str(extract_en[0])
            self.cardInfo[str(self.lang)]["NameEN"] = str(extract_en[1:])

        if str(side) == str(Card.BACK_TEMPLATE):
            self.cardInfo[str(self.lang)]["LaserCode"] = "".join(re.findall("([a-zA-Z0-9])",self.cardInfo[str(self.lang)]["LaserCode"])).upper()

        _card = namedtuple('Card', self.cardInfo[str(self.lang)].keys())(*self.cardInfo[str(self.lang)].values())
        return _card


    def extract_front_info(self, image):
        self.image = self.__readImage(image)
        self.process_kp, self.process_des = self.sift.detectAndCompute(self.image, None)
        self.__compareTemplateSimilarity(self.process_des, self.source_front_des)
        self.__findAndWrapObject(Card.FRONT_TEMPLATE)
        return self.__extractItems()
    def _get_root_path(self):
        # Get the directory of the current script or notebook
      return os.path.abspath(os.path.join(os.getcwd(), os.pardir))


reader = PersonalCard(lang="mix") # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.
result = reader.extract_front_info('/content/sample_data/datasets/identity_card/KXa2NPVvXF278Wr6gTR.jpg')
print(result)



import json

# Convert to JSON
json_data = json.dumps(required_info, ensure_ascii=False, indent=2)

print(json_data)

import json
import string
from datetime import datetime

def remove_punctuation(text):
    # Function to remove punctuation from a given text
    translator = str.maketrans("", "", string.punctuation)
    return text.translate(translator)

def map_keys(data):
    key = "date-of-birth"
    key_mapping = {
        "Identification_Number": "identification_number",
        "FullName": "name",
        "BirthdayEN": "date-of-birth",
        "DateOfIssueEN": "date-of-issue",
        "DateOfExpiryEN": "date-of-expiry"
    }

    # Function to format date string
    def format_date(date_str):
        # Remove punctuation and extra spaces from the date string
        cleaned_date_str = remove_punctuation(date_str)
        try:
            # Try parsing the date with the format "day month, year"
            dt = datetime.strptime(cleaned_date_str, "%d %b, %Y")
        except ValueError:
            # If the first format fails, try the format "day month year."
            dt = datetime.strptime(cleaned_date_str, "%d %b %Y")
        return dt.strftime("%d/%m/%Y")

    # Map keys, format date strings, remove punctuation, and convert to JSON
    dt = datetime.strptime(original_data["BirthdayEN"], "%d %b, %Y")
    mapped_data = {key_mapping[key]: format_date(value) if "Date" in key else value for key, value in data.items()}
    if key == "date-of-birth":
        mapped_data["date-of-birth"] = dt.strftime("%d/%m/%Y")
    return mapped_data

original_data = {
    "Identification_Number": "1103700593021",
    "FullName": "MissPalalee Worasirl",
    "BirthdayEN": "21 Sep, 1991",
    "DateOfIssueEN": "23 Oct, .2021",
    "DateOfExpiryEN": "20 Sep. 2020."
}

# Map keys, format date strings, remove punctuation, and convert to JSON
mapped_data = map_keys(original_data)
json_data = json.dumps(mapped_data, ensure_ascii=False, indent=2)

print(json_data)

import pymongo

db = client['OCR_APP']  # Update with your database name
collection = db['Thai_ID']

try:
    # Add timestamp and success message to the data
    json_data['timestamp'] = datetime.utcnow()
    json_data['success_message'] = "Data inserted successfully"

    # Insert the data into the collection
    result = collection.insert_one(json_data)

    # Print the ID of the inserted document
    print("Inserted ID:", result.inserted_id)

except Exception as e:
    print("Error:", str(e))

	
	