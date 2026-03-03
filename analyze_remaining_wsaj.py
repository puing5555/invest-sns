#!/usr/bin/env python3
"""
월가아재 나머지 12개 영상 시그널 분석 스크립트
"""

import os
import re
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env.local')

# API 설정
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"

def load_prompt_template():
    """pipeline_v10.md 프롬프트 로드"""
    prompt_path = Path(__file__).parent / 'prompts' / 'pipeline_v10.md'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_vtt_file(vtt_path):
    """VTT 파일에서 텍스트만 추출"""
    text_lines = []
    
    with open(vtt_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # VTT 형식에서 타임스탬프와 텍스트 추출
    lines = content.split('\n')
    in_subtitle = False
    
    for line in lines:
        line = line.strip()
        
        # 타임스탬프 라인 패턴
        if '-->' in line:
            in_subtitle = True
            continue
        
        # 빈 라인이면 자막 블록 끝
        if not line:
            in_subtitle = False
            continue
            
        # 자막 텍스트 라인
        if in_subtitle and line and not line.startswith('WEBVTT') and not line.startswith('Kind:') and not line.startswith('Language:'):
            # HTML 태그 제거 및 정리
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'align:start position:\d+%', '', clean_line)
            clean_line = clean_line.replace('?', '').strip()
            if clean_line and len(clean_line) > 2:
                text_lines.append(clean_line)
    
    return ' '.join(text_lines)

def analyze_video_signal(video_id, video_title, subtitle_text):
    """Claude API를 사용한 시그널 분석"""
    
    prompt_template = load_prompt_template()
    
    # 프롬프트 구성
    full_prompt = f"""
{prompt_template}

=== 분석 대상 영상 ===
제목: {video_title}
채널: 월가아재 (wsaj / Wall Street Ajae)
URL: https://www.youtube.com/watch?v={video_id}

=== 자막 내용 ===
{subtitle_text[:8000]}

=== 분석 지시사항 ===
위 영상의 자막을 분석하고 정확히 아래 JSON 형태로 시그널을 추출해주세요.
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
        
        # JSON 응답 파싱
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
            print(f"JSON parsing error: {e}")
            print(f"Response content: {content}")
            return {"error": "parse_failed", "raw": content[:500]}
            
    except Exception as e:
        print(f"API call error: {e}")
        return {"error": "api_failed", "message": str(e)}

def main():
    """메인 실행"""
    
    # 나머지 12개 영상 (이미 분석된 3개 제외)
    remaining_videos = [
        ("OWkw56VyeUM", "엔비디아 고점 논란, 가치평가 대가가 판 이유"),
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
    
    subs_dir = Path(__file__).parent / 'subs'
    results = []
    
    for i, (video_id, title) in enumerate(remaining_videos, 1):
        print(f"\n[ANALYZE {i}/12] Processing: {title} ({video_id})")
        
        # VTT 파일 찾기
        vtt_files = list(subs_dir.glob(f"wsaj_{video_id}*.ko.vtt"))
        if not vtt_files:
            print(f"[ERROR] VTT file not found for {video_id}")
            continue
            
        vtt_file = vtt_files[0]
        print(f"[LOAD] Reading subtitle file for {video_id}")
        
        # 자막 텍스트 추출
        subtitle_text = parse_vtt_file(vtt_file)
        print(f"[INFO] Subtitle length: {len(subtitle_text)} characters")
        
        if len(subtitle_text) < 100:
            print(f"[SKIP] Subtitle too short")
            continue
        
        # 시그널 분석
        print(f"[API] Analyzing signals...")
        result = analyze_video_signal(video_id, title, subtitle_text)
        
        # 결과 저장
        result['video_id'] = video_id
        result['video_title'] = title
        results.append(result)
        
        print(f"[RESULT] Found {len(result.get('signals', []))} signals")
        
        # 레이트 리밋 준수 (2-3초 딜레이)
        delay = 3
        print(f"[WAIT] Sleeping {delay} seconds...")
        time.sleep(delay)
    
    # 최종 결과 저장
    output_file = Path(__file__).parent / 'wsaj_remaining_signals.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[COMPLETE] Results saved to: {output_file}")
    print(f"[SUMMARY] Analyzed {len(results)} videos")
    
    # 시그널 통계
    total_signals = sum(len(r.get('signals', [])) for r in results)
    print(f"[STATS] Total signals extracted: {total_signals}")

if __name__ == "__main__":
    main()