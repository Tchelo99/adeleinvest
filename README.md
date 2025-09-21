# Real Estate Document Validator

This is a Streamlit web application designed to validate real estate documents based on predefined configurations. It allows users to upload various document types (PDF, PNG, JPG, DOCX, XLSX) and verifies them against a configurable set of required keywords for different real estate and document types.

## Features

- **Document Validation**: Upload and validate real estate documents.
- **Multiple File Types**: Supports PDF, PNG, JPG, DOCX, and XLSX files.
- **Dynamic Configuration**: Easily configure real estate types, document types, and associated keywords through a JSON file.
- **Validation History**: View a history of past validations.
- **Configuration Management**: Add new real estate types and document types directly from the user interface.

## Project Structure

```
/
|-- app.py                  # Main Streamlit application
|-- config_loader.py        # Handles loading and managing the configuration
|-- document_validator.py   # Performs the document validation
|-- requirements.txt        # Python dependencies
|-- data/
|   |-- real_estate_config.json # Configuration file for real estate and document types
|-- validation_history.json # Stores the history of validations
```

## Setup and Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

3. **Access the Application**:
   Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

## How It Works

- **`app.py`**: The main application file that creates the Streamlit interface, handles file uploads, and displays validation results.
- **`config_loader.py`**: The `ConfigLoader` class loads and manages the configuration from `data/real_estate_config.json`. This file defines the different real estate types and the required documents and keywords for each.
- **`document_validator.py`**: The `DocumentValidator` class validates the uploaded documents. It uses `pytesseract` for Optical Character Recognition (OCR) to extract text from the files and checks for the presence of the required keywords based on the loaded configuration.

## Technologies Used

- **Streamlit**: For creating the web application interface.
- **pytesseract**: For Optical Character Recognition (OCR) to extract text from images and PDFs.
- **pdf2image**: To convert PDFs into images for processing.
- **python-docx**: To extract text from `.docx` files.
- **pandas**: To extract text from `.xlsx` and `.xls` files.