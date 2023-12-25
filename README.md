# Thai ID Card Details Extraction Full Stack Flask Application

## Overview

This project is a full stack Flask application designed for extracting details from Thai ID cards using Optical Character Recognition (OCR) with Tesseract. The extracted information is stored in a MongoDB database, and the application supports CRUD (Create, Read, Update, Delete) operations for managing the extracted data.

## Features

- **OCR with Tesseract:** Utilizes Tesseract for extracting text details from Thai ID cards.
- **MongoDB Integration:** Stores the extracted information in a MongoDB database for efficient data management.
- **CRUD Operations:**
  - **Create:** Add new ID card details to the database.
  - **Read:** Fetch and display ID card details from the database.
  - **Update:** Modify existing data in the database.
  - **Delete:** Remove ID card details from the database.

## Technologies Used

- **Flask:** A micro web framework for building the application.
- **Tesseract:** An OCR engine for extracting text from images.
- **MongoDB:** A NoSQL database for storing and managing the extracted data.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/thai-id-card-extraction.git
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

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
