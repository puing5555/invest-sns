"""YouTube HTML에서 자막 URL 추출 후 다운로드"""
import urllib.request, json, re, os, time

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

VIDEOS = {
    'ksA4IT452_4': '삼성전자 사야 돼요?',
    'nm5zQxZSkbk': '스트래티지 비트코인',
    'XveVkr3JHs4': '코스피 왜 강한가',
    'N7xO-UWCM5w': '삼성전자 시총 1000조',
    'Xv-wNA91EPE': '삼성전자 팔지마 조진표',
    'BVRoApF0c8k': '4개주식 사세요 배재규',
    'fDZnPoK5lyc': '반도체 다음 4종목',
    'ZXuQCpuVCYc': '코스피 ETF',
    'tSXkj2Omz34': '코스피 6000',
    'B5owNUs_DFw': '소프트웨어 주식',
    'bmXgryWXNrw': '하이닉스 추가매수',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

for vid, title in VIDEOS.items():
    json_path = f'{SUBS_DIR}/{vid}_transcript.json'
    if os.path.exists(json_path):
        print(f"[SKIP] {vid}")
        continue
    
    try:
        print(f"[{vid}] {title}...")
        
        # Step 1: Get YouTube page HTML
        url = f'https://www.youtube.com/watch?v={vid}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
        
        # Step 2: Find captionTracks in ytInitialPlayerResponse
        match = re.search(r'"captionTracks":\s*(\[.*?\])', html)
        if not match:
            # Try another pattern
            match = re.search(r'"captions":\s*\{.*?"captionTracks":\s*(\[.*?\])', html)
        
        if not match:
            print(f"  No caption tracks found in HTML ({len(html)} bytes)")
            # Save HTML for debugging
            with open(f'{SUBS_DIR}/{vid}_debug.html', 'w', encoding='utf-8') as f:
                # Save just the relevant part
                idx = html.find('captionTracks')
                if idx > 0:
                    f.write(html[max(0,idx-200):idx+500])
                else:
                    idx = html.find('captions')
                    if idx > 0:
                        f.write(html[max(0,idx-200):idx+500])
                    else:
                        f.write(html[:2000])
            continue
        
        tracks_json = match.group(1)
        # Clean up JSON (unescape)
        tracks_json = tracks_json.replace('\\u0026', '&').replace('\\/', '/')
        tracks = json.loads(tracks_json)
        
        print(f"  Found {len(tracks)} caption tracks")
        
        # Step 3: Find Korean auto-generated caption
        ko_track = None
        for t in tracks:
            lang = t.get('languageCode', '')
            kind = t.get('kind', '')
            name = t.get('name', {})
            label = name.get('simpleText', '') if isinstance(name, dict) else str(name)
            print(f"    Track: {lang} ({kind}) - {label}")
            if lang == 'ko':
                ko_track = t
                break
        
        if not ko_track:
            # Try auto-generated
            for t in tracks:
                if t.get('languageCode', '') == 'ko' or 'Korean' in str(t.get('name', '')):
                    ko_track = t
                    break
        
        if not ko_track and tracks:
            # Use first available track
            ko_track = tracks[0]
            print(f"  No Korean track, using first: {ko_track.get('languageCode')}")
        
        if not ko_track:
            print(f"  No tracks at all")
            continue
        
        # Step 4: Download the caption
        base_url = ko_track.get('baseUrl', '')
        if not base_url:
            print(f"  No baseUrl in track")
            continue
        
        # Get JSON3 format
        caption_url = base_url + '&fmt=json3'
        req2 = urllib.request.Request(caption_url, headers=headers)
        with urllib.request.urlopen(req2, timeout=15) as resp2:
            caption_data = json.loads(resp2.read().decode('utf-8'))
        
        # Step 5: Parse segments
        events = caption_data.get('events', [])
        segments = []
        for evt in events:
            start_ms = evt.get('tStartMs', 0)
            segs = evt.get('segs', [])
            text = ''.join(s.get('utf8', '') for s in segs).strip()
            if text and text != '\n':
                segments.append({
                    'start': start_ms / 1000.0,
                    'text': text
                })
        
        # Save
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'video_id': vid,
                'title': title,
                'segments': segments,
                'total_chars': sum(len(s['text']) for s in segments)
            }, f, ensure_ascii=False, indent=2)
        
        total = sum(len(s['text']) for s in segments)
        print(f"  SUCCESS: {len(segments)} segments, {total} chars")
        
    except Exception as e:
        print(f"  ERROR: {e}")
    
    time.sleep(3)  # Rate limit respect

print("\n=== Summary ===")
for vid in VIDEOS:
    exists = os.path.exists(f'{SUBS_DIR}/{vid}_transcript.json')
    print(f"  {vid}: {'OK' if exists else 'MISSING'}")
