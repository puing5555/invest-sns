"""프록시로 YouTube 자막 다운로드 시도"""
import subprocess, sys, os, time, json

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# 무료 프록시 목록 - SOCKS5/HTTP
PROXIES = [
    'socks5://184.178.172.28:15294',
    'socks5://72.195.34.59:4145',
    'socks5://72.206.181.105:4145',
    'socks5://192.111.139.162:4145',
    'socks5://72.195.114.169:4145',
    'socks5://184.178.172.14:15294',
    'socks5://72.210.252.134:46164',
    'socks5://174.64.199.79:4145',
]

VIDEOS = [
    'ksA4IT452_4',
    'nm5zQxZSkbk', 
    'XveVkr3JHs4',
    'N7xO-UWCM5w',
    'Xv-wNA91EPE',
    'BVRoApF0c8k',
    'fDZnPoK5lyc',
    'ZXuQCpuVCYc',
    'tSXkj2Omz34',
    'B5owNUs_DFw',
    'bmXgryWXNrw',
]

# Also try without proxy but with --sleep-interval 30
def try_download(vid, proxy=None):
    srt_path = f'{SUBS_DIR}/{vid}.ko.srt'
    vtt_path = f'{SUBS_DIR}/{vid}.ko.vtt'
    json_path = f'{SUBS_DIR}/{vid}_transcript.json'
    
    if os.path.exists(srt_path) or os.path.exists(vtt_path) or os.path.exists(json_path):
        return True
    
    cmd = [sys.executable, '-m', 'yt_dlp',
           '--write-auto-sub', '--sub-lang', 'ko',
           '--skip-download', '--convert-subs', 'srt',
           '-o', f'{SUBS_DIR}/{vid}',
           f'https://www.youtube.com/watch?v={vid}']
    
    if proxy:
        cmd.insert(4, '--proxy')
        cmd.insert(5, proxy)
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if os.path.exists(srt_path):
            print(f"  SUCCESS via {proxy or 'direct'}")
            return True
        return False
    except Exception as e:
        return False

# Method 1: Try each proxy
print("=== Method 1: Proxy Download ===")
for vid in VIDEOS[:3]:  # Test with first 3
    print(f"\n[{vid}]")
    for proxy in PROXIES[:4]:  # Try first 4 proxies
        print(f"  Trying proxy {proxy}...")
        if try_download(vid, proxy):
            break
        time.sleep(2)

# Method 2: Try youtube-transcript-api with proxy
print("\n=== Method 2: Transcript API with proxy ===")
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    import requests
    
    for vid in VIDEOS[:3]:
        json_path = f'{SUBS_DIR}/{vid}_transcript.json'
        if os.path.exists(json_path):
            print(f"[SKIP] {vid}")
            continue
        
        for proxy_url in PROXIES[:4]:
            try:
                print(f"  [{vid}] Trying transcript API with {proxy_url}...")
                
                # Create proxied session
                proxies = {'http': proxy_url, 'https': proxy_url}
                
                ytt = YouTubeTranscriptApi()
                transcript = ytt.fetch(vid, languages=['ko'])
                
                segments = []
                for snippet in transcript.snippets:
                    segments.append({'start': snippet.start, 'text': snippet.text})
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({'video_id': vid, 'segments': segments}, f, ensure_ascii=False, indent=2)
                
                print(f"  SUCCESS: {len(segments)} segments")
                break
            except Exception as e:
                err = str(e)[:80]
                print(f"  FAIL: {err}")
                time.sleep(2)
except Exception as e:
    print(f"Transcript API not available: {e}")

# Method 3: Try Piped API (alternative YouTube frontend)
print("\n=== Method 3: Piped API ===")
import urllib.request

PIPED_INSTANCES = [
    'https://pipedapi.kavin.rocks',
    'https://piped-api.privacy.com.de', 
    'https://pipedapi.in.projectsegfau.lt',
    'https://api.piped.projectsegfau.lt',
]

for vid in VIDEOS[:3]:
    json_path = f'{SUBS_DIR}/{vid}_transcript.json'
    if os.path.exists(json_path):
        print(f"[SKIP] {vid}")
        continue
    
    for instance in PIPED_INSTANCES:
        try:
            url = f'{instance}/streams/{vid}'
            print(f"  [{vid}] Trying Piped: {instance}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                
                # Get subtitle tracks
                subs = data.get('subtitles', [])
                ko_subs = [s for s in subs if s.get('code', '').startswith('ko')]
                
                if ko_subs:
                    sub_url = ko_subs[0].get('url', '')
                    if sub_url:
                        req2 = urllib.request.Request(sub_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req2, timeout=10) as resp2:
                            sub_content = resp2.read().decode('utf-8')
                            with open(f'{SUBS_DIR}/{vid}.ko.vtt', 'w', encoding='utf-8') as f:
                                f.write(sub_content)
                            print(f"  SUCCESS via Piped: {len(sub_content)} chars")
                            break
                else:
                    # Auto-generated?
                    auto_subs = [s for s in subs if 'auto' in s.get('code','').lower() and 'ko' in s.get('code','').lower()]
                    print(f"  No ko subs. Available: {[s.get('code') for s in subs[:5]]}")
        except Exception as e:
            err = str(e)[:80]
            print(f"  FAIL: {err}")
        time.sleep(2)

print("\n=== Summary ===")
for vid in VIDEOS:
    srt = os.path.exists(f'{SUBS_DIR}/{vid}.ko.srt')
    vtt = os.path.exists(f'{SUBS_DIR}/{vid}.ko.vtt')
    jsn = os.path.exists(f'{SUBS_DIR}/{vid}_transcript.json')
    status = "OK" if (srt or vtt or jsn) else "MISSING"
    print(f"  {vid}: {status}")
