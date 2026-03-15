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
import shutil
import subprocess
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import yt_dlp

# 프로젝트 루트: scripts/ 기준으로 한 단계 위
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# QA 게이트 import (scripts/qa/ 모듈)
# ⚠️ import 실패 시 조용히 스킵하지 않고 즉시 종료 — QA가 없으면 파이프라인 실행 불가
try:
    from qa.gate1_metadata import run_gate1
    from qa.gate2_signals import run_gate2
    from qa.gate3_frontend import run_gate3
    _QA_AVAILABLE = True
except ImportError as _qa_err:
    print(f"[FATAL] QA Gate 모듈 import 실패 — 파이프라인 실행 불가: {_qa_err}")
    print(f"[FATAL] scripts/ 디렉토리에서 실행하세요: python scripts/auto_pipeline.py ...")
    print(f"[FATAL] --skip-qa 옵션을 명시적으로 지정한 경우에만 QA 우회 가능합니다.")
    import sys as _sys
    _sys.exit(1)

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


def _deploy_gh_pages(project_root: str, channel_slug: str) -> Optional[str]:
    """
    orphan 커밋 방식으로 out/ → gh-pages 브랜치에 배포.
    매번 히스토리 없는 깨끗한 커밋 1개만 push → 대용량 파일 히스토리 문제 원천 차단.
    성공 시 None 반환, 실패 시 에러 메시지 반환.
    """
    import tempfile as _tempfile
    import shutil as _sh

    out_path = os.path.join(project_root, 'out')
    if not os.path.isdir(out_path):
        return f"out/ 디렉토리 없음 — 빌드가 먼저 완료되어야 합니다"

    # remote URL 가져오기
    r = subprocess.run(
        ['git', 'remote', 'get-url', 'origin'],
        cwd=project_root, capture_output=True, text=True, timeout=10
    )
    if r.returncode != 0:
        return f"git remote URL 조회 실패: {r.stderr[:200]}"
    remote_url = r.stdout.strip()

    tmp_dir = _tempfile.mkdtemp(prefix='invest-sns-deploy-')
    try:
        # 1) 임시 디렉토리에 새 git repo 초기화 (orphan — 히스토리 없음)
        subprocess.run(['git', 'init'], cwd=tmp_dir, capture_output=True, timeout=10)
        subprocess.run(['git', 'checkout', '--orphan', 'gh-pages'],
                       cwd=tmp_dir, capture_output=True, timeout=10)

        # 2) out/ 내용 복사
        for item in os.listdir(out_path):
            s = os.path.join(out_path, item)
            d = os.path.join(tmp_dir, item)
            if os.path.isdir(s):
                _sh.copytree(s, d)
            else:
                _sh.copy2(s, d)

        # 3) .nojekyll 보장
        nojekyll = os.path.join(tmp_dir, '.nojekyll')
        if not os.path.exists(nojekyll):
            open(nojekyll, 'w').close()

        # 4) git add + commit
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        commit_msg = f'deploy: {channel_slug} 파이프라인 자동배포 ({ts})'

        subprocess.run(['git', 'add', '-A'], cwd=tmp_dir, capture_output=True, timeout=60)

        r = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=tmp_dir, capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            if 'nothing to commit' in (r.stdout + r.stderr):
                print(f"  [INFO] 변경사항 없음 — 재배포 스킵")
                return None
            return f"git commit 실패: {r.stderr[:300]}"

        # 5) remote 추가 + push --force
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url],
                       cwd=tmp_dir, capture_output=True, timeout=10)

        r = subprocess.run(
            ['git', 'push', 'origin', 'gh-pages', '--force'],
            cwd=tmp_dir, capture_output=True, text=True, timeout=180
        )
        if r.returncode != 0:
            return f"git push 실패: {r.stderr[:500]}"

        print(f"  [OK] orphan 배포 완료 (히스토리 없는 깨끗한 커밋)")
        return None  # 성공

    except Exception as _e:
        return str(_e)

    finally:
        # 임시 폴더 정리
        if os.path.isdir(tmp_dir):
            try:
                _sh.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                pass


