# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
"""
새 종목 자동 처리 모듈 (v2)
============================
변경사항:
  - process_from_db(): analysis_results 없이 DB에서 직접 미처리 ticker 감지
  - CRYPTO ticker → CoinGecko API (Yahoo Finance 대신)
  - 수익률(return_pct) 계산: published_at 기준 CoinGecko/Yahoo 역사 데이터
  - stockPrices.json 차트 데이터도 함께 업데이트

사용법:
  # 기존 방식 (analysis_results 있을 때)
  from new_stock_handler import NewStockHandler
  handler = NewStockHandler()
  result = handler.process_new_stocks(signals_flat_list)

  # 신규 방식 (DB 직접)
  result = handler.process_from_db(days_back=7)

CLI:
  python scripts/new_stock_handler.py --from-db
  python scripts/new_stock_handler.py --from-db --days 14
"""

import json, os, re, time, shutil, urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

# 프로젝트 루트 기준 경로
PROJECT_ROOT = Path(__file__).parent.parent
SIGNAL_PRICES_FILE = PROJECT_ROOT / "data" / "signal_prices.json"
STOCK_PRICES_FILE  = PROJECT_ROOT / "data" / "stockPrices.json"
STOCK_TICKERS_FILE = PROJECT_ROOT / "data" / "stock_tickers.json"
CRYPTO_NAMES_FILE  = PROJECT_ROOT / "data" / "cryptoNames.json"

YAHOO_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# CoinGecko ID 매핑 (ticker → coingecko id)
COINGECKO_MAP = {
    "BTC":  "bitcoin",
    "ETH":  "ethereum",
    "XRP":  "ripple",
    "SOL":  "solana",
    "BNB":  "binancecoin",
    "ADA":  "cardano",
    "DOGE": "dogecoin",
    "DOT":  "polkadot",
    "MATIC":"matic-network",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "UNI":  "uniswap",
    "ATOM": "cosmos",
    "LTC":  "litecoin",
    "ETC":  "ethereum-classic",
    "TRX":  "tron",
    "NEAR": "near",
    "FTM":  "fantom",
    "ALGO": "algorand",
    "VET":  "vechain",
    "ICP":  "internet-computer",
    "FIL":  "filecoin",
    "XLM":  "stellar",
    "HBAR": "hedera-hashgraph",
    "SUI":  "sui",
    "APT":  "aptos",
    "ARB":  "arbitrum",
    "OP":   "optimism",
    "PEPE": "pepe",
    "SHIB": "shiba-inu",
    "WLD":  "worldcoin-wld",
    "TON":  "the-open-network",
    "KLAY": "klay-token",
    "ORBS": "orbs",
    "PENGU":"pudgy-penguins",
    "CNTN": "canton-network",
    "CC":   "canton-network",
}

CRYPTO_TICKERS = set(COINGECKO_MAP.keys())


def _load_env_creds():
    env_path = PROJECT_ROOT / ".env.local"
    text = env_path.read_text(encoding="utf-8")
    svc_m  = re.search(r"SUPABASE_SERVICE_ROLE_KEY=(.+)", text)
    anon_m = re.search(r"NEXT_PUBLIC_SUPABASE_ANON_KEY=(.+)", text)
    url_m  = re.search(r"NEXT_PUBLIC_SUPABASE_URL=(.+)", text)
    KEY = (svc_m or anon_m).group(1).strip()
    URL = url_m.group(1).strip()
    return URL, KEY


