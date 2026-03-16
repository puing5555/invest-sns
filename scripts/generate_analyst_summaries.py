#!/usr/bin/env python3
"""
애널리스트 리포트 AI 요약 생성 스크립트
- 최근 1년치(2025-03-15 이후) 리포트 중 summary 없는 건 대상
- Claude API (claude-sonnet-4-20250514) 사용
- 제목+종목명+증권사+목표가+투자의견 기반으로 summary + ai_detail 생성
- 10건 배치 처리, 중간 저장
"""

import json
import os
import sys
import time
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
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "summary_progress.json"
CUTOFF_DATE = "2025-03-15"
MODEL = "claude-sonnet-4-20250514"
BATCH_SIZE = 10  # 중간 저장 주기
MAX_RETRIES = 3
CONCURRENT_BATCH = 5  # 한 번에 API 호출할 건수

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


def build_prompt(report: dict) -> str:
    ticker = report["ticker"]
    stock_name = TICKER_NAMES.get(ticker, ticker)
    firm = report["firm"]
    title = report["title"]
    opinion = report.get("opinion", "N/A")
    target_price = report.get("target_price")
    tp_str = f"{target_price:,}원" if target_price else "N/A"
    published = report.get("published_at", "")
    price_at = report.get("price_at_signal")
    price_at_str = f"{price_at:,}원" if price_at else "N/A"

    return f"""다음 증권사 애널리스트 리포트의 메타 정보를 바탕으로 요약을 생성해주세요.

[리포트 정보]
- 종목: {stock_name} ({ticker})
- 증권사: {firm}
- 제목: {title}
- 투자의견: {opinion}
- 목표가: {tp_str}
- 발행일 기준 주가: {price_at_str}
- 발행일: {published}

다음 두 가지를 생성해주세요:

1. **summary**: 한 줄 요약 (50자 이내). 핵심 투자 포인트와 목표가를 포함.
   예시: "삼성전자, HBM3E 양산 본격화로 실적 턴어라운드 전망, 목표가 10만원"

2. **ai_detail**: 아래 5개 섹션 형식으로 작성 (각 섹션 2-3문장).
```
## 투자포인트
(제목에서 유추되는 핵심 투자 논리)

## 실적전망
(목표가와 현재가 갭에서 유추되는 실적 방향성)

## 밸류에이션
(목표가 수준의 의미, 업사이드)

## 리스크
(해당 종목/섹터의 일반적 리스크)

## 결론
(투자의견과 목표가 기반 종합 판단)
```

반드시 JSON 형식으로만 응답하세요:
{{"summary": "...", "ai_detail": "..."}}"""


def call_api(client: anthropic.Anthropic, report: dict) -> dict | None:
    prompt = build_prompt(report)
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            # JSON 파싱 (```json ... ``` 래핑 제거)
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            result = json.loads(text)
            return result
        except json.JSONDecodeError:
            print(f"    ⚠️ JSON 파싱 실패 (attempt {attempt+1}), 재시도...")
            time.sleep(2)
        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            print(f"    ⏳ Rate limit, {wait}s 대기...")
            time.sleep(wait)
        except Exception as e:
            print(f"    ❌ API 오류: {e}")
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


def main():
    print("📊 애널리스트 리포트 AI 요약 생성기")
    print(f"📁 데이터: {DATA_FILE}")
    print(f"🤖 모델: {MODEL}")
    print()

    # 데이터 로드
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 대상 리포트 수집 (최근 1년, summary 없는 건)
    targets = []
    for ticker, reports in data.items():
        for report in reports:
            if report.get("published_at", "") >= CUTOFF_DATE and not report.get("summary"):
                targets.append(report)

    # 이미 처리된 건 제외
    completed = load_progress()
    targets = [r for r in targets if r.get("nid") not in completed]

    print(f"📋 대상: {len(targets)}건 (이미 완료: {len(completed)}건)")
    if not targets:
        print("✅ 모든 리포트 요약 완료!")
        return

    # API 클라이언트
    client = anthropic.Anthropic()

    processed = 0
    errors = 0
    start_time = time.time()

    for i, report in enumerate(targets):
        ticker = report["ticker"]
        stock_name = TICKER_NAMES.get(ticker, ticker)
        nid = report.get("nid", f"{ticker}_{report['published_at']}")

        print(f"[{i+1}/{len(targets)}] {stock_name} - {report['title'][:30]}...", end=" ")
        sys.stdout.flush()

        result = call_api(client, report)
        if result:
            report["summary"] = result.get("summary", "")
            report["ai_detail"] = result.get("ai_detail", "")
            completed.add(nid)
            processed += 1
            print(f"✅ {result['summary'][:40]}")
        else:
            errors += 1
            print("❌ 실패")

        # 배치 저장
        if (i + 1) % BATCH_SIZE == 0:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            save_progress(completed)
            elapsed = time.time() - start_time
            rate = processed / elapsed * 60 if elapsed > 0 else 0
            print(f"  💾 저장 ({processed}건 완료, {rate:.1f}건/분, 에러 {errors}건)")

        # Rate limit 방지
        time.sleep(0.5)

    # 최종 저장
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    save_progress(completed)

    elapsed = time.time() - start_time
    print()
    print("=" * 50)
    print(f"✅ 완료! {processed}건 처리 / {errors}건 에러")
    print(f"⏱️ 소요시간: {elapsed/60:.1f}분")
    print(f"📁 저장: {DATA_FILE}")


if __name__ == "__main__":
    main()
