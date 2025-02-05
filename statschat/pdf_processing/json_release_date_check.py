# %%
# %%
# import modules
import json
from pathlib import Path
import datetime

# %%
DATA_DIR = Path.cwd().joinpath("data/pdf_test_downloads")
JSON_DIR = Path.cwd().joinpath("data/json_conversions")

# %%
for json_file in JSON_DIR.glob("*.json"):
    # Open and read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)
        
        if len(data["release_date"]) < 10:
            print(f"""The json file {json_file.name} 
                  has {data["release_date"]} release date.
                  
                  It will need to be removed from the json_conversions dir before
                  running the embeddings.py script otherwise the FAISS files will not
                  be created""")

# %% [markdown]
# # if wanting to delete jsons with no release date so embeddings.py will create FAISS files
# 
# for json_file in JSON_DIR.glob("*.json"):
#     # Open and read the JSON file
#     with open(json_file, 'r') as file:
#         data = json.load(file)
#         
#         if len(data["release_date"]) < 10:
#             #print(data["url"])
#             json_file.unlink()



