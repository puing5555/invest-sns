#!/usr/bin/env python3
"""
간단한 테스트: 하나의 시그널만으로 Claude API 테스트
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

# API 설정
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Claude API 설정
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
}

def load_subtitle_text(video_id):
    """자막 파일에서 텍스트 추출"""
    subtitle_path = f"../subs/sesang101/{video_id}.json"
    
    if not os.path.exists(subtitle_path):
        print(f"Subtitle file not found: {subtitle_path}")
        return None
    
    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            subtitle_data = json.load(f)
        
        # 자막 텍스트 합치기
        if isinstance(subtitle_data, list):
            # 배열 형태의 자막
            texts = [entry.get('text', '') for entry in subtitle_data if entry.get('text')]
            return ' '.join(texts)
        else:
            print(f"Unknown subtitle format: {subtitle_path}")
            return None
            
    except Exception as e:
        print(f"Error reading subtitle {subtitle_path}: {e}")
        return None

def test_claude_api():
    """Claude API 테스트"""
    print("Testing Claude API...")
    
    # 테스트용 자막 텍스트 로드
    video_id = "zre4X1a4QlY"
    subtitle_text = load_subtitle_text(video_id)
    
    if not subtitle_text:
        print("Failed to load subtitle")
        return
    
    print(f"Loaded subtitle: {len(subtitle_text)} chars")
    
    # Claude API 호출
    stock = "비트코인"
    signal = "매수"
    
    prompt = f'''다음 자막에서 투자 시그널 "{stock}" ({signal})에 대한 정보를 정리해주세요.

1. key_quote: 발언자의 핵심 발언 1~2문장만 (자막 원문에서 직접 인용, 50자 이내)
2. reasoning: 영상 전체 맥락에서 이 시그널이 나온 배경과 근거를 5~10줄로 상세 요약

JSON 형식으로 응답:
{{"key_quote": "...", "reasoning": "..."}}

자막 내용:
{subtitle_text[:3000]}'''

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        print("Calling Claude API...")
        response = requests.post(CLAUDE_API_URL, headers=CLAUDE_HEADERS, json=payload)
        
        if response.status_code != 200:
            print(f"Claude API error: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        content = result['content'][0]['text']
        
        print("Claude API Response:")
        print(content)
        
        # JSON 파싱 시도
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        try:
            parsed = json.loads(content)
            print("\nParsed JSON:")
            print(f"key_quote ({len(parsed['key_quote'])} chars): {parsed['key_quote']}")
            print(f"reasoning ({len(parsed['reasoning'])} chars): {parsed['reasoning']}")
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_claude_api()