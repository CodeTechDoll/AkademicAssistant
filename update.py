import os
import json
import mistune

# Read the structure from the JSON file
with open("structure_metadata.json", "r") as structure_file:
    metadata = json.load(structure_file)
    structure = metadata["structure"]


# Build a mapping between keywords and their respective file paths
def build_keyword_mapping(structure):
    keyword_mapping = {}

    # Traverse the metadata recursively and build the keyword mapping
    def traverse_metadata(metadata, path):
        for key, value in metadata.items():
            if isinstance(value, dict) and "value" in value:
                keyword_mapping[key] = os.path.join(path, f"{key}.md")
                if "children" in value:
                    traverse_metadata(value["children"], os.path.join(path, key))

    for category, subcategories in structure.items():
        for subcategory in subcategories:
            metadata_path = os.path.join(category, f"{subcategory}_metadata.json")

            # Check if the metadata JSON file exists before trying to read it
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as metadata_file:
                    metadata = json.load(metadata_file)

                traverse_metadata(metadata, category)

    return keyword_mapping


# Find all markdown files in the given path
def find_markdown_files(path):
    markdown_files = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    return markdown_files


# Build the keyword mapping
keyword_mapping = build_keyword_mapping(structure)


# Convert a markdown string to an Abstract Syntax Tree (AST)
def markdown_to_ast(markdown: str):
    """Converts markdown string to AST"""
    mistune_ast = mistune.create_markdown(renderer=None)
    ast = mistune_ast(markdown)
    return ast


# Update the metadata of a markdown file
def update_metadata(file_path: str):
    # Replace the '.md' extension with '_metadata.json'
    metadata_path = file_path.replace(".md", "_metadata.json")

    # Convert the Markdown file to AST
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    ast = markdown_to_ast(content)

    # Extract the metadata from the AST
    metadata = {}
    current_key = None

    def extract_data(node):
        nonlocal current_key
        if node['type'] == 'heading' and 'children' in node:
            heading_text = ''.join([child['raw'] for child in node['children'] if child['type'] == 'text'])
            current_key = heading_text.lower().replace(' ', '_')
            if current_key not in metadata:
                metadata[current_key] = {'value': ''}
        elif node['type'] == 'paragraph' and 'children' in node and current_key is not None:
            paragraph_text = ''.join([child['raw'] for child in node['children'] if child['type'] == 'text'])
            metadata[current_key]['value'] += paragraph_text

        if 'children' in node:
            for child in node['children']:
                extract_data(child)

    for node in ast:
        extract_data(node)

    # Add the word count to the metadata
    metadata["word_count"] = len(content.split())

    # Save the updated metadata to the JSON file
    with open(metadata_path, "w") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)


# Replace keywords with links in a markdown file
def add_links(file_path: str):
    # Read the content of the file
    with open(file_path, "r", encoding='utf-8') as file:
        content = file.read()

    # Replace keywords with links
    updated_content = content
    for keyword, target_file in keyword_mapping.items():
        link = f"[{keyword}]({target_file})"
        updated_content = updated_content.replace(keyword, link)

    # Write the updated content to the file
    with open(file_path, "w", encoding='utf-8') as file:
        file.write(updated_content)


# Main function
if __name__ == "__main__":
    # Set the path to the folder containing your
    # setting documents
    path = os.path.abspath(".")

    # Update all markdown files
    markdown_files = find_markdown_files(path)
    for markdown_file in markdown_files:
        update_metadata(markdown_file)
        add_links(markdown_file)
