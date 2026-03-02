#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
debug_sesang101.py - 세상학개론 분석 디버그
"""

import os
import json
import sys
import time
import requests
from datetime import datetime

# 모듈 import
sys.path.append(os.path.dirname(__file__))
from pipeline_config import PipelineConfig

def debug_analysis():
    print("=== 세상학개론 분석 디버그 ===")
    
    # 설정
    config = PipelineConfig()
    
    # 테스트 자막 (짧게)
    test_subtitle = """
    세 달 뒤 5월 15일 8월 연준위장의 기가 종료됩니다. 그동안 트럼프가 금리 인하를 엄청 압박해 왔기 때문에 과연 이제 차기 연준위장이 그동안 트럼프가 원하던 인하 기조를 이어갈 것인가 아니면 고금리를 유지할 것인가에 대해서 시장이 궁금해하고 있습니다. 
    
    특히 트럼프가 지목한 차기 연준위장이 됐고 지금 현재로서 월스트리트가 가장 우려하는 것은 인플레이션입니다. 
    
    그래서 이번에 트럼프가 지명한 차기 연준위장이 과연 앞으로 어떤 정책을 가져올지에 대해서 시장이 매우 우려를 표하고 있는 상황입니다.
    """
    
    # 영상 정보
    video_info = {
        'title': 'Why are markets panicking over Trump\'s choice? Should we panic too?',
        'url': 'https://www.youtube.com/watch?v=Ke7gQMbIFLI',
        'duration': 'N/A',
        'upload_date': 'N/A'
    }
    
    # 프롬프트 생성
    prompt_template = config.load_prompt()
    channel_url = 'https://www.youtube.com/@sesang101'
    
    # 기본 프롬프트에서 채널 URL 교체
    prompt = prompt_template.replace('{CHANNEL_URL}', channel_url)
    
    # 영상 정보 추가
    video_info_text = f"""
=== 분석 대상 영상 ===
제목: {video_info['title']}
URL: {video_info['url']}
길이: {video_info.get('duration', 'N/A')}
업로드: {video_info.get('upload_date', 'N/A')}

=== 자막 내용 ===
{test_subtitle}

=== 분석 지시사항 ===
위 영상의 자막을 V10.7 프롬프트 규칙에 따라 분석하고, JSON 형태로 시그널을 추출해주세요.
"""
    
    final_prompt = prompt + "\n\n" + video_info_text
    
    print(f"프롬프트 길이: {len(final_prompt)}자")
    print(f"프롬프트 미리보기:")
    print("="*50)
    try:
        print(final_prompt[:500] + "...")
    except UnicodeEncodeError:
        print("(프롬프트에 특수문자 포함으로 출력 생략)")
    print("="*50)
    
    # API 호출
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': config.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
    }
    
    payload = {
        'model': 'claude-3-haiku-20240307',
        'max_tokens': 4000,
        'messages': [
            {
                'role': 'user',
                'content': final_prompt
            }
        ]
    }
    
    print("\n[API] Claude 호출 중...")
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code != 200:
            print(f"에러 응답: {response.text}")
            return
        
        result = response.json()
        
        if 'content' in result and result['content']:
            response_text = result['content'][0]['text']
            
            print(f"\n응답 길이: {len(response_text)}자")
            print("응답 내용:")
            print("="*50)
            print(response_text)
            print("="*50)
            
            # JSON 찾기 시도
            print("\nJSON 파싱 시도...")
            
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_str = response_text[start:end].strip()
                print(f"JSON 블록 발견 (```json): {len(json_str)}자")
                print(json_str)
            elif '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                print(f"JSON 블록 발견 (직접): {len(json_str)}자")
                print(json_str)
            else:
                print("JSON 블록을 찾을 수 없습니다")
                
        else:
            print("응답에 content가 없습니다")
            print(result)
            
    except Exception as e:
        print(f"API 호출 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_analysis()