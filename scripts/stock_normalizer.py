#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stock_normalizer.py - 종목명/ticker 정규화 모듈 (v2)
파이프라인에서 시그널 INSERT 전 자동 적용

변경사항 (v2):
  - BTC-USD → BTC 형식으로 통일 (CoinGecko API, signal_prices.json 키와 일치)
  - 한글 종목명 → 표준 ticker (BTC, ETH, XRP, ...)
  - 크립토 목록 확장

사용법:
  from stock_normalizer import normalize_ticker, normalize_market
  ticker = normalize_ticker('이더리움')  # → 'ETH'
  ticker = normalize_ticker('ETH')       # → 'ETH'
  market = normalize_market('ETH')       # → 'CRYPTO'
"""

# 한글 종목명 / 별칭 → 표준 ticker 매핑
TICKER_MAP = {
    # 암호화폐 (한글 종목명)
    '비트코인': 'BTC',
    '이더리움': 'ETH',
    '리플': 'XRP',
    '솔라나': 'SOL',
    '캔톤코인': 'CNTN',
    '도지코인': 'DOGE',
    '체인링크': 'LINK',
    '에이다': 'ADA',
    '아발란체': 'AVAX',
    '폴리곤': 'MATIC',
    '유니스왑': 'UNI',
    '아비트럼': 'ARB',
    '옵티미즘': 'OP',
    '스텔라루멘': 'XLM',
    '카르다노': 'ADA',
    '오브스': 'ORBS',
    '퍼지펭귄': 'PENGU',
    '월드코인': 'WLD',
    # 영문 별칭 → 표준 ticker (yfinance 형식 → 표준)
    'BTC-USD': 'BTC',
    'ETH-USD': 'ETH',
    'XRP-USD': 'XRP',
    'SOL-USD': 'SOL',
    'CNTN-USD': 'CNTN',
    'DOGE-USD': 'DOGE',
    'LINK-USD': 'LINK',
    'ADA-USD': 'ADA',
    'AVAX-USD': 'AVAX',
    'MATIC-USD': 'MATIC',
    # CC는 CNTN과 같은 종목
    'CC': 'CNTN',
    # 미국 주식 별칭
    '비트마인': 'BTBT',
    'BMNR': 'BTBT',
}

# 크립토 ticker 분류
CRYPTO_TICKERS = {
    'BTC', 'ETH', 'XRP', 'SOL', 'CNTN', 'CC',
    'DOGE', 'LINK', 'ADA', 'AVAX', 'MATIC',
    'UNI', 'ARB', 'OP', 'XLM', 'ORBS', 'PENGU',
    'WLD', 'HBAR', 'TON', 'NEAR', 'FTM',
    'ALGO', 'VET', 'ICP', 'FIL', 'ATOM',
    'KLAY', 'SUI', 'APT', 'PEPE', 'SHIB',
}

# 미국 주요 ticker 화이트리스트 (상위 100개 + 유명 성장주)
US_TICKERS = {
    # 빅테크 / FAANG+
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA',
    'AVGO', 'ORCL', 'ADBE', 'CRM', 'INTC', 'AMD', 'QCOM', 'TXN',
    'IBM', 'CSCO', 'INTU', 'NOW', 'SNOW', 'DDOG', 'ZS', 'CRWD',
    # 금융
    'JPM', 'BAC', 'GS', 'MS', 'WFC', 'C', 'AXP', 'BLK', 'SPGI',
    'V', 'MA', 'PYPL', 'SQ', 'AFRM', 'HOOD', 'SOFI', 'CME', 'ICE',
    # 헬스케어
    'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'PFE', 'AMGN', 'GILD',
    'ISRG', 'MDT', 'TMO', 'DHR', 'REGN', 'CI',
    # 소비재 / 리테일
    'WMT', 'COST', 'TGT', 'HD', 'LOW', 'SBUX', 'MCD',
    'NKE', 'TJX', 'BKNG', 'ABNB', 'UBER', 'LYFT', 'DASH',
    # 에너지 / 산업재
    'XOM', 'CVX', 'EOG', 'SLB', 'GE', 'HON', 'CAT', 'DE', 'EMR',
    'ETN', 'ROP', 'CTAS', 'UPS', 'LMT', 'RTX', 'BA', 'NEE', 'DUK', 'SO',
    # 통신 / 미디어
    'NFLX', 'DIS', 'CMCSA', 'T', 'VZ', 'TMUS',
    # 기타 주목 종목
    'PLTR', 'MSTR', 'COIN', 'MELI', 'SHOP', 'RBLX', 'ASML',
    'BRK', 'PEP', 'KO', 'MO', 'PLD', 'CB', 'ACN', 'PNC', 'USB',
    'BTBT', 'MARA', 'RIOT', 'CLSK', 'HUT', 'CIFR',
    # ETF (주요)
    'SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI', 'ARKK', 'SOXL', 'TQQQ',
    # 기타 자주 언급되는 미국 종목
    'MSCI', 'MCO', 'NDAQ', 'CMG', 'PANW', 'NET', 'OKTA', 'TWLO',
    'HIMS', 'IONQ', 'QUBT', 'RGTI', 'SMCI', 'ARM', 'ALAB',
}


def normalize_ticker(raw_ticker: str) -> str:
    """ticker 정규화. 매핑 없으면 원본 반환."""
    if not raw_ticker:
        return raw_ticker
    return TICKER_MAP.get(raw_ticker, raw_ticker)


def normalize_market(ticker: str) -> str:
    """ticker 기반 market 분류."""
    if ticker in CRYPTO_TICKERS:
        return 'CRYPTO'
    if ticker.isdigit():
        return 'KR'
    if '.' in ticker:
        suffix = ticker.split('.')[-1]
        if suffix in ('KS', 'KQ'):
            return 'KR'
        return 'US'
    # 미국 주요 ticker 화이트리스트로 US 자동 판별
    if ticker in US_TICKERS:
        return 'US'
    return 'US'  # 기본값 유지 (영문 티커는 US로 간주)


if __name__ == '__main__':
    # 간단 테스트
    tests = [
        ('이더리움', 'ETH-USD', 'CRYPTO'),
        ('ETH', 'ETH-USD', 'CRYPTO'),
        ('비트코인', 'BTC-USD', 'CRYPTO'),
        ('CC', 'CNTN-USD', 'CRYPTO'),
        ('BMNR', 'BTBT', 'US'),
        ('PLTR', 'PLTR', 'US'),
        ('COIN', 'COIN', 'US'),
        ('005930', '005930', 'KR'),
    ]
    print("=== stock_normalizer 테스트 ===")
    all_pass = True
    for raw, expected_ticker, expected_market in tests:
        t = normalize_ticker(raw)
        m = normalize_market(t)
        ok = (t == expected_ticker and m == expected_market)
        status = "✓" if ok else "✗"
        print(f"  {status} {raw:12} → ticker={t:12} market={m}")
        if not ok:
            all_pass = False
            print(f"      expected: ticker={expected_ticker} market={expected_market}")
    print(f"\n{'모든 테스트 통과!' if all_pass else '일부 실패'}")
