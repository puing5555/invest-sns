"""YouTube HTML에서 innertube API로 자막 추출 시도"""
import urllib.request, json, re, os, time

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

VIDEOS = [
    ('ksA4IT452_4', '삼성전자 사야 돼요?'),
    ('nm5zQxZSkbk', '스트래티지 비트코인'),
    ('XveVkr3JHs4', '코스피 왜 강한가'),
    ('N7xO-UWCM5w', '삼성전자 시총 1000조'),
    ('Xv-wNA91EPE', '삼성전자 팔지마 조진표'),
    ('BVRoApF0c8k', '4개주식 사세요 배재규'),
    ('fDZnPoK5lyc', '반도체 다음 4종목'),
    ('ZXuQCpuVCYc', '코스피 ETF'),
    ('tSXkj2Omz34', '코스피 6000'),
    ('B5owNUs_DFw', '소프트웨어 주식'),
    ('bmXgryWXNrw', '하이닉스 추가매수'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
}

def get_innertube_transcript(vid):
    """Use YouTube innertube API to get transcript"""
    # First get the page to extract API key and continuation token
    url = f'https://www.youtube.com/watch?v={vid}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
    
    # Extract API key
    api_key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
    if not api_key_match:
        return None, "No API key found"
    api_key = api_key_match.group(1)
    
    # Extract client version
    ver_match = re.search(r'"clientVersion":"([^"]+)"', html)
    client_ver = ver_match.group(1) if ver_match else '2.20240101.00.00'
    
    # Use innertube get_transcript endpoint
    innertube_url = f'https://www.youtube.com/youtubei/v1/get_transcript?key={api_key}'
    
    payload = {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": client_ver,
                "hl": "ko",
                "gl": "KR"
            }
        },
        "params": _encode_transcript_params(vid)
    }
    
    data = json.dumps(payload).encode('utf-8')
    req2 = urllib.request.Request(
        innertube_url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    )
    
    with urllib.request.urlopen(req2, timeout=15) as resp2:
        result = json.loads(resp2.read().decode('utf-8'))
    
    return result, None

def _encode_transcript_params(video_id):
    """Encode transcript params for innertube API"""
    import base64
    # This is the protobuf-encoded params for transcript request
    # Video ID in the params
    inner = b'\n\x0b' + video_id.encode() + b'\x12\x12\n\x03asr\x12\x02ko\x1a\x07DEFAULT'
    outer = b'\n' + bytes([len(inner)]) + inner
    return base64.b64encode(outer).decode()

for vid, title in VIDEOS:
    json_path = f'{SUBS_DIR}/{vid}_transcript.json'
    if os.path.exists(json_path):
        print(f"[SKIP] {vid}")
        continue
    
    print(f"[{vid}] {title}")
    
    try:
        result, err = get_innertube_transcript(vid)
        if err:
            print(f"  ERROR: {err}")
            continue
        
        # Save raw response for debugging
        with open(f'{SUBS_DIR}/{vid}_innertube.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Parse transcript from response
        actions = result.get('actions', [])
        segments = []
        
        for action in actions:
            panel = action.get('updateEngagementPanelAction', {}).get('content', {})
            transcript = panel.get('transcriptRenderer', {}).get('content', {})
            body = transcript.get('transcriptSearchPanelRenderer', {}).get('body', {})
            sections = body.get('transcriptSegmentListRenderer', {}).get('initialSegments', [])
            
            for seg in sections:
                renderer = seg.get('transcriptSegmentRenderer', {})
                snippet = renderer.get('snippet', {}).get('runs', [])
                text = ''.join(r.get('text', '') for r in snippet).strip()
                start_ms = int(renderer.get('startMs', '0'))
                
                if text:
                    segments.append({
                        'start': start_ms / 1000.0,
                        'text': text
                    })
        
        if segments:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'video_id': vid,
                    'title': title,
                    'segments': segments,
                    'total_chars': sum(len(s['text']) for s in segments)
                }, f, ensure_ascii=False, indent=2)
            print(f"  SUCCESS: {len(segments)} segments, {sum(len(s['text']) for s in segments)} chars")
        else:
            print(f"  No segments found in response (keys: {list(result.keys())})")
            if 'actions' in result:
                print(f"  Actions: {len(actions)}")
    
    except Exception as e:
        print(f"  ERROR: {e}")
    
    time.sleep(5)

print("\n=== Summary ===")
ok = 0
for vid, _ in VIDEOS:
    exists = os.path.exists(f'{SUBS_DIR}/{vid}_transcript.json')
    if exists: ok += 1
    print(f"  {vid}: {'OK' if exists else 'MISSING'}")
print(f"\nTotal: {ok}/{len(VIDEOS)}")
