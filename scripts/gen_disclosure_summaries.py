# -*- coding: utf-8 -*-
"""
공시 AI 한줄요약 생성 + 규칙 기반 sentiment
============================================
1) 상세 데이터 있는 114건 → Claude Haiku 한줄요약
2) 나머지 → 규칙 기반 sentiment 매핑

사용법:
  python scripts/gen_disclosure_summaries.py
  python scripts/gen_disclosure_summaries.py --dry-run
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / '.env.local'
DISCLOSURES_PATH = PROJECT_ROOT / 'data' / 'disclosures.json'


def load_env():
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())


# ── 규칙 기반 sentiment ──

SENTIMENT_RULES = [
    # (키워드, sentiment, 기본 요약 템플릿)
    # 호재
    ('자기주식취득결정', '호재', '{corp} 자사주 매입 결정 — 주주환원·주가부양 신호'),
    ('자기주식취득결과', '호재', '{corp} 자사주 매입 완료'),
    ('기업가치제고', '호재', '{corp} 기업가치 제고(밸류업) 계획 공시'),
    ('배당', '호재', '{corp} 배당 관련 공시'),
    # 악재
    ('유상증자결정', '악재', '{corp} 유상증자 결정 — 주식 희석 가능성'),
    ('전환사채', '악재', '{corp} CB 발행 — 전환 시 주식 희석'),
    ('신주인수권부사채', '악재', '{corp} BW 발행 — 행사 시 주식 희석'),
    ('감자', '악재', '{corp} 감자 결정'),
    # 확인필요
    ('자기주식처분결정', '중립', '{corp} 자사주 처분 결정 — 용도에 따라 해석 상이'),
    ('자기주식처분결과', '중립', '{corp} 자사주 처분 완료'),
    ('매출액또는손익구조', '확인필요', '{corp} 매출/손익 30%+ 변경 — 실적 확인 필요'),
    ('잠정실적', '확인필요', '{corp} 잠정실적 공시 — 내용 확인 필요'),
    ('합병', '확인필요', '{corp} 합병 관련 공시'),
    ('분할', '확인필요', '{corp} 분할 관련 공시'),
    ('대량보유', '중립', '{corp} 지분 5%+ 대량보유 변동'),
    ('최대주주', '중립', '{corp} 최대주주 변동'),
    ('소유주식변동', '중립', '{corp} 주요주주 지분 변동'),
    ('주주총회', '중립', '{corp} 주주총회 관련'),
    ('감사보고서', '중립', '{corp} 감사보고서 제출'),
    ('공정공시', '중립', '{corp} 공정공시'),
    ('증권신고', '악재', '{corp} 증권 발행 신고'),
]


def rule_based_sentiment(report_nm, corp_name):
    """규칙 기반 sentiment + 기본 요약"""
    for keyword, sentiment, template in SENTIMENT_RULES:
        if keyword in report_nm:
            summary = template.format(corp=corp_name)
            return sentiment, summary
    return '중립', None


def call_haiku_batch(items, api_key):
    """Claude Haiku로 한줄요약 생성 (배치)"""
    import urllib.request
    import ssl

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    results = {}

    for i, item in enumerate(items):
        rcept_no = item['rcept_no']
        corp = item['corp_name']
        report_nm = item['report_nm']
        detail_summary = item.get('detail_summary', '')

        prompt = f"""공시 정보를 개인투자자가 이해하기 쉬운 한줄요약으로 작성해.

종목: {corp}
공시: {report_nm}
상세: {detail_summary}

JSON으로 답변:
{{"summary": "쉬운 한줄 요약 (50자 이내)", "sentiment": "호재/악재/중립/확인필요"}}

