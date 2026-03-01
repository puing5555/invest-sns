"""Selenium 배치 자막 추출 v2 - driver.execute_cdp_cmd로 자막 fetch"""
import sys, io, json, os, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

SUBS_DIR = 'C:/Users/Mario/work/subs'

VIDEOS = [
    ('syuka', 'ksA4IT452_4'),
    ('syuka', 'nm5zQxZSkbk'),
    ('syuka', 'XveVkr3JHs4'),
    ('syuka', 'N7xO-UWCM5w'),
    ('hyoseok', 'B5owNUs_DFw'),
    ('hyoseok', 'bmXgryWXNrw'),
    ('dalrant', '5mvn3PfKf9Y'),
]

def setup_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_captions_via_js(driver, vid):
    """Selenium JS 실행으로 자막 URL fetch (브라우저 세션/쿠키 활용)"""
    url = f'https://www.youtube.com/watch?v={vid}'
    print(f"  Loading {url}")
    driver.get(url)
    time.sleep(6)
    
    page_source = driver.page_source
    
    # captionTracks에서 자막 URL 추출
    caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_source)
    if not caption_match:
        print("  No captionTracks found")
        return None
    
    try:
        tracks = json.loads(caption_match.group(1).replace('\\u0026', '&'))
        ko_track = next((t for t in tracks if t.get('languageCode') == 'ko'), None)
        track = ko_track or (tracks[0] if tracks else None)
        if not track:
            print("  No tracks available")
            return None
        
        base_url = track.get('baseUrl', '')
        lang = track.get('languageCode', '?')
        print(f"  Found track: lang={lang}")
        
        # 브라우저 내에서 fetch로 자막 다운로드 (쿠키/세션 자동 포함)
        caption_url = base_url + ('&' if '?' in base_url else '?') + 'fmt=json3'
        
        js_code = f"""
        return await fetch("{caption_url.replace('"', '\\"')}")
            .then(r => r.text())
            .catch(e => "ERROR:" + e.message);
        """
        
        result = driver.execute_script(js_code)
        
        if not result or result.startswith('ERROR:'):
            print(f"  JS fetch failed: {result}")
            # fallback: XMLHttpRequest
            js_code2 = f"""
            var xhr = new XMLHttpRequest();
            xhr.open('GET', "{caption_url.replace('"', '\\"')}", false);
            xhr.send();
            return xhr.responseText;
            """
            result = driver.execute_script(js_code2)
        
        if not result or len(result) < 100:
            print(f"  Empty or short response ({len(result) if result else 0} chars)")
            return None
        
        data = json.loads(result)
        events = data.get('events', [])
        segments = []
        for evt in events:
            segs = evt.get('segs', [])
            text = ''.join(s.get('utf8', '') for s in segs).strip()
            if text and text != '\n':
                segments.append({
                    'start': evt.get('tStartMs', 0) / 1000.0,
                    'duration': evt.get('dDurationMs', 0) / 1000.0,
                    'text': text
                })
        
        return segments if segments else None
        
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    print("=== Selenium 배치 자막 추출 v2 (JS fetch) ===")
    driver = setup_driver()
    print("WebDriver ready\n")
    
    results = []
    for prefix, vid in VIDEOS:
        out_path = f'{SUBS_DIR}/{prefix}_{vid}.json'
        
        # 이미 자막이 있는지 확인
        if os.path.exists(out_path):
            try:
                d = json.load(open(out_path, 'r', encoding='utf-8'))
                segs = d.get('segments', d.get('subtitles', []))
                if segs and len(segs) > 10:
                    print(f"SKIP {vid} ({prefix}): already has {len(segs)} segments")
                    results.append((vid, prefix, len(segs), 'skipped'))
                    continue
            except:
                pass
        
        print(f"EXTRACT {vid} ({prefix}):")
        try:
            segments = extract_captions_via_js(driver, vid)
            if segments:
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'video_id': vid,
                        'channel': prefix,
                        'subtitles': segments
                    }, f, ensure_ascii=False, indent=2)
                print(f"  OK: {len(segments)} segments saved\n")
                results.append((vid, prefix, len(segments), 'ok'))
            else:
                print(f"  FAIL: no captions\n")
                results.append((vid, prefix, 0, 'fail'))
        except Exception as e:
            print(f"  ERROR: {e}\n")
            results.append((vid, prefix, 0, 'error'))
        
        time.sleep(4)
    
    driver.quit()
    
    print("=== 결과 ===")
    for vid, prefix, count, status in results:
        print(f"  {prefix}/{vid}: {status} ({count} segs)")

if __name__ == '__main__':
    main()
