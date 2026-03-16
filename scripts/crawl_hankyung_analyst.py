#!/usr/bin/env python3
"""
한경 컨센서스에서 애널리스트 이름 크롤링 → 네이버 리포트와 매칭
- URL: consensus.hankyung.com/analysis/list?skinType=business
- 매칭 키: 종목코드 + 증권사 + 날짜
- 최근 1년치 (2025-03-15 ~ 2026-03-16)
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.request
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "analyst_reports.json"
CACHE_FILE = Path(__file__).parent.parent / "data" / "hankyung_cache.json"
CUTOFF_DATE = "2025-03-15"
END_DATE = "2026-03-16"
PAGE_SIZE = 80
BASE_URL = "https://consensus.hankyung.com/analysis/list"

# 증권사 이름 정규화 (한경 ↔ 네이버 차이)
FIRM_ALIASES = {
    "iM증권": "iM증권",
    "DB금융투자": "DB금융투자",
    "KB증권": "KB증권",
    "NH투자증권": "NH투자증권",
    "SK증권": "SK증권",
    "하나증권": "하나증권",
    "한화투자증권": "한화투자증권",
    "메리츠증권": "메리츠증권",
    "대신증권": "대신증권",
    "키움증권": "키움증권",
    "미래에셋증권": "미래에셋증권",
    "삼성증권": "삼성증권",
    "유안타증권": "유안타증권",
    "유진투자증권": "유진투자증권",
    "IBK투자증권": "IBK투자증권",
    "교보증권": "교보증권",
    "DS투자증권": "DS투자증권",
    "한국IR협의회": "한국IR협의회",
    "이베스트투자증권": "이베스트증권",
    "신한투자증권": "신한투자증권",
    "LS증권": "LS증권",
    "BNK투자증권": "BNK투자증권",
    "다올투자증권": "다올투자증권",
    "현대차증권": "현대차증권",
    "한국투자증권": "한국투자증권",
    "신영증권": "신영증권",
    "흥국증권": "흥국증권",
    "부국증권": "부국증권",
    "케이프투자증권": "케이프투자증권",
    "상상인증권": "상상인증권",
    "나이스디앤비": "나이스디앤비",
}


def normalize_firm(firm: str) -> str:
    firm = firm.strip()
    return FIRM_ALIASES.get(firm, firm)


def create_ssl_context():
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    return ctx


def crawl_page(page: int, ctx) -> list[dict]:
    """한경 컨센서스 한 페이지 크롤링"""
    url = f"{BASE_URL}?skinType=business&sdate={CUTOFF_DATE}&edate={END_DATE}&now_page={page}&pagenum={PAGE_SIZE}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    results = []
    rows = re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", html)
    for row in rows:
        tds = re.findall(r"<td[^>]*>([\s\S]*?)</td>", row)
        if len(tds) < 6:
            continue
        texts = [re.sub(r"<[^>]+>", "", td).strip() for td in tds]
        date, title_raw, target, opinion, analyst, firm = texts[0], texts[1], texts[2], texts[3], texts[4], texts[5]

        # 날짜 검증
        if not re.match(r"\d{4}-\d{2}-\d{2}", date):
            continue

        # 종목코드 추출: "삼성전자(005930) 제목..." → 005930
        code_match = re.search(r"\((\d{6})\)", title_raw)
        ticker = code_match.group(1) if code_match else None

        # 제목 추출: 코드 뒤의 텍스트
        title = re.sub(r"^[^)]+\)\s*", "", title_raw).strip()
        title = re.sub(r"\s+", " ", title)

        # analyst 정리 (쉼표로 여러명인 경우 첫 번째만)
        analyst = analyst.split(",")[0].strip()
        if analyst in ("리서치센터", "--", "", "N/A"):
            analyst = None

        results.append({
            "date": date,
            "ticker": ticker,
            "title": title,
            "target_price": int(target.replace(",", "")) if target.replace(",", "").isdigit() else None,
            "opinion": opinion,
            "analyst": analyst,
            "firm": normalize_firm(firm),
        })

    # 마지막 페이지 번호 추출
    pages = re.findall(r"now_page=(\d+)", html)
    last_page = max(int(p) for p in pages) if pages else page

    return results, last_page


def main():
    print("📊 한경 컨센서스 애널리스트 크롤링 + 매칭")
    print(f"📅 기간: {CUTOFF_DATE} ~ {END_DATE}")
    print()

    ctx = create_ssl_context()

    # Step 1: 크롤링
    all_hankyung = []
    if CACHE_FILE.exists():
        all_hankyung = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        print(f"📁 캐시 로드: {len(all_hankyung)}건")
    else:
        page = 1
        last_page = 999
        while page <= last_page:
            print(f"  [Page {page}] ", end="", flush=True)
            try:
                results, last_page = crawl_page(page, ctx)
                all_hankyung.extend(results)
                print(f"✅ {len(results)}건 (누적 {len(all_hankyung)}건, 마지막 페이지: {last_page})")
            except Exception as e:
                print(f"❌ {e}")
                time.sleep(5)
                continue
            page += 1
            time.sleep(1)

        # 캐시 저장
        CACHE_FILE.write_text(json.dumps(all_hankyung, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n💾 캐시 저장: {len(all_hankyung)}건 → {CACHE_FILE}")

    print(f"\n📋 한경 데이터: {len(all_hankyung)}건")
    with_analyst = sum(1 for r in all_hankyung if r.get("analyst"))
    print(f"  이름 있음: {with_analyst}건 ({with_analyst/len(all_hankyung)*100:.0f}%)")

    # Step 2: 매칭
    print("\n🔗 네이버 리포트와 매칭 중...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        naver_data = json.load(f)

    # 네이버 리포트 인덱스: (ticker, firm, date) → report
    naver_index = {}
    target_count = 0
    for ticker, reports in naver_data.items():
        for r in reports:
            if r.get("published_at", "") >= CUTOFF_DATE:
                key = (ticker, r["firm"], r["published_at"])
                naver_index[key] = r
                target_count += 1

    print(f"  네이버 최근 1년: {target_count}건")

    # 매칭 실행
    matched = 0
    already_has = 0
    no_ticker = 0
    no_match = 0

    for h in all_hankyung:
        if not h.get("analyst") or not h.get("ticker"):
            if not h.get("ticker"):
                no_ticker += 1
            continue

        key = (h["ticker"], h["firm"], h["date"])
        naver_report = naver_index.get(key)

        if naver_report:
            if naver_report.get("analyst"):
                already_has += 1
            else:
                naver_report["analyst"] = h["analyst"]
                matched += 1
        else:
            # firm 이름 차이로 못 찾는 경우 — 같은 ticker+date로 fuzzy 매칭
            for k, v in naver_index.items():
                if k[0] == h["ticker"] and k[2] == h["date"] and not v.get("analyst"):
                    v["analyst"] = h["analyst"]
                    matched += 1
                    break
            else:
                no_match += 1

    print(f"\n✅ 매칭 결과:")
    print(f"  신규 매칭: {matched}건")
    print(f"  이미 있음: {already_has}건")
    print(f"  종목코드 없음: {no_ticker}건")
    print(f"  매칭 실패: {no_match}건")

    # Step 3: 저장
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(naver_data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 저장 완료: {DATA_FILE}")

    # 최종 통계
    total = 0
    has_analyst = 0
    for reports in naver_data.values():
        for r in reports:
            if r.get("published_at", "") >= CUTOFF_DATE:
                total += 1
                if r.get("analyst"):
                    has_analyst += 1
    print(f"\n📊 최근 1년 리포트 analyst 현황: {has_analyst}/{total} ({has_analyst/total*100:.1f}%)")


if __name__ == "__main__":
    main()
