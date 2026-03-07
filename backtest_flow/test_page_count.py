"""페이지당 데이터 범위 확인 및 필요 페이지 수 측정"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://finance.naver.com/',
}

def get_page_dates(ticker, page):
    url = 'https://finance.naver.com/item/frgn.naver'
    r = requests.get(url, params={'code': ticker, 'page': page}, headers=HEADERS, timeout=10)
    r.encoding = 'euc-kr'
    soup = BeautifulSoup(r.text, 'html.parser')
    dates = []
    for table in soup.find_all('table', class_='type2'):
        ths = [t.get_text(strip=True) for t in table.find_all('th')]
        if '날짜' in ' '.join(ths):
            for row in table.find_all('tr'):
                cols = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cols) >= 6 and cols[0] and '.' in cols[0]:
                    dates.append(cols[0])
    return dates

# 삼성전자 테스트
ticker = '005930'
for page in [1, 5, 10, 20, 40, 60, 75]:
    dates = get_page_dates(ticker, page)
    if dates:
        print(f"페이지 {page}: {dates[0]} ~ {dates[-1]} ({len(dates)}행)")
    else:
        print(f"페이지 {page}: 데이터 없음")
    time.sleep(0.3)
