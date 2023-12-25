
## Overview

This project is a full stack Flask application designed for extracting details from Thai ID cards using Optical Character Recognition (OCR) with Tesseract. The extracted information is stored in a MongoDB database, and the application supports CRUD (Create, Read, Update, Delete) operations for managing the extracted data.

## Demo Video : https://youtu.be/ddkTwp9J1M4

## Demo 

Demo Video Link -  https://youtu.be/ddkTwp9J1M4

Live Link : https://okk-dpew.onrender.com/ ( Worked Perfectly on Local host, Slow Render upon Hosting upon Render , So please refer Demo Video)

## Features

- **OCR with Tesseract:** Utilizes Tesseract for extracting text details from Thai ID cards.
- **MongoDB Integration:** Stores the extracted information in a MongoDB database for efficient data management.
- **CRUD Operations:**
  - **Create:** Add new ID card details to the database.
  - **Read:** Fetch and display ID card details from the database.
  - **Update:** Modify existing data in the database.
  - **Delete:** Remove ID card details from the database.


## Data Extraction

Thai ID National Card : https://drive.google.com/file/d/1FlJOmAEVPkURgWvYomIr9iVjfKEn-hIW/view?usp=sharing


First it is uploaded through the frontend 

<img width="960" alt="image_upload" src="https://github.com/araj6523/OCR/assets/108401537/f76dfe5e-9016-4833-ba00-e750f12c99fb">

Then Accurate Results are shown :

<img width="960" alt="insert_result" src="https://github.com/araj6523/OCR/assets/108401537/71955d34-f56b-43a6-92e1-b026d2704de8">

Through POST Method , It is Stored in our MongoDB Database

<img width="755" alt="Mongo_db_insert" src="https://github.com/araj6523/OCR/assets/108401537/69c12e8e-7de3-4fcc-a093-3f31c830cf75">


 ## Instructions

1. Clone the repository:

   ```bash
   git clone 
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up Tesseract OCR:

   Follow the Tesseract installation guide for your operating system: [Tesseract Installation Guide](https://github.com/tesseract-ocr/tesseract).

4. Configure MongoDB:

   - Install MongoDB and set up a database.
   - Update the MongoDB connection settings in the `config.py` file.

5. Run the application:

   ```bash
   python app.py
   ```

   The application will be accessible at `http://localhost:5000`.


## Demo


<img width="960" alt="image_upload" src="https://github.com/araj6523/OCR/assets/108401537/f76dfe5e-9016-4833-ba00-e750f12c99fb">

<img width="950" alt="insert_image_selection" src="https://github.com/araj6523/OCR/assets/108401537/b8afb136-04f9-4c5a-9092-64a6466081c8">

<img width="960" alt="insert_result" src="https://github.com/araj6523/OCR/assets/108401537/71955d34-f56b-43a6-92e1-b026d2704de8">
<img width="755" alt="Mongo_db_insert" src="https://github.com/araj6523/OCR/assets/108401537/69c12e8e-7de3-4fcc-a093-3f31c830cf75">
<img width="944" alt="Fetch_by_id" src="https://github.com/araj6523/OCR/assets/108401537/8fd1250c-77fd-4250-b85e-2017c8caabef">
<img width="960" alt="fetch_result" src="https://github.com/araj6523/OCR/assets/108401537/1490338d-5f56-4f1b-92a8-5b8bba6e3ca8">
<img width="945" alt="update_input" src="https://github.com/araj6523/OCR/assets/108401537/301e7226-796a-47ee-9071-4fa497eb7993">
<img width="959" alt="update_output" src="https://github.com/araj6523/OCR/assets/108401537/5d09a1b4-3c80-4dd4-bad6-95b05fbc714f">
<img width="960" alt="delete_input" src="https://github.com/araj6523/OCR/assets/108401537/400ef530-37ee-4acf-b92f-233912b19e05">

## Technologies Used

- **Flask:** A micro web framework for building the application.
- **Tesseract:** An OCR engine for extracting text from images.
- **MongoDB:** A NoSQL database for storing and managing the extracted data.

## API Endpoints


-The API provides the following routes:

/api/ocr:
POST: Create a new OCR record.

GET: Retrieve all OCR records with optional filtering by identification number.

PUT: Update an existing OCR record.

DELETE: Delete an OCR record by ID.

/api/ocr/:id:
GET: Retrieve a specific OCR record by ID.

## Usage

1. Access the application in your web browser.

2. Upload an image of a Thai ID card to perform OCR and extract details.

3. Use the CRUD operations to manage the extracted data.

## Configuration

Update the configuration settings in the `config.py` file to match your environment and preferences.

```python
# config.py

MONGO_URI = 'mongodb://localhost:27017/your-database-name'
SECRET_KEY = 'your-secret-key'
```

## Contribution

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
