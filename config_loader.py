import json
import os

class ConfigLoader:
    def __init__(self, config_path="data/real_estate_config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading configuration: {str(e)}")

    def get_real_estate_types(self):
        """Get list of all real estate types."""
        return list(self.config["real_estate_types"].keys())

    def get_documents_for_type(self, real_estate_type):
        """Get list of documents for a specific real estate type."""
        return list(self.config["real_estate_types"][real_estate_type]["documents"].keys())

    def get_keywords_for_document(self, real_estate_type, document_type):
        """Get keywords for a specific document type."""
        return self.config["real_estate_types"][real_estate_type]["documents"][document_type]["keywords"]

    def save_config(self):
        """Save current configuration back to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"Error saving configuration: {str(e)}")

    def add_real_estate_type(self, type_name):
        """Add a new real estate type."""
        if type_name not in self.config["real_estate_types"]:
            self.config["real_estate_types"][type_name] = {"documents": {}}
            self.save_config()

    def add_document_type(self, real_estate_type, document_name, keywords=None):
        """Add a new document type to a real estate type."""
        if keywords is None:
            keywords = []
        self.config["real_estate_types"][real_estate_type]["documents"][document_name] = {
            "keywords": keywords
        }
        self.save_config()

    def update_keywords(self, real_estate_type, document_type, keywords):
        """Update keywords for a specific document type."""
        self.config["real_estate_types"][real_estate_type]["documents"][document_type]["keywords"] = keywords
        self.save_config() 