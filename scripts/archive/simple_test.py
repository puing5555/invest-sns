#!/usr/bin/env python3
"""
媛꾨떒???뚯뒪?? ?섎굹???쒓렇?먮쭔?쇰줈 Claude API ?뚯뒪??
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

# API ?ㅼ젙
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Claude API ?ㅼ젙
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
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
        else:
            print(f"Unknown subtitle format: {subtitle_path}")
            return None
            
    except Exception as e:
        print(f"Error reading subtitle {subtitle_path}: {e}")
        return None

def test_claude_api():
    """Claude API ?뚯뒪??""
    print("Testing Claude API...")
    
    # ?뚯뒪?몄슜 ?먮쭑 ?띿뒪??濡쒕뱶
    video_id = "zre4X1a4QlY"
    subtitle_text = load_subtitle_text(video_id)
    
    if not subtitle_text:
        print("Failed to load subtitle")
        return
    
    print(f"Loaded subtitle: {len(subtitle_text)} chars")
    
    # Claude API ?몄텧
    stock = "鍮꾪듃肄붿씤"
    signal = "留ㅼ닔"
    
    prompt = f'''?ㅼ쓬 ?먮쭑?먯꽌 ?ъ옄 ?쒓렇??"{stock}" ({signal})??????뺣낫瑜??뺣━?댁＜?몄슂.

1. key_quote: 諛쒖뼵?먯쓽 ?듭떖 諛쒖뼵 1~2臾몄옣留?(?먮쭑 ?먮Ц?먯꽌 吏곸젒 ?몄슜, 50???대궡)
2. reasoning: ?곸긽 ?꾩껜 留λ씫?먯꽌 ???쒓렇?먯씠 ?섏삩 諛곌꼍怨?洹쇨굅瑜?5~10以꾨줈 ?곸꽭 ?붿빟

JSON ?뺤떇?쇰줈 ?묐떟:
{{"key_quote": "...", "reasoning": "..."}}

?먮쭑 ?댁슜:
{subtitle_text[:3000]}'''

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
        
        # JSON ?뚯떛 ?쒕룄
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
