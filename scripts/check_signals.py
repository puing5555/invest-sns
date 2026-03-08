#!/usr/bin/env python3
import json, urllib.request
from collections import Counter

SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'

url = SUPABASE_URL + '/rest/v1/influencer_signals?select=signal,stock,ticker,pipeline_version&pipeline_version=eq.V11&order=signal'
req = urllib.request.Request(url, headers={
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY
})
with urllib.request.urlopen(req, timeout=30) as r:
    signals = json.loads(r.read().decode())

print('Total V11 signals:', len(signals))
dist = Counter(s['signal'] for s in signals)
for k, v in sorted(dist.items()):
    pct = v / len(signals) * 100 if signals else 0
    print('  {}: {}개 ({:.0f}%)'.format(k, v, pct))

print()
print('종목 목록:')
for s in signals:
    print('  {} | {:20} | {}'.format(s['signal'], s['stock'][:20], s['ticker']))
