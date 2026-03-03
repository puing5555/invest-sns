#!/usr/bin/env python3
"""
timestamp_corrector.py - 타임스탬프 전수 교정 도구
- Supabase에서 137개 시그널 조회
- key_quote를 자막에서 검색하여 실제 발언 시점 찾기
- 30초 이상 차이나면 교정
- 레이트리밋 규칙 준수
"""

import os
import re
import json
import time
import random
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(Path(__file__).parent.parent / '.env.local')

# 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# 레이트리밋 설정
MIN_DELAY = 2
MAX_DELAY = 3
RETRY_WAIT = 60
BATCH_SIZE = 20
BATCH_BREAK = 300  # 5분

class TimestampCorrector:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.processed_count = 0
        self.corrected_count = 0
        self.failed_count = 0
        self.results = []
        
    def extract_video_id_from_url(self, video_url: str) -> str:
        """YouTube URL에서 video_id 추출"""
        patterns = [
            r'v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'embed/([a-zA-Z0-9_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        return ""
    
    def extract_timestamp_from_url(self, video_url: str) -> int:
        """URL의 t= 파라미터에서 타임스탬프 추출 (초 단위)"""
        match = re.search(r't=(\d+)', video_url)
        if match:
            return int(match.group(1))
        return 0
    
    async def get_subtitles_from_yt_dlp(self, video_id: str) -> Optional[List[Dict]]:
        """yt-dlp로 자막 추출"""
        try:
            import subprocess
            import tempfile
            
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = os.path.join(temp_dir, f"{video_id}.json")
                
                # yt-dlp 명령어 실행
                cmd = [
                    'yt-dlp',
                    '--write-auto-subs',
                    '--write-subs',
                    '--sub-lang', 'ko,en',
                    '--sub-format', 'json3',
                    '--skip-download',
                    '--output', output_path,
                    f'https://www.youtube.com/watch?v={video_id}'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # 자막 파일 찾기
                    for ext in ['.ko.json3', '.en.json3', '.json3']:
                        subtitle_file = output_path.replace('.json', ext)
                        if os.path.exists(subtitle_file):
                            with open(subtitle_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                return data.get('events', [])
                
                return None
                
        except Exception as e:
            print(f"    ❌ yt-dlp 오류: {e}")
            return None
    
    def find_quote_timestamp(self, subtitles: List[Dict], key_quote: str) -> Optional[int]:
        """자막에서 key_quote 텍스트를 찾아 타임스탬프 반환"""
        if not subtitles or not key_quote:
            return None
        
        # key_quote 정규화 (공백, 특수문자 제거)
        normalized_quote = re.sub(r'[^\w가-힣]', '', key_quote.lower())
        
        if len(normalized_quote) < 5:  # 너무 짧으면 스킵
            return None
        
        # 자막 텍스트 구성
        subtitle_text = ""
        timestamp_map = {}  # 텍스트 위치 -> 타임스탬프 매핑
        
        current_pos = 0
        for event in subtitles:
            if 'segs' in event:
                start_time = event.get('tStartMs', 0) / 1000  # ms -> s
                for seg in event['segs']:
                    text = seg.get('utf8', '')
                    if text:
                        timestamp_map[current_pos] = int(start_time)
                        subtitle_text += text
                        current_pos = len(subtitle_text)
        
        # 정규화된 자막 텍스트
        normalized_subtitle = re.sub(r'[^\w가-힣]', '', subtitle_text.lower())
        
        # key_quote 검색
        quote_pos = normalized_subtitle.find(normalized_quote)
        if quote_pos == -1:
            # 부분 매칭 시도 (50% 이상 일치)
            quote_words = normalized_quote.split()
            if len(quote_words) >= 3:
                for i in range(len(quote_words) - 1):
                    partial = ''.join(quote_words[i:i+2])
                    if len(partial) >= 5:
                        partial_pos = normalized_subtitle.find(partial)
                        if partial_pos != -1:
                            quote_pos = partial_pos
                            break
        
        if quote_pos == -1:
            return None
        
        # 해당 위치의 타임스탬프 찾기
        best_timestamp = 0
        for pos, timestamp in timestamp_map.items():
            if pos <= quote_pos:
                best_timestamp = timestamp
            else:
                break
        
        return best_timestamp
    
    async def correct_timestamp(self, signal: Dict) -> Dict:
        """단일 시그널의 타임스탬프 교정"""
        signal_id = signal['id']
        video_url = signal['video_url']
        key_quote = signal['key_quote']
        current_timestamp = signal['timestamp_seconds']
        
        print(f"  🔍 시그널 {signal_id}: {key_quote[:50]}...")
        
        # URL에서 video_id 추출
        video_id = self.extract_video_id_from_url(video_url)
        if not video_id:
            return {
                'signal_id': signal_id,
                'status': 'error',
                'reason': 'invalid_video_url',
                'video_url': video_url
            }
        
        # URL의 t= 파라미터 확인
        url_timestamp = self.extract_timestamp_from_url(video_url)
        
        # 자막 추출
        subtitles = await self.get_subtitles_from_yt_dlp(video_id)
        if not subtitles:
            return {
                'signal_id': signal_id,
                'status': 'error',
                'reason': 'no_subtitles',
                'video_id': video_id
            }
        
        # key_quote로 실제 타임스탬프 찾기
        actual_timestamp = self.find_quote_timestamp(subtitles, key_quote)
        if actual_timestamp is None:
            return {
                'signal_id': signal_id,
                'status': 'error',
                'reason': 'quote_not_found',
                'key_quote': key_quote
            }
        
        # 30초 이상 차이나는지 확인
        diff = abs(current_timestamp - actual_timestamp)
        needs_correction = diff >= 30
        
        result = {
            'signal_id': signal_id,
            'video_id': video_id,
            'current_timestamp': current_timestamp,
            'url_timestamp': url_timestamp,
            'actual_timestamp': actual_timestamp,
            'diff_seconds': diff,
            'needs_correction': needs_correction,
            'status': 'success'
        }
        
        if needs_correction:
            # Supabase UPDATE 실행
            try:
                update_result = self.supabase.table('influencer_signals') \
                    .update({'timestamp_seconds': actual_timestamp}) \
                    .eq('id', signal_id) \
                    .execute()
                
                if update_result.data:
                    result['updated'] = True
                    result['status'] = 'corrected'
                    self.corrected_count += 1
                    print(f"    ✅ 교정 완료: {current_timestamp}s → {actual_timestamp}s (차이: {diff}s)")
                else:
                    result['updated'] = False
                    result['status'] = 'update_failed'
                    print(f"    ❌ 업데이트 실패")
                    
            except Exception as e:
                result['updated'] = False
                result['status'] = 'update_error'
                result['error'] = str(e)
                print(f"    ❌ 업데이트 오류: {e}")
        else:
            print(f"    ⏭️ 교정 불필요: 차이 {diff}s < 30s")
        
        return result
    
    async def get_all_signals(self) -> List[Dict]:
        """Supabase에서 모든 시그널 조회"""
        try:
            response = self.supabase.table('influencer_signals') \
                .select('id,video_url,key_quote,timestamp_seconds') \
                .execute()
            
            if response.data:
                print(f"📊 총 {len(response.data)}개 시그널 조회 완료")
                return response.data
            else:
                print("❌ 시그널 조회 실패")
                return []
                
        except Exception as e:
            print(f"❌ Supabase 조회 오류: {e}")
            return []
    
    async def run_correction(self, output_file: str = 'timestamp_correction_results.json'):
        """타임스탬프 교정 실행"""
        print(f"\n{'='*60}")
        print(f"타임스탬프 전수 교정 시작")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # 모든 시그널 조회
        signals = await self.get_all_signals()
        if not signals:
            return
        
        total_count = len(signals)
        print(f"📊 교정 대상: {total_count}개 시그널\n")
        
        # 배치별 처리
        for i in range(0, total_count, BATCH_SIZE):
            batch = signals[i:i+BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (total_count + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"📦 배치 {batch_num}/{total_batches} ({len(batch)}개) 처리 중...")
            
            for j, signal in enumerate(batch):
                try:
                    # 레이트리밋 딜레이
                    if j > 0:  # 첫 번째가 아니면 딜레이
                        delay = random.uniform(MIN_DELAY, MAX_DELAY)
                        await asyncio.sleep(delay)
                    
                    result = await self.correct_timestamp(signal)
                    self.results.append(result)
                    self.processed_count += 1
                    
                    if result['status'] == 'error':
                        self.failed_count += 1
                    
                    # 진행 상황 표시
                    progress = (i + j + 1) / total_count * 100
                    print(f"    📈 진행: {progress:.1f}% ({i + j + 1}/{total_count})")
                    
                except Exception as e:
                    print(f"    ❌ 시그널 {signal['id']} 처리 오류: {e}")
                    self.failed_count += 1
                    self.results.append({
                        'signal_id': signal['id'],
                        'status': 'exception',
                        'error': str(e)
                    })
            
            # 배치 간 휴식 (마지막 배치가 아니면)
            if i + BATCH_SIZE < total_count:
                print(f"    ⏸️ 배치 완료, {BATCH_BREAK}초 대기...")
                await asyncio.sleep(BATCH_BREAK)
        
        elapsed = time.time() - start_time
        
        # 결과 저장
        output = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': round(elapsed, 1),
            'total_signals': total_count,
            'processed': self.processed_count,
            'corrected': self.corrected_count,
            'failed': self.failed_count,
            'results': self.results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ 타임스탬프 교정 완료!")
        print(f"⏱️ 소요 시간: {elapsed:.0f}초 ({elapsed/60:.1f}분)")
        print(f"📊 처리: {self.processed_count}/{total_count}개")
        print(f"✏️ 교정: {self.corrected_count}개")
        print(f"❌ 실패: {self.failed_count}개")
        print(f"📁 결과 파일: {output_file}")
        print(f"{'='*60}")

async def main():
    corrector = TimestampCorrector()
    await corrector.run_correction()

if __name__ == '__main__':
    asyncio.run(main())