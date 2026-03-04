import json, time, re
import yfinance as yf

PRICES_PATH = r'C:\Users\Mario\work\invest-sns\data\signal_prices.json'
with open(PRICES_PATH, 'r', encoding='utf-8') as f:
    prices = json.load(f)

today = "2026-03-04"

# Add missing tickers
for ticker, name, market, currency in [
    ("SQ", "블록(스퀘어)", "US", "USD"),
    ("IXIC", "나스닥", "US", "USD"),
]:
    symbols = [ticker] if ticker != "IXIC" else ["^IXIC"]
    for sym in symbols:
        try:
            d = yf.Ticker(sym)
            h = d.history(period='5d')
            if not h.empty:
                p = round(float(h['Close'].iloc[-1]), 2)
                prices[ticker] = {
                    'name': name, 'ticker': ticker, 'market': market,
                    'current_price': p, 'currency': currency, 'last_updated': today
                }
                print(f"✅ Added {ticker}: {p}")
                break
        except Exception as e:
            print(f"❌ {ticker} ({sym}): {e}")

# Refresh all prices in batches
all_tickers = list(prices.keys())
updated = 0
failed = []

for i in range(0, len(all_tickers), 10):
    batch = all_tickers[i:i+10]
    for t in batch:
        m = prices[t].get('market', '')
        if m == 'KR':
            syms = [f"{t}.KS", f"{t}.KQ"]
        elif m == 'HK':
            syms = [t if t.endswith('.HK') else f"{t}.HK"]
        elif m in ('CRYPTO', 'CRYPTO_DEFI'):
            syms = [f"{t}-USD"]
        elif t == 'IXIC':
            syms = ['^IXIC']
        else:
            syms = [t]
        
        for sym in syms:
            try:
                d = yf.Ticker(sym)
                h = d.history(period='5d')
                if not h.empty:
                    p = round(float(h['Close'].iloc[-1]), 2)
                    if p > 0:
                        prices[t]['current_price'] = int(p) if m == 'KR' else p
                        prices[t]['last_updated'] = today
                        updated += 1
                        break
            except:
                continue
        else:
            failed.append(t)
    
    pct = min(100, (i+10)*100//len(all_tickers))
    print(f"Progress: {pct}% ({i+10}/{len(all_tickers)})")
    if i + 10 < len(all_tickers):
        time.sleep(1)

# Save
with open(PRICES_PATH, 'w', encoding='utf-8') as f:
    json.dump(prices, f, ensure_ascii=False, indent=2)

print(f"\n=== DONE ===")
print(f"Total: {len(prices)}")
print(f"Updated: {updated}")
print(f"Failed: {len(failed)}")
if failed:
    for t in failed:
        print(f"  ❌ {t}: {prices[t].get('name','?')}")

# Zero price check
zeros = [k for k, v in prices.items() if not v.get('current_price')]
print(f"Zero price entries: {len(zeros)}")
for z in zeros:
    print(f"  {z}: {prices[z].get('name','?')}")

# Save audit report
kr = len([k for k,v in prices.items() if v.get('market')=='KR'])
us = len([k for k,v in prices.items() if v.get('market')=='US'])
ot = len(prices) - kr - us

report = f"""# Price Audit Report - {today}

## Summary
- Total entries: {len(prices)}
- KR stocks: {kr}
- US stocks: {us}  
- Other (HK/Crypto/ETF): {ot}
- Prices refreshed: {updated}
- Failed to fetch: {len(failed)}
- Zero price entries: {len(zeros)}

## Failed Tickers
"""
for t in failed:
    report += f"- {t}: {prices[t].get('name','?')}\n"

report += "\n## Zero Price Tickers\n"
for z in zeros:
    report += f"- {z}: {prices[z].get('name','?')}\n"

with open(r'C:\Users\Mario\work\invest-sns\data\price_audit_report.md', 'w', encoding='utf-8') as f:
    f.write(report)
print("\nAudit report saved")
