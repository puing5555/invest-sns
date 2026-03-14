# -*- coding: utf-8 -*-
import sys, json, os, requests
from pathlib import Path
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / '.env.local')
SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
SB_H = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Accept': 'application/json'}

r = requests.get(f'{SUPABASE_URL}/rest/v1/influencer_videos?select=id,video_id,title,signal_count&video_id=eq.IjYr0FrINis', headers=SB_H)
v = r.json()[0]
print('Video:', json.dumps(v, ensure_ascii=False))

vid = v['id']
r2 = requests.get(f'{SUPABASE_URL}/rest/v1/influencer_signals?select=stock,ticker,signal_type&video_id=eq.{vid}', headers=SB_H)
signals = r2.json()
print(f'Signal type: {type(signals).__name__}')
print(f'Signals: {json.dumps(signals, ensure_ascii=False, indent=2)[:1000]}')
