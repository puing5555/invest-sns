import requests, json
URL='https://arypzhotxflimroprmdk.supabase.co'
KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
H={'apikey':KEY,'Authorization':'Bearer '+KEY}
r=requests.get(URL+'/rest/v1/influencer_signals?select=mention_type&limit=200',headers=H,timeout=10)
types=list(set(d['mention_type'] for d in r.json()))
with open('_mt_result.json','w',encoding='utf-8') as f:
    json.dump(types,f,ensure_ascii=False,indent=2)
print('saved')
