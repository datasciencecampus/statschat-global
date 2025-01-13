# %%
# import modules
import PyPDF2
import json
from pathlib import Path

# %%
# set relative paths
DATA_DIR = Path.cwd().joinpath("data")
TEST_DIR = Path.cwd().joinpath("tests")
TEST_DATA_DIR = TEST_DIR.joinpath("data")

# %%
# pdf file name
file_name = "2024-FinAccess-Household-Survey-Report.pdf"

# %%
# file path for pdf
file_path = DATA_DIR.joinpath(file_name)

# %%
# pdf metadata
pdf_metadata = PyPDF2.PdfReader(file_path)
print(str(pdf_metadata.metadata))
#print(str(pdf_metadata.metadata.producer))

# %%
# pdf date and time
pdf_date = str(pdf_metadata.metadata.creation_date)

# %%
# create list to store
pages_text = []

with open(file_path, 'rb') as pdf_file:
    
    # read file
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    # read every page
    for page_num in range(len(pdf_reader.pages)):
        
        # read page wise data from pdf file
        page = pdf_reader.pages[page_num]
        
        # extract data from page to text
        text = page.extract_text().split('\n')
        
        # add text of page to array
        pages_text.append({"page_number": page_num + 1, "text": text})
    
    #create new dict
    pdf_info = {}
    pdf_info["id"] = " "
    pdf_info["title"] = str(pdf_metadata.metadata.title)
    pdf_info["url"] = " "
    pdf_info["release_date"] = pdf_date[:10] #date only
    pdf_info["release_type"] = " "
    # pdf_info["latest"] = " "
    pdf_info["url_keywords"] = " "
    
    # create nested dictionary
    pdf_info["contents"] = pages_text

# %%
pdf_info

# %%
# For figures
figures_info = []

with open(file_path, 'rb') as pdf_file:
    
    # read file
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    # read every page
    for page_num in range(len(pdf_reader.pages)):
        
        # read page wise data from pdf file
        page = pdf_reader.pages[page_num]
        
        # extract data from page to text
        text = page.extract_text().split('\n')
        
        for fig in text:
            # for title
            if "Figure" in fig and ":" in fig and ".." in fig:
            
                # add fig head to array
                figures_info.append({"page_number": page_num + 1,"figure_title": fig})
    
    figures_dict = {}
    figures_dict["figure_title"] = figures_info   

# %%
# want to add this to pdf_info["contents"]

# %%
# write list to json file

#with open(TEST_DATA_DIR / "pdf_info.json", "w") as json_file:
with open(TEST_DATA_DIR / f"{file_path.stem}.json", "w") as json_file:
    json.dump([pdf_info], json_file, indent=4)
    
# print JSON
print(json.dumps([pdf_info], indent=4))



