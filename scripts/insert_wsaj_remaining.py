"""Insert selected wsaj remaining signals"""
import sys, io, os, json, requests, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

CHANNEL_ID = 'd4639050-bebf-41d4-9786-93005fb80b85'
SPEAKER_ID = 'a80f6cdf-e53a-42a9-95ea-1c5ba9c7a986'

# Only insert clear stock-specific signals
TO_INSERT = [
    {
        'video_id': '7x3HE_uXttI',
        'title': 'AI 수혜주 파헤치기',
        'stock': '엔비디아', 'ticker': 'NVDA', 'signal_type': '중립',
        'key_quote': 'AI 수혜주로 가장 관심을 많이 받는 건 엔비디아, 숫자로 따져보면 현재 밸류에이션이 싸지는 않다',
        'reasoning': 'AI 반도체 선두 기업으로 생성형 AI 붐의 직접 수혜주이나, 밸류에이션이 이미 높아 추가 상승 여력 제한적이라고 분석',
        'timestamp': '01:13', 'confidence': 'high'
    },
    {
        'video_id': '57NbdmLvy6I',
        'title': '노보 노디스크 & 일라이 릴리',
        'stock': '노보 노디스크', 'ticker': 'NVO', 'signal_type': '긍정',
        'key_quote': '비만 치료제 시장이 더 빠르게 성장할 수 있고, 노보 노디스크가 이 시장에서 확고한 선두',
        'reasoning': '비만 치료제 위고비/오젬픽의 시장 성장성과 노보 노디스크의 경쟁 우위를 긍정적으로 평가',
        'timestamp': '14:34', 'confidence': 'high'
    }
]

for item in TO_INSERT:
    vid = item['video_id']
    # Get upload date
    try:
        result = subprocess.run(
            ['python', '-m', 'yt_dlp', '--print', '%(upload_date)s', f'https://youtube.com/watch?v={vid}', '--no-download'],
            capture_output=True, text=True, encoding='utf-8', timeout=30
        )
        date_str = result.stdout.strip()
        pub_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}" if date_str and len(date_str) == 8 else None
    except:
        pub_date = None
    
    print(f"Video {vid}: pub_date={pub_date}")
    
    # Create video
    r = requests.get(f"{URL}/rest/v1/influencer_videos?video_id=eq.{vid}&select=id", headers=H)
    if r.ok and r.json():
        video_db_id = r.json()[0]['id']
    else:
        r = requests.post(f"{URL}/rest/v1/influencer_videos", headers=H, json={
            'channel_id': CHANNEL_ID, 'video_id': vid, 'title': item['title'],
            'published_at': pub_date, 'has_subtitle': True, 'subtitle_language': 'ko',
            'analyzed_at': '2026-03-03T20:00:00Z', 'pipeline_version': 'v10', 'signal_count': 1
        })
        if r.ok:
            video_db_id = r.json()[0]['id']
        else:
            print(f"  Video create FAIL: {r.text[:100]}")
            continue
    
    # Insert signal
    r = requests.post(f"{URL}/rest/v1/influencer_signals", headers=H, json={
        'video_id': video_db_id, 'speaker_id': SPEAKER_ID,
        'stock': item['stock'], 'ticker': item['ticker'], 'market': 'US',
        'mention_type': '결론', 'signal': item['signal_type'],
        'confidence': item['confidence'], 'timestamp': item['timestamp'],
        'key_quote': item['key_quote'], 'reasoning': item['reasoning'],
        'review_status': 'pending', 'pipeline_version': 'v10'
    })
    if r.ok:
        print(f"  ✅ {item['stock']} ({item['signal_type']}) inserted")
    else:
        print(f"  ❌ {r.text[:150]}")

print("\nDone!")
