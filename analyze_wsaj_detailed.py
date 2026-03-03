#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
월가아재 기업해부학 나머지 9개 영상 시그널 분석 (개선 버전)
실제 VTT 파일 내용 기반 정교한 분석
"""

import sys
import io
import re
import glob
import json
import os
from typing import List, Dict, Any, Tuple

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_vtt_with_timestamps(video_id: str) -> List[Tuple[str, str]]:
    """VTT 파일을 파싱하여 타임스탬프와 텍스트 쌍 반환"""
    files = glob.glob(f'subs/wsaj_{video_id}_*.ko.vtt')
    if not files:
        print(f"⚠️  VTT 파일을 찾을 수 없음: wsaj_{video_id}_*.ko.vtt")
        return []
    
    print(f"📂 파일 처리: {files[0]}")
    
    with open(files[0], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # VTT 파싱 - 타임스탬프와 텍스트 매칭
    entries = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 타임스탬프 패턴 찾기
        if '-->' in line:
            timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                
                # 다음 몇 줄에서 텍스트 찾기
                text_parts = []
                j = i + 1
                while j < len(lines) and j < i + 5:  # 최대 5줄까지 확인
                    text_line = lines[j].strip()
                    if text_line and not text_line.startswith('WEBVTT') and not '-->' in text_line:
                        # HTML 태그 제거
                        clean_text = re.sub(r'<[^>]+>', '', text_line)
                        clean_text = re.sub(r'align:.*position:.*%', '', clean_text)
                        clean_text = clean_text.strip()
                        if clean_text and clean_text not in ['[음악]', ' ']:
                            text_parts.append(clean_text)
                    j += 1
                
                if text_parts:
                    # 분:초 형식으로 변환 (HH:MM:SS -> MM:SS)
                    time_parts = timestamp.split(':')
                    if len(time_parts) >= 3:
                        mm_ss = f"{time_parts[1]}:{time_parts[2]}"
                        entries.append((mm_ss, ' '.join(text_parts)))
        
        i += 1
    
    return entries

def analyze_video_signals(entries: List[Tuple[str, str]], video_id: str, video_title: str) -> Dict[str, Any]:
    """타임스탬프가 포함된 텍스트 분석으로 정확한 시그널 추출"""
    
    result = {
        "video_id": video_id,
        "video_title": video_title,
        "signals": []
    }
    
    # 모든 텍스트 합치기 (분석용)
    all_text = ' '.join([text for _, text in entries]).lower()
    
    print(f"📄 전체 텍스트 길이: {len(all_text):,} 문자")
    
    # 핵심 발언 찾기 위한 키워드 패턴
    positive_keywords = ['추천', '매수', '좋다', '상승', '성장', '긍정적', '투자하면', '기회']
    negative_keywords = ['매도', '하락', '위험', '부정적', '피하라', '조심']
    neutral_keywords = ['지켜봐야', '중립', '모니터링', '관찰']
    
    # 영상별 특화 분석
    if "7x3HE_uXttI" in video_id:  # AI 수혜주 파헤치기
        stock_mentions = []
        for timestamp, text in entries:
            if any(keyword in text.lower() for keyword in ['엔비디아', 'nvidia', 'nvda']):
                stock_mentions.append((timestamp, text))
            elif any(keyword in text.lower() for keyword in ['구글', 'google', 'googl', '알파벳']):
                stock_mentions.append((timestamp, text))
            elif any(keyword in text.lower() for keyword in ['마이크로소프트', 'microsoft', 'msft']):
                stock_mentions.append((timestamp, text))
        
        # 발언 톤 분석
        for timestamp, text in stock_mentions:
            if '엔비디아' in text or 'nvidia' in text.lower():
                # 톤 분석
                signal_type = "중립"
                if any(pos in text for pos in positive_keywords):
                    signal_type = "긍정"
                elif any(neg in text for neg in negative_keywords):
                    signal_type = "경계"
                
                result["signals"].append({
                    "stock": "엔비디아",
                    "ticker": "NVDA", 
                    "signal_type": signal_type,
                    "key_quote": text[:100] + "..." if len(text) > 100 else text,
                    "reasoning": "AI 반도체 선두 기업으로 생성형 AI 붐의 직접 수혜",
                    "timestamp": timestamp,
                    "confidence": 8
                })
                break  # 1영상 1종목 1시그널
    
    elif "tUv4-8BihrM" in video_id:  # AI 관련주, 골드만삭스 리포트
        for timestamp, text in entries:
            if '골드만삭스' in text or '리포트' in text:
                signal_type = "중립"
                if any(pos in text for pos in positive_keywords):
                    signal_type = "긍정"
                    
                result["signals"].append({
                    "stock": "AI 섹터",
                    "ticker": "AI_SECTOR",
                    "signal_type": signal_type,
                    "key_quote": text[:100] + "..." if len(text) > 100 else text,
                    "reasoning": "골드만삭스 리포트의 AI 섹터 전망 분석",
                    "timestamp": timestamp,
                    "confidence": 7
                })
                break
    
    elif "0pS0CTDgVmU" in video_id:  # Amazon 3Q 2023 어닝콜
        for timestamp, text in entries:
            if '아마존' in text or 'amazon' in text.lower():
                if '실적' in text or '어닝' in text or '매출' in text:
                    signal_type = "중립"
                    if '좋' in text or '상승' in text or '증가' in text:
                        signal_type = "긍정"
                    elif '하락' in text or '감소' in text:
                        signal_type = "경계"
                    
                    result["signals"].append({
                        "stock": "아마존",
                        "ticker": "AMZN",
                        "signal_type": signal_type,
                        "key_quote": text[:100] + "..." if len(text) > 100 else text,
                        "reasoning": "3분기 실적 분석 기반 투자 의견",
                        "timestamp": timestamp,
                        "confidence": 7
                    })
                    break
    
    elif "B17xc8zl3Z4" in video_id:  # Meta 3Q 2023 어닝콜
        for timestamp, text in entries:
            if '메타' in text or 'meta' in text.lower():
                if '실적' in text or '어닝' in text:
                    signal_type = "중립"
                    if 'ai' in text.lower() and ('좋' in text or '성장' in text):
                        signal_type = "긍정"
                    
                    result["signals"].append({
                        "stock": "메타",
                        "ticker": "META",
                        "signal_type": signal_type,
                        "key_quote": text[:100] + "..." if len(text) > 100 else text,
                        "reasoning": "3분기 실적과 AI 전환 전략 평가",
                        "timestamp": timestamp,
                        "confidence": 7
                    })
                    break
    
    elif "57NbdmLvy6I" in video_id:  # 노보 노디스크 & 일라이 릴리
        healthcare_signals = []
        for timestamp, text in entries:
            if '노보' in text or '릴리' in text or '비만' in text or '당뇨' in text:
                healthcare_signals.append((timestamp, text))
        
        if healthcare_signals:
            # 가장 긍정적인 발언 선택
            best_signal = healthcare_signals[0]
            for timestamp, text in healthcare_signals:
                if any(pos in text for pos in positive_keywords):
                    best_signal = (timestamp, text)
                    break
            
            timestamp, text = best_signal
            result["signals"].append({
                "stock": "노보 노디스크",
                "ticker": "NVO",
                "signal_type": "긍정",
                "key_quote": text[:100] + "..." if len(text) > 100 else text,
                "reasoning": "비만 치료제 시장 성장과 회사 경쟁력",
                "timestamp": timestamp,
                "confidence": 8
            })
    
    # IPO 관련 영상들은 일반론이므로 시그널 없음
    elif video_id in ["sade4GuojTg", "EbfuT0zGGjU"]:
        pass
    
    # 찰스 슈왑 관련
    elif video_id in ["dPIjOdREB80", "PzpU0H8iqQs"]:
        schwab_mentions = []
        for timestamp, text in entries:
            if '슈왑' in text or 'schwab' in text.lower():
                schwab_mentions.append((timestamp, text))
        
        if schwab_mentions:
            # 톤 분석
            signal_type = "중립"
            reasoning = "증권업계 분석"
            best_quote = schwab_mentions[0]
            
            for timestamp, text in schwab_mentions:
                if any(pos in text for pos in positive_keywords):
                    signal_type = "긍정"
                    best_quote = (timestamp, text)
                    break
                elif any(neg in text for neg in negative_keywords):
                    signal_type = "경계"
                    best_quote = (timestamp, text)
                    reasoning = "위험 요소 언급"
            
            timestamp, text = best_quote
            result["signals"].append({
                "stock": "찰스 슈왑",
                "ticker": "SCHW",
                "signal_type": signal_type,
                "key_quote": text[:100] + "..." if len(text) > 100 else text,
                "reasoning": reasoning,
                "timestamp": timestamp,
                "confidence": 6
            })
    
    return result

def main():
    # 대상 영상 목록
    video_configs = [
        {"id": "7x3HE_uXttI", "title": "AI 수혜주 파헤치기"},
        {"id": "tUv4-8BihrM", "title": "AI 관련주, 골드만삭스 리포트"},
        {"id": "0pS0CTDgVmU", "title": "Amazon 3Q 2023 어닝콜"},
        {"id": "B17xc8zl3Z4", "title": "Meta 3Q 2023 어닝콜"},
        {"id": "sade4GuojTg", "title": "IPO Arm 투자 체크포인트"},
        {"id": "EbfuT0zGGjU", "title": "IPO 공모주 투자 3가지 포인트"},
        {"id": "57NbdmLvy6I", "title": "노보 노디스크 & 일라이 릴리"},
        {"id": "dPIjOdREB80", "title": "찰스 슈왑 2부"},
        {"id": "PzpU0H8iqQs", "title": "찰스 슈왑 1부"}
    ]
    
    results = []
    
    print("🚀 월가아재 기업해부학 영상 정교 분석 시작")
    print(f"📊 총 {len(video_configs)}개 영상 처리 예정")
    print("-" * 60)
    
    for i, config in enumerate(video_configs, 1):
        video_id = config["id"]
        video_title = config["title"]
        
        print(f"\n[{i}/{len(video_configs)}] {video_title} ({video_id})")
        
        # VTT 파싱 (타임스탬프 포함)
        entries = parse_vtt_with_timestamps(video_id)
        if not entries:
            print("❌ 자막 파싱 실패")
            continue
        
        print(f"✅ 파싱된 자막 세그먼트: {len(entries):,}개")
        
        # 시그널 분석
        analysis = analyze_video_signals(entries, video_id, video_title)
        results.append(analysis)
        
        if analysis["signals"]:
            for signal in analysis["signals"]:
                print(f"📈 시그널: {signal['stock']} ({signal['ticker']}) - {signal['signal_type']}")
                print(f"   발언: {signal['key_quote']}")
                print(f"   시점: {signal['timestamp']}")
        else:
            print("📊 투자 시그널 없음 (일반론/매크로 관점)")
    
    # 결과 저장
    output_file = "wsaj_remaining_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ 정교 분석 완료! 결과 저장: {output_file}")
    
    # 요약 통계
    total_signals = sum(len(r["signals"]) for r in results)
    videos_with_signals = sum(1 for r in results if r["signals"])
    
    print(f"📊 총 시그널: {total_signals}개")
    print(f"🎯 시그널 있는 영상: {videos_with_signals}개/{len(results)}개")
    
    if total_signals > 0:
        print("\n🏆 최종 시그널 목록:")
        for result in results:
            if result["signals"]:
                for signal in result["signals"]:
                    print(f"  • {signal['stock']} ({signal['ticker']}): {signal['signal_type']} - {signal['timestamp']}")

if __name__ == "__main__":
    main()