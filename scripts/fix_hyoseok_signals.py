"""
이효석 시그널 DB 수정 스크립트
- Step 1: 빈 레코드 삭제 (#333)
- Step 2: TSMC 중복 레코드 삭제 (#280, #282)
- Step 3: 426건 published_at 날짜 교체
"""
from dotenv import load_dotenv
import os, requests, json

load_dotenv('.env.local')
SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def get_record(table, id_val):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id_val}", headers=headers)
    return r.json()

def delete_record(table, id_val):
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id_val}", headers=headers)
    return r.status_code, r.text

print("=" * 60)
print("Step 1: 빈 레코드 삭제 (id=333)")
print("=" * 60)

rec333 = get_record('influencer_signals', 333)
print(f"삭제 전 id=333 레코드:")
print(json.dumps(rec333, ensure_ascii=False, indent=2))

status, resp = delete_record('influencer_signals', 333)
print(f"DELETE id=333 → status={status}, response={resp[:200]}")

print()
print("=" * 60)
print("Step 2: TSMC 중복 레코드 삭제 (#280, #282)")
print("=" * 60)

rec280 = get_record('influencer_signals', 280)
rec282 = get_record('influencer_signals', 282)
print(f"\n삭제 전 id=280 레코드:")
print(json.dumps(rec280, ensure_ascii=False, indent=2))
print(f"\n삭제 전 id=282 레코드:")
print(json.dumps(rec282, ensure_ascii=False, indent=2))

# 어느 게 남는지 확인 (280과 282 중 다른 ID가 남음)
print("\n→ id=280, id=282 삭제. 나머지 TSMC 레코드들은 유지됨.")

status280, resp280 = delete_record('influencer_signals', 280)
print(f"DELETE id=280 → status={status280}")
status282, resp282 = delete_record('influencer_signals', 282)
print(f"DELETE id=282 → status={status282}")

print()
print("=" * 60)
print("Step 3: 이효석아카데미 published_at 날짜 교체")
print("=" * 60)

# 이효석아카데미 시그널 전체 조회 (video_uuid 포함)
all_signals = []
offset = 0
limit = 1000
while True:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/influencer_signals"
        f"?channel_name=eq.이효석아카데미&select=id,published_at,video_uuid"
        f"&offset={offset}&limit={limit}",
        headers=headers
    )
    batch = r.json()
    if not batch:
        break
    all_signals.extend(batch)
    if len(batch) < limit:
        break
    offset += limit

print(f"이효석아카데미 시그널 총 {len(all_signals)}건 조회됨")

# video_uuid 목록 수집
video_uuids = list(set(s['video_uuid'] for s in all_signals if s.get('video_uuid')))
print(f"고유 video_uuid 수: {len(video_uuids)}")

# influencer_videos 테이블에서 published_at 조회
# UUID 목록을 배치로 조회
video_map = {}
batch_size = 100
for i in range(0, len(video_uuids), batch_size):
    batch_uuids = video_uuids[i:i+batch_size]
    uuid_list = ','.join(batch_uuids)
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/influencer_videos"
        f"?uuid=in.({uuid_list})&select=uuid,published_at",
        headers=headers
    )
    for v in r.json():
        video_map[v['uuid']] = v.get('published_at')

print(f"video 테이블에서 {len(video_map)}건 published_at 조회됨")

# 업데이트 전 샘플 5건 출력
print("\n업데이트 전 샘플 5건 (signal.published_at → video.published_at):")
count = 0
for s in all_signals[:20]:
    v_pub = video_map.get(s.get('video_uuid'))
    if v_pub:
        print(f"  id={s['id']}: {s['published_at']} → {v_pub}")
        count += 1
        if count >= 5:
            break

# 실제 업데이트
success = 0
fail = 0
for s in all_signals:
    vid_uuid = s.get('video_uuid')
    if not vid_uuid:
        fail += 1
        continue
    v_pub = video_map.get(vid_uuid)
    if not v_pub:
        fail += 1
        continue
    
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/influencer_signals?id=eq.{s['id']}",
        headers=headers,
        json={'published_at': v_pub}
    )
    if r.status_code in (200, 204):
        success += 1
    else:
        fail += 1
        print(f"  FAIL id={s['id']}: {r.status_code} {r.text[:100]}")

print(f"\n업데이트 결과: 성공={success}, 실패={fail}")

# 업데이트 후 샘플 5건 확인
print("\n업데이트 후 샘플 5건 확인:")
sample_ids = [s['id'] for s in all_signals[:5]]
for sid in sample_ids:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/influencer_signals?id=eq.{sid}&select=id,published_at,video_uuid",
        headers=headers
    )
    rec = r.json()
    if rec:
        v_pub = video_map.get(rec[0].get('video_uuid'))
        print(f"  id={rec[0]['id']}: published_at={rec[0]['published_at']} (video={v_pub})")

print()
print("=" * 60)
print("DB 작업 완료!")
print("=" * 60)
print(f"  - id=333 삭제: {'성공' if status in (200, 204) else '실패'}")
print(f"  - id=280 삭제: {'성공' if status280 in (200, 204) else '실패'}")
print(f"  - id=282 삭제: {'성공' if status282 in (200, 204) else '실패'}")
print(f"  - published_at 업데이트: {success}건 성공, {fail}건 실패")
