#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# gemini_pipeline.py - Gemini 2.0 Flash 기반 투자 시그널 파이프라인
"""
yt-dlp 자막 추출 없이 Gemini 2.0 Flash로 YouTube URL 직접 분석.

사용법:
  # 안유화 채널 테스트 (10개)
  python scripts/gemini_pipeline.py --channel https://www.youtube.com/@anyuhuatv --limit 10

  # 실제 실행 (전체)
  python scripts/gemini_pipeline.py --channel https://www.youtube.com/@anyuhuatv --execute

  # dry-run (DB INSERT 없이 분석만)
  python scripts/gemini_pipeline.py --channel https://www.youtube.com/@anyuhuatv --dry-run --limit 10

변경사항:
  - yt-dlp 자막 추출 제거
  - Gemini 2.0 Flash API로 YouTube URL 직접 분석
  - V12 프롬프트 Gemini 최적화
  - 시그널: 매수/긍정/중립/부정/매도 (슬래시 복수표기 자동 정규화)
  - 타임스탬프 Gemini가 직접 추출
  - GEMINI_API_KEY 환경변수 관리
"""

import os
import sys
import json
import time
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import yt_dlp

# 프로젝트 루트
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env.local'), override=True)

from gemini_analyzer import analyze_video_with_gemini, GEMINI_API_KEY
from db_inserter_rest import DatabaseInserter
from pipeline_config import PipelineConfig
from title_filter import TitleFilter

GEMINI_REQUEST_DELAY = 5  # 요청 간 딜레이 (초)
BATCH_SIZE = 10
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')


def log(msg: str, logfile=None):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode('utf-8', errors='replace').decode('ascii', errors='replace'))
    if logfile:
        logfile.write(line + '\n')
        logfile.flush()


def get_video_list(channel_url: str, limit: Optional[int] = None) -> List[Dict]:
    """yt-dlp flat-playlist로 영상 목록만 수집 (자막 추출 없음)
    limit은 멤버십 제외 후 최종 개수 기준으로 적용
    """
    print(f"\n[Step 1] 영상 목록 수집: {channel_url}")
    # /videos 탭으로 접근해야 실제 영상 목록을 가져올 수 있음
    fetch_url = channel_url.rstrip('/')
    if not fetch_url.endswith('/videos'):
        fetch_url = fetch_url + '/videos'
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'ignoreerrors': True,
        'skip_download': True,
    }
    videos = []
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(fetch_url, download=False)
            if not info:
                return []
            entries = info.get('entries', [])
            for e in entries:
                if not e:
                    continue
                vid_id = e.get('id', '')
                if not vid_id:
                    continue

                # 멤버십/구독자 전용 영상 즉시 제외 (AGENTS.md 규칙)
                avail = e.get('availability', '')
                if avail in ('subscriber_only', 'needs_auth', 'premium_only'):
                    continue
                title = e.get('title', '')
                if any(kw in title for kw in ['멤버십', '멤버쉽', '유료회원', '구독자전용']):
                    continue

                videos.append({
                    'video_id': vid_id,
                    'title': title,
                    'url': f"https://www.youtube.com/watch?v={vid_id}",
                    'upload_date': e.get('upload_date', ''),
                    'duration': e.get('duration', 0),
                    'duration_seconds': e.get('duration', 0),
                    'view_count': e.get('view_count', 0),
                    'channel_url': channel_url,
                })
        except Exception as e:
            print(f"[ERROR] 영상 목록 수집 실패: {e}")
    print(f"  → {len(videos)}개 영상 수집 (멤버십 제외 후)")
    # limit은 여기서 적용 (멤버십 제외 후 기준)
    if limit:
        videos = videos[:limit * 3]  # 필터 감안해 여유있게 가져옴
    return videos


def filter_videos(videos: List[Dict], skip_existing_ids: set = None) -> List[Dict]:
    """멤버십 영상 제외 + 기존 처리 영상 제외
    Gemini 파이프라인은 제목 필터 우회 - Gemini가 직접 투자 관련성 판단하고 빈 시그널 반환
    """
    skip_existing_ids = skip_existing_ids or set()
    # 멤버십 키워드만 명시적으로 제거
    membership_keywords = ['멤버십', '멤버쉽', 'members only', '유료회원', '구독자전용', '[member', '[members']
    filtered = []
    skipped_member = 0
    skipped_existing = 0
    for v in videos:
        if v['video_id'] in skip_existing_ids:
            skipped_existing += 1
            continue
        title_lower = v.get('title', '').lower()
        if any(kw in title_lower for kw in membership_keywords):
            skipped_member += 1
            continue
        filtered.append(v)
    print(f"[Step 2] 필터링 후: {len(filtered)}개 (멤버십제외={skipped_member}, 기존스킵={skipped_existing}, 전체={len(videos)}개)")
    return filtered


