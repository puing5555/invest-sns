import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
cid = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1'

r = requests.get(
    f'https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_videos?channel_id=eq.{cid}&select=id,title,published_at,video_id&order=published_at.desc.nullslast&limit=200',
    headers=h
)
vids = r.json()
if isinstance(vids, dict):
    print("Error:", vids)
    sys.exit(1)
total = len(vids)
membership = [v for v in vids if '멤버십' in (v.get('title') or '')]
normal = [v for v in vids if '멤버십' not in (v.get('title') or '')]
with_date = [v for v in normal if v.get('published_at')]
no_date = [v for v in normal if not v.get('published_at')]

print(f"Total: {total}")
print(f"Membership (excluded): {len(membership)}")
print(f"Normal: {len(normal)}")
print(f"  With date: {len(with_date)}")
print(f"  Without date: {len(no_date)}")

if with_date:
    print(f"\nLatest: {with_date[0]['published_at']} | {with_date[0]['title'][:60]}")
    print(f"Earliest: {with_date[-1]['published_at']} | {with_date[-1]['title'][:60]}")

print("\n--- All normal videos ---")
for v in normal:
    pa = v.get('published_at', 'NO-DATE')
    vid = v.get('video_id', '?')
    print(f"  {pa} | {v['title'][:60]} | {vid}")
