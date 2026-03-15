#!/usr/bin/env python3
"""
?몄긽?숆컻濡??쒓렇???섏젙 ?뚯뒪??(泥섏쓬 5媛쒕쭔)
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
        if isinstance(subtitle_data, list):
            # 諛곗뿴 ?뺥깭???먮쭑
            texts = [entry.get('text', '') for entry in subtitle_data if entry.get('text')]
            return ' '.join(texts)
        elif 'entries' in subtitle_data:
            # entries ?ㅺ? ?덈뒗 寃쎌슦
            texts = [entry.get('text', '') for entry in subtitle_data['entries'] if entry.get('text')]
            return ' '.join(texts)
        else:
            print(f"Unknown subtitle format: {subtitle_path}")
            return None
            
    except Exception as e:
        print(f"Error reading subtitle {subtitle_path}: {e}")
        return None

def get_youtube_video_id(video_id):
    """influencer_videos?먯꽌 YouTube video_id 議고쉶"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {'id': f'eq.{video_id}', 'select': 'video_id'}
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0].get('video_id')  # video_id媛 諛붾줈 YouTube ID
    
    return None

def generate_improved_signal(subtitle_text, stock, signal):
    """Claude API濡?媛쒖꽑??key_quote? reasoning ?앹꽦"""
    
    prompt = f'''?ㅼ쓬 ?먮쭑?먯꽌 ?ъ옄 ?쒓렇??"{stock}" ({signal})??????뺣낫瑜??뺣━?댁＜?몄슂.

1. key_quote: 諛쒖뼵?먯쓽 ?듭떖 諛쒖뼵 1~2臾몄옣留?(?먮쭑 ?먮Ц?먯꽌 吏곸젒 ?몄슜, 50???대궡)
2. reasoning: ?곸긽 ?꾩껜 留λ씫?먯꽌 ???쒓렇?먯씠 ?섏삩 諛곌꼍怨?洹쇨굅瑜?5~10以꾨줈 ?곸꽭 ?붿빟
   - 諛쒖뼵?먯쓽 ?듭떖 二쇱옣
   - ?ъ옄 洹쇨굅? ?쇰━  
   - ?멸툒???섏튂???곗씠??
   - 寃곕줎怨??꾨쭩

JSON ?뺤떇?쇰줈 ?묐떟:
{{"key_quote": "...", "reasoning": "..."}}

?먮쭑 ?댁슜:
{subtitle_text[:6000]}'''

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

def main():
    print("Testing Sesang101 signals improvement (first 5 signals)...")
    
    # ?섏젙???꾩슂???쒓렇??濡쒕뱶
    with open('sesang_signal_analysis.json', 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    need_fix_signals = analysis['need_fix_signals'][:5]  # 泥섏쓬 5媛쒕쭔
    print(f"Testing with {len(need_fix_signals)} signals")
    
    results = []
    
    for i, signal in enumerate(need_fix_signals):
        try:
            print(f"\n{i+1}/5 Processing: {signal['stock']} ({signal['signal']})")
            
            # YouTube video_id 議고쉶
            youtube_video_id = get_youtube_video_id(signal['video_id'])
            if not youtube_video_id:
                print(f"  YouTube video_id not found")
                continue
            
            print(f"  YouTube ID: {youtube_video_id}")
            
            # ?먮쭑 ?띿뒪??濡쒕뱶
            subtitle_text = load_subtitle_text(youtube_video_id)
            if not subtitle_text:
                print(f"  Subtitle not found")
                continue
            
            print(f"  Subtitle loaded: {len(subtitle_text)} chars")
            
            # Claude API濡?媛쒖꽑???쒓렇???앹꽦
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
            
            # 2珥??湲?
            time.sleep(2)
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # 寃곌낵 ???
    with open('test_fix_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nTest completed. Results saved to test_fix_results.json")
    print(f"Successfully processed: {len(results)} signals")

if __name__ == "__main__":
    main()
