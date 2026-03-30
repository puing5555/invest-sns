# -*- coding: utf-8 -*-
# fetch_supply_demand.py - 네이버 금융에서 투자자별 수급 데이터 크롤링 → Supabase
import sys, os, time, json, requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from pipeline_config import PipelineConfig

config = PipelineConfig()
BASE_URL = config.SUPABASE_URL + "/rest/v1"
HEADERS = {
    'apikey': config.SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates'
}
NAVER_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


def parse_number(text):
    """'+1,234' / '-1,234' / '1,234' → int"""
    text = text.strip().replace(',', '').replace('+', '')
    if not text or text == '0':
        return 0
    try:
        return int(text)
    except ValueError:
        return 0


def fetch_naver_supply(ticker, max_pages=30):
    """네이버 금융 외국인/기관 탭에서 일별 순매수 크롤링"""
    all_rows = []
    seen_dates = set()

    for page in range(1, max_pages + 1):
        url = f'https://finance.naver.com/item/frgn.naver?code={ticker}&page={page}'
        try:
            r = requests.get(url, headers=NAVER_HEADERS, timeout=10)
            r.encoding = 'euc-kr'
        except Exception as e:
            print(f'  Page {page} error: {e}')
            break

        soup = BeautifulSoup(r.text, 'html.parser')
        # Table 3: 날짜, 종가, 전일비, 등락률, 거래량, 기관, 외국인, 순매매량(외국인보유)
        tables = soup.select('table.type2')
        if len(tables) < 2:
            break

        table = tables[1]  # second type2 table has the data
        rows = table.select('tr')
        page_count = 0

        for row in rows:
            cols = row.select('td')
            if len(cols) < 9:
                continue
            date_text = cols[0].get_text(strip=True)
            if not date_text or '.' not in date_text:
                continue

            # Parse date
            try:
                trade_date = date_text.replace('.', '-').strip()
                if len(trade_date) == 10:
                    pass
                else:
                    parts = date_text.split('.')
                    trade_date = f'{parts[0].strip()}-{parts[1].strip().zfill(2)}-{parts[2].strip().zfill(2)}'
            except:
                continue

            if trade_date in seen_dates:
                continue
            seen_dates.add(trade_date)

            close_price = parse_number(cols[1].get_text(strip=True))
            inst_shares = parse_number(cols[5].get_text(strip=True))
            frgn_shares = parse_number(cols[6].get_text(strip=True))
            # 수량(주) × 종가 → 금액(원) 변환
            institution = inst_shares * close_price
            foreign_inv = frgn_shares * close_price
            # 개인 = -(기관+외국인)
            individual = -(institution + foreign_inv)

            all_rows.append({
                'ticker': ticker,
                'trade_date': trade_date,
                'institution': institution,
                'foreign_investor': foreign_inv,
                'individual': individual,
            })
            page_count += 1

        if page_count == 0:
            break
        time.sleep(0.3)

    all_rows.sort(key=lambda x: x['trade_date'])
    return all_rows


def upload_to_supabase(rows):
    """Supabase에 upsert"""
    batch_size = 100
    total = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        resp = requests.post(
            f"{BASE_URL}/stock_supply_demand?on_conflict=ticker,trade_date",
            headers=HEADERS,
            json=batch
        )
        if resp.status_code in (200, 201):
            total += len(batch)
        else:
            print(f'  Error batch {i}: {resp.status_code} {resp.text[:200]}')
    return total


def main():
    ticker = sys.argv[1] if len(sys.argv) > 1 else '005930'
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 30  # ~30 pages ≈ 1년
    name = sys.argv[3] if len(sys.argv) > 3 else ticker

    print(f'[수급 크롤링] {name} ({ticker}), max_pages={max_pages}')
    rows = fetch_naver_supply(ticker, max_pages)
    print(f'  수집: {len(rows)}건 ({rows[0]["trade_date"]} ~ {rows[-1]["trade_date"]})')

    uploaded = upload_to_supabase(rows)
    print(f'  업로드: {uploaded}건')


if __name__ == '__main__':
    main()
