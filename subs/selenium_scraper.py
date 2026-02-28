"""Selenium을 이용한 YouTube 자막 크롤링"""
import sys
import io
import json
import os
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

print("=== Selenium 크롤링 시도 ===")

def install_selenium():
    """Selenium 설치"""
    try:
        import selenium
        print("✅ Selenium 이미 설치됨")
        return True
    except ImportError:
        print("Selenium 설치 중...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium'], check=True)
        print("✅ Selenium 설치 완료")
        return True

def download_webdriver():
    """ChromeDriver 다운로드"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("ChromeDriver 설정 중...")
        
        # Chrome 옵션 설정
        options = Options()
        options.add_argument('--headless')  # 헤드리스 모드
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        
        # WebDriver 설정
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ WebDriver 설정 완료")
        return driver
        
    except Exception as e:
        print(f"❌ WebDriver 설정 실패: {e}")
        return None

def scrape_youtube_captions(driver):
    """YouTube 페이지에서 자막 크롤링"""
    try:
        url = f'https://www.youtube.com/watch?v={VID}'
        print(f"YouTube 페이지 로드: {url}")
        
        driver.get(url)
        time.sleep(5)  # 페이지 로드 대기
        
        # 자막 버튼 찾기
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print("자막 버튼 찾는 중...")
        
        # 자막/CC 버튼 클릭 시도
        try:
            # 여러 가능한 자막 버튼 셀렉터
            caption_selectors = [
                "button[aria-label*='자막']",
                "button[aria-label*='Captions']", 
                ".ytp-subtitles-button",
                ".ytp-caption-button",
                "button[data-tooltip-target-id*='caption']"
            ]
            
            caption_button = None
            for selector in caption_selectors:
                try:
                    caption_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ 자막 버튼 발견: {selector}")
                    break
                except:
                    continue
            
            if caption_button:
                caption_button.click()
                print("✅ 자막 버튼 클릭")
                time.sleep(2)
                
                # 자막 텍스트 추출
                subtitle_text = extract_subtitle_text(driver)
                if subtitle_text:
                    return subtitle_text
                    
        except Exception as e:
            print(f"❌ 자막 버튼 클릭 실패: {e}")
            
        # 대안: 페이지 소스에서 자막 데이터 추출
        print("페이지 소스에서 자막 데이터 검색...")
        page_source = driver.page_source
        
        # 자막 데이터 패턴 검색
        import re
        
        # captionTracks 패턴 검색
        caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', page_source)
        if caption_match:
            print("✅ captionTracks 데이터 발견")
            return parse_caption_tracks(caption_match.group(1))
        
        # 다른 자막 데이터 패턴들 시도
        subtitle_patterns = [
            r'"timedtext".*?"url":"([^"]+)"',
            r'"baseUrl":"([^"]*api/timedtext[^"]*)"'
        ]
        
        for pattern in subtitle_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"✅ 자막 URL 패턴 발견: {len(matches)}개")
                return fetch_from_urls(matches)
        
        print("❌ 자막 데이터를 찾을 수 없음")
        return None
        
    except Exception as e:
        print(f"❌ 크롤링 오류: {e}")
        return None

def extract_subtitle_text(driver):
    """활성화된 자막에서 텍스트 추출"""
    try:
        from selenium.webdriver.common.by import By
        
        # 자막 컨테이너 찾기
        subtitle_selectors = [
            ".caption-window",
            ".ytp-caption-segment", 
            ".captions-text",
            "[class*='caption']"
        ]
        
        for selector in subtitle_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    texts = [elem.text for elem in elements if elem.text.strip()]
                    if texts:
                        print(f"✅ 자막 텍스트 추출: {len(texts)}개")
                        return texts
            except:
                continue
                
    except Exception as e:
        print(f"❌ 자막 텍스트 추출 실패: {e}")
    
    return None

def parse_caption_tracks(tracks_json):
    """captionTracks JSON 파싱"""
    try:
        tracks = json.loads(tracks_json.replace('\\u0026', '&'))
        for track in tracks:
            if track.get('languageCode') == 'ko':
                base_url = track.get('baseUrl', '')
                if base_url:
                    print(f"✅ 한국어 자막 URL 발견")
                    return fetch_caption_from_url(base_url)
    except Exception as e:
        print(f"❌ captionTracks 파싱 실패: {e}")
    return None

def fetch_caption_from_url(url):
    """자막 URL에서 실제 자막 데이터 가져오기"""
    try:
        import urllib.request
        
        caption_url = url + '&fmt=json3'
        req = urllib.request.Request(caption_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
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
        
        return segments
        
    except Exception as e:
        print(f"❌ 자막 URL 페치 실패: {e}")
        return None

def fetch_from_urls(urls):
    """여러 URL에서 자막 시도"""
    for url in urls[:3]:  # 처음 3개만 시도
        try:
            print(f"URL 시도: {url[:80]}...")
            result = fetch_caption_from_url(url)
            if result:
                return result
        except:
            continue
    return None

# 메인 실행
if install_selenium():
    try:
        # webdriver_manager 설치
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'webdriver_manager'], check=True)
        
        driver = download_webdriver()
        if driver:
            try:
                segments = scrape_youtube_captions(driver)
                
                if segments:
                    # JSON 저장
                    json_path = f'{SUBS_DIR}/{VID}_transcript.json'
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            'video_id': VID,
                            'title': '삼성전자 사야 돼요?',
                            'method': 'selenium',
                            'segments': segments
                        }, f, ensure_ascii=False, indent=2)
                    
                    print(f"🎉 Selenium 크롤링 성공! {len(segments)}개 세그먼트")
                    print(f"저장 경로: {json_path}")
                else:
                    print("❌ Selenium 크롤링 실패")
                    
            finally:
                driver.quit()
                print("✅ WebDriver 종료")
        
    except Exception as e:
        print(f"❌ Selenium 전체 실패: {e}")

# 결과 확인
json_path = f'{SUBS_DIR}/{VID}_transcript.json'
if os.path.exists(json_path):
    size = os.path.getsize(json_path)
    print(f"📁 최종 파일: {json_path} ({size} bytes)")
else:
    print("❌ 최종 파일 없음")