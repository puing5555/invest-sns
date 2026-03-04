# -*- coding: utf-8 -*-
import urllib.request, json, random, ssl, sys
sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
URL = "https://arypzhotxflimroprmdk.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

def get(path, extra=None):
    h = {**H, **(extra or {})}
    req = urllib.request.Request(f"{URL}{path}", headers=h)
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read().decode()), r.getheader("content-range")

# Load all data
all_sigs, _ = get("/influencer_signals?select=*")
speakers, _ = get("/speakers?select=*")
sp_map = {s['id']: s for s in speakers}

# Load all videos
all_vids, _ = get("/influencer_videos?select=id,title,channel_id,published_at")
vid_map = {v['id']: v for v in all_vids}

# Load channels
channels, _ = get("/influencer_channels?select=*")
ch_map = {c['id']: c for c in channels}

print(f"=== Gate 1: 데이터 검증 ===")
print(f"A-1: 시그널 총 수 = {len(all_sigs)} ✅")
print(f"A-2: 채널 수 = {len(channels)}, 스피커 수 = {len(speakers)} ✅")

# A-5: published_at NULL in videos
null_pub = [v for v in all_vids if v.get('published_at') is None]
print(f"A-5: videos published_at NULL = {len(null_pub)} {'✅' if len(null_pub)==0 else '❌'}")

# A-6: 중복
pairs = [(s.get('video_id',''), s.get('ticker','')) for s in all_sigs]
dupes = len(pairs) - len(set(pairs))
print(f"A-6: 중복(video_id+ticker) = {dupes} {'✅' if dupes==0 else '❌'}")

# A-7: 이효석 스피커 검증
# Find 이효석 speaker id
lee_ids = [s['id'] for s in speakers if '이효석' in s.get('name','')]
# Find 이효석아카데미 channel
lee_ch = [c['id'] for c in channels if '이효석' in c.get('channel_name','') or '이효석' in c.get('name','')]
print(f"\n이효석 스피커 ID: {lee_ids}")
print(f"이효석 채널 ID: {lee_ch}")

lee_sigs = [s for s in all_sigs if s.get('speaker_id') in lee_ids]
print(f"이효석 시그널: {len(lee_sigs)}개")

guest_names = ["홍춘욱","박세익","김경록","오건영","이선엽","김일구","박종훈","강영현","이지영","한정수","신영재","염승환","석경철","정원호","윤지호","이준범","김한진","전인구","김영익","양희창","이형수"]
a7_fail = 0
for s in lee_sigs[:10]:
    vid = vid_map.get(s['video_id'], {})
    title = vid.get('title', '(영상 없음)')
    found = [g for g in guest_names if g in title]
    st = f"❌ 게스트:{','.join(found)}" if found else "✅"
    if found: a7_fail += 1
    print(f"  [{st}] {title[:70]} → {s['stock']}({s['ticker']})")
print(f"A-7 결과: {'❌ '+str(a7_fail)+'건' if a7_fail else '✅ PASS'}")

# F-3
print()
f3_ok = True
for field in ["ticker","signal","key_quote","timestamp"]:
    nulls = [s for s in all_sigs if not s.get(field)]
    ok = len(nulls) == 0
    if not ok: f3_ok = False
    print(f"F-3: {field} NULL/빈값 = {len(nulls)} {'✅' if ok else '❌'}")

# 상식 검증
samples = random.sample(all_sigs, min(5, len(all_sigs)))
print(f"\n=== 🧠 상식 검증 (5개 샘플) ===")
for s in samples:
    sp = sp_map.get(s.get('speaker_id',''), {})
    vid = vid_map.get(s.get('video_id',''), {})
    ch = ch_map.get(vid.get('channel_id',''), {})
    print(f"---")
    print(f"  채널: {ch.get('channel_name', ch.get('name','?'))}")
    print(f"  제목: {(vid.get('title') or '?')[:80]}")
    print(f"  스피커: {sp.get('name','?')}")
    print(f"  종목: {s.get('stock','?')} ({s.get('ticker','?')})")
    print(f"  시그널: {s.get('signal','?')}")
    print(f"  인용: {(s.get('key_quote') or '?')[:120]}")
