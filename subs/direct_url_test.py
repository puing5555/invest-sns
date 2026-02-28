"""직접 caption URL로 자막 다운로드"""
import urllib.request, json, io, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# Read all caption URL files
url_files = [
    'ksA4IT452_4_caption_url.txt',
    'Xv-wNA91EPE_caption_url.txt', 
    'fDZnPoK5lyc_caption_url.txt',
    'nm5zQxZSkbk_caption_url.txt',
    'XveVkr3JHs4_caption_url.txt',
    'N7xO-UWCM5w_caption_url.txt',
    'BVRoApF0c8k_caption_url.txt',
    'ZXuQCpuVCYc_caption_url.txt',
    'tSXkj2Omz34_caption_url.txt',
    'B5owNUs_DFw_caption_url.txt',
    'bmXgryWXNrw_caption_url.txt',
]

video_titles = {
    'ksA4IT452_4': '삼성전자 사야 돼요?',
    'Xv-wNA91EPE': '삼성전자 절대 팔지마',
    'fDZnPoK5lyc': '반도체 다음 4종목',
    'nm5zQxZSkbk': '국내주식 vs 해외주식',
    'XveVkr3JHs4': '우리나라 주식은',
    'N7xO-UWCM5w': '미국 주식 절대 사면 안되는',
    'BVRoApF0c8k': '하락장에서 절대 사면 안되는',
    'ZXuQCpuVCYc': '12월부터 위험한',
    'tSXkj2Omz34': '연말까지 오를',
    'B5owNUs_DFw': '11월부터 급락하는',
    'bmXgryWXNrw': '내년에 10배 오를'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
    'Referer': 'https://www.youtube.com/',
}

success_count = 0

for url_file in url_files:
    vid = url_file.replace('_caption_url.txt', '')
    title = video_titles.get(vid, 'Unknown')
    
    json_path = f'{SUBS_DIR}/{vid}_transcript.json'
    if os.path.exists(json_path):
        print(f"[SKIP] {vid} - already exists")
        continue
    
    print(f"\n[{vid}] {title}")
    
    try:
        # Read the URL
        with open(f'{SUBS_DIR}/{url_file}', 'r', encoding='utf-8') as f:
            caption_url = f.read().strip()
        
        print(f"  Trying direct URL...")
        
        # Request the caption
        req = urllib.request.Request(caption_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        # Parse segments
        events = data.get('events', [])
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
            transcript_data = {
                'video_id': vid,
                'title': title,
                'segments': segments
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
            print(f"  SUCCESS! {len(segments)} segments, {sum(len(s['text']) for s in segments)} chars")
            print(f"  First line: {segments[0]['text'][:50]}...")
            success_count += 1
        else:
            print(f"  ERROR: No segments found")
            
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.reason}")
        if e.code == 429:
            print("  Rate limited")
        elif e.code == 403:
            print("  Forbidden - URL expired")
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\n=== Summary ===")
print(f"Success: {success_count}/{len(url_files)} videos")

if success_count > 0:
    print(f"\nReady for V9 analysis on {success_count} videos!")
else:
    print(f"\nNo subtitles downloaded. URLs may be expired.")