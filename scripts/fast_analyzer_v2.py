#!/usr/bin/env python3
"""
fast_analyzer_v2.py - 고속 병렬 시그널 분석기 (DB 구조 V2 대응)
- 새로운 DB 구조에 맞춤: influencer_signals + influencer_videos
- timestamp MM:SS 형식 자동 매칭
- key_quote 기반 타임스탬프 검증 및 자동 교정
- Supabase 직접 INSERT
"""

import os
import re
import json
import asyncio
import aiohttp
import time
import glob
import requests
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

# 설정
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"
MAX_CONCURRENT = 3
MIN_CONCURRENT = 1
DELAY_BETWEEN = 1.0
MAX_RETRIES = 2

# 멀티 게스트 채널 설정
MULTI_GUEST_CHANNELS = {
    'https://www.youtube.com/@3protv',
    'https://www.youtube.com/@3ProTV',
    '삼프로TV',
}

def extract_guest_from_title(title: str) -> List[str]:
    """영상 제목에서 게스트명 추출"""
    if '|' not in title:
        return []
    after_pipe = title.split('|')[-1].strip()
    parts = [p.strip() for p in after_pipe.split(',')]
    names = []
    for part in parts:
        match = re.match(r'([가-힣]{2,3})', part.strip())
        if match:
            names.append(match.group(1))
    return names

