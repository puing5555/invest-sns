# subtitle_extractor.py - 자막 추출 모듈
import os
import time
import json
import requests
from typing import Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import yt_dlp
from pipeline_config import PipelineConfig

class SubtitleExtractor:
    def __init__(self):
        self.config = PipelineConfig()
        self.proxy_config = self.config.get_proxy_config()
        self.formatter = TextFormatter()
        
        # yt-dlp 설정
        self.ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko', 'kr', 'ko-KR'],
            'skip_download': True,
            'quiet': True
        }
        
        if self.proxy_config:
            self.ydl_opts['proxy'] = self.proxy_config['https']
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """유튜브 URL에서 비디오 ID 추출"""
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def extract_with_youtube_transcript_api(self, video_id: str) -> Optional[str]:
        """youtube_transcript_api로 자막 추출"""
        try:
            # 프록시 설정
            if self.proxy_config:
                # youtube_transcript_api는 requests를 사용하므로 환경변수로 프록시 설정
                os.environ['HTTP_PROXY'] = self.proxy_config['http']
                os.environ['HTTPS_PROXY'] = self.proxy_config['https']
            
            # 한국어 자막 시도
            languages = ['ko', 'kr', 'ko-KR', 'ko-US']
            
            for lang in languages:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # 수동 자막 우선
                    try:
                        transcript = transcript_list.find_manually_created_transcript([lang])
                        subtitle_data = transcript.fetch()
                        subtitle_text = self.formatter.format_transcript(subtitle_data)
                        print(f"[OK] 수동 자막 추출 성공 ({lang}): {len(subtitle_text)} 글자")
                        return subtitle_text
                    except:
                        pass
                    
                    # 자동 자막 시도
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        subtitle_data = transcript.fetch()
                        subtitle_text = self.formatter.format_transcript(subtitle_data)
                        print(f"[OK] 자동 자막 추출 성공 ({lang}): {len(subtitle_text)} 글자")
                        return subtitle_text
                    except:
                        pass
                        
                except Exception as e:
                    continue
                    
            print(f"[ERROR] 한국어 자막 없음 (video_id: {video_id})")
            return None
            
        except Exception as e:
            print(f"[ERROR] youtube_transcript_api 에러: {e}")
            return None
        finally:
            # 프록시 환경변수 정리
            if 'HTTP_PROXY' in os.environ:
                del os.environ['HTTP_PROXY']
            if 'HTTPS_PROXY' in os.environ:
                del os.environ['HTTPS_PROXY']
    
    def extract_with_yt_dlp(self, url: str) -> Optional[str]:
        """yt-dlp로 자막 추출"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # 정보 추출
                info = ydl.extract_info(url, download=False)
                
                # 자막 파일 다운로드 시도
                ydl.download([url])
                
                # 자막 파일 찾기
                video_id = info.get('id')
                subtitle_files = [
                    f"{video_id}.ko.vtt",
                    f"{video_id}.kr.vtt", 
                    f"{video_id}.ko-KR.vtt",
                    f"{video_id}.live_chat.json"
                ]
                
                for subtitle_file in subtitle_files:
                    if os.path.exists(subtitle_file):
                        try:
                            with open(subtitle_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # VTT 파일 파싱
                            if subtitle_file.endswith('.vtt'):
                                subtitle_text = self.parse_vtt_content(content, include_timestamps=True)
                                print(f"[OK] yt-dlp 자막 추출 성공: {len(subtitle_text)} 글자")
                                
                                # 임시 파일 정리
                                os.remove(subtitle_file)
                                return subtitle_text
                        except Exception as e:
                            print(f"자막 파일 읽기 에러: {e}")
                            continue
                        finally:
                            # 임시 파일 정리
                            if os.path.exists(subtitle_file):
                                os.remove(subtitle_file)
                
                print(f"[ERROR] yt-dlp 자막 파일 없음")
                return None
                
        except Exception as e:
            print(f"[ERROR] yt-dlp 에러: {e}")
            return None
    
    def parse_vtt_content(self, content: str, include_timestamps: bool = True) -> str:
        """
        VTT 파일 내용을 텍스트로 파싱 (통합 파서 — 전 프로젝트 단일 사용)

        Args:
            content: VTT 파일 전체 내용 (문자열)
            include_timestamps: True(기본) → "[HH:MM:SS] 발언" 포맷 유지
                                False → 텍스트만 (공백으로 이어붙임)
        Returns:
            파싱된 자막 텍스트
        """
        import re

        if include_timestamps:
            lines_out = []
            current_ts = None
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('WEBVTT') or line.startswith('NOTE') \
                        or line.startswith('Kind:') or line.startswith('Language:'):
                    continue
                # 타임코드 캡처: 00:05:30.000 --> 00:05:35.000
                ts_match = re.match(r'(\d{1,2}:\d{2}:\d{2})\.\d+ -->', line)
                if ts_match:
                    current_ts = ts_match.group(1)
                    continue
                if re.match(r'^\d+$', line):
                    continue
                clean = re.sub(r'<[^>]+>', '', line).strip()
                if clean:
                    if current_ts:
                        lines_out.append(f'[{current_ts}] {clean}')
                        current_ts = None
                    else:
                        lines_out.append(clean)
            # 연속 중복 제거
            deduped = []
            prev = None
            for l in lines_out:
                if l != prev:
                    deduped.append(l)
                prev = l
            return '\n'.join(deduped[:4000])
        else:
            # 텍스트만 (레거시 호환)
            lines = []
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('WEBVTT') or line.startswith('NOTE') \
                        or line.startswith('Kind:') or line.startswith('Language:'):
                    continue
                if '-->' in line or re.match(r'^\d+$', line):
                    continue
                clean = re.sub(r'<[^>]+>', '', line).strip()
                if clean:
                    lines.append(clean)
            deduped = []
            prev = None
            for l in lines:
                if l != prev:
                    deduped.append(l)
                prev = l
            return ' '.join(deduped[:3000])

    def parse_vtt_file(self, vtt_path: str, include_timestamps: bool = True) -> str:
        """
        VTT 파일 경로로 직접 파싱 (파일 기반 인터페이스)

        Args:
            vtt_path: .vtt 파일 경로
            include_timestamps: parse_vtt_content 동일
        Returns:
            파싱된 자막 텍스트
        """
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_vtt_content(content, include_timestamps=include_timestamps)


# ── 모듈 레벨 헬퍼 (import해서 쓰는 다른 스크립트용) ──────────────────────
_shared_extractor = None

def parse_vtt(vtt_path_or_content: str, include_timestamps: bool = True,
              is_content: bool = False) -> str:
    """
    전 프로젝트 공용 VTT 파서 (모듈 레벨 함수).

    godofIT_analyze.py, analyze_wsaj_*.py, crawl_recent_videos.py 등
    기존 스크립트들이 이 함수를 import해서 사용.

    Args:
        vtt_path_or_content: 파일 경로 또는 VTT 문자열
        include_timestamps: 타임코드 포함 여부 (기본 True)
        is_content: True이면 문자열 직접 파싱, False이면 파일 경로로 읽음
    Returns:
        파싱된 자막 텍스트
    """
    global _shared_extractor
    if _shared_extractor is None:
        _shared_extractor = SubtitleExtractor.__new__(SubtitleExtractor)
    if is_content:
        return _shared_extractor.parse_vtt_content(vtt_path_or_content, include_timestamps)
    else:
        return _shared_extractor.parse_vtt_file(vtt_path_or_content, include_timestamps)
    
    def extract_subtitle(self, url: str, retries: int = 3) -> Optional[str]:
        """
        자막 추출 (여러 방법 시도)
        
        Args:
            url: 유튜브 영상 URL
            retries: 재시도 횟수
        
        Returns:
            자막 텍스트 또는 None
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            print(f"[ERROR] 유효하지 않은 유튜브 URL: {url}")
            return None
        
        print(f"자막 추출 시작: {video_id}")
        
        for attempt in range(retries):
            try:
                # 방법 1: youtube_transcript_api 시도
                subtitle = self.extract_with_youtube_transcript_api(video_id)
                if subtitle:
                    return subtitle
                
                print(f"youtube_transcript_api 실패, yt-dlp 시도...")
                
                # 방법 2: yt-dlp 시도
                subtitle = self.extract_with_yt_dlp(url)
                if subtitle:
                    return subtitle
                
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"재시도 {attempt + 1}/{retries} ({wait_time}초 후)...")
                    time.sleep(wait_time)
                
            except Exception as e:
                print(f"자막 추출 에러 (시도 {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(5)
        
        print(f"[ERROR] 자막 추출 완전 실패: {video_id}")
        return None
    
    def extract_with_rate_limit(self, videos: list) -> list:
        """
        레이트리밋을 고려한 일괄 자막 추출
        
        Args:
            videos: 영상 정보 리스트
        
        Returns:
            자막이 추가된 영상 정보 리스트
        """
        results = []
        batch_count = 0
        
        for i, video in enumerate(videos):
            print(f"\n진행: {i+1}/{len(videos)} - {video['title'][:50]}...")
            
            # 자막 추출
            subtitle = self.extract_subtitle(video['url'])
            
            video_result = video.copy()
            video_result['subtitle'] = subtitle
            video_result['subtitle_success'] = subtitle is not None
            
            results.append(video_result)
            
            # 성공한 경우만 배치 카운트
            if subtitle:
                batch_count += 1
            
            # 레이트리밋 적용
            if i < len(videos) - 1:  # 마지막이 아닐 때만
                # 일반 요청 간격
                print(f"대기 중... ({self.config.RATE_LIMIT_REQUESTS}초)")
                time.sleep(self.config.RATE_LIMIT_REQUESTS)
                
                # 배치 휴식 (20개마다 5분)
                if batch_count > 0 and batch_count % self.config.RATE_LIMIT_BATCH_SIZE == 0:
                    print(f"배치 휴식: {self.config.RATE_LIMIT_BATCH_BREAK // 60}분...")
                    time.sleep(self.config.RATE_LIMIT_BATCH_BREAK)
        
        # 결과 요약
        success_count = sum(1 for r in results if r['subtitle_success'])
        print(f"\n=== 자막 추출 완료 ===")
        print(f"성공: {success_count}/{len(videos)}개")
        print(f"실패: {len(videos) - success_count}개")
        
        return results