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

# 코린이아빠 channel 찾기
r = requests.get(f'{SUPA}/rest/v1/influencer_channels?slug=eq.korini-appa&select=id,channel_name,slug', headers=h)
channels = r.json()
print(f'코린이아빠 채널: {channels}')

if not channels:
    # slug 패턴 검색
    r = requests.get(f'{SUPA}/rest/v1/influencer_channels?slug=ilike.*korini*&select=id,channel_name,slug', headers=h)
    channels = r.json()
    print(f'korini 포함 채널: {channels}')

if not channels:
    r = requests.get(f'{SUPA}/rest/v1/influencer_channels?channel_name=ilike.*코린*&select=id,channel_name,slug', headers=h)
    channels = r.json()
    print(f'코린 포함 채널: {channels}')

if channels:
    ch_id = channels[0]['id']
    # 해당 채널의 비디오 가져오기
    r2 = requests.get(f'{SUPA}/rest/v1/influencer_videos?channel_id=eq.{ch_id}&select=id&limit=100', headers=h)
    videos = r2.json()
    print(f'코린이아빠 비디오 수: {len(videos)}')
    
    video_ids = [v['id'] for v in videos]
    if video_ids:
        # 시그널 가져오기
        vid_filter = ','.join(video_ids[:10])
        r3 = requests.get(f'{SUPA}/rest/v1/influencer_signals?video_id=in.({vid_filter})&select=id,stock,ticker,signal&limit=50', headers=h)
        sigs = r3.json()
        print(f'코린이아빠 시그널 (첫 10개 비디오): {len(sigs)}개')
        
        # signal_prices.json에 있는지 확인
        sp = json.load(open('public/signal_prices.json', encoding='utf-8'))
        for s in sigs[:5]:
            in_sp = '✅' if s['id'] in sp else '❌'
            print(f'  {s["id"][:8]}... stock={s["stock"]} ticker={s["ticker"]} | sp={in_sp}')
