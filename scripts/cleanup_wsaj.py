import urllib.request, json

SUPA_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPA_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'

wsaj_ids = [
    'e175d337-d659-447f-ba26-07ae10949ac3',
    'ce6e9583-ca2a-49a8-a25d-004a554996a1',
    'fd048f32-58d9-4760-90f5-d948b2f27e76',
    'e4216a2e-3159-4afc-8ca0-d13128e492bf'
]

for vid_id in wsaj_ids:
    req = urllib.request.Request(
        f'{SUPA_URL}/rest/v1/influencer_videos?id=eq.{vid_id}',
        headers={'apikey': SUPA_KEY, 'Authorization': f'Bearer {SUPA_KEY}'},
        method='DELETE'
    )
    try:
        with urllib.request.urlopen(req) as r:
            print(f'deleted video {vid_id[:8]}... status={r.status}')
    except Exception as e:
        print(f'error {vid_id[:8]}: {e}')

print('wsaj_ cleanup done')
