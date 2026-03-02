#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quick_test.py - 빠른 테스트
"""

import os
import sys
import glob

sys.path.append(os.path.dirname(__file__))

try:
    from sesang101_analyze import Sesang101Analyzer
    
    print("=== 빠른 테스트 시작 ===")
    
    analyzer = Sesang101Analyzer()
    print("분석기 생성 완료")
    
    # 자막 파일 확인
    subs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'subs', 'sesang101')
    subtitle_files = glob.glob(os.path.join(subs_dir, "*.json"))
    subtitle_files = [f for f in subtitle_files if not f.endswith('_failed.txt')]
    
    print(f"자막 파일 수: {len(subtitle_files)}")
    
    if len(subtitle_files) > 0:
        print(f"첫 번째 파일: {os.path.basename(subtitle_files[0])}")
        
        # 첫 번째 파일 처리 시도
        video_id = os.path.basename(subtitle_files[0]).replace('.json', '')
        video_titles = analyzer.load_video_titles()
        
        print("비디오 제목 로드 완료")
        print(f"제목 수: {len(video_titles)}")
        
        success = analyzer.process_video(video_id, subtitle_files[0], video_titles)
        print(f"처리 결과: {success}")
    
    print("=== 테스트 완료 ===")
    
except Exception as e:
    print(f"테스트 실패: {e}")
    import traceback
    traceback.print_exc()