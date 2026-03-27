# -*- coding: utf-8 -*-
"""
fetch_news.py — 네이버 증권 종목뉴스 크롤러
Usage:
  python scripts/fetch_news.py --stock 005930 --debug        # HTML 구조 확인만
  python scripts/fetch_news.py --stock 005930 --max-pages 3  # 삼성전자 3페이지 크롤링
  python scripts/fetch_news.py --all --max-pages 5           # 전체 KR 종목
"""
import argparse
import io
import json
import os
import re
import sys
import time
import random

# Windows cp949 출력 깨짐 방지
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# 프로젝트 루트 기준
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from pipeline_config import PipelineConfig

# ── 상수 ──────────────────────────────────────────────
NEWS_URL = "https://finance.naver.com/item/news_news.naver"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/item/news.naver",
    "Accept-Language": "ko-KR,ko;q=0.9",
}
DELAY_MIN, DELAY_MAX = 1.0, 2.0
DELAY_TICKER = 3.0, 5.0
BATCH_SIZE = 50

TICKER_NAMES = {
    "005930": "삼성전자", "000660": "SK하이닉스", "035420": "NAVER",
    "035720": "카카오", "005380": "현대차", "006400": "삼성SDI",
    "051910": "LG화학", "066570": "LG전자", "068270": "셀트리온",
    "207940": "삼성바이오로직스", "373220": "LG에너지솔루션",
    "005490": "POSCO홀딩스", "042660": "한화오션", "036570": "엔씨소프트",
    "105560": "KB금융", "055550": "신한지주", "012330": "현대모비스",
}


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{ts}] {msg}", flush=True)
    except UnicodeEncodeError:
        print(f"[{ts}] {msg.encode('utf-8', errors='replace').decode('utf-8')}", flush=True)


# ── 1) 뉴스 페이지 크롤링 ─────────────────────────────
def fetch_news_page(ticker: str, page: int) -> list[dict]:
    """네이버 증권 종목뉴스 1페이지 파싱"""
    params = {"code": ticker, "page": page, "clusterId": ""}
    resp = requests.get(NEWS_URL, params=params, headers=HEADERS, timeout=15, verify=False)
    resp.encoding = "euc-kr"

    soup = BeautifulSoup(resp.text, "html.parser")
    stock_name = TICKER_NAMES.get(ticker, "")
    items = []
    seen_urls = set()

    # type5 테이블이 여러 개 (메인 + 연관기사 sub-table)
    for table in soup.find_all("table", class_="type5"):
        for tr in table.find_all("tr"):
            item = _parse_news_row(tr, ticker, stock_name)
            if item and item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                items.append(item)

    return items


def _parse_news_row(tr, ticker: str, stock_name: str) -> dict | None:
    """<tr> 하나에서 뉴스 항목 추출"""
    td_title = tr.find("td", class_="title")
    td_info = tr.find("td", class_="info")
    td_date = tr.find("td", class_="date")

    if not td_title or not td_date:
        return None

    a_tag = td_title.find("a", class_="tit")
    if not a_tag:
        return None

    title = a_tag.get_text(strip=True)
    if not title:
        return None

    href = a_tag.get("href", "")
    if href.startswith("/"):
        url = "https://finance.naver.com" + href
    else:
        url = href

    source = td_info.get_text(strip=True) if td_info else ""
    date_str = td_date.get_text(strip=True) if td_date else ""

    published_at = _parse_date(date_str)

    return {
        "ticker": ticker,
        "stock_name": stock_name,
        "market": "KR",
        "title": title,
        "source": source,
        "url": url,
        "published_at": published_at,
    }


def _parse_date(date_str: str) -> str | None:
    """'2026.03.26 21:19' → ISO 8601"""
    m = re.match(r"(\d{4})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})", date_str.strip())
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}T{m.group(4)}:{m.group(5)}:00+09:00"
    # 날짜만 있는 경우
    m2 = re.match(r"(\d{4})\.(\d{2})\.(\d{2})", date_str.strip())
    if m2:
        return f"{m2.group(1)}-{m2.group(2)}-{m2.group(3)}T00:00:00+09:00"
    return None


