import os
import json
import re
import mistune
from pathlib import Path
from lxml import etree
from typing import Dict, Any


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
    def extract_metadata(node, metadata_dict):

        if node and node.text and node.tag.startswith("h"):
            key = node.text.lower().replace(' ', '_')
            value = node.xpath("./following-sibling::p[1]/text()")
            metadata_dict[key] = value[0] if value else ""
            if node.text and node.tag == "h1":
                metadata_dict["top_level_header"] = node.text
        else:
            for child in node.iterchildren():
                extract_metadata(child, metadata_dict)

    metadata = {}
    extract_metadata(tree, metadata)
    metadata["word_count"] = len(content.split())

    # Serialize the metadata to a JSON string
    metadata_string = json.dumps(metadata, indent=2)

    # Save the metadata JSON file in the same directory as the Markdown file
    metadata_file_path = os.path.splitext(file_path)[0] + "_metadata.json"
    with open(metadata_file_path, "w") as metadata_file:
        metadata_file.write(metadata_string)

    return metadata


# Write the metadata JSON file in the same directory as the Markdown file
def write_metadata(file_path: str, metadata: Dict[str, Any]):
    metadata_string = json.dumps(metadata, indent=2)
    metadata_file_path = os.path.splitext(file_path)[0] + "_metadata.json"
    with open(metadata_file_path, "w") as metadata_file:
        metadata_file.write(metadata_string)


# Convert a markdown string to a JSON Abstract Syntax Tree (AST)
def markdown_to_ast_json(markdown: str):
    ast = markdown_to_ast(markdown)
    ast_json = json.dumps(ast, indent=2)
    return ast_json


# Build a mapping between headers and their respective file paths
def build_header_mapping():
    header_mapping = {}

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith("_metadata.json"):
                metadata_path = os.path.join(root, file)
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    top_level_header = metadata.get("top_level_header", None)
                    if top_level_header:
                        header_mapping[top_level_header] = os.path.join(root, file[:-len("_metadata.json")]) + ".md"

    return header_mapping


def fix_keys(metadata: Dict[str, Any]) -> Dict[str, Any]:
    fixed_metadata = {}
    for key, value in metadata.items():
        fixed_key = re.sub(r'\W+', '_', key.lower())
        fixed_metadata[fixed_key] = value
    return fixed_metadata


# Replace keywords with links in a markdown file
def add_links(file_path: str, metadata: Dict[str, Any]):
    # Read the content of the file
    with open(file_path, "r", encoding='utf-8') as file:
        content = file.read()

    # Replace keywords with links
    def replace_keyword(match, header_mapping):
        keyword = match.group(0)
        if keyword.lower() in header_mapping.keys():
            target_file = header_mapping[keyword.lower()]
            return f"[{keyword}]({target_file})"
        return keyword

    # Build the header mapping
    header_mapping = build_header_mapping()

    # Replace keywords with links in the content
    updated_content = re.sub(r'\b(?:[A-Za-z]+_?)+\b', lambda match: replace_keyword(match, header_mapping), content)

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

    # Build the header mapping
    header_mapping = build_header_mapping()
    for markdown_file in markdown_files:
        file_path = os.path.join(path, markdown_file)

        # Update the metadata
        metadata = update_metadata(file_path, markdown_file)

        # Fix the metadata keys
        metadata = fix_keys(metadata)

        # Write the metadata to a JSON file
        write_metadata(file_path, metadata)

        # # Add links to the markdown file
        # add_links(file_path, metadata)
