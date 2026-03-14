# -*- coding: utf-8 -*-
import os, sys, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

BASE = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json'}

r = requests.get(
    f'{BASE}/rest/v1/influencer_videos'
    f'?select=video_id,title,subtitle_text,signal_count'
    f'&signal_count=gt.0&subtitle_text=not.is.null&subtitle_text=neq.'
    f'&order=published_at.desc&limit=100',
    headers=H
)
videos = r.json()
clean, garbled = 0, 0
for v in videos:
    st = v.get('subtitle_text', '')
    q_ratio = st.count('?') / max(len(st), 1)
    has_kor = any('\uac00' <= c <= '\ud7a3' for c in st[:500])
    if q_ratio > 0.1 or (not has_kor and len(st) > 100):
        garbled += 1
        print(f'[깨짐] {v["video_id"]} | ?율={q_ratio:.0%} | 한글={has_kor} | {v["title"][:45]}')
    else:
        clean += 1
print(f'\n총 {len(videos)}개: 정상={clean}, 깨짐={garbled}')
