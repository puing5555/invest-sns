#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코린파파 채널 배치 파이프라인 실행기
- 30개씩 배치 처리
- 각 배치 완료 후 DB INSERT 건수 확인
- 암호화폐 시그널 포함 (V11.3+)

실행 방법:
  python scripts/run_corinpapa_batch.py
  python scripts/run_corinpapa_batch.py --offset 60   (60번째부터 재시작)
  python scripts/run_corinpapa_batch.py --batch-size 20
  python scripts/run_corinpapa_batch.py --skip-qa
"""

import os
import sys
import argparse
import re
import time
import requests
from datetime import datetime
from typing import Optional

# 프로젝트 루트
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# scripts/ 디렉토리를 sys.path에 추가
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

# ── 채널 설정 ──────────────────────────────────────────────────────────
CHANNEL_URL = 'https://www.youtube.com/@corinpapa1106'
CHANNEL_ID = 'c9c4dc38-c108-4988-b1d2-b177c3b324fc'
BATCH_SIZE = 30


# ── Supabase 카운트 확인 ───────────────────────────────────────────────
def _load_supabase_creds():
    """Supabase API 자격증명 로드 (.env.local)"""
    env_path = os.path.join(PROJECT_ROOT, '.env.local')
    try:
        env_text = open(env_path, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"[ERROR] .env.local 파일 없음: {env_path}")
        sys.exit(1)

    anon_key_m = re.search(r'NEXT_PUBLIC_SUPABASE_ANON_KEY=(.+)', env_text)
    url_m = re.search(r'NEXT_PUBLIC_SUPABASE_URL=(.+)', env_text)

    if not anon_key_m or not url_m:
        print("[ERROR] .env.local에서 NEXT_PUBLIC_SUPABASE_ANON_KEY 또는 NEXT_PUBLIC_SUPABASE_URL을 찾을 수 없습니다")
        sys.exit(1)

    return anon_key_m.group(1).strip(), url_m.group(1).strip()


ANON_KEY, SUPABASE_URL = _load_supabase_creds()


def get_signal_count() -> int:
    """influencer_signals 전체 카운트 조회"""
    try:
        r = requests.get(
            f'{SUPABASE_URL}/rest/v1/influencer_signals?select=id',
            headers={
                'apikey': ANON_KEY,
                'Authorization': f'Bearer {ANON_KEY}',
                'Prefer': 'count=exact',
                'Range': '0-0'
            },
            timeout=10
        )
        cr = r.headers.get('content-range', '0/0')
        total = cr.split('/')[-1] if '/' in cr else '0'
        return int(total) if total.isdigit() else 0
    except Exception as e:
        print(f"  [WARNING] 시그널 카운트 조회 실패: {e}")
        return 0


# ── 파이프라인 임포트 ──────────────────────────────────────────────────
def _import_pipeline():
    """AutoPipeline 클래스 임포트"""
    try:
        from auto_pipeline import (
            AutoPipeline, get_channel_slug, normalize_videos_for_gate,
            save_tmp_json, PROJECT_ROOT as _PR
        )
        return AutoPipeline
    except ImportError as e:
        print(f"[FATAL] auto_pipeline 임포트 실패: {e}")
        print("scripts/ 디렉토리에서 실행하거나, PROJECT_ROOT에 scripts/가 있는지 확인하세요.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='코린파파 채널 배치 파이프라인 실행기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python scripts/run_corinpapa_batch.py
  python scripts/run_corinpapa_batch.py --offset 60     # 60번째 영상부터 재시작
  python scripts/run_corinpapa_batch.py --batch-size 20 # 배치 크기 변경
  python scripts/run_corinpapa_batch.py --dry-run       # 목록 확인만 (실제 처리 안 함)
  python scripts/run_corinpapa_batch.py --skip-qa       # QA Gate 건너뜀
        """
    )
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                        help=f'배치당 처리할 영상 수 (기본값: {BATCH_SIZE})')
    parser.add_argument('--offset', type=int, default=0,
                        help='시작 오프셋 — N번째 영상부터 처리 (기본값: 0)')
    parser.add_argument('--limit', type=int, default=None,
                        help='최대 처리할 총 영상 수 (기본값: 제한 없음)')
    parser.add_argument('--dry-run', action='store_true',
                        help='영상 목록 확인만 (실제 처리 안 함)')
    parser.add_argument('--skip-existing', action='store_true',
                        help='DB에 이미 있는 영상 건너뛰기')
    parser.add_argument('--skip-qa', action='store_true',
                        help='QA Gate 검증 건너뜀 (긴급 시 사용)')
    args = parser.parse_args()

    print("=" * 70)
    print("코린파파 채널 배치 파이프라인 실행기")
    print(f"채널: {CHANNEL_URL}")
    print(f"채널 ID: {CHANNEL_ID}")
    print(f"배치 크기: {args.batch_size}")
    print(f"시작 오프셋: {args.offset}")
    if args.limit:
        print(f"최대 처리 수: {args.limit}")
    print(f"시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    AutoPipeline = _import_pipeline()

    # Dry run 모드
    if args.dry_run:
        from auto_pipeline import AutoPipeline as AP
        pipeline = AP()
        result = pipeline.run_dry_run(CHANNEL_URL, args.limit)
        if 'error' in result:
            print(f"[ERROR] {result['error']}")
            return 1
        print("\n[DRY RUN 완료] 실제 처리를 원하면 --dry-run 없이 실행하세요.")
        return 0

    # ── 전체 영상 목록 수집 ───────────────────────────────────────────
    pipeline = AutoPipeline()

    print(f"\n[1/3] 채널 영상 목록 수집 중...")
    videos = pipeline.collector.get_video_list(CHANNEL_URL, limit=None)
    if not videos:
        print("[ERROR] 영상 목록 수집 실패")
        return 1
    print(f"[OK] 총 {len(videos)}개 영상 수집")

    # ── 제목 필터링 ───────────────────────────────────────────────────
    print(f"\n[2/3] 제목 필터링...")
    passed_videos, skipped_videos = pipeline.filter.filter_videos(videos)
    pipeline.filter.print_filter_results(passed_videos, skipped_videos)

    if not passed_videos:
        print("[ERROR] 투자 관련 영상 없음")
        return 1

    # 오프셋 적용
    if args.offset > 0:
        if args.offset >= len(passed_videos):
            print(f"[ERROR] 오프셋({args.offset})이 전체 영상 수({len(passed_videos)})보다 큽니다")
            return 1
        passed_videos = passed_videos[args.offset:]
        print(f"[INFO] 오프셋 {args.offset} 적용 → {len(passed_videos)}개 영상 처리 예정")

    # limit 적용 (오프셋 이후)
    if args.limit:
        passed_videos = passed_videos[:args.limit]
        print(f"[INFO] limit {args.limit} 적용 → {len(passed_videos)}개 영상 처리")

    # ── 배치 분할 ────────────────────────────────────────────────────
    print(f"\n[3/3] 배치 처리 준비...")
    batches = [passed_videos[i:i+args.batch_size]
               for i in range(0, len(passed_videos), args.batch_size)]
    print(f"총 {len(passed_videos)}개 영상 → {len(batches)}개 배치 (배치 크기: {args.batch_size})")

    # ── 채널 정보 수집 ────────────────────────────────────────────────
    channel_info = pipeline.collector.get_channel_info(CHANNEL_URL)
    if not channel_info:
        print("[ERROR] 채널 정보 수집 실패")
        return 1

    # QA 모듈 임포트 (skip_qa=False인 경우)
    use_qa = not args.skip_qa
    run_gate2_fn = None
    if use_qa:
        try:
            from qa.gate2_signals import run_gate2 as _rg2
            run_gate2_fn = _rg2
            print("[INFO] QA Gate 2 활성화")
        except ImportError as e:
            print(f"[WARNING] QA Gate 2 임포트 실패: {e} → QA 건너뜀")
            use_qa = False

    # ── 배치 루프 ────────────────────────────────────────────────────
    total_inserted = 0
    run_start = time.time()

    for batch_idx, batch_videos in enumerate(batches):
        print(f"\n{'='*70}")
        print(f"[배치 {batch_idx+1}/{len(batches)}] {len(batch_videos)}개 영상 처리 시작 "
              f"({datetime.now().strftime('%H:%M:%S')})")

        # 배치 전 시그널 수
        before_count = get_signal_count()
        print(f"  현재 DB 시그널 수: {before_count:,}개")

        # Step 1: 자막 추출
        print(f"\n  [자막 추출] {len(batch_videos)}개 영상...")
        videos_with_subtitles = pipeline.extractor.extract_with_rate_limit(batch_videos)
        successful_videos = [v for v in videos_with_subtitles if v.get('subtitle')]
        print(f"  자막 추출 성공: {len(successful_videos)}/{len(batch_videos)}개")

        if not successful_videos:
            print(f"  [SKIP] 자막 추출 성공한 영상 없음 (암호화폐 채널 특성상 정상)")
            after_count = get_signal_count()
            print(f"  INSERT: 0개 ({before_count} → {after_count})")
            if batch_idx < len(batches) - 1:
                print(f"\n  [대기] 다음 배치까지 60초 대기...")
                time.sleep(60)
            continue

        # Step 2: AI 시그널 분석
        print(f"\n  [AI 분석] {len(successful_videos)}개 영상...")
        analysis_results = pipeline.analyzer.analyze_videos_batch(CHANNEL_URL, successful_videos)

        # 분석 결과 백업
        backup_name = f"scripts/corinpapa_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_batch{batch_idx+1}.json"
        pipeline.analyzer.save_analysis_results(analysis_results, backup_name)
        print(f"  분석 백업: {backup_name}")

        # Step 3: QA Gate 2 (선택)
        if use_qa and run_gate2_fn:
            flat_signals = []
            for res in analysis_results.get('results', []):
                flat_signals.extend(res.get('signals', []))

            print(f"\n  [QA Gate 2] {len(flat_signals)}개 시그널 검증...")
            try:
                gate2_passed = run_gate2_fn(flat_signals, 'corinpapa')
            except Exception as e:
                print(f"  [WARNING] QA Gate 2 오류: {e} → INSERT 계속 진행")
                gate2_passed = True  # 오류 시 통과로 처리 (단일 배치 방지)

            if not gate2_passed:
                print(f"  [SKIP] QA Gate 2 실패 → 배치 {batch_idx+1} DB INSERT 차단")
                if batch_idx < len(batches) - 1:
                    print(f"  60초 대기...")
                    time.sleep(60)
                continue
            print(f"  [OK] QA Gate 2 통과")

        # Step 4: DB INSERT
        print(f"\n  [DB INSERT]...")
        batch_db_stats = pipeline.db_inserter.insert_analysis_results(
            channel_info, analysis_results, args.skip_existing
        )
        print(f"  영상 INSERT: {batch_db_stats.get('inserted_videos', 0)}개")
        print(f"  시그널 INSERT: {batch_db_stats.get('inserted_signals', 0)}개")
        print(f"  스킵: {batch_db_stats.get('skipped_videos', 0)}개")

        # 배치 후 시그널 수
        after_count = get_signal_count()
        batch_inserted = after_count - before_count
        total_inserted += batch_inserted

        print(f"\n  ✅ [배치 {batch_idx+1} 완료] INSERT: {batch_inserted}개 "
              f"({before_count:,} → {after_count:,})")
        print(f"  누적 INSERT: {total_inserted}개")

        # 다음 배치 대기
        if batch_idx < len(batches) - 1:
            print(f"\n  [대기] 레이트리밋 방지 60초 대기 중...")
            time.sleep(60)

    # ── 최종 요약 ─────────────────────────────────────────────────────
    run_elapsed = time.time() - run_start
    final_count = get_signal_count()

    print(f"\n{'='*70}")
    print(f"🎉 코린파파 배치 파이프라인 완료")
    print(f"{'='*70}")
    print(f"총 실행 시간  : {run_elapsed/60:.1f}분")
    print(f"처리 배치 수  : {len(batches)}개")
    print(f"처리 영상 수  : {len(passed_videos)}개")
    print(f"총 INSERT 건수: {total_inserted}개")
    print(f"최종 DB 시그널: {final_count:,}개")
    print(f"완료 시각     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    if total_inserted == 0:
        print("\n[INFO] INSERT 0건 — 이미 처리된 영상이거나 시그널 없는 영상일 수 있습니다.")
        print("[INFO] 새 영상 처리를 원하면 --skip-existing 없이 다시 실행하거나 DB를 확인하세요.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
