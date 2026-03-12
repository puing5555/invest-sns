# -*- coding: utf-8 -*-
import sys, requests, json
sys.stdout.reconfigure(encoding='utf-8')

env = {}
with open('.env.local') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

key = env.get('SUPABASE_SERVICE_ROLE_KEY', '')
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
SUPA = 'https://arypzhotxflimroprmdk.supabase.co'

# 코린이아빠 시그널 전체 가져오기 (영상 발행일 포함)
r = requests.get(
    f'{SUPA}/rest/v1/influencer_signals'
    f'?select=id,stock,ticker,signal,'
    f'influencer_videos!inner(published_at,channel_id,influencer_channels!inner(channel_name))'
    f'&influencer_videos.influencer_channels.channel_name=eq.코린이 아빠'
    f'&limit=100',
    headers=h
)
sigs = r.json()
print(f'코린이아빠 시그널 수: {len(sigs)}')

sp = json.load(open('public/signal_prices.json', encoding='utf-8'))

missing_from_sp = []
in_sp = []
for s in sigs:
    if s['id'] in sp:
        in_sp.append(s)
    else:
        missing_from_sp.append(s)

print(f'  signal_prices 있음: {len(in_sp)}')
print(f'  signal_prices 없음: {len(missing_from_sp)}')
print()
print('=== 누락 시그널 ===')
for s in missing_from_sp:
    pub = s.get('influencer_videos', {}).get('published_at', 'N/A')[:10] if s.get('influencer_videos') else 'N/A'
    print(f'  {s["id"][:8]}... stock={s["stock"]} ticker={s["ticker"]} signal={s["signal"]} pub={pub}')

print()
print('=== 있는 시그널 샘플 ===')
for s in in_sp[:3]:
    pd = sp[s['id']]
    print(f'  ✅ {s["id"][:8]}... stock={s["stock"]} ticker={s["ticker"]} return={pd.get("return_pct")}%')
