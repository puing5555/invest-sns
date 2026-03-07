"""
한국 시장 심리지수 v7.1
10개 지표 기반 공포/탐욕 지수 (2026-03-07 업데이트)

v7 대비 개선:
  - 주가강도 (52주 신고가/신저가): yfinance top 20 KOSPI stocks → NEW
  - 시장폭 (MA200 비율): yfinance top 20 KOSPI stocks → NEW
  - 신용잔고: KOFIA API (STATSCU0100000070BO) → NEW
  - 고객예탁금: KOFIA API (STATSCU0100000060BO) → NEW

여전히 미해결:
  - 풋/콜 비율: KRX API 세션 인증 필요 (v7.1에서 스킵)

작동 지표 (10개):
  1. 모멘텀        - 코스피 vs 50일 이평 (yfinance)
  2. 주가강도      - KOSPI 상위 20종목 52주 신고/신저 비율 (yfinance)
  3. 시장폭        - KOSPI 상위 20종목 MA200 비율 (yfinance)
  5. 변동성        - KOSPI 실현변동성 vs 50일 이평 (yfinance)
  6. 안전자산      - 코스피 vs 국채ETF 60일 수익률 차이
  7. 정크본드      - 회사채 BBB- minus AA- 스프레드 (ECOS)
  8. 외국인수급    - EWY 5일 수익률 프록시
  9. 신용잔고      - 신용거래융자 전체 (KOFIA)
  10. 고객예탁금   - 투자자예탁금 (KOFIA)
  11. 코스닥/코스피 - 상대강도 60일 변화

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
# KOSPI top 20 stocks for 주가강도/시장폭
# ─────────────────────────────────────────────
KOSPI_TOP20 = [
    '005930.KS',  # Samsung Electronics
    '000660.KS',  # SK Hynix
    '207940.KS',  # Samsung Biologics
    '005380.KS',  # Hyundai Motor
    '051910.KS',  # LG Chem
    '035420.KS',  # NAVER
    '006400.KS',  # Samsung SDI
    '373220.KS',  # LG Energy Solution
    '000270.KS',  # Kia
    '068270.KS',  # Celltrion
    '105560.KS',  # KB Financial
    '055550.KS',  # Shinhan Financial
    '012330.KS',  # Hyundai Mobis
    '028260.KS',  # Samsung C&T
    '066570.KS',  # LG Electronics
    '003550.KS',  # LG Corp
    '096770.KS',  # SK Innovation
    '017670.KS',  # SK Telecom
    '030200.KS',  # KT Corp
    '009150.KS',  # Samsung Electro-Mech
]


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
# yfinance 기반 지표
# ─────────────────────────────────────────────

def get_momentum_series(start: str, end: str) -> pd.Series:
    """코스피 50일 이평 괴리율"""
    ks = yf.download("^KS11", start=start, end=end, progress=False, auto_adjust=True)
    if ks.empty:
        return pd.Series(dtype=float)
    close = ks['Close'].squeeze()
    ma50 = close.rolling(50).mean()
    return ((close - ma50) / ma50 * 100).dropna()


def get_stock_strength_series(start: str, end: str) -> pd.Series:
    """
    주가강도: KOSPI 상위 20종목 기반 52주 신고/신저 비율
    신고가 근접(5% 이내) 비율 - 신저가 근접(5% 이내) 비율
    """
    print("    (downloading 20 KOSPI stocks for 52w high/low...)")
    df = yf.download(KOSPI_TOP20, start=start, end=end, progress=False, auto_adjust=True)
    if df.empty:
        return pd.Series(dtype=float)

    close = df['Close']
    if isinstance(close, pd.Series):
        close = close.to_frame()

    result = {}
    rolling_max = close.rolling(252, min_periods=200)
    rolling_min = close.rolling(252, min_periods=200)

    for date in close.index[252:]:
        latest = close.loc[date]
        high52 = rolling_max.max().loc[date]
        low52 = rolling_min.min().loc[date]

        near_high = ((latest / high52) >= 0.95).sum()
        near_low = ((latest / low52) <= 1.05).sum()
        total = latest.count()

        if total > 0:
            ratio = (near_high - near_low) / total * 100
            result[date] = ratio

    if not result:
        return pd.Series(dtype=float)
    return pd.Series(result, dtype=float).dropna()


def get_market_breadth_series(start: str, end: str) -> pd.Series:
    """
    시장폭: KOSPI 상위 20종목 MA200 위 비율
    """
    print("    (downloading 20 KOSPI stocks for breadth...)")
    df = yf.download(KOSPI_TOP20, start=start, end=end, progress=False, auto_adjust=True)
    if df.empty:
        return pd.Series(dtype=float)

    close = df['Close']
    if isinstance(close, pd.Series):
        close = close.to_frame()

    ma200 = close.rolling(200).mean()
    above_ratio = ((close > ma200).sum(axis=1) / close.count(axis=1) * 100).dropna()
    return above_ratio


def get_volatility_series(start: str, end: str) -> pd.Series:
    """KOSPI 실현변동성 vs 50일 이평 괴리율 (역방향: 높을수록 공포)"""
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
    df = pd.concat([ks_ret.rename('ks'), bond_ret.rename('bond')], axis=1).dropna()
    return (df['ks'] - df['bond']).dropna()


def get_ewy_series(start: str, end: str) -> pd.Series:
    """EWY 5일 수익률 (외국인 수급 프록시)"""
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
    df = pd.concat([
        kq['Close'].squeeze().rename('kq'),
        ks['Close'].squeeze().rename('ks')
    ], axis=1).dropna()
    ratio = df['kq'] / df['ks']
    return (ratio.pct_change(60) * 100).dropna()


# ─────────────────────────────────────────────
# ECOS 정크본드 지표
# ─────────────────────────────────────────────

def get_junk_bond_series_monthly(start_ym: str, end_ym: str) -> pd.Series:
    """ECOS 721Y001 회사채 스프레드 월별"""
    api_key = "sample"

    def fetch_paged(item_code, start_ym, end_ym):
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
    """ECOS 정크본드: 일별(817Y002) 실패 시 월별(721Y001)로 폴백"""
    api_key = "sample"
    start_d = start.replace('-', '')
    end_d = end.replace('-', '')

    def fetch_daily_paged(item_code, start_d, end_d):
        storage = {}
        s_date = datetime.strptime(start_d, '%Y%m%d')
        e_date = datetime.strptime(end_d, '%Y%m%d')
        cur = s_date
        while cur <= e_date:
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

    s_ym = start_d[:6]
    e_ym = end_d[:6]
    return get_junk_bond_series_monthly(s_ym, e_ym)


# ─────────────────────────────────────────────
# KOFIA 지표 (신용잔고, 고객예탁금)
# ─────────────────────────────────────────────

_kofia_session = None

def _get_kofia_session():
    global _kofia_session
    if _kofia_session is None:
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://freesis.kofia.or.kr',
        })
        _kofia_session = s
    return _kofia_session


def fetch_kofia_data(obj_nm: str, start_date: str = '20150101', end_date: str = None, period: str = 'D') -> list:
    """
    KOFIA API 데이터 조회
    obj_nm: STATSCU0100000060BO (예탁금), STATSCU0100000070BO (신용잔고)
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y%m%d')

    session = _get_kofia_session()
    api_url = 'https://freesis.kofia.or.kr/meta/getMetaDataList.do'

    referer_map = {
        'STATSCU0100000060BO': 'https://freesis.kofia.or.kr/stat/FreeSIS.do?parentDivId=MSIS10000000000000&serviceId=STATSCU0100000060',
        'STATSCU0100000070BO': 'https://freesis.kofia.or.kr/stat/FreeSIS.do?parentDivId=MSIS10000000000000&serviceId=STATSCU0100000070',
    }
    session.headers.update({'Referer': referer_map.get(obj_nm, 'https://freesis.kofia.or.kr/')})

    payload = {
        "dmSearch": {
            "tmpV40": "9999",
            "tmpV41": "1",
            "tmpV1": period,
            "tmpV45": start_date,
            "tmpV46": end_date,
            "OBJ_NM": obj_nm
        }
    }
    try:
        r = session.post(api_url, json=payload, timeout=30)
        data = r.json()
        return data.get('ds1', [])
    except Exception as e:
        print(f"    KOFIA API error ({obj_nm}): {e}")
        return []


