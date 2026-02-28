"""Invidious API로 자막 다운로드 시도"""
import urllib.request, json, io, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# Invidious public instances
INVIDIOUS_INSTANCES = [
    'https://invidious.io',
    'https://inv.odyssey346.dev', 
    'https://invidious.fdn.fr',
    'https://watch.thekitty.zone',
    'https://invidious.flokinet.to',
    'https://yt.artemislena.eu',
    'https://invidious.privacydev.net',
    'https://iv.ggtyler.dev',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json',
}

print(f"Testing Invidious instances for video: {VID}")

for i, instance in enumerate(INVIDIOUS_INSTANCES):
    print(f"\n[{i+1}/{len(INVIDIOUS_INSTANCES)}] Trying: {instance}")
    
    try:
        # Get video info with captions
        api_url = f"{instance}/api/v1/videos/{VID}"
        req = urllib.request.Request(api_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        print(f"  ✅ API response received")
        
        # Look for Korean captions
        captions = data.get('captions', [])
        print(f"  Found {len(captions)} caption tracks")
        
        ko_caption = None
        for cap in captions:
            if cap.get('languageCode') == 'ko' or 'ko' in cap.get('label', '').lower():
                ko_caption = cap
                break
        
        if not ko_caption:
            print(f"  ❌ No Korean captions found")
            continue
            
        print(f"  ✅ Korean caption found: {ko_caption.get('label', '')}")
        
        # Download caption file
        caption_url = ko_caption.get('url', '')
        if not caption_url.startswith('http'):
            caption_url = instance + caption_url
            
        print(f"  Downloading from: {caption_url[:80]}...")
        
        req2 = urllib.request.Request(caption_url, headers=headers)
        with urllib.request.urlopen(req2, timeout=15) as resp2:
            caption_content = resp2.read().decode('utf-8')
        
        # Save as VTT first
        vtt_path = f'{SUBS_DIR}/{VID}.ko.vtt'
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write(caption_content)
            
        print(f"  ✅ SUCCESS! Saved {len(caption_content)} chars to {VID}.ko.vtt")
        
        # Also convert to simple JSON format
        segments = []
        lines = caption_content.split('\n')
        for i, line in enumerate(lines):
            if '-->' in line:  # VTT timestamp line
                try:
                    # Next line should be the text
                    if i + 1 < len(lines):
                        text = lines[i + 1].strip()
                        if text and not text.startswith('WEBVTT'):
                            # Parse start time
                            start_part = line.split(' --> ')[0].strip()
                            # Convert to seconds (rough)
                            time_parts = start_part.replace(',', '.').split(':')
                            if len(time_parts) >= 2:
                                start_sec = float(time_parts[-1])
                                if len(time_parts) >= 2:
                                    start_sec += int(time_parts[-2]) * 60
                                if len(time_parts) >= 3:
                                    start_sec += int(time_parts[-3]) * 3600
                                
                                segments.append({
                                    'start': start_sec,
                                    'text': text
                                })
                except:
                    pass
        
        if segments:
            json_path = f'{SUBS_DIR}/{VID}_transcript.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'video_id': VID,
                    'title': '삼성전자 사야 돼요?',
                    'segments': segments
                }, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ Also saved {len(segments)} segments to JSON")
        
        print(f"\n🎉 SUCCESS via Invidious: {instance}")
        break
        
    except urllib.error.HTTPError as e:
        print(f"  ❌ HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        
else:
    print(f"\n❌ All Invidious instances failed")