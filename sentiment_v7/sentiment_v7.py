"""
한국 시장 심리지수 v7
6개 지표 기반 공포/탐욕 지수 (2026-03-07 기준)

작동 지표 (6개):
  1. 모멘텀        - 코스피 vs 50일 이평 (yfinance)
  5. 변동성        - KOSPI 실현변동성 vs 50일 이평 (VKOSPI 대체)
  6. 안전자산      - 코스피 vs 국채ETF 60일 수익률 차이
  7. 정크본드      - 회사채 BBB- minus AA- 스프레드 (ECOS)
  8. 외국인 수급   - EWY 5일 수익률 프록시
  11. 코스닥/코스피 - 상대강도 60일 변화

스킵 지표 (5개):
  2. 주가강도      - KRX API 세션 인증 필요
  3. 시장폭        - KRX API 세션 인증 필요
  4. 풋/콜 비율    - KRX API 세션 인증 필요
  9. 신용잔고      - 금투협 JS 동적 로딩
  10. 고객예탁금   - 금투협 JS 동적 로딩

정규화: 과거 1년 rolling window Z-score CDF 방식
"""

import warnings
warnings.filterwarnings('ignore')

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import yfinance as yf
from scipy.stats import norm


# ─────────────────────────────────────────────
# 정규화 함수
# ─────────────────────────────────────────────
def zscore_to_percentile(series: pd.Series, current: float) -> float:
    """Z-score → 0~100 CDF 변환"""
    mean = series.mean()
    std = series.std()
    if std == 0 or pd.isna(std):
        return 50.0
    z = (current - mean) / std
    return float(norm.cdf(z) * 100)


def grade(score: float) -> str:
    if score < 20:
        return "극도의공포"
    elif score < 40:
        return "공포"
    elif score < 60:
        return "중립"
    elif score < 80:
        return "탐욕"
    else:
        return "극도의탐욕"


# ─────────────────────────────────────────────
# 각 지표 시계열 데이터 수집 함수
# ─────────────────────────────────────────────

def get_momentum_series(start: str, end: str) -> pd.Series:
    """코스피 50일 이평 괴리율 시계열"""
    ks = yf.download("^KS11", start=start, end=end, progress=False, auto_adjust=True)
    if ks.empty:
        return pd.Series(dtype=float)
    close = ks['Close'].squeeze()
    ma50 = close.rolling(50).mean()
    return ((close - ma50) / ma50 * 100).dropna()


def get_volatility_series(start: str, end: str) -> pd.Series:
    """KOSPI 실현변동성 vs 50일 이평 괴리율"""
    ks = yf.download("^KS11", start=start, end=end, progress=False, auto_adjust=True)
    if ks.empty:
        return pd.Series(dtype=float)
    close = ks['Close'].squeeze()
    returns = close.pct_change()
    vol20 = returns.rolling(20).std() * np.sqrt(252) * 100
    ma50_vol = vol20.rolling(50).mean()
    return ((vol20 - ma50_vol) / ma50_vol).dropna()


def get_safe_haven_series(start: str, end: str) -> pd.Series:
    """코스피 vs 국채 ETF 60일 수익률 차이"""
    ks = yf.download("^KS11", start=start, end=end, progress=False, auto_adjust=True)
    bond = yf.download("114820.KS", start=start, end=end, progress=False, auto_adjust=True)
    if ks.empty or bond.empty:
        return pd.Series(dtype=float)

    ks_ret = ks['Close'].squeeze().pct_change(60) * 100
    bond_ret = bond['Close'].squeeze().pct_change(60) * 100

    # 날짜 맞추기
    df = pd.concat([ks_ret.rename('ks'), bond_ret.rename('bond')], axis=1).dropna()
    return (df['ks'] - df['bond']).dropna()


