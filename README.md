# `KNBS StatsChat`

[![Stability](https://img.shields.io/badge/stability-experimental-orange.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#experimental)
[![Shared under the MIT License](https://img.shields.io/badge/license-MIT-green)](https://github.com/datasciencecampus/Statschat/blob/main/LICENSE)
[![Mac-OS compatible](https://shields.io/badge/MacOS--9cf?logo=Apple&style=social)]()

## Code state

> [!WARNING]
> Please be aware that for development purposes, these experiments use
> experimental Large Language Models (LLM's) not intended for production. They
> can present inaccurate information, hallucinated statements and offensive
> text by random chance or through malevolent prompts.

- **Under development** / **Experimental**
- **Tested on macOS only**
- **Peer-reviewed**
- **Depends on external API's**

## Introduction

This is an experimental application for semantic search of KNBS [statistical publications](https://www.knbs.or.ke/all-reports/).
It uses LangChain to implement a fairly simple Retriaval Augmented Generation (RAG) using embedding search
and QA information retrieval process.

Upon receiving a query, documents are returned as search results
using embedding similarity to score relevance.
Next, the relevant text is passed to a Large Language Model (LLM),
which is prompted to write an answer to the original question, if it can,
using only the information contained within the documents.

For this prototype, relevant web pages with PDF's are scraped and the data stored in `data/pdf_downloads`,
the docstore / embedding store that is created is likewise and stored in `data/db_langchain` after SETUP and then
also in `data/db_langchain_latest` after UPDATE. The LLM is either run locally with `local_llm.py` or an 
API with `main_api_local.py` (both backend).

## Step 1: Vector store
> [!NOTE]
> **Before setting up or updating the vector store ensure the [virtual or conda environment has been created.](https://github.com/KNBS-StatsChat/statschat-ke/blob/readme_docs_update/docs/api/setup_guide.md)**

Before running `pdf_runner.py` in an integrated development environment (IDE) ensure that the PDF_FILES_MODE (in `main.toml`) 
is set to the desired option. It can also be run in the command line as below.

    ```shell
    python3 statschat/pdf_runner.py
    ```

> [!NOTE]
> If the above doesn't work then use `python statschat/pdf_runner.py`

This script will webscrape PDF documents from the KNBS website, convert them to JSON files and either append or replace the vector store - based on the `PDF_FILES_MODE` parameter.

`PDF_FILES_MODE = "SETUP"` -> Will scrape all pdf files from the KNBS website and reset the vector store, creating a new one from the PDF documents that are scraped and processed into JSON files. This will only need to be done `once` as afterwards it will just need updating. 

`PDF_FILES_MODE = "UPDATE"` -> Will only scrape the latest 5 pages of PDF files from the KNBS website, compare existing PDF files in the vector store with those downloaded and only process new files - appending these to the database and "flushing" the latest data folders ready for a new run. This will need to be done as new PDFs are added to the KNBS website.

## Step 2: Usage

#### Run the sample questions manually (backend)

This assumes the [vector store](https://github.com/KNBS-StatsChat/statschat-ke/blob/readme_docs_update/docs/api/setup_guide.md) has already been created otherwise this will need to be done before.
Make sure that you're terminal is running from **`statschat-ke`**. Then use the **`cloud_llm.py`** 
(requires huggingface api token) or **`local_llm.py`** script and change the **question** parameter 
with the desired question:

![image](https://github.com/user-attachments/assets/36ec03e4-2d6a-4814-9220-8cc478196e52)

The answer, context and response will be output in the terminal.

#### Run interactive Statschat API
This main module statschat can be either called directly or deployed as an API (using fastapi).
A lightweight flask front end is implemented separately in a subfolder and relies on the API running.


In order to run the interactive Statschat API you will need to make sure you have:

**`uvicorn`**: This is a bit of software to locally replicate a server

**`fastapi`**: This is a Python library to generate the API functionality

To get these in your machine simply run: 

```
pip install fastapi uvicorn
```

Then you will need to make sure your terminal is on the **`statschat-ke`** folder.
From there, you can generate the synthetic "server" locally from your terminal:

```shell
uvicorn fast-api.main_api_local:app --reload
```

The fastapi is set to respond to http requests on a particular port.
You will see this in your terminal line, something like:

 ```shell
 Uvicorn running on http://127.0.0.1:8000
 ```

> [!NOTE]
> **Your port might be slightly different to 127.0.0.1:8000**

After a few seconds you should be able to go to your browser and ask questions.
On the search bar type something like:

```
http://127.0.0.1:8000/search?q=what+was+inflation+in+december+2023
```

This should produce a response text that is displayed on your browser.

The generic formula to ask a question is:

```
<API_URL>/search?q=<your_question>
```

# License

<!-- Unless stated otherwise, the codebase is released under [the MIT Licence][mit]. -->

The code, unless otherwise stated, is released under [the MIT License][mit].

[mit]: LICENSE
