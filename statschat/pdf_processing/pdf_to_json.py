# %%
# import modules
import os
import PyPDF2
import json
import re
from pathlib import Path
import numpy as np
from typing import List
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime

# %%
# set relative paths
# Update for latest PDFs or setup when using for first time

# Set relative paths
DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
LATEST_DATA_DIR = Path.cwd().joinpath("data/latest_pdf_downloads")
JSON_DIR = Path.cwd().joinpath("data/json_conversions")
LATEST_JSON_DIR = Path.cwd().joinpath("data/latest_json_conversions")


def load_config(config_path: Path) -> dict:
    """
    Load configuration from the main.toml file.

    Args:
        config_path (Path): Path to the configuration file.

    Returns:
        dict: Parsed configuration as a dictionary.
    """
    import toml

    return toml.load(config_path)


def get_pdf_list(directory: Path) -> List[str]:
    """
    Get a list of PDF filenames (without extensions) from a directory.

    Args:
        directory (Path): Path to the directory containing PDF files.

    Returns:
        list: List of PDF filenames (without extensions).
    """
    return [pdf_file.stem for pdf_file in directory.glob("*.pdf")]


def compare_pdfs(new_pdfs: List[str], old_pdfs: List[str]) -> List[str]:
    """
    Compare new and old PDFs and return a list of new PDFs to process.

    Args:
        new_pdfs (list): List of new PDF filenames (without extensions).
        old_pdfs (list): List of old PDF filenames (without extensions).

    Returns:
        list: List of new PDFs that are not in the old PDFs list.
    """
    return [pdf for pdf in new_pdfs if pdf not in old_pdfs]


def generate_latest_dir(original_dir: Path) -> Path:
    """
    Generate a "latest_" version of the given directory.

    Args:
        original_dir (Path): The original directory path.

    Returns:
        Path: The dynamically generated "latest_" directory path.
    """
    return original_dir.parent / f"latest_{original_dir.name}"


def get_name_and_meta(pdf_file_path):
    """Extracts file name and metadata from PDF

    Args:
        file_path (path): file path for PDF file

    Returns:
        file_name: file for PDF file
        pdf_metadata: metadata for PDF (dates etc)
    """
    file_name = pdf_file_path.name
    pdf_metadata = PyPDF2.PdfReader(pdf_file_path)
    pdf_metadata = pdf_metadata.metadata

    return (file_name, pdf_metadata)


def extract_url_keywords_from_filename(file_name: str) -> list[str]:
    """
    Extracts unique keywords from a hyphen-separated filename while
    preserving order.

    Args:
        filename (str): The input filename (e.g., '2018-Survey-Test-2018.pdf').

    Returns:
        list[str]: A list of unique keywords from the filename,
        maintaining order.

    Example:
        >>> extract_unique_keywords_from_filename("2018-Survey-Test-2018.pdf")
        ['2018', 'Survey', 'Test']
    """
    words = file_name.replace(".pdf", "").split("-")  # Remove extension & split
    url_keywords = []

    for word in words:
        if word not in url_keywords:  # Maintain order & remove duplicates
            url_keywords.append(word)

    return url_keywords


def extract_pdf_creation_date(metadata, filename: str, counter: int) -> tuple[str, int]:
    """
    Extracts the creation date from PDF metadata if available. If unavailable,
    it falls back to extracting the most recent year from the filename, the modification
    date from metadata, or the current system date as a final fallback.

    Args:
        metadata: PDF metadata dictionary from PyPDF2.PdfReader (can be None).
        filename (str): The filename from which to extract a year if needed.
        counter (int): A running count of files that lack reliable date information.

    Returns:
        tuple[str, int]: The extracted or fallback PDF creation date in 'YYYY-MM-DD'
        format, and an updated counter for files missing an explicit creation date.
    """

    pdf_creation_date = None  # Initialize variable to store the extracted date.

    def preprocess_date(date_str: str) -> str:
        """Extracts only the YYYYMMDD portion from a PyPDF2 date string."""
        if date_str and date_str.startswith("D:"):
            date_str = date_str[2:10]  # Extract only YYYYMMDD
        return (
            date_str if date_str and len(date_str) == 8 and date_str.isdigit() else None
        )

    # Ensure metadata is not None before accessing it
    if metadata:
        raw_date = metadata.get("/CreationDate") if isinstance(metadata, dict) else None
        cleaned_date = preprocess_date(str(raw_date)) if raw_date else None

        if cleaned_date:
            pdf_creation_date = (
                f"{cleaned_date[:4]}-{cleaned_date[4:6]}-{cleaned_date[6:8]}"
            )

    # Extract the most recent year from the filename if no valid creation date is found.
    if not pdf_creation_date:
        years_in_filename = sorted(
            map(int, re.findall(r"\b(19\d{2}|20\d{2})\b", filename))
        )
        if years_in_filename:
            pdf_creation_date = (
                f"{max(years_in_filename)}-01-01"  # Assign start-of-year date.
            )

    # Assign the current system date if no valid date is found.
    if not pdf_creation_date:
        pdf_creation_date = datetime.datetime.now().strftime("%Y-%m-%d")
        counter += (
            1  # Increment counter since the system date is being used as a fallback.
        )
        print("WARNING: No valid creation date found setting as todays date")

    return pdf_creation_date, counter