def get_junk_bond_series_monthly(start_ym: str, end_ym: str) -> pd.Series:
    """ECOS 721Y001 회사채 스프레드 월별 시계열 (10건씩 분할 요청)"""
    api_key = "sample"

    def fetch_paged(item_code, start_ym, end_ym):
        """sample 키 10건 제한 우회: 연도별 분할 요청"""
        storage = {}
        start_year = int(start_ym[:4])
        end_year = int(end_ym[:4])

        for year in range(start_year, end_year + 1):
            y_start = f"{year}01"
            y_end = f"{year}12" if year < end_year else end_ym
            url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/10/721Y001/M/{y_start}/{y_end}/{item_code}"
            try:
                r = requests.get(url, timeout=10)
                data = r.json()
                if 'StatisticSearch' in data:
                    for row in data['StatisticSearch'].get('row', []):
                        t = row.get('TIME', '')
                        v = row.get('DATA_VALUE', '')
                        if t and v:
                            storage[t] = float(v)
            except Exception:
                continue

        if not storage:
            return pd.Series(dtype=float)
        s = pd.Series(storage, dtype=float)
        s.index = pd.to_datetime(s.index, format='%Y%m')
        return s.sort_index()

    aa = fetch_paged("7020000", start_ym, end_ym)
    bbb = fetch_paged("7030000", start_ym, end_ym)

    if aa.empty or bbb.empty:
        return pd.Series(dtype=float)

    combined = pd.concat([aa.rename('aa'), bbb.rename('bbb')], axis=1).dropna()
    return (combined['bbb'] - combined['aa']).dropna()


def get_junk_bond_series_daily(start: str, end: str) -> pd.Series:
    """ECOS 정크본드 스프레드: 일별(817Y002) 실패 시 월별(721Y001)로 폴백"""
    api_key = "sample"
    start_d = start.replace('-', '')
    end_d = end.replace('-', '')

    def fetch_daily_paged(item_code, start_d, end_d):
        """월별로 분할 요청 (sample 키 10건 제한)"""
        from datetime import date
        storage = {}
        s_date = datetime.strptime(start_d, '%Y%m%d')
        e_date = datetime.strptime(end_d, '%Y%m%d')
        cur = s_date

        while cur <= e_date:
            # 10일씩 요청 (일별 10건 = 10영업일)
            chunk_end = min(e_date, cur + timedelta(days=14))
            url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/10/817Y002/D/{cur.strftime('%Y%m%d')}/{chunk_end.strftime('%Y%m%d')}/{item_code}"
            try:
                r = requests.get(url, timeout=10)
                data = r.json()
                if 'StatisticSearch' in data:
                    for row in data['StatisticSearch'].get('row', []):
                        t = row.get('TIME', '')
                        v = row.get('DATA_VALUE', '')
                        if t and v:
                            storage[t] = float(v)
            except Exception:
                pass
            cur = chunk_end + timedelta(days=1)

        if not storage:
            return pd.Series(dtype=float)
        s = pd.Series(storage, dtype=float)
        s.index = pd.to_datetime(s.index, format='%Y%m%d')
        return s.sort_index()

    aa = fetch_daily_paged("010300000", start_d, end_d)
    bbb = fetch_daily_paged("010320000", start_d, end_d)

    if not aa.empty and not bbb.empty and len(aa) > 10:
        combined = pd.concat([aa.rename('aa'), bbb.rename('bbb')], axis=1).dropna()
        return (combined['bbb'] - combined['aa']).dropna()

    # 일별 데이터 부족 → 월별로 대체 (더 안정적)
    s_ym = start_d[:6]
    e_ym = end_d[:6]
    return get_junk_bond_series_monthly(s_ym, e_ym)


def get_ewy_series(start: str, end: str) -> pd.Series:
    """EWY 5일 수익률 시계열"""
    ewy = yf.download("EWY", start=start, end=end, progress=False, auto_adjust=True)
    if ewy.empty:
        return pd.Series(dtype=float)
    close = ewy['Close'].squeeze()
    return (close.pct_change(5) * 100).dropna()


def get_kosdaq_kospi_series(start: str, end: str) -> pd.Series:
    """코스닥/코스피 비율 60일 변화"""
    kq = yf.download("^KQ11", start=start, end=end, progress=False, auto_adjust=True)
    ks = yf.download("^KS11", start=start, end=end, progress=False, auto_adjust=True)
    if kq.empty or ks.empty:
        return pd.Series(dtype=float)

    # 날짜 맞추기
    df = pd.concat([
        kq['Close'].squeeze().rename('kq'),
        ks['Close'].squeeze().rename('ks')
    ], axis=1).dropna()

    ratio = df['kq'] / df['ks']
    return (ratio.pct_change(60) * 100).dropna()


# ─────────────────────────────────────────────
# 오늘 심리지수 계산
# ─────────────────────────────────────────────

