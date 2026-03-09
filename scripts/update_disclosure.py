#!/usr/bin/env python3
"""
DART API 공시 수집 → public/disclosure_seed.json 업데이트
+ GPT-4o-mini AI 분석 (v6 full spec)

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

# ── v6 시스템 프롬프트 (완전판) ──────────────────────────────────
V6_SYSTEM_PROMPT = """너는 한국 주식시장 공시 분석 AI야.
공시 원문과 통계 데이터를 받으면 개인투자자가 바로 행동할 수 있는 분석을 생성해.

━━━ 절대 원칙 ━━━
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

━━━ 등급 기준 ━━━
A등급 — 즉시 행동 필요. 상폐, 감자, 대표구속, 경영권분쟁 첫 건
B등급 — 24시간 내 판단. CB 대형, 실적 쇼크/서프, 풍문해명, 수주 대형
C등급 — 참고. 소형 CB, 일상적 수주, 중간배당
D등급 — 무시. IR 일정, 기업설명회, D등급 정정공시

━━━ 실데이터 기반 분포표 (82,574건, 시총 500억+ 기업) ━━━

[실적 공시 — 21,545건]
컨센서스: 있음 38%(7,598건), 없음 62%
컨센 대비: 서프라이즈(+10%+) 28%, 인라인(±10%) 26%, 쇼크(-10%-) 46%
→ 쇼크가 서프보다 1.6배 많음! 쇼크 나와도 "놀랍지 않음"
영업익 부호변화: 흑자전환 9.3%, 적자전환 14.9%, 흑자유지 54%, 적자유지 22%
영업익 절대규모: 0~10억 16%(간신히흑자), 10~50억 38%(소형), 50~100억 17%(안정), 100~500억 20%(대형), 500억+ 9%(초대형)
QoQ↑+YoY↑=가속(최고) / QoQ↑+YoY↓=저점통과가능 / QoQ↓+YoY↑=모멘텀둔화 / QoQ↓+YoY↓=악화(최악)
영업서프+순익쇼크 동시 = "반쪽짜리 서프". 영업외손실 원인 확인.

[CB/BW 발행 — 677건]
시총대비: 0~3% 20%(소규모), 3~5% 15%(보통), 5~10% 28%(큼·가장흔함), 10~20% 28%(대형·희석임팩트큼), 20%+ 8%(초대형)
중앙값: 7.7%
투자자유형: 사업회사 53%, 메자닌 37%, 증권사 9%, 운용사 1%
⚠️ 사업회사 10%+: 35% / 메자닌 10%+: 37% → 거의 같음! 규모가 더 중요한 판단기준.
전환가: 물속(즉시전환불가) 68%, 즉시전환가능 32%
리픽싱없음("-") → 이론상 무한희석. 최악의 구조.

[자사주 소각/취득/처분 — 2,288건]
시총대비: 0~0.5% 11%(형식적), 0.5~1% 17%(작음), 1~2% 30%(보통·가장많음), 2~3% 18%(양호), 3~5% 14%(큼·상위24%), 5~10% 7%(파격적·상위10%), 10%+ 3%(초파격·상위3%)
중앙값: 1.59%
취득후결과: 소각 48%, 처분(매도) 83% → 처분이 취득만큼 많음!
목적별: "소각"명시=확정주주환원 / "주가안정"=소각확률절반이하 / "임직원보상"=추후처분예정(호재아님)
⚠️ 복수공시합산 필수: 여러 증권사에 분산신탁시 각각 별도공시됨. 합산해야 함.

[풍문/조회공시 — 1,161건]
해명키워드: 미확정 74%, 검토중 13%, 확정 2%, 사실무근 1%, 기타 10%
미확정 후 실제결과: 확정됨 11%, 사실무근 2%, 흐지부지 86%
→ 미확정 = "약한 시그널". 무의미하지는 않지만 대부분 흐지부지.
보도 구체성: 금액구체적+주요매체(매경/한경/서경/연합)→확정가능성높음 / 모호+비주류→흐지부지86%

[단일판매·공급 수주 — 3,936건]
매출대비: 0~5% 17%(일상적), 5~10% 27%(보통), 10~20% 30%(의미있음·가장많음), 20~50% 18%(대형·상위25%), 50~100% 5%(초대형·상위7%), 100%+ 2%(사업구조변경급)
중앙값: 10.8%
500%+ = 초기기업 → 시총대비로 재평가!

