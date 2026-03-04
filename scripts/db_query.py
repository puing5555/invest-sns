import urllib.request, json, ssl, re

ctx = ssl.create_default_context()
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

# First get the columns
url = f"{SUPABASE_URL}/rest/v1/influencer_signals?select=*&limit=1"
req = urllib.request.Request(url)
req.add_header('apikey', KEY)
req.add_header('Authorization', f'Bearer {KEY}')
try:
    resp = urllib.request.urlopen(req, context=ctx)
    data = json.loads(resp.read())
    if data:
        print("Columns:", list(data[0].keys()))
except urllib.error.HTTPError as e:
    print(f"Error: {e.read().decode()}")
