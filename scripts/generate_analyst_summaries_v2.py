#!/usr/bin/env python3
"""
애널리스트 리포트 AI 요약 생성 v2
- 네이버 모바일 페이지에서 리포트 본문 추출 → Claude Sonnet으로 요약
- 최근 1년치(2025-03-15 이후) 리포트 대상
- 기존 제목 기반 summary/ai_detail 삭제 후 재생성
- 병렬 5건, 10건마다 중간 저장
"""

import json
import os
import sys
import re
import time
import asyncio
import aiohttp
from pathlib import Path

# .env.local 읽기
env_path = Path(__file__).parent.parent / ".env.local"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import anthropic

DATA_FILE = Path(__file__).parent.parent / "data" / "analyst_reports.json"
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "summary_v2_progress.json"
CUTOFF_DATE = "2025-03-15"
MODEL = "claude-sonnet-4-20250514"
BATCH_SIZE = 10
CONCURRENT = 5
MAX_RETRIES = 3
TEXT_LIMIT = 3000

TICKER_NAMES = {
    "105560": "KB금융", "240810": "원익QnC", "259960": "크래프톤", "284620": "카이",
    "298040": "효성중공업", "352820": "하이브", "403870": "HPSP", "051910": "LG화학",
    "000720": "현대건설", "079160": "CJ CGV", "039490": "키움증권", "042700": "한미반도체",
    "005930": "삼성전자", "006400": "삼성SDI", "016360": "삼성증권", "036930": "주성엔지니어링",
    "005380": "현대자동차", "005940": "NH투자증권", "090430": "아모레퍼시픽", "071050": "한국금융지주",
    "000660": "SK하이닉스", "036570": "엔씨소프트", "035420": "NAVER", "055550": "신한지주",
    "068270": "셀트리온", "005490": "POSCO홀딩스", "012330": "현대모비스", "066570": "LG전자",
    "028260": "삼성물산", "000270": "기아", "096770": "SK이노베이션", "003550": "LG",
    "034730": "SK", "032830": "삼성생명", "011200": "HMM", "018260": "삼성에스디에스",
    "009150": "삼성전기", "030200": "KT", "086790": "하나금융지주", "035720": "카카오",
    "004020": "현대제철", "003670": "포스코퓨처엠", "010130": "고려아연", "011170": "롯데케미칼",
    "017670": "SK텔레콤",
}


async def fetch_report_content(session: aiohttp.ClientSession, nid: str) -> str | None:
    """네이버 모바일 페이지에서 리포트 본문 텍스트 추출"""
    url = f"https://m.stock.naver.com/research/company/{nid}"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"}

    for attempt in range(MAX_RETRIES):
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 429:
                    await asyncio.sleep(30 * (attempt + 1))
                    continue
                if resp.status != 200:
                    return None
                html = await resp.text()

            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
            if not match:
                return None

            data = json.loads(match.group(1))
            queries = data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
            for q in queries:
                rc = q.get("state", {}).get("data", {}).get("result", {}).get("researchContent")
                if rc and rc.get("content"):
                    text = re.sub(r'<[^>]+>', ' ', rc["content"])
                    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text[:TEXT_LIMIT] if text else None
            return None
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(3)
            continue
    return None


def build_prompt(report: dict, body_text: str) -> str:
    ticker = report["ticker"]
    stock_name = TICKER_NAMES.get(ticker, ticker)
    firm = report["firm"]
    title = report["title"]
    opinion = report.get("opinion", "N/A")
    target_price = report.get("target_price")
    tp_str = f"{target_price:,}원" if target_price else "N/A"

    return f"""다음 증권사 애널리스트 리포트를 분석하여 요약을 생성해주세요.

[리포트 메타]
- 종목: {stock_name} ({ticker})
- 증권사: {firm}
- 제목: {title}
- 투자의견: {opinion}
- 목표가: {tp_str}

[리포트 본문]
{body_text}

다음 두 가지를 생성해주세요:

1. **summary**: 한 줄 요약 (50자 이내). 핵심 투자 포인트와 목표가를 포함.

2. **ai_detail**: 아래 5개 섹션으로 작성 (각 2-3문장, 본문 내용 기반).
```
## 투자포인트
(본문의 핵심 투자 논리)

## 실적전망
(매출/이익 전망 수치 포함)

## 밸류에이션
(목표가 근거, 적용 지표)

## 리스크
(본문에서 언급된 리스크 요인)

## 결론
(투자의견과 목표가 기반 종합 판단)
```

반드시 JSON 형식으로만 응답하세요:
{{"summary": "...", "ai_detail": "..."}}"""


