#!/usr/bin/env python3
"""
DART API 공시 수집 → public/disclosure_seed.json 업데이트
+ GPT-4o-mini AI 분석 (v6)

사용법:
  python scripts/update_disclosure.py              # 오늘 공시 + AI 분석
  python scripts/update_disclosure.py --days 7    # 최근 7일
  python scripts/update_disclosure.py --start 20260301 --end 20260309  # 기간 지정
  python scripts/update_disclosure.py --no-ai     # AI 분석 없이 수집만
  python scripts/update_disclosure.py --backfill  # 기존 데이터 AI 재분석
"""
import sys, os, json, time, ssl, urllib.request, argparse
from datetime import datetime, timedelta
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
OUTPUT_PATH  = os.path.join(PROJECT_ROOT, 'public', 'disclosure_seed.json')

DART_API_KEY = "b6ea29c886e5d9009155a3360d3dc8a8932a523b"
DART_BASE_URL = "https://opendart.fss.or.kr/api"

# ── v6 시스템 프롬프트 ─────────────────────────────────────────
V6_SYSTEM_PROMPT = """너는 한국 주식시장 공시 분석 AI야.
공시 원문과 통계 데이터를 받으면 개인투자자가 바로 행동할 수 있는 분석을 생성해.

절대 원칙:
1. 숫자에 분포 위치를 붙여라. "시총 3%"만 쓰지 말고 "시총 3%, 전체 중 상위 35%"
2. 과장 금지. 작으면 작다고. 형식적이면 형식적이라고. 무시할 거면 "무시"
3. "확인 필요", "주시", "모니터링" 절대 금지. 뭘 봐야 하는지 구체적으로.
4. "자사주 취득 = 소각"으로 단정 금지. 소각 확률 48%. 처분도 비슷하게 많음.
5. CB "사업회사 = 무조건 덜 악재" 금지. 규모가 더 중요.
6. "미확정 = 무의미" 금지. 11%는 실제 확정됨. "약한 시그널"이 정확.
7. 데이터 편향 인지. 시총 500억+ 기준. 소형주와 다를 수 있음.
8. 데이터 없으면 솔직히. 뻥치지 마.
9. 영업익 0~10억 = "간신히 흑자". "흑자전환"에 현혹 금지.
10. 15~17시 공시 = 익일 시초가 반영. 장중 공시와 구분.

등급 기준:
  A등급 — 즉시 행동 필요. 상폐, 감자, 대표구속, 경영권분쟁 첫 건
  B등급 — 24시간 내 판단. CB 대형, 실적 쇼크/서프, 풍문해명, 수주 대형
  C등급 — 참고. 소형 CB, 일상적 수주, 중간배당
  D등급 — 무시. IR 일정, 기업설명회, 정정공시

유형별 핵심 분포 (82,574건 실데이터):
[실적] 쇼크 46%/서프 28%/인라인 26%. 쇼크가 서프보다 1.6배 많음.
  흑자전환 9.3%, 적자전환 14.9%. 영업익 0~10억=간신히 흑자.
[CB/BW] 시총대비 중앙값 7.7%. 10%+ 대형=35%. 메자닌 37%=전환 후 매도가 비즈니스모델.
  물속(전환불가) 68%. 사업회사 vs 메자닌 규모 차이 없음.
[자사주] 시총대비 중앙값 1.59%. 취득 후 소각 48%, 처분 83%. "취득=소각" 금지.
[풍문] 미확정 74%. 미확정 후 실제 확정 11%. 약한 시그널.
[수주] 매출대비 중앙값 10.8%. 20%+이면 대형(상위 25%).
[유상증자] 운영자금=현금부족/채무상환=재무위기/시설투자=성장투자.

출력: 반드시 JSON만. 다른 텍스트 없이. 필드 누락 없이.
{
  "verdict": "한줄 결론. 숫자 포함. 20~50자.",
  "verdict_tone": "bullish | bearish | neutral",
  "grade": "A | B | C | D",
  "what": "초보 설명 (전문용어 바로 풀이, 2~3문장)",
  "so_what": "숫자 크기 해석 + 통계 맥락 (구체적 수치 포함)",
  "now_what_holding": "보유 중이라면 구체적 행동 (2~3문장)",
  "now_what_not_holding": "미보유라면 구체적 행동 (2~3문장)",
  "risk": "핵심 리스크 한줄",
  "size_assessment": "파격적|큼|보통|작음|형식적|해당없음",
  "percentile": "전체 N건 중 상위/하위 X%",
  "tags": ["태그1", "태그2", "태그3"]
}"""