def extract_pdf_modification_date(metadata, pdf_creation_date: str) -> str:
    """
    Extracts the modification date from PDF metadata if available. If the modification
    date is more than 10 years earlier than the creation date, defaults to the creation
    date.

    Args:
        metadata: PDF metadata object from PyPDF2.PdfReader.
        pdf_creation_date (str): The creation date to use as a fallback if
        modification date is missing or invalid.

    Returns:
        str: The extracted or fallback modification date in 'YYYY-MM-DD' format.

    Example:
        >>> extract_pdf_modification_date(metadata, "2019-04-24")
        '2023-09-04'
        >>> extract_pdf_modification_date(metadata, "2019-04-24")
        '2019-04-24'  # Fallback to creation date
    """
    try:
        # Extract modification date from metadata
        pdf_modification_date = str(metadata.modification_date)[:10]

        # Parse the dates into datetime objects
        creation_date_obj = datetime.strptime(pdf_creation_date, "%Y-%m-%d")
        modification_date_obj = datetime.strptime(pdf_modification_date, "%Y-%m-%d")

        # Check if the modification date is >5 years earlier than the creation date
        if (modification_date_obj - creation_date_obj).days > 1825:  # ~5 years in days
            return pdf_creation_date  # Default to creation date

        return pdf_modification_date
    except (AttributeError, ValueError):
        # Fallback to creation date if modification date is unavailable or invalid
        return pdf_creation_date


def extract_pdf_metadata(pdf_file_path: Path) -> tuple:
    """
    Extracts metadata from a given PDF file.

    Args:
        pdf_file_path (Path): The path to the PDF file.
        counter (int): A running count of files missing reliable date information.

    Returns:
        tuple: (file_name, pdf_year, pdf_month,
                pdf_creation_date, pdf_metadata, updated_counter)
    """

    # Extract filename and metadata
    file_name, pdf_metadata = get_name_and_meta(pdf_file_path)
    # Extract creation and modification dates

    return file_name, pdf_metadata


def extract_pdf_text(pdf_file_path: Path, pdf_url: str) -> list:
    """
    Extracts text content from each page of a PDF file.

    Args:
        pdf_file_path (Path): The path to the PDF file.
        pdf_url (str): The base URL where the document is hosted.

    Returns:
        list: A list of dictionaries containing page number, URL, and extracted text.
    """

    pages_text = []
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            if text:
                text = text.replace("\n", "")

            page_link = f"{pdf_url}#page={page_num}"
            pages_text.append(
                {
                    "page_number": page_num,
                    "page_url": page_link,
                    "page_text": text or "",
                }
            )

    return pages_text


