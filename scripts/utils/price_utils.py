"""
price_utils.py -- 가격 데이터 신선도 검증 + 멀티소스 폴백 유틸
=====================================================================
규칙:
  - max_age_hours 이내의 데이터만 신뢰 (기본 6시간)
  - Primary: yfinance -> Secondary: CoinGecko -> Tertiary: Binance
  - 모든 소스 실패 시 None + 사유 반환 (예외 던지지 않음)
"""
import json
import time
import urllib.request
from datetime import datetime, timedelta
from typing import Optional

COINGECKO_ID_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
    'DOGE': 'dogecoin',
    'XRP': 'ripple',
    'LINK': 'chainlink',
    'CNTN': 'canton-network',
}

BINANCE_SYMBOL_MAP = {
    'BTC': 'BTCUSDT',
    'ETH': 'ETHUSDT',
    'SOL': 'SOLUSDT',
    'DOGE': 'DOGEUSDT',
    'XRP': 'XRPUSDT',
    'LINK': 'LINKUSDT',
}


def is_stale(last_updated_str: str, max_age_hours: float = 6) -> bool:
    """last_updated (YYYY-MM-DD or ISO) 가 max_age_hours 이상 지났으면 True"""
    if not last_updated_str:
        return True
    try:
        if len(last_updated_str) == 10:
            dt = datetime.strptime(last_updated_str, '%Y-%m-%d')
        else:
            dt = datetime.fromisoformat(last_updated_str[:19])
        return (datetime.now() - dt) > timedelta(hours=max_age_hours)
    except Exception:
        return True


def _fetch_yfinance(ticker_symbol: str) -> Optional[float]:
    try:
        import yfinance as yf
        t = yf.Ticker(ticker_symbol)
        price = float(t.fast_info.last_price)
        if price and price > 0:
            return round(price, 6)
    except Exception as e:
        print("  [yfinance] %s 실패: %s" % (ticker_symbol, e))
    return None


def _fetch_coingecko(ticker: str) -> Optional[float]:
    cg_id = COINGECKO_ID_MAP.get(ticker.upper())
    if not cg_id:
        return None
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=%s&vs_currencies=usd' % cg_id
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            price = data.get(cg_id, {}).get('usd')
            if price and price > 0:
                return round(float(price), 6)
    except Exception as e:
        print("  [CoinGecko] %s 실패: %s" % (ticker, e))
    return None


def _fetch_binance(ticker: str) -> Optional[float]:
    symbol = BINANCE_SYMBOL_MAP.get(ticker.upper())
    if not symbol:
        return None
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=%s' % symbol
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            price = float(data.get('price', 0))
            if price > 0:
                return round(price, 6)
    except Exception as e:
        print("  [Binance] %s 실패: %s" % (ticker, e))
    return None


def get_crypto_price(
    ticker: str,
    yf_symbol: Optional[str] = None,
    max_age_hours: float = 6,
    cached_entry: Optional[dict] = None
) -> dict:
    """
    멀티소스 폴백으로 크립토 현재가 조회.

    Returns
    -------
    {
        'price': float | None,
        'source': 'cache' | 'yfinance' | 'coingecko' | 'binance' | 'failed',
        'timestamp': 'YYYY-MM-DD HH:MM:SS',
        'is_fresh': bool,
        'error': str | None
    }
    """
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 캐시 신선하면 바로 반환
    if cached_entry and isinstance(cached_entry, dict):
        last_updated = cached_entry.get('last_updated', '')
        if not is_stale(last_updated, max_age_hours):
            cached_price = cached_entry.get('current_price')
            if cached_price and cached_price > 0:
                print("  [%s] 캐시 사용 (last_updated: %s)" % (ticker, last_updated))
                return {
                    'price': cached_price,
                    'source': 'cache',
                    'timestamp': now_str,
                    'is_fresh': True,
                    'error': None
                }

    ticker_upper = ticker.upper()
    yf_sym = yf_symbol or ('%s-USD' % ticker_upper)

    print("  [%s] 실시간 조회 시작 (캐시 스테일 or 없음)" % ticker)

    # 1차: yfinance
    price = _fetch_yfinance(yf_sym)
    if price:
        print("  [%s] [OK] yfinance: $%s" % (ticker, price))
        return {'price': price, 'source': 'yfinance', 'timestamp': now_str, 'is_fresh': True, 'error': None}
    time.sleep(1)

    # 2차: CoinGecko
    price = _fetch_coingecko(ticker_upper)
    if price:
        print("  [%s] [OK] CoinGecko: $%s" % (ticker, price))
        return {'price': price, 'source': 'coingecko', 'timestamp': now_str, 'is_fresh': True, 'error': None}
    time.sleep(2)

    # 3차: Binance
    price = _fetch_binance(ticker_upper)
    if price:
        print("  [%s] [OK] Binance: $%s" % (ticker, price))
        return {'price': price, 'source': 'binance', 'timestamp': now_str, 'is_fresh': True, 'error': None}

    print("  [%s] [FAIL] 모든 소스 실패" % ticker)
    return {
        'price': None,
        'source': 'failed',
        'timestamp': now_str,
        'is_fresh': False,
        'error': '%s 가격 조회 실패 (yfinance/CoinGecko/Binance 모두 실패)' % ticker
    }


def validate_price_freshness(data: dict, max_age_hours: float = 24) -> dict:
    """signal_prices.json 전체 스캔 -> 스테일/신선/누락 분류"""
    stale, fresh, missing = [], [], []
    for key, val in data.items():
        if not isinstance(val, dict):
            continue
        last_updated = val.get('last_updated', '')
        current_price = val.get('current_price')
        if not last_updated or current_price is None:
            missing.append(key)
        elif is_stale(last_updated, max_age_hours):
            stale.append(key)
        else:
            fresh.append(key)
    return {'stale': stale, 'fresh': fresh, 'missing': missing}
