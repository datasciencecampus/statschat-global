# %%
import requests
from bs4 import BeautifulSoup

page = 1
base_url = f'https://www.knbs.or.ke/all-reports/page'

continue_search = True

while continue_search:
    url = base_url + str(page) + '/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Break the loop if no more quotes are found
    pdf_links = [
        a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf")
    ]
    
    if len(pdf_links) == 0:
        print('I am stopping')
        continue_search = False
    
    page += 1
    print(url, len(pdf_links))

print('I am done.')


