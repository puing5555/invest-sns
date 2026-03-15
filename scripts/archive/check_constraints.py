#!/usr/bin/env python3
import requests

headers = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
}

r = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=mention_type,signal,market', headers=headers)

if r.status_code == 200:
    data = r.json()
    mention_types = set(s['mention_type'] for s in data if s['mention_type'])
    signals = set(s['signal'] for s in data if s['signal']) 
    markets = set(s['market'] for s in data if s['market'])
    
    print("허용되는 mention_type 값들:")
    for t in sorted(mention_types):
        print(f'  "{t}"')
    
    print("\n허용되는 signal 값들:")
    for s in sorted(signals):
        print(f'  "{s}"')
    
    print("\n허용되는 market 값들:")
    for m in sorted(markets):
        print(f'  "{m}"')
else:
    print(f"오류: {r.status_code}")