## Development & Testing

Tips to help with future development and testing on the backend.

```
Remember to change `pdf_files_mode` depending on whether you are creating or updating the vector store and
press `ctrl + s` or save to confirm.
```

![image](https://github.com/user-attachments/assets/fc99cef5-7bf7-486c-9272-d2d6342ed95c)

```
In some cases not every single PDF from the KNBS website will need to be scraped as this can take some time.
Especially if changes to the base code need to be tested related to "SETUP" or "UPDATE" of the vector store.

Only a finite number of PDFs will be required. If wanting to scrape PDFs from only one page then `page = 38`
not `page = 1` as that will scrape all PDFs. Be aware that the higher the page number the older the publications
that will be scraped from the KNBS website. So for example if `page=37` the oldest 2 pages 37 and 38 will scraped.

In essence the page variable in `pdf_downloader.py` determines the range of pages that PDFs are scraped from.
```
![image](https://github.com/user-attachments/assets/5ffe7917-8d32-4b8b-8724-0f21159ccc35)

```
If `pdf_files_mode` = "UPDATE" then the "max_pages" variable will need to be changed along with the `page` variable
if only wanting to have a finite number of PDFs.
```
![image](https://github.com/user-attachments/assets/b6179157-bf89-4be9-a6be-58356cb4f6b2)

