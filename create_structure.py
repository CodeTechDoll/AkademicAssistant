import os
import json


def create_structure(structure, parent=''):
    for category, subcategories in structure.items():
        os.makedirs(os.path.join(parent, category), exist_ok=True)
        for subcategory in subcategories:
            if isinstance(subcategory, str):
                subcategory_dir = os.path.join(parent, category, subcategory)
                os.makedirs(subcategory_dir, exist_ok=True)
                
                metadata_path = os.path.join(subcategory_dir, "_metadata.json")
                if not os.path.exists(metadata_path):
                    with open(metadata_path, "w") as metadata_file:
                        json.dump({}, metadata_file, indent=2)
            elif isinstance(subcategory, dict):
                create_structure(subcategory, os.path.join(parent, category))


with open("structure_metadata.json", "r") as structure_file:
    metadata = json.load(structure_file)
    structure = metadata["structure"]

create_structure(structure)
