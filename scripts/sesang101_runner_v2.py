#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 나머지 73개 영상 배치 분석 v2
- 직접 API 호출 (signal_analyzer_rest.py 우회)
- 더 안정적인 timeout 및 재시도
"""

import os
import sys
import json
import time
import glob
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

sys.path.append(os.path.dirname(__file__))
from pipeline_config import PipelineConfig

# ===== 설정 =====
SUBS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'subs', 'sesang101')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..')
VIDEOS_FILE = os.path.join(os.path.dirname(__file__), 'sesang101_videos.txt')
BATCH_SIZE = 20
START_BATCH = 6
API_DELAY = 5
BATCH_BREAK = 120
CHANNEL_URL = 'https://www.youtube.com/@sesang101'

config = PipelineConfig()
PROMPT_TEMPLATE = config.load_prompt()

HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': config.ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
}

# ===== 헬퍼 함수들 =====
def load_processed_ids():
    processed = set()
    for i in range(1, 100):
        batch_file = os.path.join(RESULTS_DIR, f'sesang101_analysis_results_batch_{i}.json')
        if not os.path.exists(batch_file):
            continue
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data.get('processed', []):
                processed.add(item['video_id'])
            for item in data.get('skipped', []):
                processed.add(item['video_id'])
        except:
            pass
    return processed

def load_titles():
    titles = {}
    if not os.path.exists(VIDEOS_FILE):
        return titles
    for enc in ['utf-8', 'cp949', 'utf-16', 'latin1']:
        try:
            with open(VIDEOS_FILE, 'r', encoding=enc) as f:
                for line in f:
                    line = line.strip()
                    if '|||' in line:
                        vid, title = line.split('|||', 1)
                        titles[vid.strip()] = title.strip()
            break
        except UnicodeDecodeError:
            continue
    return titles

def extract_subtitle(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            segments = json.load(f)
        if not isinstance(segments, list):
            return ""
        return " ".join(s.get('text', '') for s in segments if isinstance(s, dict)).strip()
    except:
        return ""

def make_api_request(payload):
    """API 요청 함수 (매우 짧은 타임아웃)"""
    return requests.post(
        'https://api.anthropic.com/v1/messages',
        headers=HEADERS,
        json=payload,
        timeout=(5, 30)  # 매우 짧은 타임아웃
    )

def analyze_video(title, url, subtitle, max_retries=5):
    """직접 Claude API 호출 (ThreadPoolExecutor 타임아웃)"""
    prompt = PROMPT_TEMPLATE.replace('{CHANNEL_URL}', CHANNEL_URL)
    prompt += f"""

=== 분석 대상 영상 ===
제목: {title}
URL: {url}

=== 자막 내용 ===
{subtitle}

