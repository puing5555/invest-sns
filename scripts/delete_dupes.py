import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key, 'Prefer': 'return=representation'}

delete_ids = [
    'a9a7da5c-a50b-42b7-b072-83eeb3311b3d',  # Rocket Lab (no ticker)
    '332a5809-ad05-4697-89f2-1a8e2f6cb359',  # SMR/원전 (no ticker)
    'e33133c1-cd42-4a51-975e-f092c50f3f46',  # 반도체 (non-stock)
    '87f3fa04-503b-4cb5-9000-ee39bd0ce907',  # 빅테크 (non-stock)
]

for did in delete_ids:
    r = requests.delete(
        f'https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?id=eq.{did}',
        headers=h
    )
    print(f"DELETE {did[:8]}: {r.status_code}")
