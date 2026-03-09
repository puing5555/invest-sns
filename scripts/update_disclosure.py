#!/usr/bin/env python3
"""
DART API 공시 수집 → public/disclosure_seed.json 업데이트

사용법:
  python scripts/update_disclosure.py              # 오늘 공시
  python scripts/update_disclosure.py --days 7    # 최근 7일
  python scripts/update_disclosure.py --start 20260301 --end 20260309  # 기간 지정
"""
import sys, os, json, uuid, ssl, urllib.request, argparse
from datetime import datetime, timedelta
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
OUTPUT_PATH  = os.path.join(PROJECT_ROOT, 'public', 'disclosure_seed.json')

DART_API_KEY = "b6ea29c886e5d9009155a3360d3dc8a8932a523b"
DART_BASE_URL = "https://opendart.fss.or.kr/api"

# ── 공시 유형 분류 ────────────────────────────────────────────
def classify_type(report_nm: str) -> str:
    n = report_nm.lower()
    if any(x in n for x in ['실적', '손익', '매출', '영업이익', '분기보고', '사업보고']):
        return '실적'
    if any(x in n for x in ['자기주식', '자사주']):
        return '자기주식'
    if any(x in n for x in ['전환사채', 'cb', 'bw', '신주인수권']):
        return '전환사채'
    if any(x in n for x in ['풍문', '조회공시']):
        return '풍문'
    if any(x in n for x in ['수주', '단일판매', '공급계약', '대규모계약']):
        return '수주'
    if any(x in n for x in ['유상증자', '제3자배정']):
        return '유상증자'
    if any(x in n for x in ['합병', '분할', '영업양수']):
        return '합병분할'
    if any(x in n for x in ['배당']):
        return '배당'
    return '기타'

# ── importance → grade / ai_score 매핑 ───────────────────────
def assign_importance(report_nm: str, dtype: str) -> str:
    n = report_nm.lower()
    if any(x in n for x in ['상장폐지', '감자', '구속', '경영권분쟁', '부도']):
        return 'high'  # A
    if dtype in ('전환사채', '풍문') or any(x in n for x in ['대규모', '대형', '쇼크']):
        return 'high'  # B
    if dtype in ('실적', '수주', '자기주식', '배당'):
        return 'medium'  # C
    return 'low'  # D

def importance_to_score(importance: str) -> int:
    return {'high': 82, 'medium': 58, 'low': 32}.get(importance, 45)

def tone_to_impact(report_nm: str, dtype: str) -> str:
    n = report_nm.lower()
    if any(x in n for x in ['자기주식취득', '자사주매입', '수주', '계약체결', '배당']):
        return '긍정'
    if any(x in n for x in ['손실', '적자', '하락', '감소', '부도', '소송', '감자']):
        return '부정'
    return '중립'

# ── DART API 호출 ─────────────────────────────────────────────
def fetch_disclosures(start_dt: str, end_dt: str, page_count: int = 100) -> list:
    ctx = ssl.create_default_context()
    all_items = []

    for corp_cls in ('Y', 'K'):  # 유가증권 + 코스닥
        url = (f"{DART_BASE_URL}/list.json"
               f"?crtfc_key={DART_API_KEY}"
               f"&bgn_de={start_dt}&end_de={end_dt}"
               f"&page_no=1&page_count={page_count}"
               f"&corp_cls={corp_cls}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
                data = json.loads(r.read())
            if data.get('status') == '000':
                items = data.get('list', [])
                all_items.extend(items)
                print(f"  DART {'KOSPI' if corp_cls=='Y' else 'KOSDAQ'}: {len(items)}건")
            else:
                print(f"  DART 에러 ({corp_cls}): {data.get('message')}")
        except Exception as e:
            print(f"  DART 요청 실패 ({corp_cls}): {e}")

    return all_items

# ── DART 항목 → disclosure_seed 형식 변환 ────────────────────
def convert(item: dict) -> dict:
    dtype   = classify_type(item['report_nm'])
    imp     = assign_importance(item['report_nm'], dtype)
    impact  = tone_to_impact(item['report_nm'], dtype)
    score   = importance_to_score(imp)
    dt_str  = item['rcept_dt']  # YYYYMMDD
    dt_iso  = f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:8]}"

    return {
        'id':               item['rcept_no'],
        'corp_name':        item['corp_name'],
        'corp_code':        item['corp_code'],
        'stock_code':       item.get('stock_code', ''),
        'market':           'kospi' if item.get('corp_cls') == 'Y' else 'kosdaq',
        'report_nm':        item['report_nm'],
        'rcept_no':         item['rcept_no'],
        'rcept_dt':         dt_iso,
        'disclosure_type':  dtype,
        'importance':       imp,
        'ai_summary':       f"{item['corp_name']} — {item['report_nm']}",
        'ai_impact':        impact,
        'ai_impact_reason': f"{dtype} 유형 공시로 시장 {impact} 영향 예상.",
        'ai_score':         score,
        'source':           'dart',
        'created_at':       f"{dt_iso}T09:00:00+07:00",
    }

# ── 메인 ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days',  type=int, default=1, help='최근 N일 (기본 1)')
    parser.add_argument('--start', default=None, help='시작일 YYYYMMDD')
    parser.add_argument('--end',   default=None, help='종료일 YYYYMMDD')
    args = parser.parse_args()

    today = datetime.now()
    if args.start and args.end:
        start_dt, end_dt = args.start, args.end
    else:
        end_dt   = today.strftime('%Y%m%d')
        start_dt = (today - timedelta(days=args.days - 1)).strftime('%Y%m%d')

    print(f"수집 기간: {start_dt} ~ {end_dt}")
    raw = fetch_disclosures(start_dt, end_dt)
    if not raw:
        print("수집된 공시 없음")
        return

    new_items = [convert(i) for i in raw]
    print(f"변환 완료: {len(new_items)}건")

    # 기존 데이터 로드 + 중복 제거 (rcept_no 기준)
    existing = []
    if os.path.exists(OUTPUT_PATH):
        try:
            existing = json.load(open(OUTPUT_PATH, encoding='utf-8'))
        except Exception:
            existing = []

    existing_ids = {d.get('rcept_no') or d.get('id') for d in existing}
    added = [d for d in new_items if d['rcept_no'] not in existing_ids]
    print(f"신규 추가: {added and len(added) or 0}건 (중복 제외)")

    # 합치기: 새 것을 앞에, 날짜 내림차순
    merged = added + existing
    merged.sort(key=lambda x: x.get('rcept_dt', ''), reverse=True)

    # 최대 200건 유지
    merged = merged[:200]

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"저장 완료: {OUTPUT_PATH} ({len(merged)}건)")

    # 날짜별 통계
    dates = Counter(d['rcept_dt'] for d in added)
    for dt in sorted(dates, reverse=True)[:5]:
        print(f"  {dt}: {dates[dt]}건")

if __name__ == '__main__':
    main()
