#!/usr/bin/env python3
"""
개별 영상 시그널 분석 스크립트 - 간단 버전
"""

import os
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API 설정
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

def extract_text_from_vtt(vtt_path):
    """VTT 파일에서 깨끗한 텍스트만 추출"""
    text_lines = []
    
    try:
        with open(vtt_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        # 다른 인코딩으로 시도
        with open(vtt_path, 'r', encoding='cp949', errors='ignore') as f:
            content = f.read()
    
    # 타임스탬프 패턴 이후의 텍스트만 추출
    lines = content.split('\n')
    capturing = False
    
    for line in lines:
        line = line.strip()
        
        # 타임스탬프 라인 건너뛰기
        if '-->' in line:
            capturing = True
            continue
        
        # WEBVTT 헤더 건너뛰기
        if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
            
        # 빈 라인이면 끝
        if not line:
            capturing = False
            continue
            
        # 텍스트 라인 처리
        if capturing and line:
            # HTML 태그와 특수 문자 제거
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'align:start position:\d+%', '', clean_line)
            clean_line = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}', '', clean_line)  # 타임스탬프 제거
            clean_line = clean_line.replace('?', '').replace('�', '').strip()
            
            if clean_line and len(clean_line) > 3:
                text_lines.append(clean_line)
    
    return ' '.join(text_lines)

def analyze_with_claude(video_id, title, subtitle_text):
    """Claude API로 분석"""
    
    # 프롬프트 구성
    prompt = f"""
당신은 투자 인플루언서의 YouTube 영상을 분석하여 주식 시그널을 추출하는 전문 분석가입니다.

## 핵심 규칙
1. 시그널 타입: 매수/긍정/중립/경계/매도 (한글 5단계만 사용)
2. 1영상 1종목 1시그널 원칙
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
      "ticker": "종목코드",
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
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ]
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

# 직접 분석 실행
if __name__ == "__main__":
    # 테스트: 엔비디아 고점 논란 영상
    video_id = "OWkw56VyeUM"
    title = "엔비디아 고점 논란, 가치평가 대가가 판 이유"
    
    # VTT 파일 찾기
    subs_dir = Path(__file__).parent / 'subs'
    vtt_files = list(subs_dir.glob(f"wsaj_{video_id}*.ko.vtt"))
    
    if vtt_files:
        vtt_file = vtt_files[0]
        print(f"Analyzing: {title}")
        print(f"VTT file: {vtt_file.name}")
        
        # 자막 텍스트 추출
        subtitle_text = extract_text_from_vtt(vtt_file)
        print(f"Subtitle length: {len(subtitle_text)} chars")
        
        if len(subtitle_text) > 100:
            # Claude 분석
            print("Calling Claude API...")
            result = analyze_with_claude(video_id, title, subtitle_text)
            
            # 결과 출력
            print("\n=== ANALYSIS RESULT ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("Subtitle too short!")
    else:
        print(f"VTT file not found for {video_id}")