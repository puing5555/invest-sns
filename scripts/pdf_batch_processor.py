#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 배치 처리 스크립트 - 애널리스트 리포트 AI 요약
- 로컬 PDF에서 텍스트 추출
- Claude Sonnet으로 한줄요약 + 상세요약 생성
- Supabase analyst_reports 테이블 업데이트
"""

import os
import sys
import json
import time
import re
import pdfplumber
import requests
from pathlib import Path
from typing import Dict, List, Optional
import anthropic
from dotenv import load_dotenv
import functools

# stdout 즉시 출력
print = functools.partial(print, flush=True)

# .env.local 로드
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env.local")

# 설정
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://arypzhotxflimroprmdk.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

PDF_DIR = Path(__file__).parent.parent / "data" / "analyst_pdfs"
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "ai_summary_progress.json"
BATCH_SIZE = 50
API_DELAY = 3
BATCH_DELAY = 30
MAX_RETRIES = 5
MIN_DELAY = 2
MAX_DELAY = 30


def supabase_request(method, endpoint, data=None, params=None):
    """Supabase REST API 직접 호출"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal" if method == "PATCH" else "return=representation",
    }
    resp = requests.request(method, url, headers=headers, json=data, params=params, timeout=30)
    resp.raise_for_status()
    if method == "GET":
        return resp.json()
    return resp


def get_pending_reports() -> List[Dict]:
    """ai_summary가 없는 리포트만 조회"""
    reports = supabase_request("GET", "analyst_reports", params={
        "select": "id,title,firm,ticker,pdf_url,published_at",
        "ai_summary": "is.null",
        "pdf_url": "not.is.null",
        "order": "id.asc",
    })
    print(f"미처리 리포트: {len(reports)}건")
    return reports


def load_progress() -> set:
    """처리 완료 ID 로드"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return set(json.load(f).get("done_ids", []))
    return set()


def save_progress(done_ids: set):
    """진행상황 저장"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"done_ids": list(done_ids), "count": len(done_ids)}, f)


def find_pdf_for_report(report: Dict) -> Optional[Path]:
    """리포트에 해당하는 PDF 파일 찾기 - {ticker}_{firm}_{published_at}.pdf"""
    ticker = report.get("ticker", "")
    firm = report.get("firm", "")
    pub_date = report.get("published_at", "")
    
    if ticker and firm and pub_date:
        candidate = PDF_DIR / f"{ticker}_{firm}_{pub_date}.pdf"
        if candidate.exists():
            return candidate
    
    # fallback: ticker+firm 부분매칭
    prefix = f"{ticker}_{firm}_"
    for pdf_file in PDF_DIR.glob("*.pdf"):
        if pdf_file.name.startswith(prefix):
            return pdf_file
    
    return None


def extract_text(pdf_path: Path) -> Optional[str]:
    """PDF에서 텍스트 추출"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:30]:  # 최대 30페이지
                t = page.extract_text()
                if t:
                    text += t + "\n"
        text = text.strip()
        return text if len(text) >= 100 else None
    except Exception as e:
        print(f"  텍스트 추출 실패: {e}")
        return None


def extract_analyst_name(text: str) -> Optional[str]:
    """애널리스트명 추출"""
    lines = text.split('\n')[:20] + text.split('\n')[-20:]
    patterns = [
        r'(?:애널리스트|분석가|Analyst)[:：\s]*([가-힣]{2,4})',
        r'([가-힣]{2,4})[\s]*(?:애널리스트|분석가)',
        r'(?:담당|작성)[:：\s]*([가-힣]{2,4})',
        r'([가-힣]{2,4})[\s]*(?:선임연구원|연구원|책임연구원)',
    ]
    for line in lines:
        for pattern in patterns:
            m = re.search(pattern, line)
            if m:
                name = m.group(1).strip()
                if 2 <= len(name) <= 4:
                    return name
    return None


def generate_summary(client, text: str, firm: str, ticker: str, delay_state: dict) -> Dict[str, str]:
    """Claude - retry + backoff"""
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1200,
                timeout=60,
                messages=[{"role": "user", "content": f"""다음 애널리스트 리포트를 분석해주세요.

증권사: {firm} | 종목: {ticker}

{text[:6000]}

