"""세상학개론 영상 제목(한국어) + 날짜 수정 via yt-dlp"""
import subprocess, requests, json, time, sys

URL = 'https://arypzhotxflimroprmdk.supabase.co'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
CHANNEL_ID = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1'

# Get all sesang101 videos
r = requests.get(URL + '/rest/v1/influencer_videos?channel_id=eq.' + CHANNEL_ID + '&select=id,video_id,title&limit=100', headers=H, timeout=15)
videos = r.json()
print(f'Total videos: {len(videos)}', flush=True)

updated = 0
errors = 0

for i, v in enumerate(videos):
    yt_id = v['video_id']
    print(f'[{i+1}/{len(videos)}] {yt_id}... ', end='', flush=True)
    
    try:
        # Get title + upload_date in one call
        result = subprocess.run(
            [sys.executable, '-m', 'yt_dlp', '--print', '%(title)s|||%(upload_date)s', '--no-download',
             '--extractor-args', 'youtube:lang=ko',
             f'https://www.youtube.com/watch?v={yt_id}'],
            capture_output=True, timeout=30
        )
        
        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace')[:100]
            print(f'yt-dlp error: {stderr}', flush=True)
            errors += 1
            time.sleep(2)
            continue
        
        # Try utf-8 first, then cp949
        try:
            output = result.stdout.decode('utf-8').strip()
        except:
            output = result.stdout.decode('cp949', errors='replace').strip()
        if '|||' not in output:
            print(f'bad output: {output[:50]}', flush=True)
            errors += 1
            time.sleep(2)
            continue
        
        title, upload_date = output.split('|||', 1)
        title = title.strip()
        upload_date = upload_date.strip()
        
        # Format date: 20240515 -> 2024-05-15T00:00:00+00:00
        if len(upload_date) == 8:
            pub = f'{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}T00:00:00+00:00'
        else:
            pub = None
        
        # Update DB
        patch = {'title': title[:500]}
        if pub:
            patch['published_at'] = pub
        
        r = requests.patch(
            URL + '/rest/v1/influencer_videos?id=eq.' + v['id'],
            headers=H, json=patch, timeout=10
        )
        
        if r.ok:
            updated += 1
            print(f'OK: {title[:40]}... ({upload_date})', flush=True)
        else:
            print(f'DB error: {r.status_code}', flush=True)
            errors += 1
        
        time.sleep(2)  # rate limit
        
    except subprocess.TimeoutExpired:
        print('timeout', flush=True)
        errors += 1
    except Exception as e:
        print(f'error: {e}', flush=True)
        errors += 1

print(f'\nDone: updated={updated}, errors={errors}', flush=True)
