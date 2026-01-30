
import requests
from bs4 import BeautifulSoup

URL = "https://www.siata.gov.co/operacional/Meteorologia/"
print(f"Listing {URL}")
try:
    response = requests.get(URL, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        print(link['href'])
except Exception as e:
    print(e)
