import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
h_update = {**h, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

# Get all null ticker signals
r = requests.get(
    'https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?ticker=is.null&select=id,stock,signal',
    headers=h
)
null_signals = r.json()
print(f"Null ticker signals: {len(null_signals)}")

# Classify
delete_ids = []  # sectors/non-stocks
map_fixes = []   # can be mapped to ticker

sectors = ['테크 기업', '조선', '반도체', '바이오 AI 기업', '소프트웨어 섹터', 
           'AI 인프라 섹터', '로봇 섹터', 'HM파마', 'HCM파마', 'SpaceX']

ticker_map = {
    '현대차그룹주': ('005380', 'KR'),
    '마이크로스트라이즈': ('MSTR', 'US'),
    '금': ('GLD', 'US'),
}

for s in null_signals:
    stock = s['stock']
    sid = s['id']
    
    if stock in sectors:
        delete_ids.append(sid)
        print(f"  DELETE: {stock} ({sid[:8]})")
    elif stock in ticker_map:
        tk, mkt = ticker_map[stock]
        map_fixes.append((sid, stock, tk, mkt))
        print(f"  MAP: {stock} -> {tk} ({sid[:8]})")
    else:
        print(f"  UNKNOWN: {stock} ({sid[:8]})")

# Execute deletes
print(f"\n--- Deleting {len(delete_ids)} sector signals ---")
for did in delete_ids:
    r = requests.delete(
        f'https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?id=eq.{did}',
        headers=h_update
    )
    print(f"  DELETE {did[:8]}: {r.status_code}")

# Execute ticker mappings
print(f"\n--- Mapping {len(map_fixes)} tickers ---")
for sid, stock, tk, mkt in map_fixes:
    new_stock = f"{stock} ({tk})"
    r = requests.patch(
        f'https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?id=eq.{sid}',
        headers=h_update,
        json={'ticker': tk, 'market': mkt, 'stock': new_stock}
    )
    print(f"  MAP {sid[:8]} {stock} -> {tk}: {r.status_code}")

print(f"\nDone! Deleted={len(delete_ids)}, Mapped={len(map_fixes)}")
