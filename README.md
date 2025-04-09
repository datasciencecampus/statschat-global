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

## Usage

#### Run the sample questions manually (backend)

This assumes the [vector store](https://github.com/KNBS-StatsChat/statschat-ke/blob/readme_docs_update/docs/api/setup_guide.md) has already been created otherwise this will need to be done before.
Make sure that you're terminal is running from **`statschat-ke`**. Then use the **`llm.py`** 
script and change the **question** parameter with the desired question:

![image](https://github.com/user-attachments/assets/83e2e4e8-1ecf-43e1-bcdc-e8f39e5d5e12)

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

### Run the search evaluation pipeline
    ```shell
    python statschat/model_evaluation/evaluation.py
    ```
    The StatsChat pipeline is currently evaluated based on small number of test
    question. The main 'app_config.toml' determines pipeline setting used in
    evaluation and results are written to `data/model_evaluation` folder.

### Testing
    ```shell
    python -m pytest
    ```
    Preferred unittesting framework is PyTest.

# License

<!-- Unless stated otherwise, the codebase is released under [the MIT Licence][mit]. -->

The code, unless otherwise stated, is released under [the MIT License][mit].

[mit]: LICENSE