class TimestampMatcher:
    """자막과 key_quote 매칭을 통한 정확한 타임스탬프 추출"""
    
    def __init__(self):
        pass
    
    def load_subtitle_from_json(self, subtitle_file: str) -> List[Dict]:
        """자막 파일에서 세그먼트 로드"""
        try:
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                segments = json.load(f)
            if not isinstance(segments, list):
                return []
            return segments
        except Exception as e:
            print(f"    자막 로드 오류: {e}")
            return []
    
    def find_quote_in_subtitle(self, segments: List[Dict], key_quote: str) -> Optional[str]:
        """자막에서 key_quote를 찾아 MM:SS 형식의 타임스탬프 반환"""
        if not segments or not key_quote:
            return None
        
        # key_quote 정규화
        normalized_quote = re.sub(r'[^\w가-힣]', '', key_quote.lower())
        if len(normalized_quote) < 5:
            return None
        
        # 자막 텍스트 구성 (timestamp -> text 매핑)
        timestamp_to_text = {}
        for seg in segments:
            if isinstance(seg, dict) and 'text' in seg:
                timestamp = seg.get('timestamp', '0:00')
                text = seg.get('text', '')
                timestamp_to_text[timestamp] = timestamp_to_text.get(timestamp, '') + text
        
        # 전체 자막 텍스트로 매칭
        all_timestamps = []
        full_subtitle = ""
        
        for timestamp in sorted(timestamp_to_text.keys()):
            text = timestamp_to_text[timestamp]
            start_pos = len(full_subtitle)
            full_subtitle += text
            all_timestamps.append({
                'timestamp': timestamp,
                'start_pos': start_pos,
                'end_pos': len(full_subtitle),
                'text': text
            })
        
        # 정규화된 자막에서 quote 검색
        normalized_subtitle = re.sub(r'[^\w가-힣]', '', full_subtitle.lower())
        quote_pos = normalized_subtitle.find(normalized_quote)
        
        if quote_pos == -1:
            # 부분 매칭 시도
            half_quote = normalized_quote[:len(normalized_quote)//2]
            if len(half_quote) >= 5:
                quote_pos = normalized_subtitle.find(half_quote)
        
        if quote_pos == -1:
            return None
        
        # 위치에 해당하는 타임스탬프 찾기
        if normalized_subtitle:
            ratio = quote_pos / len(normalized_subtitle)
            target_pos = int(len(full_subtitle) * ratio)
            
            for ts_info in all_timestamps:
                if ts_info['start_pos'] <= target_pos <= ts_info['end_pos']:
                    return ts_info['timestamp']
            
            # 가장 가까운 타임스탬프 반환
            best_timestamp = "0:00"
            min_distance = float('inf')
            
            for ts_info in all_timestamps:
                distance = min(
                    abs(ts_info['start_pos'] - target_pos),
                    abs(ts_info['end_pos'] - target_pos)
                )
                if distance < min_distance:
                    min_distance = distance
                    best_timestamp = ts_info['timestamp']
            
            return best_timestamp
        
        return None

class FastAnalyzerV2:
    def __init__(self, prompt_path: str = None):
        self.api_key = ANTHROPIC_API_KEY
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.current_concurrency = MAX_CONCURRENT
        self.rate_limited = False
        self.stats = {'processed': 0, 'skipped': 0, 'errors': 0, 'signals': 0, 'inserted': 0}
        self.results = []
        self.timestamp_matcher = TimestampMatcher()
        
        # 프롬프트 로드
        if prompt_path:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        else:
            # 기본 프롬프트 경로
            default = Path(__file__).parent.parent / 'prompts' / 'pipeline_v10.md'
            if default.exists():
                with open(default, 'r', encoding='utf-8') as f:
                    self.prompt_template = f.read()
            else:
                raise FileNotFoundError(f"프롬프트 파일 없음: {default}")
    
    def load_subtitle(self, subtitle_file: str) -> str:
        """자막 파일에서 텍스트 추출"""
        segments = self.timestamp_matcher.load_subtitle_from_json(subtitle_file)
        if not segments:
            return ""
        text_parts = []
        for seg in segments:
            if isinstance(seg, dict) and 'text' in seg:
                text_parts.append(seg['text'])
        return " ".join(text_parts).strip()
    
    def create_prompt(self, channel_url: str, video_title: str, video_id: str, subtitle: str) -> str:
        """분석 프롬프트 생성"""
        subtitle_trimmed = subtitle[:8000] if len(subtitle) > 8000 else subtitle
        
        prompt = self.prompt_template.replace('{CHANNEL_URL}', channel_url)
        
        # 멀티 게스트 채널: 제목에서 게스트명 추출하여 힌트 제공
        speaker_hint = ""
        is_multi_guest = any(ch in channel_url for ch in MULTI_GUEST_CHANNELS)
        if is_multi_guest:
            guests = extract_guest_from_title(video_title)
            if guests:
                speaker_hint = f"\n⚠️ 이 영상의 출연자(speaker): {', '.join(guests)}\n시그널의 화자를 위 출연자명으로 정확히 구분해주세요.\n"
        
        prompt += f"""

=== 분석 대상 영상 ===
제목: {video_title}
URL: https://www.youtube.com/watch?v={video_id}
{speaker_hint}
=== 자막 내용 ===
{subtitle_trimmed}

=== 분석 지시사항 ===
위 영상의 자막을 분석하고 JSON 형태로 시그널을 추출해주세요.
각 시그널에는 key_quote(핵심 발언)를 정확히 포함시켜주세요.
"""
        return prompt
    
    def parse_response(self, text: str) -> Dict:
        """응답 파싱"""
        try:
            if '```json' in text:
                start = text.find('```json') + 7
                end = text.find('```', start)
                return json.loads(text[start:end].strip())
            elif '{' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        return {"error": "parse_failed", "raw": text[:500]}
    
    async def find_or_create_video_record(self, video_id: str, video_title: str, channel_id: str) -> Optional[str]:
        """video 레코드 찾기 또는 생성, DB video_id(UUID) 반환"""
        try:
            # 먼저 기존 레코드 검색
            url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
            params = {'select': 'id', 'video_id': f'eq.{video_id}'}
            
            response = requests.get(url, headers=self.supabase_headers, params=params)
            if response.status_code == 200:
                videos = response.json()
                if videos:
                    return videos[0]['id']  # 기존 레코드의 UUID 반환
            
            # 새 레코드 생성
            new_video = {
                'channel_id': channel_id,
                'video_id': video_id,
                'title': video_title,
                'published_at': datetime.now().isoformat(),
                'duration_seconds': 0,  # 임시값
                'has_subtitle': True,
                'subtitle_language': 'ko',
                'analyzed_at': datetime.now().isoformat(),
                'pipeline_version': 'V10',
                'signal_count': 0  # 나중에 업데이트
            }
            
            response = requests.post(url, headers=self.supabase_headers, json=new_video)
            if response.status_code in [200, 201]:
                created = response.json()
                if created:
                    return created[0]['id']  # 새로 생성된 레코드의 UUID
            
            return None
            
        except Exception as e:
            print(f"    비디오 레코드 처리 오류: {e}")
            return None
    
    async def insert_signals_to_supabase(self, signals: List[Dict], db_video_id: str, 
                                       subtitle_file: str) -> int:
        """시그널들을 Supabase에 INSERT"""
        if not signals or not db_video_id:
            return 0
        
        # 자막 세그먼트 로드 (타임스탬프 매칭용)
        subtitle_segments = self.timestamp_matcher.load_subtitle_from_json(subtitle_file)
        
        inserted_count = 0
        
        for signal in signals:
            try:
                # 필수 필드 검증
                if not all(key in signal for key in ['stock', 'signal', 'key_quote']):
                    print(f"    필수 필드 누락, 스킵")
                    continue
                
                # key_quote로 정확한 타임스탬프 찾기
                timestamp_str = "0:00"  # 기본값
                key_quote = signal.get('key_quote', '')
                
                if key_quote and subtitle_segments:
                    matched_timestamp = self.timestamp_matcher.find_quote_in_subtitle(
                        subtitle_segments, key_quote
                    )
                    if matched_timestamp:
                        timestamp_str = matched_timestamp
                        print(f"    타임스탬프 매칭 성공: {timestamp_str}")
                
                # INSERT용 데이터 구성
                signal_data = {
                    'video_id': db_video_id,
                    'speaker_id': signal.get('speaker_id'),  # 나중에 매핑 필요
                    'stock': signal.get('stock'),
                    'ticker': signal.get('ticker'),
                    'market': signal.get('market', 'KR'),
                    'mention_type': signal.get('mention_type', '직접'),
                    'signal': signal.get('signal'),
                    'confidence': signal.get('confidence', 'medium'),
                    'timestamp': timestamp_str,  # MM:SS 형식
                    'key_quote': key_quote,
                    'reasoning': signal.get('reasoning', ''),
                    'review_status': 'pending',
                    'pipeline_version': 'V10'
                }
                
                # Supabase INSERT
                url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
                response = requests.post(url, headers=self.supabase_headers, json=signal_data)
                
                if response.status_code in [200, 201]:
                    inserted_count += 1
                    print(f"    시그널 INSERT 성공: {signal.get('stock')} {signal.get('signal')}")
                else:
                    print(f"    시그널 INSERT 실패: {response.status_code} - {response.text[:100]}")
                
            except Exception as e:
                print(f"    시그널 INSERT 오류: {e}")
        
        self.stats['inserted'] += inserted_count
        return inserted_count
    
    async def analyze_one(self, session: aiohttp.ClientSession, video_id: str, 
                          subtitle_file: str, channel_url: str, video_title: str,
                          channel_id: str = None) -> Dict:
        """단일 영상 분석"""
        async with self.semaphore:
            subtitle = self.load_subtitle(subtitle_file)
            if len(subtitle) < 100:
                self.stats['skipped'] += 1
                return {'video_id': video_id, 'status': 'skipped', 'reason': 'too_short'}
            
            prompt = self.create_prompt(channel_url, video_title, video_id, subtitle)
            
            for attempt in range(MAX_RETRIES + 1):
                try:
                    payload = {
                        'model': MODEL,
                        'max_tokens': 4000,
                        'messages': [{'role': 'user', 'content': prompt}]
                    }
                    
                    async with session.post(API_URL, json=payload, headers=self.headers, 
                                          timeout=aiohttp.ClientTimeout(total=180)) as resp:
                        if resp.status == 429:
                            # Rate limited
                            retry_after = int(resp.headers.get('retry-after', '30'))
                            print(f"  [429] Rate limited, waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        resp.raise_for_status()
                        data = await resp.json()
                        
                        if 'content' in data and data['content']:
                            text = data['content'][0].get('text', '')
                            result = self.parse_response(text)
                            signals = result.get('signals', [])
                            
                            # 멀티 게스트 채널: 시그널에 speaker 정보 추가
                            is_multi = any(ch in channel_url for ch in MULTI_GUEST_CHANNELS)
                            if is_multi:
                                guests = extract_guest_from_title(video_title)
                                if guests:
                                    for sig in signals:
                                        if 'speaker' not in sig or not sig.get('speaker'):
                                            sig['speaker'] = guests[0]
                            
                            # Supabase에 직접 INSERT
                            if signals and channel_id:
                                db_video_id = await self.find_or_create_video_record(
                                    video_id, video_title, channel_id
                                )
                                if db_video_id:
                                    inserted = await self.insert_signals_to_supabase(
                                        signals, db_video_id, subtitle_file
                                    )
                                    print(f"  ✅ {video_id[:12]}... → {len(signals)}개 시그널, {inserted}개 INSERT")
                                else:
                                    print(f"  ❌ {video_id[:12]}... → 비디오 레코드 생성 실패")
                            else:
                                print(f"  ✅ {video_id[:12]}... → {len(signals)}개 시그널")
                            
                            self.stats['processed'] += 1
                            self.stats['signals'] += len(signals)
                            
                            await asyncio.sleep(DELAY_BETWEEN)
                            return {
                                'video_id': video_id,
                                'title': video_title,
                                'status': 'ok',
                                'signals': signals,
                                'inserted': inserted if 'inserted' in locals() else 0,
                                'raw_result': result
                            }
                
                except asyncio.TimeoutError:
                    print(f"  [TIMEOUT] {video_id} attempt {attempt+1}")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(10)
                except Exception as e:
                    print(f"  [ERROR] {video_id}: {e}")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(5)
            
            self.stats['errors'] += 1
            return {'video_id': video_id, 'status': 'error', 'reason': 'max_retries'}
    
    async def run_batch(self, videos: List[Dict], channel_url: str, output_file: str,
                        channel_id: str = None):
        """배치 분석 실행"""
        print(f"\n{'='*80}")
        print(f"고속 병렬 분석기 V2 시작")
        print(f"대상: {len(videos)}개 영상, 모델: {MODEL}")
        print(f"DB 구조: influencer_signals + influencer_videos")
        print(f"{'='*80}\n")
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for v in videos:
                task = self.analyze_one(
                    session, v['video_id'], v['subtitle_file'],
                    channel_url, v.get('title', ''), channel_id
                )
                tasks.append(task)
            
            # 모든 태스크 실행
            self.results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        # 결과 저장
        output = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': round(elapsed, 1),
            'stats': self.stats,
            'results': self.results
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*80}")
        print(f"완료! {elapsed:.0f}초 ({elapsed/60:.1f}분)")
        print(f"처리: {self.stats['processed']}, 스킵: {self.stats['skipped']}, "
              f"에러: {self.stats['errors']}")
        print(f"시그널: {self.stats['signals']}, INSERT: {self.stats['inserted']}")
        print(f"결과: {output_file}")
        print(f"{'='*80}")

async def main():
    """CLI 실행"""
    import argparse
    parser = argparse.ArgumentParser(description='고속 병렬 시그널 분석기 V2')
    parser.add_argument('--subs-dir', required=True, help='자막 파일 디렉토리')
    parser.add_argument('--channel-url', required=True, help='채널 URL')
    parser.add_argument('--channel-id', help='Supabase channel_id (UUID)')
    parser.add_argument('--titles-file', help='영상 제목 파일 (video_id|||title)')
    parser.add_argument('--output', default='fast_analysis_v2_results.json', help='결과 파일')
    parser.add_argument('--skip-ids', help='스킵할 video_id 목록 파일')
    parser.add_argument('--concurrency', type=int, default=3, help='동시 처리 수')
    parser.add_argument('--prompt', help='프롬프트 파일 경로')
    args = parser.parse_args()
    
    global MAX_CONCURRENT
    MAX_CONCURRENT = args.concurrency
    
    # 자막 파일 로드
    subs_files = glob.glob(os.path.join(args.subs_dir, '*.json'))
    print(f"자막 파일: {len(subs_files)}개")
    
    # 스킵 ID 로드
    skip_ids = set()
    if args.skip_ids and os.path.exists(args.skip_ids):
        with open(args.skip_ids, 'r') as f:
            skip_ids = set(line.strip() for line in f if line.strip())
        print(f"스킵 ID: {len(skip_ids)}개")
    
    # 제목 로드
    titles = {}
    if args.titles_file and os.path.exists(args.titles_file):
        for enc in ['utf-8', 'cp949', 'utf-16']:
            try:
                with open(args.titles_file, 'r', encoding=enc) as f:
                    for line in f:
                        if '|||' in line:
                            vid, title = line.strip().split('|||', 1)
                            titles[vid.strip()] = title.strip()
                break
            except:
                continue
    
    # 영상 목록 구성
    videos = []
    for sf in subs_files:
        vid = os.path.splitext(os.path.basename(sf))[0]
        if vid not in skip_ids:
            if titles and vid not in titles:
                continue
            videos.append({
                'video_id': vid,
                'subtitle_file': sf,
                'title': titles.get(vid, f'영상 {vid}')
            })
    
    print(f"분석 대상: {len(videos)}개")
    
    if not videos:
        print("분석할 영상 없음!")
        return
    
    analyzer = FastAnalyzerV2(prompt_path=args.prompt)
    await analyzer.run_batch(videos, args.channel_url, args.output, args.channel_id)

if __name__ == '__main__':
    asyncio.run(main())