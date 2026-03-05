# -*- coding: utf-8 -*-
import requests, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

r = requests.get(f'{url}/rest/v1/speakers?select=id,name', headers=headers)
speakers = r.json()
print(f'Total speakers: {len(speakers)}')
print(type(speakers), speakers[:2] if isinstance(speakers, list) else speakers)

# Known slugs from speakerSlugs.ts
KNOWN = {
    '이효석', '조진표', '코린이아빠', '코린이 아빠', '박지훈', '배재원',
    '김동훈', '김장년', '고연수', '이건희', '장우진', '김장열',
    '박병창', '박명성', '달란트투자', 'syuka', '이영수', '이정윤',
    '배재규', '배제기', '김학주', '세상학개론', '월가아재'
}

missing = []
for s in sorted(speakers, key=lambda x: x['name']):
    status = '✅' if s['name'] in KNOWN else '❌ MISSING'
    print(f"  {status} {s['name']}")
    if s['name'] not in KNOWN:
        missing.append(s['name'])

print(f"\nMissing: {len(missing)}")
for m in missing:
    print(f"  '{m}'")
