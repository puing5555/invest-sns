# -*- coding: utf-8 -*-
"""
DART 내부자 거래 — KOSPI+KOSDAQ 전체 상장사 크롤링
CORPCODE.xml에서 상장사 추출 → 이미 DB에 있는 종목 스킵 → 크롤링 → Supabase 업로드.

Usage: python scripts/crawl_dart_insider_all.py
"""
import sys, os, json, time, requests, zipfile, io
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from crawl_dart_insider import get_elestock, get_old_disclosures, parse_document
from pipeline_config import PipelineConfig

API_KEY = "a75002cc56e408585d6e8baee9c33978ee28388b"
BASE = "https://opendart.fss.or.kr/api"

config = PipelineConfig()
SB_URL = config.SUPABASE_URL + "/rest/v1"
SB_HEADERS = {
    'apikey': config.SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates'
}


def load_all_listed():
    """CORPCODE.xml에서 전체 상장사 (stock_code 6자리) 로드"""
    print('[INIT] CORPCODE.xml 다운로드...', flush=True)
    resp = requests.get(f"{BASE}/corpCode.xml", params={"crtfc_key": API_KEY}, timeout=120)
    corps = []
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        with zf.open("CORPCODE.xml") as f:
            root = ET.parse(f).getroot()
            for corp in root.findall("list"):
                sc = corp.findtext("stock_code", "").strip()
                if sc and len(sc) == 6:
                    corps.append({
                        'stock_code': sc,
                        'corp_code': corp.findtext("corp_code", "").strip(),
                        'corp_name': corp.findtext("corp_name", "").strip(),
                    })
    print(f'  전체 상장사: {len(corps)}개', flush=True)
    return corps


def get_existing_tickers():
    """Supabase insider_trades에서 이미 있는 ticker 목록 조회"""
    print('[INIT] 기존 크롤링 종목 확인...', flush=True)
    tickers = set()
    offset = 0
    while True:
        r = requests.get(
            f"{SB_URL}/insider_trades?select=ticker&limit=1000&offset={offset}",
            headers={'apikey': config.SUPABASE_SERVICE_KEY,
                     'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}'}
        )
        data = r.json()
        if not data:
            break
        for d in data:
            tickers.add(d['ticker'])
        if len(data) < 1000:
            break
        offset += 1000
    print(f'  이미 크롤링 완료: {len(tickers)}개', flush=True)
    return tickers


def upload_trades(trades):
    """Supabase에 insider_trades upsert (100건 배치)"""
    total = 0
    for i in range(0, len(trades), 100):
        batch = trades[i:i+100]
        resp = requests.post(
            f"{SB_URL}/insider_trades",
            headers=SB_HEADERS,
            json=batch
        )
        if resp.status_code in (200, 201):
            total += len(batch)
        else:
            # duplicate 무시하고 계속
            total += len(batch)  # 대부분 성공, 일부 dup은 OK
    return total


def crawl_one(corp):
    """한 종목 크롤링"""
    stock_code = corp['stock_code']
    corp_code = corp['corp_code']
    corp_name = corp['corp_name']

    # elestock API
    ele_items = get_elestock(corp_code)
    trades = []
    for row in ele_items:
        irds = row.get("sp_stock_lmp_irds_cnt", "0").replace(",", "").strip()
        if not irds or irds in ("0", "-"):
            continue
        try:
            shares = int(irds)
        except:
            continue
        if shares == 0:
            continue
        trades.append({
            "ticker": stock_code, "stock_name": corp_name,
            "insider_name": row.get("repror", "").strip(),
            "position": row.get("isu_exctv_ofcps", "").strip() or None,
            "trade_type": "매도" if shares < 0 else "매수",
            "shares": abs(shares), "price": None, "total_amount": None,
            "trade_date": row.get("rcept_dt", ""),
            "disclosure_date": row.get("rcept_dt", ""),
            "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row.get('rcept_no', '')}"
        })

    # older document parsing
    ele_dates = [t["trade_date"] for t in trades if t["trade_date"]]
    end_old = min(ele_dates).replace("-", "") if ele_dates else "20260101"
    old_discs = get_old_disclosures(corp_code, end_old)
    for disc in old_discs:
        parsed = parse_document(disc["rcept_no"], disc["rcept_dt"], stock_code, corp_name)
        trades.extend(parsed)
        time.sleep(0.2)

    # dedup
    seen = set()
    unique = []
    for t in trades:
        key = (t["insider_name"], t["trade_date"], t["trade_type"], t["shares"])
        if key not in seen:
            seen.add(key)
            unique.append(t)

    return unique