# ── 2) 종목별 전체 크롤링 ─────────────────────────────
def fetch_ticker_news(ticker: str, max_pages: int = 5) -> list[dict]:
    """종목 뉴스 max_pages 페이지까지 수집"""
    all_items = []
    seen_urls = set()

    for page in range(1, max_pages + 1):
        items = fetch_news_page(ticker, page)

        if not items:
            log(f"  📄 page {page}: 빈 페이지, 종료")
            break

        new_items = []
        for item in items:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                new_items.append(item)

        all_items.extend(new_items)
        log(f"  📄 page {page}: {len(new_items)}건 수집 (누적 {len(all_items)})")

        if page < max_pages:
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    return all_items


# ── 3) 시장 전체 뉴스 크롤링 ─────────────────────────
MARKET_NEWS_URL = "https://finance.naver.com/news/mainnews.naver"


def fetch_market_news(max_pages: int = 3) -> list[dict]:
    """네이버 증권 메인뉴스 (시장 전체)"""
    all_items = []
    seen_urls = set()

    for page in range(1, max_pages + 1):
        resp = requests.get(
            MARKET_NEWS_URL,
            params={"page": page},
            headers=HEADERS,
            timeout=15,
            verify=False,
        )
        resp.encoding = "euc-kr"
        soup = BeautifulSoup(resp.text, "html.parser")

        news_list = soup.find(class_="newsList")
        if not news_list:
            log(f"  📄 market page {page}: newsList 없음, 종료")
            break

        items_on_page = 0
        for li in news_list.find_all("li"):
            # 구조: <li><dl><dd class="articleSubject"><a>제목</a></dd>
            #        <dd class="articleSummary"><span class="press">언론사</span>
            #        <span class="wdate">날짜</span></dd></dl></li>
            subject = li.find("dd", class_="articleSubject")
            if not subject:
                continue
            a_tag = subject.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            if not title:
                continue

            href = a_tag.get("href", "")
            if href.startswith("/"):
                url = "https://finance.naver.com" + href
            else:
                url = href

            if url in seen_urls:
                continue
            seen_urls.add(url)

            summary = li.find("dd", class_="articleSummary")
            source = ""
            date_str = ""
            if summary:
                press_el = summary.find("span", class_="press")
                source = press_el.get_text(strip=True) if press_el else ""
                wdate_el = summary.find("span", class_="wdate")
                date_str = wdate_el.get_text(strip=True) if wdate_el else ""
            published_at = _parse_market_date(date_str)

            all_items.append({
                "ticker": "MARKET",
                "stock_name": "시장뉴스",
                "market": "KR",
                "title": title,
                "source": source,
                "url": url,
                "published_at": published_at,
            })
            items_on_page += 1

        log(f"  📄 market page {page}: {items_on_page}건 (누적 {len(all_items)})")

        if page < max_pages:
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    return all_items


def _parse_market_date(date_str: str) -> str | None:
    """'2026-03-27 06:17:59' → ISO 8601"""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})", date_str.strip())
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}T{m.group(4)}:{m.group(5)}:{m.group(6)}+09:00"
    return _parse_date(date_str)


# ── 4) US/CRYPTO 뉴스 (Google News RSS) ────────────────
US_TICKERS = {
    "NVDA": "NVIDIA", "TSLA": "Tesla", "AAPL": "Apple", "MSFT": "Microsoft",
    "AMZN": "Amazon", "GOOGL": "Google", "META": "Meta", "AMD": "AMD",
    "PLTR": "Palantir", "AVGO": "Broadcom", "NFLX": "Netflix", "CRM": "Salesforce",
    "COIN": "Coinbase", "MSTR": "MicroStrategy", "TSM": "TSMC", "ASML": "ASML",
    "ARM": "ARM Holdings", "SMCI": "Super Micro", "IONQ": "IonQ", "RKLB": "Rocket Lab",
}
CRYPTO_TICKERS_NEWS = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "XRP": "Ripple",
    "DOGE": "Dogecoin", "ADA": "Cardano", "AVAX": "Avalanche", "LINK": "Chainlink",
    "BNB": "BNB", "DOT": "Polkadot",
}

