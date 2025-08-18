# Offline Upload

If PDF files were manually added to `data/local_pdfs` so, `download_site = ""` in the `main.toml` during vector store **SETUP**, 
in order to access the page urls for each PDF these steps below need to be followed. 

**First navigate to** `data/local_pdfs` **dir**

```
cd statschat-global/data/local_pdfs
```

**Run in terminal to setup local host** (-m may not be needed depending on your setup)

```
python3 -m http.server 8000
```
or
```
python -m http.server 8000
```
**This should be seen in the terminal**
<img width="1382" height="178" alt="image" src="https://github.com/user-attachments/assets/3508f749-9c9d-4827-958f-19d993821244" />

**When now clicking on `page_url` in a json file it should take you directly to a webpage where the PDF is hosted**

<img width="717" height="362" alt="image" src="https://github.com/user-attachments/assets/6e6d37be-2f51-41ef-8e0a-b85e930cb64f" />

<img width="1490" height="1092" alt="image" src="https://github.com/user-attachments/assets/a06e084f-d237-4c08-a724-664909b84afc" />

**Now follow Option A, B or C from the [setup guide](https://github.com/datasciencecampus/statschat-global/blob/development/docs/running_statschat.md)**