=== 분석 지시사항 ===
위 영상의 자막을 프롬프트 규칙에 따라 분석하고, JSON 형태로 시그널을 추출해주세요.
"""
    
    payload = {
        'model': 'claude-3-haiku-20240307',
        'max_tokens': 4000,
        'messages': [{'role': 'user', 'content': prompt}]
    }
    
    for attempt in range(max_retries):
        try:
            print(f"  [API] 시도 {attempt+1}/{max_retries}...")
            
            # ThreadPoolExecutor로 강제 타임아웃 (45초)
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(make_api_request, payload)
                try:
                    resp = future.result(timeout=45)
                except FutureTimeoutError:
                    print(f"  [FORCE_TIMEOUT] 45초 강제 종료")
                    time.sleep(5)  # 잠깐 대기 후 재시도
                    continue
            
            if resp.status_code == 429:
                print(f"  [RATE] 429 - 60초 대기...")
                time.sleep(60)
                continue
            
            if resp.status_code == 529:
                print(f"  [529] 서버 과부하 - 30초 대기...")
                time.sleep(30)
                continue
                
            if resp.status_code != 200:
                print(f"  [ERR] HTTP {resp.status_code}: {resp.text[:100]}")
                time.sleep(5)
                continue
            
            data = resp.json()
            text = data['content'][0]['text']
            
            # JSON 추출
            if '```json' in text:
                start = text.find('```json') + 7
                end = text.find('```', start)
                json_str = text[start:end].strip()
            elif '{' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                json_str = text[start:end]
            else:
                print(f"  [SKIP] JSON 없음")
                return None
            
            result = json.loads(json_str)
            signals = result.get('signals', [])
            return signals
            
        except json.JSONDecodeError as e:
            print(f"  [ERR] JSON 파싱: {e}")
            continue
        except requests.exceptions.Timeout:
            print(f"  [TIMEOUT] requests 타임아웃")
            continue
        except Exception as e:
            print(f"  [ERR] {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
    
    return None

# ===== 메인 =====
def main():
    print(f"=== 세상학개론 분석 v2 시작 ({datetime.now().strftime('%H:%M:%S')}) ===")
    
    processed_ids = load_processed_ids()
    print(f"[INFO] 이미 처리됨: {len(processed_ids)}개")
    
    all_files = sorted(glob.glob(os.path.join(SUBS_DIR, '*.json')))
    remaining = [(os.path.basename(f).replace('.json', ''), f) for f in all_files
                 if os.path.basename(f).replace('.json', '') not in processed_ids]
    print(f"[INFO] 처리할 영상: {len(remaining)}개")
    
    if not remaining:
        print("[DONE] 모두 처리됨!")
        return
    
    titles = load_titles()
    total_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE
    total_signals = 0
    total_analyzed = 0
    
    for batch_idx in range(total_batches):
        batch_num = START_BATCH + batch_idx
        start = batch_idx * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(remaining))
        batch = remaining[start:end]
        
        print(f"\n{'='*50}")
        print(f"배치 {batch_num} ({len(batch)}개, {start+1}-{end}/{len(remaining)})")
        print(f"{'='*50}")
        
        batch_results = {
            'batch_num': batch_num,
            'start_time': datetime.now().isoformat(),
            'processed': [],
            'skipped': [],
            'errors': [],
            'stats': {'processed': 0, 'skipped': 0, 'errors': 0, 'signals_found': 0}
        }
        
        for i, (video_id, filepath) in enumerate(batch):
            print(f"\n[{i+1}/{len(batch)}] {video_id}")
            
            subtitle = extract_subtitle(filepath)
            if len(subtitle) < 100:
                print(f"  [SKIP] 자막 짧음 ({len(subtitle)}자)")
                batch_results['skipped'].append({'video_id': video_id, 'reason': '자막 짧음'})
                batch_results['stats']['skipped'] += 1
                continue
            
            title = titles.get(video_id, f'세상학개론 {video_id}')
            url = f'https://www.youtube.com/watch?v={video_id}'
            
            print(f"  제목: {title[:50]}")
            print(f"  자막: {len(subtitle)}자")
            
            signals = analyze_video(title, url, subtitle)
            
            if signals:
                print(f"  [OK] {len(signals)}개 시그널")
                for s in signals:
                    print(f"    - {s.get('stock','?')} | {s.get('signal','?')} | {s.get('confidence','?')}")
                
                batch_results['processed'].append({
                    'video_id': video_id,
                    'title': title,
                    'signals_found': len(signals),
                    'signals': signals,
                    'timestamp': datetime.now().isoformat()
                })
                batch_results['stats']['processed'] += 1
                batch_results['stats']['signals_found'] += len(signals)
                total_signals += len(signals)
                total_analyzed += 1
            else:
                print(f"  [SKIP] 시그널 없음")
                batch_results['skipped'].append({'video_id': video_id, 'reason': '시그널 없음', 'title': title})
                batch_results['stats']['skipped'] += 1
            
            if i < len(batch) - 1:
                time.sleep(API_DELAY)
        
        # 배치 저장
        batch_results['end_time'] = datetime.now().isoformat()
        batch_file = os.path.join(RESULTS_DIR, f'sesang101_analysis_results_batch_{batch_num}.json')
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, ensure_ascii=False, indent=2)
        print(f"\n[SAVE] 배치 {batch_num} → {os.path.basename(batch_file)}")
        print(f"  분석: {batch_results['stats']['processed']}개, 스킵: {batch_results['stats']['skipped']}개, 시그널: {batch_results['stats']['signals_found']}개")
        
        if batch_idx < total_batches - 1:
            print(f"[BREAK] {BATCH_BREAK}초 휴식...")
            time.sleep(BATCH_BREAK)
    
    print(f"\n{'='*50}")
    print(f"완료! {total_analyzed}개 영상에서 {total_signals}개 시그널 발견")
    print(f"시간: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == '__main__':
    main()
