# %%
# import modules
import os
import PyPDF2
import json
from pathlib import Path
import datetime
import numpy as np
import re

# %%
# set relative paths

DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
JSON_DIR = Path.cwd().joinpath("data/json_conversions")


def get_name_and_meta(file_path):
    """
    Extracts file name and metadata from PDF
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


def determine_document_type_from_filename(filename: str) -> str:
    """
    Determines the document type based on whether 'Report' or 'Survey'
    (case-insensitive) is in the filename.

    Args:
        filename (str): The filename associated with the document.

    Returns:
        str: The document type, either 'report' if 'Report' (case-insensitive)
        is in the filename, 'survey' if 'Survey' (case-insensitive) is in the
        filename, or 'pdf_publication' as the default.

    Example:
        >>> determine_document_type_from_filename("Economic-REPORT-2019.pdf")
        'report'
        >>> determine_document_type_from_filename("ECONOMIC-survey-2019.pdf")
        'survey'
        >>> determine_document_type_from_filename("Economic-Statistics-2019.pdf")
        'pdf_publication'
    """
    filename_lower = filename.lower()  # Convert to lowercase

    if "report" in filename_lower:
        return "report"
    if "survey" in filename_lower:
        return "survey"

    return "pdf_publication"


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

    return pdf_creation_date, counter


def extract_pdf_modification_date(
    metadata, filename: str, pdf_creation_date: str
) -> str:
    """
    Extracts the modification date from PDF metadata if available. If unavailable,
    falls back to the provided PDF creation date.

    Args:
        metadata: PDF metadata object from PyPDF2.PdfReader.
        filename (str): The filename associated with the PDF.
        pdf_creation_date (str): The creation date to use as a fallback if
        modification date is missing.

    Returns:
        str: The extracted or fallback modification date in 'YYYY-MM-DD' format.

    Example:
        >>> extract_pdf_modification_date(metadata,
                                          "Economic-Report-2019.pdf",
                                          "2019-04-24")
        '2023-09-04'
        >>> extract_pdf_modification_date(metadata,
                                          "Economic-Report.pdf",
                                          "2019-04-24")
        '2019-04-24'  # Fallback to creation date
    """

    try:
        pdf_modification_date = str(metadata.modification_date)[:10]
    except AttributeError:
        print(f"An error fetching the modification date occurred for file {filename}")
        pdf_modification_date = pdf_creation_date  # Fallback to creation date

    return pdf_modification_date


def extract_pdf_metadata(pdf_file_path: Path, counter: int) -> tuple:
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
    pdf_creation_date, counter = extract_pdf_creation_date(
        pdf_metadata, file_name, counter
    )

    return file_name, pdf_creation_date, pdf_metadata, counter


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


def build_json(pdf_file_path: Path, pdf_website_url: str, counter: int) -> int:
    """
    Processes a PDF file, extracts metadata and content, then saves it as JSON.

    Args:
        pdf_file_path (Path): The path to the PDF file.
        counter (int): A running count of files missing reliable date information.

    Returns:
        int: Updated counter for files missing an explicit creation date.
    """

    # Notify which file is being processed
    print(f"Processing: {pdf_file_path.name}")

    # Extract Metadata & Pre-Process
    file_name, pdf_creation_date, pdf_metadata, counter = extract_pdf_metadata(
        pdf_file_path, counter
    )

    # Construct the document's URL
    pdf_url = pdf_website_url

    # Construct Ordered Metadata Dictionary
    pdf_info = {
        "id": str(np.random.randint(1000000, 9999999)),  # Unique ID first
        "title": file_name.replace(".pdf", "").replace("-", " ")
        or pdf_metadata.title,  # Title next
        "release_date": pdf_creation_date,  # Important date field
        "modification_date": extract_pdf_modification_date(
            pdf_metadata, file_name, pdf_creation_date
        ),
        "release_type": determine_document_type_from_filename(
            file_name
        ),  # Report, Survey, etc.
        "url": pdf_url,  # URL for document access
        "latest": True,  # Boolean flag for latest version
        "url_keywords": extract_url_keywords_from_filename(
            file_name
        ),  # Extracted keywords
        "contact_name": "Joe Bloggs",  # Contact details
        "contact_link": "mailto:test@knbs.com",
        "content": extract_pdf_text(
            pdf_file_path, pdf_url
        ),  # Extracted text at the end
    }

    # Export JSON
    JSON_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    json_file_path = JSON_DIR / f"{pdf_file_path.stem}.json"

    with open(json_file_path, "w") as json_file:
        json.dump(pdf_info, json_file, indent=4)

    return counter  # Return updated counter


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


# Initialize counter
count = 0  # Initialize counter

# Load in url dict
dict_filepath = f"{DATA_DIR}/url_dict.json"
if os.path.exists(dict_filepath):
    with open(dict_filepath, "r") as json_file:
        url_dict = json.load(json_file)

# noralize keys
normalize_dict_keys(url_dict)
# Loop through all PDF files and process them
for pdf_file_path in DATA_DIR.glob("*.pdf"):
    pdf_url = url_dict[os.path.basename(pdf_file_path)]
    count = build_json(pdf_file_path, pdf_url, count)

# Print final count of files with metadata (date) errors
print(f"Total number of files with errors: {count}")