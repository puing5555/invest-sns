#!/usr/bin/env python3
"""
범용 크립토 코인 추가 스크립트
사용법: python scripts/add_crypto_coin.py

자동 처리:
1. CoinGecko에서 365일 KRW 차트 데이터 수집
2. stockPrices.json 업데이트
3. signal_prices.json에 수익률 계산 (published_at 기준)
4. DB market 오류 시 자동 CRYPTO로 수정
5. stock_tickers.json에 티커 추가
6. public/out 동기화

추가할 코인 목록을 COINS_TO_ADD에 정의하세요.
"""
import json, urllib.request, os, time
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('.env.local')

BASE = Path(__file__).parent.parent / 'data'
ROOT = Path(__file__).parent.parent

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
ANON_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
KEY = SERVICE_ROLE_KEY or ANON_KEY

HEADERS = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── 추가할 코인 목록 ──────────────────────────────────────────────────
# { 'ticker': CoinGecko ID, 'name': 한글명 }
COINS_TO_ADD = {
    'ARB': {'cg_id': 'arbitrum', 'name': '아비트럼'},
}
# ─────────────────────────────────────────────────────────────────────


def fetch_coingecko_chart(cg_id: str, days: int = 365) -> list:
    """CoinGecko KRW 일별 차트 데이터"""
    url = f'https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=krw&days={days}&interval=daily'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    prices = data.get('prices', [])
    result = []
    for ts, price in prices:
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        result.append({'date': dt.strftime('%Y-%m-%d'), 'close': round(price, 6)})
    return result


