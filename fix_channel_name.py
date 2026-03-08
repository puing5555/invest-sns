"""채널명 GODofIT → Godofit 수정 스크립트"""
import os
import sys
import requests
from dotenv import load_dotenv
from pathlib import Path

# .env.local 로드
env_path = Path(__file__).parent / '.env.local'
load_dotenv(env_path)

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SERVICE_KEY:
    print("❌ 환경 변수 누락")
    sys.exit(1)

HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

# PATCH 채널명 수정
print("채널명 수정 중...")
resp = requests.patch(
    f'{SUPABASE_URL}/rest/v1/influencer_channels?id=eq.{CHANNEL_ID}',
    headers=HEADERS,
    json={'channel_name': 'Godofit'}
)
print(f"PATCH status: {resp.status_code}")
if resp.status_code in (200, 204):
    print("✅ 채널명 수정 성공")
else:
    print(f"❌ 실패: {resp.text}")
    sys.exit(1)

# GET으로 확인
resp2 = requests.get(
    f'{SUPABASE_URL}/rest/v1/influencer_channels?id=eq.{CHANNEL_ID}&select=id,channel_name,channel_handle',
    headers=HEADERS
)
data = resp2.json()
print(f"✅ 확인: {data}")
