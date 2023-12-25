from ocr1 import PersonalCard
import json
from pymongo import MongoClient
import certifi
import json
import os
class Card1:
    def __init__(self,path_to_img: str = None):
        self.path_to_img = path_to_img
    def inputocr(self):
        reader = PersonalCard(lang="mix", tesseract_cmd="C:/Users/SONAKSH/AppData/Local/Programs/Tesseract-OCR/tesseract")
        #print(reader.root_path)
        #print(os.path.join(reader.root_path, 'ocr\dataset', 'template.png'))
        #reader = PersonalCard(lang="mix", tesseract_cmd="C:/Users/SONAKSH/AppData/Local/Programs/Tesseract-OCR/tesseract") 
        #result = reader.extract_front_info('C:/Users/SONAKSH/Desktop/ocr/dataset/example2.jpeg')
        result = reader.extract_front_info(self.path_to_img)
        return result
    def convert_json(self,result):
        #result=self.res
        required_info = {
            "Identification_Number": result.Identification_Number,
            "FullName": result.PrefixEN+ result.NameEN + ' ' + result.LastNameEN,
            "BirthdayEN": result.BirthdayEN,
            "DateOfIssueEN": result.DateOfIssueEN,
            "DateOfExpiryEN": result.DateOfExpiryEN
        }
        print(required_info)

        #print(required_info)
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

        json_data = json.loads(json_data)
        

        
        
        # MongoDB connection details
        mongo_client = MongoClient('mongodb+srv://20ucc024:9w4B8V15AemtNxcA@cluster0.zee8wmt.mongodb.net/',tlsCAFile =certifi.where())  
        #mongo_client = MongoClient('mongodb+srv://20ucc024:9w4B8V15AemtNxcA@cluster0.zee8wmt.mongodb.net/')
        db = mongo_client['OCR_APP']
        collection = db['AGR']

        # Read JSON file

        # Insert JSON data into MongoDB
        collection.insert_one(json_data)

        print("JSON data successfully pushed to MongoDB.")
        
        return json_data
       


