# -*- coding: utf-8 -*-
"""
수익률 누락 시그널 자동 수정 스크립트
====================================
signal_prices.json에 UUID 키가 없는 시그널을 찾아서 return_pct 계산 후 추가.

사용법:
  python scripts/fix_missing_returns.py [--dry-run]
"""
import sys
import io
import os
import json
import time
import urllib.request
import urllib.error
import shutil
from datetime import datetime, date
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent
SIGNAL_PRICES_FILE = PROJECT_ROOT / "data" / "signal_prices.json"
PUBLIC_PRICES_FILE = PROJECT_ROOT / "public" / "signal_prices.json"

# .env.local 로드
env_path = PROJECT_ROOT / ".env.local"
if env_path.exists():
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

SUPA_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
SUPA_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

YAHOO_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 종목명 → ticker 매핑 테이블
STOCK_TICKER_MAP = {
    '삼성전자': '005930.KS',
    '엔비디아': 'NVDA',
    'NVIDIA': 'NVDA',
    '테슬라': 'TSLA',
    '알파벳': 'GOOGL',
    '버크셔 해서웨이': 'BRK-B',
    'Berkshire Hathaway': 'BRK-B',
    'ARM홀딩스': 'ARM',
    'BYD': 'BYDDY',
    '1211': 'BYDDY',  # BYD HK ticker -> OTC
    '아이온큐': 'IONQ',
    '뱅크오브아메리카': 'BAC',
    'SPG': 'SPG',
    'GE버노바': 'GEV',
    # 한국 종목
    'SK하이닉스': '000660.KS',
    '현대차': '005380.KS',
    'LG에너지솔루션': '373220.KS',
    'PSK': '031980.KS',
    '한미반도체': '042700.KS',
    '삼성SDI': '006400.KS',
    '심텍': '222800.KS',
    '솔브레인': '036830.KS',
    # 추가 종목들
    '케이씨티': None,  # 매핑 불가
    '팔란티어': 'PLTR',
    '팔란티어테크놀로지스': 'PLTR',
    'TSLA': 'TSLA',
    'NVDA': 'NVDA',
    'GOOGL': 'GOOGL',
    'ARM': 'ARM',
    'IONQ': 'IONQ',
    'BAC': 'BAC',
    'GEV': 'GEV',
    'PLTR': 'PLTR',
    '코스코': None,  # 매핑 불가 (섹터)
    '하이닉스': '000660.KS',
    'TCK': 'TCK',
    'TCK.A': 'TCK',
    '다이아몬드백 에너지': 'FANG',
    '다이아몬드백에너지': 'FANG',
    # 추가 국내
    '현대자동차': '005380.KS',
    'LG에너지': '373220.KS',
    '이오테크닉스': '039030.KS',
    '피에스케이': '031980.KS',
    '두산에너빌리티': '034020.KS',
    '한화에어로스페이스': '012450.KS',
    '스코디자인': None,
    'SK텔레콤': '017670.KS',
    '카카오': '035720.KS',
    'NAVER': '035420.KS',
    '네이버': '035420.KS',
    '크래프톤': '259960.KS',
    '셀트리온': '068270.KS',
    '포스코홀딩스': '005490.KS',
    '고려아연': '010130.KS',
    '에코프로비엠': '247540.KS',
    '에코프로': '086520.KS',
    '포스코퓨처엠': '003670.KS',
    'KB금융': '105560.KS',
    '신한지주': '055550.KS',
    'HD현대중공업': '329180.KS',
    'LG화학': '051910.KS',
    '삼성바이오로직스': '207940.KS',
    '이노비코전자': None,
    '하이브': '352820.KS',
    '아스코': None,
    '비비코전자': None,
    '비스코자인': None,
}

# 매핑 불가 섹터/ETF 키워드
UNMAPPABLE_KEYWORDS = [
    '방산', '우주항공', '비트코인', '이더리움', '암호화폐', '코인', '원자재',
    '금', '달러', '채권', '섹터', 'ETF', 'KODEX', 'TIGER', 'KBSTAR',
    '방위산업', '수소', '전기차', '반도체ETF', '리츠', '부동산',
    '바이오ETF', '인덱스', 'S&P', '나스닥', '코스피', '코스닥',
]


