import sys, uuid, requests
from datetime import datetime
sys.path.insert(0, 'scripts')
from pipeline_config import PipelineConfig
from db_inserter_rest import DatabaseInserter

cfg = PipelineConfig()
db = DatabaseInserter()

# Test with exactly the kind of signal the pipeline produces
test_signal = {
    'stock_symbol': 'BTCTEST',
    'signal_type': 'POSITIVE',  # English - should be converted
    'confidence': 0.7,           # float - should be converted to 'medium'
    'timestamp': '4:14',
    'key_quote': 'Test key quote for debugging',
    'reasoning': 'Test reasoning for debugging',
}

test_video_uuid = 'ed300cd9-9b76-4698-b4b6-ce3312ad8d67'

try:
    result = db._insert_signal_for_video(test_video_uuid, test_signal)
    print('Insert result:', result)
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()

# cleanup
h = {'apikey': cfg.SUPABASE_SERVICE_KEY, 'Authorization': f'Bearer {cfg.SUPABASE_SERVICE_KEY}'}
requests.delete(cfg.SUPABASE_URL + '/rest/v1/influencer_signals', headers=h, params={'stock': 'eq.BTCTEST'})
print('Cleanup done')
