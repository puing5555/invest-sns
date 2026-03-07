import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://finance.naver.com/',
}

# 테이블 2 (13행) 및 테이블 3 (33행) 상세 확인
url = 'https://finance.naver.com/item/frgn.naver'
params = {'code': '005930', 'page': 1}
r = requests.get(url, params=params, headers=headers, timeout=10)
r.encoding = 'euc-kr'

soup = BeautifulSoup(r.text, 'html.parser')
tables = soup.find_all('table', class_='type2')
print(f'type2 테이블 수: {len(tables)}')

for ti, table in enumerate(tables):
    print(f'\n=== 테이블 {ti} ===')
    rows = table.find_all('tr')
    for row in rows[:10]:
        th = [t.get_text(strip=True) for t in row.find_all('th')]
        td = [t.get_text(strip=True) for t in row.find_all('td')]
        if th:
            print('  헤더:', th)
        if td and any(td):
            print('  데이터:', td[:8])
