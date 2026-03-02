#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_single_sesang101_fixed.py - 단일 영상 테스트 (수정된 버전)
"""

import os
import json
import sys

# 모듈 import
from pipeline_config import PipelineConfig
from signal_analyzer_rest import SignalAnalyzer

def test_single_video():
    """단일 영상 테스트"""
    
    # 작업 디렉토리 변경
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    print(f"작업 디렉토리: {os.getcwd()}")
    
    # 테스트할 영상 ID
    test_video_id = "aW0cZ-rmzz8"
    subtitle_file = f"../subs/sesang101/{test_video_id}.json"
    
    print(f"테스트 영상: {test_video_id}")
    
    # 자막 파일 로드
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            subtitle_data = json.load(f)
        print(f"자막 파일 로드 성공")
        print(f"자막 데이터 타입: {type(subtitle_data)}")
        
        if isinstance(subtitle_data, list):
            print(f"자막 항목 수: {len(subtitle_data)}")
            print(f"첫 번째 항목: {subtitle_data[0] if subtitle_data else 'None'}")
        
    except Exception as e:
        print(f"자막 파일 로드 실패: {e}")
        return
    
    # 자막 텍스트 추출
    if isinstance(subtitle_data, list):
        subtitle_text = " ".join([item.get('text', '') for item in subtitle_data if 'text' in item])
    else:
        subtitle_text = ""
    
    print(f"자막 텍스트 길이: {len(subtitle_text)} 문자")
    print(f"자막 첫 200자: {subtitle_text[:200]}...")
    
    # 영상 데이터 구성
    video_data = {
        'video_id': test_video_id,
        'title': f'세상학개론 영상 {test_video_id}',
        'url': f"https://youtube.com/watch?v={test_video_id}",
        'published_at': '',
        'description': '',
        'duration': 0,
        'view_count': 0,
        'like_count': 0,
        'channel_info': {
            'url': 'https://www.youtube.com/@sesang101',
            'name': '세상학개론',
            'subscriber_count': 150000,
            'video_count': 200,
            'description': '이효석의 세상학개론 - 투자와 경제 분석'
        },
        'host_info': {
            'name': '이효석',
            'role': '세상학개론 메인 진행자',
            'bio': '투자 전문가, 유튜버'
        }
    }
    
    print("영상 데이터 구성 완료")
    
    # 시그널 분석 테스트
    try:
        print("시그널 분석 시작...")
        analyzer = SignalAnalyzer()
        
        # analyze_video_subtitle 메소드 사용
        analysis_result = analyzer.analyze_video_subtitle(
            video_data['channel_info']['url'],  # channel_url
            video_data,  # video_data
            subtitle_text  # subtitle
        )
        
        print(f"분석 완료!")
        print(f"결과 타입: {type(analysis_result)}")
        
        if analysis_result:
            print(f"시그널 수: {len(analysis_result.get('signals', []))}")
            
            # 결과를 파일로 저장
            with open('test_single_result.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            print("결과 저장: test_single_result.json")
        else:
            print("분석 결과 없음")
            
    except Exception as e:
        print(f"분석 에러: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_single_video()