# ── OpenAI API 키 로드 ────────────────────────────────────────
def load_openai_key() -> str | None:
    env_path = os.path.join(PROJECT_ROOT, '.env.local')
    if os.path.exists(env_path):
        try:
            for line in open(env_path, encoding='utf-8'):
                line = line.strip()
                if line.startswith('OPENAI_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    if key:
                        return key
        except Exception:
            pass
    return os.environ.get('OPENAI_API_KEY')


# ── GPT-4o-mini AI 분석 ───────────────────────────────────────
def analyze_with_ai(item: dict, api_key: str) -> dict | None:
    """GPT-4o-mini로 공시 분석. 실패 시 None 반환."""
    try:
        import openai
    except ImportError:
        print("  openai 패키지 없음. pip install openai 실행 중...")
        os.system(f"{sys.executable} -m pip install openai -q")
        try:
            import openai
        except ImportError:
            print("  openai 설치 실패. AI 분석 스킵.")
            return None

    user_msg = f"""다음 공시를 분석해줘.
회사명: {item.get('corp_name', '')}
공시 유형: {item.get('disclosure_type', '')}
공시 원문: {item.get('report_nm', '')}
접수일: {item.get('rcept_dt', '')}
시장: {item.get('market', '')}

JSON 형식으로만 응답. 다른 텍스트 없이."""

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": V6_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=800,
        )
        content = response.choices[0].message.content
        result = json.loads(content)
        return result
    except Exception as e:
        print(f"  AI 분석 실패 ({item.get('corp_name', '?')}): {e}")
        return None


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


# ── 단일 항목에 AI 분석 필드 추가 ─────────────────────────────
def apply_ai_analysis(item: dict, ai_result: dict) -> dict:
    """AI 분석 결과를 item에 병합."""
    item['grade']                = ai_result.get('grade', 'C')
    item['verdict']              = ai_result.get('verdict', '')
    item['verdict_tone']         = ai_result.get('verdict_tone', 'neutral')
    item['what']                 = ai_result.get('what', '')
    item['so_what']              = ai_result.get('so_what', '')
    item['now_what_holding']     = ai_result.get('now_what_holding', '')
    item['now_what_not_holding'] = ai_result.get('now_what_not_holding', '')
    item['risk']                 = ai_result.get('risk', '')
    item['size_assessment']      = ai_result.get('size_assessment', '해당없음')
    item['percentile']           = ai_result.get('percentile', '')
    item['tags']                 = ai_result.get('tags', [])
    return item


# ── needs_ai: verdict 없는 건 판별 ───────────────────────────
def needs_ai(item: dict) -> bool:
    return not item.get('verdict')


# ── 메인 ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days',     type=int, default=1,     help='최근 N일 (기본 1)')
    parser.add_argument('--start',    default=None,            help='시작일 YYYYMMDD')
    parser.add_argument('--end',      default=None,            help='종료일 YYYYMMDD')
    parser.add_argument('--no-ai',    action='store_true',     help='AI 분석 없이 수집만')
    parser.add_argument('--backfill', action='store_true',     help='기존 verdict 없는 건 재분석')
    args = parser.parse_args()

    # ── OpenAI 키 로드 ──
    api_key = None
    if not args.no_ai:
        api_key = load_openai_key()
        if api_key:
            print(f"OpenAI API 키 로드 완료 (키 앞 8자: {api_key[:8]}...)")
        else:
            print("OpenAI API 키 없음. AI 분석 스킵.")

    # ── 기존 데이터 로드 ──
    existing = []
    if os.path.exists(OUTPUT_PATH):
        try:
            existing = json.load(open(OUTPUT_PATH, encoding='utf-8'))
        except Exception:
            existing = []

    # ── 백필 모드 ──
    if args.backfill:
        print(f"백필 모드: 기존 {len(existing)}건 중 verdict 없는 건 재분석")
        if not api_key:
            print("API 키 없어 백필 불가.")
            return

        to_fill = [i for i, d in enumerate(existing) if needs_ai(d)]
        print(f"재분석 대상: {len(to_fill)}건")

        for idx, i in enumerate(to_fill):
            d = existing[i]
            print(f"  [{idx+1}/{len(to_fill)}] {d['corp_name']} — {d['report_nm'][:40]}")
            ai_result = analyze_with_ai(d, api_key)
            if ai_result:
                existing[i] = apply_ai_analysis(d, ai_result)
                print(f"    → grade={existing[i].get('grade')} | {existing[i].get('verdict', '')[:40]}")
            else:
                print(f"    → 스킵")
            time.sleep(1)  # rate limit 방지

        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        filled = sum(1 for d in existing if 'verdict' in d and d['verdict'])
        print(f"백필 완료: {OUTPUT_PATH} ({filled}건 AI 분석 포함)")
        return

    # ── 수집 모드 ──
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

    # 중복 제거
    existing_ids = {d.get('rcept_no') or d.get('id') for d in existing}
    added = [d for d in new_items if d['rcept_no'] not in existing_ids]
    print(f"신규 추가: {len(added)}건 (중복 제외)")

    # ── 신규 항목 AI 분석 ──
    if api_key and added:
        print(f"AI 분석 시작: {len(added)}건")
        for idx, item in enumerate(added):
            print(f"  [{idx+1}/{len(added)}] {item['corp_name']} — {item['report_nm'][:40]}")
            ai_result = analyze_with_ai(item, api_key)
            if ai_result:
                added[idx] = apply_ai_analysis(item, ai_result)
                print(f"    → grade={added[idx].get('grade')} | {added[idx].get('verdict', '')[:40]}")
            else:
                print(f"    → 스킵")
            if idx < len(added) - 1:
                time.sleep(1)  # rate limit 방지

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
