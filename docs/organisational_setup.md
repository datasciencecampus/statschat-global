# Organisational setup

Tips to help with future codebase adaptation and organisational setup.

## Adapting codebase for organisation

There will most likely be differences for each organisations website in relation to setup/layout. Therefore changes may need
to be made to the codebase to get the Statschat package to work for your organisation. This is due to:

**- The organisations website that PDF's are downloaded from**

**- The PDF metadata for each document**

The scripts potentially needing to be looked at and altered are:

**- pdf_downloader.py**

**- pdf_to_json.py**

## Downloading specific PDF webpages

In some cases not every single PDF from the organisations website will need to be scraped as this can take some
time. Especially if changes to the codebase need to be tested related to `SETUP` or `UPDATE` of the vector store. 
If wanting to scrape PDFs from only one page then changes will need to be made to the `main.toml`.

For example if `page_start = 1` and `page_end = 5`the 5 latest webpages PDF's will be downloaded. If wanting older
PDF's then `page_start = 37` and `page_end = 38`. In simple terms the higher the page number the older the publications
that will be scraped from the organisations website. 

![image](https://github.com/user-attachments/assets/d34f3bae-6af7-41ce-90e6-fad21b00442c)

```
Remember to change `mode` in the `main.toml` depending on whether you are creating or updating the vector
store and press `ctrl + s` or save to confirm.
```
![image](https://github.com/user-attachments/assets/17c93497-8a8c-4f08-a9da-4a4dd4e8a833)



