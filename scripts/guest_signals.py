import sys, io, re, json, httpx
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import defaultdict

URL = "https://arypzhotxflimroprmdk.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# 1. Get channel_id
r = httpx.get(f"{URL}/influencer_channels", params={"select": "id,channel_name", "channel_name": "ilike.*이효석*"}, headers=H)
channels = r.json()
print(f"채널: {channels}")
channel_id = channels[0]["id"]

# 2. Get all videos
videos = []
offset = 0
while True:
    r = httpx.get(f"{URL}/influencer_videos", params={
        "select": "id,title,published_at",
        "channel_id": f"eq.{channel_id}",
        "order": "published_at.desc",
        "offset": offset, "limit": 1000
    }, headers={**H, "Range-Unit": "items", "Range": f"{offset}-{offset+999}"})
    batch = r.json()
    if not batch: break
    videos.extend(batch)
    if len(batch) < 1000: break
    offset += 1000

print(f"총 영상: {len(videos)}개")

# 3. Guest detection
TITLES = ["대표", "이사", "본부장", "교수", "위원", "애널리스트", "연구원", "팀장", "CIO", "CEO", "CFO",
          "센터장", "실장", "부장", "차장", "원장", "소장", "국장", "사장", "회장", "전무", "상무",
          "박사", "작가", "기자", "변호사", "세무사", "회계사", "부사장", "매니저", "디렉터", "파트너"]
title_pat = "|".join(re.escape(t) for t in TITLES)

EXCLUDE = {"이효석", "투자의", "시그널", "경제의", "오늘의", "내일의", "글로벌", "미국의", "한국의", "주식의", "시장의"}

def extract_guest(title):
    guests = []
    # "| 이름 직함" pattern
    for m in re.finditer(r'\|\s*([가-힣]{2,4})\s*(' + title_pat + r')', title):
        if m.group(1) not in EXCLUDE:
            guests.append(f"{m.group(1)} {m.group(2)}")
    if guests: return guests
    # General "이름 직함" pattern
    for m in re.finditer(r'([가-힣]{2,4})\s+(' + title_pat + r')(?:\s|$|,|\||\))', title):
        if m.group(1) not in EXCLUDE:
            guests.append(f"{m.group(1)} {m.group(2)}")
    return guests

guest_videos = []
for v in videos:
    title = v.get("title") or ""
    guests = extract_guest(title)
    if guests:
        guest_videos.append({"video_id": v["id"], "title": title, "published_at": v.get("published_at"), "guests": guests})

print(f"게스트 영상: {len(guest_videos)}개")

# 4. Get signal counts per video
video_ids = [gv["video_id"] for gv in guest_videos]
signal_counts = {}

for i in range(0, len(video_ids), 20):
    batch = video_ids[i:i+20]
    ids_str = ",".join(batch)
    r = httpx.get(f"{URL}/influencer_signals", params={
        "select": "video_id",
        "video_id": f"in.({ids_str})"
    }, headers={**H, "Prefer": "count=exact"})
    # Count per video from response
    sigs = r.json()
    for s in sigs:
        vid = s["video_id"]
        signal_counts[vid] = signal_counts.get(vid, 0) + 1

for gv in guest_videos:
    gv["signal_count"] = signal_counts.get(gv["video_id"], 0)

# 5. Group by guest
guest_group = defaultdict(list)
for gv in guest_videos:
    for g in gv["guests"]:
        guest_group[g].append(gv)

# Save JSON
import os
os.makedirs("data", exist_ok=True)
with open("data/hs_guest_signals.json", "w", encoding="utf-8") as f:
    json.dump(guest_videos, f, ensure_ascii=False, indent=2)

# Print report
print("\n" + "="*60)
print("게스트별 영상 리스트")
print("="*60)
for guest, vids in sorted(guest_group.items(), key=lambda x: -len(x[1])):
    total_signals = sum(v["signal_count"] for v in vids)
    print(f"\n📌 {guest} ({len(vids)}건, 시그널 총 {total_signals}건)")
    for v in sorted(vids, key=lambda x: x.get("published_at") or "", reverse=True):
        print(f"  - {v['title']} (시그널 {v['signal_count']}건)")

print(f"\n총 게스트: {len(guest_group)}명, 총 게스트영상: {len(guest_videos)}개")
