from pykrx import stock
import json

result = {}

# KOSPI/KOSDAQ index OHLCV
try:
    kospi = stock.get_index_ohlcv_by_date("20250303", "20250307", "1001")
    print("KOSPI index OHLCV:")
    print(kospi)
    for idx in kospi.index:
        d = idx.strftime("%Y-%m-%d")
        row = kospi.loc[idx]
        if d not in result:
            result[d] = {}
        result[d]["KOSPI_pykrx"] = {
            "open": float(row["시가"]),
            "high": float(row["고가"]),
            "low": float(row["저가"]),
            "close": float(row["종가"]),
        }
except Exception as e:
    print(f"KOSPI index error: {e}")

try:
    kosdaq = stock.get_index_ohlcv_by_date("20250303", "20250307", "2001")
    print("KOSDAQ index OHLCV:")
    print(kosdaq)
    for idx in kosdaq.index:
        d = idx.strftime("%Y-%m-%d")
        row = kosdaq.loc[idx]
        if d not in result:
            result[d] = {}
        result[d]["KOSDAQ_pykrx"] = {
            "open": float(row["시가"]),
            "high": float(row["고가"]),
            "low": float(row["저가"]),
            "close": float(row["종가"]),
        }
except Exception as e:
    print(f"KOSDAQ index error: {e}")

# Investor trading by date
for date_str in ["20250305", "20250306"]:
    try:
        df = stock.get_market_trading_value_by_investor(date_str, date_str, "KOSPI")
        print(f"\n수급 {date_str}:")
        print(df)
        d = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        if d not in result:
            result[d] = {}
        inv_map = {}
        for inv_name in df.index:
            if "외국인" in str(inv_name):
                inv_map["foreign"] = int(df.loc[inv_name, "순매수"] if "순매수" in df.columns else df.loc[inv_name].iloc[-1])
            elif "기관" in str(inv_name):
                inv_map["institution"] = int(df.loc[inv_name, "순매수"] if "순매수" in df.columns else df.loc[inv_name].iloc[-1])
            elif "개인" in str(inv_name):
                inv_map["individual"] = int(df.loc[inv_name, "순매수"] if "순매수" in df.columns else df.loc[inv_name].iloc[-1])
        result[d]["investors"] = inv_map
        print(f"  parsed: {inv_map}")
    except Exception as e:
        print(f"  투자자 수급 {date_str} error: {e}")

with open("pykrx_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\nSaved to pykrx_data.json")
