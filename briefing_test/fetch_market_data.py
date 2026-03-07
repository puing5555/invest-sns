import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta

tickers = {
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "VIX": "^VIX",
    "USD/KRW": "USDKRW=X",
    "WTI": "CL=F",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
}

# Fetch from 2025-03-03 to 2025-03-08 (inclusive window)
result = {}

for name, ticker in tickers.items():
    try:
        t = yf.Ticker(ticker)
        hist = t.history(start="2025-03-03", end="2025-03-08", interval="1d")
        if hist.empty:
            print(f"  {name} ({ticker}): NO DATA")
            continue
        for idx in hist.index:
            date_str = idx.strftime("%Y-%m-%d")
            row = hist.loc[idx]
            if date_str not in result:
                result[date_str] = {}
            result[date_str][name] = {
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
            }
        print(f"  {name} ({ticker}): OK — dates {list(hist.index.strftime('%Y-%m-%d'))}")
    except Exception as e:
        print(f"  {name} ({ticker}): ERROR {e}")

# Compute pct_change between consecutive days
dates_sorted = sorted(result.keys())
for i, d in enumerate(dates_sorted):
    if i == 0:
        continue
    prev_d = dates_sorted[i-1]
    for name in result[d]:
        if name in result[prev_d]:
            cur = result[d][name]["close"]
            prev = result[prev_d][name]["close"]
            chg = cur - prev
            pct = (chg / prev * 100) if prev != 0 else 0
            result[d][name]["chg"] = round(chg, 2)
            result[d][name]["pct"] = round(pct, 2)

with open("market_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n=== Summary ===")
for d in sorted(result.keys()):
    print(f"\n{d}:")
    for name, data in result[d].items():
        chg_str = f" chg={data.get('chg','N/A')} pct={data.get('pct','N/A')}%" if 'chg' in data else ""
        print(f"  {name}: close={data['close']}{chg_str}")

print("\nSaved to market_data.json")