def supabase_fetch(path):
    req = urllib.request.Request(
        f'{SUPA_URL}/rest/v1/{path}',
        headers={'apikey': SUPA_KEY, 'Authorization': f'Bearer {SUPA_KEY}'}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def is_unmappable(stock_name: str) -> bool:
    if not stock_name:
        return True
    for kw in UNMAPPABLE_KEYWORDS:
        if kw in stock_name:
            return True
    return False


def find_ticker(stock_name: str, ticker_from_db: str) -> str | None:
    """종목명 또는 DB ticker로 Yahoo Finance 심볼 결정"""
    # DB에 이미 ticker가 있으면 우선 사용 (단, 종목명 매핑이 있으면 우선)
    if stock_name and stock_name.strip() in STOCK_TICKER_MAP:
        mapped = STOCK_TICKER_MAP[stock_name.strip()]
        if mapped:
            return mapped

    if ticker_from_db and ticker_from_db.strip():
        t = ticker_from_db.strip()
        # 매핑 테이블에서 ticker로도 확인
        if t in STOCK_TICKER_MAP:
            mapped = STOCK_TICKER_MAP[t]
            if mapped:
                return mapped
        # 6자리 숫자면 한국 주식
        if t.isdigit() and len(t) == 6:
            return f"{t}.KS"  # KS/KQ는 나중에 시도
        # 4자리 이하 숫자는 HK/China - 매핑 불가 처리
        if t.isdigit() and len(t) <= 4:
            return None
        return t

    # 종목명으로 매핑 (이미 위에서 체크했지만 혹시 모를 경우)
    if stock_name:
        t = STOCK_TICKER_MAP.get(stock_name.strip())
        if t:
            return t

    return None


def fetch_yahoo_price(symbol: str, retries: int = 3) -> float | None:
    """현재가 수집"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": YAHOO_UA})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.load(resp)
            result = data.get("chart", {}).get("result")
            if not result:
                return None
            meta = result[0].get("meta", {})
            price = meta.get("regularMarketPrice")
            return float(price) if price else None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"    [429 rate limit] {symbol} → 60초 대기...")
                time.sleep(60)
            elif e.code == 404:
                return None
            else:
                print(f"    [HTTP {e.code}] {symbol}")
                if attempt < retries - 1:
                    time.sleep(3)
        except Exception as ex:
            if attempt < retries - 1:
                time.sleep(3)
    return None


def fetch_yahoo_historical(symbol: str, date_str: str) -> float | None:
    """지정 날짜의 종가 수집"""
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        period1 = int(dt.timestamp())
        period2 = period1 + 7 * 86400  # 7일 범위 (주말/공휴일 처리)
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            f"?interval=1d&period1={period1}&period2={period2}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": YAHOO_UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        result = data.get("chart", {}).get("result")
        if not result:
            return None
        closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        closes = [c for c in closes if c is not None]
        if closes:
            return float(closes[0])
        return None
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"    [429 rate limit] 역사 데이터 {symbol} → 60초 대기...")
            time.sleep(60)
        return None
    except Exception as ex:
        return None


def try_kr_ticker(ticker_base: str) -> tuple[str | None, float | None]:
    """한국 주식 KS/KQ 순서로 시도, 성공한 symbol과 price 반환"""
    if '.' in ticker_base:
        # 이미 suffix 있음
        price = fetch_yahoo_price(ticker_base)
        return (ticker_base, price) if price else (None, None)

    # 6자리 숫자인 경우
    if ticker_base.isdigit() and len(ticker_base) == 6:
        for suffix in ['.KS', '.KQ']:
            sym = f"{ticker_base}{suffix}"
            price = fetch_yahoo_price(sym)
            if price:
                return sym, price
            time.sleep(1)
        return None, None

    return ticker_base, fetch_yahoo_price(ticker_base)


def main():
    dry_run = '--dry-run' in sys.argv
    print(f"\n{'='*60}")
    print(f"🔧 수익률 누락 시그널 자동 수정")
    if dry_run:
        print(f"   [DRY RUN 모드 - 실제 저장 안 함]")
    print(f"{'='*60}")

    # 1. signal_prices.json 로드
    with open(SIGNAL_PRICES_FILE, encoding='utf-8') as f:
        prices = json.load(f)

    uuid_returns = set(k for k in prices if len(k) == 36 and '-' in k)
    print(f"\n기존 UUID 수익률 엔트리: {len(uuid_returns)}건")

    # 2. DB에서 시그널 + 영상 정보 로드
    print("\nDB 데이터 로딩 중...")
    sigs = supabase_fetch('influencer_signals?select=id,stock,signal,ticker,video_id&limit=2000')
    vids = supabase_fetch('influencer_videos?select=id,published_at,channel_id&limit=3000')
    channels = supabase_fetch('influencer_channels?select=id,channel_name&limit=100')

    vid_pub_map = {v['id']: v.get('published_at', '') for v in vids}
    vid_ch_map = {v['id']: v.get('channel_id', '') for v in vids}
    ch_name_map = {c['id']: c.get('channel_name', '') for c in channels}

    print(f"시그널: {len(sigs)}개, 영상: {len(vids)}개, 채널: {len(channels)}개")

    # 3. 누락된 시그널 필터링
    missing = [s for s in sigs if s['id'] not in uuid_returns]
    print(f"\n누락 시그널: {len(missing)}건")

    # 4. 종목별 그룹화 (같은 종목은 한 번만 가격 수집)
    # symbol_cache: symbol -> (current_price, is_kr)
    symbol_cache = {}

    success_count = 0
    skip_count = 0
    fail_count = 0
    new_entries = {}

    for i, sig in enumerate(missing):
        sig_id = sig['id']
        stock_name = sig.get('stock', '').strip()
        db_ticker = sig.get('ticker', '').strip() if sig.get('ticker') else ''
        video_id = sig.get('video_id', '')

        pub_date = vid_pub_map.get(video_id, '')
        ch_id = vid_ch_map.get(video_id, '')
        ch_name = ch_name_map.get(ch_id, 'unknown')

        print(f"\n[{i+1}/{len(missing)}] {stock_name} (ch={ch_name}, pub={pub_date[:10] if pub_date else 'N/A'})")

        # 매핑 불가 종목 스킵
        if is_unmappable(stock_name):
            print(f"  ⏩ 매핑 불가 종목 스킵: {stock_name}")
            skip_count += 1
            continue

        # Ticker 결정
        yahoo_sym = find_ticker(stock_name, db_ticker)
        if not yahoo_sym:
            print(f"  ⏩ ticker 매핑 없음 → 스킵")
            skip_count += 1
            continue

        print(f"  ticker: {yahoo_sym}")

        # 현재가 수집 (캐시 활용)
        if yahoo_sym in symbol_cache:
            current_price, resolved_sym = symbol_cache[yahoo_sym]
        else:
            # 한국 주식 처리
            base_sym = yahoo_sym.replace('.KS', '').replace('.KQ', '')
            if base_sym.isdigit() and len(base_sym) == 6:
                resolved_sym, current_price = try_kr_ticker(base_sym)
            else:
                current_price = fetch_yahoo_price(yahoo_sym)
                resolved_sym = yahoo_sym

            if current_price is None and '.KS' not in yahoo_sym and not yahoo_sym.isdigit():
                pass  # US 종목 실패

            symbol_cache[yahoo_sym] = (current_price, resolved_sym)
            time.sleep(1)  # 레이트리밋

        if current_price is None:
            print(f"  ❌ 현재가 수집 실패 ({resolved_sym})")
            fail_count += 1
            continue

        print(f"  현재가: {current_price}")

        # 발행일 기준 역사적 가격 수집
        price_at_signal = None
        if pub_date and resolved_sym:
            pub_date_str = pub_date[:10]
            hist_key = f"{resolved_sym}@{pub_date_str}"
            if hist_key in symbol_cache:
                price_at_signal = symbol_cache[hist_key]
            else:
                price_at_signal = fetch_yahoo_historical(resolved_sym, pub_date_str)
                symbol_cache[hist_key] = price_at_signal
                time.sleep(1)

        if price_at_signal is None:
            print(f"  ⚠️  역사적 가격 없음 (pub={pub_date[:10] if pub_date else 'N/A'}) → 수익률 계산 불가")
            fail_count += 1
            continue

        print(f"  시그널 당시 가격: {price_at_signal}")

        # 수익률 계산
        if price_at_signal > 0:
            return_pct = round((current_price - price_at_signal) / price_at_signal * 100, 2)
            print(f"  수익률: {return_pct:.2f}%")
        else:
            print(f"  ❌ 시그널 가격 0 → 수익률 계산 불가")
            fail_count += 1
            continue

        # UUID 엔트리 추가
        new_entries[sig_id] = {
            "price_at_signal": price_at_signal,
            "price_current": current_price,
            "return_pct": return_pct,
            "signal_date": pub_date[:10] if pub_date else "",
            "ticker": resolved_sym or yahoo_sym
        }
        success_count += 1

    print(f"\n{'='*60}")
    print(f"📊 결과:")
    print(f"  성공: {success_count}건")
    print(f"  스킵 (매핑 불가): {skip_count}건")
    print(f"  실패 (가격 수집): {fail_count}건")

    if new_entries and not dry_run:
        prices.update(new_entries)
        with open(SIGNAL_PRICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(prices, f, ensure_ascii=False, indent=2)
        shutil.copy(SIGNAL_PRICES_FILE, PUBLIC_PRICES_FILE)
        print(f"\n✅ signal_prices.json 업데이트 완료 ({len(prices)}개 총)")
        print(f"✅ public/signal_prices.json 동기화 완료")
    elif dry_run:
        print(f"\n[DRY RUN] 저장하지 않음. 추가될 엔트리: {len(new_entries)}건")

    print(f"{'='*60}\n")
    return success_count, skip_count, fail_count


if __name__ == '__main__':
    main()
