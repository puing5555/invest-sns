"""YouTube 페이지에서 자막 URL을 직접 추출하여 자막 텍스트 가져오기"""
import requests
import re
import json
import time
import random
from bs4 import BeautifulSoup

def extract_subtitle(video_id, lang='ko'):
    """YouTube 영상에서 자막 텍스트 추출"""
    url = f'https://www.youtube.com/watch?v={video_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        
        # captionTracks에서 자막 URL 찾기
        pattern = r'"captionTracks":\[(.*?)\]'
        match = re.search(pattern, r.text)
        if not match:
            return None, "No captionTracks found"
        
        tracks_str = '[' + match.group(1) + ']'
        # JSON 파싱을 위해 이스케이프 처리
        tracks_str = tracks_str.replace('\\"', '"')
        
        try:
            tracks = json.loads(tracks_str)
        except json.JSONDecodeError:
            # 수동 파싱
            base_urls = re.findall(r'"baseUrl":"(.*?)"', match.group(1))
            lang_codes = re.findall(r'"languageCode":"(.*?)"', match.group(1))
            
            tracks = []
            for i, (bu, lc) in enumerate(zip(base_urls, lang_codes)):
                tracks.append({'baseUrl': bu.replace('\\u0026', '&'), 'languageCode': lc})
        
        # 한국어 자막 URL 찾기
        caption_url = None
        for track in tracks:
            if isinstance(track, dict) and track.get('languageCode', '').startswith(lang):
                caption_url = track.get('baseUrl', '')
                if caption_url:
                    caption_url = caption_url.replace('\\u0026', '&')
                break
        
        if not caption_url:
            return None, f"No {lang} caption found"
        
        # 자막 XML 다운로드
        r2 = requests.get(caption_url, headers=headers, timeout=15)
        if r2.status_code != 200:
            return None, f"Caption download failed: HTTP {r2.status_code}"
        
        # XML에서 텍스트 추출
        soup = BeautifulSoup(r2.text, 'html.parser')
        texts = []
        for t in soup.find_all('text'):
            text = t.get_text()
            if text.strip():
                texts.append(text.strip())
        
        if texts:
            return ' '.join(texts), None
        
        return None, "Empty caption"
        
    except Exception as e:
        return None, str(e)


def batch_extract(video_ids, delay_range=(2, 4)):
    """여러 영상의 자막을 배치로 추출"""
    results = {}
    success = 0
    fail = 0
    
    for i, vid in enumerate(video_ids):
        print(f"  [{i+1}/{len(video_ids)}] {vid}...", end=' ')
        
        text, error = extract_subtitle(vid)
        
        if text:
            results[vid] = text
            success += 1
            print(f"OK ({len(text)} chars)")
        else:
            print(f"FAIL ({error})")
            fail += 1
        
        # 레이트 리밋
        if i < len(video_ids) - 1:
            delay = random.uniform(*delay_range)
            time.sleep(delay)
        
        # 20개마다 5분 휴식
        if (i + 1) % 20 == 0 and i < len(video_ids) - 1:
            print(f"  [PAUSE] 20개 완료, 5분 휴식...")
            time.sleep(300)
    
    print(f"\n  결과: {success} 성공, {fail} 실패")
    return results


if __name__ == "__main__":
    # 테스트: 첫 번째 영상
    video_id = 'Ke7gQMbIFLI'
    print(f"Testing video: {video_id}")
    text, error = extract_subtitle(video_id)
    if text:
        print(f"Success! {len(text)} chars")
        print(f"Sample: {text[:300]}")
    else:
        print(f"Failed: {error}")
