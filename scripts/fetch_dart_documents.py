# -*- coding: utf-8 -*-
"""
DART 공시 원문 다운로드 + 원문 기반 해석 생성
=============================================
1. document.xml로 공시 원문 ZIP 다운로드
2. XML에서 텍스트 추출 (앞 3000자)
3. 원문에서 핵심 수치 파싱 → 구체적 해석 생성

사용법:
  python scripts/fetch_dart_documents.py --stock 005930 --limit 5  # 테스트
  python scripts/fetch_dart_documents.py --recent 180              # 최근 6개월
"""

import os
import sys
import json
import time
import re
import io
import zipfile
import argparse
import urllib.request
import ssl
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / '.env.local'
DISCLOSURES_PATH = PROJECT_ROOT / 'data' / 'disclosures.json'

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def load_dart_key():
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding='utf-8').splitlines():
            if line.startswith('DART_API_KEY='):
                return line.split('=', 1)[1].strip()
    sys.exit('[ERROR] DART_API_KEY not found')


def fetch_document_text(dart_key, rcept_no, max_chars=3000):
    """DART 공시 원문 텍스트 추출 (앞 max_chars자)"""
    url = f'https://opendart.fss.or.kr/api/document.xml?crtfc_key={dart_key}&rcept_no={rcept_no}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            data = r.read()
    except Exception as e:
        return None, str(e)

    if data[:2] != b'PK':
        # Not a ZIP — might be error XML
        text = data.decode('utf-8', errors='replace')
        if '<status>' in text:
            return None, text[:200]
        return text[:max_chars], None

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for name in z.namelist():
                with z.open(name) as f:
                    raw = f.read()
                for enc in ['utf-8', 'euc-kr', 'cp949']:
                    try:
                        text = raw.decode(enc)
                        text = re.sub(r'<[^>]+>', ' ', text)
                        text = re.sub(r'&[a-z]+;', ' ', text)
                        text = re.sub(r'\s+', ' ', text).strip()
                        return text[:max_chars], None
                    except UnicodeDecodeError:
                        continue
    except Exception as e:
        return None, str(e)

    return None, 'decode failed'


