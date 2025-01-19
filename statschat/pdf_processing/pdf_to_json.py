# %%
# import modules
import PyPDF2
import json
from pathlib import Path
import datetime

# %%
# set relative paths

DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
JSON_DIR = Path.cwd().joinpath("data/json_conversions")


def get_name_and_meta(file_path):
    file_name = pdf_file_path.name
    pdf_metadata = PyPDF2.PdfReader(pdf_file_path)
    pdf_metadata = pdf_metadata.metadata

    return (file_name, pdf_metadata)


def get_date(metadata, name, counter):
    # pdf date, time and year (may need to add for modification date)
    try:
        pdf_creation_date = str(metadata.creation_date)
        print(f"no issue with metadata for {name}")

    except Exception as e:
        counter += 1
        pdf_creation_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S%z")
        print(f"An error occurred for file {name}: {e}")
        print(f"Total number of files with errors: {count}")

    return pdf_creation_date, counter


def determine_dates(pdf_creation_date, pdf_modification_date):
    pdf_creation_year = pdf_creation_date[:4]
    pdf_creation_month = pdf_creation_date[5:7]

    pdf_modification_month = pdf_modification_date[5:7]
    pdf_modification_year = pdf_modification_date[:4]

    # in case creation date empty
    if pdf_creation_year == "None":
        pdf_creation_year = pdf_modification_year
    if pdf_creation_month == "":
        pdf_creation_month = pdf_modification_month

    # if months below for pdf creation and modification are different
    # An error will come in the pdf hyperlink
    if int(pdf_creation_month) < int(pdf_modification_month) and int(
        pdf_creation_year
    ) == int(pdf_modification_year):
        pdf_month = pdf_modification_month
        pdf_year = pdf_modification_year
    # if years below for pdf creation year and modification year are different
    # An error will come in the pdf hyperlink
    elif int(pdf_creation_year) < int(pdf_modification_year) and int(
        pdf_creation_month
    ) > int(pdf_modification_month):
        pdf_year = pdf_modification_year
        pdf_month = pdf_modification_month
    else:
        pdf_year = pdf_modification_year
        pdf_month = pdf_modification_month

    return pdf_year, pdf_month


def build_json(
    pdf_year, pdf_month, pdf_creation_date, pdf_file_path, pdf_metadata, file_name
):
    # create new dict
    pdf_info = {}
    pdf_info["id"] = " "
    pdf_info["url"] = (
        f"https://www.knbs.or.ke/wp-content/uploads/{pdf_year}/{pdf_month}/" + file_name
    )
    pdf_info["release_date"] = pdf_creation_date[:10]  # date only
    pdf_info["release_type"] = " "
    pdf_info["url_keywords"] = " "
    pdf_info["title"] = str(pdf_metadata.title)

    # if pdf title metadata blank
    if pdf_info["title"] == "None":
        title_from_filename = file_name.replace(".pdf", "")
        pdf_info["title"] = title_from_filename
    else:
        pdf_info["title"] = str(pdf_metadata.title)

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

            # get page link
            page_link = pdf_info["url"]

            # add text of page to array
            pages_text.append(
                {
                    "page_number": page_num + 1,
                    "page_link": page_link + "#page=" + str(page_num + 1),
                    "text": text,
                }
            )

        # create nested dictionary
        pdf_info["contents"] = pages_text

        with open(JSON_DIR / f"{pdf_file_path.stem}.json", "w") as json_file:
            json.dump([pdf_info], json_file, indent=4)

        # print JSON
        # print(json.dumps([pdf_info], indent=4))


# %%
# create counter
count = 0

pdf_list = DATA_DIR.glob("*.pdf")

# loop through folder to get filepaths
for pdf_file_path in DATA_DIR.glob("*.pdf"):
    file_name, pdf_metadata = get_name_and_meta(pdf_file_path)

    pdf_creation_date, count = get_date(pdf_metadata, file_name, count)

    try:
        pdf_modification_date = str(pdf_metadata.modification_date)
    except AttributeError:
        print(f"An error fetching the modification date occurred for file {file_name}")
        pdf_modification_date = pdf_creation_date

    pdf_year, pdf_month = determine_dates(pdf_creation_date, pdf_modification_date)

    build_json(
        pdf_year, pdf_month, pdf_creation_date, pdf_file_path, pdf_metadata, file_name
    )

print(f"Total number of files with errors: {count}")
