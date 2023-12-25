from ocr1 import PersonalCard
from main import Card1

img_path = 'C:/Users/SONAKSH/Desktop/ocr/dataset/example2.jpeg'
rea = Card1(path_to_img=img_path)
res = rea.inputocr()
rea.convert_json(res)
print(res)