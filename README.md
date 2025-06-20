# `StatsChat`

[![Stability](https://img.shields.io/badge/stability-experimental-orange.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#experimental)
[![Shared under the MIT License](https://img.shields.io/badge/license-MIT-green)](https://github.com/datasciencecampus/statschat-global/blob/main/LICENSE)

## Code state

> [!WARNING]
> Please be aware that for development purposes, these experiments use
> experimental Large Language Models (LLM's) not intended for production. They
> can present inaccurate information, hallucinated statements and offensive
> text by random chance or through malevolent prompts.

- **Under development** / **Experimental**
- **Tested on macOS & windows only**
- **Peer-reviewed**
- **Depends on external API's**

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
