import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, re

sp = json.load(open('data/signal_prices.json', 'r', encoding='utf-8'))
uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

clean = {}
removed = 0
for k, v in sp.items():
    if uuid_pattern.match(k):
        removed += 1
    else:
        clean[k] = v

print(f"Original keys: {len(sp)}")
print(f"UUID keys removed: {removed}")
print(f"Clean keys: {len(clean)}")
print(f"\nRemaining keys:")
for k in sorted(clean.keys()):
    price = clean[k].get('current_price') or clean[k].get('currentPrice', '?')
    print(f"  {k}: {price}")

json.dump(clean, open('data/signal_prices.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\nSaved!")
