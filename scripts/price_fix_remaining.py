import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
import yfinance as yf

PRICES_PATH = r'C:\Users\Mario\work\invest-sns\data\signal_prices.json'
with open(PRICES_PATH, 'r', encoding='utf-8') as f:
    prices = json.load(f)

today = "2026-03-04"
fixes = [
    ("284620", ["284620.KQ"], "KR", "KRW"),  # 아이덴 - KOSDAQ
    ("BRK.A", ["BRK-A"], "US", "USD"),  # Berkshire - yfinance uses BRK-A
    ("KS11", ["^KS11"], "US", "KRW"),  # KOSPI index
    ("RIOT", ["RIOT"], "US", "USD"),  # Riot Platforms
    ("SQ", ["XYZ"], "US", "USD"),  # Block renamed ticker to XYZ
]

for ticker, syms, market, currency in fixes:
    for sym in syms:
        try:
            d = yf.Ticker(sym)
            h = d.history(period='5d')
            if not h.empty:
                p = round(float(h['Close'].iloc[-1]), 2)
                if p > 0:
                    if ticker in prices:
                        prices[ticker]['current_price'] = int(p) if market == 'KR' else p
                        prices[ticker]['last_updated'] = today
                    else:
                        prices[ticker] = {
                            'name': prices.get(ticker, {}).get('name', ticker),
                            'ticker': ticker, 'market': market,
                            'current_price': int(p) if market == 'KR' else p,
                            'currency': currency, 'last_updated': today
                        }
                    print(f"OK {ticker} ({sym}): {p}")
                    break
        except Exception as e:
            print(f"FAIL {ticker} ({sym}): {e}")

# Also add SQ as XYZ if needed
if 'SQ' not in prices or not prices.get('SQ', {}).get('current_price'):
    print("SQ ticker may have changed to XYZ - skipping")

with open(PRICES_PATH, 'w', encoding='utf-8') as f:
    json.dump(prices, f, ensure_ascii=False, indent=2)

# Final check
zeros = [k for k, v in prices.items() if not v.get('current_price')]
print(f"\nTotal: {len(prices)}, Zero price: {len(zeros)}")
for z in zeros:
    print(f"  {z}: {prices[z].get('name','?')}")
