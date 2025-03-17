# %%
# import modules
import os
import json
from pathlib import Path


# %%
# set relative paths

DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
LATEST_DATA_DIR = Path.cwd().joinpath("data/latest_pdf_downloads")
JSON_DIR = Path.cwd().joinpath("data/latest_json_conversions")

# %%
print("STARTING PDF COMPARISONS")
# %%
# get list of new pdfs in latest_pdf_downloads
new_pdf_list = []

for new_pdf_file in LATEST_DATA_DIR.glob("*.pdf"):
    # remove .pdf from end and append to list
    new_pdf_list.append(new_pdf_file.name[:-4])

# %%
# get list of old pdfs in pdf_downloads
old_pdf_list = []

for old_pdf_file in DATA_DIR.glob("*.pdf"):
    # remove .pdf from end and append to list
    old_pdf_list.append(old_pdf_file.name[:-4])

# %%
# compare lists and see which pdfs are new
new_pdfs_to_convert = []

for new_pdf in new_pdf_list:
    # see which pdfs are new and aren't in database
    if new_pdf not in old_pdf_list:
        print(f"New pdf file: {new_pdf} will be converted to json and added.")
        new_pdfs_to_convert.append(new_pdf + ".pdf")

# %%
if __name__ == "__main__":
    from pdf_to_json import (
        build_json,
        normalize_dict_keys,
    )

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

        pdf_url = url_dict[os.path.basename(pdf_file_path)]

        count = build_json(pdf_file_path, pdf_url, count, JSON_DIR)

    print("FINISHED PDF TO JSON CONVERSION. Please now run preprocess_update_db.py")
