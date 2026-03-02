#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from sesang101_analyze import Sesang101Analyzer
import os
import glob

print('=== DEBUG RUN ===')
analyzer = Sesang101Analyzer()

print("=== 세상학개론 98개 자막 분석 시작 ===")
print(f"자막 디렉토리: {analyzer.subs_dir}")
print(f"결과 저장: {analyzer.results_file}")

# 1. 자막 파일 목록
subtitle_files = glob.glob(os.path.join(analyzer.subs_dir, "*.json"))
subtitle_files = [f for f in subtitle_files if not f.endswith('_failed.txt')]
subtitle_files.sort()

print(f"[INFO] 발견된 자막 파일: {len(subtitle_files)}개")

if len(subtitle_files) == 0:
    print(f"[ERROR] 자막 파일을 찾을 수 없습니다: {analyzer.subs_dir}")
else:
    # 전체 파일 처리
    analyzer.results['stats']['total_videos'] = len(subtitle_files)

    # 2. 영상 제목 로드
    video_titles = analyzer.load_video_titles()
    print(f"[INFO] 영상 제목 {len(video_titles)}개 로드")

    # 3. 처리되지 않은 파일들만 필터링
    unprocessed_files = []
    for subtitle_file in subtitle_files:
        video_id = os.path.basename(subtitle_file).replace('.json', '')
        if video_id not in analyzer.processed_video_ids:
            unprocessed_files.append(subtitle_file)

    print(f"[INFO] 처리할 영상: {len(unprocessed_files)}개")
    
    # 배치별 처리 (20개씩, 배치 6부터 시작)
    batch_size = 20
    start_batch = 6  # 기존 배치 1-5는 완료됨
    
    total_batches = (len(unprocessed_files) + batch_size - 1) // batch_size
    print(f"[INFO] 총 배치 수: {total_batches}개")
    
    for batch_idx in range(min(1, total_batches)):  # 첫 번째 배치만 테스트
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(unprocessed_files))
        batch_files = unprocessed_files[start_idx:end_idx]
        
        actual_batch_num = start_batch + batch_idx
        print(f"\n=== 배치 {actual_batch_num}/{start_batch + total_batches - 1} ({len(batch_files)}개) ===")
        
        # 첫 3개 파일만 출력
        for i, file_path in enumerate(batch_files[:3]):
            video_id = os.path.basename(file_path).replace('.json', '')
            print(f"  {i+1}. {video_id}")
        
        if len(batch_files) > 3:
            print(f"  ... 및 {len(batch_files) - 3}개 더")