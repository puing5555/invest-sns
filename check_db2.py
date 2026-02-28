import urllib.request, json, ssl

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
ctx = ssl.create_default_context()

def query(table, select="*", extra=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={select}{extra}"
    req = urllib.request.Request(url, headers={
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
    })
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read())

print("=== VIDEOS (keys) ===")
vids = query("influencer_videos")
if vids:
    print("Keys:", list(vids[0].keys()))
    for v in vids:
        print(json.dumps({k: v.get(k) for k in ['id','video_id','title','channel_id']}, ensure_ascii=False, default=str))

print("\n=== SPEAKERS ===")
for s in query("speakers"):
    print(json.dumps(s, ensure_ascii=False, default=str))

print("\n=== SIGNALS ===")
sigs = query("influencer_signals")
print(f"Total: {len(sigs)}")
if sigs:
    print("Keys:", list(sigs[0].keys()))
    for s in sigs[:3]:
        print(json.dumps({k: s.get(k) for k in ['stock','signal','speaker_id','video_id','pipeline_version']}, ensure_ascii=False, default=str))