def get_credit_balance_series(start: str, end: str) -> pd.Series:
    """신용거래융자 잔고 (KOFIA) - 단위: 만원 → 억원 변환"""
    start_d = start.replace('-', '')
    end_d = end.replace('-', '')
    rows = fetch_kofia_data('STATSCU0100000070BO', start_d, end_d)
    if not rows:
        return pd.Series(dtype=float)

    data = {}
    for row in rows:
        t = row.get('TMPV1', '')
        v = row.get('TMPV2')  # 신용거래융자 전체 (만원)
        if t and v is not None:
            try:
                data[pd.Timestamp(t)] = float(v) / 10000  # → 억원
            except:
                pass

    if not data:
        return pd.Series(dtype=float)
    return pd.Series(data).sort_index().dropna()


def get_customer_deposit_series(start: str, end: str) -> pd.Series:
    """투자자예탁금 (KOFIA) - 단위: 만원 → 억원 변환"""
    start_d = start.replace('-', '')
    end_d = end.replace('-', '')
    rows = fetch_kofia_data('STATSCU0100000060BO', start_d, end_d)
    if not rows:
        return pd.Series(dtype=float)

    data = {}
    for row in rows:
        t = row.get('TMPV1', '')
        v = row.get('TMPV2')  # 투자자예탁금 (만원)
        if t and v is not None:
            try:
                data[pd.Timestamp(t)] = float(v) / 10000  # → 억원
            except:
                pass

    if not data:
        return pd.Series(dtype=float)
    return pd.Series(data).sort_index().dropna()


