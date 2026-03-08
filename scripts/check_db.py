import json, urllib.request

env = {}
with open('C:/Users/Mario/work/invest-sns/.env.local', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#') and line:
            k, v = line.split('=', 1)
            env[k] = v

service_key = env['SUPABASE_SERVICE_ROLE_KEY']
supabase_url = env['NEXT_PUBLIC_SUPABASE_URL']

url = f'{supabase_url}/rest/v1/analyst_reports?select=id,ticker,firm,title,published_at,ai_summary&limit=600'
req = urllib.request.Request(url, headers={'apikey': service_key, 'Authorization': f'Bearer {service_key}'})
res = urllib.request.urlopen(req)
db_records = json.loads(res.read().decode('utf-8'))
print(f'DB 레코드 수: {len(db_records)}')

has_ai = sum(1 for r in db_records if r.get('ai_summary') and len(str(r.get('ai_summary', ''))) > 10)
print(f'ai_summary 있음: {has_ai} | 없음: {len(db_records) - has_ai}')

for r in db_records[:2]:
    title_preview = str(r.get('title', ''))[:30]
    has_sum = bool(r.get('ai_summary'))
    print(f"  ticker={r['ticker']} | title={title_preview} | ai_summary={has_sum}")
