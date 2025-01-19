# %% [markdown]
# Download all pdfs from certain webpage
# %%
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import *

# %%
# Set relative paths
DATA_DIR = DATA_DIR = Path.cwd().parent.parent.joinpath("data")

# %%
url = "https://www.knbs.or.ke/publications/page/2/"
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
print(webpage_list_pdf_links)

# %%
# number of pdf's
len(pdf_links)

# %%
for pdf in pdf_links:
    url = pdf
    parsed_url = urlparse(url)
    pdf_name = parsed_url.path
    actual_pdf_file_name = pdf_name[28:]

    response = requests.get(url)
    file_path = DATA_DIR / actual_pdf_file_name

    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File {actual_pdf_file_name} downloaded successfully")
    else:
        print(f"Failed to download file {actual_pdf_file_name}")