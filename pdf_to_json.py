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
    #print(pdf_file_path)

    # pdf file name
    file_name = pdf_file_path.name
    #print(file_name)

    # pdf metadata
    pdf_metadata = PyPDF2.PdfReader(pdf_file_path)
    #print(str(pdf_metadata.metadata))

    # pdf date, time and year
    pdf_date = str(pdf_metadata.metadata.creation_date)
    pdf_year = pdf_date[:4]
    pdf_month = pdf_date[5:7]

    #create new dict
    pdf_info = {}
    pdf_info["id"] = " "
    pdf_info["url"] = f"https://www.knbs.or.ke/wp-content/uploads/{pdf_year}/{pdf_month}/" + file_name
    pdf_info["release_date"] = pdf_date[:10] #date only
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

    with open(file_path, 'rb') as pdf_file:
        
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
            pages_text.append({"page_number": page_num + 1, 
                               "page_link": page_link + "#page=" + str(page_num + 1), 
                               "text": text})
        
        # create nested dictionary
        pdf_info["contents"] = pages_text

        #pdf_info

        #with open(TEST_DATA_DIR / "pdf_info.json", "w") as json_file:
        with open(TEST_DATA_DIR / f"{file_path.stem}.json", "w") as json_file:
            json.dump([pdf_info], json_file, indent=4)
            
        # print JSON
        print(json.dumps([pdf_info], indent=4))
        
        print(f"{pdf_info['title']} has been converted to a json")

