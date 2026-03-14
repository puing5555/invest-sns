# -*- coding: utf-8 -*-
import os, sys, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

BASE = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json', 'Prefer': 'count=exact'}

# subtitle_text 있는 영상 수
r1 = requests.get(f'{BASE}/rest/v1/influencer_videos?select=id&subtitle_text=not.is.null&subtitle_text=neq.', headers={**H, 'Range': '0-0'})
has_sub = r1.headers.get('content-range','?').split('/')[-1]

r2 = requests.get(f'{BASE}/rest/v1/influencer_videos?select=id', headers={**H, 'Range': '0-0'})
total = r2.headers.get('content-range','?').split('/')[-1]

# signal_count > 0 + subtitle_text 있는 영상
r3 = requests.get(f'{BASE}/rest/v1/influencer_videos?select=id&signal_count=gt.0&subtitle_text=not.is.null&subtitle_text=neq.', headers={**H, 'Range': '0-0'})
has_both = r3.headers.get('content-range','?').split('/')[-1]

print(f'전체 영상:               {total}')
print(f'subtitle_text 있음:      {has_sub}')
print(f'시그널+자막 모두 있음:    {has_both}')

# 샘플 1개 확인
r4 = requests.get(f'{BASE}/rest/v1/influencer_videos?select=video_id,title,signal_count,subtitle_text&signal_count=gt.0&subtitle_text=not.is.null&subtitle_text=neq.&limit=1', headers=H)
rows = r4.json()
if rows:
    v = rows[0]
    st = v.get('subtitle_text','') or ''
    print(f'\n샘플: {v["video_id"]} | signal={v["signal_count"]} | subtitle 길이={len(st)}자')
    print(f'자막 앞 200자: {st[:200]}')
