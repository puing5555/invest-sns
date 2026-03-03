#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
타임스탬프 교정 테스트 (3개 시그널만)
"""

import os
import re
import json
import time
import random
import asyncio
import subprocess
import tempfile
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

# 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

class TimestampTester:
    def __init__(self):
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
    def timestamp_to_seconds(self, timestamp_str: str) -> int:
        """MM:SS 또는 HH:MM:SS 형식을 초 단위로 변환"""
        if not timestamp_str or ':' not in timestamp_str:
            return 0
        
        parts = timestamp_str.split(':')
        try:
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            pass
        
        return 0
    
    def seconds_to_timestamp(self, seconds: int) -> str:
        """초 단위를 MM:SS 형식으로 변환"""
        if seconds < 3600:  # 1시간 미만
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}:{secs:02d}"
        else:  # 1시간 이상
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
    
    async def get_subtitles_from_yt_dlp(self, video_id: str) -> Optional[List[Dict]]:
        """yt-dlp로 자막 추출"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_template = os.path.join(temp_dir, f"{video_id}.%(ext)s")
                
                # yt-dlp 명령어 실행
                cmd = [
                    'yt-dlp',
                    '--write-auto-subs',
                    '--write-subs',
                    '--sub-lang', 'ko,en',
                    '--sub-format', 'json3',
                    '--skip-download',
                    '--output', output_template,
                    f'https://www.youtube.com/watch?v={video_id}'
                ]
                
                print(f"    🔄 자막 추출 중: {video_id}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=120,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                if result.returncode == 0:
                    # 자막 파일 찾기
                    for ext in ['.ko.json3', '.en.json3', '.json3']:
                        subtitle_file = output_template.replace('.%(ext)s', ext)
                        if os.path.exists(subtitle_file):
                            print(f"    ✅ 자막 파일 발견: {os.path.basename(subtitle_file)}")
                            with open(subtitle_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                events = data.get('events', [])
                                print(f"    📊 자막 이벤트: {len(events)}개")
                                return events
                
                print(f"    ❌ 자막 파일 없음")
                return None
                
        except Exception as e:
            print(f"    ❌ yt-dlp 오류: {e}")
            return None
    
    def find_quote_timestamp(self, subtitles: List[Dict], key_quote: str) -> Optional[int]:
        """자막에서 key_quote 텍스트를 찾아 타임스탬프 반환"""
        if not subtitles or not key_quote:
            return None
        
        print(f"    🔍 Quote 검색: {key_quote[:50]}...")
        
        # key_quote 정규화 (공백, 특수문자 제거)
        normalized_quote = re.sub(r'[^\w가-힣]', '', key_quote.lower())
        print(f"    🔍 정규화된 Quote: {normalized_quote[:50]}...")
        
        if len(normalized_quote) < 5:  # 너무 짧으면 스킵
            print(f"    ⚠️ Quote가 너무 짧음")
            return None
        
        # 자막 텍스트 구성
        subtitle_segments = []
        
        for event in subtitles:
            if 'segs' in event:
                start_time = event.get('tStartMs', 0) / 1000  # ms -> s
                for seg in event['segs']:
                    text = seg.get('utf8', '')
                    if text:
                        subtitle_segments.append({
                            'text': text,
                            'timestamp': int(start_time)
                        })
        
        print(f"    📊 자막 세그먼트: {len(subtitle_segments)}개")
        
        # 연속된 텍스트로 합치고 위치-타임스탬프 매핑 생성
        full_text = ""
        position_to_timestamp = {}
        
        for seg in subtitle_segments:
            start_pos = len(full_text)
            full_text += seg['text']
            end_pos = len(full_text)
            
            # 이 텍스트 범위의 타임스탬프 기록
            for pos in range(start_pos, end_pos):
                position_to_timestamp[pos] = seg['timestamp']
        
        print(f"    📊 전체 자막 길이: {len(full_text)}자")
        
        # 정규화된 자막 텍스트
        normalized_subtitle = re.sub(r'[^\w가-힣]', '', full_text.lower())
        print(f"    📊 정규화된 자막 길이: {len(normalized_subtitle)}자")
        
        # key_quote 검색
        quote_pos = normalized_subtitle.find(normalized_quote)
        if quote_pos == -1:
            # 부분 매칭 시도 (첫 절반)
            half_quote = normalized_quote[:len(normalized_quote)//2]
            if len(half_quote) >= 5:
                quote_pos = normalized_subtitle.find(half_quote)
                if quote_pos != -1:
                    print(f"    🔍 부분 매칭 성공: 위치 {quote_pos}")
        else:
            print(f"    🔍 전체 매칭 성공: 위치 {quote_pos}")
        
        if quote_pos == -1:
            print(f"    ❌ Quote를 자막에서 찾을 수 없음")
            # 디버깅을 위해 자막 시작 부분 출력
            print(f"    📄 자막 시작 부분: {normalized_subtitle[:200]}...")
            return None
        
        # 해당 위치의 타임스탬프 찾기
        # 정규화로 인해 위치가 달라질 수 있으므로 비율로 계산
        if normalized_subtitle:
            ratio = quote_pos / len(normalized_subtitle)
            target_pos = int(len(full_text) * ratio)
            
            print(f"    🎯 타겟 위치: {target_pos} (비율: {ratio:.3f})")
            
            # 가장 가까운 타임스탬프 찾기
            best_timestamp = 0
            min_distance = float('inf')
            
            for pos, timestamp in position_to_timestamp.items():
                distance = abs(pos - target_pos)
                if distance < min_distance:
                    min_distance = distance
                    best_timestamp = timestamp
            
            print(f"    ⏰ 발견된 타임스탬프: {best_timestamp}초")
            return best_timestamp
        
        return None
    
    async def test_signals(self, limit: int = 3):
        """3개 시그널로 테스트"""
        try:
            url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
            params = {
                'select': 'id,timestamp,key_quote,stock,video_id,influencer_videos(video_id,title)',
                'limit': str(limit)
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            signals = response.json()
            print(f"\n📊 테스트 대상: {len(signals)}개 시그널")
            
            for i, signal in enumerate(signals):
                print(f"\n{'='*60}")
                print(f"🧪 테스트 {i+1}/{len(signals)}")
                print(f"{'='*60}")
                
                signal_id = signal['id']
                video_info = signal.get('influencer_videos')
                key_quote = signal['key_quote']
                current_timestamp_str = signal['timestamp']
                
                if not video_info or not key_quote:
                    print(f"❌ 데이터 부족")
                    continue
                
                video_id = video_info['video_id']
                video_title = video_info.get('title', '')
                
                print(f"🆔 Signal ID: {signal_id}")
                print(f"🎥 Video: {video_id}")
                print(f"📺 Title: {video_title}")
                print(f"💬 Quote: {key_quote}")
                print(f"⏰ Current: {current_timestamp_str}")
                
                # 현재 타임스탬프를 초 단위로 변환
                current_seconds = self.timestamp_to_seconds(current_timestamp_str)
                print(f"⏱️ Current (초): {current_seconds}")
                
                # 자막 추출
                subtitles = await self.get_subtitles_from_yt_dlp(video_id)
                if not subtitles:
                    print(f"❌ 자막 추출 실패")
                    continue
                
                # key_quote로 실제 타임스탬프 찾기
                actual_seconds = self.find_quote_timestamp(subtitles, key_quote)
                if actual_seconds is None:
                    print(f"❌ Quote 매칭 실패")
                    continue
                
                # 결과 비교
                diff = abs(current_seconds - actual_seconds)
                new_timestamp_str = self.seconds_to_timestamp(actual_seconds)
                
                print(f"🎯 실제 타임스탬프: {actual_seconds}초 ({new_timestamp_str})")
                print(f"📊 차이: {diff}초")
                print(f"{'✅' if diff >= 30 else '⏭️'} 교정 {'필요' if diff >= 30 else '불필요'}")
                
                # 잠시 대기
                await asyncio.sleep(2)
            
            print(f"\n{'='*60}")
            print(f"🧪 테스트 완료")
            print(f"{'='*60}")
                
        except Exception as e:
            print(f"❌ 테스트 오류: {e}")
            import traceback
            traceback.print_exc()

async def main():
    tester = TimestampTester()
    await tester.test_signals(3)

if __name__ == '__main__':
    asyncio.run(main())