import xml.etree.ElementTree as ET

def fetch_google_news(query: str, ticker: str, stock_name: str, market: str,
                      max_results: int = 10) -> list[dict]:
    """Google News RSS로 뉴스 수집"""
    import urllib.parse
    encoded = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"

    items = []
    try:
        resp = requests.get(rss_url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=15)
        resp.encoding = "utf-8"
        root = ET.fromstring(resp.text)

        for item in root.findall(".//item")[:max_results]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            source = item.findtext("source", "")

            # pubDate: 'Thu, 27 Mar 2026 01:23:00 GMT' → ISO
            published_at = _parse_rss_date(pub_date)

            items.append({
                "ticker": ticker,
                "stock_name": stock_name,
                "market": market,
                "title": title,
                "source": source,
                "url": link,
                "published_at": published_at,
            })
    except Exception as e:
        log(f"  ⚠️ Google News 실패 ({ticker}): {e}")

    return items


def _parse_rss_date(date_str: str) -> str | None:
    """'Thu, 27 Mar 2026 01:23:00 GMT' → ISO 8601"""
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        return None


def fetch_us_news(max_results: int = 10) -> list[dict]:
    """US 주요 종목 뉴스 수집"""
    all_items = []
    for ticker, name in US_TICKERS.items():
        query = f"{name} {ticker} stock"
        items = fetch_google_news(query, ticker, name, "US", max_results)
        all_items.extend(items)
        log(f"  📄 {ticker} ({name}): {len(items)}건")
        time.sleep(random.uniform(1.0, 2.0))
    return all_items


def fetch_crypto_news(max_results: int = 10) -> list[dict]:
    """CRYPTO 주요 종목 뉴스 수집"""
    all_items = []
    for ticker, name in CRYPTO_TICKERS_NEWS.items():
        query = f"{name} {ticker} crypto"
        items = fetch_google_news(query, ticker, name, "CRYPTO", max_results)
        all_items.extend(items)
        log(f"  📄 {ticker} ({name}): {len(items)}건")
        time.sleep(random.uniform(1.0, 2.0))
    return all_items


# ── 5) Supabase UPSERT ───────────────────────────────
def upsert_news(items: list[dict]) -> dict:
    """stock_news 테이블에 UPSERT (url 중복 무시)"""
    config = PipelineConfig()
    base_url = config.SUPABASE_URL + "/rest/v1"
    headers = {
        "apikey": config.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=ignore-duplicates,return=minimal",
    }

    inserted = 0
    errors = 0

    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i : i + BATCH_SIZE]
        resp = requests.post(f"{base_url}/stock_news", headers=headers, json=batch)

        if resp.status_code in (200, 201):
            inserted += len(batch)
        elif resp.status_code == 409:
            # 전부 중복
            log(f"  ⏭ batch {i}: 전부 중복 (409)")
        else:
            log(f"  ❌ batch {i}: HTTP {resp.status_code} {resp.text[:200]}")
            errors += len(batch)

    return {"inserted": inserted, "errors": errors}


