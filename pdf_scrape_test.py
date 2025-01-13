# %% [markdown]
# Download all pdfs from certain page comes out in horrible format though

# %%
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import *

# %%
# Set relative paths
DATA_DIR = Path.cwd().joinpath("data")

# %%
url = "https://www.knbs.or.ke/publications/"
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
    file_path = DATA_DIR / f"{actual_pdf_file_name}.json"

    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print("File downloaded successfully")
    else:
        print("Failed to download file")

# %%
for pdf in pdf_links:
    url = pdf
    parsed_url = urlparse(url)
    pdf_name = parsed_url.path
    actual_pdf_file_name = pdf_name[28:]
    actual_pdf_file_name = actual_pdf_file_name.replace(".pdf", "")

    response = requests.get(url)
    file_path = DATA_DIR / f"{actual_pdf_file_name}.json"

    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        print("File downloaded successfully")
    else:
        print("Failed to download file")

# %% [markdown]
# comes out in horrible format


# %%
def download_pdf(url, filename):
    response = requests.get(url)
    with open(filename, "wb") as f:
        f.write(response.content)


# %%
download_pdf(
    url="https://www.knbs.or.ke/wp-content/uploads/2024/12/Analytical-Report-on-ICTBased-on-2022-KDHS.pdf",
    filename="test",
)

# %%
# https://www.youtube.com/watch?v=DQdU2Pj5AC8
