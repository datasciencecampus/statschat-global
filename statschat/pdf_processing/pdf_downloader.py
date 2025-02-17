# %% [markdown]
# Download all pdfs from certain webpage
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
# Extract and Parse HTML content from website
# for ease during navigation and extraction of elements
url = "https://www.knbs.or.ke/all-reports/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# %%
# finds pdf refs on webpage
pdf_links = [
    a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf")
]

# %%
# on separate lines
webpage_list_pdf_links = "\n".join(pdf_links)

# %%
# number of pdf's
len(pdf_links)

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
    file_path = f"{DATA_DIR}/{actual_pdf_file_name}"

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
