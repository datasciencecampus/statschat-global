# %%
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse
import json
from tqdm import tqdm
from statschat import load_config
import re

# %% Configuration

# Load configuration
config = load_config(name="main")
PDF_FILES = config["preprocess"]["download_mode"].upper()

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


page = 1  # Higher the number the older the publications
# Set max pages for UPDATE mode
max_pages = 100 if PDF_FILES == "SETUP" else 5  # Limit to 5 for updates

# %% Scrape intermediate report pages and extract PDF links
all_pdf_entries = {}  # {"pdf_url": "report_page", ...}
visited_report_pages = set()

# %% Scrape PDF links from website
all_pdf_links = []  # List to store all PDF URLs
page = 1
base_url = "URL to scrape from here"

print("IN PROGRESS.")
while True:
    # Trigger page limit for UPDATE mode
    if max_pages and page > max_pages:
        print(f"Reached page limit ({max_pages}) for UPDATE mode. Stopping search.")
        break

    # Visit each page and extract report links
    url = f"{base_url}{page}/"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to access {url}. Stopping search.")
        break

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all links that match the /reports/ pattern
    report_links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if re.search(r"/reports/[^/]+/?$", a["href"])
        and not a["href"].startswith("https://www.knbs.or.ke/reports/kenya-census")
    ]

    report_links = list(dict.fromkeys(report_links))
    # remove duplicate reports
    if not report_links:
        print(f"Reached page limit ({page}). Stopping search.")
        break

    # print(report_links)
    print(f"Found {len(report_links)} report pages on page {page}")

    # Step 2: Visit each report page and extract PDF links
    for report_url in report_links:
        if report_url in visited_report_pages:
            continue  # Skip already visited report pages

        visited_report_pages.add(report_url)
        report_response = requests.get(report_url)

        if report_response.status_code != 200:
            print(f"Failed to access report page: {report_url}")
            continue

        report_soup = BeautifulSoup(report_response.content, "html.parser")

        pdf_links = report_soup.find(
            "a", href=lambda href: href and href.endswith(".pdf")
        )
        # if pdf link found - retain first one
        if pdf_links:
            pdf_links = pdf_links["href"]
            all_pdf_entries[
                pdf_links
            ] = report_url  # Store the PDF URL and report page URL

    page += 1

print(f"Total PDFs found: {len(all_pdf_entries)}")

# %% If in UPDATE mode, filter only new PDFs
if PDF_FILES == "UPDATE":
    existing_urls = set(
        entry["pdf_url"]
        for entry in original_url_dict.values()
        if isinstance(entry, dict) and "pdf_url" in entry.keys()
    )

    # Filter `all_pdf_entries` to include only new entries
    new_entries = {
        pdf_url: report_page
        for pdf_url, report_page in all_pdf_entries.items()
        if pdf_url not in existing_urls
    }

    if not new_entries:
        print("No new PDFs found. Exiting update process.")
        exit()

    print(f"Found {len(new_entries)} new PDFs to download.")
    all_pdf_entries = new_entries  # Replace with filtered dictionary

# %% Download PDFs and Update URL Dictionary
format = "[{elapsed}<{remaining}]{n_fmt}/{total_fmt}|{l_bar}{bar} {rate_fmt}{postfix}"
for pdf, report_page in tqdm(
    all_pdf_entries.items(),
    desc="DOWNLOADING PDF FILES:",
    bar_format=format,
    colour="yellow",
    total=len(all_pdf_entries),
    dynamic_ncols=True,
):
    pdf_url = pdf
    report_url = report_page
    parsed_url = urlparse(pdf_url)
    pdf_name = Path(parsed_url.path).name

    file_path = DATA_DIR / pdf_name

    # Download PDF
    response = requests.get(pdf_url)

    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)

        # Store both pdf_url and report page
        url_dict[pdf_name] = {"pdf_url": pdf_url, "report_page": report_url}
    else:
        print(f"Failed to download: {pdf_url}")

# %% Save New URL Dictionary to JSON (Only new entries)
with open(url_dict_path, "w") as json_file:
    json.dump(url_dict, json_file, indent=4)
    print(f"Saved new url_dict.json to {url_dict_path}")

if PDF_FILES == "UPDATE":
    print("Finished downloading new PDF files.")

if PDF_FILES == "SETUP":
    print("Finished downloading all PDF files.")
