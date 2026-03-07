# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://finance.naver.com/',
}

START_DATE = "2023-01-01"
END_DATE = "2026-03-07"

def fetch_naver_flow(ticker, start=START_DATE, end=END_DATE, max_pages=42):
    url = 'https://finance.naver.com/item/frgn.naver'
    all_rows = []

    for page in range(1, max_pages + 1):
        try:
            r = requests.get(url, params={'code': ticker, 'page': page},
                           headers=HEADERS, timeout=10)
            r.encoding = 'euc-kr'
            soup = BeautifulSoup(r.text, 'html.parser')

            data_table = None
            for t in soup.find_all('table', class_='type2'):
                headers_row = t.find_all('th')
                header_text = ' '.join([h.get_text(strip=True) for h in headers_row])
                if '날짜' in header_text and '기관' in header_text:
                    data_table = t
                    break

            if data_table is None:
                break

            rows = data_table.find_all('tr')
            page_data = []
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cols) >= 7 and cols[0] and '.' in cols[0]:
                    try:
                        date_str = cols[0].replace('.', '-')
                        institution_str = cols[5].replace(',', '').replace('+', '').strip()
                        foreign_str = cols[6].replace(',', '').replace('+', '').strip()
                        if institution_str and foreign_str:
                            page_data.append({
                                'date': pd.to_datetime(date_str),
                                'institution': int(institution_str),
                                'foreign': int(foreign_str),
                            })
                    except (ValueError, IndexError) as e:
                        print(f"  파싱 오류: {cols} -> {e}")

            if not page_data:
                break

            min_date = min(r['date'] for r in page_data)
            all_rows.extend(page_data)

            if page <= 2:
                print(f"  페이지 {page}: {page_data[0]['date'].date()} ~ {page_data[-1]['date'].date()} ({len(page_data)}행)")

            if min_date < pd.to_datetime(start):
                break

            time.sleep(0.1)

        except Exception as e:
            print(f"  페이지 {page} 오류: {e}")
            break

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)
    df = df.rename(columns={'date': '날짜', 'institution': '기관', 'foreign': '외국인'})
    df = df.drop_duplicates('날짜').sort_values('날짜').set_index('날짜')
    df = df[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]
    df['개인'] = -(df['기관'] + df['외국인'])
    return df if len(df) > 0 else None


print("삼성전자 수급 테스트...")
df = fetch_naver_flow('005930')
if df is not None:
    print(f"수집 완료: {len(df)}행")
    print(df.tail(3))
else:
    print("수집 실패")
