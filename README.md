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

This is an experimental application for semantic search of KNBS statistical publications.
It uses LangChain to implement a fairly simple Retriaval Augmented Generation (RAG) using embedding search
and QA information retrieval process.

Upon receiving a query, documents are returned as search results
using embedding similarity to score relevance.
Next, the relevant text is passed to a Large Language Model (LLM),
which is prompted to write an answer to the original question, if it can,
using only the information contained within the documents.

For this prototype, relevant web pages are scraped and the data stored in `data/bulletins`,
the docstore / embedding store that is created is likewise in local folders and files,
and the LLM is either run in memory or accessed through VertexAI.

## 4) Usage

This main module statschat can be either called directly or deployed as an API (using fastapi).
A lightweight flask front end is implemented separately in a subfolder and relies on the API running.

The first time you instantiate the `Inquirer` class, any ML models specified in the code will be
downloaded to your machine. This will use a few GB of data and take a few
minutes. App and search pipeline parameter are stored and can be updated by
editing `statschat/_config/main.toml`.

We have included few EXAMPLE scraped data files in `data/bulletins` so that
the preprocessing and app can be run as a small example system without waiting
on webscraping.

### With Vertex AI

If you wish to use Google's model API update the model variables in
`statschat/_config/main.toml`:
* to use the question-answering system with Google's PaLM2 API set the
  `generative_model_name` parameter to `text-unicorn` or `gemini-pro` (their
  name for the model).
* for PaLM2 (Gecko) to create embeddings, set the `embedding_model_name`
  parameter to `textembedding-gecko@001`. You may also wish to disable the
  removal of near-identical documents in the preprocessing pipeline (line 59,
  `statschat/embedding/preprocess.py`), to reduce calls to the embedding API.

In addition to changing this parameter, you will need a Google Cloud Platform
(GCP) project set up, with the Vertex AI API enabled. You will need to have the
GCP Command Line Interface installed in the machine running this code, logged
in to an account with sufficient permissions to access the API (you may need to
set up [application default credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to)).
Usually this can be achieved by running:
```shell
gcloud config set project "<PROJECT_ID>"
gcloud auth application-default login
```

## 5) Example endpoint commands

1. #### Webscraping the source documents

Before running `pdf_runner.py` you should make sure that the PDF_FILES_MODE (in `main.toml`) is set to the desired option.

    ```shell
    python statschat/pdf_runner.py
    ```

This script will webscrape PDF documents from the KNBS website, convert them to JSON files and either append or replace the vector store - based on the PDF_FILES_MODE parameter.

PDF_FILES_MODE = "UPDATE" -> Will only scrape the latest 5 pages of PDF files, compare existing PDF files in the vector store with those downloaded and only process new files - appending these to the database and "flushing" the latest data folders ready for a new run.

PDF_FILES_MODE = "SETUP" -> Will scrape all pdf files from the KNBS website and reset the vector store, creating a new one from the PDF documents that are scraped and processed into JSON files.

Further information on how to "UPDATE" vector store can be found [here](https://github.com/KNBS-StatsChat/statschat-ke/blob/readme_docs_update/docs/api/update_db.md)

> [!NOTE]
> The second script my flag some files that don't have compliant metadata.
> For now the guidance is to delete those PDFs, the produced JSONS and re-run the script.

2. #### Run the sample questions manually

    Make sure that you're terminal is running from `statschat-ke`.
    Then run the `llm.py` script using:

    ```shell
    python statschat/generative/llm.py
    ```

3. #### Run the interactive Statschat API

    In order to run the interactive Statschat API you will need to make sure you have:

        - `uvicorn`: This is a bit of software to locally replicate a server.
        - `fastapi`: This is a Python library to generate the API functionality.

    To get these in your machine simply run `pip install fastapi uvicorn`.

    Then you will need to make sure your terminal is on the `statschat-ke` folder.
    From there, you can generate the synthetic "server" locally from your terminal:

    ```shell
    uvicorn fast-api.main_api:app --reload
    ```

    The fastapi is set to respond to http requests on a particular port.
    You will see this in your terminal line, something like:

    ```shell
    Uvicorn running on http://127.0.0.1:8000
    ```

    Your port might be slightly different to 127.0.0.1:8000

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

4. #### Run the flask web interface

    ```shell
    python flask-app/app.py
    ```
    To use the user UI
    navigate in your browser to http://localhost:5000. Note that it requires the API to be running and the endpoind specified in the app.

5. #### Run the search evaluation pipeline
    ```shell
    python statschat/model_evaluation/evaluation.py
    ```
    The StatsChat pipeline is currently evaluated based on small number of test
    question. The main 'app_config.toml' determines pipeline setting used in
    evaluation and results are written to `data/model_evaluation` folder.


6. #### Testing
    ```shell
    python -m pytest
    ```
    Preferred unittesting framework is PyTest.

# License

<!-- Unless stated otherwise, the codebase is released under [the MIT Licence][mit]. -->

The code, unless otherwise stated, is released under [the MIT License][mit].

[mit]: LICENSE
