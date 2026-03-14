import sys, os, requests
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / '.env.local')

URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json'}

from eval_claude_v11v12 import get_eval_videos, get_ground_truth

videos = get_eval_videos()
print(f'영상 수: {len(videos)}')

for v in videos[:5]:
    gt = get_ground_truth(v['id'])
    print(f"  {v['video_id']} | DB id: {v['id']} | signal_count: {v.get('signal_count','?')} | GT: {len(gt)}건 | {[x.get('signal_type') for x in gt]}")