def get_existing_video_ids(channel_id: str, db: DatabaseInserter) -> set:
    """DB에 이미 존재하는 video_id 세트 반환"""
    try:
        import requests as req
        config = PipelineConfig()
        resp = req.get(
            f"{config.SUPABASE_URL}/rest/v1/influencer_videos",
            headers={
                'apikey': config.SUPABASE_SERVICE_KEY,
                'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}',
                'Prefer': 'count=exact'
            },
            params={'channel_id': f'eq.{channel_id}', 'select': 'video_id', 'limit': '2000'},
            timeout=15
        )
        if resp.ok:
            return {r['video_id'] for r in resp.json()}
    except Exception as e:
        print(f"[WARN] 기존 영상 ID 조회 실패: {e}")
    return set()


def get_channel_info(channel_url: str) -> Dict:
    """채널 메타데이터 수집"""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': 1,
        'ignoreerrors': True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            if info:
                return {
                    'url': channel_url,
                    'channel_url': channel_url,
                    'name': info.get('channel', info.get('uploader', 'Unknown')),
                    'channel_title': info.get('channel', info.get('uploader', 'Unknown')),
                    'subscriber_count': info.get('channel_follower_count', 0) or 0,
                    'description': info.get('description', ''),
                }
    except Exception as e:
        print(f"[WARN] 채널 정보 수집 실패: {e}")
    return {'url': channel_url, 'channel_url': channel_url, 'name': 'Unknown', 'channel_title': 'Unknown'}


