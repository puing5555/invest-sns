import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / '.env.local')

URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json'}

# 1. influencer_videos 컬럼 확인
r = requests.get(f'{URL}/rest/v1/influencer_videos?select=*&limit=1', headers=H)
v = r.json()
if isinstance(v, list) and v:
    print("videos 컬럼:", list(v[0].keys()))
    print("signal_count 값:", v[0].get('signal_count'))

# 2. signal_count 필터 확인
r2 = requests.get(f'{URL}/rest/v1/influencer_videos?select=id,video_id&signal_count=gt.0&limit=3', headers=H)
print(f"\nsignal_count>0 영상 수 (limit 3): {r2.json() if isinstance(r2.json(), list) else r2.json()}")

# 3. subtitle_text 조건
r3 = requests.get(
    f'{URL}/rest/v1/influencer_videos?select=id,video_id,signal_count'
    f'&signal_count=gt.0&subtitle_text=not.is.null&subtitle_text=neq.&limit=5',
    headers=H
)
data3 = r3.json()
print(f"\n자막+시그널 영상: {len(data3) if isinstance(data3, list) else data3}")

# 4. 첫 번째 영상의 GT 직접 조회
if isinstance(data3, list) and data3:
    vid_id = data3[0]['id']
    r4 = requests.get(f'{URL}/rest/v1/influencer_signals?select=stock,signal&video_id=eq.{vid_id}&limit=3', headers=H)
    print(f"\n영상 {vid_id} GT: {r4.json()}")
