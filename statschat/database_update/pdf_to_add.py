# %%
# import modules
import PyPDF2
import json
from pathlib import Path
import datetime
import numpy as np
# %%
# set relative paths

DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
JSON_DIR = Path.cwd().joinpath("data/json_conversions")
LATEST_JSON_DIR = Path.cwd().joinpath("data/json_conversions_latest")

# %%
json_list = []

for json_file in JSON_DIR.glob("*.json"):
    # remove .json from end
    #print(json_file.name[:-5])
    
    # append to list
    json_list.append(json_file.name[:-5])

#json_list = json_list.sort() 
json_list = sorted(json_list)
print(f"There are currently {len(json_list)} json files in the {JSON_DIR.stem} folder")
    
# %%
pdf_list = []

for pdf_file in DATA_DIR.glob("*.pdf"):
    # remove pdf from end
    #print(pdf_file.name[:-4])
    
    # append to list
    pdf_list.append(pdf_file.name[:-4])

pdf_list = sorted(pdf_list) 
print(f"There are currently {len(pdf_list)} pdf files in the {DATA_DIR.stem} folder")

# %%
new_pdfs_to_convert = []

for json, pdf in zip(json_list, pdf_list):
    #print(f"json: {json} pdf: {pdf}")
    if pdf not in json_list:
        print(f"The pdf file: {pdf} not in database")
        #print(pdf + ".pdf")
        new_pdfs_to_convert.append(pdf + ".pdf")
        
#print(new_pdfs_to_convert)
    