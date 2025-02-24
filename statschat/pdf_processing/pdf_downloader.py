# %%
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse
import json

# %%
# Set relative paths
DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")

# Check if DATA_DIR exists, if not, create the folder
if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

# %%
# get all webpages on KNBS website that have PDFs and add them to a list

all_pdf_links = []

# %%
# on separate lines
webpage_list_pdf_links = "\n".join(pdf_links)

continue_search = True

# %%
# Initalise empty dict to store url and download links
url_dict = {}
# %%
# Iterate over each PDF URL extracted from the webpage,
for pdf in pdf_links:
    url = pdf
    parsed_url = urlparse(url)
    pdf_name = parsed_url.path
    actual_pdf_file_name = pdf_name[28:]

    # Download PDF and save to a local file path.
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Break the loop if no more quotes are found
    pdf_links = [
        a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf")
    ]
    
    if len(pdf_links) == 0:
        print('HAVE STOPPED GETTING WEBPAGES')
        continue_search = False
    
    page += 1
    all_pdf_links.append(url)

print('FINISHED COMPILING LINKS AND WILL NOW START DOWNLOADING PDFs')

# %%
# print counter

# %%
# removes last append to list as that webpage has no pdfs (USE THIS)

all_pdf_links = all_pdf_links[:-1]
all_pdf_links

# %%
# gets links for every PDF from every KNBS webpage and adds to a list

all_knbs_pdf_file_links = []

for pdf_file in all_pdf_links:
    
    url = pdf_file
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    pdf_links = [
        a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf")
    ]
    
    all_knbs_pdf_file_links.append(pdf_links)

# %%
# gets page range for PDFs to loop through multiple lists made

pdf_page_range = len(all_knbs_pdf_file_links)

# %%
# downloads PDFs to relevant folder

counter = 0 

for i in range(pdf_page_range):
    for pdf in all_knbs_pdf_file_links[i]:
        url = pdf
        parsed_url = urlparse(url)
        pdf_name = parsed_url.path
        actual_pdf_file_name = pdf_name[28:]

        response = requests.get(url)
        file_path = f"{DATA_DIR}/{actual_pdf_file_name}"

        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"File {actual_pdf_file_name} downloaded successfully")
            
            counter += 1
        
        else:
            print(f"Failed to download file {actual_pdf_file_name}")
            
        


    # update dictionary
    url_dict[actual_pdf_file_name] = url
    print(url_dict[actual_pdf_file_name])

    # Save file in binary mode if request is successful,
    # return error message if request fails.
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File {actual_pdf_file_name} downloaded successfully")
    else:
        print(f"Failed to download file {actual_pdf_file_name}")

# Export url link dictionary to json file
with open(f"{DATA_DIR}/url_dict.json", "w") as json_file:
    json.dump(url_dict, json_file, indent=4)
    print("url_dict saved to url_dict.json")
