#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request, json
from collections import Counter

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

# 1. GODofIT 채널 확인
print("=== 1. GODofIT 채널 조회 ===")
channels = rest_get('influencer_channels', 'select=id,channel_name,channel_handle&channel_handle=eq.%40GODofIT')
print(json.dumps(channels, ensure_ascii=False, indent=2))

if not channels:
    print("GODofIT 채널 없음!")
    exit()

channel_id = channels[0]['id']
print("\n채널 ID:", channel_id)

# 2. 해당 채널의 영상 수
print("\n=== 2. 영상 수 ===")
videos = rest_get('influencer_videos', 'select=id,video_id,pipeline_version&channel_id=eq.{}'.format(channel_id))
print("영상 총:", len(videos), "개")

# 3. 해당 영상들의 시그널
print("\n=== 3. 시그널 집계 ===")
all_signals = []
batch_size = 20
for i in range(0, len(videos), batch_size):
    batch = videos[i:i+batch_size]
    ids = ','.join(['"{}"'.format(v['id']) for v in batch])
    sigs = rest_get('influencer_signals', 'select=signal,pipeline_version&video_id=in.({})'.format(ids))
    all_signals.extend(sigs)

print("시그널 총:", len(all_signals), "개")
signal_counts = Counter(s['signal'] for s in all_signals)
print("signal별:", dict(signal_counts))
pipeline_counts = Counter(s['pipeline_version'] for s in all_signals)
print("pipeline_version별:", dict(pipeline_counts))

# 4. 영상 샘플 5개 - 타이틀, video_id, signal_count
print("\n=== 4. 영상 샘플 5개 ===")
sample_videos = rest_get('influencer_videos', 
    'select=id,video_id,title,signal_count,analyzed_at,pipeline_version&channel_id=eq.{}&limit=5'.format(channel_id))
for v in sample_videos:
    print(json.dumps(v, ensure_ascii=False))
