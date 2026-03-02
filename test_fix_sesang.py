#!/usr/bin/env python3
"""
세상학개론 시그널 수정 테스트 (처음 5개만)
"""
import os
import json
import time
import requests
import glob
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.local')

# API 설정
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Claude API 설정
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
}

# Supabase 설정
SUPABASE_HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json'
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
        elif 'entries' in subtitle_data:
            # entries 키가 있는 경우
            texts = [entry.get('text', '') for entry in subtitle_data['entries'] if entry.get('text')]
            return ' '.join(texts)
        else:
            print(f"Unknown subtitle format: {subtitle_path}")
            return None
            
    except Exception as e:
        print(f"Error reading subtitle {subtitle_path}: {e}")
        return None

def get_youtube_video_id(video_id):
    """influencer_videos에서 YouTube video_id 조회"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {'id': f'eq.{video_id}', 'select': 'video_id'}
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0].get('video_id')  # video_id가 바로 YouTube ID
    
    return None

def generate_improved_signal(subtitle_text, stock, signal):
    """Claude API로 개선된 key_quote와 reasoning 생성"""
    
    prompt = f'''다음 자막에서 투자 시그널 "{stock}" ({signal})에 대한 정보를 정리해주세요.

1. key_quote: 발언자의 핵심 발언 1~2문장만 (자막 원문에서 직접 인용, 50자 이내)
2. reasoning: 영상 전체 맥락에서 이 시그널이 나온 배경과 근거를 5~10줄로 상세 요약
   - 발언자의 핵심 주장
   - 투자 근거와 논리  
   - 언급된 수치나 데이터
   - 결론과 전망

JSON 형식으로 응답:
{{"key_quote": "...", "reasoning": "..."}}

자막 내용:
{subtitle_text[:6000]}'''

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
        response = requests.post(CLAUDE_API_URL, headers=CLAUDE_HEADERS, json=payload)
        
        if response.status_code != 200:
            print(f"Claude API error: {response.status_code}")
            print(response.text)
            return None
        
        result = response.json()
        content = result['content'][0]['text']
        
        # JSON 파싱
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        parsed = json.loads(content)
        return parsed
        
    except Exception as e:
        print(f"Claude API call failed: {e}")
        return None

def main():
    print("Testing Sesang101 signals improvement (first 5 signals)...")
    
    # 수정이 필요한 시그널 로드
    with open('sesang_signal_analysis.json', 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    need_fix_signals = analysis['need_fix_signals'][:5]  # 처음 5개만
    print(f"Testing with {len(need_fix_signals)} signals")
    
    results = []
    
    for i, signal in enumerate(need_fix_signals):
        try:
            print(f"\n{i+1}/5 Processing: {signal['stock']} ({signal['signal']})")
            
            # YouTube video_id 조회
            youtube_video_id = get_youtube_video_id(signal['video_id'])
            if not youtube_video_id:
                print(f"  YouTube video_id not found")
                continue
            
            print(f"  YouTube ID: {youtube_video_id}")
            
            # 자막 텍스트 로드
            subtitle_text = load_subtitle_text(youtube_video_id)
            if not subtitle_text:
                print(f"  Subtitle not found")
                continue
            
            print(f"  Subtitle loaded: {len(subtitle_text)} chars")
            
            # Claude API로 개선된 시그널 생성
            improved = generate_improved_signal(subtitle_text, signal['stock'], signal['signal'])
            if not improved:
                print(f"  Claude API failed")
                continue
            
            print(f"  Generated key_quote: {len(improved['key_quote'])} chars")
            print(f"  Generated reasoning: {len(improved['reasoning'])} chars")
            
            results.append({
                'signal_id': signal['id'],
                'stock': signal['stock'],
                'signal_type': signal['signal'],
                'original': {
                    'key_quote': '(from DB)',
                    'reasoning': '(from DB)'
                },
                'improved': improved
            })
            
            # 2초 대기
            time.sleep(2)
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # 결과 저장
    with open('test_fix_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nTest completed. Results saved to test_fix_results.json")
    print(f"Successfully processed: {len(results)} signals")

if __name__ == "__main__":
    main()