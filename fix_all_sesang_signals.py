#!/usr/bin/env python3
"""
세상학개론 시그널 82개 key_quote/reasoning 전체 수정 스크립트
Claude API로 자막 기반 재생성 및 Supabase 업데이트
"""
import os
import json
import time
import requests
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
        return None
    
    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            subtitle_data = json.load(f)
        
        # 자막 텍스트 합치기
        if isinstance(subtitle_data, list):
            texts = [entry.get('text', '') for entry in subtitle_data if entry.get('text')]
            return ' '.join(texts)
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
            return data[0].get('video_id')
    
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
{subtitle_text[:4000]}'''

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
            print(f"  Claude API error: {response.status_code}")
            return None
        
        result = response.json()
        content = result['content'][0]['text']
        
        # JSON 파싱
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        parsed = json.loads(content)
        return parsed
        
    except Exception as e:
        print(f"  Claude API error: {e}")
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
    return response.status_code in [200, 204]

def main():
    print("Starting Sesang101 signals improvement...")
    
    # 수정이 필요한 시그널 로드
    with open('sesang_signal_analysis.json', 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    need_fix_signals = analysis['need_fix_signals']
    total = len(need_fix_signals)
    
    print(f"Signals to fix: {total}")
    
    # 진행 상황 추적
    processed = 0
    succeeded = 0
    failed = 0
    batch_size = 5
    
    # 결과 저장 
    results = []
    
    for i in range(0, total, batch_size):
        batch = need_fix_signals[i:i+batch_size]
        print(f"\nBatch {i//batch_size + 1}/{(total-1)//batch_size + 1} ({len(batch)} signals)...")
        
        for j, signal in enumerate(batch):
            try:
                signal_id = signal['id']
                stock = signal['stock']
                signal_type = signal['signal']
                video_id = signal['video_id']
                
                print(f"  {i+j+1}/{total}: {stock} ({signal_type})")
                
                # YouTube video_id 조회
                youtube_video_id = get_youtube_video_id(video_id)
                if not youtube_video_id:
                    print(f"    No YouTube ID found")
                    failed += 1
                    continue
                
                # 자막 텍스트 로드
                subtitle_text = load_subtitle_text(youtube_video_id)
                if not subtitle_text:
                    print(f"    No subtitle found")
                    failed += 1
                    continue
                
                # Claude API로 개선된 시그널 생성
                improved = generate_improved_signal(subtitle_text, stock, signal_type)
                if not improved:
                    failed += 1
                    continue
                
                # Supabase 업데이트
                if update_signal_in_supabase(signal_id, improved['key_quote'], improved['reasoning']):
                    print(f"    ✓ Updated ({len(improved['key_quote'])}/{len(improved['reasoning'])} chars)")
                    succeeded += 1
                    
                    results.append({
                        'signal_id': signal_id,
                        'stock': stock,
                        'signal_type': signal_type,
                        'key_quote_len': len(improved['key_quote']),
                        'reasoning_len': len(improved['reasoning'])
                    })
                else:
                    print(f"    ✗ Update failed")
                    failed += 1
                
                processed += 1
                
                # 요청 간 2초 대기
                time.sleep(2)
                
            except Exception as e:
                print(f"    Error: {e}")
                failed += 1
        
        # 배치 완료 후 상태 출력
        print(f"  Batch complete: {succeeded} succeeded, {failed} failed")
        
        # 중간 결과 저장
        with open('fix_progress.json', 'w', encoding='utf-8') as f:
            json.dump({
                'processed': processed,
                'succeeded': succeeded, 
                'failed': failed,
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        # 배치 간 5초 대기
        if i + batch_size < total:
            print("  Waiting 5 seconds...")
            time.sleep(5)
    
    print(f"\n🎉 Final results:")
    print(f"  Total processed: {processed}/{total}")
    print(f"  Successful updates: {succeeded}")
    print(f"  Failed updates: {failed}")
    print(f"  Success rate: {succeeded/processed*100:.1f}%")
    
    # 최종 결과 저장
    final_result = {
        'total_signals': total,
        'processed': processed,
        'succeeded': succeeded,
        'failed': failed,
        'success_rate': succeeded/processed*100 if processed > 0 else 0,
        'results': results,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('sesang_signals_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    print(f"  Results saved to sesang_signals_fixed.json")

if __name__ == "__main__":
    main()