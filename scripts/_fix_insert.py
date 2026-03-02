import requests, json, time
URL='https://arypzhotxflimroprmdk.supabase.co'
KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
H={'apikey':KEY,'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Prefer':'return=representation'}
SPEAKER_ID='b07d8758-493a-4a51-9bc5-7ef75f0be67c'

# Valid mention types
VALID_MT = {'결론','티저','교육','컨센서스','보유','논거','뉴스','리포트'}
# Map invalid to valid
MT_MAP = {'분석':'논거','투자':'논거','추천':'논거','팁':'논거','언급':'논거','전망':'논거','핵심발언':'논거','시장전망':'논거','긍정':'논거'}

# Load videos
r=requests.get(URL+'/rest/v1/influencer_videos?select=video_id,id&limit=1000',headers=H,timeout=15)
vids={v['video_id']:v['id'] for v in r.json()}

# Load existing signals
r=requests.get(URL+'/rest/v1/influencer_signals?speaker_id=eq.'+SPEAKER_ID+'&select=video_id,stock',headers=H,timeout=15)
existing=set((s['video_id'],s['stock']) for s in r.json())
print(f'Existing: {len(existing)} signals', flush=True)

signals=json.load(open('sesang101_supabase_upload.json','r',encoding='utf-8'))
inserted=0; skipped=0; errors=0

for s in signals:
    vid_uuid=vids.get(s['video_id'])
    if not vid_uuid: continue
    if (vid_uuid,s['stock']) in existing:
        skipped+=1; continue
    
    # Fix mention_type
    mt=s.get('mention_type','논거')
    if mt not in VALID_MT:
        mt=MT_MAP.get(mt,'논거')
    
    # Fix signal
    sig_map={'매수':'매수','긍정':'긍정','중립':'중립','경계':'경계','매도':'매도'}
    sig=sig_map.get(s.get('signal',''),'중립')
    
    # Fix market - N/A not valid
    market=s.get('market','KR')
    if market in ('N/A','','null',None):
        market='OTHER'
    
    # Fix stock - N/A not valid
    stock=s.get('stock','')
    if not stock or stock=='N/A':
        skipped+=1; continue
    
    row={
        'video_id':vid_uuid,'speaker_id':SPEAKER_ID,
        'stock':stock,'ticker':s.get('ticker'),'market':market,
        'mention_type':mt,'signal':sig,'confidence':s.get('confidence','medium'),
        'timestamp':s.get('timestamp'),'key_quote':(s.get('key_quote','') or '')[:1000],
        'reasoning':(s.get('reasoning','') or '')[:2000],
        'review_status':'pending','pipeline_version':'V9.1'
    }
    
    r=requests.post(URL+'/rest/v1/influencer_signals',headers=H,json=row,timeout=10)
    if r.ok:
        inserted+=1; existing.add((vid_uuid,stock))
        print(f'  OK: {stock} ({sig})', flush=True)
    else:
        errors+=1
        # Save full error for debugging
        with open('_last_err.json','w',encoding='utf-8') as f:
            json.dump({'stock':stock,'mt':mt,'sig':sig,'market':market,'status':r.status_code,'error':r.text},f,ensure_ascii=False)
        print(f'  ERR: {stock} - {r.status_code}', flush=True)
    time.sleep(0.05)

print(f'\nDone: inserted={inserted} skipped={skipped} errors={errors} total={len(existing)}', flush=True)
