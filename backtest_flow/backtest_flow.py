"""
수급 기반 백테스트 엔진
전략 1: 외국인 연속 순매수
전략 2: 기관+외국인 동시 전환
전략 3: 스마트머니 (개인 폭매도 + 외국인 폭매수 교집합)
"""
import warnings
import pandas as pd
import numpy as np
warnings.filterwarnings("ignore")


# ── 공통 유틸 ───────────────────────────────────────────────────────────────

def get_nth_trading_day(df, base_date, n):
    """n거래일 후 날짜 반환"""
    dates = df.index.tolist()
    try:
        idx = dates.index(base_date)
        if idx + n < len(dates):
            return dates[idx + n]
    except Exception:
        pass
    return None


def calc_return(price_df, buy_date, sell_date):
    """시가 매수 → 종가 매도 수익률 (%)"""
    try:
        # 컬럼명 한글/영문 모두 대응
        open_col  = [c for c in price_df.columns if "시가" in str(c) or c == "Open"][0]
        close_col = [c for c in price_df.columns if "종가" in str(c) or c == "Close"][0]
        buy_price  = price_df.loc[buy_date, open_col]
        sell_price = price_df.loc[sell_date, close_col]
        if buy_price > 0:
            return (sell_price - buy_price) / buy_price * 100
    except Exception:
        pass
    return None


def find_col(df, keywords):
    """키워드 포함 컬럼 찾기"""
    for c in df.columns:
        for kw in keywords:
            if kw in str(c):
                return c
    return None


# ── 전략 1: 외국인 연속 순매수 ─────────────────────────────────────────────

def strategy1_foreign_consecutive(flow_df, price_df, consec_days, hold_days_list=[5, 10, 20]):
    """
    consec_days일 연속 외국인 순매수 확인 → 다음날 시가 매수
    """
    results = []
    foreign_col = find_col(flow_df, ["외국인"])
    if foreign_col is None:
        return pd.DataFrame()

    flow = flow_df.copy()
    flow["is_foreign_buy"] = flow[foreign_col] > 0
    dates = flow.index.tolist()
    max_hold = max(hold_days_list)

    for i in range(consec_days, len(dates) - max_hold - 1):
        window = flow.iloc[i - consec_days:i]
        if not window["is_foreign_buy"].all():
            continue

        entry_date = dates[i]
        if entry_date not in price_df.index:
            continue

        row = {
            "entry_date": entry_date,
            "consec_days": consec_days,
            "foreign_buy_amount": flow.iloc[i - 1][foreign_col],
        }
        for hold in hold_days_list:
            sell_date = get_nth_trading_day(price_df, entry_date, hold)
            row[f"ret_{hold}d"] = calc_return(price_df, entry_date, sell_date) if sell_date else None

        results.append(row)

    return pd.DataFrame(results)


# ── 전략 2: 기관+외국인 동시 전환 ─────────────────────────────────────────

def strategy2_institution_foreign_switch(flow_df, price_df, confirm_days, hold_days_list=[5, 10, 20]):
    """
    기관+외국인 동시 순매수 전환 (이전에는 둘 다 순매도 or 어느 하나 순매도)
    confirm_days: 연속 확인 일수
    """
    results = []
    foreign_col     = find_col(flow_df, ["외국인"])
    institution_col = find_col(flow_df, ["기관"])
    if foreign_col is None or institution_col is None:
        return pd.DataFrame()

    flow = flow_df.copy()
    flow["foreign_pos"]     = flow[foreign_col] > 0
    flow["institution_pos"] = flow[institution_col] > 0
    flow["both_buy"]        = flow["foreign_pos"] & flow["institution_pos"]
    dates = flow.index.tolist()
    max_hold = max(hold_days_list)

    for i in range(confirm_days + 1, len(dates) - max_hold - 1):
        window = flow.iloc[i - confirm_days:i]
        if not window["both_buy"].all():
            continue

        # 전환 확인: confirm_days 이전 날이 순매도였어야 함
        prev = flow.iloc[i - confirm_days - 1]
        if prev["foreign_pos"] and prev["institution_pos"]:
            continue  # 이미 순매수 → 전환 아님

        entry_date = dates[i]
        if entry_date not in price_df.index:
            continue

        row = {"entry_date": entry_date, "confirm_days": confirm_days}
        for hold in hold_days_list:
            sell_date = get_nth_trading_day(price_df, entry_date, hold)
            row[f"ret_{hold}d"] = calc_return(price_df, entry_date, sell_date) if sell_date else None

        results.append(row)

    return pd.DataFrame(results)


