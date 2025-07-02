# Running Statschat

This document provides a guide on how to run the Statschat tool, which is designed to answer questions about statistics and data from PDF documents.

## Step 1: Create the Vector Store

The vector store can be set up running `pdf_runner.py` in an integrated development environment (IDE).
You can also run it from the command line as below:

    ```shell
    python3 statschat/pdf_runner.py
    ```

Before running `pdf_runner.py`  ensure that the key variables in `statschat/config/main.toml`
are set to the desired options.

The `download_site` variable will determine what website is used as an endpoint to scrape
PDF files from. If left empty, the system will look for PDFs placed in the `data/local_pdfs` folder.

The `pdf_runner.py` script will webscrape PDF documents from the website, or take the ones locally stored.
It will then convert them to JSON files and either append or replace the existing vector store.
This will be based on the `download_mode` parameter.

`download_mode = "SETUP"` -> Will scrape all pdf files and reset the vector store,
creating a new one from the PDF documents that are scraped and processed into JSON files.
This will only need to be done `once` as afterwards it will just need updating.

`download_mode = "UPDATE"` -> Will only scrape the latest PDF files.
If on website mode from the website, compare existing PDF files in the vector store with those downloaded and only process new files - appending these to the database and "flushing" the latest data folders ready for a new run. This will need to be done as new PDFs are added to the relevant websites website.

> [!NOTE]
> **You might get an error after running `pdf_runner.py` related to SSL: certification.**
![image](https://github.com/user-attachments/assets/2d408392-fe66-438e-83b1-550943f14751)
> **If so then run:**
```
pip install pip_system_certs
```
## Step 2: Usage

### Option A: Run Questions Manually (backend)

This assumes the [vector store]("update link") has already been created otherwise this will need to be done before.
Make sure that you're terminal is running from **`statschat`**. Then use the **`llm.py`**
script and change the **question** parameter with the desired question:

![image](https://github.com/user-attachments/assets/36ec03e4-2d6a-4814-9220-8cc478196e52)

The answer, context and response will be output in the terminal.

### Option B: Run the Interactive Statschat API

The `statschat` tool can be deployed as an API (using fastapi).
This allows you to ask questions interactively via a web interface or directly through HTTP requests.
In order to run the interactive Statschat API you will need to make sure you have:

- **`uvicorn`**: This is a bit of software to locally replicate a server
- **`fastapi`**: This is a Python library to generate the API functionality

To get these in your machine simply run:

    ```shell
    pip install fastapi uvicorn
    ```

Then you will need to make sure your terminal is on the **`statschat-global`** folder.
From there, you can generate the synthetic "server" locally from your terminal:

    ```shell
    uvicorn fast-api.main_api_local:app --reload
    ```

The fast-api is set to respond to http requests on a particular port.
You will see this in your terminal line, something like:

    ```shell
    Uvicorn running on http://127.0.0.1:8000
    ```

> [!NOTE]
> **Your port might be slightly different to 127.0.0.1:8000**

After a few seconds you should be able to go to your browser and ask questions.
On the search bar type something like:

    ```shell
    http://127.0.0.1:8000/search?q=what+was+inflation+in+december+2023
    ```

This should produce a response text that is displayed on your browser.
The generic formula to ask a question is:

    ```shell
    <API_URL>/search?q=<your_question>
    ```

### Option C: Running the Flask web interface

In order to run the user UI, which has a website interface that relies on the API,
you can use a sample Flask web interface.
In order to initiate that, make sure that the API is running and then start up the app:

    ```shell
    python flask-app/app.py
    ```

Then navigate, in your browser to http://localhost:5000.

## Step 3: Additional Configuration

You may need to configure additional settings for the StatChat project.
This can include setting up environment variables, configuring the API keys, or adjusting the project settings.
For more information on how to configure the project, please refer to the [Configuration Guide](docs/config_guide.md).
