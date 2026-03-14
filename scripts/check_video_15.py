# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv('.env.local')
import os, requests
BASE = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json'}
r = requests.get(f'{BASE}/rest/v1/influencer_videos?select=video_id,title,subtitle_text,signal_count&signal_count=gt.0&subtitle_text=not.is.null&subtitle_text=neq.&order=published_at.desc&limit=20', headers=H)
videos = r.json()
for i, v in enumerate(videos, 1):
    st = v.get('subtitle_text','')
    print(f'{i:2}. {v["video_id"]:<15} | sig={v["signal_count"]:2} | sub_len={len(st):<7} | {v["title"][:50]}')
