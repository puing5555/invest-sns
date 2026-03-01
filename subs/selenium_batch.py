"""Selenium 배치 자막 추출 - 7개 영상"""
import sys, io, json, os, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

SUBS_DIR = 'C:/Users/Mario/work/subs'

VIDEOS = [
    ('syuka', 'ksA4IT452_4', '삼성전자 사야 돼요?'),
    ('syuka', 'nm5zQxZSkbk', '비트코인/스트래티지'),
    ('syuka', 'XveVkr3JHs4', '코스피'),
    ('syuka', 'N7xO-UWCM5w', '삼성전자 시총'),
    ('hyoseok', 'B5owNUs_DFw', '이효석'),
    ('hyoseok', 'bmXgryWXNrw', '이효석'),
    ('dalrant', '5mvn3PfKf9Y', '달란트투자'),
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

def extract_captions(driver, vid):
    """YouTube 페이지에서 captionTracks URL 추출 후 자막 다운로드"""
    url = f'https://www.youtube.com/watch?v={vid}'
    print(f"  Loading {url}")
    driver.get(url)
    time.sleep(5)
    
    page_source = driver.page_source
    
    # captionTracks에서 자막 URL 추출
    caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_source)
    if caption_match:
        try:
            tracks = json.loads(caption_match.group(1).replace('\\u0026', '&'))
            # 한국어 우선, 없으면 첫 번째
            ko_track = next((t for t in tracks if t.get('languageCode') == 'ko'), None)
            track = ko_track or (tracks[0] if tracks else None)
            if track:
                base_url = track.get('baseUrl', '')
                lang = track.get('languageCode', '?')
                print(f"  Found caption track: lang={lang}")
                segs = fetch_json3(base_url)
                if segs:
                    return segs
        except Exception as e:
            print(f"  captionTracks parse error: {e}")
    
    # fallback: baseUrl 패턴
    urls = re.findall(r'"baseUrl":"([^"]*api/timedtext[^"]*)"', page_source)
    urls = [u.replace('\\u0026', '&') for u in urls]
    if urls:
        print(f"  Found {len(urls)} timedtext URLs")
        for u in urls[:3]:
            segs = fetch_json3(u)
            if segs:
                return segs
    
    print("  No caption data found")
    return None

def fetch_json3(base_url):
    """자막 URL에서 json3 포맷으로 다운로드"""
    import urllib.request, ssl
    ctx = ssl.create_default_context()
    
    caption_url = base_url + ('&' if '?' in base_url else '?') + 'fmt=json3'
    req = urllib.request.Request(caption_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
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
        print(f"  fetch_json3 error: {e}")
        return None

def main():
    print("=== Selenium 배치 자막 추출 ===")
    driver = setup_driver()
    print("WebDriver ready\n")
    
    results = []
    for prefix, vid, title in VIDEOS:
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
            segments = extract_captions(driver, vid)
            if segments:
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'video_id': vid,
                        'channel': prefix,
                        'subtitles': segments
                    }, f, ensure_ascii=False, indent=2)
                print(f"  OK: {len(segments)} segments saved")
                results.append((vid, prefix, len(segments), 'ok'))
            else:
                print(f"  FAIL: no captions")
                results.append((vid, prefix, 0, 'fail'))
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((vid, prefix, 0, 'error'))
        
        time.sleep(3)  # rate limit 방지
    
    driver.quit()
    
    print("\n=== 결과 ===")
    for vid, prefix, count, status in results:
        print(f"  {prefix}/{vid}: {status} ({count} segs)")

if __name__ == '__main__':
    main()
