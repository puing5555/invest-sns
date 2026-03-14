import sys, os, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / '.env.local')

URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json', 'Prefer': 'count=exact'}

# 자막 있는 영상 수
r1 = requests.get(f'{URL}/rest/v1/influencer_videos?select=id&subtitle_text=not.is.null&limit=1', headers=H)
print(f"자막 있는 영상 (not null): Content-Range={r1.headers.get('Content-Range','?')}")

# 자막 + has_subtitle 영상
r2 = requests.get(f'{URL}/rest/v1/influencer_videos?select=id&has_subtitle=eq.true&limit=1', headers=H)
print(f"has_subtitle=true 영상: Content-Range={r2.headers.get('Content-Range','?')}")

# signal_count > 0 영상
r3 = requests.get(f'{URL}/rest/v1/influencer_videos?select=id&signal_count=gt.0&limit=1', headers=H)
print(f"signal_count>0 영상: Content-Range={r3.headers.get('Content-Range','?')}")

# 둘 다 만족
r4 = requests.get(f'{URL}/rest/v1/influencer_videos?select=id&signal_count=gt.0&subtitle_text=not.is.null&limit=1', headers=H)
print(f"자막+시그널 모두: Content-Range={r4.headers.get('Content-Range','?')}")
