# %%
# import modules
import PyPDF2
import json
from pathlib import Path
import datetime
import numpy as np
#from statschat.pdf_processing.pdf_to_json import get_name_and_meta, get_date, determine_dates, build_json

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

# %%
convert_pdf_paths = []

# %%
def get_name_and_meta(file_path):
    """Extracts file name and metadata from PDF

    Args:
        file_path (path): file path for PDF file

    Returns:
        file_name: file for PDF file
        pdf_metadata: metadata for PDF (dates etc)
    """
    file_name = pdf_file_path.name
    pdf_metadata = PyPDF2.PdfReader(pdf_file_path)
    pdf_metadata = pdf_metadata.metadata

    return (file_name, pdf_metadata)

def get_date(metadata, name, counter):
    """Extracts creation date from PDF metadata
       Assigns current date if creation date is unavailable

    Args:
        metadata (_type_): metadata for PDF file
        name (str): PDF file name
        counter (int): counts numbers

    Returns:
        pdf_creation_date: date PDF file was created
        counter: number of PDF files with metadata issues
    """

    # pdf date, time and year (may need to add for modification date)
    try:
        pdf_creation_date = str(metadata.creation_date)
        print(f"no issue with metadata for {name}")

    except Exception as e:
        counter += 1
        pdf_creation_date = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"An error occurred for file {name}: {e}")
        print(f"Total number of files with errors: {count}")

    return pdf_creation_date, counter

def determine_dates(pdf_creation_date, pdf_modification_date):
    """Determines the correct year and month based on creation and modification date

    Args:
        pdf_creation_date (datetime): date pdf created
        pdf_modification_date (datetime): date pdf modified

    Returns:
        pdf_date: date for PDF to go into URL
        pdf_month: month for PDF to go into URL
    """

    pdf_creation_year = pdf_creation_date[:4]
    pdf_creation_month = pdf_creation_date[5:7]

    pdf_modification_month = pdf_modification_date[5:7]
    pdf_modification_year = pdf_modification_date[:4]

    # in case creation date empty
    if pdf_creation_year == "None":
        pdf_creation_year = pdf_modification_year
    if pdf_creation_month == "":
        pdf_creation_month = pdf_modification_month

    # if months below for pdf creation and modification are different
    # An error will come in the pdf hyperlink
    if int(pdf_creation_month) < int(pdf_modification_month) and int(
        pdf_creation_year
    ) == int(pdf_modification_year):
        pdf_month = pdf_modification_month
        pdf_year = pdf_modification_year
    # if years below for pdf creation year and modification year are different
    # An error will come in the pdf hyperlink
    elif int(pdf_creation_year) < int(pdf_modification_year) and int(
        pdf_creation_month
    ) > int(pdf_modification_month):
        pdf_year = pdf_modification_year
        pdf_month = pdf_modification_month
    else:
        pdf_year = pdf_modification_year
        pdf_month = pdf_modification_month

    return pdf_year, pdf_month

# %%
count = 0 

# convert pdf files to paths
for pdf in new_pdfs_to_convert:
    pdf_file_path = DATA_DIR.joinpath(pdf)
    #print(DATA_DIR.joinpath(pdf))
    file_name, pdf_metadata = get_name_and_meta(pdf_file_path)
    
    pdf_creation_date, count = get_date(pdf_metadata, file_name, count)
    
    try:
        pdf_modification_date = str(pdf_metadata.modification_date)
    except AttributeError:
        print(f"An error fetching the modification date occurred for file {file_name}")
        pdf_modification_date = pdf_creation_date

    pdf_year, pdf_month = determine_dates(pdf_creation_date, pdf_modification_date)
    
    print(pdf_year, pdf_month)
    
    