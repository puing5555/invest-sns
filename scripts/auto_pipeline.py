#!/usr/bin/env python3
# auto_pipeline.py - 대량 자막 수집 자동화 파이프라인
"""
투자 유튜버 채널 자동 분석 파이프라인

사용법:
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --dry-run
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute --limit 10
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute --skip-existing
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute --skip-qa

기능:
1. yt-dlp로 채널 영상 목록 수집
2. 제목 필터링 (투자 관련 영상만 선별)
3. QA Gate 1 - 메타데이터 검증
4. Webshare 프록시로 자막 추출
5. Anthropic Claude로 시그널 분석 (V10 프롬프트)
6. QA Gate 2 - 시그널 검증
7. Supabase DB에 INSERT + QA Gate 3 (프론트엔드 검증)
"""

import os
import sys
import argparse
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import yt_dlp

# 프로젝트 루트: scripts/ 기준으로 한 단계 위
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# QA 게이트 import (scripts/qa/ 모듈)
_QA_AVAILABLE = False
try:
    from qa.gate1_metadata import run_gate1
    from qa.gate2_signals import run_gate2
    from qa.gate3_frontend import run_gate3
    _QA_AVAILABLE = True
except ImportError as _qa_err:
    print(f"[WARNING] QA Gate 모듈 import 실패 (--skip-qa 강제 적용): {_qa_err}")

# 모듈 import
from title_filter import TitleFilter
from subtitle_extractor import SubtitleExtractor
from signal_analyzer_rest import SignalAnalyzer
from db_inserter_rest import DatabaseInserter
from pipeline_config import PipelineConfig


# ────────────────────────────────────────
# 유틸
# ────────────────────────────────────────

def get_channel_slug(channel_url: str) -> str:
    """채널 URL에서 슬러그 추출
    https://www.youtube.com/@sesang101 → sesang101
    """
    m = re.search(r'@([^/?#]+)', channel_url)
    if m:
        return m.group(1).lower()
    m = re.search(r'/c/([^/?#]+)', channel_url)
    if m:
        return m.group(1).lower()
    m = re.search(r'/channel/([^/?#]+)', channel_url)
    if m:
        return m.group(1).lower()
    # 최후 수단: URL 마지막 경로 세그먼트
    return channel_url.rstrip('/').split('/')[-1].lower() or 'unknown'


def normalize_videos_for_gate(videos: List[Dict], channel_name: str = '') -> List[Dict]:
    """yt-dlp 영상 데이터를 gate1 형식으로 정규화
    upload_date (YYYYMMDD) → published_at (YYYY-MM-DD)
    """
    normalized = []
    for v in videos:
        nv = dict(v)
        # upload_date → published_at 변환
        ud = v.get('upload_date', '')
        if ud and len(ud) == 8 and 'published_at' not in v:
            nv['published_at'] = f"{ud[:4]}-{ud[4:6]}-{ud[6:]}"
        elif not nv.get('published_at'):
            nv['published_at'] = ''
        # channel_name 추가
        if channel_name and not nv.get('channel_name'):
            nv['channel_name'] = channel_name
        normalized.append(nv)
    return normalized