def get_abstract_metadata(url: str) -> dict:  # noqa: C901
    """
    Extracts metadata from KNBS website for PDFs.

    Args:
        url (str): URL of the chosen KNBS PDF.

    Returns:
        dict: Dictionary of abstract metadata.
    """
    # Scrape PDF links from KNBS website
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    web_byte = urlopen(req).read()

    soup = BeautifulSoup(web_byte, features="html.parser")

    # Kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Get text
    text = soup.body.get_text(separator=" ")

    # Extract the substring containing the relevant metadata
    start = "About Report "
    end = "Share This Page"
    index_1 = text.find(start)
    index_2 = text.find(end, index_1 + len(start))

    if index_1 != -1 and index_2 != -1:
        pdf_substring = text[index_1 + len(start) : index_2]
        pdf_substring = "About-Report " + pdf_substring + " Overview-End"
    else:
        pdf_substring = ""  # Default to an empty string if delimiters are not found

    # Extract publication info
    start = "About-Report"
    end = " Overview"
    index_1 = pdf_substring.find(start)
    index_2 = pdf_substring.find(end, index_1 + len(start))

    if index_1 != -1 and index_2 != -1:
        publication_info = pdf_substring[index_1 + len(start) : index_2]
    else:
        publication_info = ""  # Default to an empty string if delimiters are not found

    # Extract overview info
    start = "Overview "
    end = " Overview-End"
    index_1 = pdf_substring.find(start)
    index_2 = pdf_substring.find(end, index_1 + len(start))

    if index_1 != -1 and index_2 != -1:
        overview_info = pdf_substring[index_1 + len(start) : index_2]
    else:
        overview_info = ""  # Default to an empty string if delimiters are not found

    # Split publication info into components
    publication_info_split = publication_info.split()

    # Extract publication date
    publication_date = (
        " ".join(publication_info_split[-2:])
        if len(publication_info_split) >= 2
        else "Unknown"
    )

    # if page layout different as per "https://www.knbs.or.ke/reports/kdhs-2014/"
    # will catch error and resolve
    if publication_date == "Unknown":
        # Extract text containing the relevant metadata with different start/end point
        start = "Main Report"
        end = "Visit the KNBS"
        index_1 = text.find(start)
        index_2 = text.find(end, index_1 + len(start))

        if index_1 != -1 and index_2 != -1:
            pdf_substring_new = text[index_1 + len(start) : index_2]

            # range of publication years should be between this range (adjustable)
            for year in range(1954, 2050):
                if str(year) in pdf_substring_new:
                    publication_date = str(year)
    # Extract publication theme
    publication_theme = (
        " ".join(publication_info_split[1:-2])
        if len(publication_info_split) > 2
        else "Unknown"
    )
    # Extract publication type
    publication_type = (
        publication_info_split[0] if len(publication_info_split) > 0 else "Unknown"
    )

    # Extract the PDF link
    pdf_link = None
    for link in soup.find_all("a", href=True):
        if link["href"].endswith(".pdf"):
            pdf_link = link["href"]
            break

    if not pdf_link:
        pdf_link = "No PDF link found"

    # Create dictionary for metadata
    url_dict_abstract = {
        "date": publication_date if publication_date != "Unknown" else "Unknown",
        "overview": overview_info,
        "publication_type": publication_type,
        "publication_theme": publication_theme,
        "pdf_abstract_url": pdf_link,
    }

    return url_dict_abstract


def convert_to_date(date_str: str) -> str:
    """
    Converts a date string in the format 'Month Year' or 'Year' into 'dd-mm-yyyy'.

    Args:
        date_str (str): The date string to convert (e.g., 'May 2025' or '2025').

    Returns:
        str: The converted date in 'dd-mm-yyyy' format.
    """
    try:
        # Try parsing 'Month Year' format
        date_obj = datetime.strptime(date_str, "%B %Y")
        return date_obj.strftime("%Y-%m-01")
    except ValueError:
        pass  # If parsing fails, continue to the next format

    try:
        # Try parsing 'Year' format
        date_obj = datetime.strptime(date_str, "%Y")
        return date_obj.strftime("%Y-01-01")
    except ValueError:
        pass  # If parsing fails, continue to the next format

    # If no valid format is found, raise an error
    raise ValueError(f"Invalid date format: {date_str}")


def build_json(
    pdf_file_path: Path, pdf_website_url: str, report_page: str, JSON_DIR: Path
) -> int:
    """
    Processes a PDF file, extracts metadata and content, then saves it as JSON.

    Args:
        pdf_file_path (Path): The path to the PDF file.
        pdf_website_url (str): The URL of the PDF document.
        report_page (str): The URL of the report page.
        counter (int): A running count of files missing reliable date information.
        JSON_DIR (Path): The path to the chosen json folder - latest or old

    Returns:
        int: Updated counter for files missing an explicit creation date.
    """

    # Notify which file is being processed
    # print(f"Processing: {pdf_file_path.name}")

    # Extract Metadata & Pre-Process
    file_name, pdf_metadata = extract_pdf_metadata(pdf_file_path)

    # Construct the document's URL
    pdf_url = pdf_website_url
    # Obtain additional metadata from pdf report page
    pdf_add_metadata = get_abstract_metadata(report_page)
    try:
        pdf_creation_date = convert_to_date(pdf_add_metadata["date"])
    except Exception:
        # Fallback: extract from PDF metadata or filename
        pdf_creation_date, _ = extract_pdf_creation_date(pdf_metadata, file_name, 0)
        print("Defaulting to PDF metadata or filename for creation date.")

    # Construct Ordered Metadata Dictionary
    pdf_info = {
        "id": str(np.random.randint(1000000, 9999999)),  # Unique ID first
        "title": file_name.replace(".pdf", "").replace("-", " ")
        or pdf_metadata.title,  # Title next
        "release_date": pdf_creation_date,  # Release date field
        "modification_date": extract_pdf_modification_date(
            pdf_metadata, pdf_creation_date
        ),
        "overview": pdf_add_metadata["overview"],  # Overview of the document
        "theme": pdf_add_metadata["publication_theme"],  # Publication theme
        "release_type": pdf_add_metadata["publication_type"],  # Report, Survey, etc.
        "url": pdf_url,  # URL for document access
        "latest": True,  # Boolean flag for latest version
        "url_keywords": extract_url_keywords_from_filename(
            file_name
        ),  # Extracted keywords
        "contact_name": "Kenya National Bureau of Statistics",  # Contact details
        "contact_link": "datarequest@knbs.or.ke",
        "content": extract_pdf_text(
            pdf_file_path, pdf_url
        ),  # Extracted text at the end
    }
    # check if overview is equal to the title
    if pdf_info["overview"] == pdf_info["title"] + " ":
        pdf_info["overview"] = " "  # Set overview to empty string

    # Export JSON
    JSON_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    json_file_path = JSON_DIR / f"{pdf_file_path.stem}.json"

    with open(json_file_path, "w") as json_file:
        json.dump(pdf_info, json_file, indent=4)

    return None