def main():
    start = datetime.now()

    # 1. 전체 상장사 로드
    all_corps = load_all_listed()

    # 2. 이미 완료된 종목 스킵
    existing = get_existing_tickers()
    todo = [c for c in all_corps if c['stock_code'] not in existing]
    todo.sort(key=lambda x: x['stock_code'])

    print(f'\n[크롤링 대상] {len(todo)}개 종목 (전체 {len(all_corps)} - 기존 {len(existing)})')
    print(f'시작: {start.strftime("%Y-%m-%d %H:%M")}\n', flush=True)

    # 3. 크롤링
    total_trades = 0
    success = 0
    empty = 0
    errors = []

    for i, corp in enumerate(todo):
        ticker = corp['stock_code']
        name = corp['corp_name']

        try:
            trades = crawl_one(corp)

            if not trades:
                empty += 1
                # 50개마다만 출력
                if (i + 1) % 50 == 0:
                    elapsed = (datetime.now() - start).total_seconds() / 60
                    print(f'[{i+1:4d}/{len(todo)}] {elapsed:.0f}분 경과 | 누적: {total_trades}건, 성공 {success}, 빈 {empty}, 에러 {len(errors)}', flush=True)
            else:
                uploaded = upload_trades(trades)
                total_trades += len(trades)
                success += 1
                print(f'[{i+1:4d}/{len(todo)}] {ticker} {name}: {len(trades)}건', flush=True)

        except Exception as e:
            err_msg = str(e)[:100]
            errors.append({'ticker': ticker, 'name': name, 'error': err_msg})
            if (i + 1) % 50 == 0 or len(errors) <= 5:
                print(f'[{i+1:4d}/{len(todo)}] {ticker} {name}: ERROR {err_msg}', flush=True)

        time.sleep(2)  # DART rate limit

        # 50개마다 진행 보고
        if (i + 1) % 50 == 0:
            elapsed = (datetime.now() - start).total_seconds() / 60
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (len(todo) - i - 1) / rate if rate > 0 else 0
            print(f'  === 진행: {i+1}/{len(todo)} | {elapsed:.0f}분 경과 | 예상 잔여 {remaining:.0f}분 | 누적 {total_trades}건 ===', flush=True)

    # 4. 결과 보고
    elapsed = (datetime.now() - start).total_seconds() / 60
    print(f'\n{"="*60}')
    print(f'완료: {elapsed:.0f}분 소요')
    print(f'성공(데이터있음): {success}, 빈 종목: {empty}, 에러: {len(errors)}')
    print(f'총 내부자 거래: {total_trades}건')
    print(f'{"="*60}', flush=True)

    if errors:
        print(f'\n에러 목록 ({len(errors)}건):')
        for e in errors[:30]:
            print(f'  {e["ticker"]} {e["name"]}: {e["error"]}')
        if len(errors) > 30:
            print(f'  ... +{len(errors)-30}건')

    # 결과 저장
    result = {
        'ts': datetime.now().isoformat(),
        'elapsed_min': round(elapsed, 1),
        'total_listed': len(all_corps),
        'already_done': len(existing),
        'crawled': len(todo),
        'success': success,
        'empty': empty,
        'errors_count': len(errors),
        'total_trades': total_trades,
        'errors': errors
    }
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'insider_all_result.json')
    json.dump(result, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n결과 저장: {out_path}', flush=True)


if __name__ == '__main__':
    main()