class NewStockHandler:
    def __init__(self):
        self.signal_prices = self._load_json(SIGNAL_PRICES_FILE, {})
        self.stock_prices  = self._load_json(STOCK_PRICES_FILE, {})
        self.stock_tickers = self._load_json(STOCK_TICKERS_FILE, [])
        self.crypto_names  = self._load_json(CRYPTO_NAMES_FILE, {})
        self.today = date.today().isoformat()
        try:
            self._db_url, self._db_key = _load_env_creds()
            self._db_headers = {
                "apikey": self._db_key,
                "Authorization": f"Bearer {self._db_key}",
            }
        except Exception:
            self._db_url = self._db_key = None
            self._db_headers = {}

    def _load_json(self, path, default):
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    # ──────────────────────────────────────────────────────────────────
    # DB 직접 조회
    # ──────────────────────────────────────────────────────────────────
    def _db_get(self, path: str) -> list:
        if not self._db_url:
            return []
        url = f"{self._db_url}/rest/v1/{path}"
        req = urllib.request.Request(url, headers=self._db_headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())

    def get_missing_tickers_from_db(self, days_back: int = 7) -> list:
        """
        최근 N일 DB 시그널 중 signal_prices.json에 없는 ticker 반환.
        returns: [{'ticker':..., 'stock':..., 'market':...}, ...]
        """
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%S")
        rows = self._db_get(
            f"influencer_signals?select=stock,ticker,market&"
            f"created_at=gte.{cutoff}&order=created_at.desc"
        )
        seen, result = set(), []
        for row in rows:
            ticker = (row.get("ticker") or "").strip()
            if not ticker or ticker in seen:
                continue
            seen.add(ticker)
            if ticker not in self.signal_prices:
                result.append({
                    "ticker": ticker,
                    "stock":  row.get("stock", ticker),
                    "market": row.get("market", "KR"),
                })
        return result

    def get_signal_return_data(self, ticker: str) -> list:
        """
        해당 ticker의 모든 시그널 UUID + published_at 반환.
        수익률 계산 기준 날짜로 사용.
        """
        rows = self._db_get(
            f"influencer_signals?ticker=eq.{ticker}&"
            f"select=id,influencer_videos(published_at)"
        )
        result = []
        for row in rows:
            pub = (row.get("influencer_videos") or {}).get("published_at", "")
            if pub:
                result.append({"id": row["id"], "published_at": pub[:10]})
        return result

    # ──────────────────────────────────────────────────────────────────
    # 가격 수집
    # ──────────────────────────────────────────────────────────────────
    def _http_get_json(self, url: str, headers: dict = None) -> dict:
        h = {"User-Agent": YAHOO_UA, "Accept": "application/json"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())

    def fetch_coingecko_current(self, cg_id: str) -> float | None:
        """CoinGecko 현재가 KRW"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=krw"
            data = self._http_get_json(url)
            return float(data[cg_id]["krw"])
        except Exception as e:
            print(f"    [CG] {cg_id} 현재가 실패: {e}")
            return None

    def fetch_coingecko_chart(self, cg_id: str, days: int = 365) -> list:
        """CoinGecko 일별 KRW 차트 [{date, close}, ...]"""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=krw&days={days}&interval=daily"
            data = self._http_get_json(url)
            result = []
            for ts, price in data.get("prices", []):
                dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                result.append({"date": dt.strftime("%Y-%m-%d"), "close": round(price, 6)})
            return result
        except Exception as e:
            print(f"    [CG] {cg_id} 차트 실패: {e}")
            return []

    def fetch_yahoo_price(self, symbol: str) -> float | None:
        """Yahoo Finance regularMarketPrice"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
            data = self._http_get_json(url)
            result = data.get("chart", {}).get("result")
            if not result:
                return None
            price = result[0].get("meta", {}).get("regularMarketPrice")
            return float(price) if price else None
        except Exception as e:
            print(f"    [YF] {symbol} 실패: {e}")
            return None

    def fetch_yahoo_history(self, symbol: str, period: str = "1y") -> list:
        """Yahoo Finance 일별 가격 [{date, close}, ...]"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval=1d"
            data = self._http_get_json(url)
            result = data.get("chart", {}).get("result")
            if not result:
                return []
            ts_list = result[0].get("timestamp", [])
            closes  = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
            out = []
            for ts, close in zip(ts_list, closes):
                if close is None:
                    continue
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                out.append({"date": dt.strftime("%Y-%m-%d"), "close": round(float(close), 4)})
            return out
        except Exception as e:
            print(f"    [YF hist] {symbol} 실패: {e}")
            return []

    def _find_price_by_date(self, price_records: list, target_date: str) -> float | None:
        """날짜로 가격 조회 (없으면 가장 가까운 날짜)"""
        if not price_records:
            return None
        for p in price_records:
            if p["date"] == target_date:
                return p["close"]
        t = datetime.strptime(target_date, "%Y-%m-%d").timestamp()
        closest = min(price_records, key=lambda p: abs(datetime.strptime(p["date"], "%Y-%m-%d").timestamp() - t))
        return closest["close"]

    # ──────────────────────────────────────────────────────────────────
    # 종목 처리
    # ──────────────────────────────────────────────────────────────────
    def _process_crypto(self, stock_info: dict) -> dict | None:
        """크립토 처리: CoinGecko 현재가 + 차트 + 수익률"""
        ticker = stock_info["ticker"]
        cg_id  = COINGECKO_MAP.get(ticker)
        if not cg_id:
            print(f"    [SKIP] CoinGecko ID 없음: {ticker}")
            return None

        # 차트 데이터 수집
        price_records = self.fetch_coingecko_chart(cg_id, 365)
        if not price_records:
            return None

        current_price = price_records[-1]["close"]
        prev_price    = price_records[-2]["close"] if len(price_records) >= 2 else current_price
        change     = round(current_price - prev_price, 6)
        change_pct = round((change / prev_price * 100) if prev_price else 0, 2)

        # stockPrices.json 차트 업데이트
        self.stock_prices[ticker] = {
            "currentPrice":  current_price,
            "change":        change,
            "changePercent": change_pct,
            "currency":      "KRW",
            "market":        "CRYPTO",
            "name":          self.crypto_names.get(ticker, stock_info.get("stock", ticker)),
            "prices":        price_records,
        }

        # cryptoNames.json 업데이트
        if ticker not in self.crypto_names and stock_info.get("stock"):
            self.crypto_names[ticker] = stock_info["stock"]
            CRYPTO_NAMES_FILE.write_text(
                json.dumps(self.crypto_names, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        return {
            "ticker":        ticker,
            "market":        "CRYPTO",
            "current_price": current_price,
            "currency":      "KRW",
            "price_records": price_records,
        }

    def _process_stock(self, stock_info: dict) -> dict | None:
        """주식 처리: Yahoo Finance 현재가 + 차트"""
        ticker = stock_info["ticker"]
        market = stock_info.get("market", "KR")

        # KR 종목 (6자리 숫자)
        if ticker.isdigit() and len(ticker) == 6:
            price = self.fetch_yahoo_price(f"{ticker}.KS") or self.fetch_yahoo_price(f"{ticker}.KQ")
            currency = "KRW"
            yf_symbol = f"{ticker}.KS"
        elif "." in ticker:
            # 8473.T 같은 형태
            price = self.fetch_yahoo_price(ticker)
            currency = "JPY" if ticker.endswith(".T") else "USD"
            yf_symbol = ticker
        else:
            price = self.fetch_yahoo_price(ticker)
            currency = "USD"
            yf_symbol = ticker

        if price is None:
            return None

        # 차트 히스토리
        price_records = self.fetch_yahoo_history(yf_symbol, "1y")

        return {
            "ticker":        ticker,
            "market":        market,
            "current_price": price,
            "currency":      currency,
            "price_records": price_records,
        }

    def _calculate_returns(self, ticker: str, price_data: dict) -> dict:
        """
        signal_prices.json에 UUID 기준 수익률 저장.
        returns: {uuid: {return_pct, price_at_signal, price_current, signal_date}}
        """
        current_price = price_data["current_price"]
        price_records = price_data.get("price_records", [])
        returns = {}

        if not self._db_url:
            return returns

        signal_rows = self.get_signal_return_data(ticker)
        for row in signal_rows:
            sig_id = row["id"]
            pub_at = row["published_at"]
            if not pub_at:
                continue
            entry_price = self._find_price_by_date(price_records, pub_at) if price_records else None
            if entry_price and entry_price > 0:
                return_pct = round((current_price - entry_price) / entry_price * 100, 2)
                returns[sig_id] = {
                    "price_at_signal": round(entry_price, 6),
                    "price_current":   round(current_price, 6),
                    "return_pct":      return_pct,
                    "signal_date":     pub_at,
                    "ticker":          ticker,
                    "market":          price_data["market"],
                    "currency":        price_data["currency"],
                }
        return returns

    # ──────────────────────────────────────────────────────────────────
    # 저장
    # ──────────────────────────────────────────────────────────────────
    def _save_all(self):
        """signal_prices.json + stockPrices.json + public/out 동기화"""
        SIGNAL_PRICES_FILE.write_text(
            json.dumps(self.signal_prices, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        STOCK_PRICES_FILE.write_text(
            json.dumps(self.stock_prices, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        for fname in ["signal_prices.json", "stockPrices.json"]:
            src = PROJECT_ROOT / "data" / fname
            for dest_dir in ["public", "out"]:
                dst = PROJECT_ROOT / dest_dir / fname
                if src.exists() and dst.parent.exists():
                    shutil.copy2(str(src), str(dst))
        print(f"  저장 완료: signal_prices({len(self.signal_prices)}개) stockPrices({len(self.stock_prices)}개)")

    def update_stock_tickers(self, new_tickers: list) -> list:
        existing = set(self.stock_tickers)
        added = [t for t in new_tickers if t not in existing]
        if added:
            self.stock_tickers.extend(added)
            STOCK_TICKERS_FILE.write_text(
                json.dumps(self.stock_tickers, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"  stock_tickers.json +{len(added)}개: {added}")
        return added

    # ──────────────────────────────────────────────────────────────────
    # 공개 API
    # ──────────────────────────────────────────────────────────────────
    def detect_new_stocks(self, signals: list) -> list:
        """flat signals list → signal_prices에 없는 ticker 반환"""
        seen, result = set(), []
        for sig in signals:
            ticker = (sig.get("ticker") or "").strip()
            if not ticker or ticker in seen or ticker in self.signal_prices:
                continue
            seen.add(ticker)
            result.append({
                "ticker": ticker,
                "stock":  sig.get("stock", ticker),
                "market": sig.get("market", "KR"),
            })
        return result

    def process_stock_list(self, stock_list: list) -> dict:
        """
        stock_list: [{'ticker', 'stock', 'market'}, ...]
        가격 수집 + 수익률 계산 + JSON 저장까지 한 번에 처리.
        """
        prices_added = 0
        failed = []
        added_tickers = []
        total = len(stock_list)

        for i, stock_info in enumerate(stock_list):
            ticker = stock_info["ticker"]
            market = stock_info.get("market", "KR")
            name   = stock_info.get("stock", ticker)
            print(f"\n  [{i+1}/{total}] {ticker} ({name}) [{market}]")

            is_crypto = (market == "CRYPTO") or (ticker.upper() in CRYPTO_TICKERS)

            # 가격 수집
            if is_crypto:
                price_data = self._process_crypto(stock_info)
            else:
                price_data = self._process_stock(stock_info)

            if not price_data:
                failed.append(ticker)
                print(f"    [FAIL] 가격 수집 실패")
                time.sleep(1)
                continue

            # signal_prices: 티커 키 (현재가)
            self.signal_prices[ticker] = {
                "name":          name,
                "ticker":        ticker,
                "market":        price_data["market"],
                "current_price": round(price_data["current_price"], 6),
                "currency":      price_data["currency"],
                "last_updated":  self.today,
                "source":        "coingecko" if is_crypto else "yahoo",
            }

            # 수익률 계산 (UUID 키)
            returns = self._calculate_returns(ticker, price_data)
            if returns:
                self.signal_prices.update(returns)
                print(f"    수익률 계산: {len(returns)}개 시그널")
                for uid, r in returns.items():
                    print(f"      {uid[:8]}... {r['signal_date']} → {r['return_pct']:+.2f}%")

            prices_added += 1
            added_tickers.append(ticker)
            print(f"    현재가: {price_data['current_price']} {price_data['currency']}")

            # CoinGecko 레이트리밋: 2초
            time.sleep(2 if is_crypto else 1)

        # 저장
        self._save_all()

        # stock_tickers.json 업데이트
        new_in_tickers = self.update_stock_tickers(added_tickers)

        return {
            "new_stocks":    stock_list,
            "prices_added":  prices_added,
            "prices_failed": failed,
            "tickers_added": new_in_tickers,
            "rebuild_needed": len(new_in_tickers) > 0,
        }

    def process_new_stocks(self, analysis_results_or_signals) -> dict:
        """
        하위 호환: analysis_results 객체 OR flat signals list 모두 허용.
        - analysis_results: {'results': [{'signals': [...]}]}
        - flat list: [{'ticker', 'stock', 'market'}, ...]
        """
        # flat list 판별
        if isinstance(analysis_results_or_signals, list):
            signals = analysis_results_or_signals
        elif isinstance(analysis_results_or_signals, dict):
            signals = []
            for res in analysis_results_or_signals.get("results", []):
                sigs = res.get("signals") or res.get("signal_list") or []
                signals.extend(sigs)
        else:
            signals = []

        new_stocks = self.detect_new_stocks(signals)
        if not new_stocks:
            print("  새 종목 없음 (모든 ticker 이미 처리됨)")
            return {"new_stocks": [], "prices_added": 0, "rebuild_needed": False}

        print(f"  새 종목 {len(new_stocks)}개: {[s['ticker'] for s in new_stocks]}")
        return self.process_stock_list(new_stocks)

    def process_from_db(self, days_back: int = 7) -> dict:
        """
        DB에서 직접 최근 N일 시그널 읽어서 미처리 ticker 처리.
        analysis_results 없이도 독립 실행 가능.
        """
        print(f"  DB에서 최근 {days_back}일 시그널 스캔 중...")
        missing = self.get_missing_tickers_from_db(days_back)
        if not missing:
            print("  미처리 ticker 없음")
            return {"new_stocks": [], "prices_added": 0, "rebuild_needed": False}

        print(f"  미처리 ticker {len(missing)}개: {[s['ticker'] for s in missing]}")
        return self.process_stock_list(missing)


# ── CLI ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="새 종목 가격/수익률 자동 처리")
    parser.add_argument("--from-db",  action="store_true", help="DB에서 직접 미처리 ticker 감지")
    parser.add_argument("--days",     type=int, default=7, help="DB 스캔 기간 (기본 7일)")
    parser.add_argument("--tickers",  nargs="+",           help="직접 지정 ticker 처리")
    args = parser.parse_args()

    handler = NewStockHandler()

    if args.tickers:
        # 직접 ticker 지정 모드
        stock_list = []
        for t in args.tickers:
            market = "CRYPTO" if t.upper() in CRYPTO_TICKERS else (
                "KR" if (t.isdigit() and len(t) == 6) else "US"
            )
            stock_list.append({"ticker": t, "stock": t, "market": market})
        result = handler.process_stock_list(stock_list)

    elif args.from_db:
        result = handler.process_from_db(args.days)

    else:
        # 레거시: missing_price_stocks.json
        missing_file = PROJECT_ROOT / "data" / "tmp" / "missing_price_stocks.json"
        if missing_file.exists():
            with open(missing_file, encoding="utf-8") as f:
                missing_stocks = json.load(f)
            signals = [
                {"ticker": s["ticker"], "stock": s["stock"], "market": s["market"]}
                for s in missing_stocks if s.get("ticker")
            ]
            result = handler.process_new_stocks(signals)
        else:
            parser.print_help()
            sys.exit(1)

    print(f"\n=== 결과 ===")
    print(f"가격 수집 성공: {result['prices_added']}개")
    print(f"가격 수집 실패: {result.get('prices_failed', [])}")
    print(f"stock_tickers 추가: {result.get('tickers_added', [])}")
    print(f"재빌드 필요: {result['rebuild_needed']}")
