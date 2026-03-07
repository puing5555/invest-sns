import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://finance.naver.com/',
}

# 네이버 금융 외국인 현황 페이지
url = 'https://finance.naver.com/item/frgn.naver'
params = {'code': '005930', 'page': 1}
r = requests.get(url, params=params, headers=headers, timeout=10)
r.encoding = 'euc-kr'
print('Status:', r.status_code)

soup = BeautifulSoup(r.text, 'html.parser')
tables = soup.find_all('table')
print('테이블 수:', len(tables))

for i, table in enumerate(tables):
    rows = table.find_all('tr')
    classes = table.get('class', [])
    print(f'테이블 {i}: {len(rows)}행, class={classes}')
    for row in rows[:3]:
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        if cols:
            print('  ', cols[:8])
