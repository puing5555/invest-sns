#!/usr/bin/env python3
"""
?몄긽?숆컻濡??쒓렇??key_quote/reasoning ?섏젙 ?ㅽ겕由쏀듃
- 93媛??쒓렇??以?82媛??섏젙 ?꾩슂
- Claude API濡??먮쭑 湲곕컲 key_quote(吏㏃? ?몄슜), reasoning(湲??붿빟) ?ъ깮??
- 5媛쒖뵫 諛곗튂 泥섎━, ?붿껌 媛?2珥??湲?
"""
import os
import json
import time
import requests
import glob
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.local')

# API ?ㅼ젙
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SESANG_SPEAKER_ID = "b9496a5f-06fa-47eb-bc2d-47060b095534"

# Claude API ?ㅼ젙
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
}

# Supabase ?ㅼ젙
SUPABASE_HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json'
}

def load_subtitle_text(video_id):
    """?먮쭑 ?뚯씪?먯꽌 ?띿뒪??異붿텧"""
    subtitle_path = f"../subs/sesang101/{video_id}.json"
    
    if not os.path.exists(subtitle_path):
        print(f"Subtitle file not found: {subtitle_path}")
        return None
    
    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            subtitle_data = json.load(f)
        
        # ?먮쭑 ?띿뒪???⑹튂湲?
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
    """influencer_videos?먯꽌 YouTube video_id 議고쉶"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {'id': f'eq.{video_id}', 'select': 'youtube_video_id'}
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0].get('youtube_video_id')
    
    return None

def generate_improved_signal(subtitle_text, stock, signal):
    """Claude API濡?媛쒖꽑??key_quote? reasoning ?앹꽦"""
    
    prompt = f'''?ㅼ쓬 ?먮쭑?먯꽌 ?ъ옄 ?쒓렇??"{stock}" ({signal})??????뺣낫瑜??뺣━?댁＜?몄슂.

1. key_quote: 諛쒖뼵?먯쓽 ?듭떖 諛쒖뼵 1~2臾몄옣 (?먮쭑 ?먮Ц?먯꽌 吏곸젒 ?몄슜)
2. reasoning: ?곸긽 ?꾩껜 留λ씫?먯꽌 ???쒓렇?먯씠 ?섏삩 諛곌꼍怨?洹쇨굅瑜?5~10以꾨줈 ?곸꽭???붿빟
   - 諛쒖뼵?먯쓽 ?듭떖 二쇱옣
   - ?ъ옄 洹쇨굅? ?쇰━
   - ?멸툒???섏튂???곗씠??
   - 寃곕줎怨??꾨쭩

JSON?쇰줈 ?묐떟:
{{"key_quote": "...", "reasoning": "..."}}

?먮쭑 ?댁슜:
{subtitle_text[:8000]}...''' # 8000???쒗븳

    payload = {
        "model": "claude-sonnet-4-6",
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
        
        # JSON ?뚯떛
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        parsed = json.loads(content)
        return parsed
        
    except Exception as e:
        print(f"Claude API call failed: {e}")
        return None

def update_signal_in_supabase(signal_id, key_quote, reasoning):
    """Supabase?먯꽌 ?쒓렇???낅뜲?댄듃"""
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
    
    # ?섏젙???꾩슂???쒓렇??濡쒕뱶
    with open('sesang_signal_analysis.json', 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    need_fix_signals = analysis['need_fix_signals']
    print(f"Signals to fix: {len(need_fix_signals)}")
    
    # 吏꾪뻾 ?곹솴 異붿쟻
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
                
                # YouTube video_id 議고쉶
                youtube_video_id = get_youtube_video_id(video_id)
                if not youtube_video_id:
                    print(f"  YouTube video_id not found for {video_id}")
                    failed += 1
                    continue
                
                # ?먮쭑 ?띿뒪??濡쒕뱶
                subtitle_text = load_subtitle_text(youtube_video_id)
                if not subtitle_text:
                    print(f"  Subtitle not found for {youtube_video_id}")
                    failed += 1
                    continue
                
                # Claude API濡?媛쒖꽑???쒓렇???앹꽦
                improved = generate_improved_signal(subtitle_text, stock, signal_type)
                if not improved:
                    print(f"  Claude API failed for {stock}")
                    failed += 1
                    continue
                
                # Supabase ?낅뜲?댄듃
                if update_signal_in_supabase(signal_id, improved['key_quote'], improved['reasoning']):
                    print(f"  Updated: {stock}")
                    succeeded += 1
                else:
                    print(f"  Update failed: {stock}")
                    failed += 1
                
                processed += 1
                
                # ?붿껌 媛?2珥??湲?
                time.sleep(2)
                
            except Exception as e:
                print(f"  Error processing {signal.get('stock', 'unknown')}: {e}")
                failed += 1
        
        print(f"Batch completed. Processed: {processed}, Succeeded: {succeeded}, Failed: {failed}")
        
        # 諛곗튂 媛?異붽? ?湲?
        if i + batch_size < len(need_fix_signals):
            print("Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    print(f"\nFinal results:")
    print(f"Total processed: {processed}")
    print(f"Successful updates: {succeeded}")
    print(f"Failed updates: {failed}")

if __name__ == "__main__":
    main()
