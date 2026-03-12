import urllib.request, json

URL = "https://arypzhotxflimroprmdk.supabase.co"
# DEPLOYMENT.md의 anon key
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

req = urllib.request.Request(
    URL + "/rest/v1/influencer_channels?select=id&limit=1",
    headers={"apikey": ANON_KEY, "Authorization": "Bearer " + ANON_KEY}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        print("OK - anon key 유효:", data)
except Exception as e:
    print("FAIL:", e)