# ─────────────────────────────────────────────
# 오늘 심리지수 계산
# ─────────────────────────────────────────────

INDICATOR_NAMES = {
    "모멘텀": "코스피 vs 50일이평 괴리율",
    "주가강도": "KOSPI 상위20종목 52주 신고/신저 비율",
    "시장폭": "KOSPI 상위20종목 MA200 위 비율",
    "변동성": "KOSPI 실현변동성 vs 이평 (역방향)",
    "안전자산": "코스피 vs 국채ETF 수익률 차이",
    "정크본드": "회사채 BBB- minus AA- 스프레드 (역방향)",
    "외국인수급": "EWY 5일 수익률 (외국인 프록시)",
    "신용잔고": "신용거래융자 잔고 (KOFIA, 역방향)",
    "고객예탁금": "투자자예탁금 (KOFIA)",
    "코스닥코스피": "코스닥/코스피 상대강도 60일 변화",
}

# 역방향: 높을수록 공포
INVERTED = {"변동성", "정크본드", "신용잔고"}


def compute_today(lookback_start="2024-01-01", include_stock_indices=True) -> dict:
    """오늘 심리지수 계산"""
    today_str = datetime.today().strftime("%Y-%m-%d")
    end_str = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    lb_start = lookback_start

    # KOFIA: use 2015 start for better Z-score baseline
    kofia_start = "2015-01-01"

    print(f"데이터 수집 중... (lookback: {lb_start} ~ {today_str})")

    series_map = {}
    current_map = {}

    def try_add(key, series):
        if series is not None and not series.empty:
            series_map[key] = series
            current_map[key] = float(series.iloc[-1])
            return True
        return False

    # 1. 모멘텀
    print("  [1/10] 모멘텀...")
    try_add("모멘텀", get_momentum_series(lb_start, end_str))

    # 2. 주가강도
    if include_stock_indices:
        print("  [2/10] 주가강도 (52주 신고/신저)...")
        try_add("주가강도", get_stock_strength_series(lb_start, end_str))

    # 3. 시장폭
    if include_stock_indices:
        print("  [3/10] 시장폭 (MA200)...")
        try_add("시장폭", get_market_breadth_series(lb_start, end_str))

    # 4. 변동성
    print("  [4/10] 변동성...")
    try_add("변동성", get_volatility_series(lb_start, end_str))

    # 5. 안전자산
    print("  [5/10] 안전자산...")
    try_add("안전자산", get_safe_haven_series(lb_start, end_str))

    # 6. 정크본드
    print("  [6/10] 정크본드 (ECOS)...")
    try_add("정크본드", get_junk_bond_series_daily(lb_start, today_str))

    # 7. 외국인수급
    print("  [7/10] 외국인수급 (EWY)...")
    try_add("외국인수급", get_ewy_series(lb_start, end_str))

    # 8. 신용잔고
    print("  [8/10] 신용잔고 (KOFIA)...")
    try_add("신용잔고", get_credit_balance_series(kofia_start, end_str))

    # 9. 고객예탁금
    print("  [9/10] 고객예탁금 (KOFIA)...")
    try_add("고객예탁금", get_customer_deposit_series(kofia_start, end_str))

    # 10. 코스닥/코스피
    print("  [10/10] 코스닥/코스피...")
    try_add("코스닥코스피", get_kosdaq_kospi_series(lb_start, end_str))

    # Z-score 정규화 → 0~100
    valid_keys = list(series_map.keys())
    weight = 1.0 / len(valid_keys) if valid_keys else 0

    components = {}
    for key in valid_keys:
        raw = current_map[key]
        score = zscore_to_percentile(series_map[key], raw)
        if key in INVERTED:
            score = 100 - score
        components[key] = {
            "raw": round(raw, 4),
            "score": round(score, 1),
            "weight": round(weight, 4),
            "description": INDICATOR_NAMES.get(key, key)
        }

    total_score = sum(v["score"] * v["weight"] for v in components.values())
    total_score = round(total_score, 1)

    skipped = ["풋/콜 비율(KRX - API 세션 인증 필요)"]

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
    print(f"\n{'='*65}")
    print(f"한국 시장 심리지수 v7.1 ({result['date']})")
    print(f"{'='*65}")
    print(f"  점수: {result['score']:.1f} / 100")
    print(f"  등급: {result['grade']}")
    print(f"  사용 지표: {result['available_count']}개")
    print(f"\n  [지표별 기여]")
    for key, v in result['components'].items():
        inv = " (역)" if key in INVERTED else ""
        print(f"  {key:12s}: raw={v['raw']:9.3f} | score={v['score']:5.1f}{inv}")
    print(f"\n  [스킵 지표]")
    for s in result['skipped']:
        print(f"  - {s}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    result = compute_today()
    print_result(result)

    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("today_result_v7_1.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("today_result_v7_1.json 저장 완료")
