"""수동 접근 - transcript URL을 다른 도구로 시도"""
import urllib.request, urllib.parse, json, os, base64, time

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# 이미 추출한 caption URL 파일들 읽기
def get_saved_urls():
    urls = {}
    for f in os.listdir(SUBS_DIR):
        if f.endswith('_caption_url.txt'):
            vid = f.replace('_caption_url.txt', '')
            with open(f'{SUBS_DIR}/{f}', 'r') as file:
                urls[vid] = file.read().strip()
    return urls

def try_cors_proxies(url):
    """CORS 프록시들 시도"""
    proxies = [
        'https://cors-anywhere.herokuapp.com/',
        'https://api.allorigins.win/get?url=',
        'https://api.codetabs.com/v1/proxy?quest=',
        'https://corsproxy.io/?',
        'https://corsproxy.org/?',
        'https://crossorigin.me/',
        'https://cors-proxy.taskcluster.net/',
        'https://yacdn.org/proxy/',
        'https://api.allorigins.win/raw?url=',
    ]
    
    for proxy in proxies:
        try:
            proxy_url = proxy + urllib.parse.quote(url) if proxy.endswith('=') else proxy + url
            req = urllib.request.Request(
                proxy_url,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; subtitle-fetcher/1.0)'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read().decode('utf-8')
                if '"events":' in data:  # Looks like valid transcript JSON
                    return json.loads(data)
        except:
            pass
    return None

def try_web_archive(url):
    """Web Archive에서 시도"""
    archive_urls = [
        f'https://web.archive.org/web/2024/{url}',
        f'https://web.archive.org/web/2023/{url}',
        f'https://archive.today/newest/{url}',
    ]
    
    for archive_url in archive_urls:
        try:
            req = urllib.request.Request(archive_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read().decode('utf-8')
                if '"events":' in data:
                    return json.loads(data)
        except:
            pass
    return None

def extract_from_embed(vid):
    """YouTube embed에서 자막 추출 시도"""
    embed_url = f'https://www.youtube.com/embed/{vid}?cc_load_policy=1&hl=ko'
    try:
        req = urllib.request.Request(embed_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
            
        # Look for any transcript/caption data in the embed
        if '"captions":' in html or '"captionTracks":' in html:
            print(f"  Found caption data in embed HTML for {vid}")
            # Save for manual inspection
            with open(f'{SUBS_DIR}/{vid}_embed.html', 'w', encoding='utf-8') as f:
                f.write(html)
            return True
    except:
        pass
    return False

print("=== Manual Caption Recovery ===")

urls = get_saved_urls()
print(f"Found {len(urls)} saved caption URLs")

for vid, caption_url in urls.items():
    json_path = f'{SUBS_DIR}/{vid}_transcript.json'
    if os.path.exists(json_path):
        print(f"[SKIP] {vid}")
        continue
    
    print(f"\n[{vid}] Trying manual approaches...")
    
    # Method 1: CORS proxies
    print("  Method 1: CORS proxies...")
    data = try_cors_proxies(caption_url)
    if data:
        print("  ✅ SUCCESS via CORS proxy!")
    else:
        print("  ❌ CORS proxies failed")
        
        # Method 2: Web Archive
        print("  Method 2: Web Archive...")
        data = try_web_archive(caption_url)
        if data:
            print("  ✅ SUCCESS via Web Archive!")
        else:
            print("  ❌ Web Archive failed")
            
            # Method 3: YouTube Embed
            print("  Method 3: YouTube Embed...")
            if extract_from_embed(vid):
                print("  ✅ Found caption data in embed")
                continue
            else:
                print("  ❌ Embed approach failed")
                continue
    
    # If we got data, parse it
    try:
        events = data.get('events', [])
        segments = []
        for evt in events:
            start_ms = evt.get('tStartMs', 0)
            segs = evt.get('segs', [])
            text = ''.join(s.get('utf8', '') for s in segs).strip()
            if text and text != '\n':
                segments.append({'start': start_ms / 1000.0, 'text': text})
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'video_id': vid,
                'segments': segments,
                'total_chars': sum(len(s['text']) for s in segments)
            }, f, ensure_ascii=False, indent=2)
        
        print(f"  📝 Saved {len(segments)} segments, {sum(len(s['text']) for s in segments)} chars")
        
    except Exception as e:
        print(f"  ❌ Parse error: {e}")
    
    time.sleep(10)  # Don't hammer too hard

print("\n=== Final Check ===")
success = 0
for vid in urls.keys():
    exists = os.path.exists(f'{SUBS_DIR}/{vid}_transcript.json')
    if exists:
        success += 1
    print(f"  {vid}: {'✅' if exists else '❌'}")

print(f"\nManual recovery: {success}/{len(urls)} successful")