def call_claude(client: anthropic.Anthropic, report: dict, body_text: str) -> dict | None:
    prompt = build_prompt(report, body_text)
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(text)
        except json.JSONDecodeError:
            time.sleep(2)
        except anthropic.RateLimitError:
            time.sleep(30 * (attempt + 1))
        except Exception as e:
            print(f"    ❌ API: {e}")
            time.sleep(5)
    return None


def load_progress() -> set:
    if PROGRESS_FILE.exists():
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return set(data.get("completed_nids", []))
    return set()


def save_progress(completed_nids: set):
    PROGRESS_FILE.write_text(
        json.dumps({"completed_nids": list(completed_nids), "count": len(completed_nids)}, ensure_ascii=False),
        encoding="utf-8",
    )


async def fetch_batch(session, reports):
    """병렬로 네이버 본문 추출"""
    tasks = [fetch_report_content(session, r.get("nid", "")) for r in reports]
    return await asyncio.gather(*tasks)


async def main():
    print("📊 애널리스트 리포트 AI 요약 생성기 v2 (본문 기반)")
    print(f"📁 데이터: {DATA_FILE}")
    print(f"🤖 모델: {MODEL}")
    print()

    # 데이터 로드
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Step 1: 기존 제목 기반 summary/ai_detail 삭제 (최근 1년)
    cleared = 0
    for ticker, reports in data.items():
        for report in reports:
            if report.get("published_at", "") >= CUTOFF_DATE:
                if report.get("summary") or report.get("ai_detail"):
                    report["summary"] = None
                    report["ai_detail"] = None
                    cleared += 1
    print(f"🗑️ 기존 요약 {cleared}건 삭제")

    # 저장 (삭제 반영)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Step 2: 대상 수집 (nid 있는 건만)
    targets = []
    for ticker, reports in data.items():
        for report in reports:
            if (report.get("published_at", "") >= CUTOFF_DATE
                    and report.get("nid")
                    and report.get("pdf_url")):
                targets.append(report)

    # 이미 처리된 건 제외
    completed = load_progress()
    targets = [r for r in targets if r.get("nid") not in completed]

    print(f"📋 대상: {len(targets)}건 (이미 완료: {len(completed)}건)")
    if not targets:
        print("✅ 완료!")
        return

    # API 클라이언트
    client = anthropic.Anthropic()
    processed = 0
    errors = 0
    no_content = 0
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        for batch_start in range(0, len(targets), CONCURRENT):
            batch = targets[batch_start:batch_start + CONCURRENT]

            # 병렬로 본문 추출
            contents = await fetch_batch(session, batch)

            # Claude API 호출 (순차 - rate limit 고려)
            for report, content in zip(batch, contents):
                idx = batch_start + batch.index(report) + 1
                ticker = report["ticker"]
                stock_name = TICKER_NAMES.get(ticker, ticker)
                nid = report.get("nid")

                print(f"[{idx}/{len(targets)}] {stock_name} - {report['title'][:30]}...", end=" ")
                sys.stdout.flush()

                if not content or len(content) < 50:
                    no_content += 1
                    print("⏭️ 본문없음")
                    completed.add(nid)
                    continue

                result = call_claude(client, report, content)
                if result:
                    report["summary"] = result.get("summary", "")
                    report["ai_detail"] = result.get("ai_detail", "")
                    completed.add(nid)
                    processed += 1
                    summary_preview = result.get("summary", "")[:40]
                    print(f"✅ {summary_preview}")
                else:
                    errors += 1
                    print("❌ 실패")

                time.sleep(0.3)

            # 배치 저장
            if (batch_start + CONCURRENT) % BATCH_SIZE < CONCURRENT:
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                save_progress(completed)
                elapsed = time.time() - start_time
                rate = processed / elapsed * 60 if elapsed > 0 else 0
                total_done = processed + no_content + errors
                print(f"  💾 저장 ({processed}건 요약 / {no_content}건 본문없음 / {errors}건 에러 / {rate:.1f}건/분)")

            # 네이버 rate limit 방지
            await asyncio.sleep(0.5)

    # 최종 저장
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    save_progress(completed)

    elapsed = time.time() - start_time
    print()
    print("=" * 50)
    print(f"✅ 완료!")
    print(f"📈 요약 생성: {processed}건")
    print(f"⏭️ 본문없음: {no_content}건")
    print(f"❌ 에러: {errors}건")
    print(f"⏱️ 소요시간: {elapsed/60:.1f}분")
    print(f"📁 저장: {DATA_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
