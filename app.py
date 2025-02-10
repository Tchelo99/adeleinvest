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
                
                # Show extracted text
                st.subheader("Extracted Text")
                if result.get("extracted_text"):
                    st.text_area("", result["extracted_text"], height=300)
                else:
                    st.write("No text extracted")

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
        
        # Configuration Management
        st.title("Configuration")
        if st.checkbox("Show Configuration Management"):
            st.subheader("Add New Real Estate Type")
            new_type = st.text_input("New Real Estate Type")
            if st.button("Add Type") and new_type:
                config.add_real_estate_type(new_type)
                st.success(f"Added {new_type}")
            
            st.subheader("Add New Document Type")
            selected_type = st.selectbox(
                "Select Real Estate Type",
                config.get_real_estate_types()
            )
            new_doc = st.text_input("New Document Name")
            new_keywords = st.text_input("Keywords (comma-separated)")
            if st.button("Add Document") and new_doc and new_keywords:
                keywords_list = [k.strip() for k in new_keywords.split(",")]
                config.add_document_type(selected_type, new_doc, keywords_list)
                st.success(f"Added {new_doc} to {selected_type}")

if __name__ == "__main__":
    main() 