INDICATOR_NAMES = {
    "모멘텀": "코스피 vs 50일이평 괴리율",
    "변동성": "KOSPI 실현변동성 vs 이평 (역방향)",
    "안전자산": "코스피 vs 국채ETF 수익률 차이",
    "정크본드": "회사채 BBB- minus AA- 스프레드 (역방향)",
    "외국인수급": "EWY 5일 수익률 (외국인 프록시)",
    "코스닥코스피": "코스닥/코스피 상대강도 60일 변화",
}

# 변동성, 정크본드는 높을수록 공포 → 역방향
INVERTED = {"변동성", "정크본드"}


def compute_today(lookback_start="2024-01-01") -> dict:
    """오늘 심리지수 계산"""
    today_str = datetime.today().strftime("%Y-%m-%d")
    end_str = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    lb_start = lookback_start

    print(f"데이터 수집 중... (lookback: {lb_start} ~ {today_str})")

    # 각 지표 시계열 수집
    series_map = {}
    current_map = {}

    # 1. 모멘텀
    print("  [1/6] 모멘텀...")
    s = get_momentum_series(lb_start, end_str)
    if not s.empty:
        series_map["모멘텀"] = s
        current_map["모멘텀"] = float(s.iloc[-1])

    # 2. 변동성
    print("  [2/6] 변동성...")
    s = get_volatility_series(lb_start, end_str)
    if not s.empty:
        series_map["변동성"] = s
        current_map["변동성"] = float(s.iloc[-1])

    # 3. 안전자산
    print("  [3/6] 안전자산...")
    s = get_safe_haven_series(lb_start, end_str)
    if not s.empty:
        series_map["안전자산"] = s
        current_map["안전자산"] = float(s.iloc[-1])

    # 4. 정크본드
    print("  [4/6] 정크본드 (ECOS)...")
    s = get_junk_bond_series_daily(lb_start, today_str)
    if not s.empty:
        series_map["정크본드"] = s
        current_map["정크본드"] = float(s.iloc[-1])

    # 5. 외국인수급
    print("  [5/6] 외국인수급 (EWY)...")
    s = get_ewy_series(lb_start, end_str)
    if not s.empty:
        series_map["외국인수급"] = s
        current_map["외국인수급"] = float(s.iloc[-1])

    # 6. 코스닥/코스피
    print("  [6/6] 코스닥/코스피...")
    s = get_kosdaq_kospi_series(lb_start, end_str)
    if not s.empty:
        series_map["코스닥코스피"] = s
        current_map["코스닥코스피"] = float(s.iloc[-1])

    # Z-score 정규화 → 0~100
    components = {}
    valid_keys = list(series_map.keys())
    weight = 1.0 / len(valid_keys) if valid_keys else 0

    for key in valid_keys:
        raw = current_map[key]
        score = zscore_to_percentile(series_map[key], raw)
        # 역방향: 높을수록 공포 → 반전
        if key in INVERTED:
            score = 100 - score
        components[key] = {
            "raw": round(raw, 4),
            "score": round(score, 1),
            "weight": round(weight, 4),
            "description": INDICATOR_NAMES.get(key, key)
        }

    # 최종 점수
    total_score = sum(v["score"] * v["weight"] for v in components.values())
    total_score = round(total_score, 1)

    skipped = ["주가강도(KRX)", "시장폭(KRX)", "풋/콜(KRX)", "신용잔고(KOFIA)", "고객예탁금(KOFIA)"]

    result = {
        "date": today_str,
        "score": total_score,
        "grade": grade(total_score),
        "components": components,
        "available_count": len(valid_keys),
        "skipped": skipped,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return result


def print_result(result: dict):
    """결과 출력"""
    print(f"\n{'='*60}")
    print(f"한국 시장 심리지수 v7 ({result['date']})")
    print(f"{'='*60}")
    print(f"  점수: {result['score']:.1f} / 100")
    print(f"  등급: {result['grade']}")
    print(f"  사용 지표: {result['available_count']}개")
    print(f"\n  [지표별 기여]")
    for key, v in result['components'].items():
        print(f"  {key:12s}: raw={v['raw']:8.3f} | score={v['score']:5.1f} | weight={v['weight']:.3f}")
    print(f"\n  [스킵 지표]")
    for s in result['skipped']:
        print(f"  - {s}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    result = compute_today()
    print_result(result)

    with open("today_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("today_result.json 저장 완료")
