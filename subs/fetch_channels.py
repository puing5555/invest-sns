"""4개 채널 영상 목록 + 자막 다운로드"""
import subprocess, json, os, sys, time

CHANNELS = {
    'syukaworld': {'handle': '@syukaworld', 'name': '슈카월드'},
    'booreadman': {'handle': '@bu_read_nam', 'name': '부읽남TV', 'search': 'ytsearch15:부읽남TV 주식'},
    'dalrant': {'handle': '@dalranttuja', 'name': '달란트투자', 'search': 'ytsearch15:달란트투자 주식'},
    'leehyoseok': {'handle': '@leehyoseok', 'name': '이효석아카데미', 'search': 'ytsearch15:이효석아카데미 주식'},
}

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'
os.makedirs(SUBS_DIR, exist_ok=True)

def get_playlist(channel_key, channel_info):
    outfile = f'{SUBS_DIR}/{channel_key}_videos.json'
    if os.path.exists(outfile) and os.path.getsize(outfile) > 100:
        print(f"[{channel_key}] Already have playlist, skipping")
        return outfile

    # Try search first if handle doesn't work
    url = channel_info.get('search', f"https://www.youtube.com/{channel_info['handle']}/videos")
    if 'search' not in channel_info:
        url = f"https://www.youtube.com/{channel_info['handle']}/videos"
    
    cmd = [sys.executable, '-m', 'yt_dlp', '--flat-playlist', '-J', url, '--playlist-items', '1:15', '--sleep-interval', '1']
    
    print(f"[{channel_key}] Fetching playlist: {url}")
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    
    if result.returncode != 0:
        # Try search fallback
        if 'search' not in channel_info:
            search_url = f"ytsearch15:{channel_info['name']} 주식 투자"
            print(f"[{channel_key}] Handle failed, trying search: {search_url}")
            cmd = [sys.executable, '-m', 'yt_dlp', '--flat-playlist', '-J', search_url, '--sleep-interval', '1']
            result = subprocess.run(cmd, capture_output=True, timeout=120)
    
    if result.returncode == 0 and result.stdout:
        with open(outfile, 'wb') as f:
            f.write(result.stdout)
        print(f"[{channel_key}] Saved playlist to {outfile}")
        return outfile
    else:
        stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
        print(f"[{channel_key}] FAILED: {stderr[:200]}")
        return None

def parse_playlist(filepath, channel_key):
    try:
        raw = open(filepath, 'rb').read()
        # Try different encodings
        for enc in ['utf-8-sig', 'utf-8', 'cp949']:
            try:
                text = raw.decode(enc)
                break
            except:
                continue
        else:
            text = raw.decode('utf-8', errors='replace')
        
        data = json.loads(text)
        entries = data.get('entries', [])
        print(f"\n=== {channel_key} ({len(entries)} videos) ===")
        for i, e in enumerate(entries, 1):
            ch = e.get('channel', e.get('uploader', '?'))
            print(f"  {i:2d}. {e['id']} [{ch}] {e.get('title','?')}")
        return entries
    except Exception as ex:
        print(f"ERROR parsing {filepath}: {ex}")
        return []

# Already have syuka_30
print("=== Processing channels ===\n")

for key, info in CHANNELS.items():
    if key == 'syukaworld':
        continue  # Already have it
    filepath = get_playlist(key, info)
    if filepath:
        parse_playlist(filepath, key)
    time.sleep(2)
