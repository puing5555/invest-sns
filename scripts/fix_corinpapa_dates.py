#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코린파파 156개 영상 published_at 실제 날짜로 업데이트
- DB에서 video_id 목록 가져오기 (published_at IS NULL)
- yt-dlp로 실제 YouTube 업로드 날짜 수집
- Supabase PATCH로 업데이트

실행: python scripts/fix_corinpapa_dates.py
"""

import os
import sys
import re
import time
import json
import requests
from datetime import datetime

# Windows cp949 환경에서 UTF-8 출력 강제
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── .env.local 로드 ────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    env_path = os.path.join(PROJECT_ROOT, '.env.local')
    try:
        env_text = open(env_path, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"[FATAL] .env.local 파일 없음: {env_path}")
        sys.exit(1)

    url_m = re.search(r'NEXT_PUBLIC_SUPABASE_URL=(.+)', env_text)
    svc_m = re.search(r'SUPABASE_SERVICE_ROLE_KEY=(.+)', env_text)

    if not url_m or not svc_m:
        print("[FATAL] .env.local에서 SUPABASE_URL 또는 SERVICE_ROLE_KEY를 찾을 수 없습니다")
        sys.exit(1)

    return url_m.group(1).strip(), svc_m.group(1).strip()


SUPABASE_URL, SUPABASE_KEY = load_env()
REST_BASE = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}

CHANNEL_ID = 'c9c4dc38-c108-4988-b1d2-b177c3b324fc'


def get_null_videos():
    """published_at IS NULL인 영상 목록 조회"""
    rows = []
    limit = 200
    offset = 0

    while True:
        url = (
            f"{REST_BASE}/influencer_videos"
            f"?select=id,video_id,title"
            f"&channel_id=eq.{CHANNEL_ID}"
            f"&published_at=is.null"
            f"&order=id"
            f"&limit={limit}&offset={offset}"
        )
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            batch = r.json()
        except Exception as e:
            print(f"[ERROR] DB 조회 실패: {e}")
            break

        if not batch:
            break
        rows.extend(batch)
        if len(batch) < limit:
            break
        offset += limit

    return rows


def get_upload_date(video_id):
    """yt-dlp로 YouTube 업로드 날짜 수집. 반환: 'YYYY-MM-DD' or None"""
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
    headers = {**HEADERS, 'Prefer': 'return=minimal'}
    try:
        r = requests.patch(url, headers=headers, json={'published_at': date_str}, timeout=30)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"  [PATCH ERROR] {row_id}: {e}")
        return False


def main():
    print("=" * 60)
    print("코린파파 published_at 수집 + DB 업데이트")
    print(f"시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. DB에서 published_at IS NULL 영상 목록 조회
    print(f"\n[1/3] DB에서 published_at IS NULL 영상 조회...")
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
    samples = []  # 샘플 5건

    TODAY = datetime.utcnow().strftime('%Y-%m-%d')

    for i, row in enumerate(videos):
        row_id = row['id']
        video_id = row['video_id']
        title = (row.get('title') or video_id)[:50]

        upload_date = get_upload_date(video_id)

        if upload_date == 'MEMBERS_ONLY':
            members_count += 1
            # 10개마다 진행 상황 출력
            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{total}] 완료: {success_count}건, 실패: {fail_count}건, 멤버십: {members_count}건")
        elif upload_date:
            # 오늘 날짜이면 크롤링 날짜일 수 있음 → NULL 유지
            if upload_date == TODAY:
                print(f"  [{i+1}] {video_id} — 오늘 날짜({TODAY}) 스킵 (크롤링 날짜 의심)")
                fail_count += 1
            else:
                ok = patch_published_at(row_id, upload_date)
                if ok:
                    success_count += 1
                    if len(samples) < 5:
                        samples.append({'video_id': video_id, 'title': title, 'date': upload_date})
                else:
                    fail_count += 1
        else:
            fail_count += 1

        # 10개마다 진행 상황 출력
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{total}] 완료: {success_count}건, 실패: {fail_count}건, 멤버십: {members_count}건")

        # 딜레이: 영상당 2초, 30개마다 5초 추가
        time.sleep(2)
        if (i + 1) % 30 == 0 and i + 1 < total:
            print(f"  [{i+1}/{total}] 30개 배치 완료 - 5초 추가 대기...")
            time.sleep(5)

    # 3. 최종 요약
    print(f"\n[3/3] 완료")
    print("=" * 60)
    print(f"총 처리: {total}건")
    print(f"성공:    {success_count}건")
    print(f"실패:    {fail_count}건 (날짜 수집 불가)")
    print(f"멤버십:  {members_count}건 (정상 스킵)")
    print("=" * 60)

    if samples:
        print("\n샘플 (성공 5건):")
        for s in samples:
            print(f"  {s['video_id']} | {s['date']} | {s['title']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
