#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전체 채널 영상 published_at 백필
- DB에서 published_at IS NULL인 모든 영상 처리 (채널 필터 없음)
- yt-dlp로 실제 YouTube 업로드 날짜 수집
- Supabase PATCH로 업데이트
- 배치 200개씩, 2초 딜레이, 50개마다 진행상황 출력

실행: python scripts/backfill_all_published_at.py
"""

import os
import sys
import time
import requests
from datetime import datetime

# Windows cp949 환경에서 UTF-8 출력 강제
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── Supabase 크레덴셜 ────────────────────────────────────────────────────
SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'

REST_BASE = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}

BATCH_SIZE = 200
PROGRESS_INTERVAL = 50


def get_null_videos():
    """published_at IS NULL인 모든 영상 목록 조회 (채널 필터 없음)"""
    rows = []
    offset = 0

    while True:
        url = (
            f"{REST_BASE}/influencer_videos"
            f"?select=id,video_id,title,channel_id"
            f"&published_at=is.null"
            f"&order=id"
            f"&limit={BATCH_SIZE}&offset={offset}"
        )
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            batch = r.json()
        except Exception as e:
            print(f"[ERROR] DB 조회 실패 (offset={offset}): {e}")
            break

        if not batch:
            break
        rows.extend(batch)
        print(f"  조회 중... {len(rows)}건")
        if len(batch) < BATCH_SIZE:
            break
        offset += BATCH_SIZE
        time.sleep(2)

    return rows


def get_upload_date(video_id):
    """yt-dlp로 YouTube 업로드 날짜 수집. 반환: 'YYYY-MM-DD' or None or 'MEMBERS_ONLY'"""
    try:
        import yt_dlp
    except ImportError:
        print("[FATAL] yt-dlp가 설치되지 않았습니다. pip install yt-dlp")
        sys.exit(1)

    url = f'https://www.youtube.com/watch?v={video_id}'
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            upload_date = info.get('upload_date')  # 'YYYYMMDD' 형식
            if upload_date and len(str(upload_date)) == 8:
                return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    except Exception as e:
        err_str = str(e)
        # 멤버십 전용 영상 = 정상 스킵
        if 'members-only' in err_str.lower() or 'join' in err_str.lower() or 'private' in err_str.lower():
            return 'MEMBERS_ONLY'
        print(f"  Error {video_id}: {err_str[:100]}")
    return None


def patch_published_at(row_id, date_str):
    """Supabase PATCH: published_at 업데이트"""
    url = f"{REST_BASE}/influencer_videos?id=eq.{row_id}"
    h = {**HEADERS, 'Prefer': 'return=minimal'}
    try:
        r = requests.patch(url, headers=h, json={'published_at': date_str}, timeout=30)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"  [PATCH ERROR] {row_id}: {e}")
        return False


def main():
    print("=" * 60)
    print("전체 채널 published_at 백필")
    print(f"시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. DB에서 published_at IS NULL 영상 목록 조회
    print(f"\n[1/3] DB에서 published_at IS NULL 영상 전체 조회...")
    videos = get_null_videos()
    total = len(videos)

    if total == 0:
        print("[OK] published_at IS NULL 영상 없음 — 작업 불필요")
        return 0

    print(f"[OK] {total}건 조회됨")

    # 2. yt-dlp로 날짜 수집 + PATCH
    print(f"\n[2/3] yt-dlp 날짜 수집 + DB 업데이트 (2초 딜레이)...")
    success_count = 0
    fail_count = 0
    members_count = 0

    TODAY = datetime.now().strftime('%Y-%m-%d')

    for i, row in enumerate(videos):
        row_id = row['id']
        video_id = row['video_id']

        upload_date = get_upload_date(video_id)

        if upload_date == 'MEMBERS_ONLY':
            members_count += 1
        elif upload_date:
            if upload_date == TODAY:
                fail_count += 1
            else:
                ok = patch_published_at(row_id, upload_date)
                if ok:
                    success_count += 1
                else:
                    fail_count += 1
        else:
            fail_count += 1

        # 50개마다 진행상황 출력
        if (i + 1) % PROGRESS_INTERVAL == 0:
            print(f"  [{i+1}/{total}] 성공: {success_count}건, 실패: {fail_count}건, 멤버십: {members_count}건")

        # 딜레이: 영상당 2초
        time.sleep(2)
        # 200개마다 5초 추가 대기
        if (i + 1) % BATCH_SIZE == 0 and i + 1 < total:
            print(f"  [{i+1}/{total}] 배치 완료 - 5초 추가 대기...")
            time.sleep(5)

    # 3. 최종 요약
    print(f"\n[3/3] 완료")
    print("=" * 60)
    print(f"총 처리: {total}건")
    print(f"성공:    {success_count}건")
    print(f"실패:    {fail_count}건 (날짜 수집 불가)")
    print(f"멤버십:  {members_count}건 (정상 스킵)")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
