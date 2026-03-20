# -*- coding: utf-8 -*-
"""
DART DS005 상세 데이터 수집 → disclosures.json에 merge
=======================================================
자사주 취득/처분 + 유상증자 상세 정보 (수량, 금액, 기간 등)

사용법:
  python scripts/fetch_dart_details.py
  python scripts/fetch_dart_details.py --dry-run   # API 호출 없이 대상만 확인
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import ssl
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / '.env.local'
DISCLOSURES_PATH = PROJECT_ROOT / 'data' / 'disclosures.json'

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
    sys.exit('[ERROR] DART_API_KEY not found')


def dart_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def parse_num(s):
    """'3,572,800,000,000' -> 3572800000000, '-' -> None"""
    if not s or s.strip() == '-':
        return None
    try:
        return int(s.replace(',', ''))
    except ValueError:
        return None


def parse_date(s):
    """'2026년 01월 30일' -> '2026.01.30', '-' -> None"""
    if not s or s.strip() == '-':
        return None
    import re
    m = re.search(r'(\d{4})\D+(\d{2})\D+(\d{2})', s)
    return f'{m.group(1)}.{m.group(2)}.{m.group(3)}' if m else None


def fetch_treasury_acquire(api_key, corp_code, bgn_de, end_de):
    """자기주식 취득 결정 상세"""
    url = (f'https://opendart.fss.or.kr/api/tsstkAqDecsn.json?'
           f'crtfc_key={api_key}&corp_code={corp_code}'
           f'&bgn_de={bgn_de}&end_de={end_de}')
    data = dart_get(url)
    if data.get('status') != '000':
        return []
    results = []
    for item in data.get('list', []):
        shares = parse_num(item.get('aqpln_stk_ostk'))
        amount = parse_num(item.get('aqpln_prc_ostk'))
        bgd = parse_date(item.get('aqexpd_bgd'))
        edd = parse_date(item.get('aqexpd_edd'))
        results.append({
            'rcept_no': item.get('rcept_no'),
            'detail_type': 'treasury_acquire',
            'shares': shares,
            'amount': amount,
            'period_start': bgd,
            'period_end': edd,
            'purpose': item.get('aq_pp', ''),
            'method': item.get('aq_mth', ''),
        })
    return results


def fetch_treasury_dispose(api_key, corp_code, bgn_de, end_de):
    """자기주식 처분 결정 상세"""
    url = (f'https://opendart.fss.or.kr/api/tsstkDpDecsn.json?'
           f'crtfc_key={api_key}&corp_code={corp_code}'
           f'&bgn_de={bgn_de}&end_de={end_de}')
    data = dart_get(url)
    if data.get('status') != '000':
        return []
    results = []
    for item in data.get('list', []):
        shares = parse_num(item.get('dppln_stk_ostk'))
        amount = parse_num(item.get('dppln_prc_ostk'))
        bgd = parse_date(item.get('dpprpd_bgd'))
        edd = parse_date(item.get('dpprpd_edd'))
        results.append({
            'rcept_no': item.get('rcept_no'),
            'detail_type': 'treasury_dispose',
            'shares': shares,
            'amount': amount,
            'period_start': bgd,
            'period_end': edd,
            'purpose': item.get('dp_pp', ''),
        })
    return results


def fetch_capital_increase(api_key, corp_code, bgn_de, end_de):
    """유상증자 결정 상세"""
    url = (f'https://opendart.fss.or.kr/api/piicDecsn.json?'
           f'crtfc_key={api_key}&corp_code={corp_code}'
           f'&bgn_de={bgn_de}&end_de={end_de}')
    data = dart_get(url)
    if data.get('status') != '000':
        return []
    results = []
    for item in data.get('list', []):
        new_shares = parse_num(item.get('nstk_ostk_cnt'))
        face_value = parse_num(item.get('fv_ps'))
        # 자금용도 합산
        fund_keys = ['fdpp_fclt', 'fdpp_bsninh', 'fdpp_op',
                     'fdpp_dtrp', 'fdpp_ocsa', 'fdpp_etc']
        fund_total = 0
        for fk in fund_keys:
            v = parse_num(item.get(fk))
            if v:
                fund_total += v
        results.append({
            'rcept_no': item.get('rcept_no'),
            'detail_type': 'capital_increase',
            'new_shares': new_shares,
            'face_value': face_value,
            'fund_total': fund_total or None,
            'method': item.get('ic_mthn', ''),
        })
    return results


def format_amount_kr(n):
    """숫자 -> 한글 금액 (억/조)"""
    if n is None:
        return None
    if n >= 1_0000_0000_0000:
        return f'{n / 1_0000_0000_0000:.1f}조원'
    if n >= 1_0000_0000:
        return f'{n / 1_0000_0000:,.0f}억원'
    if n >= 1_0000:
        return f'{n / 1_0000:,.0f}만원'
    return f'{n:,}원'


def format_shares_kr(n):
    """숫자 -> 한글 주식수"""
    if n is None:
        return None
    if n >= 1_0000_0000:
        return f'{n / 1_0000_0000:.1f}억주'
    if n >= 1_0000:
        return f'{n / 1_0000:,.0f}만주'
    return f'{n:,}주'


def build_summary(detail):
    """상세 데이터 -> 한줄 요약"""
    dt = detail.get('detail_type', '')

    if dt == 'treasury_acquire':
        parts = []
        s = detail.get('shares')
        if s:
            parts.append(f'{format_shares_kr(s)} 취득')
        a = detail.get('amount')
        if a:
            parts.append(format_amount_kr(a))
        bgd = detail.get('period_start')
        edd = detail.get('period_end')
        if bgd and edd:
            parts.append(f'{bgd}~{edd}')
        pp = detail.get('purpose', '')
        if pp and '주주가치' in pp:
            parts.append('주주가치 제고')
        elif pp and '임직원' in pp:
            parts.append('임직원 보상')
        return ' · '.join(parts) if parts else None

    if dt == 'treasury_dispose':
        parts = []
        s = detail.get('shares')
        if s:
            parts.append(f'{format_shares_kr(s)} 처분')
        a = detail.get('amount')
        if a:
            parts.append(format_amount_kr(a))
        pp = detail.get('purpose', '')
        if pp:
            short = pp[:20]
            parts.append(short)
        return ' · '.join(parts) if parts else None

    if dt == 'capital_increase':
        parts = []
        ns = detail.get('new_shares')
        if ns:
            parts.append(f'신주 {format_shares_kr(ns)}')
        ft = detail.get('fund_total')
        if ft:
            parts.append(format_amount_kr(ft))
        m = detail.get('method', '')
        if m:
            parts.append(m[:15])
        return ' · '.join(parts) if parts else None

    return None


def main():
    parser = argparse.ArgumentParser(description='DART DS005 상세 수집')
    parser.add_argument('--dry-run', action='store_true', help='대상만 확인')
    args = parser.parse_args()

    api_key = load_api_key()

    with open(DISCLOSURES_PATH, encoding='utf-8') as f:
        data = json.load(f)

    disclosures = data['disclosures']
    bgn_de = data['meta']['period'].split('~')[0]
    end_de = data['meta']['period'].split('~')[1]

    # 대상 추출: 자사주 + 증자 종목의 고유 corp_code
    treasury_corps = set()
    capinc_corps = set()
    for d in disclosures:
        nm = d['report_nm']
        cc = d['corp_code']
        if '자기주식취득' in nm:
            treasury_corps.add(cc)
        if '자기주식처분' in nm:
            treasury_corps.add(cc)
        if '유상증자' in nm:
            capinc_corps.add(cc)

    print(f'대상: 자사주 {len(treasury_corps)}개 종목, 증자 {len(capinc_corps)}개 종목')
    total_api_calls = len(treasury_corps) * 2 + len(capinc_corps)
    print(f'API 호출 예상: {total_api_calls}건')

    if args.dry_run:
        return

    # 수집
    all_details = {}  # rcept_no -> detail
    errors = 0

    print('\n[1/2] 자사주 취득/처분 상세 수집...')
    for i, cc in enumerate(sorted(treasury_corps)):
        try:
            acq = fetch_treasury_acquire(api_key, cc, bgn_de, end_de)
            for d in acq:
                all_details[d['rcept_no']] = d
            time.sleep(0.3)

            dsp = fetch_treasury_dispose(api_key, cc, bgn_de, end_de)
            for d in dsp:
                all_details[d['rcept_no']] = d
            time.sleep(0.3)
        except Exception as e:
            errors += 1
            print(f'  [WARN] {cc}: {e}')
            time.sleep(1)

        if (i + 1) % 10 == 0:
            print(f'  [{i+1}/{len(treasury_corps)}] 누적 {len(all_details)}건')
            time.sleep(1)

    print(f'  자사주 완료: {len(all_details)}건')

    print('\n[2/2] 유상증자 상세 수집...')
    ci_before = len(all_details)
    for i, cc in enumerate(sorted(capinc_corps)):
        try:
            ci = fetch_capital_increase(api_key, cc, bgn_de, end_de)
            for d in ci:
                all_details[d['rcept_no']] = d
            time.sleep(0.3)
        except Exception as e:
            errors += 1
            print(f'  [WARN] {cc}: {e}')
            time.sleep(1)

        if (i + 1) % 10 == 0:
            print(f'  [{i+1}/{len(capinc_corps)}] 누적 {len(all_details) - ci_before}건')

    print(f'  증자 완료: {len(all_details) - ci_before}건')

    # Merge into disclosures
    merged = 0
    for d in disclosures:
        rn = d.get('rcept_no', '')
        if rn in all_details:
            detail = all_details[rn]
            d['detail'] = detail
            d['detail_summary'] = build_summary(detail)
            merged += 1

    data['meta']['detail_merged'] = merged
    data['meta']['detail_collected_at'] = __import__('datetime').datetime.now().isoformat()

    with open(DISCLOSURES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'\n=== 결과 ===')
    print(f'상세 수집: {len(all_details)}건')
    print(f'공시에 merge: {merged}건')
    if errors:
        print(f'에러: {errors}건')
    print(f'저장: {DISCLOSURES_PATH.relative_to(PROJECT_ROOT)} '
          f'({DISCLOSURES_PATH.stat().st_size // 1024}KB)')

    # 샘플 출력
    print('\n=== 샘플 ===')
    count = 0
    for d in disclosures:
        if d.get('detail_summary') and count < 5:
            print(f"  {d['corp_name']} | {d['detail_summary']}")
            count += 1


if __name__ == '__main__':
    main()
