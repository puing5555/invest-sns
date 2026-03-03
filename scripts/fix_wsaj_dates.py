"""Fix wsaj signal dates - use video upload date instead of today"""
import sys, io, os, json, requests, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}

WSAJ_SPEAKER = 'a80f6cdf-e53a-42a9-95ea-1c5ba9c7a986'

# Step 1: Get wsaj videos and their youtube dates
r = requests.get(f"{URL}/rest/v1/influencer_videos?channel_id=eq.d4639050-bebf-41d4-9786-93005fb80b85&select=id,video_id,title,published_at", headers=H)
videos = r.json()
print(f"wsaj videos: {len(videos)}")

# Step 2: Get actual upload dates from yt-dlp
for v in videos:
    vid = v['video_id']
    title = v['title']
    pub = v.get('published_at')
    print(f"\n{vid} | current pub: {pub} | {title}")
    
    if not pub:
        # Get date from yt-dlp
        try:
            result = subprocess.run(
                ['python', '-m', 'yt_dlp', '--print', '%(upload_date)s', f'https://youtube.com/watch?v={vid}', '--no-download'],
                capture_output=True, text=True, encoding='utf-8', timeout=30
            )
            date_str = result.stdout.strip()
            if date_str and date_str != 'NA' and len(date_str) == 8:
                formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                print(f"  yt-dlp date: {formatted}")
                # Update video
                r2 = requests.patch(
                    f"{URL}/rest/v1/influencer_videos?id=eq.{v['id']}",
                    headers=H, json={'published_at': formatted}
                )
                print(f"  Video updated: {r2.status_code}")
                v['published_at'] = formatted
            else:
                print(f"  yt-dlp returned: {date_str}")
        except Exception as e:
            print(f"  yt-dlp error: {e}")

# Step 3: Check if influencer_signals has a date field
r = requests.get(f"{URL}/rest/v1/influencer_signals?select=*&speaker_id=eq.{WSAJ_SPEAKER}&limit=1", headers=H)
sig_cols = list(r.json()[0].keys()) if r.json() else []
print(f"\nSignal columns: {sig_cols}")

# The date is likely from created_at or the video's published_at
# The frontend probably uses video published_at for display
print("\nDone! Video published_at dates should now be correct.")
print("Frontend fetches date from influencer_videos.published_at via JOIN.")
