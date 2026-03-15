import sys; sys.path.insert(0, 'scripts')
from pipeline_config import PipelineConfig
import requests
cfg = PipelineConfig()
h = {'apikey': cfg.SUPABASE_SERVICE_KEY, 'Authorization': f'Bearer {cfg.SUPABASE_SERVICE_KEY}'}
r = requests.get(cfg.SUPABASE_URL + '/rest/v1/influencer_signals', headers=h,
    params={'select': 'confidence,signal', 'limit': '10', 'order': 'created_at.desc'})
for s in r.json():
    conf = s.get('confidence', '')
    sig = s.get('signal', '')
    print(f'confidence: {conf!r} | signal: {sig!r}')

# Also test with integer confidence
import uuid
from datetime import datetime
test_data = {
    'id': str(uuid.uuid4()),
    'video_id': 'ed300cd9-9b76-4698-b4b6-ce3312ad8d67',
    'stock': 'TEST_DELETE',
    'ticker': '',
    'market': 'OTHER',
    'mention_type': '결론',
    'signal': '긍정',
    'confidence': 7,  # try integer
    'timestamp': '4:14',
    'key_quote': 'test',
    'reasoning': 'test',
    'created_at': datetime.now().isoformat(),
}
h2 = dict(h)
h2['Content-Type'] = 'application/json'
h2['Prefer'] = 'return=minimal'
r2 = requests.post(cfg.SUPABASE_URL + '/rest/v1/influencer_signals', headers=h2, json=test_data)
print(f'\nTest integer confidence (7): {r2.status_code} {r2.text[:200]}')
if r2.ok:
    requests.delete(cfg.SUPABASE_URL + '/rest/v1/influencer_signals', headers=h, params={'stock': 'eq.TEST_DELETE'})
