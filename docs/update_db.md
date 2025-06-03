## How to update PDF Database with new PDF files

### For Server - run on a...basis (automatically done on KNBS server)

Before running **`pdf_runner.py`** ensure that the PDF_FILES_MODE (in **`main.toml`**) is set to the desired option **"UPDATE"**.
You can either run the python file in the IDE or use in the terminal as below.

    ```shell
    python statschat/pdf_runner.py
    ```

This script will webscrape PDF documents from the KNBS website, convert them to JSON files and either append or replace the vector store - based on the PDF_FILES_MODE parameter.

PDF_FILES_MODE = "UPDATE" -> Will only scrape the latest 5 pages of PDF files, compare existing PDF files in the vector store with
those downloaded and only process new files - appending these to the database and "flushing" the latest data folders ready for a new run.

### For Development
For development/testing purposes this update can also be done by running these 3 scripts individually

```
1) Run script `pdf_downloader.py` and PDF_FILES_MODE (in main.toml) is set to the desired option "UPDATE".
```

**Downloads newest PDF files into the `latest_pdf_downloads` folder. Informs how many new PDF files there are then converts them to json files in the `latest_json_conversions` folder**

```
2) Run script 'preprocess.py'
```

**Splits the latest json conversion files, moves them to `latest_json_splits`, converts them to a pickle file and finally merges that pickle file with the pickle file currently in the `db_langchain_latest` folder**

```
3) Run script 'merge_database_files.py' to move
   new PDF, json conversions and splits to relevant folders after database update.
```

- Moves new PDF files to the from **`latest_pdf_downloads`** to **`pdf_downloads`** folder and then removes all files in the **`latest_pdf_downloads`**

- Moves new json conversions from **`latest_json_conversions`** to **`json_conversions`** folder and then removes all files in **`latest_json_conversion`**

- Moves new json splits from **`latest_json_splits`** to **`json_splits`** folder and then removes all files in **`latest_json_splits`**

```
Repeat process each time new KNBS PDF files are published to
update the database that Statschats will use to answer questions
```
