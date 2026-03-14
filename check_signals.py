import sys
sys.path.insert(0, 'scripts')
from pipeline_config import PipelineConfig
import requests, json

cfg = PipelineConfig()
headers = {'apikey': cfg.SUPABASE_SERVICE_KEY, 'Authorization': f'Bearer {cfg.SUPABASE_SERVICE_KEY}'}

# Check existing signal values
r = requests.get(cfg.SUPABASE_URL + '/rest/v1/influencer_signals', headers=headers,
    params={'select': 'signal,mention_type,ticker', 'limit': '5', 'order': 'created_at.desc'})
data = r.json()
for s in data:
    sig = s.get('signal', '')
    mt = s.get('mention_type', '')
    tk = s.get('ticker', '')
    print(f'signal: {sig} | mention_type: {mt} | ticker: {tk}')
