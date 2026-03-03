#!/usr/bin/env python3
"""
월가아재 영상들 일괄 분석 스크립트
"""

import os
import re
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 남은 영상들 (이미 분석된 4개 제외)
remaining_videos = [
    ("liP35sqr9aU", "엔비디아 실적 서프라이즈"),
    ("7x3HE_uXttI", "AI 수혜주 파헤치기"),
    ("tUv4-8BihrM", "AI 관련주, 골드만삭스 리포트"),
    ("l9suWlP7U68", "테슬라 = AI 대장주?"),
    ("_Ex0vR_1Ekg", "테슬라 목표가"),
    ("0pS0CTDgVmU", "Amazon 3Q 2023 어닝콜"),
    ("B17xc8zl3Z4", "Meta 3Q 2023 어닝콜"),
    ("sade4GuojTg", "IPO Arm 투자 체크포인트"),
    ("EbfuT0zGGjU", "IPO 공모주 투자 3가지 포인트"),
    ("57NbdmLvy6I", "노보 노디스크 & 일라이 릴리"),
    ("dPIjOdREB80", "찰스 슈왑 (1부)"),
    ("PzpU0H8iqQs", "찰스 슈왑 (2부)")
]

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

def extract_text_from_vtt(vtt_path):
    """VTT 파일에서 깨끗한 텍스트만 추출"""
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
        
        if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
            
        if not line:
            capturing = False
            continue
            
        if capturing and line:
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'align:start position:\d+%', '', clean_line)
            clean_line = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}', '', clean_line)
            clean_line = clean_line.replace('?', '').replace('�', '').strip()
            
            if clean_line and len(clean_line) > 3:
                text_lines.append(clean_line)
    
    return ' '.join(text_lines)

def analyze_with_claude(video_id, title, subtitle_text):
    """Claude API로 분석"""
    
    prompt = f"""
당신은 투자 인플루언서의 YouTube 영상을 분석하여 주식 시그널을 추출하는 전문 분석가입니다.

## 핵심 규칙
1. 시그널 타입: 매수/긍정/중립/경계/매도 (한글 5단계만 사용)
2. 1영상 1종목 1시그널 원칙 (같은 종목 여러 언급 시 가장 강한 시그널 1개만)
3. timestamp: 0:00 금지, 실제 발언 시점만
4. confidence: 1-10 숫자만 사용

=== 분석 대상 영상 ===
제목: {title}
채널: 월가아재 (wsaj)
URL: https://www.youtube.com/watch?v={video_id}

=== 자막 내용 ===
{subtitle_text[:6000]}

위 영상의 자막을 분석하고 다음 JSON 형태로만 응답해주세요:

{{
  "signals": [
    {{
      "stock": "종목명",
      "ticker": "종목코드 또는 null",
      "signal_type": "매수|긍정|중립|경계|매도",
      "key_quote": "실제 발언 인용 (15자 이상)",
      "reasoning": "구체적 근거 (20자 이상)",
      "timestamp": "MM:SS",
      "confidence": 7
    }}
  ]
}}
"""
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
    }
    
    data = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        content = result['content'][0]['text']
        
        # JSON 파싱
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            json_str = content[start:end].strip()
        elif '{' in content:
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
        else:
            return {"error": "no_json", "raw": content[:300]}
            
        return json.loads(json_str)
        
    except Exception as e:
        return {"error": str(e)}

def main():
    subs_dir = Path(__file__).parent / 'subs'
    results = []
    
    print(f"Starting batch analysis of {len(remaining_videos)} videos...")
    
    for i, (video_id, title) in enumerate(remaining_videos, 1):
        print(f"\n[{i}/{len(remaining_videos)}] Analyzing: {title}")
        
        # VTT 파일 찾기
        vtt_files = list(subs_dir.glob(f"wsaj_{video_id}*.ko.vtt"))
        if not vtt_files:
            print(f"ERROR: VTT file not found for {video_id}")
            continue
            
        vtt_file = vtt_files[0]
        
        # 자막 텍스트 추출
        subtitle_text = extract_text_from_vtt(vtt_file)
        print(f"Subtitle length: {len(subtitle_text)} chars")
        
        if len(subtitle_text) < 100:
            print("WARNING: Subtitle too short, skipping...")
            continue
        
        # Claude 분석
        print("Calling Claude API...")
        result = analyze_with_claude(video_id, title, subtitle_text)
        
        # 결과 저장
        result['video_id'] = video_id
        result['video_title'] = title
        results.append(result)
        
        # 결과 출력
        if 'signals' in result:
            print(f"SUCCESS: Found {len(result['signals'])} signals")
            for signal in result['signals']:
                print(f"  - {signal.get('stock', 'Unknown')}: {signal.get('signal_type', 'Unknown')}")
        else:
            print(f"ERROR: {result}")
        
        # 레이트 리밋 (3초)
        if i < len(remaining_videos):
            print("Waiting 3 seconds...")
            time.sleep(3)
    
    # 결과 저장
    output_file = Path(__file__).parent / 'wsaj_batch_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== BATCH ANALYSIS COMPLETE ===")
    print(f"Results saved to: {output_file}")
    print(f"Analyzed: {len(results)} videos")
    
    # 시그널 통계
    total_signals = sum(len(r.get('signals', [])) for r in results)
    print(f"Total signals: {total_signals}")

if __name__ == "__main__":
    main()