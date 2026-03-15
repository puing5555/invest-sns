# -*- coding: utf-8 -*-
"""중국 종목 ticker null → 정확한 ticker로 업데이트"""
import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://arypzhotxflimroprmdk.supabase.co'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'

CHINA_MAP = {
    'BYD': ('1211.HK', 'OTHER'),
    'CATL': ('300750.SZ', 'OTHER'),
    'SMIC': ('0981.HK', 'OTHER'),
    '지리자동차': ('0175.HK', 'OTHER'),
    '푸야오글라스': ('3606.HK', 'OTHER'),
    '푸야오글래스': ('3606.HK', 'OTHER'),
    '샤오미': ('1810.HK', 'OTHER'),
    '텐센트': ('0700.HK', 'OTHER'),
    '알리바바': ('9988.HK', 'OTHER'),
}

# Also fix ETF tickers
ETF_MAP = {
    '타이거차이나전기차솔루티브': ('371460.KS', 'ETF'),
    '타이거차이나테크탑10': ('396520.KS', 'ETF'),
    '타이거차이나반도체팹리스': ('438330.KS', 'ETF'),
    '타이거차이나반도체팹세트': ('438330.KS', 'ETF'),
    '타이거차이나반도체팩세트': ('438330.KS', 'ETF'),
    '타이거차이나휴먼노이드로봇': ('490490.KS', 'ETF'),
    '타이거차이나휴먼로봇': ('490490.KS', 'ETF'),
    '타이거차이나테크톱10': ('396520.KS', 'ETF'),
    'TIGER차이나전기차솔루티브': ('371460.KS', 'ETF'),
    'TIGER차이나테크탑10': ('396520.KS', 'ETF'),
    'TIGER차이나반도체팹리스': ('438330.KS', 'ETF'),
    'TIGER 차이나 전기차 ETF': ('371460.KS', 'ETF'),
    'TIGER 차이나테크 탑 10 ETF': ('396520.KS', 'ETF'),
    'TIGER 차이나 솔루티브 셀렉티브': ('371460.KS', 'ETF'),
    'TIGER 차이나 증권 ETF': ('371450.KS', 'ETF'),
    '타이거 차이나전기차솔루티브': ('371460.KS', 'ETF'),
    '타이거 차이나테크탑10': ('396520.KS', 'ETF'),
    '타이거 차이나반도체팹리스': ('438330.KS', 'ETF'),
    '타이거 차이나 증권 ETF': ('371450.KS', 'ETF'),
    '타이거 차이나테크 탑 10 ETF': ('396520.KS', 'ETF'),
    '타이거 차이나 전기차 솔렉티브': ('371460.KS', 'ETF'),
    '타이거차이나테크 탑 10': ('396520.KS', 'ETF'),
}

ALL_MAP = {**CHINA_MAP, **ETF_MAP}

def api_get(path):
    req = urllib.request.Request(URL + path, headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def api_patch(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(URL + path, data=body, method='PATCH', headers={
        'apikey': KEY, 'Authorization': 'Bearer ' + KEY,
        'Content-Type': 'application/json', 'Prefer': 'return=minimal'
    })
    with urllib.request.urlopen(req) as resp:
        return resp.status

# Get all signals with null ticker
signals = api_get('/rest/v1/influencer_signals?select=id,stock,ticker,market&ticker=is.null&order=stock')
print(f'ticker=null 시그널: {len(signals)}개')

updated = 0
for s in signals:
    stock = s['stock']
    if stock in ALL_MAP:
        ticker, market = ALL_MAP[stock]
        patch = {'ticker': ticker, 'market': market}
        status = api_patch(f'/rest/v1/influencer_signals?id=eq.{s["id"]}', patch)
        print(f'  {stock} -> ticker={ticker}, market={market} (status={status})')
        updated += 1

# Also fix BYD with ticker=002594 (A-share) -> 1211.HK (H-share, yfinance compatible)
byd_a = api_get('/rest/v1/influencer_signals?select=id,stock,ticker&stock=eq.BYD&ticker=eq.002594')
for s in byd_a:
    status = api_patch(f'/rest/v1/influencer_signals?id=eq.{s["id"]}', {'ticker': '1211.HK'})
    print(f'  BYD 002594 -> 1211.HK (status={status})')
    updated += 1

# Fix CATL with ticker=300750 (missing .SZ)
catl = api_get('/rest/v1/influencer_signals?select=id,stock,ticker&stock=eq.CATL&ticker=eq.300750')
for s in catl:
    status = api_patch(f'/rest/v1/influencer_signals?id=eq.{s["id"]}', {'ticker': '300750.SZ'})
    print(f'  CATL 300750 -> 300750.SZ (status={status})')
    updated += 1

print(f'\n=== 업데이트: {updated}개 ===')
