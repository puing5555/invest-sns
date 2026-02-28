"""YouTube 자막 - baseUrl 추출 후 Google Cache/다른 도메인으로 우회"""
import urllib.request, json, re, os, time, ssl

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

VIDEOS = [
    'ksA4IT452_4', 'nm5zQxZSkbk', 'XveVkr3JHs4', 'N7xO-UWCM5w',
    'Xv-wNA91EPE', 'BVRoApF0c8k', 'fDZnPoK5lyc', 'ZXuQCpuVCYc',
    'tSXkj2Omz34', 'B5owNUs_DFw', 'bmXgryWXNrw',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
}

# Create SSL context that doesn't verify (for proxies)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_caption_url(vid):
    """Extract caption baseUrl from YouTube page HTML"""
    url = f'https://www.youtube.com/watch?v={vid}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
    
    match = re.search(r'"captionTracks":\s*(\[.*?\])', html)
    if not match:
        return None, None
    
    tracks_json = match.group(1).replace('\\u0026', '&').replace('\\/', '/')
    tracks = json.loads(tracks_json)
    
    for t in tracks:
        if t.get('languageCode') == 'ko':
            return t.get('baseUrl', ''), t.get('kind', '')
    return None, None

def download_caption(base_url):
    """Try multiple methods to download the caption"""
    caption_url = base_url + '&fmt=json3'
    
    # Method 1: Direct with different User-Agent (mobile)
    mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
        'Accept': '*/*',
    }
    try:
        req = urllib.request.Request(caption_url, headers=mobile_headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        pass
    
    # Method 2: Via Google webcache
    try:
        cache_url = f'https://webcache.googleusercontent.com/search?q=cache:{caption_url}'
        req = urllib.request.Request(cache_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except:
        pass
    
    # Method 3: Via web archive
    try:
        archive_url = f'https://web.archive.org/web/2024/{caption_url}'
        req = urllib.request.Request(archive_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except:
        pass
    
    # Method 4: Try different YouTube domains
    for domain in ['m.youtube.com', 'music.youtube.com']:
        try:
            alt_url = caption_url.replace('www.youtube.com', domain)
            req = urllib.request.Request(alt_url, headers=mobile_headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except:
            pass
    
    # Method 5: Via cors-anywhere type proxy
    for proxy_base in [
        'https://corsproxy.io/?',
        'https://api.allorigins.win/raw?url=',
    ]:
        try:
            proxy_url = proxy_base + urllib.parse.quote(caption_url)
            req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except:
            pass
    
    return None

import urllib.parse

for vid in VIDEOS:
    json_path = f'{SUBS_DIR}/{vid}_transcript.json'
    if os.path.exists(json_path):
        print(f"[SKIP] {vid}")
        continue
    
    print(f"[{vid}]")
    
    try:
        # Get caption URL
        base_url, kind = get_caption_url(vid)
        if not base_url:
            print(f"  No Korean caption URL found")
            continue
        
        print(f"  Caption URL found (kind={kind})")
        
        # Try to download
        caption_data = download_caption(base_url)
        
        if not caption_data:
            # Save the URL for manual download later
            url_file = f'{SUBS_DIR}/{vid}_caption_url.txt'
            with open(url_file, 'w') as f:
                f.write(base_url + '&fmt=json3')
            print(f"  All methods failed. Saved URL to {url_file}")
            continue
        
        # Parse segments
        events = caption_data.get('events', [])
        segments = []
        for evt in events:
            start_ms = evt.get('tStartMs', 0)
            segs = evt.get('segs', [])
            text = ''.join(s.get('utf8', '') for s in segs).strip()
            if text and text != '\n':
                segments.append({'start': start_ms / 1000.0, 'text': text})
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'video_id': vid, 'segments': segments, 'total_chars': sum(len(s['text']) for s in segments)}, f, ensure_ascii=False, indent=2)
        
        print(f"  SUCCESS: {len(segments)} segments")
        
    except Exception as e:
        print(f"  ERROR: {e}")
    
    time.sleep(5)

print("\n=== Summary ===")
ok = 0
for vid in VIDEOS:
    exists = os.path.exists(f'{SUBS_DIR}/{vid}_transcript.json')
    url_exists = os.path.exists(f'{SUBS_DIR}/{vid}_caption_url.txt')
    status = "OK" if exists else ("URL saved" if url_exists else "MISSING")
    if exists: ok += 1
    print(f"  {vid}: {status}")
print(f"\nTotal: {ok}/{len(VIDEOS)} downloaded")
