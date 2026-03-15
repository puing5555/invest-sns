# -*- coding: utf-8 -*-
"""안유화 채널 - 남은 ETF/종목 수익률 재계산"""
import urllib.request, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')
import yfinance as yf
from datetime import datetime, timedelta

URL = 'https://arypzhotxflimroprmdk.supabase.co'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'

# 남은 시그널 ID → yfinance ticker
REMAINING = {
    # 푸야오글래스 (글래스 vs 글라스 오타)
    'e6d4f79b-c571-4910-9b3e-f9a5d1a93fb6': ('푸야오글래스', '3606.HK'),
    # TIGER ETFs
    'b5d26826-6476-4c45-9f18-5dc4166a8088': ('뉴럴링크', None),  # 비상장
    '656dda76-3726-43a1-85a3-0e3fd39d514e': ('노나텍', None),  # 확인 필요
    '3b1b6220-300a-4725-bdf5-0e4f990e17ef': ('두나무', None),  # 비상장
    'a7bd541f-80a0-4284-9f19-133b4e0a4266': ('화웨이', None),  # 비상장
    '935e1768-d6aa-4d9e-a396-3a2155489d61': ('TIGER차이나전기차솔루티브', '371460.KS'),
    '051c0946-130d-423f-8ef7-d12fee4a1d01': ('TIGER차이나테크탑10', '396520.KS'),
    '4423db68-2695-4046-ae40-32537de2bbf7': ('TIGER차이나반도체팹리스', '438330.KS'),
    '17cfedc6-d158-4f12-ab4b-85d953a01b74': ('TIGER 차이나 전기차 ETF', '371460.KS'),
    '0e6d3be6-4917-480f-83ff-57c96e71d64e': ('TIGER 차이나테크 탑 10 ETF', '396520.KS'),
    'bf0c3112-3415-4760-8153-9f89bf589e59': ('TIGER 차이나 솔루티브 셀렉티브', '371460.KS'),
}

def api_get(path):
    req = urllib.request.Request(URL + path, headers={
        'apikey': KEY, 'Authorization': 'Bearer ' + KEY
    })
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

def get_price(ticker_symbol, date_str=None):
    try:
        t = yf.Ticker(ticker_symbol)
        if date_str:
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            start = dt - timedelta(days=7)
            end = dt + timedelta(days=7)
            hist = t.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
            if not hist.empty:
                target = dt.strftime('%Y-%m-%d')
                dates = hist.index.strftime('%Y-%m-%d').tolist()
                if target in dates:
                    return float(hist.loc[target:target]['Close'].iloc[0])
                before = hist[hist.index <= str(dt)]
                if not before.empty:
                    return float(before['Close'].iloc[-1])
                return float(hist['Close'].iloc[0])
        else:
            return float(t.fast_info.last_price)
    except Exception as e:
        print(f'  [ERROR] {ticker_symbol}: {e}')
    return None

# First, get published_at for each signal
updated = 0
skipped = 0

for sig_id, (name, yf_ticker) in REMAINING.items():
    if not yf_ticker:
        print(f'SKIP {name} - 비상장/매핑 없음')
        skipped += 1
        continue
    
    # Get signal's video to find published_at
    sig_data = api_get(f'/rest/v1/influencer_signals?select=id,video_id,return_pct&id=eq.{sig_id}')
    if not sig_data:
        print(f'SKIP {name} - 시그널 없음')
        continue
    
    if sig_data[0].get('return_pct') is not None:
        print(f'SKIP {name} - 이미 수익률 있음: {sig_data[0]["return_pct"]}%')
        continue
    
    video_id = sig_data[0]['video_id']
    vid_data = api_get(f'/rest/v1/influencer_videos?select=published_at&id=eq.{video_id}')
    pub_date = vid_data[0]['published_at'] if vid_data else None
    
    print(f'Processing: {name} ({yf_ticker}) pub={pub_date}')
    
    price_at = get_price(yf_ticker, pub_date) if pub_date else None
    time.sleep(0.5)
    price_now = get_price(yf_ticker)
    time.sleep(0.5)
    
    if price_at and price_now:
        ret = round((price_now - price_at) / price_at * 100, 2)
        print(f'  price_at={price_at:.2f} → price_now={price_now:.2f} → return={ret}%')
        
        patch_data = {
            'price_at_signal': round(price_at, 2),
            'price_current': round(price_now, 2),
            'return_pct': ret
        }
        status = api_patch(f'/rest/v1/influencer_signals?id=eq.{sig_id}', patch_data)
        print(f'  DB updated (status={status})')
        updated += 1
    else:
        print(f'  FAILED: price_at={price_at}, price_now={price_now}')

print(f'\n=== 결과 ===')
print(f'업데이트: {updated}')
print(f'스킵(비상장): {skipped}')
