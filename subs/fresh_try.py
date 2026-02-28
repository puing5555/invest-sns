"""새로운 caption URL 추출 후 즉시 다운로드 - 1개만 테스트"""
import urllib.request, json, re, time, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
    'Cookie': '',
}

print(f"Step 1: Getting fresh page for {VID}...")
url = f'https://www.youtube.com/watch?v={VID}'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8')
print(f"  Page loaded: {len(html)} bytes")

# Extract fresh caption URL
match = re.search(r'"captionTracks":\s*(\[.*?\])', html)
if not match:
    print("  ERROR: No captionTracks found")
    exit(1)

tracks = json.loads(match.group(1).replace('\\u0026', '&').replace('\\/', '/'))
print(f"  Found {len(tracks)} tracks")

ko_track = None
for t in tracks:
    if t.get('languageCode') == 'ko':
        ko_track = t
        break

if not ko_track:
    print("  ERROR: No Korean track")
    exit(1)

base_url = ko_track['baseUrl']
print(f"  Korean caption URL found (kind={ko_track.get('kind','')})")

# Wait 10 seconds before fetching caption
print("Step 2: Waiting 10s before caption fetch...")
time.sleep(10)

# Try to fetch with same session headers
caption_url = base_url + '&fmt=json3'
print(f"Step 3: Fetching caption...")
req2 = urllib.request.Request(caption_url, headers=headers)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    data = json.loads(resp2.read().decode('utf-8'))
    
    events = data.get('events', [])
    segments = []
    for evt in events:
        segs = evt.get('segs', [])
        text = ''.join(s.get('utf8', '') for s in segs).strip()
        if text and text != '\n':
            segments.append({'start': evt.get('tStartMs', 0) / 1000.0, 'text': text})
    
    print(f"  SUCCESS! {len(segments)} segments, {sum(len(s['text']) for s in segments)} chars")
    print(f"  First line: {segments[0]['text'][:60] if segments else 'none'}")
    
    with open(f'C:/Users/Mario/work/invest-sns/subs/{VID}_transcript.json', 'w', encoding='utf-8') as f:
        json.dump({'video_id': VID, 'title': '삼성전자 사야 돼요?', 'segments': segments}, f, ensure_ascii=False, indent=2)
    print(f"  Saved!")
    
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.reason}")
    if e.code == 429:
        print("  Still rate limited :(")
except Exception as e:
    print(f"  Error: {e}")
