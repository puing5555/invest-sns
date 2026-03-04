# -*- coding: utf-8 -*-
import urllib.request, json, random, ssl, sys
sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
URL = "https://arypzhotxflimroprmdk.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
T = "influencer_signals"

def get(path, headers_extra=None):
    h = {**HEADERS}
    if headers_extra: h.update(headers_extra)
    req = urllib.request.Request(f"{URL}{path}", headers=h)
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read().decode()), r.getheader("content-range")

# First get full schema
sample, _ = get(f"/{T}?select=*&limit=1")
print("컬럼:", list(sample[0].keys()))

# A-1: 시그널 총 수
_, cr = get(f"/{T}?select=id&limit=1", {"Range": "0-0", "Prefer": "count=exact"})
total = cr.split("/")[1] if cr else "?"
print(f"\nA-1: 시그널 총 수 = {total}")

# A-2: 채널 수 - check videos or speakers table
for tbl in ["speakers","influencers","videos"]:
    try:
        _, cr2 = get(f"/{tbl}?select=id&limit=1", {"Range": "0-0", "Prefer": "count=exact"})
        ct = cr2.split("/")[1] if cr2 else "?"
        print(f"A-2: {tbl} 수 = {ct}")
    except: pass

# Get all signals for checks
all_sigs, _ = get(f"/{T}?select=*")
print(f"총 로드: {len(all_sigs)}개")

# A-5: published_at NULL - check if field exists, or use created_at
has_published = 'published_at' in all_sigs[0]
if has_published:
    nulls = [s for s in all_sigs if s.get('published_at') is None]
    print(f"A-5: published_at NULL = {len(nulls)} {'✅' if len(nulls)==0 else '❌'}")
else:
    # Check videos table for published_at
    print("A-5: influencer_signals에 published_at 없음, videos 테이블 확인")
    try:
        vids, _ = get("/videos?select=id,published_at&published_at=is.null")
        print(f"A-5: videos.published_at NULL = {len(vids)} {'✅' if len(vids)==0 else '❌'}")
    except Exception as e:
        print(f"A-5: videos 접근 실패: {e}")

# A-6: 중복 (video_id + ticker)
pairs = [(s.get('video_id',''), s.get('ticker','')) for s in all_sigs]
dupes = len(pairs) - len(set(pairs))
print(f"A-6: 중복(video_id+ticker) = {dupes} {'✅' if dupes==0 else '❌'}")
if dupes > 0:
    from collections import Counter
    c = Counter(pairs)
    for p, cnt in c.most_common(5):
        if cnt > 1: print(f"  중복: video={p[0][:20]}.. ticker={p[1]} x{cnt}")

# A-7: 스피커 검증 - need to join with speakers/videos
# Get speakers
try:
    speakers, _ = get("/speakers?select=*")
    sp_map = {s['id']: s for s in speakers}
    print(f"\n스피커 수: {len(speakers)}")
    for sp in speakers[:10]:
        print(f"  {sp.get('name','?')} ({sp.get('channel_name','?')})")
except: 
    sp_map = {}
    print("스피커 테이블 접근 실패")

# Get videos
try:
    videos, _ = get("/videos?select=id,title,channel_name,published_at")
    vid_map = {v['id']: v for v in videos}
    print(f"영상 수: {len(videos)}")
except:
    vid_map = {}
    print("videos 테이블 접근 실패")

# A-7: 이효석 스피커 검증
print(f"\nA-7: 스피커 검증")
lee_sigs = []
for s in all_sigs:
    sp = sp_map.get(s.get('speaker_id',''), {})
    vid = vid_map.get(s.get('video_id',''), {})
    sp_name = sp.get('name','')
    ch_name = vid.get('channel_name','') or sp.get('channel_name','')
    if '이효석' in sp_name and '이효석' in ch_name:
        lee_sigs.append({**s, '_sp_name': sp_name, '_vid_title': vid.get('title',''), '_ch': ch_name})

guest_names = ["홍춘욱","박세익","김경록","오건영","이선엽","김일구","박종훈","강영현","이지영","한정수","신영재","염승환","석경철","정원호","윤지호","이준범","김한진","전인구","김영익"]
a7_fail = 0
for d in lee_sigs[:10]:
    title = d['_vid_title']
    found = [g for g in guest_names if g in title]
    st = f"❌ 게스트:{','.join(found)}" if found else "✅"
    if found: a7_fail += 1
    print(f"  [{st}] speaker={d['_sp_name']} | {title[:70]}")
print(f"A-7 결과: {'❌ '+str(a7_fail)+'건' if a7_fail else '✅ PASS'} (검사 {min(len(lee_sigs),10)}건)")

# F-3: 필수 필드 NULL
print()
for field in ["ticker","signal","key_quote","timestamp"]:
    nulls = [s for s in all_sigs if s.get(field) is None or s.get(field) == '']
    print(f"F-3: {field} NULL/빈값 = {len(nulls)} {'✅' if len(nulls)==0 else '❌'}")

# 상식 검증
samples = random.sample(all_sigs, min(5, len(all_sigs)))
print(f"\n🧠 상식 검증 (5개 샘플):")
for s in samples:
    sp = sp_map.get(s.get('speaker_id',''), {})
    vid = vid_map.get(s.get('video_id',''), {})
    print(f"---")
    print(f"  채널: {vid.get('channel_name','?')}")
    print(f"  제목: {(vid.get('title') or '?')[:80]}")
    print(f"  스피커: {sp.get('name','?')}")
    print(f"  종목: {s.get('stock','?')} ({s.get('ticker','?')})")
    print(f"  시그널: {s.get('signal','?')}")
    print(f"  인용: {(s.get('key_quote') or '?')[:120]}")
