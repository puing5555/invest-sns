"""HTTP 프록시만으로 빠른 테스트"""
import urllib.request, json, io, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# HTTP 프록시만
HTTP_PROXIES = [
    'http://8.210.149.250:9999',
    'http://47.74.152.29:8888', 
    'http://43.134.33.254:3128',
    'http://178.128.21.246:8080',
    'http://103.152.113.18:80',
    'http://103.152.113.32:80',
    'http://185.217.143.96:80',
    'http://195.201.34.198:80',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Accept': '*/*',
}

# Read existing caption URL
url_file = f'{SUBS_DIR}/ksA4IT452_4_caption_url.txt'
with open(url_file, 'r') as f:
    caption_url = f.read().strip()

print(f"Testing {len(HTTP_PROXIES)} HTTP proxies...")

for i, proxy in enumerate(HTTP_PROXIES):
    print(f"\n[{i+1}/{len(HTTP_PROXIES)}] {proxy}")
    
    try:
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        opener = urllib.request.build_opener(proxy_handler)
        
        req = urllib.request.Request(caption_url, headers=headers)
        with opener.open(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        events = data.get('events', [])
        if events:
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
                json_path = f'{SUBS_DIR}/{VID}_transcript.json'
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'video_id': VID,
                        'title': '삼성전자 사야 돼요?',
                        'segments': segments
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"  ✅ SUCCESS! {len(segments)} segments")
                print(f"🎉 SUCCESS via: {proxy}")
                break
        else:
            print(f"  ❌ No events")
            
    except Exception as e:
        print(f"  ❌ {str(e)[:60]}")

else:
    print(f"\n❌ All HTTP proxies failed")

# Check result
json_path = f'{SUBS_DIR}/{VID}_transcript.json'
if os.path.exists(json_path):
    print(f"\n✅ File created: {json_path}")
else:
    print(f"\n❌ No file created")