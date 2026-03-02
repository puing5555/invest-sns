import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

result = subprocess.run([
    sys.executable, '-m', 'yt_dlp', '--flat-playlist', '-j',
    '--dateafter', '20251001',
    '--datebefore', '20260301',
    'https://www.youtube.com/@sesang101/videos'
], capture_output=True, text=True, timeout=120)

lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
print(f'Found {len(lines)} videos')

existing_ids = set()
# Check which are already in DB
for line in lines:
    try:
        d = json.loads(line)
        vid = d.get('id', '?')
        title = d.get('title', '?')
        print(f"{vid} | {title}")
        existing_ids.add(vid)
    except:
        pass

if result.stderr:
    print('STDERR:', result.stderr[:500])
