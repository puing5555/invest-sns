#!/usr/bin/env python3
"""코인 yfinance 가격 수집 → signal_prices.json 업데이트"""
import json, time
from pathlib import Path
from datetime import datetime
import yfinance as yf

CRYPTO_TICKERS = {
    'BTC-USD': '비트코인',
    'ETH-USD': '이더리움',
    'XRP-USD': '리플',
    'SOL-USD': '솔라나',
    'LINK-USD': '체인링크',
    'DOGE-USD': '도지코인',
    # CNTN-USD는 yfinance에 없으므로 스킵
}

PRICES_FILE = Path(__file__).parent.parent / 'data' / 'signal_prices.json'

data = json.loads(PRICES_FILE.read_text(encoding='utf-8'))
today = datetime.now().strftime('%Y-%m-%d')

for yf_ticker, name in CRYPTO_TICKERS.items():
    try:
        t = yf.Ticker(yf_ticker)
        info = t.fast_info
        current_price = float(info.last_price)

        data[yf_ticker] = {
            'name': name,
            'ticker': yf_ticker,
            'market': 'CRYPTO',
            'current_price': round(current_price, 4),
            'currency': 'USD',
            'last_updated': today
        }
        print(f"  {yf_ticker}: ${current_price:.4f}")
        time.sleep(1)
    except Exception as e:
        print(f"  {yf_ticker} 실패: {e}")

PRICES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n완료. {len(CRYPTO_TICKERS)}개 코인 현재가 업데이트")
