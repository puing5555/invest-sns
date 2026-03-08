#!/usr/bin/env python3
"""
?몄긽?숆컻濡??쒓렇??82媛?key_quote/reasoning ?꾩껜 ?섏젙 ?ㅽ겕由쏀듃
Claude API濡??먮쭑 湲곕컲 ?ъ깮??諛?Supabase ?낅뜲?댄듃
"""
import os
import json
import time
import requests
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
        return None
    
    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            subtitle_data = json.load(f)
        
        # ?먮쭑 ?띿뒪???⑹튂湲?
        if isinstance(subtitle_data, list):
            texts = [entry.get('text', '') for entry in subtitle_data if entry.get('text')]
            return ' '.join(texts)
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
            return data[0].get('video_id')
    
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
{subtitle_text[:4000]}'''

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
            print(f"  Claude API error: {response.status_code}")
            return None
        
        result = response.json()
        content = result['content'][0]['text']
        
        # JSON ?뚯떛
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        parsed = json.loads(content)
        return parsed
        
    except Exception as e:
        print(f"  Claude API error: {e}")
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
    return response.status_code in [200, 204]

def main():
    print("Starting Sesang101 signals improvement...")
    
    # ?섏젙???꾩슂???쒓렇??濡쒕뱶
    with open('sesang_signal_analysis.json', 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    need_fix_signals = analysis['need_fix_signals']
    total = len(need_fix_signals)
    
    print(f"Signals to fix: {total}")
    
    # 吏꾪뻾 ?곹솴 異붿쟻
    processed = 0
    succeeded = 0
    failed = 0
    batch_size = 5
    
    # 寃곌낵 ???
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
                
                # YouTube video_id 議고쉶
                youtube_video_id = get_youtube_video_id(video_id)
                if not youtube_video_id:
                    print(f"    No YouTube ID found")
                    failed += 1
                    continue
                
                # ?먮쭑 ?띿뒪??濡쒕뱶
                subtitle_text = load_subtitle_text(youtube_video_id)
                if not subtitle_text:
                    print(f"    No subtitle found")
                    failed += 1
                    continue
                
                # Claude API濡?媛쒖꽑???쒓렇???앹꽦
                improved = generate_improved_signal(subtitle_text, stock, signal_type)
                if not improved:
                    failed += 1
                    continue
                
                # Supabase ?낅뜲?댄듃
                if update_signal_in_supabase(signal_id, improved['key_quote'], improved['reasoning']):
                    print(f"    ??Updated ({len(improved['key_quote'])}/{len(improved['reasoning'])} chars)")
                    succeeded += 1
                    
                    results.append({
                        'signal_id': signal_id,
                        'stock': stock,
                        'signal_type': signal_type,
                        'key_quote_len': len(improved['key_quote']),
                        'reasoning_len': len(improved['reasoning'])
                    })
                else:
                    print(f"    ??Update failed")
                    failed += 1
                
                processed += 1
                
                # ?붿껌 媛?2珥??湲?
                time.sleep(2)
                
            except Exception as e:
                print(f"    Error: {e}")
                failed += 1
        
        # 諛곗튂 ?꾨즺 ???곹깭 異쒕젰
        print(f"  Batch complete: {succeeded} succeeded, {failed} failed")
        
        # 以묎컙 寃곌낵 ???
        with open('fix_progress.json', 'w', encoding='utf-8') as f:
            json.dump({
                'processed': processed,
                'succeeded': succeeded, 
                'failed': failed,
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        # 諛곗튂 媛?5珥??湲?
        if i + batch_size < total:
            print("  Waiting 5 seconds...")
            time.sleep(5)
    
    print(f"\n?럦 Final results:")
    print(f"  Total processed: {processed}/{total}")
    print(f"  Successful updates: {succeeded}")
    print(f"  Failed updates: {failed}")
    print(f"  Success rate: {succeeded/processed*100:.1f}%")
    
    # 理쒖쥌 寃곌낵 ???
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
