from bs4 import BeautifulSoup
import requests
import re

url = "https://scholar.google.com/scholar?cites=1843156135598356389&as_sdt=2005&sciodt=0,5&hl=en"

result = requests.get(
        url,
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }
)

soup = BeautifulSoup(result.text, 'html.parser')

#list_string = soup.find_all('div',id="gs_res_ccl_mid")
#print(list_string)

with open ("html.txt", "r") as s:
    string = s.read()
    list = re.findall("https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", string)
    print(list)