def save_tmp_json(data: Any, slug: str, suffix: str) -> str:
    """data/tmp/{slug}_{suffix}.json 에 저장 후 경로 반환"""
    tmp_dir = os.path.join(PROJECT_ROOT, 'data', 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    path = os.path.join(tmp_dir, f"{slug}_{suffix}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


class YouTubeChannelCollector:
    """유튜브 채널 영상 수집기"""
    
    def __init__(self):
        self.config = PipelineConfig()
        
        # yt-dlp 설정
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # 메타데이터만 추출
            'playlistend': 50,     # 최대 50개 영상
        }
        
        # 프록시 설정
        proxy_config = self.config.get_proxy_config()
        if proxy_config:
            self.ydl_opts['proxy'] = proxy_config['https']
    
    def get_channel_info(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """채널 기본 정보 수집"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # 채널 정보 추출
                channel_info = ydl.extract_info(channel_url, download=False)
                
                return {
                    'name': channel_info.get('uploader', 'Unknown'),
                    'url': channel_url,
                    'description': channel_info.get('description', ''),
                    'subscriber_count': channel_info.get('subscriber_count', 0),
                    'video_count': channel_info.get('video_count', 0),
                    'channel_id': channel_info.get('channel_id', ''),
                    'channel_title': channel_info.get('title', 'Unknown Channel')
                }
                
        except Exception as e:
            print(f"[ERROR] 채널 정보 수집 실패: {e}")
            return None
    
    def get_video_list(self, channel_url: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """채널의 영상 목록 수집"""
        try:
            # limit 적용
            opts = self.ydl_opts.copy()
            if limit:
                opts['playlistend'] = limit
            
            # 채널 URL에 /videos 추가해서 실제 영상 목록만 가져오기
            videos_url = channel_url
            if not videos_url.endswith('/videos'):
                videos_url = videos_url.rstrip('/') + '/videos'
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                print(f"채널 영상 목록 수집 중: {videos_url}")
                
                # 플레이리스트 추출
                playlist_info = ydl.extract_info(videos_url, download=False)
                
                if 'entries' not in playlist_info:
                    print("[ERROR] 영상 목록을 찾을 수 없습니다")
                    return []
                
                videos = []
                for entry in playlist_info['entries']:
                    if entry is None:
                        continue
                    
                    video_data = {
                        'title': entry.get('title', 'No Title'),
                        'url': entry.get('url', entry.get('webpage_url', '')),
                        'video_id': entry.get('id', ''),
                        'duration': entry.get('duration_string', entry.get('duration', 'Unknown')),
                        'view_count': entry.get('view_count', 0),
                        'upload_date': entry.get('upload_date', ''),
                        'thumbnail': entry.get('thumbnail', ''),
                        'description': entry.get('description', '')
                    }
                    
                    # URL 정규화
                    if video_data['video_id']:
                        video_data['url'] = f"https://www.youtube.com/watch?v={video_data['video_id']}"
                    
                    videos.append(video_data)
                
                print(f"[OK] 영상 목록 수집 완료: {len(videos)}개")
                return videos
                
        except Exception as e:
            print(f"[ERROR] 영상 목록 수집 실패: {e}")
            return []


class AutoPipeline:
    """자동화 파이프라인 메인 클래스"""
    
    def __init__(self):
        self.config = PipelineConfig()
        self.collector = YouTubeChannelCollector()
        self.filter = TitleFilter()
        self.extractor = SubtitleExtractor()
        self.analyzer = SignalAnalyzer()
        self.db_inserter = DatabaseInserter()
    
    def run_dry_run(self, channel_url: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Dry run - 영상 목록과 필터링 결과만 출력"""
        print("=== DRY RUN 모드 ===")
        print("영상 목록 수집과 필터링 결과만 출력합니다. 실제 처리는 하지 않습니다.")
        
        # 1. 채널 정보 수집
        channel_info = self.collector.get_channel_info(channel_url)
        if not channel_info:
            return {'error': '채널 정보 수집 실패'}
        
        print(f"\n=== 채널 정보 ===")
        print(f"채널명: {channel_info['channel_title']}")
        print(f"업로더: {channel_info['name']}")
        print(f"구독자: {channel_info.get('subscriber_count', 'N/A'):,}")
        print(f"총 영상: {channel_info.get('video_count', 'N/A'):,}")
        print(f"URL: {channel_url}")
        
        # 2. 영상 목록 수집
        videos = self.collector.get_video_list(channel_url, limit)
        if not videos:
            return {'error': '영상 목록 수집 실패'}
        
        # 3. 제목 필터링
        passed_videos, skipped_videos = self.filter.filter_videos(videos)
        
        # 4. 필터링 결과 출력
        self.filter.print_filter_results(passed_videos, skipped_videos)
        
        # 5. 예상 처리 시간 계산
        subtitle_time = len(passed_videos) * (self.config.RATE_LIMIT_REQUESTS + 10)  # 자막 추출
        analysis_time = len(passed_videos) * (self.config.RATE_LIMIT_API_REQUESTS + 20)  # AI 분석
        total_time_minutes = (subtitle_time + analysis_time) // 60
        
        print(f"\n=== 예상 처리 시간 ===")
        print(f"자막 추출: 약 {subtitle_time // 60}분")
        print(f"AI 분석: 약 {analysis_time // 60}분")
        print(f"총 예상 시간: 약 {total_time_minutes}분")
        
        return {
            'channel_info': channel_info,
            'total_videos': len(videos),
            'passed_videos': len(passed_videos),
            'skipped_videos': len(skipped_videos),
            'estimated_time_minutes': total_time_minutes,
            'sample_passed': passed_videos[:5],  # 샘플 5개
            'sample_skipped': skipped_videos[:5]   # 샘플 5개
        }
    
    def run_execute(self, channel_url: str, limit: Optional[int] = None,
                   skip_existing: bool = False, skip_qa: bool = False) -> Dict[str, Any]:
        """실제 실행 - 전체 7단계 파이프라인 수행"""
        print("=== EXECUTE 모드 ===")
        print("전체 파이프라인을 실행합니다.")

        # QA 사용 가능 여부
        use_qa = _QA_AVAILABLE and not skip_qa
        if skip_qa:
            print("[INFO] QA Gate 건너뜀 (--skip-qa 옵션)")
        elif not _QA_AVAILABLE:
            print("[WARNING] QA Gate 모듈 없음 - QA 건너뜀")

        total_steps = 7 if use_qa else 6
        start_time = time.time()

        # 채널 슬러그 추출 (QA용 식별자)
        channel_slug = get_channel_slug(channel_url)

        # QA 결과 추적
        qa_results = {
            'gate1': None,
            'gate2': None,
            'gate3': None,
        }

        try:
            # ── Step 1: 채널 정보 수집 ─────────────────────────────────
            print(f"\n[1/{total_steps}] 채널 정보 수집...")
            channel_info = self.collector.get_channel_info(channel_url)
            if not channel_info:
                return {'error': '채널 정보 수집 실패'}
            print(f"[OK] 채널: {channel_info['channel_title']} ({channel_info['name']})")

            # ── Step 2: 영상 목록 수집 ────────────────────────────────
            print(f"\n[2/{total_steps}] 영상 목록 수집...")
            videos = self.collector.get_video_list(channel_url, limit)
            if not videos:
                return {'error': '영상 목록 수집 실패'}

            # ── Step 3: 제목 필터링 [→ QA Gate 1] ────────────────────
            print(f"\n[3/{total_steps}] 제목 필터링...")
            passed_videos, skipped_videos = self.filter.filter_videos(videos)
            self.filter.print_filter_results(passed_videos, skipped_videos)

            if not passed_videos:
                return {'error': '투자 관련 영상이 없습니다'}

            if use_qa:
                print(f"\n[3/{total_steps}] QA Gate 1: 메타데이터 검증...")

                # 메타데이터 정규화 및 임시 저장
                normalized_videos = normalize_videos_for_gate(
                    passed_videos, channel_info.get('channel_title', channel_slug)
                )
                meta_path = save_tmp_json(normalized_videos, channel_slug, 'metadata')
                print(f"[INFO] 메타데이터 저장: {meta_path}")

                try:
                    gate1_passed, gate1_filtered = run_gate1(
                        normalized_videos,
                        channel_slug,
                        len(videos)  # total_original
                    )
                except Exception as e:
                    print(f"[ERROR] QA Gate 1 실행 오류: {e}")
                    gate1_passed, gate1_filtered = False, passed_videos

                qa_results['gate1'] = gate1_passed

                if not gate1_passed:
                    print("[ERROR] QA Gate 1 실패 → 파이프라인 중단")
                    return {'error': 'QA Gate 1 실패', 'qa_results': qa_results}

                print(f"[OK] QA Gate 1 통과 → 검증된 영상: {len(gate1_filtered)}개")
                passed_videos = gate1_filtered  # gate1이 걸러낸 결과 사용

            # ── Step 4: 자막 추출 ────────────────────────────────────
            print(f"\n[4/{total_steps}] 자막 추출...")
            videos_with_subtitles = self.extractor.extract_with_rate_limit(passed_videos)

            # 자막 추출 성공한 것만 필터링
            successful_videos = [v for v in videos_with_subtitles if v.get('subtitle')]
            if not successful_videos:
                return {'error': '자막 추출에 성공한 영상이 없습니다'}

            # ── Step 5: AI 시그널 분석 ───────────────────────────────
            print(f"\n[5/{total_steps}] AI 시그널 분석...")
            analysis_results = self.analyzer.analyze_videos_batch(channel_url, successful_videos)

            # 분석 결과 저장 (중간 백업)
            backup_filename = f"scripts/pipeline_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.analyzer.save_analysis_results(analysis_results, backup_filename)

            # ── Step 6: QA Gate 2 (시그널 검증) ─────────────────────
            if use_qa:
                print(f"\n[6/{total_steps}] QA Gate 2: 시그널 검증...")

                # 시그널 평탄화 (모든 result에서 signals 추출)
                flat_signals = []
                for res in analysis_results.get('results', []):
                    flat_signals.extend(res.get('signals', []))

                # 시그널 임시 저장
                signals_path = save_tmp_json(flat_signals, channel_slug, 'signals')
                print(f"[INFO] 시그널 저장: {signals_path} ({len(flat_signals)}개)")

                try:
                    gate2_passed = run_gate2(flat_signals, channel_slug)
                except Exception as e:
                    print(f"[ERROR] QA Gate 2 실행 오류: {e}")
                    gate2_passed = False

                qa_results['gate2'] = gate2_passed

                if not gate2_passed:
                    print("[ERROR] QA Gate 2 실패 → DB INSERT 차단")
                    return {'error': 'QA Gate 2 실패', 'qa_results': qa_results}

                print("[OK] QA Gate 2 통과 → DB INSERT 진행")

            # ── Step 7: DB INSERT [→ QA Gate 3] ─────────────────────
            db_step = 7 if use_qa else 6
            print(f"\n[{db_step}/{total_steps}] DB INSERT...")
            db_stats = self.db_inserter.insert_analysis_results(
                channel_info, analysis_results, skip_existing
            )

            # signal_prices.json 업데이트 준비
            price_update_stocks = self.db_inserter.update_signal_prices_json()

            # QA Gate 3: 프론트엔드 검증
            if use_qa:
                print(f"\n[{db_step}/{total_steps}] QA Gate 3: 프론트엔드 검증...")
                try:
                    gate3_passed = run_gate3(
                        slug=channel_slug,
                        project_root=PROJECT_ROOT,
                        check_deploy=False
                    )
                except Exception as e:
                    print(f"[ERROR] QA Gate 3 실행 오류: {e}")
                    gate3_passed = False

                qa_results['gate3'] = gate3_passed

                if not gate3_passed:
                    print("[WARNING] QA Gate 3 실패 → 배포 차단 (DB INSERT는 완료)")
                else:
                    print("[OK] QA Gate 3 통과 → 배포 준비 완료")

            # ── 실행 완료 요약 ────────────────────────────────────────
            end_time = time.time()
            execution_time = end_time - start_time

            result = {
                'channel_info': channel_info,
                'channel_slug': channel_slug,
                'execution_time_minutes': execution_time // 60,
                'total_videos': len(videos),
                'passed_videos': len(passed_videos),
                'successful_subtitles': len(successful_videos),
                'db_stats': db_stats,
                'price_update_stocks_count': len(price_update_stocks),
                'backup_file': backup_filename,
                'qa_results': qa_results,
            }

            print(f"\n=== 파이프라인 완료 ({total_steps}단계) ===")
            print(f"총 실행 시간: {execution_time // 60:.1f}분")
            print(f"처리 영상: {db_stats['inserted_videos']}개")
            print(f"생성 시그널: {db_stats['inserted_signals']}개")
            print(f"백업 파일: {backup_filename}")
            if use_qa:
                g1 = '✅' if qa_results['gate1'] else '❌'
                g2 = '✅' if qa_results['gate2'] else '❌'
                g3 = '✅' if qa_results['gate3'] else '❌' if qa_results['gate3'] is not None else '⏭'
                print(f"QA Gate 1(메타): {g1}  Gate 2(시그널): {g2}  Gate 3(프론트): {g3}")

            return result

        except Exception as e:
            print(f"[ERROR] 파이프라인 실행 중 에러: {e}")
            return {'error': str(e)}


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='투자 유튜버 채널 자동 분석 파이프라인 (7단계 QA Gate 통합)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # Dry run - 영상 목록과 필터링 결과만 확인
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --dry-run

  # 실제 실행 - 전체 파이프라인 수행 (QA Gate 포함)
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute

  # 최대 10개 영상만 처리
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute --limit 10

  # DB에 이미 있는 영상 건너뛰기
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute --skip-existing

  # QA Gate 건너뛰기 (긴급 시)
  python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute --skip-qa
        """
    )
    
    # 필수 인자
    parser.add_argument('--channel', required=True,
                       help='유튜브 채널 URL (예: https://www.youtube.com/@sesang101)')
    
    # 모드 선택 (배타적)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--dry-run', action='store_true',
                           help='영상 목록과 필터링 결과만 출력 (실행 안 함)')
    mode_group.add_argument('--execute', action='store_true',
                           help='실제 파이프라인 실행')
    
    # 옵션 인자
    parser.add_argument('--limit', type=int, default=None,
                       help='최대 처리할 영상 수 (기본값: 제한 없음)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='DB에 이미 있는 영상 건너뛰기')
    parser.add_argument('--skip-qa', action='store_true',
                       help='QA Gate 검증 건너뛰기 (긴급 시 사용, 기본값: 실행)')
    parser.add_argument('--prompt-version', default='V10',
                       help='사용할 프롬프트 버전 (기본값: V10)')
    
    args = parser.parse_args()
    
    # 인자 검증
    if not args.channel.startswith('https://www.youtube.com/'):
        print("[ERROR] 올바른 유튜브 채널 URL을 입력해주세요")
        print("예시: https://www.youtube.com/@sesang101")
        return 1
    
    if args.limit and args.limit <= 0:
        print("[ERROR] limit은 1 이상의 정수여야 합니다")
        return 1
    
    # 파이프라인 실행
    pipeline = AutoPipeline()
    
    try:
        if args.dry_run:
            result = pipeline.run_dry_run(args.channel, args.limit)
        else:
            result = pipeline.run_execute(
                args.channel, args.limit, args.skip_existing,
                skip_qa=args.skip_qa
            )
        
        # 결과 확인
        if 'error' in result:
            print(f"[ERROR] 실행 실패: {result['error']}")
            return 1
        
        # 성공
        print("[SUCCESS] 파이프라인 완료!")
        return 0
        
    except KeyboardInterrupt:
        print("\n[ERROR] 사용자에 의해 중단됨")
        return 1
    except Exception as e:
        print(f"[ERROR] 예상치 못한 에러: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
