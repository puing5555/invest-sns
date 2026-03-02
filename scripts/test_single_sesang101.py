#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_single_sesang101.py - 세상학개론 단일 영상 테스트
"""

import os
import json
import sys
import time
from datetime import datetime

# 모듈 import
sys.path.append(os.path.dirname(__file__))
from pipeline_config import PipelineConfig
from signal_analyzer_rest import SignalAnalyzer
from db_inserter_rest import DatabaseInserter

def test_single_video():
    print("=== 세상학개론 단일 영상 테스트 ===")
    
    # 설정
    config = PipelineConfig()
    analyzer = SignalAnalyzer()
    db_inserter = DatabaseInserter()
    
    # 채널 정보
    channel_info = {
        'url': 'https://www.youtube.com/@sesang101',
        'name': '세상학개론',
        'subscriber_count': 150000,
        'video_count': 200,
        'description': '이효석의 세상학개론 - 투자와 경제 분석'
    }
    
    # 호스트 정보
    host_info = {
        'name': '이효석',
        'role': '세상학개론 메인 진행자',
        'bio': '투자 전문가, 유튜버'
    }
    
    # 테스트 파일
    subs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'subs', 'sesang101')
    test_file = os.path.join(subs_dir, 'BeEHwOe-J98.json')  # 팰런티어 관련 영상
    video_id = 'BeEHwOe-J98'
    
    print(f"테스트 파일: {test_file}")
    print(f"비디오 ID: {video_id}")
    
    try:
        # 1. 자막 텍스트 추출
        print("\n[1] 자막 텍스트 추출...")
        with open(test_file, 'r', encoding='utf-8') as f:
            segments = json.load(f)
        
        full_text = ""
        for segment in segments:
            if isinstance(segment, dict) and 'text' in segment:
                full_text += segment['text'] + " "
        
        full_text = full_text.strip()
        print(f"자막 길이: {len(full_text)}자")
        print(f"미리보기: {full_text[:200]}...")
        
        # 2. 영상 정보
        video_info = {
            'title': 'Palantir\'s Future Amidst the New Year\'s Market Crash',
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'duration': 'N/A',
            'upload_date': 'N/A'
        }
        
        print(f"\n[2] 영상 정보:")
        print(f"제목: {video_info['title']}")
        print(f"URL: {video_info['url']}")
        
        # 3. 시그널 분석
        print(f"\n[3] V10.7 시그널 분석...")
        start_time = time.time()
        
        result = analyzer.analyze_video_subtitle(
            channel_url=channel_info['url'],
            video_data=video_info,
            subtitle=full_text
        )
        
        end_time = time.time()
        print(f"분석 소요시간: {end_time - start_time:.2f}초")
        
        if not result:
            print("시그널 없음")
            return
        
        # 결과에서 시그널 추출
        signals = result.get('signals', [])
        if not signals:
            print("시그널 없음")
            print(f"분석 결과: {result}")
            return
        
        print(f"발견된 시그널: {len(signals)}개")
        
        for i, signal in enumerate(signals, 1):
            print(f"\n--- 시그널 {i} ---")
            print(f"종목: {signal.get('stock', 'N/A')}")
            print(f"시그널: {signal.get('signal_type', 'N/A')}")
            print(f"핵심 발언: {signal.get('key_quote', 'N/A')}")
            print(f"근거: {signal.get('reasoning', 'N/A')}")
            print(f"타임스탬프: {signal.get('timestamp', 'N/A')}")
            print(f"신뢰도: {signal.get('confidence', 'N/A')}")
        
        # 4. 채널/호스트 정보 확보 (테스트용)
        print(f"\n[4] 채널/호스트 정보...")
        channel_id = db_inserter.get_or_create_channel(channel_info)
        print(f"채널 ID: {channel_id}")
        
        host_id = db_inserter.get_or_create_speaker(host_info, channel_id)
        print(f"호스트 ID: {host_id}")
        
        print(f"\n=== 테스트 완료 ===")
        print("실제 DB 삽입은 하지 않았습니다.")
        
    except Exception as e:
        print(f"[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_video()