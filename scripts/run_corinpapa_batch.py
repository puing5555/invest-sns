#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코린파파 채널 배치 파이프라인 실행기 (V11.4 - 전면 재작성)
- Supabase REST API 직접 호출 (godofIT_analyze.py 패턴)
- analyze_video_subtitle() 직접 호출 (video_uuid KeyError 회피)
- 30개씩 배치 처리, 배치 간 60초 대기
- --offset N 옵션으로 중단 시 재시작 가능

실행 방법:
  python scripts/run_corinpapa_batch.py
  python scripts/run_corinpapa_batch.py --offset 60     # 60번째 영상부터 재시작
  python scripts/run_corinpapa_batch.py --batch-size 20 # 배치 크기 변경
  python scripts/run_corinpapa_batch.py --dry-run       # 목록 확인만 (실제 처리 안 함)
  python scripts/run_corinpapa_batch.py --limit 10      # 최대 10개만 처리
"""

import os
import sys
import re
import uuid
import json
import time
import argparse
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

# ── 경로 설정 ──────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

# ── 채널 설정 ──────────────────────────────────────────────────────────
CHANNEL_HANDLE = '@corinpapa1106'
CHANNEL_NAME = '코린이 아빠의 투자일기'
CHANNEL_URL_YT = 'https://www.youtube.com/@corinpapa1106'
PIPELINE_VERSION = 'V11.4'
BATCH_SIZE = 30

# 암호화폐 ticker 목록 (market='CRYPTO' 판단용)
CRYPTO_TICKERS = {
    'BTC', 'ETH', 'XRP', 'BNB', 'ADA', 'SOL', 'DOGE', 'DOT', 'MATIC',
    'AVAX', 'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'BCH', 'TRX', 'NEAR',
    'FTM', 'ALGO', 'VET', 'ICP', 'THETA', 'FIL', 'EGLD', 'XLM', 'HBAR',
    'SUI', 'APT', 'ARB', 'OP', 'PEPE', 'SHIB', 'WLD', 'TON',
}


# ── .env.local 로드 ────────────────────────────────────────────────────
def _load_supabase_creds():
    """Supabase 자격증명 로드 (.env.local - SERVICE_ROLE_KEY 우선)"""
    env_path = os.path.join(PROJECT_ROOT, '.env.local')
    try:
        env_text = open(env_path, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"[FATAL] .env.local 파일 없음: {env_path}")
        sys.exit(1)

    url_m = re.search(r'NEXT_PUBLIC_SUPABASE_URL=(.+)', env_text)
    svc_m = re.search(r'SUPABASE_SERVICE_ROLE_KEY=(.+)', env_text)

    if not url_m or not svc_m:
        print("[FATAL] .env.local에서 NEXT_PUBLIC_SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY를 찾을 수 없습니다")
        sys.exit(1)

    return url_m.group(1).strip(), svc_m.group(1).strip()


_SUPABASE_URL, _SUPABASE_KEY = _load_supabase_creds()
_REST_BASE = f"{_SUPABASE_URL}/rest/v1"
_HEADERS = {
    'apikey': _SUPABASE_KEY,
    'Authorization': f'Bearer {_SUPABASE_KEY}',
    'Content-Type': 'application/json',
}


# ── Supabase REST 헬퍼 ─────────────────────────────────────────────────
def rest_get(table: str, params: str = '') -> List[Dict]:
    """Supabase REST GET"""
    url = f"{_REST_BASE}/{table}?{params}" if params else f"{_REST_BASE}/{table}"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [REST GET ERROR] {table}: {e}")
        return []


def rest_post(table: str, data: Dict) -> Optional[Dict]:
    """Supabase REST POST — 생성된 row 반환"""
    url = f"{_REST_BASE}/{table}"
    headers = {**_HEADERS, 'Prefer': 'return=representation'}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        r.raise_for_status()
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    except Exception as e:
        print(f"  [REST POST ERROR] {table}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  [REST POST DETAIL] {e.response.text[:300]}")
        return None


def rest_patch(table: str, filter_str: str, data: Dict) -> Optional[Dict]:
    """Supabase REST PATCH"""
    url = f"{_REST_BASE}/{table}?{filter_str}"
    headers = {**_HEADERS, 'Prefer': 'return=representation'}
    try:
        r = requests.patch(url, headers=headers, json=data, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [REST PATCH ERROR] {table}: {e}")
        return None


def get_signal_count() -> int:
    """influencer_signals 전체 카운트 조회"""
    try:
        r = requests.get(
            f"{_REST_BASE}/influencer_signals?select=id",
            headers={**_HEADERS, 'Prefer': 'count=exact', 'Range': '0-0'},
            timeout=10
        )
        cr = r.headers.get('content-range', '0/0')
        total = cr.split('/')[-1] if '/' in cr else '0'
        return int(total) if total.isdigit() else 0
    except Exception as e:
        print(f"  [WARNING] 시그널 카운트 조회 실패: {e}")
        return 0


# ── 채널/영상/시그널 CRUD ──────────────────────────────────────────────
def get_or_create_channel() -> Optional[str]:
    """코린파파 채널 UUID 조회 또는 생성"""
    # handle로 조회
    rows = rest_get('influencer_channels',
                    f'select=id,channel_name&channel_handle=eq.{CHANNEL_HANDLE}')
    if not rows:
        # channel_name으로 fallback
        rows = rest_get('influencer_channels',
                        f'select=id,channel_name&channel_name=ilike.*코린이*아빠*')
    if rows:
        cid = rows[0]['id']
        print(f"  [채널] 기존 채널 확인: {cid} ({rows[0].get('channel_name', '')})")
        return cid

    # 없으면 INSERT
    channel_data = {
        'id': str(uuid.uuid4()),
        'channel_name': CHANNEL_NAME,
        'channel_handle': CHANNEL_HANDLE,
        'channel_url': CHANNEL_URL_YT,
        'platform': 'youtube',
        'description': '코린이 아빠의 암호화폐/주식 투자 채널',
    }
    result = rest_post('influencer_channels', channel_data)
    if result:
        cid = result.get('id', channel_data['id'])
        print(f"  [채널] 새 채널 생성: {cid}")
        return cid

    print(f"  [ERROR] 채널 생성 실패")
    return None


def get_or_create_video(channel_id: str, video_data: Dict) -> Optional[str]:
    """
    influencer_videos 조회 또는 생성.
    반환값: influencer_videos.id (UUID) — YouTube video_id가 아님!
    """
    yt_video_id = video_data.get('video_id') or video_data.get('id', '')
    if not yt_video_id:
        print(f"  [WARNING] video_id 없음: {video_data.get('title', 'unknown')}")
        return None

    existing = rest_get('influencer_videos', f'select=id&video_id=eq.{yt_video_id}')
    if existing:
        return existing[0]['id']

    # published_at 처리
    pub_at = video_data.get('published_at') or video_data.get('upload_date')
    if pub_at:
        # yt-dlp 형식: '20240115' → '2024-01-15'
        if re.match(r'^\d{8}$', str(pub_at)):
            pub_at = f"{pub_at[:4]}-{pub_at[4:6]}-{pub_at[6:8]}"
    else:
        pub_at = None

    # duration_seconds 처리
    dur = video_data.get('duration_seconds') or video_data.get('duration')
    try:
        dur = int(dur) if dur else None
    except (ValueError, TypeError):
        dur = None

    new_video = {
        'id': str(uuid.uuid4()),
        'channel_id': channel_id,
        'video_id': yt_video_id,
        'title': video_data.get('title', yt_video_id),
        'published_at': pub_at,
        'duration_seconds': dur,
        'has_subtitle': True,
        'subtitle_language': 'ko',
        'pipeline_version': PIPELINE_VERSION,
        'analyzed_at': datetime.utcnow().isoformat(),
    }
    result = rest_post('influencer_videos', new_video)
    if result:
        vid_uuid = result.get('id', new_video['id'])
        return vid_uuid

    print(f"  [ERROR] 영상 INSERT 실패: {yt_video_id}")
    return None


def _normalize_confidence(conf) -> str:
    """confidence 값 정규화 (숫자 → high/medium/low)"""
    if isinstance(conf, (int, float)):
        if conf >= 8:
            return 'high'
        elif conf >= 5:
            return 'medium'
        else:
            return 'low'
    if isinstance(conf, str):
        lower = conf.lower()
        if lower in ('high', 'medium', 'low'):
            return lower
        # 숫자 문자열
        try:
            n = float(lower)
            return _normalize_confidence(n)
        except ValueError:
            pass
    return 'medium'


def _detect_market(signal: Dict) -> str:
    """ticker 기반으로 market 결정"""
    market = signal.get('market', '')
    if market and market.upper() != 'KR':
        # 이미 지정된 경우 CRYPTO 여부만 보정
        ticker = (signal.get('ticker') or '').upper()
        if ticker in CRYPTO_TICKERS:
            return 'CRYPTO'
        return market

    ticker = (signal.get('ticker') or '').upper()
    if ticker in CRYPTO_TICKERS:
        return 'CRYPTO'

    return market or 'KR'


def insert_signal(video_uuid: str, signal_data: Dict) -> bool:
    """influencer_signals INSERT (중복 체크 포함)"""
    stock = signal_data.get('stock', '')
    if not stock:
        return False  # 종목 없는 시그널 스킵

    # 중복 체크: 같은 video_uuid + stock 조합
    existing = rest_get('influencer_signals',
                        f'select=id&video_id=eq.{video_uuid}&stock=eq.{stock}')
    if existing:
        print(f"    [SKIP] 중복 시그널: {stock}")
        return False

    # signal 값 정규화
    signal_val = (signal_data.get('signal_type') or signal_data.get('signal', '중립')).strip()
    VALID_SIGNALS = {'매수', '긍정', '중립', '부정', '매도'}
    if signal_val not in VALID_SIGNALS:
        signal_val = '중립'

    # timestamp 검증
    ts = signal_data.get('timestamp', '')
    if ts and not re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', str(ts)):
        ts = ''

    data = {
        'id': str(uuid.uuid4()),
        'video_id': video_uuid,
        'stock': stock,
        'ticker': signal_data.get('ticker', ''),
        'market': _detect_market(signal_data),
        'mention_type': '결론',
        'signal': signal_val,
        'confidence': _normalize_confidence(signal_data.get('confidence', 'medium')),
        'timestamp': ts or None,
        'key_quote': (signal_data.get('key_quote', '') or '')[:500],
        'reasoning': (signal_data.get('reasoning', '') or '')[:500],
        'pipeline_version': PIPELINE_VERSION,
        'review_status': 'pending',
    }

    result = rest_post('influencer_signals', data)
    if result:
        return True

    return False


# ── 파이프라인 임포트 ──────────────────────────────────────────────────
def _import_pipeline_components():
    """AutoPipeline 컴포넌트 임포트"""
    try:
        from auto_pipeline import AutoPipeline
        return AutoPipeline
    except ImportError as e:
        print(f"[FATAL] auto_pipeline 임포트 실패: {e}")
        sys.exit(1)


def _import_analyzer():
    """SignalAnalyzer 임포트"""
    try:
        from signal_analyzer_rest import SignalAnalyzer
        return SignalAnalyzer()
    except ImportError as e:
        print(f"[FATAL] signal_analyzer_rest 임포트 실패: {e}")
        sys.exit(1)


# ── 메인 ──────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='코린파파 채널 배치 파이프라인 실행기 (V11.4)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python scripts/run_corinpapa_batch.py
  python scripts/run_corinpapa_batch.py --offset 60     # 60번째 영상부터 재시작
  python scripts/run_corinpapa_batch.py --batch-size 20 # 배치 크기 변경
  python scripts/run_corinpapa_batch.py --dry-run       # 목록 확인만
  python scripts/run_corinpapa_batch.py --limit 10      # 최대 10개만
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
    args = parser.parse_args()

    print("=" * 70)
    print("코린파파 채널 배치 파이프라인 실행기 (V11.4)")
    print(f"채널: {CHANNEL_URL_YT}")
    print(f"배치 크기: {args.batch_size}")
    print(f"시작 오프셋: {args.offset}")
    if args.limit:
        print(f"최대 처리 수: {args.limit}")
    print(f"시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    AutoPipeline = _import_pipeline_components()
    pipeline = AutoPipeline()

    # ── 전체 영상 목록 수집 ───────────────────────────────────────────
    print(f"\n[1/3] 채널 영상 목록 수집 중...")
    videos = pipeline.collector.get_video_list(CHANNEL_URL_YT, limit=None)
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

    # limit 적용
    if args.limit:
        passed_videos = passed_videos[:args.limit]
        print(f"[INFO] limit {args.limit} 적용 → {len(passed_videos)}개 영상 처리")

    # ── Dry run ──────────────────────────────────────────────────────
    if args.dry_run:
        print(f"\n[DRY RUN] 처리 예정 영상 {len(passed_videos)}개:")
        for i, v in enumerate(passed_videos[:20], 1):
            print(f"  {i:3d}. [{v.get('video_id', v.get('id','?'))}] {v.get('title','?')[:60]}")
        if len(passed_videos) > 20:
            print(f"  ... 외 {len(passed_videos)-20}개")
        print("\n[DRY RUN 완료] 실제 처리를 원하면 --dry-run 없이 실행하세요.")
        return 0

    # ── 채널 UUID 확보 ────────────────────────────────────────────────
    print(f"\n[3/3] 배치 처리 시작...")
    channel_id = get_or_create_channel()
    if not channel_id:
        print("[FATAL] 채널 UUID 획득 실패. 중단.")
        return 1

    # SignalAnalyzer 인스턴스
    analyzer = _import_analyzer()

    # ── 배치 분할 ────────────────────────────────────────────────────
    batches = [passed_videos[i:i+args.batch_size]
               for i in range(0, len(passed_videos), args.batch_size)]
    print(f"총 {len(passed_videos)}개 영상 → {len(batches)}개 배치 (배치 크기: {args.batch_size})")

    total_inserted_signals = 0
    total_inserted_videos = 0
    run_start = time.time()

    for batch_idx, batch_videos in enumerate(batches):
        print(f"\n{'='*70}")
        print(f"[배치 {batch_idx+1}/{len(batches)}] {len(batch_videos)}개 영상 처리 시작 "
              f"({datetime.now().strftime('%H:%M:%S')})")

        before_count = get_signal_count()
        print(f"  현재 DB 시그널 수: {before_count:,}개")

        # Step 1: 자막 추출
        print(f"\n  [자막 추출] {len(batch_videos)}개 영상...")
        videos_with_subtitles = pipeline.extractor.extract_with_rate_limit(batch_videos)
        successful_videos = [v for v in videos_with_subtitles if v.get('subtitle')]
        print(f"  자막 추출 성공: {len(successful_videos)}/{len(batch_videos)}개")

        if not successful_videos:
            print(f"  [SKIP] 자막 있는 영상 없음")
            after_count = get_signal_count()
            print(f"  INSERT: 0개 ({before_count} → {after_count})")
            if batch_idx < len(batches) - 1:
                print(f"\n  [대기] 다음 배치까지 60초 대기...")
                time.sleep(60)
            continue

        # Step 2: 각 영상별 video_uuid 확보 + AI 분석 + 시그널 INSERT
        print(f"\n  [AI 분석 + DB INSERT] {len(successful_videos)}개 영상...")
        batch_videos_inserted = 0
        batch_signals_inserted = 0

        for v_idx, video_data in enumerate(successful_videos):
            yt_vid_id = video_data.get('video_id') or video_data.get('id', 'unknown')
            print(f"\n  [{v_idx+1}/{len(successful_videos)}] {video_data.get('title', yt_vid_id)[:50]}")

            # 2-a. influencer_videos UUID 확보
            video_uuid = get_or_create_video(channel_id, video_data)
            if not video_uuid:
                print(f"    [ERROR] video UUID 획득 실패 — 건너뜀")
                continue

            # video_data에 video_uuid 추가 (안전하게 전달)
            video_data['video_uuid'] = video_uuid
            batch_videos_inserted += 1

            # 2-b. AI 분석 (analyze_video_subtitle 직접 호출)
            subtitle = video_data.get('subtitle', '')
            result = analyzer.analyze_video_subtitle(
                CHANNEL_URL_YT,
                video_data,
                subtitle
            )

            if not result:
                print(f"    [WARNING] AI 분석 결과 없음")
                continue

            # 2-c. signals 추출 (다양한 응답 구조 대응)
            signals = []
            if isinstance(result, list):
                signals = result
            elif isinstance(result, dict):
                signals = (
                    result.get('signals') or
                    result.get('signal_list') or
                    result.get('results') or
                    []
                )

            if not signals:
                print(f"    [INFO] 시그널 없음")
                continue

            print(f"    [AI] {len(signals)}개 시그널 추출됨")

            # 2-d. 시그널 INSERT
            sig_inserted = 0
            for signal in signals:
                if insert_signal(video_uuid, signal):
                    sig_inserted += 1
                    print(f"      ✅ INSERT: {signal.get('stock', '?')} / "
                          f"{signal.get('signal_type') or signal.get('signal', '?')} / "
                          f"conf={signal.get('confidence', '?')}")

            batch_signals_inserted += sig_inserted
            print(f"    → {sig_inserted}/{len(signals)}개 INSERT")

        # Step 3: 배치 결과 확인
        after_count = get_signal_count()
        batch_net = after_count - before_count
        total_inserted_signals += batch_net
        total_inserted_videos += batch_videos_inserted

        print(f"\n  ✅ [배치 {batch_idx+1} 완료]")
        print(f"  영상 처리: {batch_videos_inserted}개")
        print(f"  시그널 INSERT: {batch_net}개 ({before_count:,} → {after_count:,})")
        print(f"  누적 시그널 INSERT: {total_inserted_signals}개")

        # 다음 배치 대기
        if batch_idx < len(batches) - 1:
            print(f"\n  [대기] 레이트리밋 방지 60초 대기 중...")
            time.sleep(60)

    # ── 최종 요약 ─────────────────────────────────────────────────────
    run_elapsed = time.time() - run_start
    final_count = get_signal_count()

    print(f"\n{'='*70}")
    print(f"🎉 코린파파 배치 파이프라인 완료 (V11.4)")
    print(f"{'='*70}")
    print(f"총 실행 시간  : {run_elapsed/60:.1f}분")
    print(f"처리 배치 수  : {len(batches)}개")
    print(f"처리 영상 수  : {len(passed_videos)}개")
    print(f"영상 DB 등록  : {total_inserted_videos}개")
    print(f"총 INSERT 건수: {total_inserted_signals}개")
    print(f"최종 DB 시그널: {final_count:,}개")
    print(f"완료 시각     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    if total_inserted_signals == 0:
        print("\n[INFO] INSERT 0건 — 이미 처리된 영상이거나 시그널 없는 영상일 수 있습니다.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
