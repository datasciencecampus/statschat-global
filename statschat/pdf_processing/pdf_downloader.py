# %%
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

# %%
# Set relative paths
DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")

# Check if DATA_DIR exists, if not, create the folder
if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

# %%
# get all webpages on KNBS website that have PDFs and add them to a list

all_pdf_links = []

page = 1
base_url = f'https://www.knbs.or.ke/all-reports/page'

continue_search = True

while continue_search:
    url = base_url + str(page) + '/'
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

print('HAVE FINISHED COMPILING THEM AND WILL NOW START DOWNLOADING')

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
        else:
            print(f"Failed to download file {actual_pdf_file_name}")


