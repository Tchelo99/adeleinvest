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
    
    # Initialize config loader
    config = ConfigLoader()
    
    # Initialize validator with config
    validator = DocumentValidator(config)
    
    # Sidebar for history
    st.sidebar.title("Validation History")
    if st.sidebar.button("Show History"):
        history = load_validation_history()
        for result in history:
            with st.sidebar.expander(f"{result['filename']} - {result['timestamp']}"):
                st.write(f"Real Estate Type: {result['real_estate_type']}")
                st.write(f"Document Type: {result['document_type']}")
                st.write(f"Valid: {'✅' if result['is_valid'] else '❌'}")
    
    # Main form
    with st.form("validation_form"):
        # Real estate type selection
        real_estate_type = st.selectbox(
            "Select Real Estate Type",
            options=config.get_real_estate_types()
        )
        
        # Document type selection (dependent on real estate type)
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
                
                # Show details
                with st.expander("See Validation Details"):
                    if result["found_keywords"]:
                        st.write("Found Keywords:")
                        for keyword in result["found_keywords"]:
                            st.write(f"✅ {keyword}")
                    else:
                        st.write("❌ No matching keywords found")
                    
                    # Show extracted text for debugging
                    with st.expander("Show Extracted Text"):
                        st.text(result.get("extracted_text", "No text extracted"))

    # Add configuration management section
    if st.sidebar.checkbox("Show Configuration Management"):
        st.sidebar.subheader("Configuration Management")
        
        # Add new real estate type
        new_type = st.sidebar.text_input("New Real Estate Type")
        if st.sidebar.button("Add Real Estate Type") and new_type:
            config.add_real_estate_type(new_type)
            st.sidebar.success(f"Added {new_type}")
            
        # Add new document type
        selected_type = st.sidebar.selectbox("Select Real Estate Type for New Document", 
                                           config.get_real_estate_types())
        new_doc = st.sidebar.text_input("New Document Name")
        new_keywords = st.sidebar.text_input("Keywords (comma-separated)")
        if st.sidebar.button("Add Document") and new_doc and new_keywords:
            keywords_list = [k.strip() for k in new_keywords.split(",")]
            config.add_document_type(selected_type, new_doc, keywords_list)
            st.sidebar.success(f"Added {new_doc} to {selected_type}")

if __name__ == "__main__":
    main() 