규칙:
- 자사주 취득(매입) = 호재 (주가부양, 주주환원)
- 자사주 처분: 임직원 보상이면 중립, 시장 매도면 악재
- 유상증자 = 악재 (희석)
- CB/BW 발행 = 악재 (희석 가능성)
- 금액은 억/조 단위로"""

        body = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=body,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            }
        )

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
                resp = json.loads(r.read().decode('utf-8'))

            text = resp['content'][0]['text'].strip()
            # JSON 파싱
            if '{' in text:
                json_str = text[text.index('{'):text.rindex('}') + 1]
                parsed = json.loads(json_str)
                results[rcept_no] = {
                    'ai_summary': parsed.get('summary', ''),
                    'sentiment': parsed.get('sentiment', '중립'),
                }
            else:
                results[rcept_no] = {'ai_summary': text[:80], 'sentiment': '중립'}

        except Exception as e:
            print(f'  [{i+1}] ERROR {corp}: {e}')
            results[rcept_no] = {'ai_summary': '', 'sentiment': '중립'}

        if (i + 1) % 10 == 0:
            print(f'  [{i+1}/{len(items)}] 완료')

        time.sleep(0.5)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    load_env()
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')

    with open(DISCLOSURES_PATH, encoding='utf-8') as f:
        data = json.load(f)

    disclosures = data['disclosures']

    # 1) 상세 데이터 있는 건 분리
    detailed = [d for d in disclosures if d.get('detail_summary')]
    rest = [d for d in disclosures if not d.get('detail_summary')]

    print(f'전체: {len(disclosures)}건')
    print(f'상세 있음 (Haiku): {len(detailed)}건')
    print(f'상세 없음 (규칙): {len(rest)}건')

    if args.dry_run:
        # 규칙 기반 커버율 확인
        covered = 0
        for d in rest:
            s, _ = rule_based_sentiment(d['report_nm'], d['corp_name'])
            if s != '중립' or _ is not None:
                covered += 1
        print(f'\n규칙 기반 커버: {covered}/{len(rest)}건')
        return

    # 2) Haiku 요약 생성
    if not api_key:
        print('[ERROR] ANTHROPIC_API_KEY not found')
        sys.exit(1)

    print(f'\n[1/2] Haiku 한줄요약 생성 ({len(detailed)}건)...')
    haiku_results = call_haiku_batch(detailed, api_key)

    # merge Haiku 결과
    haiku_merged = 0
    for d in disclosures:
        rn = d.get('rcept_no', '')
        if rn in haiku_results:
            d['ai_summary'] = haiku_results[rn].get('ai_summary', '')
            d['sentiment'] = haiku_results[rn].get('sentiment', '중립')
            haiku_merged += 1

    print(f'  Haiku merge: {haiku_merged}건')

    # 3) 규칙 기반 sentiment (나머지)
    print(f'\n[2/2] 규칙 기반 sentiment ({len(rest)}건)...')
    rule_count = 0
    for d in disclosures:
        if d.get('ai_summary'):
            continue  # Haiku 결과 있으면 스킵
        sentiment, rule_summary = rule_based_sentiment(d['report_nm'], d['corp_name'])
        d['sentiment'] = sentiment
        if rule_summary:
            d['ai_summary'] = rule_summary
            rule_count += 1

    print(f'  규칙 매칭: {rule_count}건')

    # 저장
    data['meta']['ai_summary_count'] = haiku_merged + rule_count
    data['meta']['ai_summary_at'] = __import__('datetime').datetime.now().isoformat()

    with open(DISCLOSURES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 통계
    sentiments = {}
    for d in disclosures:
        s = d.get('sentiment', '')
        if s:
            sentiments[s] = sentiments.get(s, 0) + 1

    print(f'\n=== 결과 ===')
    print(f'Haiku 요약: {haiku_merged}건')
    print(f'규칙 요약: {rule_count}건')
    print(f'sentiment 없음: {len(disclosures) - sum(sentiments.values())}건')
    print(f'\nsentiment 분포:')
    for s, c in sorted(sentiments.items(), key=lambda x: -x[1]):
        print(f'  {s}: {c}건')

    # 샘플
    print('\n=== Haiku 샘플 ===')
    cnt = 0
    for d in disclosures:
        if d.get('ai_summary') and d.get('detail_summary') and cnt < 5:
            print(f"  [{d['sentiment']}] {d['corp_name']}: {d['ai_summary']}")
            cnt += 1


if __name__ == '__main__':
    main()
