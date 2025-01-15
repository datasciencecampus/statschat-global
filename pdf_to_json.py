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
for pdf_file_path in DATA_DIR.glob('*.pdf'):
    print(pdf_file_path)
    # loop through folder to get filepaths

    # pdf file name in case can't get title from metadata
    file_name = pdf_file_path.name
    
    # pdf metadata
    pdf_metadata = PyPDF2.PdfReader(pdf_file_path)
    print(str(pdf_metadata.metadata))
    

    # pdf date, time and year
    pdf_creation_date = str(pdf_metadata.metadata.creation_date)
    pdf_creation_year = pdf_creation_date[:4]
    pdf_creation_month = pdf_creation_date[5:7]
        
    pdf_modification_date = str(pdf_metadata.metadata.modification_date)
    pdf_modification_month = pdf_modification_date[5:7]
    pdf_modification_year = pdf_modification_date[:4]
    
    # incase creation date empty
    if pdf_creation_year == "None":
        pdf_creation_year = pdf_modification_year
    if pdf_creation_month == '':
        pdf_creation_month = pdf_modification_month
    
    print(pdf_creation_year)
    print(pdf_creation_month)
    print(pdf_modification_year)
    print(pdf_modification_month)
    
    
    # if months below for pdf creation and modification are different will get error in pdf hyperlink
    if int(pdf_creation_month) < int(pdf_modification_month) and int(pdf_creation_year) == int(pdf_modification_year):
        pdf_month = pdf_modification_month
        pdf_year = pdf_creation_year
    # if years below for pdf creation year and modification year are different will get error in pdf hyperlink
    elif int(pdf_creation_year) < int(pdf_modification_year) and int(pdf_creation_month) > int(pdf_modification_month):
        pdf_year = pdf_modification_year
        pdf_month = pdf_modification_month
    else:
        pdf_year = pdf_modification_year
        pdf_month = pdf_modification_month
    
    
    #create new dict
    pdf_info = {}
    pdf_info["id"] = " "
    pdf_info["url"] = f"https://www.knbs.or.ke/wp-content/uploads/{pdf_year}/{pdf_month}/" + file_name
    #pdf_info["url_option_two"] = f"https://www.knbs.or.ke/wp-content/uploads/{pdf_year}/{pdf_month}/" + file_name
    pdf_info["release_date"] = pdf_creation_date[:10] #date only
    pdf_info["release_type"] = " "
    # pdf_info["latest"] = " "
    pdf_info["url_keywords"] = " "
    pdf_info["title"] = str(pdf_metadata.metadata.title)
        
    # if pdf title metadata blank
    if pdf_info["title"] == "None":
        title_from_filename = file_name.replace(".pdf", "")
        pdf_info["title"] = title_from_filename
    else:
        pdf_info["title"] = str(pdf_metadata.metadata.title)
        
    # create list to store
    pages_text = []

    with open(pdf_file_path, 'rb') as pdf_file:
        
        # read file
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # read every page
        for page_num in range(len(pdf_reader.pages)):
            
            # read page wise data from pdf file
            page = pdf_reader.pages[page_num]
            
            # extract data from page to text
            text = page.extract_text().split('\n')
            
            # get page link
            page_link = pdf_info["url"]
            
            # add text of page to array
            pages_text.append({"page_number": page_num + 1, "page_link": page_link + "#page=" + str(page_num + 1), "text": text})
        
        # create nested dictionary
        pdf_info["contents"] = pages_text

        #pdf_info

        with open(TEST_DATA_DIR / f"{pdf_file_path.stem}.json", "w") as json_file:
            json.dump([pdf_info], json_file, indent=4)
            
        # print JSON
        print(json.dumps([pdf_info], indent=4))
