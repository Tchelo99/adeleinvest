import streamlit as st
from document_validator import DocumentValidator
from config_loader import ConfigLoader
import json

def load_validation_history():
    try:
        with open("validation_history.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def main():
    st.title("Real Estate Document Validator")
    
    # Initialize config loader and validator
    config = ConfigLoader()
    validator = DocumentValidator(config)
    
    # Main form
    with st.form("validation_form"):
        # Real estate type selection
        real_estate_type = st.selectbox(
            "Select Real Estate Type",
            options=config.get_real_estate_types()
        )
        
        # Document type selection
        document_type = st.selectbox(
            "Select Document Type",
            options=config.get_documents_for_type(real_estate_type)
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=['pdf', 'png', 'jpg', 'jpeg', 'docx']
        )
        
        # Submit button
        submit_button = st.form_submit_button("Validate Document")
    
    # Handle validation
    if submit_button and uploaded_file is not None:
        with st.spinner('Validating document...'):
            result = validator.validate_document(
                uploaded_file,
                real_estate_type,
                document_type
            )
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                # Show results
                if result["is_valid"]:
                    st.success("Document Validated Successfully! ✅")
                else:
                    st.error("Document Validation Failed ❌")
                
                # Show keywords
                st.subheader("Found Keywords")
                if result["found_keywords"]:
                    for keyword in result["found_keywords"]:
                        st.write(f"✅ {keyword}")
                else:
                    st.write("❌ No matching keywords found")

    # Sidebar for history
    with st.sidebar:
        st.title("Validation History")
        if st.button("Show History"):
            history = load_validation_history()
            for result in history:
                st.write("---")
                st.write(f"File: {result['filename']}")
                st.write(f"Type: {result['real_estate_type']}")
                st.write(f"Document: {result['document_type']}")
                st.write(f"Status: {'✅ Valid' if result['is_valid'] else '❌ Invalid'}")

if __name__ == "__main__":
    main() 