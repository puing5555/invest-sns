import sys, io, os, requests, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')
URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

# Get existing video and speaker IDs to test
r = requests.get(f"{URL}/rest/v1/influencer_signals?select=video_id,speaker_id,signal,mention_type,market&limit=1", headers=H)
existing = r.json()[0]
print("Existing signal example:", json.dumps(existing, ensure_ascii=False))

# Try insert with exact same pattern
vid_id = '2bacfb7b-a6fe-4b4e-af81-c87cbe8a231b'  # wsaj video
spk_id = 'a80f6cdf-e53a-42a9-95ea-1c5ba9c7a986'  # wsaj speaker

r = requests.post(f"{URL}/rest/v1/influencer_signals", headers=H, json={
    'video_id': vid_id,
    'speaker_id': spk_id,
    'stock': '엔비디아',
    'ticker': 'NVDA',
    'market': 'US',
    'mention_type': '결론',
    'signal': '긍정',
    'confidence': 7,
    'timestamp': '08:45',
    'key_quote': '재고자산 조정이 현재 시점에서는 거의 끝난 상태',
    'reasoning': 'ARM 인수 실패 비용 해결로 이익률 회복 전망',
    'review_status': 'pending',
    'pipeline_version': 'v10'
})
print(f"\nInsert status: {r.status_code}")
print(f"Response: {r.text[:500]}")
