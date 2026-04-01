# -*- coding: utf-8 -*-
"""
DART 내부자 거래 전체 재크롤링 — 수정된 파서로 전 종목 upsert.
기존 정상 데이터 유지, 한자(영문) 버그로 빠진 거래를 올바른 이름으로 재수집.

Usage: python scripts/crawl_dart_insider_regen.py
"""
import sys, os, json, time, requests, zipfile, io, warnings
import xml.etree.ElementTree as ET
from datetime import datetime

warnings.filterwarnings('ignore')
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


def upload_trades(trades):
    """Supabase upsert (100건 배치). 빈 이름은 제외."""
    clean = [t for t in trades if t.get('insider_name')]
    total = 0
    for i in range(0, len(clean), 100):
        batch = clean[i:i+100]
        resp = requests.post(
            f"{SB_URL}/insider_trades",
            headers=SB_HEADERS,
            json=batch
        )
        if resp.status_code in (200, 201):
            total += len(batch)
        # duplicate/conflict는 무시 — 기존 정상 데이터 유지
    return total


def crawl_one(corp):
    stock_code = corp['stock_code']
    corp_code = corp['corp_code']
    corp_name = corp['corp_name']

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

    all_corps = load_all_listed()
    all_corps.sort(key=lambda x: x['stock_code'])

    print(f'\n[전체 재크롤링] {len(all_corps)}개 종목 — upsert 모드')
    print(f'시작: {start.strftime("%Y-%m-%d %H:%M")}\n', flush=True)

    total_trades = 0
    success = 0
    empty = 0
    errors = []
    skipped_empty_name = 0

    for i, corp in enumerate(all_corps):
        ticker = corp['stock_code']
        name = corp['corp_name']

        try:
            trades = crawl_one(corp)
            # 빈 이름 필터
            valid = [t for t in trades if t.get('insider_name')]
            skipped_empty_name += len(trades) - len(valid)

            if not valid:
                empty += 1
            else:
                uploaded = upload_trades(valid)
                total_trades += len(valid)
                success += 1
                if len(valid) >= 10 or (i + 1) % 50 == 0:
                    print(f'[{i+1:4d}/{len(all_corps)}] {ticker} {name}: {len(valid)}건', flush=True)

        except Exception as e:
            err_msg = str(e)[:100]
            errors.append({'ticker': ticker, 'name': name, 'error': err_msg})

        time.sleep(2)

        if (i + 1) % 50 == 0:
            elapsed = (datetime.now() - start).total_seconds() / 60
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (len(all_corps) - i - 1) / rate if rate > 0 else 0
            print(f'  === {i+1}/{len(all_corps)} | {elapsed:.0f}분 | 잔여 {remaining:.0f}분 | 누적 {total_trades}건 | 에러 {len(errors)} | 빈이름스킵 {skipped_empty_name} ===', flush=True)

    elapsed = (datetime.now() - start).total_seconds() / 60
    print(f'\n{"="*60}')
    print(f'완료: {elapsed:.0f}분 소요')
    print(f'성공: {success}, 빈 종목: {empty}, 에러: {len(errors)}')
    print(f'총 업로드: {total_trades}건 (빈이름 스킵: {skipped_empty_name})')
    print(f'{"="*60}', flush=True)

    if errors:
        print(f'\n에러 ({len(errors)}건):')
        for e in errors[:30]:
            print(f'  {e["ticker"]} {e["name"]}: {e["error"]}')

    result = {
        'ts': datetime.now().isoformat(),
        'elapsed_min': round(elapsed, 1),
        'total_corps': len(all_corps),
        'success': success, 'empty': empty,
        'errors_count': len(errors),
        'total_trades': total_trades,
        'skipped_empty_name': skipped_empty_name,
        'errors': errors
    }
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'insider_regen_result.json')
    json.dump(result, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n결과 저장: {out_path}', flush=True)


if __name__ == '__main__':
    main()
