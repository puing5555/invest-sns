"""GODofIT 채널 비디오 제목 183개 수정 스크립트 (yt-dlp 사용)"""
import os
import sys
import time
import subprocess
import requests
from dotenv import load_dotenv
from pathlib import Path

# Windows 콘솔 UTF-8 출력
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# .env.local 로드
env_path = Path(__file__).parent / '.env.local'
load_dotenv(env_path)

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SERVICE_KEY:
    print("ERROR: env vars missing")
    sys.exit(1)

HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

# 1. 비디오 목록 가져오기 (페이지네이션으로 전부)
import functools
print = functools.partial(print, flush=True)
print("Fetching video list from Supabase...")
videos = []
offset = 0
limit = 1000

while True:
    resp = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_videos'
        f'?channel_id=eq.{CHANNEL_ID}'
        f'&select=id,video_id,title'
        f'&offset={offset}&limit={limit}',
        headers=HEADERS
    )
    batch = resp.json()
    if not batch:
        break
    videos.extend(batch)
    if len(batch) < limit:
        break
    offset += limit

total = len(videos)
print(f"Found {total} videos")

# 2. yt-dlp로 제목 가져와서 업데이트
success_count = 0
fail_count = 0
failed_ids = []

for i, v in enumerate(videos, 1):
    vid_uuid = v['id']
    video_id = v['video_id']
    url = f'https://www.youtube.com/watch?v={video_id}'

    try:
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        result = subprocess.run(
            [sys.executable, '-m', 'yt_dlp', '--print', '%(title)s', '--no-download', '--no-warnings', url],
            capture_output=True,
            text=False,
            timeout=30,
            env=env
        )
        title = result.stdout.decode('utf-8', errors='replace').strip()

        if result.returncode != 0 or not title or title == '[Private video]' or title == '[Deleted video]':
            err = result.stderr.strip()[:100] if result.stderr else 'empty title'
            print(f"[{i}/{total}] FAIL video_id={video_id} ({err})")
            fail_count += 1
            failed_ids.append(video_id)
        else:
            # PATCH title
            patch_resp = requests.patch(
                f'{SUPABASE_URL}/rest/v1/influencer_videos?id=eq.{vid_uuid}',
                headers=HEADERS,
                json={'title': title}
            )
            if patch_resp.status_code in (200, 204):
                print(f"[{i}/{total}] video_id={video_id} -> {title[:60]}")
                success_count += 1
            else:
                print(f"[{i}/{total}] PATCH FAIL video_id={video_id} status={patch_resp.status_code}")
                fail_count += 1
                failed_ids.append(video_id)

    except subprocess.TimeoutExpired:
        print(f"[{i}/{total}] TIMEOUT video_id={video_id}")
        fail_count += 1
        failed_ids.append(video_id)
    except Exception as e:
        print(f"[{i}/{total}] EXCEPTION video_id={video_id}: {e}")
        fail_count += 1
        failed_ids.append(video_id)

    # 2초 딜레이
    time.sleep(2)

    # 20개마다 5초 추가 대기
    if i % 20 == 0:
        print(f"  -- Batch pause 5s (completed {i}/{total}) --")
        time.sleep(5)

# 3. 요약
print(f"\n=== DONE ===")
print(f"Success: {success_count}")
print(f"Fail: {fail_count}")
if failed_ids:
    print(f"Failed video_ids: {failed_ids}")
    with open('failed_title_updates.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(failed_ids))
    print("Failed list saved to failed_title_updates.txt")
