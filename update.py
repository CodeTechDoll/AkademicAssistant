import os
import json
import re
import mistune
from pathlib import Path
from lxml import etree


# Read the structure from the JSON file
with open("structure_metadata.json", "r") as structure_file:
    metadata = json.load(structure_file)
    structure = metadata["structure"]


# Build a mapping between keywords and their respective file paths
def build_keyword_mapping(structure):
    keyword_mapping = {}

    def traverse_metadata(category_metadata, category_path):
        for key, value in category_metadata.items():
            if isinstance(value, dict) and "value" in value:
                keyword_mapping[key] = Path(category_path) / f"{key}.md"
                if "children" in value:
                    traverse_metadata(value["children"], Path(category_path) / key)

    for category, subcategories in structure.items():
        for subcategory in subcategories:
            metadata_path = Path(category) / f"{subcategory}_metadata.json"

            if metadata_path.exists():
                with metadata_path.open("r") as metadata_file:
                    category_metadata = json.load(metadata_file)

                traverse_metadata(category_metadata, category)

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
    mistune_ast = mistune.create_markdown(renderer=None)
    ast = mistune_ast(markdown)
    return ast


# Update the metadata of a markdown file
def update_metadata(directory_path: str, filename: str):
    file_path = os.path.join(directory_path, filename)

    # Convert the Markdown file to AST
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    parser = etree.HTMLParser()
    tree = etree.fromstring(mistune.html(content), parser)

    # Extract the metadata from the AST
    metadata = {}
    for node in tree.xpath("//h1|//h2|//h3|//h4|//h5|//h6"):
        key = node.text.lower().replace(' ', '_')
        value = node.xpath("./following-sibling::p[1]/text()")
        metadata[key] = value[0] if value else ""

    # Add the word count to the metadata
    metadata["word_count"] = len(content.split())

    # Serialize the metadata to a JSON string
    metadata_string = json.dumps(metadata, indent=2)

    # Save the metadata JSON file in the same directory as the Markdown file
    metadata_file_path = os.path.splitext(file_path)[0] + "_metadata.json"
    with open(metadata_file_path, "w") as metadata_file:
        metadata_file.write(metadata_string)

    return metadata_string


# Replace keywords with links in a markdown file
def add_links(file_path: str):
    # Read the content of the file
    with open(file_path, "r", encoding='utf-8') as file:
        content = file.read()

    # Replace keywords with links
    def replace_keyword(match):
        keyword = match.group(0)
        if keyword.lower() in keyword_mapping:
            target_file = keyword_mapping[keyword.lower()]
            return f"[{keyword}]({target_file})"
        return keyword

    updated_content = re.sub(r'\b(?:[A-Za-z]+_?)+\b', replace_keyword, content)

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
        metadata = update_metadata(path, markdown_file)
        add_links(os.path.join(path, markdown_file))