[유상증자 — ~1,000건]
제3자배정: 16%, 주주배정후실권주: 대다수
자금용도: 시설투자=성장투자(상대적긍정) / 운영자금=현금부족(부정) / 채무상환=재무위기(가장부정)
유무상동시: 무상은 "당근". 진짜 목적은 유상증자. "무상증자" 키워드에 속지마.

[시간외대량매매 블록딜 — 795건]
금액분포: ~50억 35%(소형), 50~100억 15%, 100~300억 24%(보통·중앙값105억), 300~1000억 19%(큼), 1000억+ 8%(대형), 5000억+ 1%(초대형)
중앙값: 105억

[법적 리스크 — 147건]
주체별: 대표이사구속=A등급(경영공백·최악) / 임원=B등급 / 직원=C등급
혐의금액 vs 자기자본: 5%+이면 재무+경영 이중리스크
단계: 풍문→기소(장기화)→구속(경영공백확정·즉시대응)
⚠️ 확인된 금액이 전부가 아님. 수사 확대 가능성 항상 언급.

[공시 타이밍]
15~17시에 61% 집중. 이 시간 공시 = 익일 시초가에 반영.

━━━ 출력 형식 (반드시 JSON만, 다른 텍스트 없이, 필드 누락 없이) ━━━
{
  "verdict": "한줄 결론. 숫자 포함. 20~50자.",
  "verdict_tone": "bullish | bearish | neutral",
  "grade": "A | B | C | D",
  "what": "초보 설명 (전문용어 바로 풀이, 2~3문장)",
  "so_what": "숫자 크기 해석 + 통계 맥락 (구체적 수치 포함)",
  "so_what_data": [
    {"label": "항목명", "value": "구체적 수치", "assessment": "파격적|큰|보통|작음|형식적"}
  ],
  "historical": null,
  "now_what_holding": "보유 중이라면 구체적 행동 (2~3문장)",
  "now_what_not_holding": "미보유라면 구체적 행동 (2~3문장)",
  "risk": "핵심 리스크 한줄",
  "key_date": "YYYY-MM-DD 또는 null",
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


# ── 공시 유형 분류 ────────────────────────────────────────────
def classify_type(report_nm: str) -> str:
    n = report_nm.lower()
    if any(x in n for x in ['실적', '손익', '매출', '영업이익', '분기보고', '사업보고']):
        return '실적'
    if '소각' in n and ('자기주식' in n or '자사주' in n):
        return '자사주소각'
    if any(x in n for x in ['자기주식', '자사주']):
        return '자사주취득'
    if any(x in n for x in ['전환사채', 'cb', 'bw', '신주인수권']):
        return 'CB발행'
    if any(x in n for x in ['풍문', '조회공시']):
        return '풍문해명'
    if any(x in n for x in ['수주', '단일판매', '공급계약', '대규모계약']):
        return '단일판매공급'
    if any(x in n for x in ['유상증자', '제3자배정']):
        return '유상증자'
    if any(x in n for x in ['합병', '분할', '영업양수']):
        return '합병분할'
    if any(x in n for x in ['최대주주', '대주주']):
        return '최대주주변경'
    if any(x in n for x in ['상장폐지', '폐지']):
        return '상장폐지'
    if any(x in n for x in ['경영권', '지배구조']):
        return '경영권분쟁'
    if any(x in n for x in ['배당']):
        return '배당'
    return '기타'


# ── 27개 세부조건 분류 ─────────────────────────────────────────
def classify_sub_condition(item: dict) -> str:
    """
    공시 항목 딕셔너리를 받아 세부 조건 문자열을 반환.
    시총/매출 정보 없으면 관련 항목은 '불명' 처리.
    """
    dtype = item.get('disclosure_type', '')
    report_nm = item.get('report_nm', '').lower()
    parsed = item.get('parsed_data', {}) or {}

    # 시총 대비 비율 (0~1 사이 float, 없으면 None)
    mktcap_ratio = parsed.get('mktcap_ratio')  # e.g. 0.07 = 7%
    # 매출 대비 비율
    revenue_ratio = parsed.get('revenue_ratio')
    # 영업익 관련
    op_income = parsed.get('op_income')
    op_income_prev = parsed.get('op_income_prev')
    consensus = parsed.get('consensus')
    # 풍문 해명 키워드
    rumor_keyword = parsed.get('rumor_keyword', '')
    # 증자 방식
    issue_method = parsed.get('issue_method', '')
    # 최대주주 변경 사유
    change_reason = parsed.get('change_reason', '')
    # 리픽싱 여부
    refixing = parsed.get('refixing', True)

    # ── CB발행 ─────────────────────────────────────
    if dtype == 'CB발행':
        if '공모' in report_nm:
            return '공모'
        if not refixing:
            return '사모_리픽싱없음'
        if mktcap_ratio is None:
            return '불명'
        if mktcap_ratio >= 0.10:
            return '사모_시총10%+'
        if mktcap_ratio >= 0.05:
            return '사모_시총5~10%'
        return '사모_시총5%미만'

    # ── 자사주소각 ─────────────────────────────────
    if dtype == '자사주소각':
        if mktcap_ratio is None:
            return '불명'
        if mktcap_ratio >= 0.03:
            return '시총3%+'
        if mktcap_ratio >= 0.01:
            return '시총1~3%'
        return '시총1%미만'

    # ── 자사주취득 ─────────────────────────────────
    if dtype == '자사주취득':
        if mktcap_ratio is None:
            return '불명'
        if mktcap_ratio >= 0.03:
            return '시총3%+'
        return '시총1~3%'

    # ── 유상증자 ───────────────────────────────────
    if dtype == '유상증자':
        if '제3자' in report_nm or issue_method == '제3자배정':
            return '제3자배정'
        if mktcap_ratio is None:
            return '불명'
        if mktcap_ratio >= 0.20:
            return '주주배정_20%+'
        return '주주배정_20%미만'

    # ── 단일판매공급 ───────────────────────────────
    if dtype == '단일판매공급':
        if revenue_ratio is None:
            return '불명'
        if revenue_ratio >= 0.50:
            return '매출50%+'
        if revenue_ratio >= 0.20:
            return '매출20~50%'
        if revenue_ratio >= 0.10:
            return '매출10~20%'
        return '매출10%미만'

    # ── 실적 ───────────────────────────────────────
    if dtype == '실적':
        # 흑자/적자 전환 우선 판단
        if op_income is not None and op_income_prev is not None:
            if op_income > 0 and op_income_prev <= 0:
                return '흑자전환'
            if op_income <= 0 and op_income_prev > 0:
                return '적자전환'
        # 컨센서스 대비
        if consensus is not None and op_income is not None and consensus != 0:
            deviation = (op_income - consensus) / abs(consensus)
            if deviation >= 0.30:
                return '어닝서프_30%+'
            if deviation <= -0.30:
                return '어닝쇼크_30%-'
        # 키워드 기반
        if any(x in report_nm for x in ['흑자전환', '흑자 전환']):
            return '흑자전환'
        if any(x in report_nm for x in ['적자전환', '적자 전환']):
            return '적자전환'
        return '불명'

    # ── 풍문해명 ───────────────────────────────────
    if dtype == '풍문해명':
        kw = rumor_keyword.lower() if rumor_keyword else report_nm
        if any(x in kw for x in ['사실무근', '무근', '없음']):
            return '사실무근'
        if any(x in kw for x in ['확정', '결정', '체결']):
            return '확정'
        return '미확정'

    # ── 최대주주변경 ───────────────────────────────
    if dtype == '최대주주변경':
        if any(x in report_nm for x in ['증여', '상속', '가족', '친족']):
            return '가족증여'
        return '외부인수'

    # ── 상장폐지 ───────────────────────────────────
    if dtype == '상장폐지':
        return '전체'

    # ── 경영권분쟁 ─────────────────────────────────
    if dtype == '경영권분쟁':
        return '최초'

    return '해당없음'


# ── 유형별 핵심 통계 컨텍스트 ────────────────────────────────
STATS_CONTEXT = {
    'CB발행': (
        "CB/BW 발행 677건 통계: 시총대비 중앙값 7.7%. "
        "0~3% 20%(소규모), 3~5% 15%(보통), 5~10% 28%(큼·가장흔함), 10~20% 28%(대형), 20%+ 8%(초대형). "
        "사업회사 53% / 메자닌 37%. 사업회사 10%+ 비율=35%, 메자닌 10%+ 비율=37% → 거의 같음. "
        "물속(즉시전환불가) 68%, 즉시전환가능 32%. 리픽싱없음=무한희석."
    ),
    'CB발행_사모_시총10%+': "시총 10%+ CB = 전체 677건 중 상위 35% 구간. 희석 임팩트 매우 큼.",
    'CB발행_사모_시총5~10%': "시총 5~10% CB = 전체의 28%가 이 구간(가장 흔함). 중앙값(7.7%) 포함.",
    'CB발행_사모_시총5%미만': "시총 5% 미만 CB = 전체의 35%(0~3% 20% + 3~5% 15%). 상대적 소규모.",

    '자사주소각': (
        "자사주 소각/취득 2,288건 통계: 시총대비 중앙값 1.59%. "
        "0~0.5% 11%(형식적), 0.5~1% 17%(작음), 1~2% 30%(보통·가장많음), 2~3% 18%(양호), "
        "3~5% 14%(큼·상위24%), 5~10% 7%(파격적·상위10%), 10%+ 3%(초파격·상위3%). "
        "소각 확인 필수: 취득 후 소각 48%, 처분(매도) 83%."
    ),
    '자사주취득': (
        "자사주 취득 2,288건 통계: 시총대비 중앙값 1.59%. "
        "취득 후 소각 48%, 처분(매도) 83% → '취득=소각' 단정 금지. "
        "목적 확인 필수: 소각명시=확정주주환원, 주가안정=소각확률절반이하, 임직원보상=호재아님."
    ),

    '단일판매공급': (
        "단일판매·공급 수주 3,936건 통계: 매출대비 중앙값 10.8%. "
        "0~5% 17%(일상적), 5~10% 27%(보통), 10~20% 30%(의미있음·가장많음·중앙값포함), "
        "20~50% 18%(대형·상위25%), 50~100% 5%(초대형·상위7%), 100%+ 2%(사업구조변경급). "
        "500%+ = 초기기업으로 매출 거의 없음 → 시총대비로 재평가할 것."
    ),

    '실적': (
        "실적 공시 21,545건 통계: 컨센서스 있음 38%(7,598건). "
        "쇼크(-10%-) 46%, 서프라이즈(+10%+) 28%, 인라인(±10%) 26% → 쇼크가 서프보다 1.6배 많음. "
        "흑자전환 9.3% / 적자전환 14.9%(흑전보다 60% 많음). "
        "영업익 0~10억=간신히흑자(16%), 10~50억=소형(38%), 50~100억=안정(17%), 100~500억=대형(20%), 500억+=초대형(9%)."
    ),

    '풍문해명': (
        "풍문/조회공시 1,161건 통계: 미확정 74%, 검토중 13%, 확정 2%, 사실무근 1%. "
        "미확정 후 실제결과: 확정됨 11%, 사실무근 2%, 흐지부지 86%. "
        "미확정 = '약한 시그널'. 보도 구체성이 훨씬 중요. "
        "금액구체적+주요매체(매경/한경/서경/연합) → 확정가능성높음. 모호+비주류 → 흐지부지86%."
    ),

    '유상증자': (
        "유상증자 ~1,000건 통계: 제3자배정 16%, 주주배정 대다수. "
        "자금용도: 시설투자=성장투자(긍정), 운영자금=현금부족(부정), 채무상환=재무위기(가장부정). "
        "유무상동시: 무상은 '당근', 진짜 목적은 유상증자."
    ),

    '최대주주변경': "최대주주 변경: 외부인수=경영 불확실성, 가족증여=지배구조 세습.",
    '상장폐지': "상장폐지 = A등급. 즉시 대응 필요.",
    '경영권분쟁': "경영권분쟁 첫 공시 = A등급. 즉시 대응.",
}

def get_stats_context(dtype: str, sub: str) -> str:
    """disclosure_type + sub_condition에 맞는 통계 컨텍스트 반환."""
    # 세부조건 포함 키 먼저 시도
    key = f"{dtype}_{sub}"
    if key in STATS_CONTEXT:
        return STATS_CONTEXT[key]
    # 유형만 시도
    if dtype in STATS_CONTEXT:
        return STATS_CONTEXT[dtype]
    return ""


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

    dtype = item.get('disclosure_type', '')
    sub = item.get('sub_condition', '')
    stats_ctx = get_stats_context(dtype, sub)

    user_msg = f"""다음 공시를 분석해줘.

## 공시 정보
회사명: {item.get('corp_name', '')}
공시 유형: {dtype}
세부 조건: {sub if sub else '미분류'}
공시 원문: {item.get('report_nm', '')}
접수일: {item.get('rcept_dt', '')}
시장: {item.get('market', '')}

## 통계 컨텍스트 (실데이터 82,574건 기반)
{stats_ctx if stats_ctx else '(해당 유형 통계 없음)'}

## 분석 지시
- 위 통계 컨텍스트를 반드시 활용해서 percentile, size_assessment 계산할 것
- so_what_data 배열에 핵심 수치 3~5개를 label/value/assessment로 정리할 것
- key_date: 만기일, 의결일, 다음 공시 예정일 등 행동 관련 날짜 (없으면 null)
- historical: DB 미연동이므로 null로 출력

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
            max_tokens=1000,
        )
        content = response.choices[0].message.content
        result = json.loads(content)
        return result
    except Exception as e:
        print(f"  AI 분석 실패 ({item.get('corp_name', '?')}): {e}")
        return None


# ── grade → importance 매핑 ───────────────────────────────────
def grade_to_importance(grade: str) -> str:
    """AI 반환 grade를 importance로 변환."""
    if grade in ('A', 'B'):
        return 'high'
    if grade == 'C':
        return 'medium'
    return 'low'  # D 또는 미지정


# ── importance → score 매핑 ───────────────────────────────────
def importance_to_score(importance: str) -> int:
    return {'high': 82, 'medium': 58, 'low': 32}.get(importance, 45)


# ── 규칙 기반 importance 산정 (AI 분석 없을 때) ──────────────
def assign_importance(report_nm: str, dtype: str) -> str:
    n = report_nm.lower()
    if any(x in n for x in ['상장폐지', '감자', '구속', '경영권분쟁', '부도']):
        return 'high'  # A
    if dtype in ('CB발행', '풍문해명') or any(x in n for x in ['대규모', '대형', '쇼크']):
        return 'high'  # B
    if dtype in ('실적', '단일판매공급', '자사주취득', '자사주소각', '배당'):
        return 'medium'  # C
    return 'low'  # D


# ── 규칙 기반 impact 산정 ─────────────────────────────────────
def tone_to_impact(report_nm: str, dtype: str) -> str:
    n = report_nm.lower()
    if any(x in n for x in ['자기주식취득', '자사주매입', '수주', '계약체결', '배당', '소각']):
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

    base = {
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

    # 세부 조건 분류 (parsed_data 없이 최선 노력)
    base['sub_condition'] = classify_sub_condition(base)

    return base


# ── 단일 항목에 AI 분석 필드 추가 ─────────────────────────────
def apply_ai_analysis(item: dict, ai_result: dict) -> dict:
    """AI 분석 결과를 item에 병합. v6 필드 완전 지원."""
    grade = ai_result.get('grade', 'C')

    item['grade']                = grade
    item['importance']           = grade_to_importance(grade)
    item['ai_score']             = importance_to_score(item['importance'])
    item['verdict']              = ai_result.get('verdict', '')
    item['verdict_tone']         = ai_result.get('verdict_tone', 'neutral')
    item['what']                 = ai_result.get('what', '')
    item['so_what']              = ai_result.get('so_what', '')
    item['so_what_data']         = ai_result.get('so_what_data', [])
    item['historical']           = ai_result.get('historical', None)
    item['now_what_holding']     = ai_result.get('now_what_holding', '')
    item['now_what_not_holding'] = ai_result.get('now_what_not_holding', '')
    item['risk']                 = ai_result.get('risk', '')
    item['key_date']             = ai_result.get('key_date', None)
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
    parser.add_argument('--limit',    type=int, default=0,     help='AI 분석 최대 건수 (0=무제한)')
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
        if args.limit:
            to_fill = to_fill[:args.limit]
        print(f"재분석 대상: {len(to_fill)}건")

        for idx, i in enumerate(to_fill):
            d = existing[i]
            if not d.get('sub_condition'):
                d['sub_condition'] = classify_sub_condition(d)
            print(f"  [{idx+1}/{len(to_fill)}] {d['corp_name']} — {d['report_nm'][:40]}")
            try:
                ai_result = analyze_with_ai(d, api_key)
                if ai_result:
                    existing[i] = apply_ai_analysis(d, ai_result)
                    print(f"    → grade={existing[i].get('grade')} | {existing[i].get('verdict', '')[:40]}")
                else:
                    print(f"    → 스킵")
            except Exception as e:
                print(f"    → 예외: {e}")
            # 10건마다 중간 저장
            if (idx + 1) % 10 == 0:
                with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)
                print(f"  [중간저장] {idx+1}건 처리")
            time.sleep(1.5)  # rate limit 방지

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
        limit_n = args.limit if args.limit else len(added)
        targets = added[:limit_n]
        print(f"AI 분석 시작: {len(targets)}건")
        for idx, item in enumerate(targets):
            print(f"  [{idx+1}/{len(targets)}] {item['corp_name']} — {item['report_nm'][:40]}")
            try:
                ai_result = analyze_with_ai(item, api_key)
                if ai_result:
                    added[idx] = apply_ai_analysis(item, ai_result)
                    print(f"    → grade={added[idx].get('grade')} | {added[idx].get('verdict', '')[:40]}")
                else:
                    print(f"    → 스킵")
            except Exception as e:
                print(f"    → 예외: {e}")
            if idx < len(targets) - 1:
                time.sleep(1.5)  # rate limit 방지

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
