"""
fetch_data.py — 미국/한국 주식 데이터 수집
pykrx 우선, 실패 시 yfinance 한국 티커로 폴백
"""

import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# ── 미국 티커 ──────────────────────────────────────────
US_TICKERS = ["NVDA", "TSLA", "AAPL", "AMD", "AMZN", "CRCL", "COIN",
              "META", "GOOG", "MSFT", "AVGO", "ARM", "SMCI"]

# ── 한국 티커: {코드: (이름, 그룹, 사이즈)} ──────────────
KR_TICKERS = {
    # 반도체 대형
    "000660": ("SK하이닉스",       "반도체", "대형"),
    "005930": ("삼성전자",          "반도체", "대형"),
    # 반도체 중형
    "042700": ("한미반도체",        "반도체", "중형"),
    "058470": ("리노공업",          "반도체", "중형"),
    "095340": ("ISC",               "반도체", "중형"),
    "089030": ("테크윙",            "반도체", "중형"),
    "036930": ("주성엔지니어링",    "반도체", "중형"),
    "440110": ("파두",              "반도체", "중형"),
    "394280": ("오픈엣지테크",      "반도체", "중형"),
    "399720": ("가온칩스",          "반도체", "중형"),
    "045970": ("코아시아",          "반도체", "중형"),
    # 2차전지 대형
    "373220": ("LG에너지솔루션",   "2차전지", "대형"),
    "006400": ("삼성SDI",           "2차전지", "대형"),
    # 2차전지 중형
    "247540": ("에코프로비엠",      "2차전지", "중형"),
    "003670": ("포스코퓨처엠",      "2차전지", "중형"),
    "137400": ("피엔티",            "2차전지", "중형"),
    # IT부품 대형
    "011070": ("LG이노텍",          "IT부품", "대형"),
    "009150": ("삼성전기",          "IT부품", "대형"),
    # IT부품 중형
    "090460": ("비에이치",          "IT부품", "중형"),
    "033240": ("자화전자",          "IT부품", "중형"),
    "007810": ("코리아써키트",      "IT부품", "중형"),
    # 물류
    "000120": ("CJ대한통운",        "물류", "대형"),
    "002320": ("한진",              "물류", "중형"),
    # 크립토
    "094480": ("갤럭시아머니트리", "크립토", "중형"),
    "054920": ("한컴위드",          "크립토", "중형"),
    "041190": ("우리기술투자",      "크립토", "중형"),
    "121800": ("비덴트",            "크립토", "중형"),
    # IT서비스
    "035420": ("네이버",            "IT서비스", "대형"),
    "035720": ("카카오",            "IT서비스", "대형"),
    "089600": ("나스미디어",        "IT서비스", "중형"),
    "012510": ("더존비즈온",        "IT서비스", "중형"),
    "030520": ("한글과컴퓨터",      "IT서비스", "중형"),
    "018260": ("삼성SDS",           "IT서비스", "대형"),
}

# ── 페어링 맵 ─────────────────────────────────────────
PAIR_MAP = {
    "NVDA": ["000660", "005930", "042700", "058470", "095340", "089030",
             "036930", "440110", "394280", "399720", "045970"],
    "AMD":  ["000660", "005930", "042700", "058470", "095340", "089030",
             "036930", "440110", "394280", "399720", "045970"],
    "SMCI": ["042700", "058470", "095340", "089030", "036930"],
    "TSLA": ["373220", "006400", "247540", "003670", "137400"],
    "AAPL": ["011070", "009150", "090460", "033240", "007810"],
    "AMZN": ["000120", "002320"],
    "CRCL": ["094480", "054920", "041190", "121800"],
    "COIN": ["094480", "054920", "041190", "121800"],
    "META": ["035420", "035720", "089600", "012510", "030520", "018260"],
    "GOOG": ["035420", "035720", "089600", "012510", "030520", "018260"],
    "MSFT": ["035420", "035720", "089600", "012510", "030520", "018260"],
    "AVGO": ["000660", "005930", "042700", "058470"],
    "ARM":  ["000660", "005930", "042700", "058470"],
}


def fetch_us_data(ticker, start="2023-01-01", end="2026-03-07"):
    try:
        df = yf.download(ticker, start=start, end=end, auto_adjust=True,
                         progress=False)
        if df.empty:
            return None
        # yfinance 1.x MultiIndex 처리
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df["pct_change"] = df["Close"].pct_change() * 100
        return df
    except Exception as e:
        print(f"  [미국 오류] {ticker}: {e}")
        return None


def fetch_kr_data_pykrx(code, start="20230101", end="20260307"):
    """pykrx로 한국 주식 수집"""
    try:
        from pykrx import stock
        df = stock.get_market_ohlcv_by_date(start, end, code)
        if df is None or df.empty:
            return None
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df["pct_change"] = df["종가"].pct_change() * 100
        return df
    except Exception as e:
        print(f"  [pykrx 오류] {code}: {e}")
        return None


def fetch_kr_data_yf(code, start="2023-01-01", end="2026-03-07"):
    """yfinance 폴백으로 한국 주식 수집"""
    ticker = f"{code}.KS"
    try:
        df = yf.download(ticker, start=start, end=end, auto_adjust=True,
                         progress=False)
        if df.empty:
            ticker = f"{code}.KQ"
            df = yf.download(ticker, start=start, end=end, auto_adjust=True,
                             progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df["종가"] = df["Close"]
        df["시가"] = df["Open"]
        df["pct_change"] = df["Close"].pct_change() * 100
        return df
    except Exception as e:
        print(f"  [yfinance KR 오류] {code}: {e}")
        return None


def fetch_kr_data(code, start="20230101", end="20260307"):
    """pykrx 우선, 실패 시 yfinance 폴백"""
    df = fetch_kr_data_pykrx(code, start, end)
    if df is not None and not df.empty:
        return df, "pykrx"
    df = fetch_kr_data_yf(code, start.replace("-", "")[:8] if "-" in start else start)
    if df is not None and not df.empty:
        return df, "yfinance"
    return None, "실패"


def load_all_data(us_start="2023-01-01", us_end="2026-03-07",
                  kr_start="20230101", kr_end="20260307"):
    """전체 데이터 로드 후 딕셔너리로 반환"""
    print("=" * 60)
    print("데이터 수집 시작")
    print("=" * 60)

    us_data = {}
    us_status = {}
    print("\n[미국 주식]")
    for t in US_TICKERS:
        df = fetch_us_data(t, us_start, us_end)
        if df is not None:
            us_data[t] = df
            us_status[t] = f"✅ {len(df)}행"
            print(f"  {t}: {len(df)}행")
        else:
            us_status[t] = "❌ 실패"
            print(f"  {t}: 실패")

    kr_data = {}
    kr_status = {}
    print("\n[한국 주식]")
    for code, (name, sector, size) in KR_TICKERS.items():
        df, src = fetch_kr_data(code, kr_start, kr_end)
        if df is not None:
            kr_data[code] = df
            kr_status[code] = f"✅ {len(df)}행 ({src})"
            print(f"  {code} {name}: {len(df)}행 ({src})")
        else:
            kr_status[code] = "❌ 실패"
            print(f"  {code} {name}: 실패")

    print(f"\n수집 완료 - 미국 {len(us_data)}/{len(US_TICKERS)}, "
          f"한국 {len(kr_data)}/{len(KR_TICKERS)}")
    return us_data, kr_data, us_status, kr_status


if __name__ == "__main__":
    us_data, kr_data, us_status, kr_status = load_all_data()
