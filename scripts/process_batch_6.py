#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
첫 번째 배치(배치 6) 처리 전용 스크립트
"""

import sys
sys.path.append('.')

from sesang101_analyze import Sesang101Analyzer
import os
import glob
import time

print('=== 배치 6 처리 시작 ===')
analyzer = Sesang101Analyzer()

# 자막 파일 목록
subtitle_files = glob.glob(os.path.join(analyzer.subs_dir, "*.json"))
subtitle_files = [f for f in subtitle_files if not f.endswith('_failed.txt')]
subtitle_files.sort()

print(f"[INFO] 발견된 자막 파일: {len(subtitle_files)}개")

# 처리되지 않은 파일들만 필터링
unprocessed_files = []
for subtitle_file in subtitle_files:
    video_id = os.path.basename(subtitle_file).replace('.json', '')
    if video_id not in analyzer.processed_video_ids:
        unprocessed_files.append(subtitle_file)

print(f"[INFO] 처리할 영상: {len(unprocessed_files)}개")

# 배치 6 (첫 20개)
batch_size = 20
batch_files = unprocessed_files[:batch_size]
actual_batch_num = 6

print(f"\n=== 배치 {actual_batch_num} ({len(batch_files)}개) 처리 ===")

# 영상 제목 로드
video_titles = analyzer.load_video_titles()

# 각 영상 처리
for i, subtitle_file in enumerate(batch_files):
    video_id = os.path.basename(subtitle_file).replace('.json', '')
    print(f"\n[{i+1}/{len(batch_files)}] 처리 중: {video_id}")
    
    success = analyzer.process_video(video_id, subtitle_file, video_titles)
    
    if success:
        analyzer.results['stats']['processed'] += 1
    else:
        analyzer.results['stats']['skipped'] += 1
    
    print(f"[INFO] 진행률: {i+1}/{len(batch_files)} ({100*(i+1)/len(batch_files):.1f}%)")

# 배치 완료 후 중간 저장
analyzer.save_intermediate_results(actual_batch_num)

# 요약 출력
print(f"\n=== 배치 {actual_batch_num} 완료 ===")
print(f"처리 완료: {analyzer.results['stats']['processed']}개")
print(f"스킵: {analyzer.results['stats']['skipped']}개")
print(f"오류: {len(analyzer.results['errors'])}개")
print(f"발견된 시그널: {analyzer.results['stats']['signals_found']}개")