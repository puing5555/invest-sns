import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Mario\work\invest-sns\data\signal_prices.json','r',encoding='utf-8') as f:
    sp = json.load(f)
with open(r'C:\Users\Mario\work\invest-sns\data\stockPrices.json','r',encoding='utf-8') as f:
    cp = json.load(f)

missing_chart = [k for k in sp if k not in cp]
zero_price = [k for k,v in sp.items() if not v.get('current_price')]
print(f"signal_prices: {len(sp)} entries, {len(zero_price)} zero price")
print(f"stockPrices: {len(cp)} entries")
print(f"Missing chart data: {len(missing_chart)}")
for k in missing_chart:
    name = sp[k].get('name', '?')
    print(f"  {k}: {name}")
