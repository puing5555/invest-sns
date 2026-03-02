"""새 시그널에 대한 가격 업데이트 + public 동기화"""
import json, requests
import yfinance as yf
from datetime import datetime

URL='https://arypzhotxflimroprmdk.supabase.co'
KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
H={'apikey':KEY,'Authorization':'Bearer '+KEY}

# Get all signal IDs from Supabase
print('Fetching signals from Supabase...', flush=True)
r=requests.get(URL+'/rest/v1/influencer_signals?select=id&limit=1000',headers=H,timeout=15)
db_ids=set(s['id'] for s in r.json())
print(f'DB signals: {len(db_ids)}', flush=True)

# Load current prices
prices=json.load(open('data/signal_prices.json','r',encoding='utf-8'))
existing_ids=set(prices.keys())
print(f'Existing prices: {len(existing_ids)}', flush=True)

# Find missing
missing=db_ids-existing_ids
print(f'Missing: {len(missing)}', flush=True)

if missing:
    # For now, add placeholder prices (will be updated later with real data)
    for sid in missing:
        prices[sid]={'price_at_signal':None,'price_current':None,'return_pct':None}
    print(f'Added {len(missing)} placeholders', flush=True)

# Save
json.dump(prices,open('data/signal_prices.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
json.dump(prices,open('public/signal_prices.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(f'Saved: {len(prices)} entries (data + public synced)', flush=True)
