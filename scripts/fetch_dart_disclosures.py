# -*- coding: utf-8 -*-
"""
DART 공시 수집 스크립트
=====================
한국 종목 대상 최근 1년치 주요 공시 수집 → data/disclosures.json

사용법:
  python scripts/fetch_dart_disclosures.py
  python scripts/fetch_dart_disclosures.py --days 90     # 최근 90일
  python scripts/fetch_dart_disclosures.py --stock 005930 # 특정 종목만
"""

import os
import sys
import json
import time
import zipfile
import argparse
import xml.etree.ElementTree as ET
import urllib.request
import ssl
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / '.env.local'
CORP_CODE_CACHE = PROJECT_ROOT / 'data' / 'dart_corp_codes.json'
OUTPUT_PATH = PROJECT_ROOT / 'data' / 'disclosures.json'

# SSL (Windows 환경 대응)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def load_api_key():
    if os.environ.get('DART_API_KEY'):
        return os.environ['DART_API_KEY']
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding='utf-8').splitlines():
            if line.startswith('DART_API_KEY='):
                return line.split('=', 1)[1].strip()
    print('[ERROR] DART_API_KEY not found in .env.local')
    sys.exit(1)


def dart_get(url):
    """DART API GET -> JSON dict"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def build_corp_code_map(api_key):
    """corpCode.xml ZIP -> {stock_code: corp_code} 매핑 (7일 캐시)"""
    if CORP_CODE_CACHE.exists():
        age = time.time() - CORP_CODE_CACHE.stat().st_mtime
        if age < 7 * 86400:
            with open(CORP_CODE_CACHE, encoding='utf-8') as f:
                return json.load(f)

    print('[1/3] corpCode.xml 다운로드...')
    url = f'https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    zip_path = PROJECT_ROOT / 'data' / 'corpCode.zip'
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        zip_path.write_bytes(r.read())

    mapping = {}
    with zipfile.ZipFile(zip_path) as z:
        with z.open('CORPCODE.xml') as f:
            tree = ET.parse(f)
    for corp in tree.getroot().findall('list'):
        sc = corp.findtext('stock_code', '').strip()
        cc = corp.findtext('corp_code', '').strip()
        if sc and cc and len(sc) == 6:
            mapping[sc] = cc

    zip_path.unlink(missing_ok=True)
    with open(CORP_CODE_CACHE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False)
    print(f'  -> {len(mapping)}개 종목 매핑 완료')
    return mapping


def fetch_disclosures_for_stock(api_key, corp_code, stock_code, bgn_de, end_de):
    """단일 종목 주요 공시 수집 (B,C,D,E,I)"""
    results = []

    for ty in ['B', 'C', 'D', 'E', 'I']:
        url = (f'https://opendart.fss.or.kr/api/list.json?'
               f'crtfc_key={api_key}&corp_code={corp_code}'
               f'&bgn_de={bgn_de}&end_de={end_de}'
               f'&pblntf_ty={ty}&page_count=100')
        try:
            data = dart_get(url)
        except Exception as e:
            print(f'    [WARN] {stock_code} ty={ty}: {e}')
            time.sleep(1)
            continue

        if data.get('status') == '020':
            print(f'  [LIMIT] 일일 한도 초과! 중단합니다.')
            return results, True  # limit hit

        if data.get('status') != '000':
            continue

        for item in data.get('list', []):
            results.append({
                'stock_code': stock_code,
                'corp_code': corp_code,
                'corp_name': item.get('corp_name', ''),
                'corp_cls': item.get('corp_cls', ''),
                'report_nm': item.get('report_nm', ''),
                'rcept_no': item.get('rcept_no', ''),
                'rcept_dt': item.get('rcept_dt', ''),
                'flr_nm': item.get('flr_nm', ''),
                'rm': item.get('rm', ''),
                'pblntf_ty': ty,
            })
        time.sleep(0.3)

    return results, False


# ── 중요 공시 필터 ──

IMPORTANT_KEYWORDS = [
    # B001 주요사항보고서
    '주요사항보고서',
    # C001 유상증자, C002 CB/BW, C004 합병
    '증권신고', '유상증자', '전환사채', '신주인수권부사채', '합병', '분할',
    # D001 대량보유
    '대량보유',
    # E001/E002 자기주식
    '자기주식', '자사주',
    # I 거래소공시 (핵심)
    '영업(잠정)실적', '잠정실적', '매출액또는손익구조',
    '기업가치제고', '공정공시', '주주총회',
    '최대주주', '전환가액', '감자', '배당',
]

NOISE_KEYWORDS = [
    '임원ㆍ주요주주특정증권등소유상황보고서',
    '의결권대리행사',
]


def is_important(item):
    nm = item.get('report_nm', '')
    for noise in NOISE_KEYWORDS:
        if noise in nm:
            return False
    for kw in IMPORTANT_KEYWORDS:
        if kw in nm:
            return True
    if item.get('pblntf_ty') == 'I':
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description='DART 주요 공시 수집')
    parser.add_argument('--days', type=int, default=365, help='수집 기간 (기본 365일)')
    parser.add_argument('--stock', type=str, default=None, help='특정 종목코드만')
    args = parser.parse_args()

    api_key = load_api_key()
    corp_map = build_corp_code_map(api_key)

    # 한국 종목 목록
    tickers_path = PROJECT_ROOT / 'data' / 'stock_tickers.json'
    with open(tickers_path, encoding='utf-8') as f:
        all_tickers = json.load(f)
    kr_tickers = [t for t in all_tickers if t.isdigit() and len(t) == 6]

    if args.stock:
        kr_tickers = [t for t in kr_tickers if t == args.stock]
        if not kr_tickers:
            print(f'[ERROR] {args.stock} not found')
            sys.exit(1)

    end_de = datetime.now().strftime('%Y%m%d')
    bgn_de = (datetime.now() - timedelta(days=args.days)).strftime('%Y%m%d')

    print(f'[2/3] 공시 수집: {len(kr_tickers)}종목, {bgn_de}~{end_de}')

    all_disclosures = []
    skipped = 0
    for i, stock_code in enumerate(kr_tickers):
        corp_code = corp_map.get(stock_code)
        if not corp_code:
            skipped += 1
            continue

        items, limit_hit = fetch_disclosures_for_stock(
            api_key, corp_code, stock_code, bgn_de, end_de)
        important = [it for it in items if is_important(it)]
        all_disclosures.extend(important)

        if (i + 1) % 10 == 0 or i == len(kr_tickers) - 1:
            print(f'  [{i+1}/{len(kr_tickers)}] {stock_code}: '
                  f'전체 {len(items)}건 -> 주요 {len(important)}건 '
                  f'(누적 {len(all_disclosures)}건)')

        if limit_hit:
            print(f'  [!] API 한도 초과 — {i+1}번째 종목까지 수집 후 저장합니다.')
            break

        # 20종목마다 2초 쉬기 (일일 10,000건 한도 대비)
        if (i + 1) % 20 == 0:
            time.sleep(2)

    # 날짜 내림차순 + 중복 제거
    all_disclosures.sort(key=lambda x: x['rcept_dt'], reverse=True)
    seen = set()
    deduped = []
    for d in all_disclosures:
        if d['rcept_no'] not in seen:
            seen.add(d['rcept_no'])
            deduped.append(d)

    print(f'\n[3/3] 저장: {len(deduped)}건 (중복 {len(all_disclosures) - len(deduped)}건 제거)')
    if skipped:
        print(f'  -> corp_code 매핑 없는 종목: {skipped}개 스킵')

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump({
            'meta': {
                'collected_at': datetime.now().isoformat(),
                'period': f'{bgn_de}~{end_de}',
                'stocks': len(kr_tickers) - skipped,
                'total_count': len(deduped),
            },
            'disclosures': deduped,
        }, f, ensure_ascii=False, indent=2)

    print(f'  -> {OUTPUT_PATH.relative_to(PROJECT_ROOT)} '
          f'({OUTPUT_PATH.stat().st_size // 1024}KB)')

    # 유형별 통계
    ty_count = Counter(d['pblntf_ty'] for d in deduped)
    ty_labels = {'B': '주요사항', 'C': '발행공시', 'D': '지분공시',
                 'E': '기타공시', 'I': '거래소공시'}
    print('\n  유형별 건수:')
    for ty, cnt in sorted(ty_count.items()):
        print(f'    [{ty}] {ty_labels.get(ty, ty)}: {cnt}건')


if __name__ == '__main__':
    main()
