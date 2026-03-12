# -*- coding: utf-8 -*-
import sys, requests, json, os
sys.stdout.reconfigure(encoding='utf-8')

env = {}
with open('.env.local') as f:
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

key = env.get('SUPABASE_SERVICE_ROLE_KEY', '')
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
SUPA = 'https://arypzhotxflimroprmdk.supabase.co'

ch_id = 'c9c4dc38-c108-4988-b1d2-b177c3b324fc'
r = requests.get(f'{SUPA}/rest/v1/influencer_videos?channel_id=eq.{ch_id}&select=id&limit=100', headers=h)
videos = r.json()
print(f'코린이아빠 비디오 수: {len(videos)}')

video_ids = [v['id'] for v in videos]
sp = json.load(open('public/signal_prices.json', encoding='utf-8'))
sp_uuids = set(k for k in sp if '-' in k and len(k) == 36)

total_sigs = []
for vid_id in video_ids:
    r2 = requests.get(f'{SUPA}/rest/v1/influencer_signals?video_id=eq.{vid_id}&select=id,stock,ticker,signal', headers=h)
    sigs = r2.json()
    total_sigs.extend(sigs)

print(f'코린이아빠 시그널 총: {len(total_sigs)}')
in_sp = [s for s in total_sigs if s['id'] in sp_uuids]
not_in_sp = [s for s in total_sigs if s['id'] not in sp_uuids]
print(f'  signal_prices 있음: {len(in_sp)}')
print(f'  signal_prices 없음: {len(not_in_sp)}')
print()
for s in not_in_sp[:15]:
    print(f'  ❌ {s["id"][:8]}... stock={s["stock"]} ticker={s["ticker"]} signal={s["signal"]}')
for s in in_sp[:5]:
    print(f'  ✅ {s["id"][:8]}... stock={s["stock"]} ticker={s["ticker"]} signal={s["signal"]}')
