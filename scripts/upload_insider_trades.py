# upload_insider_trades.py - insider_trades JSON → Supabase upsert
import json
import sys
import requests
from pipeline_config import PipelineConfig

config = PipelineConfig()
BASE_URL = config.SUPABASE_URL + "/rest/v1"
HEADERS = {
    'apikey': config.SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates'
}

def upload(stock_code: str):
    path = f"data/insider_trades_{stock_code}.json"
    with open(path, 'r', encoding='utf-8') as f:
        trades = json.load(f)

    print(f"Loaded {len(trades)} trades from {path}")

    # Delete existing trades for this ticker first
    del_resp = requests.delete(
        f"{BASE_URL}/insider_trades?ticker=eq.{stock_code}",
        headers={**HEADERS, 'Prefer': ''}
    )
    print(f"Deleted existing: {del_resp.status_code}")

    # Insert in batches of 50
    batch_size = 50
    total = 0
    for i in range(0, len(trades), batch_size):
        batch = trades[i:i+batch_size]
        resp = requests.post(
            f"{BASE_URL}/insider_trades",
            headers=HEADERS,
            json=batch
        )
        if resp.status_code in (200, 201):
            total += len(batch)
            print(f"  Inserted {total}/{len(trades)}")
        else:
            print(f"  Error batch {i}: {resp.status_code} {resp.text}")

    print(f"Done: {total}/{len(trades)} inserted")

if __name__ == '__main__':
    code = sys.argv[1] if len(sys.argv) > 1 else '222800'
    upload(code)