# ── 전략 3: 스마트머니 ────────────────────────────────────────────────────

def strategy3_smart_money(all_flow, all_price, confirm_days, hold_days_list=[5, 10, 20], top_n=10):
    """
    매일 개인 순매도 상위 top_n + 외국인 순매수 상위 top_n 교집합
    confirm_days: 연속 교집합 일수
    """
    results = []

    all_dates = sorted(set.union(*[set(df.index) for df in all_flow.values()]))
    max_hold = max(hold_days_list)

    for i in range(confirm_days, len(all_dates) - max_hold - 1):
        entry_date = all_dates[i]
        candidate_tickers = None

        for d_back in range(confirm_days):
            check_date = all_dates[i - confirm_days + d_back]

            retail_sell = {}
            foreign_buy = {}

            for ticker, flow_df in all_flow.items():
                if check_date not in flow_df.index:
                    continue
                r = flow_df.loc[check_date]
                f_col = find_col(flow_df, ["외국인"])
                r_col = find_col(flow_df, ["개인"])
                if f_col is None or r_col is None:
                    continue
                f_val = r[f_col]
                r_val = r[r_col]
                if f_val > 0:
                    foreign_buy[ticker] = f_val
                if r_val < 0:
                    retail_sell[ticker] = abs(r_val)

            top_foreign    = set(sorted(foreign_buy,    key=foreign_buy.get,    reverse=True)[:top_n])
            top_retail_sel = set(sorted(retail_sell,    key=retail_sell.get,    reverse=True)[:top_n])
            cross = top_foreign & top_retail_sel

            if d_back == 0:
                candidate_tickers = cross
            else:
                candidate_tickers &= cross

            if not candidate_tickers:
                break

        if not candidate_tickers:
            continue

        for ticker in candidate_tickers:
            if ticker not in all_price:
                continue
            price_df = all_price[ticker]
            if entry_date not in price_df.index:
                continue

            row = {"entry_date": entry_date, "ticker": ticker, "confirm_days": confirm_days}
            for hold in hold_days_list:
                sell_date = get_nth_trading_day(price_df, entry_date, hold)
                row[f"ret_{hold}d"] = calc_return(price_df, entry_date, sell_date) if sell_date else None

            results.append(row)

    return pd.DataFrame(results)


# ── 집계 ─────────────────────────────────────────────────────────────────

def summarize_results(df, hold_days=[5, 10, 20]):
    summary = {}
    for hold in hold_days:
        col = f"ret_{hold}d"
        if col not in df.columns:
            continue
        valid = df[col].dropna()
        if len(valid) == 0:
            continue
        summary[f"{hold}일"] = {
            "시그널수":   int(len(valid)),
            "평균수익률": round(float(valid.mean()), 2),
            "승률":       round(float((valid > 0).mean() * 100), 1),
            "최대수익":   round(float(valid.max()), 2),
            "최대손실":   round(float(valid.min()), 2),
            "중간값":     round(float(valid.median()), 2),
        }
    return summary


def top_bottom_tickers(df, hold_day=10, n=10):
    col = f"ret_{hold_day}d"
    if col not in df.columns or "ticker" not in df.columns:
        return {}, {}
    by_ticker = df.groupby("ticker")[col].mean().dropna()
    top    = {k: round(v, 2) for k, v in by_ticker.nlargest(n).items()}
    bottom = {k: round(v, 2) for k, v in by_ticker.nsmallest(n).items()}
    return top, bottom
