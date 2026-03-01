#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_sesang101.py - 세상학개론 분석 테스트
"""

import os
import sys
import json
import glob

# 경로 설정
sys.path.append(os.path.dirname(__file__))

try:
    from pipeline_config import PipelineConfig
    print("[OK] pipeline_config import 성공")
    
    config = PipelineConfig()
    print(f"[OK] config 생성 성공")
    print(f"ANTHROPIC_API_KEY: {config.ANTHROPIC_API_KEY[:10]}..." if config.ANTHROPIC_API_KEY else "None")
    print(f"SUPABASE_URL: {config.SUPABASE_URL[:20]}..." if config.SUPABASE_URL else "None")
    
    # 프롬프트 로드 테스트
    prompt = config.load_prompt()
    print(f"[OK] 프롬프트 로드 성공: {len(prompt)}자")
    
except Exception as e:
    print(f"[ERROR] Config 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

try:
    from signal_analyzer_rest import SignalAnalyzer
    print("[OK] signal_analyzer_rest import 성공")
    
    analyzer = SignalAnalyzer()
    print("[OK] SignalAnalyzer 생성 성공")
    
except Exception as e:
    print(f"[ERROR] SignalAnalyzer 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

try:
    from db_inserter_rest import DatabaseInserter
    print("[OK] db_inserter_rest import 성공")
    
    db_inserter = DatabaseInserter()
    print("[OK] DatabaseInserter 생성 성공")
    
except Exception as e:
    print(f"[ERROR] DatabaseInserter 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

# 자막 파일 확인
subs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'subs', 'sesang101')
print(f"[INFO] 자막 디렉토리: {subs_dir}")
print(f"[INFO] 디렉토리 존재: {os.path.exists(subs_dir)}")

if os.path.exists(subs_dir):
    subtitle_files = glob.glob(os.path.join(subs_dir, "*.json"))
    subtitle_files = [f for f in subtitle_files if not f.endswith('_failed.txt')]
    print(f"[INFO] 발견된 자막 파일: {len(subtitle_files)}개")
    
    if subtitle_files:
        # 첫 번째 파일 테스트
        test_file = subtitle_files[0]
        video_id = os.path.basename(test_file).replace('.json', '')
        print(f"[TEST] 테스트 파일: {video_id}")
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                segments = json.load(f)
            
            print(f"[OK] 자막 파일 로드 성공: {len(segments)}개 세그먼트")
            
            # 텍스트 추출
            full_text = ""
            for segment in segments:
                if isinstance(segment, dict) and 'text' in segment:
                    full_text += segment['text'] + " "
            
            full_text = full_text.strip()
            print(f"[OK] 텍스트 추출 성공: {len(full_text)}자")
            print(f"[PREVIEW] {full_text[:100]}...")
            
        except Exception as e:
            print(f"[ERROR] 자막 파일 테스트 실패: {e}")

print("\n=== 테스트 완료 ===")