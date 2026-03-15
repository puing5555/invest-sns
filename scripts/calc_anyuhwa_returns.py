# -*- coding: utf-8 -*-
"""안유화 채널 시그널 수익률 재계산 (중국 종목 포함)"""
import urllib.request, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://arypzhotxflimroprmdk.supabase.co'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
CHANNEL_ID = '6d6817ca-76ab-484e-ad7e-b537921c3d25'

# yfinance ticker 매핑
TICKER_MAP = {
    # 중국/HK
    'BYD': '1211.HK',
    'CATL': '300750.SZ',
    'SMIC': '0981.HK',
    '지리자동차': '0175.HK',
    '푸야오글라스': '3606.HK',
    '화웨이': None,  # 비상장
    '샤오미': '1810.HK',
    '텐센트': '0700.HK',
    '알리바바': '9988.HK',
    # 한국
    '삼성전자': '005930.KS',
    '현대자동차': '005380.KS',
    '네이버': '035420.KS',
    '카카오': '035720.KS',
    '노나텍': None,  # 확인 필요
    # 미국
    '테슬라': 'TSLA',
    # ETF - ticker가 없으면 이름으로 매핑 시도
    'TIGER 차이나전기차솔루티브': '371460.KS',
    'TIGER 차이나테크탑10': '396520.KS',
    'TIGER 차이나반도체팹리스': '438330.KS',
    'TIGER 차이나 전기차 ETF': '371460.KS',
    'TIGER 차이나테크 탑 10 ETF': '396520.KS',
    'TIGER 차이나 솔루티브 셀렉티브': None,  # 확인 필요
    'TIGER차이나테크탑10': '396520.KS',
    'TIGER차이나전기차솔루티브': '371460.KS',
    'TIGER차이나반도체팹리스': '438330.KS',
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
    """yfinance로 가격 조회. date_str이 있으면 해당일 종가, 없으면 현재가"""
    import yfinance as yf
    try:
        t = yf.Ticker(ticker_symbol)
        if date_str:
            from datetime import datetime, timedelta
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            start = dt - timedelta(days=5)
            end = dt + timedelta(days=5)
            hist = t.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
            if not hist.empty:
                # 가장 가까운 날짜
                target = dt.strftime('%Y-%m-%d')
                if target in hist.index.strftime('%Y-%m-%d').tolist():
                    return float(hist.loc[target:target]['Close'].iloc[0])
                # 이전 가장 가까운 날
                before = hist[hist.index <= str(dt)]
                if not before.empty:
                    return float(before['Close'].iloc[-1])
                return float(hist['Close'].iloc[0])
        else:
            return float(t.fast_info.last_price)
    except Exception as e:
        print(f'  [ERROR] {ticker_symbol}: {e}')
    return None

# 1. Get videos
videos = api_get(f'/rest/v1/influencer_videos?select=id,video_id,title,published_at&channel_id=eq.{CHANNEL_ID}')
print(f'안유화 채널 영상: {len(videos)}개')

# 2. Get all signals
all_signals = []
for v in videos:
    sigs = api_get(f'/rest/v1/influencer_signals?select=id,stock,ticker,market,signal,price_at_signal,price_current,return_pct&video_id=eq.{v["id"]}')
    for s in sigs:
        s['published_at'] = v.get('published_at')
    all_signals.extend(sigs)

missing = [s for s in all_signals if s.get('return_pct') is None]
print(f'전체 시그널: {len(all_signals)}개, 수익률 없음: {len(missing)}개\n')

# 3. Calculate returns
updated = 0
failed = []

for s in missing:
    stock = s['stock']
    ticker = s.get('ticker')
    pub_date = s.get('published_at')
    
    # Resolve yfinance ticker
    yf_ticker = None
    if ticker:
        # DB에 ticker가 있으면 변환
        if ticker in ('005930', '005380', '035420', '035720'):
            yf_ticker = ticker + '.KS'
        elif ticker in ('300750',):
            yf_ticker = ticker + '.SZ'
        elif ticker in ('002594',):
            yf_ticker = '1211.HK'  # BYD A주 → HK
        else:
            yf_ticker = ticker
    
    if not yf_ticker:
        yf_ticker = TICKER_MAP.get(stock)
    
    if not yf_ticker:
        print(f'  SKIP {stock} - ticker 매핑 없음')
        failed.append({'id': s['id'], 'stock': stock, 'reason': 'no ticker'})
        continue
    
    print(f'  Processing: {stock} ({yf_ticker}) pub={pub_date}')
    
    # Get price at signal date
    price_at = get_price(yf_ticker, pub_date) if pub_date else None
    time.sleep(0.5)
    
    # Get current price
    price_now = get_price(yf_ticker)
    time.sleep(0.5)
    
    if price_at and price_now:
        ret = round((price_now - price_at) / price_at * 100, 2)
        print(f'    price_at={price_at:.2f} → price_now={price_now:.2f} → return={ret}%')
        
        # Update DB
        patch_data = {
            'price_at_signal': round(price_at, 2),
            'price_current': round(price_now, 2),
            'return_pct': ret
        }
        status = api_patch(f'/rest/v1/influencer_signals?id=eq.{s["id"]}', patch_data)
        print(f'    DB updated (status={status})')
        updated += 1
    else:
        reason = f'price_at={price_at}, price_now={price_now}'
        print(f'    FAILED: {reason}')
        failed.append({'id': s['id'], 'stock': stock, 'reason': reason})

print(f'\n=== 결과 ===')
print(f'업데이트: {updated}/{len(missing)}')
print(f'실패: {len(failed)}')
for f in failed:
    print(f'  - {f["stock"]}: {f["reason"]}')