def run_pipeline(
    channel_url: str,
    limit: Optional[int] = None,
    offset: int = 0,
    dry_run: bool = False,
    skip_existing: bool = True,
):
    """메인 파이프라인 실행"""
    import traceback as _tb
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(LOG_DIR, f'gemini_pipeline_{timestamp}.log')

    try:
      with open(log_path, 'w', encoding='utf-8') as logfile:
        log(f"=== Gemini 파이프라인 시작 ===", logfile)
        log(f"채널: {channel_url}", logfile)
        log(f"limit={limit} | offset={offset} | dry_run={dry_run} | skip_existing={skip_existing}", logfile)

        # API 키 확인
        if not GEMINI_API_KEY:
            log("[FATAL] GEMINI_API_KEY 없음 - .env.local에 GEMINI_API_KEY=... 추가하세요", logfile)
            return

        # DB 초기화
        db = DatabaseInserter()

        # Step 1: 채널 정보 + 채널 DB 등록
        log("\n[Step 1] 채널 정보 수집...", logfile)
        channel_info = get_channel_info(channel_url)
        log(f"  채널명: {channel_info.get('channel_title', 'Unknown')}", logfile)

        channel_id = None
        if not dry_run:
            try:
                channel_id = db.get_or_create_channel(channel_info)
                log(f"  채널 UUID: {channel_id}", logfile)
            except Exception as e:
                log(f"[ERROR] 채널 등록 실패: {e}", logfile)
                return

        # Step 2: 영상 목록 수집
        videos = get_video_list(channel_url, limit=limit)
        if not videos:
            log("[ERROR] 영상 없음", logfile)
            return

        # Step 3: 기존 영상 제외 + 제목 필터
        existing_ids = set()
        if skip_existing and channel_id:
            existing_ids = get_existing_video_ids(channel_id, db)
            log(f"  기존 DB 영상: {len(existing_ids)}개 (스킵)", logfile)

        filtered = filter_videos(videos, skip_existing_ids=existing_ids)
        # offset + limit 적용 (필터 후 기준)
        if offset:
            filtered = filtered[offset:]
        if limit and len(filtered) > limit:
            filtered = filtered[:limit]
        if not filtered:
            log("[INFO] 처리할 새 영상 없음", logfile)
            return

        # Step 4-7: Gemini 분석 + DB INSERT
        total_analyzed = 0
        total_inserted = 0
        total_signals = 0
        results = []

        log(f"\n[Step 4-7] Gemini 분석 시작 ({len(filtered)}개 영상)...", logfile)
        for i, video in enumerate(filtered, 1):
            try:
                vid_id = video['video_id']
                title = video.get('title', '')
                log(f"\n  [{i}/{len(filtered)}] {vid_id} | {title[:50]}", logfile)

                # 60분(3600초) 초과 영상 스킵
                dur = video.get('duration_seconds') or video.get('duration') or 0
                try:
                    dur = int(dur)
                except Exception:
                    dur = 0
                if dur > 3600:
                    log(f"  [SKIP] 영상 길이 {dur//60}분 - 60분 초과 스킵", logfile)
                    time.sleep(1)
                    continue

                # Gemini 분석
                try:
                    signals = analyze_video_with_gemini(video)
                    total_analyzed += 1
                except Exception as e:
                    log(f"  [ERROR] 분석 실패: {e}", logfile)
                    time.sleep(GEMINI_REQUEST_DELAY)
                    continue

                if not signals:
                    log(f"  → 시그널 없음 (스킵)", logfile)
                    time.sleep(GEMINI_REQUEST_DELAY)
                    continue

                log(f"  → {len(signals)}개 시그널 추출:", logfile)
                for s in signals:
                    log(f"     {s['signal_type']} | {s['stock']} ({s.get('ticker','')}) | conf={s['confidence']} | ts={s.get('timestamp')}", logfile)

                # DB INSERT
                if not dry_run and channel_id:
                    try:
                        video_uuid = db.get_or_create_video(video, channel_id)
                        inserted = db.insert_signals(signals, video_uuid, channel_id)
                        total_inserted += inserted
                        total_signals += len(signals)
                        log(f"  → DB INSERT: {inserted}/{len(signals)}개", logfile)
                    except Exception as e:
                        log(f"  [ERROR] DB INSERT 실패: {e}", logfile)
                else:
                    total_signals += len(signals)
                    log(f"  [DRY-RUN] INSERT 스킵", logfile)

                results.append({
                    'video_id': vid_id,
                    'title': title,
                    'signals_count': len(signals),
                    'signals': signals,
                })

                # 요청 간 딜레이
                if i < len(filtered):
                    time.sleep(GEMINI_REQUEST_DELAY)

            except Exception as loop_err:
                import traceback
                log(f"  [CRITICAL] 영상 {video.get('video_id','?')} 처리 중 예외: {loop_err}", logfile)
                log(f"  {_tb.format_exc()}", logfile)
                log(f"  → 다음 영상으로 계속 진행", logfile)
                time.sleep(GEMINI_REQUEST_DELAY)
                continue

        # 결과 요약
        log(f"\n{'='*60}", logfile)
        log(f"[완료] 총 {total_analyzed}개 영상 분석, {total_signals}개 시그널 추출", logfile)
        if not dry_run:
            log(f"       DB INSERT: {total_inserted}개", logfile)
        log(f"로그 파일: {log_path}", logfile)

        # 결과 저장 (dry-run 시)
        if dry_run:
            result_path = os.path.join(LOG_DIR, f'gemini_dryrun_{timestamp}.json')
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            log(f"결과 저장: {result_path}", logfile)

        return {
            'analyzed': total_analyzed,
            'signals': total_signals,
            'inserted': total_inserted,
        }
    except Exception as fatal:
      err_msg = _tb.format_exc()
      print(f"[FATAL] 파이프라인 최상위 예외:\n{err_msg}")
      try:
          with open(log_path, 'a', encoding='utf-8') as ef:
              ef.write(f"\n[FATAL] {fatal}\n{err_msg}\n")
      except Exception:
          pass
      return None


def main():
    parser = argparse.ArgumentParser(description='Gemini 2.0 Flash 파이프라인')
    parser.add_argument('--channel', required=True, help='YouTube 채널 URL')
    parser.add_argument('--limit', type=int, default=None, help='처리할 영상 수')
    parser.add_argument('--offset', type=int, default=0, help='시작 오프셋 (0-based)')
    parser.add_argument('--dry-run', action='store_true', help='DB INSERT 없이 분석만')
    parser.add_argument('--execute', action='store_true', help='실제 실행 (INSERT 포함)')
    parser.add_argument('--no-skip-existing', action='store_true', help='기존 영상도 재처리')
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("[INFO] --dry-run 또는 --execute 옵션을 지정하세요 (기본: --dry-run)")
        args.dry_run = True

    run_pipeline(
        channel_url=args.channel,
        limit=args.limit,
        offset=args.offset,
        dry_run=args.dry_run or not args.execute,
        skip_existing=not args.no_skip_existing,
    )


if __name__ == '__main__':
    main()
