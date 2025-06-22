from dotenv import load_dotenv
load_dotenv(override=True)
import json, os, datetime, re
from collections import Counter

# Loading the environmental variables.
JSON_DIR  = os.getenv("JSON_DIR")
UNIQUE_DIR = os.getenv("UNIQUE_DIR")

os.makedirs(os.path.dirname(JSON_DIR), exist_ok=True)

import pickle

with open('data/items_en.pkl', 'rb') as f:
    items = pickle.load(f)

items_list = []
for item in items:
    item_object = {
        "_id": item.id,
        "name": item.name["en"], 
        "shoppingCategory": item.shopping_category["en"], 
        "shopping_subcategory": item.shopping_subcategory["en"], 
        "item_category": item.item_category["en"],
        "item_subcategory": item.item_subcategory["en"], 
        "tags_dsw": item.item_tags_dsw["en"],
        "tags_gsw": item.item_tags_gsw["en"]
    }

    items_list.append(item_object)

with open(JSON_DIR, "w", encoding="utf-8") as f:
    f.write("[")
    for idx, doc in enumerate(items_list):
        print(idx)

        if idx != len(items_list) - 1:
            f.write(json.dumps(doc, default=str) + ",\n")
        else:
            f.write(json.dumps(doc, default=str) + "\n")
    f.write("]")

def collect_unique_strings(json_file_path):
    # Set to store unique strings
    unique_strings = set()
    counts: Counter = Counter()

    # Open and load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    pattern = r'[^\w\s]'  # Matches all punctuation

    def collect_clean(s: str):
        cleaned_parts = [
                    re.sub(pattern, "", part.strip()) for part in s.split(",")
                ]
        for token in cleaned_parts:
            if token:                     # ignore empty tokens
                unique_strings.add(token)
                counts[token] += 1        # tally occurrences

    # Iterate through each document in the JSON
    for document in data:
        for key, value in document.items():
            if key == "_id" or key == "name": continue
            # If the value is a string, split by comma and add to the set
            if isinstance(value, str):
                collect_clean(value)
            elif isinstance(value, list):
                for s in value:
                    collect_clean(s)

    return unique_strings, counts

unique_strings, counts = collect_unique_strings(JSON_DIR)

os.makedirs(os.path.dirname(JSON_DIR), exist_ok=True)

with open(UNIQUE_DIR, 'w') as output_file:
    for string in unique_strings:
        output_file.write(f"{string}, {counts[string]}\n")