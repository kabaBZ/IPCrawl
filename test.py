import requests
import random
from bs4 import BeautifulSoup


page = 1
url = f'https://ip.jiangxianli.com/?page={page}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
}
response = requests.get(url, headers=headers)
print(response.text)
soup = BeautifulSoup(response.text, 'lxml')
soup = soup.find('table', attrs={'class': 'layui-table'})
for item in soup.find('tbody').find_all('tr'):
    if len(item.find_all('td')) != 11: continue
    ip = item.find_all('td')[0].text.strip()
    port = item.find_all('td')[1].text.strip()
    proxy_type = item.find_all('td')[3].text.strip()
    print(ip)