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
            clean_line = clean_line.replace('?', '').replace('�', '').strip()
            
            if clean_line and len(clean_line) > 3:
                text_lines.append(clean_line)
    
    return ' '.join(text_lines)

def analyze_video(video_id, title):
    # VTT 파일 찾기
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
YouTube 투자 영상 시그널 분석:

## 중요 규칙
1. 1영상 1종목 1시그널 (같은 종목 여러 언급시 가장 강한 시그널 1개만)
2. 시그널 타입: 매수/긍정/중립/경계/매도 (한글만)
3. timestamp: 0:00 금지, 실제 발언 시점

=== 영상 ===
제목: {title}
채널: 월가아재

=== 자막 ===
{subtitle_text[:5000]}

JSON 응답:
{{
  "signals": [
    {{
      "stock": "종목명",
      "ticker": "종목코드",
      "signal_type": "매수|긍정|중립|경계|매도",
      "key_quote": "핵심 발언 (15자 이상)",
      "reasoning": "근거 (20자 이상)",
      "timestamp": "MM:SS",
      "confidence": 7
    }}
  ]
}}

⚠️ 같은 종목은 반드시 1개 시그널만!
"""
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": "claude-sonnet-4-20250514",
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

# 테슬라 관련 영상 2개 분석
if __name__ == "__main__":
    
    tesla_videos = [
        ("l9suWlP7U68", "테슬라 = AI 대장주?"),
        ("_Ex0vR_1Ekg", "테슬라 목표가")
    ]
    
    results = []
    
    for video_id, title in tesla_videos:
        print(f"\\n분석 중: {title}")
        result = analyze_video(video_id, title)
        result['video_id'] = video_id
        result['video_title'] = title
        results.append(result)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 2초 딜레이
        import time
        time.sleep(2)
    
    # 결과 저장
    with open('tesla_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)