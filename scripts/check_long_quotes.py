import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
r = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=id,stock,ticker,signal,key_quote,speaker_id', headers=h)
data = r.json()
total = len(data)
long = [d for d in data if d.get('key_quote') and len(d['key_quote']) > 200]
long.sort(key=lambda x: len(x['key_quote']), reverse=True)

print(f'Total signals: {total}')
print(f'key_quote > 200자: {len(long)}개 ({len(long)/total*100:.0f}%)')
print()

for i, d in enumerate(long):
    kq = d['key_quote']
    sid = d['id'][:8]
    print(f"{i+1}. [{sid}] {d['stock']} | {len(kq)}자")
    print(f"   {kq[:120]}...")
    print()
