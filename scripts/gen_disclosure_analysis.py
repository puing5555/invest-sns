# -*- coding: utf-8 -*-
"""
공시 투자자 관점 해석 생성 (규칙 기반 템플릿) → disclosures.json에 merge
======================================================================
상세 데이터 있는 114건 대상, ai_analysis 필드 추가

사용법:
  python scripts/gen_disclosure_analysis.py
"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCLOSURES_PATH = PROJECT_ROOT / 'data' / 'disclosures.json'


def fmt_amount(n):
    if n is None: return None
    if n >= 1_0000_0000_0000: return f'{n / 1_0000_0000_0000:.1f}조원'
    if n >= 1_0000_0000: return f'{round(n / 1_0000_0000):,}억원'
    return f'{n:,}원'


def fmt_shares(n):
    if n is None: return None
    if n >= 1_0000_0000: return f'{n / 1_0000_0000:.1f}억주'
    if n >= 1_0000: return f'{round(n / 1_0000):,}만주'
    return f'{n:,}주'


def calc_period_months(start, end):
    """'2026.03.19' ~ '2026.06.18' -> ~3개월"""
    if not start or not end: return None
    try:
        s = datetime.strptime(start, '%Y.%m.%d')
        e = datetime.strptime(end, '%Y.%m.%d')
        days = (e - s).days
        if days <= 35: return '약 1개월'
        if days <= 65: return '약 2개월'
        if days <= 100: return '약 3개월'
        if days <= 190: return '약 6개월'
        return f'약 {days // 30}개월'
    except Exception:
        return None


def gen_treasury_acquire(d):
    detail = d['detail']
    corp = d['corp_name']
    shares = detail.get('shares')
    amount = detail.get('amount')
    purpose = detail.get('purpose', '')
    method = detail.get('method', '')
    period_start = detail.get('period_start')
    period_end = detail.get('period_end')
    period = calc_period_months(period_start, period_end)

    lines = []

    # 1문장: 핵심
    parts = []
    if shares: parts.append(fmt_shares(shares))
    if amount: parts.append(fmt_amount(amount))
    scale = ' · '.join(parts)
    lines.append(f'{corp}이(가) {scale} 규모의 자사주 매입을 결정했습니다.')

    # 2문장: 영향
    if '장내' in method and period:
        lines.append(f'{period}간 장내에서 직접 매수하므로 해당 기간 지속적인 매수세가 유입됩니다.')
    elif '장내' in method:
        lines.append(f'장내에서 직접 매수하므로 시장에 매수세가 유입되는 효과가 있습니다.')
    else:
        lines.append(f'자사주 매입은 유통 주식수를 줄여 주당 가치를 높이는 효과가 있습니다.')

    # 3문장: 주의
    if '임직원' in purpose or '보상' in purpose:
        lines.append(f'다만 목적이 \'{purpose}\'이므로 향후 직원에게 지급 시 매물로 나올 수 있어 단기 호재, 중기 중립으로 봐야 합니다.')
    elif '주주' in purpose or '소각' in purpose:
        lines.append(f'목적이 \'{purpose}\'로 주주환원 의지가 강하며, 소각 시 영구적인 주당 가치 상승 효과가 있습니다.')
    else:
        lines.append(f'취득 후 소각 여부에 따라 장기 영향이 달라지므로 후속 공시를 확인해야 합니다.')

    return ' '.join(lines)


def gen_treasury_dispose(d):
    detail = d['detail']
    corp = d['corp_name']
    shares = detail.get('shares')
    amount = detail.get('amount')
    purpose = detail.get('purpose', '')

    lines = []

    parts = []
    if shares: parts.append(fmt_shares(shares))
    if amount: parts.append(fmt_amount(amount))
    scale = ' · '.join(parts) if parts else '일정 규모'
    lines.append(f'{corp}이(가) 보유 자사주 {scale}를 처분합니다.')

    if '임직원' in purpose or '성과급' in purpose or '보상' in purpose:
        lines.append(f'임직원 보상 목적 처분으로, 시장 매도가 아니라 직원에게 직접 교부되므로 주가 영향은 제한적입니다.')
        lines.append(f'다만 수령자가 즉시 매도할 수 있어 단기적으로 소량의 매도 압력이 발생할 수 있습니다.')
    elif '시장' in purpose or '매도' in purpose:
        lines.append(f'시장 매도를 통한 처분이므로 단기적으로 매도 압력이 발생합니다.')
        lines.append(f'처분 금액의 용도(운영자금, 투자 등)에 따라 장기 영향이 달라집니다.')
    else:
        lines.append(f'자사주 처분은 유통 주식수 증가로 이어질 수 있으며, 처분 방식에 따라 영향이 다릅니다.')
        lines.append(f'처분 목적({purpose or "미상"})과 방식을 확인하여 실질적 매도 압력 여부를 판단해야 합니다.')

    return ' '.join(lines)


def gen_capital_increase(d):
    detail = d['detail']
    corp = d['corp_name']
    new_shares = detail.get('new_shares')
    fund_total = detail.get('fund_total')
    method = detail.get('method', '')

    lines = []

    parts = []
    if new_shares: parts.append(f'신주 {fmt_shares(new_shares)}')
    if fund_total: parts.append(fmt_amount(fund_total))
    scale = ' · '.join(parts) if parts else ''
    lines.append(f'{corp}이(가) {scale} 규모의 유상증자를 결정했습니다.')

    lines.append(f'신주 발행으로 기존 주주의 지분이 희석되며, 증자 방식({method or "미정"})에 따라 참여 기회가 결정됩니다.')

    if '주주배정' in method:
        lines.append(f'주주배정 방식이므로 기존 주주에게 신주 인수 우선권이 있으나, 참여하지 않으면 지분이 희석됩니다.')
    elif '제3자' in method:
        lines.append(f'제3자 배정 방식이므로 기존 주주 참여 기회 없이 지분이 희석됩니다. 배정 대상과 목적을 확인해야 합니다.')
    else:
        lines.append(f'자금 용도와 증자 가격(할인율)을 확인하여 기업 가치 대비 적정성을 판단해야 합니다.')

    return ' '.join(lines)


def main():
    with open(DISCLOSURES_PATH, encoding='utf-8') as f:
        data = json.load(f)

    targets = [d for d in data['disclosures'] if d.get('detail')]
    print(f'대상: {len(targets)}건')

    generated = 0
    for d in targets:
        dt = d['detail'].get('detail_type', '')
        try:
            if dt == 'treasury_acquire':
                d['ai_analysis'] = gen_treasury_acquire(d)
                generated += 1
            elif dt == 'treasury_dispose':
                d['ai_analysis'] = gen_treasury_dispose(d)
                generated += 1
            elif dt == 'capital_increase':
                d['ai_analysis'] = gen_capital_increase(d)
                generated += 1
        except Exception as e:
            print(f'  ERROR {d["corp_name"]}: {e}')

    data['meta']['ai_analysis_count'] = generated
    data['meta']['ai_analysis_at'] = datetime.now().isoformat()

    with open(DISCLOSURES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'생성: {generated}건')

    # 샘플
    print('\n=== 샘플 ===')
    cnt = 0
    for d in data['disclosures']:
        if d.get('ai_analysis') and cnt < 3:
            print(f'\n[{d["corp_name"]}] {d["report_nm"]}')
            print(f'  {d["ai_analysis"]}')
            cnt += 1


if __name__ == '__main__':
    main()
