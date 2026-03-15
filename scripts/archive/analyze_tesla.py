#!/usr/bin/env python3

import os
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_vtt(vtt_path):
    text_lines = []
    
    try:
        with open(vtt_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        with open(vtt_path, 'r', encoding='cp949', errors='ignore') as f:
            content = f.read()
    
    lines = content.split('\n')
    capturing = False
    
    for line in lines:
        line = line.strip()
        
        if '-->' in line:
            capturing = True
            continue
        
        if not line or line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            capturing = False
            continue
            
        if capturing and line:
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'align:start position:\d+%', '', clean_line) 
            clean_line = clean_line.replace('?', '').replace('占?, '').strip()
            
            if clean_line and len(clean_line) > 3:
                text_lines.append(clean_line)
    
    return ' '.join(text_lines)

def analyze_video(video_id, title):
    # VTT ?뚯씪 李얘린
    subs_dir = Path(__file__).parent / 'subs'
    vtt_files = list(subs_dir.glob(f"wsaj_{video_id}*.ko.vtt"))
    
    if not vtt_files:
        return {"error": f"VTT file not found for {video_id}"}
    
    subtitle_text = extract_text_from_vtt(vtt_files[0])
    
    if len(subtitle_text) < 100:
        return {"error": "Subtitle too short"}
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': os.getenv('ANTHROPIC_API_KEY', ''),
        'anthropic-version': '2023-06-01'
    }
    
    prompt = f"""
YouTube ?ъ옄 ?곸긽 ?쒓렇??遺꾩꽍:

## 以묒슂 洹쒖튃
1. 1?곸긽 1醫낅ぉ 1?쒓렇??(媛숈? 醫낅ぉ ?щ윭 ?멸툒??媛??媛뺥븳 ?쒓렇??1媛쒕쭔)
2. ?쒓렇????? 留ㅼ닔/湲띿젙/以묐┰/寃쎄퀎/留ㅻ룄 (?쒓?留?
3. timestamp: 0:00 湲덉?, ?ㅼ젣 諛쒖뼵 ?쒖젏

=== ?곸긽 ===
?쒕ぉ: {title}
梨꾨꼸: ?붽??꾩옱

=== ?먮쭑 ===
{subtitle_text[:5000]}

JSON ?묐떟:
{{
  "signals": [
    {{
      "stock": "醫낅ぉ紐?,
      "ticker": "醫낅ぉ肄붾뱶",
      "signal_type": "留ㅼ닔|湲띿젙|以묐┰|寃쎄퀎|留ㅻ룄",
      "key_quote": "?듭떖 諛쒖뼵 (15???댁긽)",
      "reasoning": "洹쇨굅 (20???댁긽)",
      "timestamp": "MM:SS",
      "confidence": 7
    }}
  ]
}}

?좑툘 媛숈? 醫낅ぉ? 諛섎뱶??1媛??쒓렇?먮쭔!
"""
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        
        if response.status_code == 200:
            content = response.json()['content'][0]['text']
            
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                return json.loads(content[start:end].strip())
            elif '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                return json.loads(content[start:end])
                
        return {"error": f"API error: {response.status_code}"}
        
    except Exception as e:
        return {"error": str(e)}

# ?뚯뒳??愿???곸긽 2媛?遺꾩꽍
if __name__ == "__main__":
    
    tesla_videos = [
        ("l9suWlP7U68", "?뚯뒳??= AI ??μ＜?"),
        ("_Ex0vR_1Ekg", "?뚯뒳??紐⑺몴媛")
    ]
    
    results = []
    
    for video_id, title in tesla_videos:
        print(f"\\n遺꾩꽍 以? {title}")
        result = analyze_video(video_id, title)
        result['video_id'] = video_id
        result['video_title'] = title
        results.append(result)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 2珥??쒕젅??
        import time
        time.sleep(2)
    
    # 寃곌낵 ???
    with open('tesla_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
