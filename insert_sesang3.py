import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
h = {'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

SPEAKER_ID = 'b9496a5f-06fa-47eb-bc2d-47060b095534'

signals = [
    # Video 1: 트럼프의 선택에 시장이 패닉하는 이유
    {
        'video_id': '34eea767-edf0-45c7-b527-ebfbe86d3b9f',
        'speaker_id': SPEAKER_ID,
        'stock': '금 (GLD)',
        'ticker': 'GLD',
        'market': 'US',
        'mention_type': '논거',
        'signal': '경계',
        'confidence': 'medium',
        'key_quote': '이렇게 금이랑은 같은 귀금속 시장이 과열되었다가 브레이크가 걸리고',
        'reasoning': '케빈 워시의 강한 달러 정책으로 인해 귀금속 시장에 브레이크가 걸렸다고 언급',
        'timestamp': '08:45',
        'review_status': 'pending',
        'pipeline_version': 'V10.7'
    },
    {
        'video_id': '34eea767-edf0-45c7-b527-ebfbe86d3b9f',
        'speaker_id': SPEAKER_ID,
        'stock': '비트코인 (BTC)',
        'ticker': 'BTC',
        'market': 'CRYPTO',
        'mention_type': '논거',
        'signal': '경계',
        'confidence': 'high',
        'key_quote': '비트코인 시장은 안 그래도 이제 코인베이스랑 뭐 전통 금융 애들이랑 싸우면서 클레티 법안 통과가 무산돼서 좀 이렇게 비살 비질거리고 있었는데',
        'reasoning': '클레티 법안 무산과 케빈 워시 지명으로 비트코인 시장이 어려운 상황에 처했다고 분석',
        'timestamp': '09:15',
        'review_status': 'pending',
        'pipeline_version': 'V10.7'
    },
    # Video 3: 제2의 팔란티어, 알고도 10배 못 먹는 이유
    {
        'video_id': 'c186fc91-b734-40a4-a76e-20853b3da15e',
        'speaker_id': SPEAKER_ID,
        'stock': '팔란티어 (PLTR)',
        'ticker': 'PLTR',
        'market': 'US',
        'mention_type': '논거',
        'signal': '긍정',
        'confidence': 'medium',
        'key_quote': '비트코인, 팔란티어, 아이렌 같은 종목을 알고도 10열배의 수익률을 못 보는 이유',
        'reasoning': '10배 수익률 가능 종목으로 언급하며 장기 보유의 중요성 강조',
        'timestamp': '01:45',
        'review_status': 'pending',
        'pipeline_version': 'V10.7'
    },
    {
        'video_id': 'c186fc91-b734-40a4-a76e-20853b3da15e',
        'speaker_id': SPEAKER_ID,
        'stock': '비트코인 (BTC)',
        'ticker': 'BTC',
        'market': 'CRYPTO',
        'mention_type': '논거',
        'signal': '긍정',
        'confidence': 'high',
        'key_quote': '금리나 사이클과 AI와 비트코인 네러티브의 추위만 잘 지켜보면서',
        'reasoning': 'AI와 함께 강력한 네러티브로 언급하며 투자 기회로 평가',
        'timestamp': '12:30',
        'review_status': 'pending',
        'pipeline_version': 'V10.7'
    },
    {
        'video_id': 'c186fc91-b734-40a4-a76e-20853b3da15e',
        'speaker_id': SPEAKER_ID,
        'stock': '아이렌 (IREN)',
        'ticker': 'IREN',
        'market': 'US',
        'mention_type': '직접추천',
        'signal': '매수',
        'confidence': 'high',
        'key_quote': '제가 4월 초에 처음 투자한 아이레는 6개월 만에 거의 아홉배가 올랐지만',
        'reasoning': '직접 투자하여 6개월간 9배 수익률을 달성한 성공 사례로 제시',
        'timestamp': '00:25',
        'review_status': 'pending',
        'pipeline_version': 'V10.7'
    },
]

print(f"Inserting {len(signals)} signals...")
for s in signals:
    r = requests.post(f'{url}/rest/v1/influencer_signals', headers=h, json=s)
    if r.status_code in (200, 201):
        inserted = r.json()
        rid = inserted[0]['id'] if isinstance(inserted, list) else inserted['id']
        print(f"  ✅ {s['stock']} | {s['signal']} | id: {rid}")
    else:
        print(f"  ❌ {s['stock']} | {r.status_code} | {r.text[:200]}")

print("\nDone!")
