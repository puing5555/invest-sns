# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
"""
새 종목 자동 처리 모듈
======================
파이프라인 step 6에서 DB INSERT 후 호출됨.
1. 시그널에서 새 종목 감지 (signal_prices.json에 없는 종목)
2. Yahoo Finance / 네이버금융에서 가격 수집
3. signal_prices.json 업데이트
4. stock_tickers.json 업데이트
5. 재빌드 필요 여부 반환

사용법:
  from new_stock_handler import NewStockHandler
  handler = NewStockHandler()
  result = handler.process_new_stocks(signals)
  # result: {'new_stocks': [...], 'prices_added': N, 'rebuild_needed': bool}
"""

import json
import os
import time
import requests
from datetime import date
from pathlib import Path

# 프로젝트 루트 기준 경로
PROJECT_ROOT = Path(__file__).parent.parent
SIGNAL_PRICES_FILE = PROJECT_ROOT / "data" / "signal_prices.json"
STOCK_TICKERS_FILE = PROJECT_ROOT / "data" / "stock_tickers.json"

YAHOO_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class NewStockHandler:
    def __init__(self):
        self.signal_prices = self._load_signal_prices()
        self.stock_tickers = self._load_stock_tickers()
        self.today = date.today().isoformat()

    def _load_signal_prices(self) -> dict:
        if SIGNAL_PRICES_FILE.exists():
            with open(SIGNAL_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_stock_tickers(self) -> list:
        if STOCK_TICKERS_FILE.exists():
            with open(STOCK_TICKERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def detect_new_stocks(self, signals: list) -> list:
        """signal_prices.json에 없는 종목 추출"""
        new_stocks = []
        seen = set()
        for sig in signals:
            ticker = sig.get("ticker", "").strip()
            stock = sig.get("stock", "").strip()
            market = sig.get("market", "KR")
            if not ticker:
                continue
            # 이미 signal_prices에 있으면 스킵
            if ticker in self.signal_prices:
                continue
            # 중복 방지
            if ticker in seen:
                continue
            seen.add(ticker)
            new_stocks.append({
                "ticker": ticker,
                "stock": stock or ticker,
                "market": market
            })
        return new_stocks

    def _fetch_yahoo(self, symbol: str) -> float | None:
        """Yahoo Finance에서 regularMarketPrice 추출"""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": YAHOO_USER_AGENT},
                timeout=10
            )
            if resp.status_code == 429:
                print(f"    [RATE LIMIT] 429 → 60초 대기")
                time.sleep(60)
                return None
            if resp.status_code != 200:
                return None
            data = resp.json()
            result = data.get("chart", {}).get("result")
            if not result:
                return None
            meta = result[0].get("meta", {})
            price = meta.get("regularMarketPrice")
            return float(price) if price else None
        except Exception as e:
            print(f"    [ERROR] {symbol}: {e}")
            return None

    def fetch_price_kr(self, ticker: str) -> dict | None:
        """KR 종목 가격 수집 - ticker가 6자리 숫자 (코스피 → 코스닥 순서)"""
        if not (ticker.isdigit() and len(ticker) == 6):
            return None

        # 코스피 (.KS) 먼저 시도
        price = self._fetch_yahoo(f"{ticker}.KS")
        if price is None:
            time.sleep(1)
            # 코스닥 (.KQ) 시도
            price = self._fetch_yahoo(f"{ticker}.KQ")

        if price is None:
            return None

        return {
            "ticker": ticker,
            "market": "KR",
            "current_price": price,
            "currency": "KRW"
        }

    def fetch_price_us(self, ticker: str) -> dict | None:
        """US 종목 가격 수집"""
        price = self._fetch_yahoo(ticker)
        if price is None:
            return None
        return {
            "ticker": ticker,
            "market": "US",
            "current_price": price,
            "currency": "USD"
        }

    def fetch_price_for_stock(self, stock_info: dict) -> dict | None:
        """종목 정보에 따라 적절한 방법으로 가격 수집"""
        ticker = stock_info.get("ticker", "").strip()
        market = stock_info.get("market", "KR")

        if not ticker:
            return None

        # SECTOR / ETF는 ticker가 없는 경우가 대부분 → 스킵
        if market in ("SECTOR", "ETF"):
            # ticker가 있으면 US ETF처럼 시도
            if ticker and not ticker.isdigit():
                result = self.fetch_price_us(ticker)
                if result:
                    result["market"] = market
                    return result
            return None

        if market == "KR" or (ticker.isdigit() and len(ticker) == 6):
            return self.fetch_price_kr(ticker)
        else:
            return self.fetch_price_us(ticker)

    def update_signal_prices(self, new_prices: dict):
        """signal_prices.json에 새 가격 데이터 추가"""
        self.signal_prices.update(new_prices)
        with open(SIGNAL_PRICES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.signal_prices, f, ensure_ascii=False, indent=2)
        print(f"    → signal_prices.json 저장 ({len(self.signal_prices)}개 총)")

    def update_stock_tickers(self, new_tickers: list):
        """stock_tickers.json에 새 ticker 추가 (중복 제거)"""
        existing_set = set(self.stock_tickers)
        added = []
        for t in new_tickers:
            if t not in existing_set:
                self.stock_tickers.append(t)
                existing_set.add(t)
                added.append(t)
        if added:
            with open(STOCK_TICKERS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.stock_tickers, f, ensure_ascii=False, indent=2)
            print(f"    → stock_tickers.json 업데이트 (+{len(added)}개: {added})")
        return added

    def process_new_stocks(self, signals: list) -> dict:
        """전체 프로세스 실행"""
        # 1. 새 종목 감지
        new_stocks = self.detect_new_stocks(signals)
        if not new_stocks:
            return {
                "new_stocks": [],
                "prices_added": 0,
                "rebuild_needed": False
            }

        print(f"  새 종목 {len(new_stocks)}개 감지: {[s['ticker'] for s in new_stocks]}")

        # 2. 가격 수집
        new_prices = {}
        failed = []
        for i, stock in enumerate(new_stocks):
            ticker = stock["ticker"]
            stock_name = stock.get("stock", ticker)
            print(f"  [{i+1}/{len(new_stocks)}] {ticker} ({stock_name}) 수집 중...")

            price_data = self.fetch_price_for_stock(stock)
            if price_data:
                new_prices[ticker] = {
                    "name": stock_name,
                    "ticker": ticker,
                    "market": price_data.get("market", "KR"),
                    "current_price": price_data["current_price"],
                    "currency": price_data["currency"],
                    "last_updated": self.today
                }
                print(f"    ✓ {price_data['current_price']} {price_data['currency']}")
            else:
                failed.append(ticker)
                print(f"    ✗ 수집 실패 → 스킵")

            # 레이트리밋: 요청 간 2초 딜레이
            if i < len(new_stocks) - 1:
                time.sleep(2)

        # 3. signal_prices.json 업데이트
        if new_prices:
            self.update_signal_prices(new_prices)

        # 4. stock_tickers.json 업데이트 (가격 수집 성공한 종목만)
        added_tickers = []
        if new_prices:
            added_tickers = self.update_stock_tickers(list(new_prices.keys()))

        rebuild_needed = len(added_tickers) > 0

        return {
            "new_stocks": new_stocks,
            "prices_added": len(new_prices),
            "prices_failed": failed,
            "tickers_added": added_tickers,
            "rebuild_needed": rebuild_needed
        }


# CLI 직접 실행용
if __name__ == "__main__":
    import sys
    # missing_price_stocks.json 처리 모드
    missing_file = PROJECT_ROOT / "data" / "tmp" / "missing_price_stocks.json"
    if missing_file.exists():
        with open(missing_file, "r", encoding="utf-8") as f:
            missing_stocks = json.load(f)
        print(f"missing_price_stocks.json에서 {len(missing_stocks)}개 종목 로드")

        # signal 형식으로 변환
        signals = [
            {"ticker": s["ticker"], "stock": s["stock"], "market": s["market"]}
            for s in missing_stocks
            if s.get("ticker")  # ticker 없는 건 스킵
        ]
        print(f"  → ticker 있는 종목: {len(signals)}개")

        handler = NewStockHandler()
        result = handler.process_new_stocks(signals)

        print(f"\n=== 결과 ===")
        print(f"새 종목 감지: {len(result['new_stocks'])}개")
        print(f"가격 수집 성공: {result['prices_added']}개")
        print(f"가격 수집 실패: {len(result.get('prices_failed', []))}개")
        if result.get('prices_failed'):
            print(f"  실패 목록: {result['prices_failed']}")
        print(f"stock_tickers 추가: {len(result.get('tickers_added', []))}개")
        print(f"재빌드 필요: {result['rebuild_needed']}")
    else:
        print(f"파일 없음: {missing_file}")
        sys.exit(1)
