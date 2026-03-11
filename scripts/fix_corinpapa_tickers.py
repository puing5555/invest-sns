#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_corinpapa_tickers.py
코린파파 채널 시그널의 ticker를 yfinance 호환 형식으로 수정
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# .env.local 로드
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY 없음")
    sys.exit(1)

CORIN_CHANNEL_ID = 'c9c4dc38-c108-4988-b1d2-b177c3b324fc'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ticker 매핑: old → new (COIN, PLTR 등 주식은 제외)
TICKER_MAP = {
    'ETH': 'ETH-USD',
    'BTC': 'BTC-USD',
    'XRP': 'XRP-USD',
    'SOL': 'SOL-USD',
    'CC': 'CNTN-USD',
    'LINK': 'LINK-USD',
    'BMNR': 'BTBT',
}


def get_corinpapa_video_ids():
    """코린파파 채널의 video UUID 목록 수집"""
    video_ids = []
    offset = 0
    limit = 1000
    while True:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
        params = {
            'channel_id': f'eq.{CORIN_CHANNEL_ID}',
            'select': 'id',
            'limit': limit,
            'offset': offset,
        }
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        video_ids.extend([row['id'] for row in data])
        if len(data) < limit:
            break
        offset += limit
    return video_ids


def update_tickers(video_ids, old_ticker, new_ticker):
    """해당 video_id 목록 중 old_ticker → new_ticker 변경"""
    if not video_ids:
        return 0

    # video_id IN (...) 형태로 필터
    video_id_filter = ','.join(video_ids)
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {
        'video_id': f'in.({video_id_filter})',
        'ticker': f'eq.{old_ticker}',
    }
    patch_headers = {**headers, 'Prefer': 'return=representation'}
    resp = requests.patch(url, headers=patch_headers, params=params, json={'ticker': new_ticker})
    if resp.status_code in (200, 201, 204):
        try:
            updated = resp.json()
            return len(updated)
        except Exception:
            return 0
    else:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
        return 0


def verify_sample(new_ticker, limit=3):
    """변경된 ticker 샘플 확인"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {
        'ticker': f'eq.{new_ticker}',
        'select': 'id,stock,ticker',
        'limit': limit,
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        return resp.json()
    return []


def main():
    print("=== 코린파파 ticker 정규화 스크립트 ===\n")

    # 1. video ID 목록 수집
    print("1. 코린파파 비디오 목록 수집 중...")
    video_ids = get_corinpapa_video_ids()
    print(f"   → {len(video_ids)}개 비디오 발견\n")

    if not video_ids:
        print("ERROR: 비디오가 없습니다. channel_id 확인 필요")
        sys.exit(1)

    # 2. ticker 변경
    print("2. ticker 업데이트 시작...\n")
    total_updated = 0
    results = {}

    for old_ticker, new_ticker in TICKER_MAP.items():
        print(f"   {old_ticker} → {new_ticker} 변경 중...")
        count = update_tickers(video_ids, old_ticker, new_ticker)
        results[f"{old_ticker}→{new_ticker}"] = count
        total_updated += count
        print(f"   OK {count}건 변경 완료")

    # 3. 결과 출력
    print(f"\n=== 변경 결과 ===")
    for mapping, count in results.items():
        print(f"  {mapping}: {count}건")
    print(f"\n  총 변경: {total_updated}건")

    # 4. 샘플 확인
    print("\n=== 샘플 확인 (ETH-USD) ===")
    samples = verify_sample('ETH-USD', limit=3)
    for s in samples:
        print(f"  id={s.get('id', '')[:8]}... ticker={s.get('ticker')} stock={s.get('stock')}")

    print("\n=== 완료 ===")


if __name__ == '__main__':
    main()
