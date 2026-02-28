"""무료 프록시 + 60초 간격으로 자막 다운로드"""
import urllib.request, json, io, sys, os, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# 무료 SOCKS5/HTTP 프록시 목록 (2026년 활성 프록시들)
FREE_PROXIES = [
    'socks5://184.178.172.28:15294',
    'socks5://72.195.34.59:4145', 
    'socks5://72.206.181.105:4145',
    'socks5://192.111.139.162:4145',
    'socks5://72.195.114.169:4145',
    'socks5://184.178.172.14:15294',
    'socks5://72.210.252.134:46164',
    'socks5://174.64.199.79:4145',
    'http://8.210.149.250:9999',
    'http://47.74.152.29:8888',
    'http://43.134.33.254:3128',
    'http://178.128.21.246:8080',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
    'Accept': '*/*',
    'Referer': 'https://www.youtube.com/',
}

def test_proxy_direct_url(proxy_url):
    """기존 caption URL로 프록시 테스트"""
    
    # Read existing caption URL
    url_file = f'{SUBS_DIR}/ksA4IT452_4_caption_url.txt'
    if not os.path.exists(url_file):
        return False
        
    with open(url_file, 'r', encoding='utf-8') as f:
        caption_url = f.read().strip()
    
    print(f"  Using existing caption URL...")
    
    try:
        # Create proxy handler
        if proxy_url.startswith('socks5://'):
            import socks
            import socket
            
            proxy_parts = proxy_url.replace('socks5://', '').split(':')
            proxy_host = proxy_parts[0]
            proxy_port = int(proxy_parts[1])
            
            socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
            socket.socket = socks.socksocket
            
        elif proxy_url.startswith('http://'):
            proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
        
        # Try to fetch caption
        req = urllib.request.Request(caption_url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        # Parse events
        events = data.get('events', [])
        if not events:
            return False
            
        segments = []
        for evt in events:
            segs = evt.get('segs', [])
            text = ''.join(s.get('utf8', '') for s in segs).strip()
            if text and text != '\n':
                segments.append({
                    'start': evt.get('tStartMs', 0) / 1000.0,
                    'text': text
                })
        
        if segments:
            # Save transcript
            json_path = f'{SUBS_DIR}/{VID}_transcript.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'video_id': VID,
                    'title': '삼성전자 사야 돼요?',
                    'segments': segments
                }, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ SUCCESS! {len(segments)} segments saved")
            return True
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}...")
        return False
        
    return False

print(f"Testing {len(FREE_PROXIES)} proxies with 60s intervals...")

for i, proxy in enumerate(FREE_PROXIES):
    print(f"\n[{i+1}/{len(FREE_PROXIES)}] Testing proxy: {proxy}")
    
    try:
        if test_proxy_direct_url(proxy):
            print(f"\n🎉 SUCCESS via proxy: {proxy}")
            break
            
    except Exception as e:
        print(f"  ❌ Proxy failed: {e}")
    
    # 60초 대기 (마지막은 제외)
    if i < len(FREE_PROXIES) - 1:
        print(f"  💤 Waiting 60 seconds before next proxy...")
        time.sleep(60)
        
else:
    print(f"\n❌ All proxies failed")
    
print(f"\nChecking if file was created...")
json_path = f'{SUBS_DIR}/{VID}_transcript.json'
if os.path.exists(json_path):
    print(f"✅ File exists: {json_path}")
else:
    print(f"❌ No file created")