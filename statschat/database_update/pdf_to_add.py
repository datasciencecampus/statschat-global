# %%
# import modules
import PyPDF2
import json
from pathlib import Path
import datetime
import numpy as np
#from statschat.pdf_processing.pdf_to_json import (
    # get_name_and_meta, 
    # get_date, determine_dates, 
    # build_json,
    # extract_url_keywords_from_filename,
    # determine_document_type_from_filename,
    # extract_pdf_creation_date,
    # extract_pdf_modification_date,
    # extract_pdf_metadata,extract_pdf_text,
    #)

# %%
# set relative paths

DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
LATEST_DATA_DIR = Path.cwd().joinpath("data/latest_pdf_downloads")

# %%
new_pdf_list = []

for new_pdf_file in LATEST_DATA_DIR.glob("*.pdf"):
    # remove .pdf from end and append to list
    new_pdf_list.append(new_pdf_file.name[:-4])

new_pdf_list = sorted(new_pdf_list)
print(f"There are currently {len(new_pdf_list)} pdf files in the {LATEST_DATA_DIR.stem} folder")
    
# %%
old_pdf_list = []

for old_pdf_file in DATA_DIR.glob("*.pdf"):
    # remove .pdf from end and append to list
    old_pdf_list.append(old_pdf_file.name[:-4])

old_pdf_list = sorted(old_pdf_list) 
print(f"There are currently {len(old_pdf_list)} pdf files in the {DATA_DIR.stem} folder")

# %%
new_pdfs_to_convert = []

for new_pdf in new_pdf_list:
    #print(old_pdf)
    if new_pdf not in old_pdf_list:
        print(f"The pdf file: {new_pdf} is currently not in the database")
        new_pdfs_to_convert.append(new_pdf + ".pdf")
        
# print(new_pdfs_to_convert)

# %%
#for pdf in new_pdfs_to_convert:
    #print(DATA_DIR.joinpath(pdf))
    #pdf_file_path = DATA_DIR.joinpath(pdf)
    #print(pdf_file_path)
    
    