# Project Structure

Successful running of the scripts assumes a certain structure in how where data and other auxiliary inputs need to be located. The below tree demonstrates where each file/folder needs to be for successful execution or where files will be located following execution.

## Overview

```
📦statschat-global
 ┣ 📂data           # Holds the knowledge
 ┣ 📂docs           # Documentation
 ┣ 📂fast-api       # Builds API interface
 ┣ 📂flask-app      # Builds Flask webapp
 ┣ 📂log            # Holds logs of runs
 ┣ 📂statschat      # Main package codebase
 ┣ 📜pyproject.toml
 ┣ 📜.gitignore
 ┗ 📜README.md
```

The structure above organises the project into clearly defined directories for data storage, documentation, API and web application code, logs, and the main package. This layout helps maintain separation of concerns, making it easier to manage, develop, and scale different components of the project efficiently.

Additionally, the `pyproject.toml` file is used for managing project dependencies and configurations, while the `.gitignore` file specifies files and directories that should be ignored by version control systems like Git.

## Data

```
📦statschat-global
 ┣ 📂data
 ┃ ┣ 📂db_langchain
 ┃ ┣ 📂db_langchain_latest
 ┃ ┣ 📂json_conversions
 ┃ ┣ 📂json_split
 ┃ ┣ 📂latest_pdf_store
 ┃ ┣ 📂latest_json_conversions
 ┃ ┣ 📂latest_json_split
 ┃ ┗ 📂pdf_store
 ┃

```

The `data` directory is structured to hold all the knowledge and processed data used by the application. It contains subdirectories for different stages of data processing and storage, including:

- `db_langchain`: Contains the main vector store used for semantic search.
- `db_langchain_latest`: Holds the latest version of the vector store after updates.
- `json_conversions`: Stores JSON files converted from PDF documents.
- `json_split`: Contains split JSON files for more granular data processing.
- `latest_pdf_store`: Temporary storage for newly downloaded PDF files before processing.
- `latest_json_conversions`: Temporary storage for newly converted JSON files.
- `latest_json_split`: Temporary storage for newly split JSON files.
- `pdf_store`: Contains the processed PDF files that are used for knowledge retrieval.

## Main Package Code Structure

```
📦statschat
 ┣ 📂statschat
 ┃ ┣ 📂config
 ┃ ┃ ┣📜main.toml
 ┃ ┃ ┗📜utils.py
 ┃ ┣ 📂embedding
 ┃ ┃ ┣📜latest_flag_helpers.py
 ┃ ┃ ┣📜latest_updates.py
 ┃ ┃ ┗📜preprocess.py
 ┃ ┣ 📂generative
 ┃ ┃ ┣📜cloud_llm.py
 ┃ ┃ ┣📜local_llm.py
 ┃ ┃ ┣📜prompts_cloud.py
 ┃ ┃ ┣📜prompts_local.py
 ┃ ┃ ┣📜response_model.py
 ┃ ┃ ┗📜utils.py
 ┃ ┣ 📂model_evaluation
 ┃ ┃ ┗📜evaluation.py
 ┃ ┣ 📂pdf_processing
 ┃ ┃ ┣ 📜merge_database_files.py
 ┃ ┃ ┣ 📜pdf_downloader.py
 ┃ ┃ ┣ 📜pdf_local_load.py
 ┃ ┗ ┗ 📜pdf_to_json.py
 ┗ 📜pdf_runner.py

```

The `statschat` directory contains the main package codebase, which is responsible for the core functionality of the application. This directory is further divided into several submodules, each handling specific tasks related to the overall workflow of the project.

- **config**: Contains configuration files and utility scripts for managing settings and reusable functions across the project.
- **embedding**: Handles the creation and updating of vector stores, as well as preprocessing data for embedding models.
- **generative**: Implements logic for interacting with both cloud-based and local large language models (LLMs), manages prompt templates, response modeling, and related utilities.
- **model_evaluation**: Provides tools for evaluating the performance and accuracy of the models used in the project.
- **pdf_processing**: Manages all aspects of PDF handling, including downloading, loading, merging, and converting PDFs to JSON for further processing.

This modular structure ensures that each component is focused on a distinct aspect of the workflow, supporting maintainability and scalability as the project evolves.
