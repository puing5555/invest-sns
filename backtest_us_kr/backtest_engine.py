"""
backtest_engine.py — 백테스트 엔진
미국 급등 → 한국 다음 영업일 매수 → A/B/C 매도 시나리오
"""

import pandas as pd
import numpy as np


def get_next_kr_trading_day(us_date, kr_df):
    """미국 날짜 다음 한국 영업일 반환 (최대 5일 탐색)"""
    next_day = us_date + pd.Timedelta(days=1)
    for i in range(5):
        candidate = next_day + pd.Timedelta(days=i)
        if candidate in kr_df.index:
            return candidate
    return None


def get_nth_trading_day(buy_date, kr_df, n=2):
    """매수일 기준 n번째 이후 거래일 반환"""
    try:
        idx = kr_df.index.get_loc(buy_date)
        target_idx = idx + (n - 1)
        if target_idx < len(kr_df):
            return kr_df.index[target_idx]
    except Exception:
        pass
    return None


def classify_surge(pct):
    if pct < 10:
        return "5~10%"
    elif pct < 15:
        return "10~15%"
    else:
        return "15%+"


def get_weekday_group(date):
    """월~목 vs 금요일"""
    dow = date.dayofweek  # 0=월, 4=금
    return "금요일" if dow == 4 else "월~목"


def get_price(df, date, col_kr="종가", col_en="Close"):
    """컬럼명 유연 조회"""
    if col_kr in df.columns:
        return df.loc[date, col_kr]
    elif col_en in df.columns:
        return df.loc[date, col_en]
    return None


def get_open_price(df, date):
    if "시가" in df.columns:
        return df.loc[date, "시가"]
    elif "Open" in df.columns:
        return df.loc[date, "Open"]
    return None


def run_backtest(us_df, kr_df, threshold=5.0):
    """
    단일 페어 백테스트
    Returns: pd.DataFrame with columns:
        us_date, us_pct, surge_class, weekday_group,
        kr_buy_date, buy_price, return_A, return_B, return_C
    """
    results = []

    us_df = us_df.copy()
    us_df.index = pd.to_datetime(us_df.index).tz_localize(None)
    kr_df = kr_df.copy()
    kr_df.index = pd.to_datetime(kr_df.index).tz_localize(None)

    pct_col = "pct_change"

    for i in range(1, len(us_df) - 3):
        us_date = us_df.index[i]
        us_pct_val = us_df.iloc[i][pct_col]

        # NaN 처리
        if pd.isna(us_pct_val):
            continue
        # scalar 추출
        if hasattr(us_pct_val, '__len__'):
            us_pct_val = float(us_pct_val.iloc[0]) if len(us_pct_val) > 0 else np.nan
        us_pct = float(us_pct_val)

        if us_pct < threshold:
            continue

        kr_buy_date = get_next_kr_trading_day(us_date, kr_df)
        if kr_buy_date is None:
            continue

        buy_price = get_open_price(kr_df, kr_buy_date)
        if buy_price is None or pd.isna(buy_price) or buy_price == 0:
            continue

        sell_date_A = kr_buy_date
        sell_date_B = get_nth_trading_day(kr_buy_date, kr_df, n=2)
        sell_date_C = get_nth_trading_day(kr_buy_date, kr_df, n=3)

        def calc_return(sell_date):
            if sell_date is None or sell_date not in kr_df.index:
                return None
            sp = get_price(kr_df, sell_date)
            if sp is None or pd.isna(sp) or sp == 0:
                return None
            return (float(sp) - float(buy_price)) / float(buy_price) * 100

        results.append({
            "us_date":       us_date,
            "us_pct":        us_pct,
            "surge_class":   classify_surge(us_pct),
            "weekday_group": get_weekday_group(us_date),
            "kr_buy_date":   kr_buy_date,
            "buy_price":     float(buy_price),
            "return_A":      calc_return(sell_date_A),
            "return_B":      calc_return(sell_date_B),
            "return_C":      calc_return(sell_date_C),
        })

    return pd.DataFrame(results)


def summarize_pair(df_results):
    """페어 결과 요약"""
    if df_results.empty:
        return {"signals": 0}

    def stats(col):
        vals = df_results[col].dropna()
        if vals.empty:
            return {"avg": None, "win_rate": None, "max": None, "min": None, "n": 0}
        return {
            "avg":      round(vals.mean(), 2),
            "win_rate": round((vals > 0).mean() * 100, 1),
            "max":      round(vals.max(), 2),
            "min":      round(vals.min(), 2),
            "n":        len(vals),
        }

    return {
        "signals": len(df_results),
        "A": stats("return_A"),
        "B": stats("return_B"),
        "C": stats("return_C"),
    }


def run_all_pairs(us_data, kr_data, pair_map, kr_tickers_meta, threshold=5.0):
    """
    전체 페어 백테스트 실행
    Returns: dict[us_ticker][kr_code] = {results_df, summary}
    """
    all_results = {}

    for us_ticker, kr_codes in pair_map.items():
        if us_ticker not in us_data:
            continue
        us_df = us_data[us_ticker]
        all_results[us_ticker] = {}

        for kr_code in kr_codes:
            if kr_code not in kr_data:
                continue
            kr_df = kr_data[kr_code]
            kr_name = kr_tickers_meta[kr_code][0]

            df_res = run_backtest(us_df, kr_df, threshold)
            summary = summarize_pair(df_res)
            all_results[us_ticker][kr_code] = {
                "name":    kr_name,
                "results": df_res,
                "summary": summary,
            }

    return all_results


if __name__ == "__main__":
    print("backtest_engine.py — import only")
