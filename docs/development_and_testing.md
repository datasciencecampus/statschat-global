## Development & Testing

Tips to help with future development and testing on the backend.

```
Remember to change `pdf_files_mode` in the `main.toml` depending on whether you are creating (SETUP) or updating (UPDATE)
the vector store and press `ctrl + s` or save. Please see here (here)[]
```

![image](https://github.com/user-attachments/assets/fc99cef5-7bf7-486c-9272-d2d6342ed95c)

### Page range
```
In some cases not every single PDF from the KNBS website will need to be scraped as this can take some time.
Especially if changes to the base code need to be tested related to the `SETUP` or `UPDATE` of the vector store.

If wanting to scrape PDFs from only one page then use the page number related to the last page with pdf files,
currently that would be `page = 38`. Be aware that the higher the page number the older the publications that
will be scraped from the KNBS website.
So for example if `page = 37` the oldest 2 pages 37 and 38 will scraped.

In essence the `page` variable in `pdf_downloader.py` determines the range of pages that PDFs are scraped from.
```
#### UPDATE
```
When `pdf_files_mode` is set to "UPDATE" the default behaviour is to scrape the pdf's from the 5 most recently uploaded
pages of documents. This can be altered by changing the `max_pages` variable in `pdf_downloader.py`. Any pdf files that have
already been previously downloaded (i.e. when setting up the vector store or any previous updates) will be filtered out
pre-download to avoid any duplicate entries.
```
#### SETUP
```
When `pdf_files_mode` is set to "SETUP" the default behaviour is to scrape ALL pdf files, from the most recent page to the
last. There is no need to change the max_pages as the script will automatically exist and continue with the pdf preprocessing
once it runs out of valid pages to scrape.
```
![image](https://github.com/user-attachments/assets/bfe4bce4-2d38-4bab-b1ab-ccd6987c607b)

```
If `pdf_files_mode` = `UPDATE` then the `max_pages` variable will need to be changed along with the `page` variable
if only wanting to have a finite number of PDFs. For example if wanting to `UPDATE` the vector store with KNBS PDFs
from page 37 and 38 then `page = 37` and `max_pages = 38`.
```
![image](https://github.com/user-attachments/assets/b6179157-bf89-4be9-a6be-58356cb4f6b2)
