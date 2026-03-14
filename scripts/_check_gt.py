import os, requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / '.env.local')

SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
h = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Accept': 'application/json'}

# 영상 1개
r = requests.get(f'{SUPABASE_URL}/rest/v1/influencer_videos?select=id,video_id,title&signal_count=gt.0&subtitle_text=not.is.null&limit=1', headers=h)
v = r.json()[0]
db_id = v['id']
print(f"DB id: {db_id}")
print(f"video_id: {v['video_id']}")

# GT 쿼리 - UUID 기준
r2 = requests.get(
    f'{SUPABASE_URL}/rest/v1/influencer_signals?select=stock,signal_type,video_id&video_id=eq.{db_id}',
    headers=h
)
result2 = r2.json()
print(f"UUID 기준 GT 건수: {len(result2)}")
if result2:
    print(f"샘플: {result2[0]}")

# signals 컬럼 확인
r3 = requests.get(f'{SUPABASE_URL}/rest/v1/influencer_signals?select=*&limit=1', headers=h)
data3 = r3.json()
if data3:
    cols = list(data3[0].keys())
    print(f"\nsignals 컬럼: {cols}")
    print(f"video_id 값 예시: {data3[0].get('video_id')}")
else:
    print("signals 테이블 조회 실패")
    print(f"응답: {r3.text[:200]}")
