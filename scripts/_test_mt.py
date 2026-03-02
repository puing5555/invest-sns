import requests, json, sys
URL='https://arypzhotxflimroprmdk.supabase.co'
KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
H={'apikey':KEY,'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Prefer':'return=minimal'}

for mt in ['분석','투자','뉴스','교육','결론','보유','리포트','컨센서스','추천','팁','언급','전망','핵심발언','시장전망']:
    r=requests.post(URL+'/rest/v1/influencer_signals',headers=H,json={
        'video_id':'8b8ddea2-1548-4db9-976f-da0b6e877a31',
        'speaker_id':'b07d8758-493a-4a51-9bc5-7ef75f0be67c',
        'stock':'__test__'+mt,'signal':'매수','confidence':'high',
        'mention_type':mt,'market':'KR',
        'review_status':'pending','pipeline_version':'V9.1'
    },timeout=5)
    status='OK' if r.ok else 'FAIL'
    print(f'{mt}: {status}',flush=True)

# cleanup test data
requests.delete(URL+'/rest/v1/influencer_signals?stock=like.__test__%',headers=H,timeout=10)
print('cleanup done',flush=True)
