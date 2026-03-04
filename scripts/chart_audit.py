import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Mario\work\invest-sns\data\stockPrices.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print(f"Total entries in stockPrices.json: {len(d)}")
empty = [k for k,v in d.items() if not v.get('prices') or len(v['prices'])==0]
print(f"Empty chart data: {len(empty)}")
for k in empty:
    print(f"  {k}: {d[k].get('name','?')}")

# Compare with signal_prices.json
with open(r'C:\Users\Mario\work\invest-sns\data\signal_prices.json', 'r', encoding='utf-8') as f:
    prices = json.load(f)

missing_chart = [k for k in prices if k not in d]
print(f"\nIn signal_prices but missing from stockPrices: {len(missing_chart)}")
for k in sorted(missing_chart)[:30]:
    print(f"  {k}: {prices[k].get('name','?')}")