def get_db_signals(ticker: str) -> list:
    """DB에서 해당 티커 시그널 + 영상 published_at 조회"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals?ticker=eq.{ticker}&select=id,stock,signal,ticker,market,influencer_videos(published_at)"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def fix_db_market(ticker: str):
    """market이 CRYPTO가 아니면 자동 수정"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals?ticker=eq.{ticker}&market=neq.CRYPTO"
    update_data = json.dumps({'market': 'CRYPTO'}).encode('utf-8')
    req = urllib.request.Request(url, data=update_data, method='PATCH', headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        if result:
            print(f"  ⚠️  DB market 자동 수정 ({len(result)}개)")
        return result


def find_price_by_date(price_records: list, target_date: str) -> float:
    """날짜로 가격 조회 (정확히 없으면 가장 가까운 날짜)"""
    for p in price_records:
        if p['date'] == target_date:
            return p['close']
    # 가장 가까운 날짜
    t = datetime.strptime(target_date, '%Y-%m-%d').timestamp()
    closest = min(price_records, key=lambda p: abs(datetime.strptime(p['date'], '%Y-%m-%d').timestamp() - t))
    print(f"  날짜 {target_date} 없음 → {closest['date']} 사용")
    return closest['close']


def add_to_tickers(ticker: str):
    """stock_tickers.json에 티커 추가"""
    path = BASE / 'stock_tickers.json'
    tickers = json.loads(path.read_text(encoding='utf-8'))
    if ticker not in tickers:
        tickers.append(ticker)
        path.write_text(json.dumps(tickers, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  stock_tickers.json에 {ticker} 추가 (총 {len(tickers)}개)")
    else:
        print(f"  stock_tickers.json에 이미 존재: {ticker}")


def sync_to_public_out(*filenames):
    """data/ → public/, out/ 동기화"""
    for fname in filenames:
        src = BASE / fname
        if not src.exists():
            continue
        for dest_dir in ['public', 'out']:
            dst = ROOT / dest_dir / fname
            if dst.exists():
                dst.write_bytes(src.read_bytes())
    print(f"  public/out 동기화 완료: {', '.join(filenames)}")


# ── 메인 ─────────────────────────────────────────────────────────────
sp_path = BASE / 'stockPrices.json'
spp_path = BASE / 'signal_prices.json'
sp = json.loads(sp_path.read_text(encoding='utf-8'))
spp = json.loads(spp_path.read_text(encoding='utf-8'))

for ticker, info in COINS_TO_ADD.items():
    cg_id = info['cg_id']
    name = info['name']
    print(f"\n{'='*50}")
    print(f"[COIN] {name} ({ticker}) | CoinGecko: {cg_id}")
    print('='*50)

    # 1. 차트 데이터 수집
    print("[1] 차트 데이터 수집 중...")
    price_records = fetch_coingecko_chart(cg_id)
    current_price = price_records[-1]['close']
    prev_price = price_records[-2]['close'] if len(price_records) >= 2 else current_price
    change = round(current_price - prev_price, 6)
    change_pct = round((change / prev_price * 100) if prev_price else 0, 2)
    print(f"  현재가: {current_price:,.4f} KRW | 전일대비: {change_pct:+.2f}% | 데이터: {len(price_records)}일")

    # 2. stockPrices.json 업데이트
    sp[ticker] = {
        'currentPrice': current_price,
        'change': change,
        'changePercent': change_pct,
        'currency': 'KRW',
        'market': 'CRYPTO',
        'name': name,
        'prices': price_records
    }
    print(f"  [OK] stockPrices.json 업데이트")

    # 3. DB 시그널 조회 + market 수정
    print("[3] DB 시그널 조회...")
    signals = get_db_signals(ticker)
    print(f"  시그널 {len(signals)}개")
    fix_db_market(ticker)

    # 4. 수익률 계산 (published_at 기준)
    for sig in signals:
        sig_id = sig['id']
        published_at = sig.get('influencer_videos', {}).get('published_at', '')
        if not published_at:
            print(f"  ⚠️  {sig_id} published_at 없음 → 수익률 skip")
            continue
        
        signal_date = published_at[:10]  # YYYY-MM-DD
        signal_price = find_price_by_date(price_records, signal_date)
        return_pct = round((current_price - signal_price) / signal_price * 100, 2)
        
        spp[sig_id] = {
            'price_at_signal': round(signal_price, 6),
            'price_current': round(current_price, 6),
            'return_pct': return_pct,
            'signal_date': signal_date,
            'ticker': ticker,
            'market': 'CRYPTO',
            'currency': 'KRW'
        }
        print(f"  💰 {sig_id[:8]}... | {signal_date} {signal_price:,.4f} KRW → {current_price:,.4f} KRW | 수익률: {return_pct:+.2f}%")

    # 5. 티커 키도 추가 (현재가)
    spp[ticker] = {
        'name': name,
        'ticker': ticker,
        'market': 'CRYPTO',
        'current_price': round(current_price, 6),
        'currency': 'KRW',
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'source': 'coingecko'
    }

    # 6. stock_tickers.json
    add_to_tickers(ticker)

    # 7. cryptoNames.json 업데이트 (stockNames.ts + StockDetailClient.tsx 자동 반영)
    crypto_names_path = BASE / 'cryptoNames.json'
    crypto_names = json.loads(crypto_names_path.read_text(encoding='utf-8'))
    if ticker not in crypto_names:
        crypto_names[ticker] = name
        crypto_names_path.write_text(json.dumps(crypto_names, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  [OK] cryptoNames.json에 {ticker}: {name} 추가")
    else:
        print(f"  cryptoNames.json 이미 존재: {ticker}")

    time.sleep(2)  # CoinGecko 레이트리밋

# JSON 저장
sp_path.write_text(json.dumps(sp, ensure_ascii=False, indent=2), encoding='utf-8')
spp_path.write_text(json.dumps(spp, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n[OK] stockPrices.json 저장 (총 {len(sp)}개)")
print(f"[OK] signal_prices.json 저장 (총 {len(spp)}개)")

# public/out 동기화
sync_to_public_out('stockPrices.json', 'signal_prices.json')

print("\n[DONE] 완료! TS 파일 수정 불필요 (cryptoNames.json 자동 반영)")
print("  다음: npm run build && git commit && git push")
