"""Insert wsaj signals - correct schema"""
import sys, io, os, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

# 1. Create channel
r = requests.get(f"{URL}/rest/v1/influencer_channels?channel_name=eq.월가아재&select=id", headers=H)
if r.ok and r.json():
    channel_id = r.json()[0]['id']
    print(f"Channel exists: {channel_id}")
else:
    r = requests.post(f"{URL}/rest/v1/influencer_channels", headers=H, json={
        'channel_name': '월가아재',
        'channel_handle': '@wsaj',
        'channel_url': 'https://www.youtube.com/@wsaj',
        'platform': 'youtube',
        'description': '매크로/투자교육 + 기업분석'
    })
    if r.ok:
        channel_id = r.json()[0]['id']
        print(f"Channel created: {channel_id}")
    else:
        print(f"Channel create failed: {r.text}")
        sys.exit(1)

# 2. Create or find speaker
r = requests.get(f"{URL}/rest/v1/speakers?name=eq.월가아재&select=id", headers=H)
if r.ok and r.json():
    speaker_id = r.json()[0]['id']
    print(f"Speaker exists: {speaker_id}")
else:
    r = requests.post(f"{URL}/rest/v1/speakers", headers=H, json={
        'name': '월가아재',
        'bio': '월스트리트 출신 데이터과학자, 투자교육/매크로 분석'
    })
    if r.ok:
        speaker_id = r.json()[0]['id']
        print(f"Speaker created: {speaker_id}")
    else:
        print(f"Speaker create failed: {r.text}")
        sys.exit(1)

# 3. Load results
results = json.load(open('wsaj_all_results.json', 'r', encoding='utf-8'))

inserted = 0
failed = 0

for item in results:
    vid = item['video_id']
    title = item['video_title']
    
    # Create video
    r = requests.get(f"{URL}/rest/v1/influencer_videos?video_id=eq.{vid}&select=id", headers=H)
    if r.ok and r.json():
        video_db_id = r.json()[0]['id']
    else:
        r = requests.post(f"{URL}/rest/v1/influencer_videos", headers=H, json={
            'channel_id': channel_id,
            'video_id': vid,
            'title': title,
            'has_subtitle': True,
            'subtitle_language': 'ko',
            'analyzed_at': '2026-03-03T19:30:00Z',
            'pipeline_version': 'v10',
            'signal_count': len(item['signals'])
        })
        if r.ok:
            video_db_id = r.json()[0]['id']
        else:
            print(f"  ❌ Video create failed {vid}: {r.text[:100]}")
            failed += 1
            continue
    
    # Insert signals
    for sig in item['signals']:
        r = requests.post(f"{URL}/rest/v1/influencer_signals", headers=H, json={
            'video_id': video_db_id,
            'speaker_id': speaker_id,
            'stock': sig['stock'],
            'ticker': sig['ticker'],
            'market': 'US',
            'mention_type': '결론',
            'signal': sig['signal_type'],
            'confidence': 'very_high' if sig.get('confidence', 7) >= 9 else 'high' if sig.get('confidence', 7) >= 7 else 'medium' if sig.get('confidence', 7) >= 5 else 'low',
            'timestamp': sig['timestamp'],
            'key_quote': sig['key_quote'],
            'reasoning': sig['reasoning'],
            'review_status': 'pending',
            'pipeline_version': 'v10'
        })
        if r.ok:
            inserted += 1
            print(f"  ✅ {sig['stock']} ({sig['signal_type']}) - {vid}")
        else:
            failed += 1
            print(f"  ❌ {sig['stock']}: {r.text[:150]}")

print(f"\n=== 결과: {inserted} inserted, {failed} failed ===")
