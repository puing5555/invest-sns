"""Debug timestamp matching"""
import sys, io, os, re, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
h = {'apikey': key, 'Authorization': f'Bearer {key}'}

r = requests.get(url + '/rest/v1/influencer_signals?select=id,key_quote,timestamp,video_id,influencer_videos(video_id,subtitle_text,title)&limit=200', headers=h)
signals = r.json()

# Categorize
no_sub = 0
has_sub_no_match = 0
has_sub_match = 0

for s in signals:
    vi = s.get('influencer_videos') or {}
    sub = vi.get('subtitle_text') or ''
    kq = (s.get('key_quote') or '').strip()
    
    if not sub:
        no_sub += 1
        continue
    
    if not kq:
        has_sub_no_match += 1
        continue
    
    # Check if ANY part of key_quote appears in subtitle
    found = False
    for length in [40, 20, 10]:
        fragment = kq[:length]
        if fragment in sub:
            found = True
            break
    
    if found:
        has_sub_match += 1
    else:
        has_sub_no_match += 1
        # Show why it doesn't match
        if has_sub_no_match <= 5:
            print(f"\nNO MATCH: ts={s['timestamp']}")
            print(f"  quote: {kq[:80]}")
            print(f"  sub start: {sub[:150]}")
            # Check if subtitle is for a different video
            print(f"  video: {vi.get('title','')[:60]}")

print(f"\n자막없음: {no_sub}, 자막있음+매칭: {has_sub_match}, 자막있음+불일치: {has_sub_no_match}")
print(f"자막이 5000자로 잘려서 후반부 발언은 매칭 안 됨")

# Check: how many have subtitle_text > 4900 (truncated)
r2 = requests.get(url + '/rest/v1/influencer_videos?select=video_id,subtitle_text&subtitle_text=not.is.null&limit=200', headers=h)
truncated = sum(1 for v in r2.json() if len(v.get('subtitle_text','')) >= 4900)
total_with_sub = len(r2.json())
print(f"\n자막 보유 영상: {total_with_sub}, 5000자 잘림: {truncated}")
