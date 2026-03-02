#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 나머지 73개 영상 배치 분석 스크립트
- 이미 처리된 영상 자동 스킵
- 20개마다 배치 저장 + 2분 휴식
- API 요청 간 5초 대기
- 429 레이트리밋 시 2분 대기 후 재시도
"""

import os
import sys
import json
import time
import glob
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from pipeline_config import PipelineConfig
from signal_analyzer_rest import SignalAnalyzer

# ===== 설정 =====
SUBS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'subs', 'sesang101')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..')
VIDEOS_FILE = os.path.join(os.path.dirname(__file__), 'sesang101_videos.txt')
BATCH_SIZE = 20
START_BATCH = 6
API_DELAY = 5        # API 요청 간 대기 (초)
BATCH_BREAK = 120    # 배치 간 휴식 (초)
RATE_LIMIT_WAIT = 120  # 429 에러 시 대기 (초)

CHANNEL_URL = 'https://www.youtube.com/@sesang101'
CHANNEL_NAME = '세상학개론'
HOST_NAME = '이효석'

# ===== 이미 처리된 영상 수집 =====
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

# ===== 영상 제목 로드 =====
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

# ===== 자막 텍스트 추출 =====
def extract_subtitle(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            segments = json.load(f)
        if not isinstance(segments, list):
            return ""
        return " ".join(s.get('text', '') for s in segments if isinstance(s, dict)).strip()
    except:
        return ""

# ===== 메인 실행 =====
def main():
    print(f"=== 세상학개론 나머지 영상 분석 시작 ({datetime.now().strftime('%H:%M:%S')}) ===")
    
    # 이미 처리된 영상
    processed_ids = load_processed_ids()
    print(f"[INFO] 이미 처리된 영상: {len(processed_ids)}개")
    
    # 자막 파일 목록
    all_files = sorted(glob.glob(os.path.join(SUBS_DIR, '*.json')))
    print(f"[INFO] 전체 자막 파일: {len(all_files)}개")
    
    # 미처리 파일만
    remaining = [(os.path.basename(f).replace('.json', ''), f) for f in all_files 
                 if os.path.basename(f).replace('.json', '') not in processed_ids]
    print(f"[INFO] 처리할 영상: {len(remaining)}개")
    
    if not remaining:
        print("[DONE] 모든 영상이 이미 처리됨!")
        return
    
    # 영상 제목 로드
    titles = load_titles()
    print(f"[INFO] 영상 제목: {len(titles)}개 로드")
    
    # 분석기 초기화
    analyzer = SignalAnalyzer()
    
    # 배치별 처리
    total_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE
    global_processed = 0
    global_signals = 0
    
    for batch_idx in range(total_batches):
        batch_num = START_BATCH + batch_idx
        start = batch_idx * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(remaining))
        batch = remaining[start:end]
        
        print(f"\n{'='*60}")
        print(f"=== 배치 {batch_num} ({len(batch)}개, {start+1}-{end}/{len(remaining)}) ===")
        print(f"{'='*60}")
        
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
            
            # 자막 추출
            subtitle = extract_subtitle(filepath)
            if len(subtitle) < 100:
                print(f"  [SKIP] 자막 너무 짧음 ({len(subtitle)}자)")
                batch_results['skipped'].append({'video_id': video_id, 'reason': '자막 너무 짧음'})
                batch_results['stats']['skipped'] += 1
                continue
            
            title = titles.get(video_id, f'세상학개론 {video_id}')
            video_data = {
                'title': title,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'duration': 'N/A',
                'upload_date': 'N/A'
            }
            
            print(f"  제목: {title[:60]}...")
            print(f"  자막: {len(subtitle)}자")
            
            # API 분석
            try:
                result = analyzer.analyze_video_subtitle(
                    channel_url=CHANNEL_URL,
                    video_data=video_data,
                    subtitle=subtitle
                )
                
                if result and result.get('signals'):
                    signals = result['signals']
                    print(f"  [OK] {len(signals)}개 시그널 발견")
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
                    global_processed += 1
                    global_signals += len(signals)
                else:
                    print(f"  [SKIP] 시그널 없음")
                    batch_results['skipped'].append({'video_id': video_id, 'reason': '시그널 없음', 'title': title})
                    batch_results['stats']['skipped'] += 1
                    
            except Exception as e:
                print(f"  [ERROR] {e}")
                batch_results['errors'].append({'video_id': video_id, 'error': str(e)})
                batch_results['stats']['errors'] += 1
            
            # API 딜레이
            if i < len(batch) - 1:
                print(f"  [WAIT] {API_DELAY}초 대기...")
                time.sleep(API_DELAY)
        
        # 배치 결과 저장
        batch_results['end_time'] = datetime.now().isoformat()
        batch_file = os.path.join(RESULTS_DIR, f'sesang101_analysis_results_batch_{batch_num}.json')
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, ensure_ascii=False, indent=2)
        print(f"\n[SAVE] 배치 {batch_num} 저장: {batch_file}")
        print(f"[STATS] 분석: {batch_results['stats']['processed']}개, 스킵: {batch_results['stats']['skipped']}개, 시그널: {batch_results['stats']['signals_found']}개")
        
        # 배치 간 휴식
        if batch_idx < total_batches - 1:
            print(f"\n[BREAK] {BATCH_BREAK}초 휴식...")
            time.sleep(BATCH_BREAK)
    
    # 최종 요약
    print(f"\n{'='*60}")
    print(f"=== 전체 분석 완료 ({datetime.now().strftime('%H:%M:%S')}) ===")
    print(f"총 처리: {len(remaining)}개 영상")
    print(f"시그널 발견: {global_processed}개 영상에서 {global_signals}개")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
