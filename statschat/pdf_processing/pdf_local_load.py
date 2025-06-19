import json
from glob import glob
from pathlib import Path
from tqdm import tqdm
from statschat import load_config

config = load_config(name="main")
PDF_FILES = config["preprocess"]["download_mode"].upper()
base_url = config["preprocess"]["download_site"].upper()

BASE_DIR = Path.cwd().joinpath("data")
DATA_DIR = BASE_DIR.joinpath(
    "pdf_store" if PDF_FILES == "SETUP" else "latest_pdf_store"
)
DATA_DIR.mkdir(parents=True, exist_ok=True)
url_dict = {}

pdf_files = glob(str(BASE_DIR / "local_pdfs" / "*.pdf"))
print(f"Found {len(pdf_files)} PDFs in data/local_pdfs.")

for pdf in tqdm(
    pdf_files,
    desc="HANDLING LOCAL PDF FILES:",
    bar_format=format,
    colour="yellow",
    total=len(pdf_files),
    dynamic_ncols=True,
):
    pdf_path = Path(pdf)
    pdf_name = pdf_path.name
    dest_path = DATA_DIR / pdf_name

    # Copy the PDF file to DATA_DIR
    if not dest_path.exists():
        dest_path.write_bytes(pdf_path.read_bytes())

    url_dict[pdf_name] = {"pdf_url": pdf_name, "report_page": str(dest_path)}

OUTPUT_URL_DIR = BASE_DIR.joinpath(
    "pdf_store" if PDF_FILES == "SETUP" else "latest_pdf_store"
)
OUTPUT_URL_DIR.mkdir(parents=True, exist_ok=True)
url_dict_path = OUTPUT_URL_DIR / "url_dict.json"
with open(url_dict_path, "w") as json_file:
    json.dump(url_dict, json_file, indent=4)
    print(f"Saved new url_dict.json to {url_dict_path}")


if PDF_FILES == "UPDATE":
    print("Finished processing new PDF files.")

if PDF_FILES == "SETUP":
    print("Finished processing all PDF files.")
