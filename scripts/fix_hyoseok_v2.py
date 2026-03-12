"""
이효석아카데미 시그널 날짜 수정
- influencer_signals.created_at이 '2026-03-04' (크롤링 날짜)로 잘못 저장된 것
- video의 실제 published_at으로 교체
- 추가: #333 빈 레코드, #280/#282 TSMC 중복 삭제 (Supabase 대시보드 순서 기준으로 재확인 필요)
"""
from dotenv import load_dotenv
import os, requests, json
from collections import defaultdict

load_dotenv('.env.local')
URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
headers_base = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}
headers = {**headers_base, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

HYOSEOK_CHANNEL_ID = 'd153b75b-1843-4a99-b49f-c31081a8f566'

print("=" * 60)
print("Step A: 이효석 videos 수집")
print("=" * 60)
all_videos = []
offset = 0
while True:
    r = requests.get(
        f'{URL}/rest/v1/influencer_videos?channel_id=eq.{HYOSEOK_CHANNEL_ID}'
        f'&select=id,video_id,published_at&offset={offset}&limit=500',
        headers=headers_base
    )
    batch = r.json()
    if not isinstance(batch, list) or not batch:
        break
    all_videos.extend(batch)
    if len(batch) < 500:
        break
    offset += 500

vid_ids = [v['id'] for v in all_videos]
vid_pub_map = {v['id']: v['published_at'] for v in all_videos}
print(f"이효석아카데미 videos: {len(all_videos)}건")

print()
print("=" * 60)
print("Step B: created_at='2026-03-04' 이효석 시그널 수집")
print("=" * 60)
target_signals = []
batch_size = 100
for i in range(0, len(vid_ids), batch_size):
    batch_vids = vid_ids[i:i+batch_size]
    vid_list = ','.join(batch_vids)
    r = requests.get(
        f'{URL}/rest/v1/influencer_signals?video_id=in.({vid_list})'
        f'&created_at=gte.2026-03-04T00:00:00&created_at=lt.2026-03-05T00:00:00'
        f'&select=id,video_id,created_at,stock,ticker',
        headers=headers_base
    )
    data = r.json()
    if isinstance(data, list):
        target_signals.extend(data)

print(f"대상 시그널: {len(target_signals)}건 (created_at=2026-03-04)")

# 샘플 5건 출력 (업데이트 전)
print("\n업데이트 전 샘플 5건:")
for s in target_signals[:5]:
    pub = vid_pub_map.get(s['video_id'], 'N/A')
    print(f"  id={s['id'][:12]}... created_at={s['created_at'][:10]}, video.published_at={pub}, stock={s['stock']}")

print()
print("=" * 60)
print("Step C: created_at → video.published_at 업데이트")
print("=" * 60)
success = 0
fail = 0
fail_list = []

for s in target_signals:
    vid_pub = vid_pub_map.get(s['video_id'])
    if not vid_pub:
        fail += 1
        fail_list.append({'id': s['id'], 'reason': 'no_video_published_at'})
        continue
    
    r = requests.patch(
        f'{URL}/rest/v1/influencer_signals?id=eq.{s["id"]}',
        headers={**headers_base, 'Content-Type': 'application/json'},
        json={'created_at': vid_pub}
    )
    if r.status_code in (200, 204):
        success += 1
    else:
        fail += 1
        fail_list.append({'id': s['id'], 'status': r.status_code, 'error': r.text[:100]})

print(f"업데이트 성공: {success}건 / 실패: {fail}건")
if fail_list[:3]:
    print(f"실패 샘플: {json.dumps(fail_list[:3], ensure_ascii=False)}")

# 업데이트 후 샘플 5건 확인
print("\n업데이트 후 샘플 5건 확인:")
sample_ids = [s['id'] for s in target_signals[:5]]
for sid in sample_ids:
    r = requests.get(
        f'{URL}/rest/v1/influencer_signals?id=eq.{sid}&select=id,created_at,video_id',
        headers=headers_base
    )
    rec = r.json()
    if rec and isinstance(rec, list):
        pub = vid_pub_map.get(rec[0]['video_id'], 'N/A')
        print(f"  id={rec[0]['id'][:12]}... created_at={rec[0]['created_at'][:10]}, video.pub={pub[:10] if pub else 'N/A'}")

print()
print("=" * 60)
print("완료 요약")
print("=" * 60)
print(f"  이효석 시그널 날짜 업데이트: {success}건 성공 / {fail}건 실패")
