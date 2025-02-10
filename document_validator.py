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
                # For images, read bytes directly
                image_bytes = uploaded_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                # Reset file pointer for potential reuse
                uploaded_file.seek(0)
                # Try multiple languages
                text = pytesseract.image_to_string(image, lang='fra+eng')
                
            elif file_extension == '.pdf':
                # Save PDF content to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_path = tmp_file.name
                
                try:
                    # Set poppler path based on environment
                    if platform.system() == 'Windows':
                        poppler_path = r'C:\Program Files\poppler-0.68.0\bin'
                    else:
                        # On Linux/Cloud, poppler is in the standard location
                        poppler_path = '/usr/lib/x86_64-linux-gnu'

                    # Convert PDF to images with higher DPI
                    pages = convert_from_path(
                        tmp_path,
                        dpi=300,  # Higher DPI for better quality
                        grayscale=True,  # Convert to grayscale for better OCR
                        poppler_path=poppler_path if platform.system() == 'Windows' else None
                    )
                    text = ""
                    for page in pages:
                        # Enhance image before OCR
                        page = self._enhance_image(page)
                        # Try multiple languages
                        text += pytesseract.image_to_string(
                            page,
                            lang='fra+eng',  # Use both French and English
                            config='--psm 1 --oem 3'  # Use more accurate OCR mode
                        )
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                
            elif file_extension == '.docx':
                docx_bytes = uploaded_file.read()
                uploaded_file.seek(0)
                text = docx2txt.process(io.BytesIO(docx_bytes))
                
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
            return text.lower()
            
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

    def _enhance_image(self, image):
        """Enhance image quality for better OCR results."""
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')
        
        # Increase contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Optional: Add more image processing here if needed
        return image

    def validate_document(self, uploaded_file, real_estate_type, document_type):
        try:
            # Extract text from document
            extracted_text = self.extract_text(uploaded_file)
            
            # Get keywords for document type
            keywords = self.config.get_keywords_for_document(real_estate_type, document_type)
            
            # Check for keywords with more flexible matching
            found_keywords = []
            for keyword in keywords:
                # Convert both to lower case
                keyword_lower = keyword.lower()
                # Remove accents for comparison
                keyword_normalized = self._normalize_text(keyword_lower)
                text_normalized = self._normalize_text(extracted_text)
                
                # Try different variations of the keyword
                if (keyword_lower in extracted_text or 
                    keyword_normalized in text_normalized or
                    keyword_lower.replace(' ', '') in extracted_text.replace(' ', '') or
                    keyword_lower.replace('-', '') in extracted_text.replace('-', '')):
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
                "found_keywords": found_keywords,
                "extracted_text": extracted_text  # Optional: for debugging
            }
            
            # Save to history
            self.save_validation_result(result)
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

    def _normalize_text(self, text):
        """Remove accents and special characters for more flexible matching."""
        import unicodedata
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

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