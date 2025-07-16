# `StatsChat`

[![Stability](https://img.shields.io/badge/stability-experimental-orange.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#experimental)
[![Shared under the MIT License](https://img.shields.io/badge/license-MIT-green)](https://github.com/datasciencecampus/statschat-global/blob/main/LICENSE)

## Code state

> [!WARNING]
> **Please be aware that for development purposes, these experiments use**
> **experimental Large Language Models (LLM's) not intended for production. They**
> **can present inaccurate information, hallucinated statements and offensive**
> **text by random chance or through malevolent prompts.**

- **Under development** / **Experimental**
- **Tested on macOS & windows only**
- **Peer-reviewed**
- **Depends on external API's**

## Disclaimer
The code contained within this repository is provided 'as is'. We stress that:

- Any use of this code is entirely at the risk of the user, and users are fully responsible for checking whether the codebase is suitable for their use case, as well as the quality and accuracy of any outputs generated.
- [Cloud based implementation](https://github.com/datasciencecampus/statschat-global/blob/main/statschat/generative/cloud_llm.py)([also via FASTApi](https://github.com/datasciencecampus/statschat-global/blob/main/fast-api/main_api_cloud.py)) is a quick way to test without having to download the LLM itself but there are potential security issues so please be aware of this. **The ONS advises a [local based model](https://github.com/datasciencecampus/statschat-global/blob/main/statschat/generative/local_llm.py) for querying**. However this is entirely up to your organisation.
- (Co) authors of this codebase at the Office for National Statistics Data Science Campus do not commit to responding to requests for additional features or long-term maintenance of the codebase

## A tool designed for the semantic search of statistical publications with PDF's 
This repository is a development to the code included in the Python package **[statschat](https://github.com/datasciencecampus/statschat-app)**, with the original codebase by Iva Spakulova and Martin Wood.

This version of `statschat` adds functionality to webscrape **PDF documents** from websites with **[pdf_downloader.py](https://github.com/datasciencecampus/statschat-global/blob/main/statschat/pdf_processing/pdf_downloader.py)** and then converts these into jsons with **[pdf_to_json.py](https://github.com/datasciencecampus/statschat-global/blob/main/statschat/pdf_processing/pdf_to_json.py)** to create a vector store for semantic search.

We cannot guarantee the effectiveness of this method with your organisations website or with other file types besides PDF's.

## Introduction

This is an experimental application for semantic search of statistical publications.
It uses LangChain and HuggingFace to implement a fairly simple
Retriaval Augmented Generation (RAG) using embedding search and QA information retrieval process.

Upon receiving a query, documents are returned as search results
using embedding similarity to score relevance.
Next, the relevant text is passed to a Large Language Model (LLM),
which is prompted to write an answer to the original question, if it can,
using only the information contained within the documents.

To use this application, you will need to set up a vector store
with the relevant documents, which can be done by scraping the relevant websites
and processing the PDF documents into JSON files.
Read the documentation below in the given order to get started.

## Table of Key Documentation

To get started with the project, please refer to the following documentation in the `docs` folder:

- [Repository Structure](docs/repo_structure.md)
- [Setup Guide](docs/setup_guide.md)
- [Running Statschat](docs/running_statschat.md)
- [Configuration Guide](docs/config_guide.md)
- [Search Configuration Guide](docs/search_config_parameters.md)

The tool can be interacted with in several ways, and the following guides will help you get started:

- [API Guide](docs/running_api.md)
- [Web Application Guide](docs/running_app.md)

In order to tailor the tool to your use case and deploying it effectively,
the following documentation is also available:

- [Tailoring the tool](docs/developing_and_testing.md)
- [Server Deployment](docs/server_deployment.md)

## License

<!-- Unless stated otherwise, the codebase is released under [the MIT Licence][mit]. -->

The code, unless otherwise stated, is released under [the MIT License][mit].

[mit]: LICENSE
