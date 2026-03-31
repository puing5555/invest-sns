# -*- coding: utf-8 -*-
"""
QA 오케스트레이터 - Gate 1 → 2 → 3 순서 실행
==============================================
사용법:
  python scripts/qa/run_all_gates.py \
    --channel godofit \
    --metadata-file data/tmp/godofit_metadata.json \
    --signals-file data/tmp/godofit_signals.json

  # Gate 3 (프론트엔드) 포함
  python scripts/qa/run_all_gates.py \
    --channel godofit \
    --metadata-file data/tmp/godofit_metadata.json \
    --signals-file data/tmp/godofit_signals.json \
    --slug godofit \
    --check-deploy

  # Gate 1/2만 실행 (--skip-gate3)
  python scripts/qa/run_all_gates.py \
    --channel godofit \
    --metadata-file data/tmp/godofit_metadata.json \
    --signals-file data/tmp/godofit_signals.json \
    --skip-gate3

옵션:
  --channel         채널 슬러그 (필수)
  --metadata-file   Gate 1 입력 JSON
  --signals-file    Gate 2 입력 JSON
  --slug            Gate 3 인플루언서 슬러그 (기본: --channel 값)
  --check-deploy    Gate 3 배포 HTTP 체크 활성화
  --skip-gate3      Gate 3 건너뜀 (빌드 전 파이프라인 검증만 할 때)
  --total           Gate 1 원본 영상 총 수 (통과율 계산용)

실패 시: exit(1) + data/qa/error_patterns.json에 에러 누적
성공 시: exit(0)
"""

import sys
import os
import json
import argparse
from datetime import datetime

# scripts/qa/ 기준으로 부모 추가
sys.path.insert(0, os.path.dirname(__file__))

from gate1_metadata import run_gate1
from gate2_signals import run_gate2
from gate3_frontend import run_gate3
from gate4_ticker_check import run_gate4

QA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'qa')


def load_json_file(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def normalize_videos(data):
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'videos' in data:
        return data['videos']
    raise ValueError("입력 형식 오류: 배열 또는 {'videos': [...]} 형식이어야 합니다.")


def normalize_signals(data):
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'signals' in data:
        return data['signals']
    raise ValueError("입력 형식 오류: 배열 또는 {'signals': [...]} 형식이어야 합니다.")


def print_banner(msg):
    border = '═' * 60
    print(f"\n╔{border}╗")
    print(f"║  {msg:<57}║")
    print(f"╚{border}╝")


def main():
    parser = argparse.ArgumentParser(description='QA 오케스트레이터 - Gate 1~4 순서 실행')
    parser.add_argument('--channel', '-c', required=True, help='채널 슬러그 (예: godofit)')
    parser.add_argument('--metadata-file', '-m', required=True,
                        help='Gate 1 입력: 메타데이터 JSON 파일')
    parser.add_argument('--signals-file', '-s', required=True,
                        help='Gate 2 입력: 시그널 JSON 파일')
    parser.add_argument('--slug', help='Gate 3 슬러그 (기본: --channel 값)')
    parser.add_argument('--check-deploy', action='store_true',
                        help='Gate 3 배포 HTTP 체크 활성화')
    parser.add_argument('--skip-gate3', action='store_true',
                        help='Gate 3 건너뜀')
    parser.add_argument('--total', '-t', type=int,
                        help='Gate 1 원본 영상 총 수 (통과율 계산용)')
    parser.add_argument('--project-root', '-r',
                        default=os.path.join(os.path.dirname(__file__), '..', '..'),
                        help='프로젝트 루트 경로')
    args = parser.parse_args()

    channel = args.channel
    slug = args.slug or channel
    project_root = os.path.abspath(args.project_root)

    print_banner(f"🚀 QA 파이프라인 시작: {channel}")
    print(f"  시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  메타데이터: {args.metadata_file}")
    print(f"  시그널: {args.signals_file}")
    print(f"  Gate 3: {'건너뜀' if args.skip_gate3 else f'활성 (slug={slug})'}")

    results = {
        'gate1': None,
        'gate2': None,
        'gate3': None,
        'gate4': None,
    }

    # ──────────────────────────────────
    # Gate 1
    # ──────────────────────────────────
    print_banner("Gate 1: 메타데이터 검증")
    try:
        raw = load_json_file(args.metadata_file)
        videos = normalize_videos(raw)
    except Exception as e:
        print(f"❌ 메타데이터 파일 읽기 실패: {e}", file=sys.stderr)
        sys.exit(1)

    g1_passed, filtered_videos = run_gate1(videos, channel, args.total)
    results['gate1'] = 'PASS' if g1_passed else 'FAIL'

    if not g1_passed:
        _print_summary(results, channel)
        sys.exit(1)

    print(f"✅ Gate 1 통과 → 필터된 영상 {len(filtered_videos)}개 → Gate 2로 이동")

    # ──────────────────────────────────
    # Gate 2
    # ──────────────────────────────────
    print_banner("Gate 2: 시그널 분석 검증")
    try:
        raw = load_json_file(args.signals_file)
        signals = normalize_signals(raw)
    except Exception as e:
        print(f"❌ 시그널 파일 읽기 실패: {e}", file=sys.stderr)
        sys.exit(1)

    g2_passed = run_gate2(signals, channel)
    results['gate2'] = 'PASS' if g2_passed else 'FAIL'

    if not g2_passed:
        _print_summary(results, channel)
        sys.exit(1)

    print(f"✅ Gate 2 통과 → Gate 3로 이동")

    # ──────────────────────────────────
    # Gate 3
    # ──────────────────────────────────
    if args.skip_gate3:
        print_banner("Gate 3: 건너뜀 (--skip-gate3)")
        results['gate3'] = 'SKIP'
    else:
        print_banner(f"Gate 3: 프론트엔드 검증 (slug={slug})")
        g3_passed = run_gate3(slug, project_root, args.check_deploy)
        results['gate3'] = 'PASS' if g3_passed else 'FAIL'

        if not g3_passed:
            _print_summary(results, channel)
            sys.exit(1)

        print(f"✅ Gate 3 통과 → 배포 승인")

    # ──────────────────────────────────
    # Gate 4: Ticker 유효성 검증
    # ──────────────────────────────────
    print_banner("Gate 4: Ticker 유효성 검증")
    g4_code = run_gate4(fix=False)
    results['gate4'] = 'PASS' if g4_code == 0 else 'FAIL'

    if g4_code != 0:
        print("⚠️  Gate 4 실패: 누락 ticker 존재. --fix로 자동 추가 가능:")
        print("   python scripts/qa/gate4_ticker_check.py --fix")
        _print_summary(results, channel)
        sys.exit(1)

    print("✅ Gate 4 통과 → 모든 ticker 검증 완료")

    # ──────────────────────────────────
    # 최종 요약
    # ──────────────────────────────────
    _print_summary(results, channel)

    print(f"\n🎉 모든 QA 게이트 통과! 파이프라인 완료.")
    print(f"  완료 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(0)


def _print_summary(results, channel):
    print(f"\n{'─'*60}")
    print(f"📋 QA 결과 요약 — 채널: {channel}")
    print(f"{'─'*60}")
    icons = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️', None: '⏸️'}
    for gate, result in results.items():
        icon = icons.get(result, '?')
        label = result or '미실행'
        print(f"  {icon} {gate.upper()}: {label}")
    print(f"{'─'*60}")


if __name__ == '__main__':
    main()
