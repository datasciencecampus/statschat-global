# %%
# import modules
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
        tuple[str, int]: The extracted or fallback PDF creation date in 'YYYY-MM-DD' format,
        and an updated counter for files missing an explicit creation date.
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

    # Use modification date from metadata if no valid creation date or filename year is found.
    if metadata:
        raw_mod_date = metadata.get("/ModDate") if isinstance(metadata, dict) else None
        cleaned_mod_date = preprocess_date(str(raw_mod_date)) if raw_mod_date else None

        if not pdf_creation_date and cleaned_mod_date:
            pdf_creation_date = f"{cleaned_mod_date[:4]}-{cleaned_mod_date[4:6]}-{cleaned_mod_date[6:8]}"
            counter += 1  # Increment counter since modification date is being used.

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


def determine_dates(pdf_creation_date, pdf_modification_date):
    """
    Determines the correct year and month based on creation and modification date
    """
    pdf_year = pdf_creation_date[:4]
    pdf_month = pdf_creation_date[5:7]

    return pdf_year, pdf_month


def extract_pdf_metadata(pdf_file_path: Path, counter: int) -> tuple:
    """
    Extracts metadata from a given PDF file.

    Args:
        pdf_file_path (Path): The path to the PDF file.
        counter (int): A running count of files missing reliable date information.

    Returns:
        tuple: (file_name, pdf_year, pdf_month, pdf_creation_date, pdf_metadata, updated_counter)
    """

    # Extract filename and metadata
    file_name, pdf_metadata = get_name_and_meta(pdf_file_path)
    print(pdf_metadata, "metadata")
    # Extract creation and modification dates
    pdf_creation_date, counter = extract_pdf_creation_date(
        pdf_metadata, file_name, counter
    )
    pdf_modification_date = extract_pdf_modification_date(
        pdf_metadata, file_name, pdf_creation_date
    )

    # Determine document date-based folder structure
    pdf_year, pdf_month = determine_dates(pdf_creation_date, pdf_modification_date)

    return file_name, pdf_year, pdf_month, pdf_creation_date, pdf_metadata, counter


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


def build_json(pdf_file_path: Path, counter: int) -> int:
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
    file_name, pdf_year, pdf_month, pdf_creation_date, pdf_metadata, counter = (
        extract_pdf_metadata(pdf_file_path, counter)
    )

    # Construct the document's URL
    pdf_url = (
        f"https://www.knbs.or.ke/wp-content/uploads/{pdf_year}/{pdf_month}/{file_name}"
    )

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


# Initialize counter
count = 0  # Initialize counter

# Loop through all PDF files and process them
for pdf_file_path in DATA_DIR.glob("*.pdf"):
    count = build_json(pdf_file_path, count)

# Print final count of files with metadata (date) errors
print(f"Total number of files with errors: {count}")

'''
def build_json(
    file_name, pdf_year, pdf_month, pdf_creation_date, pdf_file_path, pdf_metadata
):
    """
    Constructs a JSON representation of the PDF file
    Saves it to a file
    """

    # create new dict
    pdf_info = {}
    pdf_info["id"] = str(np.random.randint(1000000, 9999999))
    pdf_info["latest"] = True
    pdf_info["url"] = (
        f"https://www.knbs.or.ke/wp-content/uploads/{pdf_year}/{pdf_month}/" + file_name
    )
    pdf_info["release_date"] = pdf_creation_date
    pdf_info["release_type"] = determine_document_type_from_filename(file_name)
    pdf_info["url_keywords"] = extract_url_keywords_from_filename(file_name)
    pdf_info["contact_name"] = "Joe Bloggs"
    pdf_info["contact_link"] = "mailto:test@knbs.com"
    print(pdf_info)
    # Extract a meaningful title from the filename (best practice)
    clean_title = file_name.replace(".pdf", "").replace("-", " ")
    print(pdf_metadata.title)
    # Store extracted title in JSON
    pdf_info["title"] = clean_title if clean_title else pdf_metadata.title

    print(f"DEBUG: pdf_file_path = {pdf_file_path}, type = {type(pdf_file_path)}")
    # create list to store
    pages_text = []
    with open(pdf_file_path, "rb") as pdf_file:
        # read file
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # read every page
        for page_num in range(len(pdf_reader.pages)):
            # read page wise data from pdf file
            page = pdf_reader.pages[page_num]

            # extract data from page to text
            text = page.extract_text().split("\n")
            # convert list of strings into one large string
            text = "".join(text)

            # get page link
            page_link = pdf_info["url"]

            # add text of page to array
            pages_text.append(
                {
                    "page_number": page_num + 1,
                    "page_url": page_link + "#page=" + str(page_num + 1),
                    "page_text": text,
                }
            )

        # create nested dictionary
        pdf_info["content"] = pages_text

        # Check if JSON_DIR exists, if not, create the folder
        if not JSON_DIR.exists():
            JSON_DIR.mkdir(parents=True, exist_ok=True)

        with open(JSON_DIR / f"{pdf_file_path.stem}.json", "w") as json_file:
            json.dump(pdf_info, json_file, indent=4)

        # print JSON
        # print(json.dumps([pdf_info], indent=4))


# %%
# create counter
count = 0

pdf_list = DATA_DIR.glob("*.pdf")
# loop through folder to get filepaths
for pdf_file_path in DATA_DIR.glob("*.pdf"):
    # extract filename and metadata
    file_name, pdf_metadata = get_name_and_meta(pdf_file_path)
    # extract creation date
    pdf_creation_date, count = extract_pdf_creation_date(pdf_metadata,
                                                         file_name,
                                                         count)
    pdf_modification_date = extract_pdf_modification_date(pdf_metadata,
                                                          file_name,
                                                          pdf_creation_date)
    pdf_year, pdf_month = determine_dates(pdf_creation_date, pdf_modification_date) #change this to be the default url in future - also then no need to reimpute?
    build_json(
        file_name, pdf_year, pdf_month, pdf_creation_date, pdf_file_path, pdf_metadata
    )

print(f"Total number of files with errors: {count}")
'''
