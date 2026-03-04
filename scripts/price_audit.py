import json, os, sys

# 1. Load signal_prices.json
with open(r'C:\Users\Mario\work\invest-sns\data\signal_prices.json', 'r', encoding='utf-8') as f:
    prices = json.load(f)

print(f"Total tickers in signal_prices.json: {len(prices)}")

zeros = []
valid = []
for k, v in prices.items():
    p = v.get('current_price', 0)
    if not p or p == 0:
        zeros.append((k, v.get('name', '?'), v.get('market', '?')))
    else:
        valid.append((k, v.get('name', '?'), v.get('market', '?'), p))

print(f"Valid prices: {len(valid)}")
print(f"Zero/null/missing: {len(zeros)}")

if zeros:
    print("\n=== Zero/null price tickers ===")
    for t, n, m in zeros:
        print(f"  {t}: {n} ({m})")

# Classify
kr = [k for k,v in prices.items() if v.get('market') == 'KR']
us = [k for k,v in prices.items() if v.get('market') == 'US']
other = [k for k,v in prices.items() if v.get('market') not in ('KR', 'US')]
print(f"\nKR: {len(kr)}, US: {len(us)}, Other: {len(other)}")
if other:
    for k in other:
        print(f"  Other: {k} -> {prices[k].get('market')}")
