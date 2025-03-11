#import pdf_to_json as ptj
# %%
# import modules
import PyPDF2
import json
from pathlib import Path
import datetime
import numpy as np


DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
pdf_list = list(DATA_DIR.glob("*.pdf"))
first_pdf = pdf_list[0]
print(first_pdf)

def get_name_and_meta(file_path):
    """
    Extracts file name and metadata from PDF
    """
    file_name = file_path.name
    pdf_metadata = PyPDF2.PdfReader(file_path)
    pdf_metadata = pdf_metadata.metadata

    return (file_name, pdf_metadata)

file_name, pdf_metadata = get_name_and_meta(first_pdf)
print(file_name, pdf_metadata)