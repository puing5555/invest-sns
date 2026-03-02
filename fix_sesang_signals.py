#!/usr/bin/env python3
"""
세상학개론 시그널 key_quote/reasoning 수정 스크립트
- 93개 시그널 중 82개 수정 필요
- Claude API로 자막 기반 key_quote(짧은 인용), reasoning(긴 요약) 재생성
- 5개씩 배치 처리, 요청 간 2초 대기
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
SESANG_SPEAKER_ID = "b9496a5f-06fa-47eb-bc2d-47060b095534"

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
        if 'entries' in subtitle_data:
            texts = [entry.get('text', '') for entry in subtitle_data['entries'] if entry.get('text')]
            return ' '.join(texts)
        else:
            print(f"No entries found in subtitle: {subtitle_path}")
            return None
            
    except Exception as e:
        print(f"Error reading subtitle {subtitle_path}: {e}")
        return None

def get_youtube_video_id(video_id):
    """influencer_videos에서 YouTube video_id 조회"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {'id': f'eq.{video_id}', 'select': 'youtube_video_id'}
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0].get('youtube_video_id')
    
    return None

def generate_improved_signal(subtitle_text, stock, signal):
    """Claude API로 개선된 key_quote와 reasoning 생성"""
    
    prompt = f'''다음 자막에서 투자 시그널 "{stock}" ({signal})에 대한 정보를 정리해주세요.

1. key_quote: 발언자의 핵심 발언 1~2문장 (자막 원문에서 직접 인용)
2. reasoning: 영상 전체 맥락에서 이 시그널이 나온 배경과 근거를 5~10줄로 상세히 요약
   - 발언자의 핵심 주장
   - 투자 근거와 논리
   - 언급된 수치나 데이터
   - 결론과 전망

JSON으로 응답:
{{"key_quote": "...", "reasoning": "..."}}

자막 내용:
{subtitle_text[:8000]}...''' # 8000자 제한

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

def update_signal_in_supabase(signal_id, key_quote, reasoning):
    """Supabase에서 시그널 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {'id': f'eq.{signal_id}'}
    
    data = {
        'key_quote': key_quote,
        'reasoning': reasoning
    }
    
    response = requests.patch(url, headers=SUPABASE_HEADERS, params=params, json=data)
    
    if response.status_code in [200, 204]:
        return True
    else:
        print(f"Supabase update failed: {response.status_code}")
        print(response.text)
        return False

def main():
    print("Starting Sesang101 signals improvement...")
    
    # 수정이 필요한 시그널 로드
    with open('sesang_signal_analysis.json', 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    need_fix_signals = analysis['need_fix_signals']
    print(f"Signals to fix: {len(need_fix_signals)}")
    
    # 진행 상황 추적
    processed = 0
    succeeded = 0
    failed = 0
    batch_size = 5
    
    for i in range(0, len(need_fix_signals), batch_size):
        batch = need_fix_signals[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} signals)...")
        
        for signal in batch:
            try:
                signal_id = signal['id']
                stock = signal['stock']
                signal_type = signal['signal']
                video_id = signal['video_id']
                
                print(f"Processing: {stock} ({signal_type})")
                
                # YouTube video_id 조회
                youtube_video_id = get_youtube_video_id(video_id)
                if not youtube_video_id:
                    print(f"  YouTube video_id not found for {video_id}")
                    failed += 1
                    continue
                
                # 자막 텍스트 로드
                subtitle_text = load_subtitle_text(youtube_video_id)
                if not subtitle_text:
                    print(f"  Subtitle not found for {youtube_video_id}")
                    failed += 1
                    continue
                
                # Claude API로 개선된 시그널 생성
                improved = generate_improved_signal(subtitle_text, stock, signal_type)
                if not improved:
                    print(f"  Claude API failed for {stock}")
                    failed += 1
                    continue
                
                # Supabase 업데이트
                if update_signal_in_supabase(signal_id, improved['key_quote'], improved['reasoning']):
                    print(f"  Updated: {stock}")
                    succeeded += 1
                else:
                    print(f"  Update failed: {stock}")
                    failed += 1
                
                processed += 1
                
                # 요청 간 2초 대기
                time.sleep(2)
                
            except Exception as e:
                print(f"  Error processing {signal.get('stock', 'unknown')}: {e}")
                failed += 1
        
        print(f"Batch completed. Processed: {processed}, Succeeded: {succeeded}, Failed: {failed}")
        
        # 배치 간 추가 대기
        if i + batch_size < len(need_fix_signals):
            print("Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    print(f"\nFinal results:")
    print(f"Total processed: {processed}")
    print(f"Successful updates: {succeeded}")
    print(f"Failed updates: {failed}")

if __name__ == "__main__":
    main()