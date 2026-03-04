import requests, random, json

URL = "https://arypzhotxflimroprmdk.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# 1. Get all signals
r = requests.get(f"{URL}/rest/v1/influencer_signals?select=*&limit=1000", headers=HEADERS)
signals = r.json()
print(f"Total signals: {len(signals)}")

# 2. Random 30
random.seed(42)
sample = random.sample(signals, min(30, len(signals)))

# 3. Get video titles for these
video_ids = list(set(s.get("video_id") for s in sample if s.get("video_id")))
videos = {}
for vid in video_ids:
    r2 = requests.get(f"{URL}/rest/v1/influencer_videos?id=eq.{vid}&select=id,title,channel_id", headers=HEADERS)
    data = r2.json()
    if data:
        videos[vid] = data[0]

# 4. Output as JSON for analysis
output = []
for s in sample:
    vid = s.get("video_id")
    v = videos.get(vid, {})
    output.append({
        "ticker": s.get("ticker"),
        "signal_type": s.get("signal_type"),
        "key_quote": s.get("key_quote"),
        "confidence": s.get("confidence"),
        "video_title": v.get("title", "?"),
        "channel_id": v.get("channel_id", "?"),
        "video_id": vid,
    })

with open("C:/Users/Mario/work/invest-sns/data/audit_raw.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("Saved to audit_raw.json")
