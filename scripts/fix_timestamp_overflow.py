# -*- coding: utf-8 -*-
"""Step 2: timestamp > duration 초과 시그널 NULL 처리"""
import sys, io, os, json, urllib.request, urllib.error
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LOG_PATH = r'C:\Users\Mario\work\invest-sns\data\tmp\fix_overflow.log'
LOG = open(LOG_PATH, 'w', encoding='utf-8')

def log(msg):
    LOG.write(str(msg) + '\n')
    LOG.flush()
    print(str(msg), flush=True)

# env
with open(r'C:\Users\Mario\work\invest-sns\.env.local', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

SUPA_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPA_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

HDR = {
    'apikey': SUPA_KEY,
    'Authorization': f'Bearer {SUPA_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}


def sb_get(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def sb_patch(path, params, body):
    url = f"{SUPA_URL}/rest/v1/{path}?{params}"
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PATCH', headers=HDR)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return True, r.status
    except urllib.error.HTTPError as e:
        return False, e.code


def ts_to_secs(ts):
    if not ts or str(ts).strip() in ('', 'N/A', 'null', 'None'):
        return None
    try:
        parts = list(map(int, str(ts).strip().split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        else:
            return parts[0]
    except Exception:
        return None


log("=" * 60)
log("Step 2: timestamp 초과 시그널 NULL 처리")
log("=" * 60)

# 1. influencer_videos 로드 (uuid → yt_video_id, duration_seconds, channel_id)
log("[INFO] influencer_videos 로드 중...")
vids_url = f"{SUPA_URL}/rest/v1/influencer_videos?select=id,video_id,duration_seconds,channel_id&limit=3000"
vids = sb_get(vids_url)
log(f"  {len(vids)}개 영상 로드")

# uuid → {yt_id, duration_seconds, channel_id}
vid_map = {v['id']: v for v in vids}
log(f"  duration 있는 영상: {sum(1 for v in vids if v.get('duration_seconds'))}개")

# 2. influencer_signals 로드 (pagination)
log("[INFO] influencer_signals 로드 중...")
all_signals = []
limit = 2000
offset = 0
while True:
    url = f"{SUPA_URL}/rest/v1/influencer_signals?select=id,stock,timestamp,video_id&limit={limit}&offset={offset}"
    chunk = sb_get(url)
    if not chunk:
        break
    all_signals.extend(chunk)
    if len(chunk) < limit:
        break
    offset += limit
    log(f"  로드: {len(all_signals)}개...")

log(f"  총 {len(all_signals)}개 시그널")

# 3. timestamp > duration 찾기
overflow = []
no_duration = 0
no_video = 0

for s in all_signals:
    ts = s.get('timestamp')
    vid_uuid = s.get('video_id')
    vid_data = vid_map.get(vid_uuid, {})
    
    yt_video_id = vid_data.get('video_id')  # YouTube video ID
    duration = vid_data.get('duration_seconds')
    
    if not vid_data:
        no_video += 1
        continue
    if not duration:
        no_duration += 1
        continue
    
    ts_secs = ts_to_secs(ts)
    if ts_secs and ts_secs > duration:
        overflow.append({
            'id': s['id'],
            'stock': s.get('stock'),
            'timestamp': ts,
            'ts_secs': ts_secs,
            'duration': duration,
            'yt_video_id': yt_video_id,
            'channel_id': vid_data.get('channel_id'),
        })

log(f"\n  초과 시그널: {len(overflow)}건 (duration없음: {no_duration}, 영상없음: {no_video})")

if not overflow:
    log("  [OK] 초과 시그널 없음")
else:
    # 채널별 분포
    by_channel = defaultdict(int)
    for s in overflow:
        by_channel[s.get('channel_id', 'unknown')] += 1

    log("  채널별 분포:")
    for ch, cnt in sorted(by_channel.items(), key=lambda x: -x[1]):
        log(f"    {ch}: {cnt}건")

    log("\n  수정 전 샘플 (최대 5건):")
    for s in overflow[:5]:
        log(f"    {s['stock']} | ts={s['timestamp']}({s['ts_secs']}s) > dur={s['duration']}s | yt={s['yt_video_id']}")

    log(f"\n  [FIX] {len(overflow)}건 timestamp NULL 처리 중...")
    null_ok = 0
    null_fail = 0
    for s in overflow:
        ok, status = sb_patch('influencer_signals', f'id=eq.{s["id"]}', {'timestamp': None})
        if ok:
            null_ok += 1
        else:
            null_fail += 1
            if null_fail <= 5:
                log(f"    [WARN] PATCH 실패: {s['id']} status={status}")

    log(f"\n  [DONE] NULL 처리: 성공={null_ok}, 실패={null_fail}")
    log(f"  채널별 건수:")
    for ch, cnt in sorted(by_channel.items(), key=lambda x: -x[1]):
        log(f"    {ch}: {cnt}건")

log("\n" + "=" * 60)
log("[SUMMARY]")
log(f"  overflow NULL 처리: {len(overflow)}건")
log("=" * 60)

LOG.close()
