#! /usr/bin/python

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from ocr1 import PersonalCard 
from main import Card1 # Assuming the OCR script is in the same directory
import os
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from pymongo import MongoClient
import certifi
from bson import json_util
import json
from bson import ObjectId



app = Flask(__name__)

# Configure MongoDB connection
'''
app.config['MONGO_URI'] = 'mongodb+srv://20ucc024:9w4B8V15AemtNxcA@cluster0.zee8wmt.mongodb.net/'
#mongo = PyMongo(app)
mongo = PyMongo(app, ssl_cert_reqs=False)
db_name = 'OCR_APP'
collection_name = 'AGR'

# Additional error handling
if not mongo.cx:
    raise ValueError("MongoDB connection failed. Check your URI.")
if db_name not in mongo.cx.list_database_names():
    raise ValueError(f"Database '{db_name}' not found.")
if collection_name not in mongo.cx[db_name].list_collection_names():
    raise ValueError(f"Collection '{collection_name}' not found in database '{db_name}'.")

# Access the specific collection within the specified database
collection = mongo.cx[db_name][collection_name]
'''
mongo_client = MongoClient('mongodb+srv://20ucc024:9w4B8V15AemtNxcA@cluster0.zee8wmt.mongodb.net/',tlsCAFile =certifi.where())  
#mongo_client = MongoClient('mongodb+srv://20ucc024:9w4B8V15AemtNxcA@cluster0.zee8wmt.mongodb.net/')
db = mongo_client['OCR_APP']
collection = db['AGR']

UPLOAD_FOLDER = 'ocr'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if request.method == 'POST':
        # Access the uploaded file from the request
        uploaded_file = request.files['image_upload']

        # Check if the file is empty
        if uploaded_file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Ensure the upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save the file to the upload folder
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)
        result = extract_information(file_path)
        #update_record_in_mongo(result, identification_number, new_full_name)


        return render_template('result.html', result=result)


        #return render_template('result.html', result=result)

def extract_information(image_path):
    #img_path = 'C:/Users/SONAKSH/Desktop/ocr/dataset/example2.jpeg'
    rea = Card1(path_to_img=image_path)
    res = rea.inputocr()
    result=rea.convert_json(res)
    #print(res)
    return result

@app.route('/api/data', methods=['GET'])
def get_data_by_identification_number():
    identification_number = request.args.get('identification_number')
    data = collection.find_one({'identification_number': identification_number})
    if data:
        #return jsonify(json_util.dumps(data))
        data_dict = json_util.loads(json_util.dumps(data))
        
        # Convert ObjectId to string to make it JSON serializable
        for key, value in data_dict.items():
            if isinstance(value, ObjectId):
                data_dict[key] = str(value)

        # Beautify the JSON string with an indent of 2
        beautified_json = json.dumps(data_dict, indent=2)
        return jsonify(beautified_json)
    else:
        return jsonify({'message': 'Data not found'}), 404

# Update Operation
@app.route('/api/data/<string:identification_number>', methods=['PUT'])
def update_data(identification_number):
    #identification_number = request.args.get('identification_number')
    data = collection.find_one_and_update(
        {'identification_number': identification_number},
        {'$set': {'name': request.json['name'],
        'date-of-birth': request.json['date-of-birth'],
        'date-of-issue': request.json['date-of-issue'],
        'date-of-expiry': request.json['date-of-expiry']}},
        return_document=True
    )
    if data:
        return jsonify(json_util.dumps(data))
    else:
        return jsonify({'message': 'Data not found'}), 404

# Delete Operation
@app.route('/api/data/<string:identification_number>', methods=['DELETE'])
def delete_data(identification_number):
    result = collection.delete_one({'identification_number': identification_number})
    if result.deleted_count > 0:
        return jsonify({'message': 'Data deleted successfully'})
    else:
        return jsonify({'message': 'Data not found'}), 404


    '''
    # Assuming 'ocr1.py' is in the same directory
    

    # Replace this path with your Tesseract OCR installation path
    tesseract_cmd = "C:/Users/SONAKSH/AppData/Local/Programs/Tesseract-OCR/tesseract"

    # Initialize the OCR reader
    reader = PersonalCard(lang="mix", tesseract_cmd=tesseract_cmd)

    # Extract information from the image
    result = reader.extract_front_info(image_path)

    return result
'''
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
