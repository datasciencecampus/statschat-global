# %%
# import packages
from pathlib import Path

# %%
# Database directories
DATA_DIR = Path.cwd().joinpath("data/pdf_downloads")
JSON_DIR = Path.cwd().joinpath("data/json_conversions")
JSON_SPLIT_DIR = Path.cwd().joinpath("data/json_split")

# Latest directories
LATEST_JSON_SPLIT_DIR = Path.cwd().joinpath("data/latest_json_split")
LATEST_JSON_DIR = Path.cwd().joinpath("data/latest_json_conversions")
LATEST_DATA_DIR = Path.cwd().joinpath("data/latest_pdf_downloads")

# %%
# Moves latest json conversions files 'json_conversions' folder

for json_file in LATEST_JSON_DIR.glob("*.json"):
    
    source_file = json_file

    destination_file = JSON_DIR.joinpath(json_file.name)

    source_file.rename(destination_file)
    
    print(f"{json_file.name} has been moved to {JSON_DIR}")

# %%
# Moves latest json split files to all 'json_split' folder

for json_split_file in LATEST_JSON_SPLIT_DIR.glob("*.json"):
    
    source_file = json_split_file

    destination_file = JSON_SPLIT_DIR.joinpath(json_split_file.name)

    source_file.rename(destination_file)
    
    print(f"{json_split_file.name} has been moved to {JSON_SPLIT_DIR}")

# %%
# Moves latest PDF file downloads to 'pdf_downloads' folder

for pdf_file in LATEST_DATA_DIR.glob("*.pdf"):
    
    source_file = pdf_file

    destination_file = DATA_DIR.joinpath(pdf_file.name)

    source_file.rename(destination_file)
    
    print(f"{pdf_file.name} has been moved to {DATA_DIR}")