def normalize_dict_keys(file_dict: dict) -> dict:
    """
    Normalizes dictionary keys by converting mixed slashes ('/' and '\\')
    into Windows-compatible backslashes ('\\').

    Args:
        file_dict (dict): Dictionary with file paths as keys.

    Returns:
        dict: Dictionary with normalized file paths as keys.
    """
    return {os.path.normpath(k): v for k, v in file_dict.items()}


def process_pdfs(mode: str, config: dict):
    """
    Process PDFs based on the mode (SETUP or UPDATE).

    Args:
        mode (str): The mode of operation ('SETUP' or 'UPDATE').
        config (dict): Configuration dictionary loaded from the config file.

    Returns:
        None
    """
    # Load directories from config
    DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
    JSON_DIR = Path.cwd().joinpath("data/json_conversions")

    if mode == "SETUP":
        print("Running in SETUP mode: Processing all PDFs.")
        pdf_dir = DATA_DIR
        json_dir = JSON_DIR
        pdf_list = get_pdf_list(pdf_dir)

    elif mode == "UPDATE":
        # Dynamically generate "latest" directories
        pdf_dir = generate_latest_dir(DATA_DIR)
        json_dir = generate_latest_dir(JSON_DIR)
        print("Running in UPDATE mode: Processing only new PDFs.")

        # Compare old and new PDFs
        new_pdfs = get_pdf_list(pdf_dir)
        old_pdfs = get_pdf_list(DATA_DIR)
        pdf_list = compare_pdfs(new_pdfs, old_pdfs)

        if not pdf_list:
            print("No new PDFs to process. Exiting.")
            return

        print(f"Found {len(pdf_list)} new PDFs to process.")

    # Load URL dictionary
    url_dict_path = pdf_dir.joinpath("url_dict.json")
    if not url_dict_path.exists():
        print(f"URL dictionary not found at {url_dict_path}. Exiting.")
        return

    with open(url_dict_path, "r") as json_file:
        url_dict = json.load(json_file)

    normalize_dict_keys(url_dict)

    # Process PDFs
    count = 0
    for pdf in tqdm(
        pdf_list,
        desc="Converting PDF file(s) to json(s)",
        total=len(url_dict),
        colour="red",
        dynamic_ncols=True,
        bar_format=(
            "[{elapsed}<{remaining}] {n_fmt}/{total_fmt}| "
            "{l_bar}{bar} {rate_fmt}{postfix}"
        ),
    ):
        pdf_path = pdf_dir.joinpath(f"{pdf}.pdf")
        pdf_url = url_dict.get(f"{pdf}.pdf", {}).get("pdf_url", "Unknown URL")
        report_page = url_dict.get(f"{pdf}.pdf", {}).get(
            "report_page", "Unknown Overview URL"
        )
        build_json(pdf_path, pdf_url, report_page, json_dir)
        count += 1

    print(f"Processed {count} PDFs. JSON files saved to {json_dir}.")


if __name__ == "__main__":
    # Load configuration
    config_path = Path(__file__).resolve().parent.parent / "config" / "main.toml"
    config = load_config(config_path)

    # Get mode from configuration
    mode = config["preprocess"]["mode"].upper()

    # Process PDFs based on mode
    process_pdfs(mode, config)
