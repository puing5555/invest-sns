#!/usr/bin/env python3
"""
?붽??꾩옱(wsaj) VTT ?먮쭑 湲곕컲 ?쒓렇??遺꾩꽍 ?ㅽ겕由쏀듃
pipeline_v10 ?꾨＼?꾪듃 ?ъ슜
"""

import os
import re
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env.local')

# API ?ㅼ젙
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

def load_prompt_template():
    """pipeline_v10.md ?꾨＼?꾪듃 濡쒕뱶"""
    prompt_path = Path(__file__).parent / 'prompts' / 'pipeline_v10.md'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_vtt_file(vtt_path):
    """VTT ?뚯씪?먯꽌 ?띿뒪?몃쭔 異붿텧"""
    text_lines = []
    
    with open(vtt_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # VTT ?뺤떇?먯꽌 ??꾩뒪?ы봽? ?띿뒪??異붿텧
    # 00:00:00.480 --> 00:00:02.330 ?뺥깭???쇱씤??李얘퀬 ?ㅼ쓬 ?쇱씤?ㅼ씠 ?띿뒪??
    lines = content.split('\n')
    in_subtitle = False
    
    for line in lines:
        line = line.strip()
        
        # ??꾩뒪?ы봽 ?쇱씤 ?⑦꽩
        if '-->' in line:
            in_subtitle = True
            continue
        
        # 鍮??쇱씤?대㈃ ?먮쭑 釉붾줉 ??
        if not line:
            in_subtitle = False
            continue
            
        # ?먮쭑 ?띿뒪???쇱씤
        if in_subtitle and line and not line.startswith('WEBVTT') and not line.startswith('Kind:') and not line.startswith('Language:'):
            # HTML ?쒓렇 ?쒓굅 諛??뺣━
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'align:start position:\d+%', '', clean_line)
            clean_line = clean_line.replace('?', '').strip()
            if clean_line and len(clean_line) > 2:
                text_lines.append(clean_line)
    
    return ' '.join(text_lines)

def analyze_video_signal(video_id, video_title, subtitle_text):
    """Claude API瑜??ъ슜???쒓렇??遺꾩꽍"""
    
    prompt_template = load_prompt_template()
    
    # ?꾨＼?꾪듃 援ъ꽦
    full_prompt = f"""
{prompt_template}

=== 遺꾩꽍 ????곸긽 ===
?쒕ぉ: {video_title}
梨꾨꼸: ?붽??꾩옱 (wsaj / Wall Street Ajae)
URL: https://www.youtube.com/watch?v={video_id}

=== ?먮쭑 ?댁슜 ===
{subtitle_text[:8000]}

=== 遺꾩꽍 吏?쒖궗??===
???곸긽???먮쭑??遺꾩꽍?섍퀬 ?뺥솗???꾨옒 JSON ?뺥깭濡??쒓렇?먯쓣 異붿텧?댁＜?몄슂.
"""
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
    }
    
    data = {
        "model": MODEL,
        "max_tokens": 2000,
        "messages": [
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result['content'][0]['text']
        
        # JSON ?묐떟 ?뚯떛
        try:
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                return json.loads(content[start:end].strip())
            elif '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                return json.loads(content[start:end])
        except json.JSONDecodeError as e:
            print(f"JSON ?뚯떛 ?먮윭: {e}")
            print(f"?묐떟 ?댁슜: {content}")
            return {"error": "parse_failed", "raw": content[:500]}
            
    except Exception as e:
        print(f"API ?몄텧 ?먮윭: {e}")
        return {"error": "api_failed", "message": str(e)}

def main():
    """硫붿씤 ?ㅽ뻾"""
    
    # ?대? 異붿텧???곸긽??
    videos = [
        ("oDfnMrrRfl8", "Nvidia 諛몃쪟?먯씠??),
        ("AQ2z2ZCBFa4", "Nvidia AI/硫뷀?踰꾩뒪/?먯쑉二쇳뻾"),
        ("5fhbkQ2Qidc", "媛移섑룊媛 ?媛媛 ?붾퉬?붿븘 二쇱떇 ?????댁쑀")
    ]
    
    subs_dir = Path(__file__).parent / 'subs'
    results = []
    
    for video_id, title in videos:
        print(f"\n[ANALYZE] Processing: {title} ({video_id})")
        
        # VTT ?뚯씪 李얘린
        vtt_files = list(subs_dir.glob(f"wsaj_{video_id}*.ko.vtt"))
        if not vtt_files:
            print(f"[ERROR] VTT file not found for {video_id}")
            continue
            
        vtt_file = vtt_files[0]
        print(f"[LOAD] Reading subtitle file for {video_id}")
        
        # ?먮쭑 ?띿뒪??異붿텧
        subtitle_text = parse_vtt_file(vtt_file)
        print(f"[INFO] Subtitle length: {len(subtitle_text)} characters")
        
        if len(subtitle_text) < 100:
            print(f"[SKIP] Subtitle too short")
            continue
        
        # ?쒓렇??遺꾩꽍
        print(f"[API] Analyzing signals...")
        result = analyze_video_signal(video_id, title, subtitle_text)
        
        # 寃곌낵 ???
        result['video_id'] = video_id
        result['video_title'] = title
        results.append(result)
        
        print(f"[RESULT] {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # ?덉씠??由щ컠 以??
        print(f"[WAIT] Sleeping 2 seconds...")
        time.sleep(2)
    
    # 理쒖쥌 寃곌낵 ???
    output_file = Path(__file__).parent / 'wsaj_signals_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[COMPLETE] Results saved to: {output_file}")
    print(f"[SUMMARY] Analyzed {len(results)} videos")

if __name__ == "__main__":
    main()
