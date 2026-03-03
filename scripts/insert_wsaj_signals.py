"""Insert wsaj 기업해부학 7개 시그널 into Supabase"""
import sys, io, os, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
HEADERS = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

# Channel info for wsaj
CHANNEL_NAME = '월가아재'
YT_CHANNEL_ID = 'UCiV9Y_RbLHETm6FNm6RPzrQ'  # Will look up

# Video publish dates (approximate from content)
VIDEO_DATES = {
    'oDfnMrrRfl8': '2023-01-15',  # Nvidia 밸류에이션
    'AQ2z2ZCBFa4': '2023-02-15',  # Nvidia AI/메타버스
    '5fhbkQ2Qidc': '2023-09-01',  # 대가가 안 판 이유
    'OWkw56VyeUM': '2023-08-15',  # 대가가 판 이유
    'liP35sqr9aU': '2023-08-25',  # 실적 서프라이즈
    'l9suWlP7U68': '2023-09-15',  # 테슬라=AI대장주
    '_Ex0vR_1Ekg': '2023-10-01',  # 테슬라 목표가
}

SIGNAL_MAP = {
    '매수': '매수', '긍정': '긍정', '중립': '중립', '경계': '경계', '매도': '매도'
}

def get_or_create_channel():
    """Find or create wsaj channel"""
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_channels?channel_name=eq.{CHANNEL_NAME}&select=id',
        headers=HEADERS
    )
    if r.ok and r.json():
        return r.json()[0]['id']
    
    # Create channel
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/influencer_channels',
        headers=HEADERS,
        json={
            'channel_name': CHANNEL_NAME,
            'youtube_channel_id': YT_CHANNEL_ID,
            'channel_url': 'https://www.youtube.com/@wsaj',
            'description': '매크로/투자교육 + 기업분석'
        }
    )
    if r.ok:
        return r.json()[0]['id']
    print(f"Failed to create channel: {r.text}")
    return None

def get_or_create_speaker(channel_id):
    """Find or create speaker"""
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_speakers?channel_id=eq.{channel_id}&speaker_name=eq.{CHANNEL_NAME}&select=id',
        headers=HEADERS
    )
    if r.ok and r.json():
        return r.json()[0]['id']
    
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/influencer_speakers',
        headers=HEADERS,
        json={
            'channel_id': channel_id,
            'speaker_name': CHANNEL_NAME,
            'speaker_role': 'host'
        }
    )
    if r.ok:
        return r.json()[0]['id']
    print(f"Failed to create speaker: {r.text}")
    return None

def get_or_create_video(channel_id, video_id, title, published_at):
    """Find or create video"""
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.{video_id}&select=id',
        headers=HEADERS
    )
    if r.ok and r.json():
        return r.json()[0]['id']
    
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/influencer_videos',
        headers=HEADERS,
        json={
            'channel_id': channel_id,
            'video_id': video_id,
            'title': title,
            'published_at': published_at,
            'has_subtitle': True,
            'subtitle_language': 'ko',
            'analyzed_at': '2026-03-03T19:30:00Z',
            'pipeline_version': 'v10',
            'signal_count': 1
        }
    )
    if r.ok:
        return r.json()[0]['id']
    print(f"Failed to create video: {r.text}")
    return None

def insert_signal(video_db_id, speaker_id, signal):
    """Insert signal"""
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/influencer_signals',
        headers=HEADERS,
        json={
            'video_id': video_db_id,
            'speaker_id': speaker_id,
            'stock_name': signal['stock'],
            'stock_ticker': signal['ticker'],
            'signal_type': signal['signal_type'],
            'key_quote': signal['key_quote'],
            'reasoning': signal['reasoning'],
            'timestamp': signal['timestamp'],
            'confidence': signal.get('confidence', 7),
            'review_status': 'pending'
        }
    )
    return r.ok, r.text

def main():
    results = json.load(open('wsaj_all_results.json', 'r', encoding='utf-8'))
    
    channel_id = get_or_create_channel()
    if not channel_id:
        print("Failed to get channel")
        return
    print(f"Channel ID: {channel_id}")
    
    speaker_id = get_or_create_speaker(channel_id)
    if not speaker_id:
        print("Failed to get speaker")
        return
    print(f"Speaker ID: {speaker_id}")
    
    inserted = 0
    failed = 0
    
    for item in results:
        vid = item['video_id']
        title = item['video_title']
        pub_date = VIDEO_DATES.get(vid, '2023-06-01')
        
        video_db_id = get_or_create_video(channel_id, vid, title, pub_date)
        if not video_db_id:
            print(f"  ❌ Failed to create video: {vid}")
            failed += 1
            continue
        
        for sig in item['signals']:
            ok, text = insert_signal(video_db_id, speaker_id, sig)
            if ok:
                inserted += 1
                print(f"  ✅ {sig['stock']} ({sig['signal_type']}) - {vid}")
            else:
                failed += 1
                print(f"  ❌ {sig['stock']}: {text[:100]}")
    
    print(f"\n=== 결과: {inserted} inserted, {failed} failed ===")

if __name__ == '__main__':
    main()
