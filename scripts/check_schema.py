import requests, json
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
headers = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# List tables
r = requests.get("https://arypzhotxflimroprmdk.supabase.co/rest/v1/signals?select=*&limit=2", headers=headers)
print("Status:", r.status_code)
print("Response:", r.text[:1000])

# Try other table names
for table in ['signal', 'stock_signals', 'influencer_signals']:
    r2 = requests.get(f"https://arypzhotxflimroprmdk.supabase.co/rest/v1/{table}?select=*&limit=1", headers=headers)
    print(f"\n{table}: {r2.status_code} {r2.text[:200]}")
