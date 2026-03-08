#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request, json

SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'

def rest_get(path, params=''):
    url = '{}/rest/v1/{}?{}'.format(SUPABASE_URL, path, params)
    req = urllib.request.Request(url, headers={
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer {}'.format(SUPABASE_KEY)
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

channels = rest_get('influencer_channels', 'select=id,channel_name,channel_handle,channel_url&limit=50')
print("총 채널: {}개".format(len(channels)))
for c in channels:
    print(json.dumps(c, ensure_ascii=False))
