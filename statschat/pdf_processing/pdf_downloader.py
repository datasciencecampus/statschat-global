# %%
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse
import json

# %% Configuration

PDF_FILES = "UPDATE"  # Change to "SETUP" for the first run

# Set directories
BASE_DIR = Path.cwd().joinpath("data")
DATA_DIR = BASE_DIR.joinpath(
    "pdf_downloads" if PDF_FILES == "SETUP" else "latest_pdf_downloads"
)
OUTPUT_URL_DIR = BASE_DIR.joinpath(
    "pdf_downloads" if PDF_FILES == "SETUP" else "latest_pdf_downloads"
)
ORIGINAL_URL_DICT_PATH = BASE_DIR.joinpath("pdf_downloads/url_dict.json")

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_URL_DIR.mkdir(parents=True, exist_ok=True)

print(f"STARTING DATABASE {PDF_FILES}. PLEASE WAIT...")

# Set path for new url_dict.json (where new entries are saved)
url_dict_path = OUTPUT_URL_DIR / "url_dict.json"

# Initialize URL dictionary
if PDF_FILES == "SETUP":
    url_dict = {}  # Start fresh, do not load anything

elif PDF_FILES == "UPDATE":
    if ORIGINAL_URL_DICT_PATH.exists():
        with open(ORIGINAL_URL_DICT_PATH, "r") as json_file:
            original_url_dict = json.load(json_file)
            print(f"Loaded existing url_dict.json from {ORIGINAL_URL_DICT_PATH}")
    else:
        print("No existing url_dict.json found in pdf_downloads. Exiting update mode.")
        exit()  # Nothing to update if there's no record

    url_dict = {}  # This will store only new entries

# Set max pages for UPDATE mode
max_pages = None if PDF_FILES == "SETUP" else 5  # Limit to 5 pages for updates

print("IN PROGRESS.")

# %% Scrape PDF links from KNBS website
all_pdf_links = []  # List to store all PDF URLs
page = 1
base_url = "https://www.knbs.or.ke/all-reports/page"

while True:
    if max_pages and page > max_pages:
        print(f"Reached page limit ({max_pages}). Stopping search.")
        break

    url = f"{base_url}{page}/"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to access {url}. Stopping search.")
        break

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract all PDF links on the page
    pdf_links = [
        a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf")
    ]

    if not pdf_links:  # If no PDFs found, assume we've reached the last page
        print("No PDFs found. Stopping search.")
        break

    all_pdf_links.extend(pdf_links)  # Flatten list correctly
    print(f"Found {len(pdf_links)} PDFs on page {page}")

    page += 1

print(f"Total PDFs found: {len(all_pdf_links)}")

# %% If in UPDATE mode, filter only new PDFs

if PDF_FILES == "UPDATE":
    existing_urls = set(
        original_url_dict.values()
    )  # Convert existing URLs to a set for quick lookup
    new_pdf_links = [pdf for pdf in all_pdf_links if pdf not in existing_urls]

    if not new_pdf_links:
        print("No new PDFs found. Exiting update process.")
        exit()

    print(f"Found {len(new_pdf_links)} new PDFs to download.")
    all_pdf_links = new_pdf_links  # Replace with filtered list

# %% Download PDFs and Update URL Dictionary

for pdf_url in all_pdf_links:
    parsed_url = urlparse(pdf_url)
    pdf_name = Path(parsed_url.path).name  # Extract the actual filename

    file_path = DATA_DIR / pdf_name  # Store PDFs in the correct directory

    # Download PDF
    response = requests.get(pdf_url)

    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
            print(f"Downloaded: {pdf_name} -> {file_path}")

        url_dict[pdf_name] = pdf_url  # Store only new entries
    else:
        print(f"Failed to download: {pdf_url}")

# %% Save New URL Dictionary to JSON (Only new entries)
with open(url_dict_path, "w") as json_file:
    json.dump(url_dict, json_file, indent=4)
    print(f"Saved new url_dict.json to {url_dict_path}")

if PDF_FILES == "UPDATE":
    print("Finished downloading new PDF file. Please run pdf_database_update.py next.")

if PDF_FILES == "SETUP":
    print("Finished downloading all PDF files. Please run pdf_to_json.py next.")