# ── 4) 메인 ──────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="네이버 증권 종목뉴스 크롤러")
    parser.add_argument("--stock", type=str, help="단일 종목 코드 (예: 005930)")
    parser.add_argument("--all", action="store_true", help="전체 KR 종목")
    parser.add_argument("--max-pages", type=int, default=5, help="종목당 최대 페이지 (기본 5)")
    parser.add_argument("--debug", action="store_true", help="HTML 파싱 확인만 (DB 저장 안 함)")
    parser.add_argument("--market", action="store_true", help="시장 전체 뉴스 크롤링")
    parser.add_argument("--us", action="store_true", help="US 주요 종목 뉴스 (Google News)")
    parser.add_argument("--crypto", action="store_true", help="CRYPTO 주요 종목 뉴스 (Google News)")
    parser.add_argument("--max-results", type=int, default=10, help="Google News 종목당 최대 건수 (기본 10)")
    args = parser.parse_args()

    if not args.stock and not args.all and not args.market and not args.us and not args.crypto:
        parser.error("--stock, --all, --market 중 하나 필수")

    # 시장 뉴스 모드
    if args.market:
        log("📰 시장 전체 뉴스 크롤링")
        items = fetch_market_news(args.max_pages)
        log(f"  수집: {len(items)}건")
        if args.debug:
            for item in items[:10]:
                print(f"    {item['published_at'][:16] if item['published_at'] else '????-??-??'} | {item['source']:10s} | {item['title'][:50]}")
            if len(items) > 10:
                print(f"    ... +{len(items)-10}건")
        else:
            if items:
                result = upsert_news(items)
                log(f"  ✅ DB 저장: {result['inserted']}건 (에러 {result['errors']}건)")
        log(f"📊 완료: 시장 뉴스 {len(items)}건")
        if not args.us and not args.crypto:
            return

    # US 뉴스 모드
    if args.us:
        log("📰 US 종목 뉴스 크롤링 (Google News)")
        items = fetch_us_news(args.max_results)
        log(f"  수집: {len(items)}건")
        if not args.debug and items:
            result = upsert_news(items)
            log(f"  ✅ DB 저장: {result['inserted']}건 (에러 {result['errors']}건)")
        log(f"📊 완료: US 뉴스 {len(items)}건")
        if not args.crypto:
            return

    # CRYPTO 뉴스 모드
    if args.crypto:
        log("📰 CRYPTO 종목 뉴스 크롤링 (Google News)")
        items = fetch_crypto_news(args.max_results)
        log(f"  수집: {len(items)}건")
        if not args.debug and items:
            result = upsert_news(items)
            log(f"  ✅ DB 저장: {result['inserted']}건 (에러 {result['errors']}건)")
        log(f"📊 완료: CRYPTO 뉴스 {len(items)}건")
        return

    # 종목 리스트
    if args.stock:
        tickers = [args.stock]
    else:
        with open(os.path.join(ROOT, "data", "stock_tickers.json"), "r") as f:
            all_tickers = json.load(f)
        tickers = [t for t in all_tickers if t.isdigit() and len(t) == 6]
        log(f"📋 KR 종목 {len(tickers)}개 로드")

    total_collected = 0
    total_inserted = 0

    for idx, ticker in enumerate(tickers):
        name = TICKER_NAMES.get(ticker, ticker)
        log(f"🔍 [{idx+1}/{len(tickers)}] {name} ({ticker})")

        items = fetch_ticker_news(ticker, args.max_pages)
        total_collected += len(items)

        if args.debug:
            log(f"  [DEBUG] 수집 {len(items)}건:")
            for item in items[:10]:
                print(f"    {item['published_at'][:16] if item['published_at'] else '????-??-??'} | {item['source']:8s} | {item['title'][:50]}")
                print(f"    → {item['url'][:80]}")
            if len(items) > 10:
                print(f"    ... +{len(items)-10}건")
        else:
            if items:
                result = upsert_news(items)
                total_inserted += result["inserted"]
                log(f"  ✅ DB 저장: {result['inserted']}건 (에러 {result['errors']}건)")
            else:
                log(f"  ⏭ 뉴스 없음")

        if idx < len(tickers) - 1:
            time.sleep(random.uniform(*DELAY_TICKER))

    log(f"📊 완료: 수집 {total_collected}건, DB 저장 {total_inserted}건")


if __name__ == "__main__":
    main()