def _get_signal_count(project_root: str) -> int:
    """Supabase REST API로 influencer_signals 테이블 전체 카운트 조회"""
    try:
        import requests as _requests
        env_path = os.path.join(project_root, '.env.local')
        env_text = open(env_path, encoding='utf-8').read()
        anon_key_m = re.search(r'NEXT_PUBLIC_SUPABASE_ANON_KEY=(.+)', env_text)
        url_m = re.search(r'NEXT_PUBLIC_SUPABASE_URL=(.+)', env_text)
        if not anon_key_m or not url_m:
            return 0
        anon_key = anon_key_m.group(1).strip()
        supabase_url = url_m.group(1).strip()
        r = _requests.get(
            f'{supabase_url}/rest/v1/influencer_signals?select=id',
            headers={
                'apikey': anon_key,
                'Authorization': f'Bearer {anon_key}',
                'Prefer': 'count=exact',
                'Range': '0-0'
            },
            timeout=10
        )
        cr = r.headers.get('content-range', '0/0')
        total = cr.split('/')[-1] if '/' in cr else '0'
        return int(total) if total.isdigit() else 0
    except Exception:
        return 0


class YouTubeChannelCollector:
    """유튜브 채널 영상 수집기"""
    
    def __init__(self):
        self.config = PipelineConfig()
        
        # yt-dlp 설정
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # 메타데이터만 추출
            # playlistend 기본값 없음 → --limit 옵션으로 제어
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
                member_only_skipped = 0

                # ── 멤버십 전용 영상 판단 기준 (Step 2 단계에서 즉시 제외) ──────────
                _MEMBER_ONLY_AVAILABILITY = {'needs_auth', 'subscriber_only', 'premium_only'}
                _MEMBER_ONLY_TITLE_PATTERNS = [
                    '[members', '(members', 'members only', 'members-only',
                    '[멤버십', '(멤버십', '멤버 전용', '[member',
                ]

                def _is_member_only_entry(entry: dict) -> bool:
                    """yt-dlp flat entry가 멤버십 전용인지 판단"""
                    # 1순위: availability 필드
                    avail = str(entry.get('availability') or '').lower()
                    if avail in _MEMBER_ONLY_AVAILABILITY:
                        return True
                    # 2순위: 제목 패턴
                    title_lower = str(entry.get('title') or '').lower()
                    if any(p in title_lower for p in _MEMBER_ONLY_TITLE_PATTERNS):
                        return True
                    # 3순위: channel_is_verified / is_member 등 플래그
                    if entry.get('is_member') or entry.get('membership'):
                        return True
                    return False

                for entry in playlist_info['entries']:
                    if entry is None:
                        continue

                    # ── Step 2 멤버십 필터 ────────────────────────────────────────
                    if _is_member_only_entry(entry):
                        vid_id = entry.get('id', '?')
                        title  = entry.get('title', '')[:40]
                        avail  = entry.get('availability', 'N/A')
                        print(f"  [MEMBER-SKIP] {vid_id} | avail={avail} | {title}")
                        member_only_skipped += 1
                        continue

                    # duration_seconds: yt-dlp는 'duration' 필드에 정수(초)를 줌
                    _dur_raw = entry.get('duration')
                    _dur_secs = int(_dur_raw) if _dur_raw and str(_dur_raw).isdigit() else None

                    video_data = {
                        'title': entry.get('title', 'No Title'),
                        'url': entry.get('url', entry.get('webpage_url', '')),
                        'video_id': entry.get('id', ''),
                        'duration': entry.get('duration_string', entry.get('duration', 'Unknown')),
                        'duration_seconds': _dur_secs,
                        'view_count': entry.get('view_count', 0),
                        'upload_date': entry.get('upload_date', ''),
                        'thumbnail': entry.get('thumbnail', ''),
                        'description': entry.get('description', '')
                    }
                    
                    # URL 정규화
                    if video_data['video_id']:
                        video_data['url'] = f"https://www.youtube.com/watch?v={video_data['video_id']}"
                    
                    videos.append(video_data)

                if member_only_skipped:
                    print(f"  [MEMBER-ONLY] Step2 필터: {member_only_skipped}개 제외됨")
                print(f"[OK] 영상 목록 수집 완료: {len(videos)}개 (멤버십 제외 후)")
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
    
    def _process_single_video(self, video: Dict, channel_url: str, worker_id: int = 0,
                              channel_id: Optional[str] = None) -> Optional[Dict]:
        """단일 영상 자막 추출 + AI 분석 (병렬 워커용)
        
        수정 (2026-03-12): channel_id 파라미터 추가.
        자막 추출 후 DB에서 video_uuid를 먼저 확보한 뒤 AI 분석 진행.
        (코린파파 배치와 동일한 패턴 — video_uuid KeyError 완전 해결)
        """
        import random
        # 워커 간 충돌 방지 초기 딜레이 (0~4초 랜덤)
        if worker_id > 0:
            time.sleep(random.uniform(1.0, worker_id * 2.0))

        title_short = video.get('title', '')[:40]
        video_id = video.get('video_id', '')

        try:
            # Step A: 자막 추출
            from subtitle_extractor import MemberOnlyVideoError
            subtitle = self.extractor.extract_subtitle(video['url'])
            if not subtitle:
                print(f"  [SKIP] 자막 없음: {title_short}")
                return None

            video_with_sub = video.copy()
            video_with_sub['subtitle'] = subtitle
            video_with_sub['subtitle_success'] = True

            # Step A-2: video_uuid DB 확보 (channel_id가 있을 때만)
            # channel_id가 없으면 video_id를 임시 키로 사용 (fallback)
            if channel_id:
                try:
                    video_uuid = self.db_inserter.get_or_create_video(video_with_sub, channel_id)
                    video_with_sub['video_uuid'] = video_uuid
                except Exception as e:
                    print(f"  [ERROR] video UUID 확보 실패 ({title_short}): {e}")
                    return None
            else:
                # channel_id 없는 경우 — 임시 UUID (나중에 insert_analysis_results에서 재처리)
                video_with_sub['video_uuid'] = video_with_sub.get('video_uuid', f'tmp-{video_id}')

            # Step B: AI 분석
            analysis_result = self.analyzer.analyze_video_subtitle(
                channel_url, video_with_sub, subtitle
            )
            if not analysis_result:
                print(f"  [SKIP] 분석 실패: {title_short}")
                return None

            # Step C: 시그널 추출 (다양한 응답 구조 대응 — run_corinpapa_batch 패턴)
            if isinstance(analysis_result, list):
                raw_signals = analysis_result
            elif isinstance(analysis_result, dict):
                raw_signals = (
                    analysis_result.get('signals') or
                    analysis_result.get('signal_list') or
                    analysis_result.get('results') or
                    []
                )
            else:
                raw_signals = []

            # convert_to_database_format은 video_uuid가 있을 때만 호출
            if hasattr(self.analyzer, 'convert_to_database_format') and video_with_sub.get('video_uuid'):
                signals = self.analyzer.convert_to_database_format(
                    analysis_result, video_with_sub['video_uuid']
                )
            else:
                signals = raw_signals

            # Step D: 중복 제거 (V11.5 dedup)
            if hasattr(self.analyzer, 'deduplicate_signals'):
                signals = self.analyzer.deduplicate_signals(signals, video.get('title', ''))

            print(f"  [OK] {title_short}: {len(signals)}개 시그널")
            return {
                'video_id': video_id,
                'video_uuid': video_with_sub['video_uuid'],
                'signals': signals,
                'analysis_result': analysis_result,
                'video_data': video_with_sub,
            }
        except MemberOnlyVideoError as e:
            print(f"  [MEMBER-ONLY] 스킵: {title_short}")
            return {'member_only': True, 'video_id': video_id}

        except Exception as e:
            print(f"  [ERROR] {title_short}: {e}")
            return None

    def run_execute(self, channel_url: str, limit: Optional[int] = None,
                   skip_existing: bool = False, skip_qa: bool = False,
                   batch_size: int = 30) -> Dict[str, Any]:
        """실제 실행 - 전체 파이프라인 수행 (배치 처리)"""
        print("=== EXECUTE 모드 ===")
        print(f"전체 파이프라인을 실행합니다. (배치 크기: {batch_size})")

        # QA 사용 여부 — import 실패 시 이미 exit(1)했으므로 _QA_AVAILABLE=True 보장
        use_qa = not skip_qa
        if skip_qa:
            print("[INFO] QA Gate 건너뜀 (--skip-qa 옵션 명시적 지정)")

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
            print(f"\n[1] 채널 정보 수집...")
            channel_info = self.collector.get_channel_info(channel_url)
            if not channel_info:
                return {'error': '채널 정보 수집 실패'}
            print(f"[OK] 채널: {channel_info['channel_title']} ({channel_info['name']})")

            # ── Step 2: 영상 목록 수집 (전체) ────────────────────────
            print(f"\n[2] 영상 목록 수집...")
            videos = self.collector.get_video_list(channel_url, limit)
            if not videos:
                return {'error': '영상 목록 수집 실패'}

            # ── Step 3: 제목 필터링 [→ QA Gate 1] ────────────────────
            print(f"\n[3] 제목 필터링...")
            passed_videos, skipped_videos = self.filter.filter_videos(videos)
            self.filter.print_filter_results(passed_videos, skipped_videos)

            if not passed_videos:
                return {'error': '투자 관련 영상이 없습니다'}

            if use_qa:
                print(f"\n[QA Gate 1] 메타데이터 검증...")

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

            # ── 배치 분할 처리 ────────────────────────────────────────
            batches = [passed_videos[i:i+batch_size]
                       for i in range(0, len(passed_videos), batch_size)]
            print(f"\n[배치 처리] 총 {len(passed_videos)}개 영상 → {len(batches)}개 배치 (배치 크기: {batch_size})")

            # 전체 누적 통계
            all_db_stats = {'inserted_videos': 0, 'inserted_signals': 0, 'skipped_videos': 0}
            last_analysis_results = None
            backup_filename = None
            successful_videos_total = []

            # ── DB 채널 UUID 사전 확보 (video_uuid 확보에 필요) ──────
            print(f"\n[채널 DB 등록] 채널 UUID 확보 중...")
            try:
                db_channel_id = self.db_inserter.get_or_create_channel(channel_info)
                print(f"[OK] DB 채널 UUID: {db_channel_id}")
            except Exception as _ce:
                print(f"[WARNING] 채널 UUID 확보 실패: {_ce} — video_uuid는 배치 INSERT 시 재처리됩니다")
                db_channel_id = None

            for batch_idx, batch_videos in enumerate(batches):
                print(f"\n{'='*60}")
                print(f"[배치 {batch_idx+1}/{len(batches)}] {len(batch_videos)}개 영상 처리 시작")

                # Supabase 카운트 확인 (배치 전)
                before_count = _get_signal_count(PROJECT_ROOT)
                print(f"  현재 시그널 수: {before_count}개")

                # ── Step 4+5: 자막 추출 + AI 분석 병렬 처리 (동시 3개) ──
                print(f"\n  [Step 4+5] 자막 추출 + AI 분석 병렬 처리 (동시 3개)...")
                from concurrent.futures import ThreadPoolExecutor, as_completed

                parallel_results = []
                failed_count = 0
                member_only_count = 0

                with ThreadPoolExecutor(max_workers=3) as executor:
                    future_map = {
                        executor.submit(
                            self._process_single_video, video, channel_url, idx % 3, db_channel_id
                        ): video
                        for idx, video in enumerate(batch_videos)
                    }
                    for future in as_completed(future_map):
                        result = future.result()
                        if result and result.get('member_only'):
                            member_only_count += 1
                        elif result:
                            parallel_results.append(result)
                        else:
                            failed_count += 1

                if not parallel_results:
                    print(f"  [SKIP] 처리 성공한 영상 없음 → 다음 배치 (멤버십 {member_only_count}개 스킵)")
                    if batch_idx < len(batches) - 1:
                        print(f"  60초 대기...")
                        time.sleep(60)
                    continue

                print(f"  병렬 처리 완료: 성공 {len(parallel_results)}/{len(batch_videos)}개 (실패 {failed_count}개, 멤버십스킵 {member_only_count}개)")

                # successful_videos 리스트 (이후 단계 호환용)
                successful_videos = [r['video_data'] for r in parallel_results]
                successful_videos_total.extend(successful_videos)

                # analysis_results 형식으로 재구성 (QA Gate 2, DB INSERT 호환)
                analysis_results = {
                    'total': len(parallel_results),
                    'success': len(parallel_results),
                    'failed': failed_count,
                    'signals_extracted': sum(len(r['signals']) for r in parallel_results),
                    'results': parallel_results,
                }
                last_analysis_results = analysis_results

                # 배치별 분석 결과 백업
                batch_backup = f"scripts/pipeline_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_batch{batch_idx+1}.json"
                try:
                    import json as _json
                    backup_path = os.path.join(PROJECT_ROOT, batch_backup)
                    with open(backup_path, 'w', encoding='utf-8') as _bf:
                        _json.dump(analysis_results, _bf, ensure_ascii=False, indent=2)
                    print(f"  백업: {batch_backup}")
                except Exception as _be:
                    print(f"  [WARNING] 백업 실패: {_be}")
                if backup_filename is None:
                    backup_filename = batch_backup

                # ── QA Gate 2 (시그널 검증) ───────────────────────────
                if use_qa:
                    print(f"\n  [QA Gate 2] 시그널 검증...")

                    flat_signals = []
                    for res in analysis_results.get('results', []):
                        flat_signals.extend(res.get('signals', []))

                    signals_path = save_tmp_json(
                        flat_signals, f"{channel_slug}_b{batch_idx+1}", 'signals'
                    )
                    print(f"  시그널 저장: {signals_path} ({len(flat_signals)}개)")

                    try:
                        gate2_passed = run_gate2(flat_signals, channel_slug)
                    except Exception as e:
                        print(f"  [ERROR] QA Gate 2 실행 오류: {e}")
                        gate2_passed = False

                    if not gate2_passed:
                        print(f"  [ERROR] QA Gate 2 실패 → 배치 {batch_idx+1} DB INSERT 차단")
                        qa_results['gate2'] = False
                        if batch_idx < len(batches) - 1:
                            print(f"  60초 대기...")
                            time.sleep(60)
                        continue

                    qa_results['gate2'] = True
                    print(f"  [OK] QA Gate 2 통과")

                # ── Step 7: DB INSERT ────────────────────────────────
                print(f"\n  [Step 7] DB INSERT...")
                batch_db_stats = self.db_inserter.insert_analysis_results(
                    channel_info, analysis_results, skip_existing
                )

                # 통계 누적
                for key in ['inserted_videos', 'inserted_signals', 'skipped_videos']:
                    all_db_stats[key] = all_db_stats.get(key, 0) + batch_db_stats.get(key, 0)

                # Supabase 카운트 확인 (배치 후)
                after_count = _get_signal_count(PROJECT_ROOT)
                batch_inserted = after_count - before_count
                print(f"  [배치 {batch_idx+1} 완료] INSERT: {batch_inserted}개 ({before_count} → {after_count})")

                # 배치 사이 대기 (마지막 배치 제외)
                if batch_idx < len(batches) - 1:
                    print(f"\n  [대기] 레이트리밋 방지 60초 대기 중...")
                    time.sleep(60)

            print(f"\n{'='*60}")
            print(f"[배치 처리 완료] 총 {all_db_stats.get('inserted_videos', 0)}개 영상, "
                  f"{all_db_stats.get('inserted_signals', 0)}개 시그널 INSERT")

            db_stats = all_db_stats

            # ── Step 7.5: 수익률 자동 계산 (DB 직접) ─────────────
            print(f"\n[Step 7.5] 수익률 자동 계산 (yfinance → DB)...")
            try:
                returns_result = self.db_inserter.calculate_returns_for_signals()
                print(f"  수익률 계산: {returns_result.get('updated', 0)}개 업데이트, "
                      f"{returns_result.get('skipped', 0)}개 스킵")
            except Exception as _ret_err:
                print(f"  [WARNING] 수익률 계산 오류 (건너뜀): {_ret_err}")

            # signal_prices.json 업데이트 준비 (레거시 호환)
            price_update_stocks = self.db_inserter.update_signal_prices_json()

            # ── Step 8: 새 종목 가격 데이터 수집 ────────────────────
            print(f"\n[Step 8] 새 종목 가격 데이터 수집...")
            rebuild_needed = False
            try:
                import sys as _sys
                import os as _os
                _scripts_dir = _os.path.dirname(_os.path.abspath(__file__))
                if _scripts_dir not in _sys.path:
                    _sys.path.insert(0, _scripts_dir)
                from new_stock_handler import NewStockHandler
                _handler = NewStockHandler()
                if last_analysis_results:
                    stock_result = _handler.process_new_stocks(last_analysis_results)
                    if stock_result['new_stocks']:
                        print(f"  새 종목 {len(stock_result['new_stocks'])}개 감지")
                        print(f"  가격 수집 완료: {stock_result['prices_added']}개")
                        if stock_result.get('rebuild_needed'):
                            print(f"  stock_tickers.json 업데이트됨 → 재빌드 필요")
                            rebuild_needed = True
                    else:
                        print("  새 종목 없음 (기존 가격 데이터 모두 존재)")
            except Exception as _e:
                print(f"  [WARNING] 새 종목 처리 오류 (건너뜀): {_e}")

            # ── Step 8.3: 기존 종목 차트 가격 갱신 ─────────────────
            print(f"\n[Step 8.3] 기존 종목 차트 가격 갱신 (stockPrices.json)...")
            try:
                import yfinance as _yf
                import time as _time2
                _sp_path = os.path.join(PROJECT_ROOT, 'data', 'stockPrices.json')
                with open(_sp_path, 'r', encoding='utf-8') as _f:
                    _sp = json.load(_f)
                
                _updated = 0
                _CRYPTO = {'BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'LINK', 'KLAY', 'XLM',
                           'ORBS', 'WLD', 'PENGU', 'UNI', 'ARB', 'USDC', 'USDT'}
                _INDEX_MAP = {'IXIC': '^IXIC', 'KS11': '^KS11', 'GSPC': '^GSPC'}
                
                for _ticker, _data in _sp.items():
                    if not _data.get('prices'):
                        continue
                    # 마지막 날짜가 2일 이상 지났으면 갱신
                    _last_date = _data['prices'][-1].get('date', '')
                    if not _last_date:
                        continue
                    from datetime import datetime as _dt
                    try:
                        _days_old = (_dt.now() - _dt.strptime(_last_date, '%Y-%m-%d')).days
                    except Exception:
                        continue
                    if _days_old < 2:
                        continue
                    
                    # yfinance ticker 변환
                    if _ticker.upper() in _CRYPTO:
                        _yf_sym = f"{_ticker.upper()}-USD"
                    elif _ticker.upper() in _INDEX_MAP:
                        _yf_sym = _INDEX_MAP[_ticker.upper()]
                    elif _ticker.isdigit() and len(_ticker) == 6:
                        _yf_sym = f"{_ticker}.KS"
                    elif _ticker.isdigit() and len(_ticker) == 4:
                        _yf_sym = f"{_ticker.zfill(4)}.HK"
                    else:
                        _yf_sym = _ticker
                    
                    try:
                        _hist = _yf.Ticker(_yf_sym).history(start=_last_date)
                        if _hist.empty:
                            continue
                        _hist = _hist.dropna(subset=['Close'])
                        if _hist.empty:
                            continue
                        
                        # 새 데이터 추가 (기존 마지막 날짜 이후)
                        _existing_dates = {p['date'] for p in _data['prices']}
                        _new_count = 0
                        for _date, _row in _hist.iterrows():
                            _d = _date.strftime('%Y-%m-%d')
                            if _d not in _existing_dates:
                                import math as _math
                                _close = float(_row['Close'])
                                if _math.isnan(_close) or _math.isinf(_close):
                                    continue
                                _data['prices'].append({
                                    'date': _d,
                                    'close': round(_close, 2),
                                    'volume': int(_row['Volume']) if not _math.isnan(_row['Volume']) else 0
                                })
                                _new_count += 1
                        
                        if _new_count > 0:
                            _data['prices'].sort(key=lambda p: p['date'])
                            _data['currentPrice'] = _data['prices'][-1]['close']
                            if len(_data['prices']) >= 2:
                                _prev = _data['prices'][-2]['close']
                                _curr = _data['prices'][-1]['close']
                                _data['change'] = round(_curr - _prev, 2)
                                _data['changePercent'] = round((_curr - _prev) / _prev * 100, 2) if _prev else 0
                            _updated += 1
                        
                        _time2.sleep(0.2)
                    except Exception:
                        continue
                
                if _updated > 0:
                    with open(_sp_path, 'w', encoding='utf-8') as _f:
                        json.dump(_sp, _f, ensure_ascii=False)
                    print(f"  {_updated}개 종목 차트 갱신 완료")
                else:
                    print(f"  갱신 필요 종목 없음 (모두 최신)")
            except Exception as _e:
                print(f"  [WARNING] 차트 갱신 오류 (건너뜀): {_e}")

            # ── Step 8.5: data/ → public/ 동기화 ─────────────────────
            print(f"\n[Step 8.5] data/ → public/ 동기화...")
            import shutil as _shutil
            _prices_src = os.path.join(PROJECT_ROOT, 'data', 'signal_prices.json')
            _prices_dst = os.path.join(PROJECT_ROOT, 'public', 'signal_prices.json')
            if os.path.exists(_prices_src):
                _shutil.copy2(_prices_src, _prices_dst)
                print(f"  signal_prices.json 동기화 완료")
            _sp_src = os.path.join(PROJECT_ROOT, 'data', 'stockPrices.json')
            _sp_dst = os.path.join(PROJECT_ROOT, 'public', 'stockPrices.json')
            if os.path.exists(_sp_src):
                _shutil.copy2(_sp_src, _sp_dst)
                print(f"  stockPrices.json 동기화 완료")

            # ── Step 8.6: speaker_slugs.json 갱신 ──────────────────────
            print(f"\n[Step 8.6] speaker_slugs.json 갱신...")
            try:
                slug_script = os.path.join(PROJECT_ROOT, 'scripts', 'generate_speaker_slugs.js')
                slug_result = subprocess.run(
                    ['node', slug_script],
                    cwd=PROJECT_ROOT,
                    capture_output=True, text=True, timeout=30,
                    encoding='utf-8', errors='replace'
                )
                if slug_result.returncode == 0:
                    print(slug_result.stdout.strip())
                else:
                    print(f"[WARNING] speaker_slugs.js 실패: {slug_result.stderr[:200]}")
            except Exception as e:
                print(f"[WARNING] speaker_slugs.js 실행 불가: {e}")

            # ── Step 9: npm run build ─────────────────────────────────
            print(f"\n[Step 9] 프론트엔드 빌드 (npm run build)...")
            build_result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=PROJECT_ROOT,
                capture_output=True, text=True, timeout=300,
                encoding='utf-8', errors='replace'
            )
            if build_result.returncode != 0:
                print(f"[ERROR] 빌드 실패:\n{build_result.stderr[-500:]}")
                return {'error': 'npm run build 실패', 'qa_results': qa_results,
                        'db_stats': db_stats}
            # 빌드된 페이지 수 출력
            out_dir = os.path.join(PROJECT_ROOT, 'out')
            html_count = sum(1 for _ in Path(out_dir).rglob('*.html')) if os.path.isdir(out_dir) else 0
            print(f"[OK] 빌드 완료 (HTML {html_count}개)")

            # ── QA Gate 3 (빌드 결과 검증) ────────────────────────────
            if use_qa:
                print(f"\n[QA Gate 3] 프론트엔드 검증...")
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
                    print("[ERROR] QA Gate 3 실패 → 배포 차단 (DB INSERT는 완료됨)")
                    return {
                        'error': 'QA Gate 3 실패 - 배포 차단',
                        'db_stats': db_stats,
                        'qa_results': qa_results,
                    }
                print("[OK] QA Gate 3 통과")

            # ── 배포 (git worktree → gh-pages push) ──────────────────
            print(f"\n[배포] GitHub Pages...")
            deploy_error = _deploy_gh_pages(PROJECT_ROOT, channel_slug)
            if deploy_error:
                print(f"⛔ 배포 실패: {deploy_error}")
                return {
                    'error': f'배포 실패: {deploy_error}',
                    'db_stats': db_stats,
                    'qa_results': qa_results,
                }
            print("[OK] GitHub Pages 배포 완료 → https://puing5555.github.io/invest-sns/")

            # ── 실행 완료 요약 ────────────────────────────────────────
            end_time = time.time()
            execution_time = end_time - start_time

            result = {
                'channel_info': channel_info,
                'channel_slug': channel_slug,
                'execution_time_minutes': execution_time // 60,
                'total_videos': len(videos),
                'passed_videos': len(passed_videos),
                'successful_subtitles': len(successful_videos_total),
                'db_stats': db_stats,
                'price_update_stocks_count': len(price_update_stocks),
                'backup_file': backup_filename,
                'qa_results': qa_results,
            }

            print(f"\n=== 파이프라인 완료 ===")
            print(f"총 실행 시간: {execution_time // 60:.1f}분")
            print(f"처리 영상: {db_stats.get('inserted_videos', '?')}개")
            print(f"생성 시그널: {db_stats.get('inserted_signals', '?')}개")
            print(f"백업 파일: {backup_filename}")
            g1 = 'OK' if qa_results['gate1'] else ('SKIP' if qa_results['gate1'] is None else 'FAIL')
            g2 = 'OK' if qa_results['gate2'] else ('SKIP' if qa_results['gate2'] is None else 'FAIL')
            g3 = 'OK' if qa_results['gate3'] else ('SKIP' if qa_results['gate3'] is None else 'FAIL')
            print(f"QA: Gate1(메타)={g1}  Gate2(시그널)={g2}  Gate3(프론트)={g3}")
            print(f"빌드+배포: {'완료' if qa_results['gate3'] or not use_qa else '차단'}")

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
    parser.add_argument('--batch-size', type=int, default=30,
                       help='배치당 처리할 영상 수 (기본값: 30)')
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
                skip_qa=args.skip_qa,
                batch_size=args.batch_size
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
