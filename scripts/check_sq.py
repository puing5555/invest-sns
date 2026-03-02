import json, os, requests
from dotenv import load_dotenv
load_dotenv('.env.local')

# 1. stockPrices.json
with open('data/stockPrices.json','r',encoding='utf-8') as f:
    sp = json.load(f)
for k in ['SQ','XYZ']:
    if k in sp:
        p = sp[k]
        prices = p.get('prices',[])
        print(f"stockPrices {k}: currentPrice={p.get('currentPrice')}, {len(prices)}일치, {prices[0]['date']}~{prices[-1]['date']}")
    else:
        print(f"stockPrices {k}: 없음")

# 2. DB check
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}
r = requests.get(f"{url}/rest/v1/influencer_signals?select=id,stock,ticker&or=(ticker.eq.SQ,ticker.eq.XYZ)", headers=headers)
data = r.json()
print(f"\nDB signals with SQ or XYZ ticker: {len(data)}")
for s in data:
    print(f"  {s['id'][:8]}... stock={s['stock']} ticker={s['ticker']}")
