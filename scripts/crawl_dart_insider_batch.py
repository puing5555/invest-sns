# -*- coding: utf-8 -*-
"""
DART 내부자 거래 일괄 크롤링 — KR 전체 종목
stock_tickers.json에서 KR 6자리 코드 추출, 각 종목 10년치 크롤링 → Supabase 업로드.

Usage: python scripts/crawl_dart_insider_batch.py
"""
import sys, os, json, time, re, requests
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from crawl_dart_insider import get_elestock, get_old_disclosures, parse_document, API_KEY, BASE
from pipeline_config import PipelineConfig
import zipfile, io, xml.etree.ElementTree as ET

config = PipelineConfig()
SB_URL = config.SUPABASE_URL + "/rest/v1"
SB_HEADERS = {
    'apikey': config.SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates'
}

# 이미 완료된 종목 + 상장폐지 + DART 미등록 ETF
SKIP = {
    '005930', '036710',
    # 상장폐지/코드변경
    '033400', '046810', '124570', '153910', '090090', '188490',
    # ETF (DART 내부자 대상 아님)
    '371450', '371460', '396520', '438330', '490490',
}

# CORPCODE.xml 캐시 (한 번만 다운로드)
_CORP_MAP = None

def load_corp_map():
    global _CORP_MAP
    if _CORP_MAP is not None:
        return _CORP_MAP
    print('[INIT] CORPCODE.xml 다운로드 중...', flush=True)
    resp = requests.get(f"{BASE}/corpCode.xml", params={"crtfc_key": API_KEY}, timeout=120)
    _CORP_MAP = {}
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        with zf.open("CORPCODE.xml") as f:
            root = ET.parse(f).getroot()
            for corp in root.findall("list"):
                sc = corp.findtext("stock_code", "").strip()
                if sc:
                    _CORP_MAP[sc] = (
                        corp.findtext("corp_code", "").strip(),
                        corp.findtext("corp_name", "").strip()
                    )
    print(f'  {len(_CORP_MAP)}개 종목 로드 완료', flush=True)
    return _CORP_MAP


def get_corp_code_cached(stock_code):
    m = load_corp_map()
    if stock_code in m:
        return m[stock_code]
    return None, None


def get_kr_tickers():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stock_tickers.json')
    tickers = json.load(open(data_path, encoding='utf-8'))
    kr = set()
    for t in tickers:
        code = t.replace('.KS', '')
        if re.match(r'^\d{6}$', code):
            kr.add(code)
    return sorted(kr - SKIP)


def upload_insider_trades(trades):
    """Supabase에 insider_trades 테이블 upsert (100건 배치)"""
    batch_size = 100
    total = 0
    for i in range(0, len(trades), batch_size):
        batch = trades[i:i+batch_size]
        resp = requests.post(
            f"{SB_URL}/insider_trades?on_conflict=ticker,insider_name,trade_date,trade_type,shares",
            headers=SB_HEADERS,
            json=batch
        )
        if resp.status_code in (200, 201):
            total += len(batch)
        else:
            # on_conflict 칼럼이 없을 수 있으므로 fallback
            resp2 = requests.post(
                f"{SB_URL}/insider_trades",
                headers=SB_HEADERS,
                json=batch
            )
            if resp2.status_code in (200, 201):
                total += len(batch)
            else:
                print(f'    Upload error batch {i}: {resp2.status_code} {resp2.text[:150]}')
    return total


def crawl_one(stock_code):
    """한 종목 크롤링 → trades 리스트 반환"""
    corp_code, corp_name = get_corp_code_cached(stock_code)
    if not corp_code:
        return None, 0

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
            "ticker": stock_code,
            "stock_name": corp_name,
            "insider_name": row.get("repror", "").strip(),
            "position": row.get("isu_exctv_ofcps", "").strip() or None,
            "trade_type": "매도" if shares < 0 else "매수",
            "shares": abs(shares),
            "price": None,
            "total_amount": None,
            "trade_date": row.get("rcept_dt", ""),
            "disclosure_date": row.get("rcept_dt", ""),
            "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row.get('rcept_no', '')}"
        })

    # older document parsing
    ele_dates = [t["trade_date"] for t in trades if t["trade_date"]]
    end_old = min(ele_dates).replace("-", "") if ele_dates else "20260101"
    old_discs = get_old_disclosures(corp_code, end_old)
    for i, disc in enumerate(old_discs):
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

    return corp_name, unique


def main():
    tickers = get_kr_tickers()
    print(f'[DART 내부자 일괄 크롤링] {len(tickers)}개 종목 (삼성전자/심텍 제외)')
    print()

    results = []
    total_trades = 0
    success = 0
    fail = 0

    for i, ticker in enumerate(tickers):
        print(f'[{i+1:3d}/{len(tickers)}] {ticker}', end=' ', flush=True)
        try:
            name, trades = crawl_one(ticker)
            if name is None:
                print('-> corp_code not found (skip)')
                fail += 1
                results.append({'ticker': ticker, 'status': 'not_found', 'count': 0})
                time.sleep(2)
                continue

            if not trades:
                print(f'-> {name}: 0건')
                results.append({'ticker': ticker, 'name': name, 'status': 'ok', 'count': 0, 'uploaded': 0})
                time.sleep(2)
                continue

            uploaded = upload_insider_trades(trades)
            print(f'-> {name}: {len(trades)}건 크롤링, {uploaded}건 업로드')
            results.append({
                'ticker': ticker, 'name': name, 'status': 'ok',
                'count': len(trades), 'uploaded': uploaded
            })
            total_trades += len(trades)
            success += 1
        except Exception as e:
            print(f'-> ERROR: {e}')
            results.append({'ticker': ticker, 'status': 'error', 'error': str(e)})
            fail += 1

        time.sleep(2)  # DART rate limit

    print(f'\n{"="*60}')
    print(f'완료: 성공 {success}, 실패 {fail}, 총 {total_trades}건')
    print(f'{"="*60}')

    # 종목별 건수 보고
    for r in sorted(results, key=lambda x: x.get('count', 0), reverse=True):
        if r.get('count', 0) > 0:
            print(f"  {r['ticker']} {r.get('name',''):12s}: {r['count']:4d}건")

    # Save
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'insider_batch_result.json')
    json.dump(results, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n결과 저장: {out_path}')


if __name__ == '__main__':
    main()
