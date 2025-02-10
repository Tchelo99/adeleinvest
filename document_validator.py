import pytesseract
from pdf2image import convert_from_path
import docx2txt
import os
from PIL import Image
from typing import List, Dict, Set
import json
from datetime import datetime
import platform
import tempfile
import io

class DocumentValidator:
    def __init__(self, config):
        # Set Tesseract path based on environment
        if platform.system() == 'Windows':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # On Linux/Cloud, Tesseract is installed in the standard location
        
        self.config = config
        self.history_file = "validation_history.json"

    def extract_text(self, uploaded_file):
        # Get file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        try:
            if file_extension in ['.jpg', '.jpeg', '.png']:
                image = Image.open(uploaded_file)
                text = pytesseract.image_to_string(image, lang='fra')
            elif file_extension == '.pdf':
                # Create a temporary file to save the uploaded PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    pdf_path = tmp_file.name
                
                try:
                    # Convert PDF to images
                    pages = convert_from_path(pdf_path)
                    text = ""
                    for page in pages:
                        text += pytesseract.image_to_string(page, lang='fra')
                finally:
                    # Clean up the temporary file
                    os.unlink(pdf_path)
                
            elif file_extension == '.docx':
                # For docx files, we need to read the bytes
                text = docx2txt.process(io.BytesIO(uploaded_file.getvalue()))
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
            return text.lower()
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

    def validate_document(self, uploaded_file, real_estate_type, document_type):
        try:
            # Extract text from document
            extracted_text = self.extract_text(uploaded_file)
            
            # Get keywords for document type
            keywords = self.config.get_keywords_for_document(real_estate_type, document_type)
            
            # Check for keywords - document is valid if at least one keyword is found
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in extracted_text:
                    found_keywords.append(keyword)
            
            # Document is valid if at least one keyword is found
            is_valid = len(found_keywords) > 0
            
            # Create result
            result = {
                "timestamp": datetime.now().isoformat(),
                "filename": uploaded_file.name,
                "real_estate_type": real_estate_type,
                "document_type": document_type,
                "is_valid": is_valid,
                "found_keywords": found_keywords
            }
            
            # Save to history
            self.save_validation_result(result)
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

    def save_validation_result(self, result):
        try:
            # Load existing history
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Add new result
            history.append(result)
            
            # Save updated history
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error saving validation result: {str(e)}") 