다음 JSON 형식으로만 답변:
{{"ai_summary": "한줄요약 50자이내, 구체적 투자포인트", "ai_detail": "상세요약 500자이상. 투자포인트/실적전망/밸류에이션/리스크/결론 구조. 구체적 수치 포함"}}"""}]
            )
            raw = resp.content[0].text.strip()
            delay_state["current"] = max(MIN_DELAY, delay_state["current"] - 0.5)
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw)
            return {"ai_summary": result.get("ai_summary", ""), "ai_detail": result.get("ai_detail", "")}
        except json.JSONDecodeError:
            print(f"  JSON parse fail, saving raw")
            return {"ai_summary": raw[:100] if raw else "", "ai_detail": raw if raw else ""}
        except anthropic.RateLimitError:
            delay_state["current"] = min(MAX_DELAY, delay_state["current"] * 2)
            wait = delay_state["current"] * (attempt + 1)
            print(f"  [WARN] 429 rate limit, wait {wait:.0f}s ({attempt+1}/{MAX_RETRIES})")
            time.sleep(wait)
        except anthropic.APITimeoutError:
            wait = 10 * (attempt + 1)
            print(f"  [WARN] timeout, wait {wait}s ({attempt+1}/{MAX_RETRIES})")
            time.sleep(wait)
        except anthropic.APIStatusError as e:
            if e.status_code == 529:
                delay_state["current"] = min(MAX_DELAY, delay_state["current"] * 2)
                wait = delay_state["current"] * (attempt + 1)
                print(f"  [WARN] 529 overloaded, wait {wait:.0f}s ({attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                print(f"  [FAIL] API {e.status_code}: {e}")
                return {}
        except Exception as e:
            print(f"  [FAIL] {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return {}
    print(f"  [FAIL] all {MAX_RETRIES} retries failed")
    return {}


def update_supabase(report_id: int, updates: Dict) -> bool:
    """Supabase 업데이트"""
    try:
        supabase_request("PATCH", f"analyst_reports?id=eq.{report_id}", data=updates)
        return True
    except Exception as e:
        print(f"  Supabase 업데이트 실패: {e}")
        return False


def main():
    print("=" * 60)
    print("PDF AI 요약 배치 처리 시작")
    print("=" * 60)

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not found in .env.local")
        sys.exit(1)
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_SERVICE_ROLE_KEY not found in .env.local")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # 미처리 리포트 조회
    reports = get_pending_reports()
    if not reports:
        print("모든 리포트가 이미 처리됨!")
        return

    # 진행상황 로드 (중간 저장)
    done_ids = load_progress()
    print(f"이전 진행: {len(done_ids)}건 완료")

    # PDF 파일 목록 캐시
    pdf_files = {f.name: f for f in PDF_DIR.glob("*.pdf")}
    print(f"로컬 PDF: {len(pdf_files)}개")

    success = 0
    skip = 0
    fail = 0
    delay_state = {"current": API_DELAY}

    for i, report in enumerate(reports):
        rid = report["id"]
        if rid in done_ids:
            skip += 1
            continue

        print(f"\n[{i+1}/{len(reports)}] ID={rid} | {report.get('firm','')} | {report.get('ticker','')}")

        # PDF 찾기
        pdf_path = find_pdf_for_report(report)
        if not pdf_path:
            print("  PDF 파일 없음 - 스킵")
            fail += 1
            continue

        # 텍스트 추출
        text = extract_text(pdf_path)
        if not text:
            print("  텍스트 추출 실패 - 스킵")
            fail += 1
            continue

        # 애널리스트명
        analyst = extract_analyst_name(text)

        # AI 요약
        result = generate_summary(client, text, report.get("firm", ""), report.get("ticker", ""), delay_state)
        if not result:
            fail += 1
            continue

        # Supabase 업데이트 (ai_detail -> summary 컬럼에 저장)
        updates = {}
        if result.get("ai_summary"):
            updates["ai_summary"] = result["ai_summary"]
        if result.get("ai_detail"):
            updates["summary"] = result["ai_detail"]
        if analyst:
            updates["analyst_name"] = analyst

        if update_supabase(rid, updates):
            success += 1
            done_ids.add(rid)
            print(f"  OK | {result.get('ai_summary', '')[:40]}...")
        else:
            fail += 1

        # 동적 딜레이
        time.sleep(delay_state["current"])

        # 10개마다 중간저장
        if success > 0 and success % 10 == 0:
            save_progress(done_ids)
            print(f"  [SAVE] {len(done_ids)} done, delay={delay_state['current']:.1f}s")

        # 50개마다 휴식 + 중간저장
        if success > 0 and success % BATCH_SIZE == 0:
            save_progress(done_ids)
            print(f"\n{'='*40}")
            print(f"중간 저장: {success}건 완료 / {fail}건 실패")
            print(f"{BATCH_DELAY}초 휴식...")
            print(f"{'='*40}")
            time.sleep(BATCH_DELAY)

    # 최종 저장
    save_progress(done_ids)
    print(f"\n{'='*60}")
    print(f"배치 처리 완료!")
    print(f"성공: {success} | 실패: {fail} | 스킵: {skip}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
