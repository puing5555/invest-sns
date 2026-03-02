import os, requests, re
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
skey = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', key)
headers = {'apikey': skey, 'Authorization': f'Bearer {skey}', 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}

# Get all signals
r = requests.get(f"{url}/rest/v1/influencer_signals?select=id,stock,ticker&limit=200",
                 headers={'apikey': key, 'Authorization': f'Bearer {key}'})
data = r.json()

updates = []
for s in data:
    stock = s.get('stock','')
    new_stock = stock
    
    # Remove parenthesized ticker from stock name: "현대차 (005380)" -> "현대차"
    new_stock = re.sub(r'\s*\([^)]+\)\s*$', '', new_stock).strip()
    
    # 현대차그룹주 -> 현대차
    if new_stock == '현대차그룹주':
        new_stock = '현대차'
    
    # 반도체 섹터 -> TSMC (for TSM ticker)
    if new_stock == '반도체 섹터':
        new_stock = 'TSMC'
    
    if new_stock != stock:
        updates.append((s['id'], stock, new_stock))

print(f"Updates needed: {len(updates)}")
for uid, old, new in updates[:10]:
    print(f"  {uid[:8]}: '{old}' -> '{new}'")
if len(updates) > 10:
    print(f"  ... and {len(updates)-10} more")

# Apply updates automatically
success = 0
for uid, old, new in updates:
    r = requests.patch(f"{url}/rest/v1/influencer_signals?id=eq.{uid}",
                      headers=headers, json={'stock': new})
    if r.status_code < 300:
        success += 1
    else:
        print(f"  FAIL {uid[:8]}: {r.status_code} {r.text}")
print(f"\nDone! {success}/{len(updates)} updated")