def parse_and_analyze(d, doc_text):
    """원문 텍스트에서 핵심 정보 추출 → 구체적 해석 생성"""
    corp = d['corp_name']
    nm = d['report_nm']
    existing_detail = d.get('detail', {})
    dt = existing_detail.get('detail_type', '')

    # 원문에서 자사주 비율 추출 (비율(%) 필드에서)
    ratio_match = re.search(r'비율\(%\)\s*([\d.]+)', doc_text)
    own_ratio = float(ratio_match.group(1)) if ratio_match else None

    # 발행주식총수: "발행주식총수의 1% : NN주" 패턴에서 역산
    total_shares = None
    pct1_match = re.search(r'발행주식총수의 1%[^0-9]{0,20}([\d,]+)', doc_text)
    if pct1_match:
        total_shares = int(pct1_match.group(1).replace(',', '')) * 100

    # 자사주 취득결과보고서 (별도 포맷 — 일별 매수 내역 테이블)
    if '취득결과보고서' in nm:
        # 일별 내역에서 총 취득수량/금액 합산
        rows = re.findall(r'보통주식\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)', doc_text)
        total_qty = 0
        total_amt = 0
        for row in rows:
            try:
                total_qty += int(row[1].replace(',', ''))  # 취득수량
                total_amt += int(row[3].replace(',', ''))  # 취득가액총액
            except ValueError:
                pass
        # 취득기간
        period_m = re.search(r'취득기간[^\d]*([\d]{4}년\s*[\d]{2}월\s*[\d]{2}일)\s*부터\s*([\d]{4}년\s*[\d]{2}월\s*[\d]{2}일)', doc_text)
        period_str = ''
        if period_m:
            period_str = f' {period_m.group(1).replace(" ","")}~{period_m.group(2).replace(" ","")} 동안'

        lines = []
        if total_qty and total_amt:
            lines.append(f'{corp} 자사주{period_str} {total_qty:,}주 · {fmt_kr(total_amt)} 취득 완료.')
            avg_price = total_amt // total_qty if total_qty else 0
            if avg_price:
                lines.append(f'평균 매입단가 {avg_price:,}원.')
        else:
            lines.append(f'{corp} 자사주 취득 결과 보고.')

        lines.append(f'계획 대비 실제 취득 수량과 금액을 비교하여 실행력을 평가할 수 있습니다.')
        return ' '.join(lines)

    # 자사주 처분결과보고서
    if '처분결과보고서' in nm:
        rows = re.findall(r'보통주식\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)', doc_text)
        total_qty = 0
        total_amt = 0
        for row in rows:
            try:
                total_qty += int(row[1].replace(',', ''))
                total_amt += int(row[3].replace(',', ''))
            except ValueError:
                pass
        lines = []
        if total_qty and total_amt:
            lines.append(f'{corp} 자사주 {total_qty:,}주 · {fmt_kr(total_amt)} 처분 완료.')
        else:
            lines.append(f'{corp} 자사주 처분 결과 보고.')
        lines.append(f'처분 방식과 수령자의 매도 가능성을 확인해야 합니다.')
        return ' '.join(lines)

    # 자사주 취득 결정
    if dt == 'treasury_acquire' or re.search(r'자기주식.*취득', nm):
        shares = existing_detail.get('shares')
        amount = existing_detail.get('amount')
        purpose = existing_detail.get('purpose', '')
        method = existing_detail.get('method', '')

        ratio = None
        if shares and total_shares and total_shares > 0:
            ratio = shares / total_shares * 100

        # PSU 관련 내용 추출
        psu_match = re.search(r'(PSU|성과연동|Performance Stock Unit)', doc_text)
        buyback_limit = re.search(r'자기주식 취득금액 한도[^\d]*([\d,]+)', doc_text)

        lines = []
        parts = []
        if shares:
            parts.append(f'{shares:,}주')
        if amount:
            parts.append(fmt_kr(amount))
        if ratio:
            parts.append(f'발행주식의 {ratio:.1f}%')
        lines.append(f'{corp} {" · ".join(parts)} 규모 자사주 매입 결정.')

        if '장내' in method:
            period_start = existing_detail.get('period_start', '')
            period_end = existing_detail.get('period_end', '')
            if period_start and period_end:
                lines.append(f'{period_start}~{period_end} 장내 직접 매수로, 해당 기간 지속적 매수세 유입.')
            else:
                lines.append(f'장내 직접 매수로 시장에 매수세 유입.')

        if psu_match and '임직원' in purpose:
            lines.append(f'목적이 성과연동 주식보상(PSU) 등 임직원 보상이므로 향후 직원 지급 시 매물 가능성 있어 단기 호재, 중기 중립.')
        elif '주주' in purpose or '소각' in purpose:
            lines.append(f'주주가치 제고 목적으로 소각 시 영구적 주당가치 상승. 강한 호재.')
        elif '임직원' in purpose:
            lines.append(f'임직원 보상 목적이므로 지급 후 매도 가능성 있어 단기 호재, 중기 중립.')

        return ' '.join(lines)

    # 자사주 처분 결정
    if dt == 'treasury_dispose' or re.search(r'자기주식.*처분', nm):
        shares = existing_detail.get('shares')
        amount = existing_detail.get('amount')
        purpose = existing_detail.get('purpose', '')

        lines = []
        parts = []
        if shares: parts.append(f'{shares:,}주')
        if amount: parts.append(fmt_kr(amount))
        lines.append(f'{corp} 자사주 {" · ".join(parts)} 처분.')

        if '임직원' in purpose or '성과급' in purpose:
            # 처분 방식 확인
            etc_match = re.search(r'기타\s*([\d,]+)', doc_text)
            lines.append(f'임직원 보상 목적 직접 교부로 시장 매도 아님. 주가 직접 영향 제한적.')
            lines.append(f'수령 직원의 즉시 매도 가능성은 있으나 물량이 제한적.')
        else:
            lines.append(f'시장 또는 장외 처분으로 유통 주식 증가. 매도 압력 발생 가능.')
            lines.append(f'처분 대금 용도를 확인하여 기업 전략 맥락에서 판단 필요.')

        return ' '.join(lines)

    # 유상증자
    if dt == 'capital_increase' or '유상증자' in nm:
        new_shares = existing_detail.get('new_shares')
        fund_total = existing_detail.get('fund_total')
        method = existing_detail.get('method', '')

        # 자금 용도 상세 추출
        fund_uses = []
        for label, pattern in [('시설투자', r'시설[^\d]*([\d,]+)'),
                                ('채무상환', r'채무상환[^\d]*([\d,]+)'),
                                ('운영자금', r'운영[^\d]*([\d,]+)'),
                                ('증권취득', r'증권취득[^\d]*([\d,]+)')]:
            m = re.search(pattern, doc_text)
            if m:
                val = int(m.group(1).replace(',', ''))
                if val > 0:
                    fund_uses.append(f'{label} {fmt_kr(val)}')

        lines = []
        parts = []
        if new_shares: parts.append(f'신주 {new_shares:,}주')
        if fund_total: parts.append(fmt_kr(fund_total))
        lines.append(f'{corp} {" · ".join(parts)} 규모 유상증자.')

        if fund_uses:
            lines.append(f'자금용도: {", ".join(fund_uses)}.')

        ratio = None
        bfic_match = re.search(r'증자전 발행주식총수[^\d]*([\d,]+)', doc_text)
        if new_shares and bfic_match:
            bfic = int(bfic_match.group(1).replace(',', ''))
            if bfic > 0:
                ratio = new_shares / bfic * 100
                lines.append(f'기존 주식 대비 {ratio:.1f}% 희석. {"주주배정이므로 기존 주주 참여 가능." if "주주배정" in method else "제3자 배정으로 기존 주주 참여 불가."}')

        if not ratio:
            lines.append(f'신주 발행으로 기존 주주 지분 희석. 증자 가격 할인율 확인 필요.')

        return ' '.join(lines)

    # 밸류업
    if '기업가치제고' in nm:
        lines = [f'{corp} 기업가치 제고(밸류업) 계획을 공시.']
        # 원문에서 주요 정책 추출
        policies = []
        if re.search(r'배당', doc_text): policies.append('배당 확대')
        if re.search(r'자사주|자기주식', doc_text): policies.append('자사주 매입')
        if re.search(r'ROE|자기자본이익률', doc_text): policies.append('ROE 개선')
        if re.search(r'주주환원', doc_text): policies.append('주주환원 강화')
        if policies:
            lines.append(f'주요 내용: {", ".join(policies)}.')
        lines.append(f'정부 밸류업 프로그램 참여로 기관투자자 관심 증가 기대.')
        return ' '.join(lines)

    # 잠정실적 / 매출변동
    if '잠정실적' in nm or '매출액또는손익' in nm:
        lines = [f'{corp} 실적 관련 공시.']
        # 원문에서 금액 추출
        revenue_m = re.search(r'매출액[^\d]{0,30}([\d,]{6,})', doc_text)
        op_m = re.search(r'영업이익[^\d]{0,30}([\d,]{6,})', doc_text)
        ni_m = re.search(r'당기순이익[^\d]{0,30}([\d,]{6,})', doc_text)
        nums = []
        if revenue_m: nums.append(f'매출 {fmt_kr(int(revenue_m.group(1).replace(",","")))}')
        if op_m: nums.append(f'영업이익 {fmt_kr(int(op_m.group(1).replace(",","")))}')
        if ni_m: nums.append(f'순이익 {fmt_kr(int(ni_m.group(1).replace(",","")))}')
        if nums:
            lines.append(f'주요 수치: {", ".join(nums)}.')
        # 증감률 추출
        change_m = re.search(r'(증가|감소|상승|하락)[^\d]{0,10}([\d.]+)%', doc_text)
        if change_m:
            lines.append(f'전년 대비 {change_m.group(2)}% {change_m.group(1)}.')
        lines.append(f'컨센서스 대비 서프라이즈/쇼크 여부를 확인해야 합니다.')
        return ' '.join(lines)

    # 배당
    if '배당' in nm:
        lines = [f'{corp} 배당 관련 공시.']
        div_m = re.search(r'주당.*?배당금[^\d]{0,15}([\d,]+)', doc_text)
        if div_m:
            lines.append(f'주당 배당금 {div_m.group(1)}원.')
        div_rate = re.search(r'배당수익률[^\d]{0,10}([\d.]+)', doc_text)
        if div_rate:
            lines.append(f'배당수익률 {div_rate.group(1)}%.')
        lines.append(f'배당 기준일과 전년 대비 증감을 확인하세요.')
        return ' '.join(lines)

    # 대량보유
    if '대량보유' in nm:
        lines = [f'{corp} 지분 5%+ 대량보유 변동 보고.']
        reporter_m = re.search(r'보고자[^\w]{0,10}(\S+)', doc_text)
        if reporter_m:
            lines.append(f'보고자: {reporter_m.group(1)}.')
        ratio_m = re.search(r'보유비율[^\d]{0,10}([\d.]+)', doc_text)
        if ratio_m:
            lines.append(f'보유비율 {ratio_m.group(1)}%.')
        purpose_m = re.search(r'보유목적[^\w]{0,10}(단순투자|경영참여|일반투자)', doc_text)
        if purpose_m:
            p = purpose_m.group(1)
            if p == '경영참여':
                lines.append(f'경영참여 목적으로 경영권 이슈 가능성.')
            else:
                lines.append(f'{p} 목적.')
        return ' '.join(lines)

    # 기타 — 원문에서 핵심 숫자 추출 (10억원 이상만)
    if doc_text and len(doc_text) > 100:
        nums = []
        for label, pattern in [('매출', r'매출액[^\d]{0,20}([\d,]{10,})'),
                                ('영업이익', r'영업이익[^\d]{0,20}([\d,]{10,})'),
                                ('총액', r'총\s*액[^\d]{0,10}([\d,]{10,})')]:
            m = re.search(pattern, doc_text)
            if m:
                try:
                    val = int(m.group(1).replace(',', ''))
                    if val >= 1_0000_0000:  # 1억원 이상만
                        nums.append(f'{label} {fmt_kr(val)}')
                except ValueError:
                    pass
        if nums:
            return f'{corp} 공시. 주요 수치: {", ".join(nums)}. DART 원문에서 상세 내용을 확인하세요.'

    return None


