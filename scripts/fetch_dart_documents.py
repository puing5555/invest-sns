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
            avg_price = total_amt // total_qty if total_qty else 0
            lines.append(f'{corp}가 자사주(회사가 자기 주식을 사는 것){period_str} {total_qty:,}주를 총 {fmt_kr(total_amt)}에 매입 완료했습니다.')
            if avg_price:
                lines.append(f'평균 {avg_price:,}원에 샀습니다.')
            lines.append(f'내 주식에 미치는 영향: 회사가 약속대로 자사주를 매입해 시장의 신뢰가 유지됩니다.')
        else:
            lines.append(f'{corp}가 자사주 매입을 완료했다는 결과 보고입니다.')
            lines.append(f'내 주식에 미치는 영향: 매입 완료 자체는 이미 반영된 호재이므로 추가 영향은 제한적입니다.')
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
            lines.append(f'{corp}가 보유하던 자사주 {total_qty:,}주({fmt_kr(total_amt)} 규모)를 처분(매도 또는 직원에게 지급) 완료했습니다.')
        else:
            lines.append(f'{corp}가 자사주 처분을 완료했다는 결과 보고입니다.')
        lines.append(f'내 주식에 미치는 영향: 직원 보상용이면 영향 적고, 시장 매도면 단기 매물 부담이 있을 수 있습니다.')
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
        if shares: parts.append(f'{shares:,}주')
        if amount: parts.append(fmt_kr(amount))
        if ratio: parts.append(f'전체 주식의 {ratio:.1f}%')
        lines.append(f'{corp}가 자사주(자기 회사 주식) {" · ".join(parts)} 규모를 사기로 결정했습니다.')

        if '장내' in method:
            period_start = existing_detail.get('period_start', '')
            period_end = existing_detail.get('period_end', '')
            if period_start and period_end:
                lines.append(f'{period_start}~{period_end} 동안 주식시장에서 직접 매수하므로, 이 기간 동안 주가를 받쳐주는 매수세(사는 힘)가 생깁니다.')

        if psu_match and '임직원' in purpose:
            lines.append(f'내 주식에 미치는 영향: 매입 기간엔 호재지만, 나중에 직원들에게 지급되면 그 직원들이 팔 수 있어서 단기 호재·중기 중립입니다.')
        elif '주주' in purpose or '소각' in purpose:
            lines.append(f'내 주식에 미치는 영향: 주주환원 목적이라 소각(없애기)하면 내 지분 가치가 올라갑니다. 강한 호재.')
        elif '임직원' in purpose:
            lines.append(f'내 주식에 미치는 영향: 매입 기간엔 호재지만, 직원 보상용이라 나중에 매물이 나올 수 있어 단기 호재·중기 중립입니다.')
        else:
            lines.append(f'내 주식에 미치는 영향: 회사가 자기 주식을 사면 시장에 유통되는 주식이 줄어 주가에 긍정적입니다.')

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
        lines.append(f'{corp}가 보유 중인 자사주 {" · ".join(parts)}를 처분(내보내기)하기로 했습니다.')

        if '임직원' in purpose or '성과급' in purpose:
            lines.append(f'직원 보상용으로 직접 지급하는 것이라 주식시장에서 파는 게 아닙니다.')
            lines.append(f'내 주식에 미치는 영향: 시장 매도가 아니라 직접 영향은 적지만, 받은 직원이 바로 팔 수도 있어 소량 매물 가능성.')
        else:
            lines.append(f'내 주식에 미치는 영향: 시장에 매물(팔려는 주식)이 나와 단기적으로 주가 하락 압력이 생길 수 있습니다.')

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
        if new_shares: parts.append(f'새 주식 {new_shares:,}주')
        if fund_total: parts.append(fmt_kr(fund_total))
        lines.append(f'{corp}가 유상증자(돈을 받고 새 주식을 발행)를 결정했습니다. 규모: {" · ".join(parts)}.')

        if fund_uses:
            lines.append(f'모은 돈의 용도: {", ".join(fund_uses)}.')

        ratio = None
        bfic_match = re.search(r'증자전 발행주식총수[^\d]*([\d,]+)', doc_text)
        if new_shares and bfic_match:
            bfic = int(bfic_match.group(1).replace(',', ''))
            if bfic > 0:
                ratio = new_shares / bfic * 100

        if ratio and '주주배정' in method:
            lines.append(f'내 주식에 미치는 영향: 내 지분이 {ratio:.1f}% 희석(가치 하락)되지만, 기존 주주에게 우선 참여 기회가 있어 참여하면 방어 가능.')
        elif ratio:
            lines.append(f'내 주식에 미치는 영향: 내 지분이 {ratio:.1f}% 희석됩니다. 새 주식이 나오면 기존 주식 가치가 줄어들어 보통 악재입니다.')
        else:
            lines.append(f'내 주식에 미치는 영향: 새 주식이 발행되면 내 지분 비율이 줄어듭니다(희석). 보통 단기 악재.')

        return ' '.join(lines)

    # 밸류업
    if '기업가치제고' in nm:
        lines = [f'{corp}가 밸류업(기업가치를 높이겠다는) 계획을 발표했습니다.']
        policies = []
        if re.search(r'배당', doc_text): policies.append('배당(주주에게 돈 나눠주기) 확대')
        if re.search(r'자사주|자기주식', doc_text): policies.append('자사주 매입')
        if re.search(r'ROE|자기자본이익률', doc_text): policies.append('수익성 개선')
        if re.search(r'주주환원', doc_text): policies.append('주주환원 강화')
        if policies:
            lines.append(f'구체적으로: {", ".join(policies)}을 약속했습니다.')
        lines.append(f'내 주식에 미치는 영향: 주주에게 더 많이 돌려주겠다는 신호라 보통 호재입니다.')
        return ' '.join(lines)

    # 잠정실적 / 매출변동
    if '잠정실적' in nm or '매출액또는손익' in nm:
        lines = [f'{corp}가 실적(회사가 얼마나 벌었는지)을 공시했습니다.']
        revenue_m = re.search(r'매출액[^\d]{0,30}([\d,]{6,})', doc_text)
        op_m = re.search(r'영업이익[^\d]{0,30}([\d,]{6,})', doc_text)
        ni_m = re.search(r'당기순이익[^\d]{0,30}([\d,]{6,})', doc_text)
        nums = []
        if revenue_m: nums.append(f'매출(총 판매액) {fmt_kr(int(revenue_m.group(1).replace(",","")))}')
        if op_m: nums.append(f'영업이익(본업으로 번 돈) {fmt_kr(int(op_m.group(1).replace(",","")))}')
        if ni_m: nums.append(f'순이익(최종 이익) {fmt_kr(int(ni_m.group(1).replace(",","")))}')
        if nums:
            lines.append(f'{", ".join(nums)}.')
        change_m = re.search(r'(증가|감소|상승|하락)[^\d]{0,10}([\d.]+)%', doc_text)
        if change_m:
            lines.append(f'전년 대비 {change_m.group(2)}% {change_m.group(1)}했습니다.')
        lines.append(f'내 주식에 미치는 영향: 시장 예상보다 좋으면 주가 상승, 나쁘면 하락합니다. 증권사 예상치와 비교해 보세요.')
        return ' '.join(lines)

    # 배당
    if '배당' in nm:
        lines = [f'{corp}가 배당(주식 보유자에게 돈을 나눠주는 것)을 결정했습니다.']
        div_m = re.search(r'주당.*?배당금[^\d]{0,15}([\d,]+)', doc_text)
        if div_m:
            lines.append(f'1주당 {div_m.group(1)}원을 받을 수 있습니다.')
        div_rate = re.search(r'배당수익률[^\d]{0,10}([\d.]+)', doc_text)
        if div_rate:
            lines.append(f'배당수익률(투자 대비 받는 비율) {div_rate.group(1)}%입니다.')
        lines.append(f'내 주식에 미치는 영향: 배당 기준일에 주식을 보유하고 있어야 받을 수 있고, 배당 후 주가는 배당금만큼 떨어지는 게 일반적입니다.')
        return ' '.join(lines)

    # 대량보유
    if '대량보유' in nm:
        lines = [f'{corp} 주식을 5% 이상 대량 보유한 사람/기관의 변동 보고입니다.']
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
                lines.append(f'내 주식에 미치는 영향: 경영참여 목적이라 경영권 다툼이 생길 수 있어 주가 변동성이 커질 수 있습니다.')
            else:
                lines.append(f'내 주식에 미치는 영향: 단순투자 목적이라 당장 큰 영향은 없지만, 대주주가 많이 사면 주가에 긍정적 신호입니다.')
        else:
            lines.append(f'내 주식에 미치는 영향: 누가 왜 많이 샀는지(또는 팔았는지)에 따라 달라집니다.')
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
            return f'{corp} 공시입니다. 주요 수치: {", ".join(nums)}. 자세한 내용은 DART 원문을 확인하세요.'

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
