import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
h = {'apikey': key, 'Authorization': f'Bearer {key}'}

video_ids = ['Ke7gQMbIFLI', '4wCO1fdl9iU', '4cCGQFHrbK4']

for vid in video_ids:
    r = requests.get(f'{url}/rest/v1/influencer_videos?video_id=eq.{vid}&select=id,title,subtitle_text', headers=h)
    v = r.json()[0] if r.json() else None
    if not v:
        print(f"[MISSING] {vid}")
        continue
    has_sub = bool(v.get('subtitle_text'))
    sub_len = len(v.get('subtitle_text') or '')
    print(f"[{vid}] {v['title'][:60]} | subtitle: {has_sub} ({sub_len} chars) | uuid: {v['id']}")
    
    r2 = requests.get(f'{url}/rest/v1/influencer_signals?video_id=eq.{v["id"]}&select=*', headers=h)
    signals = r2.json()
    print(f"  Signals: {len(signals)}")
    if signals:
        print(f"  Raw: {json.dumps(signals[0], ensure_ascii=False)[:200]}")
