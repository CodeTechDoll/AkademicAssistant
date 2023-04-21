import gzip
import os
import hashlib
import pickle
from bs4 import BeautifulSoup
from config import config


def parse_directory(directory):
    data = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    soup = BeautifulSoup(content, "html.parser")
                    data.append(soup.get_text())

    return data


def save_to_datafile(data, filename="datafile.bin"):
    data_hash = hashlib.sha256(str(data).encode()).hexdigest()
    with gzip.open(filename, "wb") as f:
        pickle.dump((data, data_hash), f)


def load_from_datafile(filename="datafile.bin"):
    with gzip.open(filename, "rb") as f:
        data, data_hash = pickle.load(f)
    return data, data_hash


# Example usage
# data = parse_directory(config.get("DEFAULT", "setting_directory"))
# save_to_datafile(data)
data, data_hash = load_from_datafile()
print(data, 1000)

with open('data.txt', 'w') as f:
    pickle.dump(data, f)
    