"""sesang101 채널 자막 추출 - Webshare 프록시 사용"""
import json, os, sys, time, random

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

WEBSHARE_USER = "pvljrgkf"
WEBSHARE_PASS = "0e0eqk9rbwzq"
SUBS_DIR = r"C:\Users\Mario\work\subs\sesang101"

os.makedirs(SUBS_DIR, exist_ok=True)

api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username=WEBSHARE_USER,
        proxy_password=WEBSHARE_PASS,
    )
)

# Load video list
videos_file = os.path.join(os.path.dirname(__file__), 'sesang101_videos.txt')
video_ids = []
with open(videos_file, 'r', encoding='utf-16') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            # Format: video_id or url
            if 'youtube.com' in line or 'youtu.be' in line:
                if 'v=' in line:
                    vid = line.split('v=')[1].split('&')[0]
                else:
                    vid = line.split('/')[-1].split('?')[0]
            else:
                vid = line.split('|||')[0].split()[0] if '|||' in line else (line.split()[0] if ' ' in line else line)
            video_ids.append(vid)

print(f"Total videos: {len(video_ids)}")

# Check already extracted
existing = set(os.listdir(SUBS_DIR))
remaining = [v for v in video_ids if f"{v}.json" not in existing]
print(f"Already extracted: {len(video_ids) - len(remaining)}, Remaining: {len(remaining)}")

success = 0
fail = 0
for i, vid in enumerate(remaining[:20]):  # Batch of 20
    print(f"\n[{i+1}/{min(len(remaining),20)}] {vid}...", end=" ")
    try:
        transcript = api.fetch(vid, languages=['ko', 'en'])
        # Save
        entries = [{'text': s.text, 'start': s.start, 'duration': s.duration} for s in transcript]
        with open(os.path.join(SUBS_DIR, f"{vid}.json"), 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=1)
        print(f"OK ({len(entries)} segments)")
        success += 1
    except Exception as e:
        err = str(e)[:100]
        print(f"FAIL: {err}")
        fail += 1
    
    delay = random.uniform(2, 4)
    time.sleep(delay)

print(f"\n{'='*40}")
print(f"Done! Success: {success}, Fail: {fail}")
