import sys
sys.path.insert(0, 'scripts')
from pipeline_config import PipelineConfig
import requests, json

cfg = PipelineConfig()
base_headers = {
    'apikey': cfg.SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {cfg.SUPABASE_SERVICE_KEY}',
}

anyuhua_channel_id = '6d6817ca-76ab-484e-ad7e-b537921c3d25'

# Total signals count
url2 = cfg.SUPABASE_URL + '/rest/v1/influencer_signals'
h2 = dict(base_headers)
h2['Prefer'] = 'count=exact'
r2 = requests.get(url2, headers=h2, params={'select': 'id', 'limit': '1'})
print('Total signals in DB:', r2.headers.get('content-range', 'N/A'))

# Anyuhua signals count - check column name
r_sample = requests.get(url2, headers=base_headers, params={'select': '*', 'limit': '1'})
sample = r_sample.json()
if isinstance(sample, list) and sample:
    print('Columns:', list(sample[0].keys()))

# Check anyuhua videos processed
url3 = cfg.SUPABASE_URL + '/rest/v1/influencer_videos'
h3 = dict(base_headers)
h3['Prefer'] = 'count=exact'
r3 = requests.get(url3, headers=h3, params={
    'select': 'id',
    'channel_id': f'eq.{anyuhua_channel_id}',
    'limit': '1'
})
print('Anyuhua videos in DB:', r3.headers.get('content-range', 'N/A'))
