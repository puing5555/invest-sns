# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd

def fetch_price_pykrx(ticker, start="2023-01-01", end="2026-03-07"):
    try:
        from pykrx import stock
        df = stock.get_market_ohlcv_by_date(
            start.replace('-', ''), end.replace('-', ''), ticker
        )
        if df is not None and not df.empty:
            df.index = pd.to_datetime(df.index)
            print(f"pykrx 성공: {len(df)}행, 컬럼={df.columns.tolist()}")
            return df
        print("pykrx 빈 결과")
    except Exception as e:
        print(f"pykrx 실패: {e}")
    return None

def fetch_price_yfinance(ticker, start="2023-01-01", end="2026-03-07"):
    try:
        import yfinance as yf
        yt = f"{ticker}.KS"
        df = yf.download(yt, start=start, end=end, auto_adjust=True, progress=False)
        if df is not None and not df.empty:
            print(f"yfinance 성공: {len(df)}행, 컬럼={df.columns.tolist()}")
            return df
        print("yfinance 빈 결과")
    except Exception as e:
        print(f"yfinance 실패: {e}")
    return None

print("=== pykrx 테스트 ===")
df = fetch_price_pykrx('005930')
if df is not None:
    print(df.tail(2))

print("\n=== yfinance 테스트 ===")
df2 = fetch_price_yfinance('005930')
if df2 is not None:
    print(df2.tail(2))
