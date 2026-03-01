"""Selenium v3 - driver.get()으로 자막 URL 직접 navigate"""
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

def get_caption_url(driver, vid):
    """영상 페이지에서 captionTracks URL 추출"""
    url = f'https://www.youtube.com/watch?v={vid}'
    driver.get(url)
    time.sleep(5)
    
    page_source = driver.page_source
    caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_source)
    if not caption_match:
        return None
    
    tracks = json.loads(caption_match.group(1).replace('\\u0026', '&'))
    ko_track = next((t for t in tracks if t.get('languageCode') == 'ko'), None)
    track = ko_track or (tracks[0] if tracks else None)
    if not track:
        return None
    
    return track.get('baseUrl', ''), track.get('languageCode', '?')

def fetch_via_navigate(driver, caption_url):
    """driver.get()으로 자막 URL navigate → body text 파싱"""
    full_url = caption_url + ('&' if '?' in caption_url else '?') + 'fmt=json3'
    driver.get(full_url)
    time.sleep(3)
    
    from selenium.webdriver.common.by import By
    body = driver.find_element(By.TAG_NAME, 'body').text
    
    if not body or len(body) < 50:
        # pre 태그일 수도
        try:
            body = driver.find_element(By.TAG_NAME, 'pre').text
        except:
            pass
    
    if not body or len(body) < 50:
        # page_source에서 추출
        body = driver.page_source
        # HTML 태그 제거
        match = re.search(r'<pre[^>]*>(.*?)</pre>', body, re.DOTALL)
        if match:
            body = match.group(1)
    
    if not body or len(body) < 50:
        return None
    
    data = json.loads(body)
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

def main():
    print("=== Selenium v3: navigate to caption URL ===")
    driver = setup_driver()
    print("WebDriver ready\n")
    
    results = []
    for prefix, vid in VIDEOS:
        out_path = f'{SUBS_DIR}/{prefix}_{vid}.json'
        
        if os.path.exists(out_path):
            try:
                d = json.load(open(out_path, 'r', encoding='utf-8'))
                segs = d.get('segments', d.get('subtitles', []))
                if segs and len(segs) > 10:
                    print(f"SKIP {vid} ({prefix}): {len(segs)} segs exist")
                    results.append((vid, prefix, len(segs), 'skipped'))
                    continue
            except:
                pass
        
        print(f"EXTRACT {vid} ({prefix}):")
        try:
            info = get_caption_url(driver, vid)
            if not info:
                print("  No caption URL found")
                results.append((vid, prefix, 0, 'no-url'))
                time.sleep(3)
                continue
            
            caption_url, lang = info
            print(f"  Caption URL found (lang={lang})")
            
            segments = fetch_via_navigate(driver, caption_url)
            if segments:
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'video_id': vid,
                        'channel': prefix,
                        'subtitles': segments
                    }, f, ensure_ascii=False, indent=2)
                print(f"  OK: {len(segments)} segments\n")
                results.append((vid, prefix, len(segments), 'ok'))
            else:
                print(f"  FAIL: fetch returned nothing\n")
                results.append((vid, prefix, 0, 'fail'))
        except Exception as e:
            print(f"  ERROR: {e}\n")
            results.append((vid, prefix, 0, 'error'))
        
        time.sleep(4)
    
    driver.quit()
    
    print("=== 결과 ===")
    ok = sum(1 for _,_,_,s in results if s == 'ok')
    print(f"성공: {ok}/{len(results)}")
    for vid, prefix, count, status in results:
        emoji = '✅' if status in ('ok','skipped') else '❌'
        print(f"  {emoji} {prefix}/{vid}: {status} ({count} segs)")

if __name__ == '__main__':
    main()
