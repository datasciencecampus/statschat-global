## Project structure tree
Successful running of the scripts assumes a certain structure in how where data and other auxiliary inputs need to be located. The below tree demonstrates where each file/folder needs to be for successful execution or where files will be located following execution.

### Overview
```
📦statschat-ke
 ┣ 📂data
 ┣ 📂docs
 ┣ 📂fast-api
 ┣ 📂log
 ┣ 📂notebooks
 ┣ 📂statschat
 ┣ 📜pyproject.toml
 ┣ 📜.gitignore
 ┗ 📜README.md

```

 ### Data
 ```
📦statschat-ke
 ┣ 📂data
 ┃ ┣ 📂db_langchain
 ┃ ┣ 📂db_langchain_latest
 ┃ ┣ 📂json_conversions
 ┃ ┣ 📂json_split
 ┃ ┣ 📂latest_pdf_store
 ┃ ┣ 📂latest_json_conversions
 ┃ ┣ 📂latest_json_split
 ┗ ┗ 📂pdf_store

```

 ### Code
 ```
📦statschat-ke
 ┣ 📂statschat
 ┃ ┣ 📂config
 ┃ ┃ ┣📜main.toml
 ┃ ┃ ┣📜questions.toml
 ┃ ┃ ┗📜utils.toml
 ┃ ┣ 📂embedding
 ┃ ┃ ┣📜latest_flag_helpers.py
 ┃ ┃ ┣📜latest_updates.py
 ┃ ┃ ┗📜preprocess.py
 ┃ ┣ 📂generative
 ┃ ┃ ┣📜generate_local.py
 ┃ ┃ ┣📜llm.py
 ┃ ┃ ┣📜prompts.py
 ┃ ┃ ┣📜prompts_local.py
 ┃ ┃ ┣📜response_model.py
 ┃ ┃ ┗📜utils.py
 ┃ ┣ 📂model_evaluation
 ┃ ┃ ┗📜evaluation.py
 ┃ ┣ 📂pdf_processing
 ┃ ┃ ┣ 📜merge_database_files.py
 ┃ ┃ ┣ 📜pdf_downloader.py
 ┃ ┗ ┗ 📜pdf_to_json.py
 ┗ 📜pdf_runner.py

```
