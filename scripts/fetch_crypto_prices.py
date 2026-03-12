#!/usr/bin/env python3
"""코인 yfinance + CoinGecko 가격 수집 → signal_prices.json 업데이트"""
import json, time, urllib.request
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
}

# yfinance 미지원 코인 → CoinGecko ID 매핑
COINGECKO_TICKERS = {
    'CNTN-USD': ('canton-network', '캔톤코인'),
    'PENGU-USD': ('pudgy-penguins', '퍼지펭귄'),
}

def fetch_coingecko(cg_id):
    """CoinGecko API로 현재가 조회 (USD)"""
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get(cg_id, {}).get('usd')
    except Exception as e:
        print(f"  CoinGecko {cg_id} 실패: {e}")
        return None

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

# CoinGecko 미지원 코인 수집
for yf_ticker, (cg_id, name) in COINGECKO_TICKERS.items():
    print(f"CoinGecko: {yf_ticker} ({cg_id})...")
    price = fetch_coingecko(cg_id)
    if price:
        data[yf_ticker] = {
            'name': name,
            'ticker': yf_ticker,
            'market': 'CRYPTO',
            'current_price': round(price, 6),
            'currency': 'USD',
            'last_updated': today,
            'source': 'coingecko'
        }
        print(f"  {yf_ticker}: ${price}")
    else:
        # CoinGecko도 실패 시 '가격정보없음' 마커 저장
        data[yf_ticker] = {
            'name': name,
            'ticker': yf_ticker,
            'market': 'CRYPTO',
            'current_price': None,
            'currency': 'USD',
            'last_updated': today,
            'note': '가격정보없음'
        }
        print(f"  {yf_ticker}: 가격정보없음")
    time.sleep(3)

PRICES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n완료. yfinance {len(CRYPTO_TICKERS)}개 + CoinGecko {len(COINGECKO_TICKERS)}개 업데이트")
