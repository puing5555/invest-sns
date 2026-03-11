#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stock_normalizer.py - 종목명/ticker 정규화 모듈
파이프라인에서 시그널 INSERT 전 자동 적용

사용법:
  from stock_normalizer import normalize_ticker, normalize_market
  ticker = normalize_ticker('이더리움')  # → 'ETH-USD'
  ticker = normalize_ticker('ETH')       # → 'ETH-USD'
  market = normalize_market('ETH-USD')   # → 'CRYPTO'
"""

# 한글 종목명 → yfinance ticker 매핑
# BTC-USD, ETH-USD 형태로 yfinance에서 코인 조회 가능
TICKER_MAP = {
    # 암호화폐
    '비트코인': 'BTC-USD',
    'BTC': 'BTC-USD',
    '이더리움': 'ETH-USD',
    'ETH': 'ETH-USD',
    '리플': 'XRP-USD',
    'XRP': 'XRP-USD',
    '솔라나': 'SOL-USD',
    'SOL': 'SOL-USD',
    '캔톤코인': 'CNTN-USD',
    'CC': 'CNTN-USD',
    'CNTN': 'CNTN-USD',
    '도지코인': 'DOGE-USD',
    'DOGE': 'DOGE-USD',
    '체인링크': 'LINK-USD',
    'LINK': 'LINK-USD',
    '에이다': 'ADA-USD',
    'ADA': 'ADA-USD',
    '아발란체': 'AVAX-USD',
    'AVAX': 'AVAX-USD',
    '폴리곤': 'MATIC-USD',
    'MATIC': 'MATIC-USD',
    # 비트마인
    '비트마인': 'BTBT',
    'BMNR': 'BTBT',
    # 한국 종목 (6자리 → .KS)
    # 미국 종목 (이미 올바른 ticker면 그대로)
}

# 마켓 분류
CRYPTO_TICKERS = {
    'BTC-USD', 'ETH-USD', 'XRP-USD', 'SOL-USD', 'CNTN-USD',
    'DOGE-USD', 'LINK-USD', 'ADA-USD', 'AVAX-USD', 'MATIC-USD',
}


def normalize_ticker(raw_ticker: str) -> str:
    """ticker 정규화. 매핑 없으면 원본 반환."""
    if not raw_ticker:
        return raw_ticker
    return TICKER_MAP.get(raw_ticker, raw_ticker)


def normalize_market(ticker: str) -> str:
    """ticker 기반 market 분류."""
    if ticker in CRYPTO_TICKERS or ticker.endswith('-USD'):
        return 'CRYPTO'
    if ticker.isdigit():
        return 'KR'
    if '.' in ticker:
        suffix = ticker.split('.')[-1]
        if suffix in ('KS', 'KQ'):
            return 'KR'
        return 'US'
    return 'US'


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
