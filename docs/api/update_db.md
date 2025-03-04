## Instructions for how to update PDF Database with PDF files

### Run on a...basis

...
1) Run script 'pdf_downloader.py' but ensure 'PDF_FILES = "UPDATE"'
...
This downloads all PDF files into the 'latest_pdf_downloads' folder

...
2) Run script 'pdf_database_update.py'
...
This tells you how many new PDF files there are then converts them to json files in the 'latest_json_conversions' folder 

...
3) Run script 'preprocess_update_db.py'
...
This converts the new json files into a pickle file then adds them to the 'db_langchain_latest' folder

...
4) Run script 'merge_database_files.py' to move new PDF, json conversions and splits to relevant folders after database update
...
This moves the new PDF files to the from 'latest_pdf' to 'pdf_downloads' folder and then removes all files in the 'latest_pdf_'
This moves the new json conversions from 'latest_json' to the 'json_con' folder and then removes all files in 'latest_json_conversion'
This moves the new json splits from 'latest_json_splits' to the 'json_splits' folder and then removes all files in 'latest_json_splits'

## Repeat this process each time new KNBS PDF files are published to update the database that Statschats will use. 