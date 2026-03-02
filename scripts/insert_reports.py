import json, requests

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# Delete all existing
resp = requests.delete(f"{SUPABASE_URL}/rest/v1/analyst_reports?id=not.is.null", headers=headers)
print(f"Delete: {resp.status_code}")

# Deduplicate
with open("data/analyst_reports.json", "r", encoding="utf-8") as f:
    data = json.load(f)

seen = {}
for ticker, items in data.items():
    for item in items:
        key = (ticker, item["firm"], item["published_at"], item["title"])
        seen[key] = {
            "ticker": ticker,
            "firm": item["firm"],
            "analyst_name": item.get("analyst", ""),
            "title": item["title"],
            "target_price": item.get("target_price"),
            "opinion": item.get("opinion", ""),
            "published_at": item["published_at"],
            "pdf_url": item.get("pdf_url", ""),
            "summary": item.get("summary", "")
        }

rows = list(seen.values())
print(f"Inserting {len(rows)} unique rows")

inserted = 0
for i in range(0, len(rows), 50):
    batch = rows[i:i+50]
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/analyst_reports",
        headers={**headers, "Prefer": "return=minimal"},
        json=batch
    )
    if resp.status_code in (200, 201):
        inserted += len(batch)
    else:
        print(f"Batch {i}: ERROR {resp.status_code} {resp.text[:200]}")

print(f"Done: {inserted}/{len(rows)} inserted")

# Verify count
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/analyst_reports?select=id&limit=1",
    headers={**headers, "Prefer": "count=exact"}
)
print(f"DB count: {resp.headers.get('content-range')}")
