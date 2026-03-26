# -*- coding: utf-8 -*-
"""
DART 공시 수집 스크립트
=====================
한국 종목 대상 주요 공시 수집 → data/disclosures.json

사용법:
  python scripts/fetch_dart_disclosures.py                      # 최근 1년
  python scripts/fetch_dart_disclosures.py --from-date 20200101  # 2020년부터 전체
  python scripts/fetch_dart_disclosures.py --resume              # 이전 수집 이어서
  python scripts/fetch_dart_disclosures.py --stock 005930        # 특정 종목만
  python scripts/fetch_dart_disclosures.py --days 90             # 최근 90일
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
PROGRESS_PATH = PROJECT_ROOT / 'data' / 'dart_collect_progress.json'

# SSL (Windows 환경 대응)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def load_api_keys():
    """Load all DART API keys from .env.local"""
    keys = []
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding='utf-8').splitlines():
            if line.startswith('DART_API_KEY') and '=' in line:
                val = line.split('=', 1)[1].strip()
                if val and val not in keys:
                    keys.append(val)
    if os.environ.get('DART_API_KEY'):
        k = os.environ['DART_API_KEY']
        if k not in keys:
            keys.insert(0, k)
    if not keys:
        print('[ERROR] DART_API_KEY not found in .env.local')
        sys.exit(1)
    return keys


class KeyRotator:
    """API 키 로테이션 + limit 관리"""
    def __init__(self, keys):
        self.keys = keys
        self.idx = 0
        self.exhausted = set()  # limit hit된 키 인덱스

    @property
    def current(self):
        return self.keys[self.idx]

    def rotate(self):
        """다음 키로 전환. 모든 키 소진 시 True 반환."""
        self.exhausted.add(self.idx)
        if len(self.exhausted) >= len(self.keys):
            return True  # 모든 키 소진
        # 다음 사용 가능한 키 찾기
        for _ in range(len(self.keys)):
            self.idx = (self.idx + 1) % len(self.keys)
            if self.idx not in self.exhausted:
                return False
        return True

    def alternate(self):
        """요청마다 키 번갈아 사용 (소진되지 않은 키만)"""
        for _ in range(len(self.keys)):
            self.idx = (self.idx + 1) % len(self.keys)
            if self.idx not in self.exhausted:
                return
        # 전부 소진이면 현재 키 유지


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

    print('[INIT] corpCode.xml download...')
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
    print(f'  -> {len(mapping)} tickers mapped')
    return mapping


def make_year_ranges(bgn_de, end_de):
    """기간을 연도별 chunk로 분할 (DART API 1년 제한 대응)"""
    ranges = []
    bgn = datetime.strptime(bgn_de, '%Y%m%d')
    end = datetime.strptime(end_de, '%Y%m%d')

    current = bgn
    while current < end:
        year_end = datetime(current.year, 12, 31)
        chunk_end = min(year_end, end)
        ranges.append((current.strftime('%Y%m%d'), chunk_end.strftime('%Y%m%d')))
        current = chunk_end + timedelta(days=1)

    return ranges


def fetch_disclosures_for_stock(rotator, corp_code, stock_code, year_ranges):
    """단일 종목 전체 기간 주요 공시 수집 (B,C,D,E,I × 연도별)"""
    results = []

    for bgn_de, end_de in year_ranges:
        for ty in ['B', 'C', 'D', 'E', 'I']:
            url = (f'https://opendart.fss.or.kr/api/list.json?'
                   f'crtfc_key={rotator.current}&corp_code={corp_code}'
                   f'&bgn_de={bgn_de}&end_de={end_de}'
                   f'&pblntf_ty={ty}&page_count=100')
            try:
                data = dart_get(url)
            except Exception as e:
                print(f'    [WARN] {stock_code} {bgn_de[:4]} ty={ty}: {e}')
                time.sleep(1)
                continue

            if data.get('status') == '020':
                # limit hit → 다른 키로 전환
                all_exhausted = rotator.rotate()
                if all_exhausted:
                    print(f'  [LIMIT] All API keys exhausted!')
                    return results, True
                print(f'  [LIMIT] Key exhausted, switching to key #{rotator.idx + 1}')
                # 전환 후 같은 요청 재시도
                url = url.replace(url.split('crtfc_key=')[1].split('&')[0], rotator.current)
                try:
                    data = dart_get(url)
                except Exception:
                    continue
                if data.get('status') == '020':
                    all_exhausted = rotator.rotate()
                    if all_exhausted:
                        return results, True

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
            rotator.alternate()  # 요청마다 키 번갈아

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


def load_existing():
    """기존 disclosures.json 로드 → {rcept_no: disclosure} 맵"""
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, encoding='utf-8') as f:
            data = json.load(f)
        existing = {}
        for d in data.get('disclosures', []):
            existing[d['rcept_no']] = d
        return existing, data.get('meta', {})
    return {}, {}


def load_progress():
    """resume용 진행 상태 로드"""
    if PROGRESS_PATH.exists():
        with open(PROGRESS_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {'completed_stocks': [], 'from_date': None}


def save_progress(completed_stocks, from_date):
    """진행 상태 저장"""
    with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
        json.dump({
            'completed_stocks': completed_stocks,
            'from_date': from_date,
            'last_run': datetime.now().isoformat(),
        }, f, ensure_ascii=False, indent=2)


def save_output(existing_map, new_disclosures, meta_overrides):
    """기존 + 신규 merge 후 저장"""
    # 기존 데이터에 신규 추가 (rcept_no 기준 dedup)
    merged = dict(existing_map)
    added = 0
    for d in new_disclosures:
        if d['rcept_no'] not in merged:
            merged[d['rcept_no']] = d
            added += 1

    # 날짜 내림차순 정렬
    sorted_list = sorted(merged.values(), key=lambda x: x.get('rcept_dt', ''), reverse=True)

    # 날짜 범위 계산
    dates = [d['rcept_dt'] for d in sorted_list if d.get('rcept_dt')]
    period = f'{min(dates)}~{max(dates)}' if dates else ''

    # 기존 meta 보존 (ai_summary_count 등)
    meta = {
        'collected_at': datetime.now().isoformat(),
        'period': period,
        'stocks': len(set(d['stock_code'] for d in sorted_list)),
        'total_count': len(sorted_list),
    }
    # 기존 AI 관련 meta 보존
    for key in ['detail_merged', 'ai_summary_count', 'ai_analysis_count', 'doc_analysis_count']:
        if key in meta_overrides:
            meta[key] = meta_overrides[key]

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump({
            'meta': meta,
            'disclosures': sorted_list,
        }, f, ensure_ascii=False, indent=2)

    return len(sorted_list), added


def main():
    parser = argparse.ArgumentParser(description='DART 주요 공시 수집')
    parser.add_argument('--days', type=int, default=None, help='수집 기간 (일)')
    parser.add_argument('--from-date', type=str, default=None, help='시작일 (YYYYMMDD, 예: 20200101)')
    parser.add_argument('--stock', type=str, default=None, help='특정 종목코드만')
    parser.add_argument('--resume', action='store_true', help='이전 수집 이어서')
    args = parser.parse_args()

    api_keys = load_api_keys()
    print(f'[INIT] API keys: {len(api_keys)}개')
    rotator = KeyRotator(api_keys)

    corp_map = build_corp_code_map(rotator.current)

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

    # 기간 결정
    end_de = datetime.now().strftime('%Y%m%d')
    if args.from_date:
        bgn_de = args.from_date
    elif args.days:
        bgn_de = (datetime.now() - timedelta(days=args.days)).strftime('%Y%m%d')
    else:
        bgn_de = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')

    # 연도별 분할
    year_ranges = make_year_ranges(bgn_de, end_de)
    print(f'[INFO] Period: {bgn_de} ~ {end_de} ({len(year_ranges)} year chunks)')

    # 기존 데이터 로드
    existing_map, existing_meta = load_existing()
    print(f'[INFO] Existing disclosures: {len(existing_map)}')

    # Resume 처리
    completed_stocks = set()
    if args.resume:
        progress = load_progress()
        completed_stocks = set(progress.get('completed_stocks', []))
        if progress.get('from_date'):
            bgn_de = progress['from_date']
            year_ranges = make_year_ranges(bgn_de, end_de)
        print(f'[RESUME] {len(completed_stocks)} stocks already completed, skipping')

    print(f'[COLLECT] {len(kr_tickers)} stocks, {bgn_de}~{end_de}')

    new_disclosures = []
    skipped = 0
    limit_hit = False
    api_calls = 0

    for i, stock_code in enumerate(kr_tickers):
        if stock_code in completed_stocks:
            continue

        corp_code = corp_map.get(stock_code)
        if not corp_code:
            skipped += 1
            continue

        items, limit_hit = fetch_disclosures_for_stock(
            rotator, corp_code, stock_code, year_ranges)
        important = [it for it in items if is_important(it)]
        # 기존에 없는 것만 추가
        new_items = [it for it in important if it['rcept_no'] not in existing_map]
        new_disclosures.extend(new_items)
        api_calls += len(year_ranges) * 5  # rough estimate

        completed_stocks.add(stock_code)

        if (i + 1) % 10 == 0 or i == len(kr_tickers) - 1:
            active = len(kr_tickers) - len(completed_stocks.intersection(set(kr_tickers[:i])))
            print(f'  [{i+1}/{len(kr_tickers)}] {stock_code}: '
                  f'{len(items)}->{len(important)} important, '
                  f'+{len(new_items)} new '
                  f'(total new: {len(new_disclosures)})')

        if limit_hit:
            print(f'  [!] API limit — saving progress after {i+1} stocks.')
            break

        # 20종목마다 중간 저장 + 2초 쉬기
        if (i + 1) % 20 == 0:
            save_progress(list(completed_stocks), bgn_de)
            time.sleep(2)

    # 최종 저장
    total, added = save_output(existing_map, new_disclosures, existing_meta)
    save_progress(list(completed_stocks), bgn_de)

    print(f'\n[DONE] Total: {total} disclosures (+{added} new)')
    if skipped:
        print(f'  -> No corp_code: {skipped} stocks skipped')
    print(f'  -> Completed stocks: {len(completed_stocks)}/{len(kr_tickers)}')
    print(f'  -> {OUTPUT_PATH.relative_to(PROJECT_ROOT)} '
          f'({OUTPUT_PATH.stat().st_size // 1024}KB)')

    if limit_hit:
        remaining = len(kr_tickers) - len(completed_stocks)
        print(f'\n  [!] {remaining} stocks remaining. Run with --resume to continue.')

    # 유형별 통계
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        final_data = json.load(f)
    ty_count = Counter(d['pblntf_ty'] for d in final_data['disclosures'])
    ty_labels = {'B': 'Major', 'C': 'Issuance', 'D': 'Ownership',
                 'E': 'Other', 'I': 'Exchange'}
    print('\n  Type breakdown:')
    for ty, cnt in sorted(ty_count.items()):
        print(f'    [{ty}] {ty_labels.get(ty, ty)}: {cnt}')


if __name__ == '__main__':
    main()
