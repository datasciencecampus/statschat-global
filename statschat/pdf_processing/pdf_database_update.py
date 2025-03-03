# %%
# import modules
import PyPDF2
import os
import json
from pathlib import Path
import datetime
import numpy as np
from statschat.pdf_processing.pdf_to_json import (
    get_name_and_meta,  
    build_json,
    extract_url_keywords_from_filename,
    extract_pdf_metadata,extract_pdf_text,
    normalize_dict_keys,
    )

# %%
# set relative paths

DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
LATEST_DATA_DIR = Path.cwd().joinpath("data/latest_pdf_downloads")
JSON_DIR = Path.cwd().joinpath("data/latest_json_conversions")

# %%
print("STARTING PDF COMPARISONS")
# %%
new_pdf_list = []

for new_pdf_file in LATEST_DATA_DIR.glob("*.pdf"):
    # remove .pdf from end and append to list
    new_pdf_list.append(new_pdf_file.name[:-4])

# sort alphabetically
new_pdf_list = sorted(new_pdf_list)
print(f"There are currently {len(new_pdf_list)} pdf files in the {LATEST_DATA_DIR.stem} folder")
    
# %%
old_pdf_list = []

for old_pdf_file in DATA_DIR.glob("*.pdf"):
    # remove .pdf from end and append to list
    old_pdf_list.append(old_pdf_file.name[:-4])

# sort alphabetically
old_pdf_list = sorted(old_pdf_list) 
print(f"There are currently {len(old_pdf_list)} pdf files in the {DATA_DIR.stem} folder")

# %%
new_pdfs_to_convert = []

for new_pdf in new_pdf_list:
    #print(old_pdf)
    
    # see which pdfs are new and aren't in database
    if new_pdf not in old_pdf_list:
        print(f"The pdf file: {new_pdf} is currently not in the database and needs to be added")
        new_pdfs_to_convert.append(new_pdf + ".pdf")
        
# print(new_pdfs_to_convert)

# %%

print("STARTING CONVERSION OF LATEST PDF FILES")
# Initialize counter
count = 0  # Initialize counter

# Load in url dict
dict_filepath = f"{LATEST_DATA_DIR}/url_dict.json"
if os.path.exists(dict_filepath):
    with open(dict_filepath, "r") as json_file:
        url_dict = json.load(json_file)
        
# normalize keys
normalize_dict_keys(url_dict)

# Loop through all PDF files and process them        
# Use functions from pdf_to_json to convert new pdfs to jsons
for pdf in new_pdfs_to_convert:
    
    pdf_file_path = LATEST_DATA_DIR.joinpath(pdf)
    
    file_name, pdf_metadata = get_name_and_meta(pdf_file_path)
    
    pdf_url = url_dict[os.path.basename(pdf_file_path)]
    
    url_keywords = extract_url_keywords_from_filename(file_name)
    
    file_name, pdf_creation_date, pdf_metadata, counter = extract_pdf_metadata(pdf_file_path, count)
    
    pages_text = extract_pdf_text(pdf_file_path, pdf_url)
    
    count = build_json(pdf_file_path, pdf_url, count, JSON_DIR)
    #print(pdf_file_path)
    
print("FINISHED PDF TO JSON CONVERSION")
    
    