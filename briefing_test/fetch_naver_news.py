import requests
from bs4 import BeautifulSoup
import time
import json

def fetch_naver_finance_news(date_str: str, max_pages: int = 5) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    news_list = []
    seen = set()

    for page in range(1, max_pages + 1):
        url = f"https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&date={date_str}&page={page}"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "lxml")

            articles = soup.select(".articleSubject a")
            if not articles:
                articles = soup.select("dl dd.articleSubject a")
            if not articles:
                articles = soup.select("ul.newsList li a")
            if not articles:
                # broad fallback
                articles = soup.select("a[href*='article']")

            count_before = len(news_list)
            for a in articles:
                title = a.get_text(strip=True)
                if title and len(title) > 5 and title not in seen:
                    seen.add(title)
                    news_list.append({"title": title, "date": date_str})
            
            print(f"  page {page}: found {len(news_list) - count_before} articles (total {len(news_list)})")
            if len(news_list) - count_before == 0:
                break
        except Exception as e:
            print(f"  page {page} error: {e}")
        time.sleep(0.5)

    return news_list

def fetch_naver_news_alt(date_str: str) -> list:
    """Alternative: general finance news"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    news_list = []
    seen = set()
    
    for page in range(1, 4):
        url = f"https://news.naver.com/main/list.naver?mode=LS2D&sid1=101&sid2=258&date={date_str}&page={page}"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "lxml")
            articles = soup.select("ul.type06_headline li dt:not(.photo) a, ul.type06 li dt:not(.photo) a")
            for a in articles:
                title = a.get_text(strip=True)
                if title and title not in seen:
                    seen.add(title)
                    news_list.append({"title": title, "date": date_str})
        except Exception as e:
            print(f"  alt page {page} error: {e}")
        time.sleep(0.3)
    return news_list

all_news = {}

for date_str in ["20250305", "20250306"]:
    print(f"\n=== Fetching news for {date_str} ===")
    news = fetch_naver_finance_news(date_str, max_pages=5)
    
    if len(news) < 5:
        print(f"  Primary source got {len(news)}, trying alt source...")
        news2 = fetch_naver_news_alt(date_str)
        print(f"  Alt source got {len(news2)}")
        # merge
        seen = {n["title"] for n in news}
        for n in news2:
            if n["title"] not in seen:
                news.append(n)
                seen.add(n["title"])
    
    print(f"  Total: {len(news)} articles")
    all_news[date_str] = news

with open("naver_news.json", "w", encoding="utf-8") as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print("\n=== News Summary ===")
for d, news in all_news.items():
    print(f"{d}: {len(news)} articles")
    for i, n in enumerate(news[:10], 1):
        print(f"  {i}. {n['title']}")
print("\nSaved to naver_news.json")