def fmt_kr(n):
    if n >= 1_0000_0000_0000: return f'{n / 1_0000_0000_0000:.1f}조원'
    if n >= 1_0000_0000: return f'{round(n / 1_0000_0000):,}억원'
    return f'{n:,}원'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stock', type=str, help='특정 종목만')
    parser.add_argument('--limit', type=int, default=0, help='최대 건수')
    parser.add_argument('--recent', type=int, default=0, help='최근 N일')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    dart_key = load_dart_key()

    with open(DISCLOSURES_PATH, encoding='utf-8') as f:
        data = json.load(f)

    # 대상: 주요 필터 (sentiment 있는 것)
    NOISE_RE = re.compile(r'최대주주등소유주식변동|기타경영사항\(자율공시\)|주주총회소집|정기주주총회결과')
    targets = [d for d in data['disclosures']
               if d.get('sentiment') in ('호재', '악재', '확인필요')
               and not NOISE_RE.search(d['report_nm'])]

    if args.stock:
        targets = [d for d in targets if d['stock_code'] == args.stock]

    if args.recent:
        cutoff = (datetime.now() - timedelta(days=args.recent)).strftime('%Y%m%d')
        targets = [d for d in targets if d['rcept_dt'] >= cutoff]

    if args.limit:
        targets = targets[:args.limit]

    print(f'대상: {len(targets)}건')
    if args.dry_run:
        return

    success = 0
    errors = 0
    for i, d in enumerate(targets):
        doc_text, err = fetch_document_text(dart_key, d['rcept_no'])
        if err:
            errors += 1
            if (i + 1) <= 5 or errors <= 3:
                print(f'  [{i+1}] WARN {d["corp_name"]}: {err[:80]}')
        elif doc_text:
            analysis = parse_and_analyze(d, doc_text)
            if analysis:
                d['ai_analysis'] = analysis
                success += 1

        if (i + 1) % 20 == 0:
            print(f'  [{i+1}/{len(targets)}] 성공 {success} / 에러 {errors}')
            # 중간 저장
            with open(DISCLOSURES_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        time.sleep(0.5)  # DART API 부하 방지

    # 저장
    data['meta']['doc_analysis_count'] = success
    data['meta']['doc_analysis_at'] = datetime.now().isoformat()
    with open(DISCLOSURES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'\n=== 결과 ===')
    print(f'원문 다운로드 성공: {len(targets) - errors}건')
    print(f'해석 생성: {success}건')
    print(f'에러: {errors}건')

    # 샘플
    print('\n=== 샘플 ===')
    cnt = 0
    for d in targets:
        if d.get('ai_analysis') and cnt < 5:
            print(f'\n[{d["corp_name"]}] {d["report_nm"]}')
            print(f'  {d["ai_analysis"]}')
            cnt += 1


if __name__ == '__main__':
    main()
