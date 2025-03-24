## Instructions for how to update PDF Database with new PDF files

### Run on a...basis (automatically done on KNBS server)

```
1) Run script `pdf_downloader.py` and ensure PDF_FILES = UPDATE
```

**Downloads newest PDF files into the `latest_pdf_downloads` folder**

```
2) Run script 'pdf_database_update.py'
```

**Informs how many new PDF files there are then converts them to json files in the `latest_json_conversions` folder**

```
3) Run script 'preprocess_update_db.py'
```

**Splits the latest json conversion files, moves them to `latest_json_splits`, converts them to a pickle file and finally merges that pickle file with the pickle file currently in the `db_langchain_latest` folder**

```
4) Run script 'merge_database_files.py' to move new PDF, json conversions and splits to relevant folders after database update
```

- **Moves new PDF files to the from `latest_pdf_downloads` to `pdf_downloads` folder and then removes all files in the `latest_pdf_downloads`**

- **Moves new json conversions from `latest_json_conversions` to `json_conversions` folder and then removes all files in `latest_json_conversion`**

- **Moves new json splits from `latest_json_splits` to `json_splits` folder and then removes all files in `latest_json_splits`**

```
Repeat process each time new KNBS PDF files are published to update the database that Statschats will use to answer questions
```
