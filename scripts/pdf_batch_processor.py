#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 諛곗튂 泥섎━ ?ㅽ겕由쏀듃 - ?좊꼸由ъ뒪??由ы룷??AI ?붿빟
- 濡쒖뺄 PDF?먯꽌 ?띿뒪??異붿텧
- Claude Sonnet?쇰줈 ?쒖쨪?붿빟 + ?곸꽭?붿빟 ?앹꽦
- Supabase analyst_reports ?뚯씠釉??낅뜲?댄듃
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

# stdout 利됱떆 異쒕젰
print = functools.partial(print, flush=True)

# .env.local 濡쒕뱶
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env.local")

# ?ㅼ젙
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
    """Supabase REST API 吏곸젒 ?몄텧"""
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
    """ai_summary媛 ?녿뒗 由ы룷?몃쭔 議고쉶"""
    reports = supabase_request("GET", "analyst_reports", params={
        "select": "id,title,firm,ticker,pdf_url,published_at",
        "ai_summary": "is.null",
        "pdf_url": "not.is.null",
        "order": "id.asc",
    })
    print(f"誘몄쿂由?由ы룷?? {len(reports)}嫄?)
    return reports


def load_progress() -> set:
    """泥섎━ ?꾨즺 ID 濡쒕뱶"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return set(json.load(f).get("done_ids", []))
    return set()


def save_progress(done_ids: set):
    """吏꾪뻾?곹솴 ???""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"done_ids": list(done_ids), "count": len(done_ids)}, f)


def find_pdf_for_report(report: Dict) -> Optional[Path]:
    """由ы룷?몄뿉 ?대떦?섎뒗 PDF ?뚯씪 李얘린 - {ticker}_{firm}_{published_at}.pdf"""
    ticker = report.get("ticker", "")
    firm = report.get("firm", "")
    pub_date = report.get("published_at", "")
    
    if ticker and firm and pub_date:
        candidate = PDF_DIR / f"{ticker}_{firm}_{pub_date}.pdf"
        if candidate.exists():
            return candidate
    
    # fallback: ticker+firm 遺遺꾨ℓ移?
    prefix = f"{ticker}_{firm}_"
    for pdf_file in PDF_DIR.glob("*.pdf"):
        if pdf_file.name.startswith(prefix):
            return pdf_file
    
    return None


def extract_text(pdf_path: Path) -> Optional[str]:
    """PDF?먯꽌 ?띿뒪??異붿텧"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:30]:  # 理쒕? 30?섏씠吏
                t = page.extract_text()
                if t:
                    text += t + "\n"
        text = text.strip()
        return text if len(text) >= 100 else None
    except Exception as e:
        print(f"  ?띿뒪??異붿텧 ?ㅽ뙣: {e}")
        return None


def extract_analyst_name(text: str) -> Optional[str]:
    """?좊꼸由ъ뒪?몃챸 異붿텧"""
    lines = text.split('\n')[:20] + text.split('\n')[-20:]
    patterns = [
        r'(?:?좊꼸由ъ뒪??遺꾩꽍媛|Analyst)[:竊?s]*([媛-??{2,4})',
        r'([媛-??{2,4})[\s]*(?:?좊꼸由ъ뒪??遺꾩꽍媛)',
        r'(?:?대떦|?묒꽦)[:竊?s]*([媛-??{2,4})',
        r'([媛-??{2,4})[\s]*(?:?좎엫?곌뎄???곌뎄??梨낆엫?곌뎄??',
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
                model="claude-sonnet-4-6",
                max_tokens=1200,
                timeout=60,
                messages=[{"role": "user", "content": f"""?ㅼ쓬 ?좊꼸由ъ뒪??由ы룷?몃? 遺꾩꽍?댁＜?몄슂.

利앷텒?? {firm} | 醫낅ぉ: {ticker}

{text[:6000]}

?ㅼ쓬 JSON ?뺤떇?쇰줈留??듬?:
{{"ai_summary": "?쒖쨪?붿빟 50?먯씠?? 援ъ껜???ъ옄?ъ씤??, "ai_detail": "?곸꽭?붿빟 500?먯씠?? ?ъ옄?ъ씤???ㅼ쟻?꾨쭩/諛몃쪟?먯씠??由ъ뒪??寃곕줎 援ъ“. 援ъ껜???섏튂 ?ы븿"}}"""}]
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
    """Supabase ?낅뜲?댄듃"""
    try:
        supabase_request("PATCH", f"analyst_reports?id=eq.{report_id}", data=updates)
        return True
    except Exception as e:
        print(f"  Supabase ?낅뜲?댄듃 ?ㅽ뙣: {e}")
        return False


def main():
    print("=" * 60)
    print("PDF AI ?붿빟 諛곗튂 泥섎━ ?쒖옉")
    print("=" * 60)

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not found in .env.local")
        sys.exit(1)
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_SERVICE_ROLE_KEY not found in .env.local")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # 誘몄쿂由?由ы룷??議고쉶
    reports = get_pending_reports()
    if not reports:
        print("紐⑤뱺 由ы룷?멸? ?대? 泥섎━??")
        return

    # 吏꾪뻾?곹솴 濡쒕뱶 (以묎컙 ???
    done_ids = load_progress()
    print(f"?댁쟾 吏꾪뻾: {len(done_ids)}嫄??꾨즺")

    # PDF ?뚯씪 紐⑸줉 罹먯떆
    pdf_files = {f.name: f for f in PDF_DIR.glob("*.pdf")}
    print(f"濡쒖뺄 PDF: {len(pdf_files)}媛?)

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

        # PDF 李얘린
        pdf_path = find_pdf_for_report(report)
        if not pdf_path:
            print("  PDF ?뚯씪 ?놁쓬 - ?ㅽ궢")
            fail += 1
            continue

        # ?띿뒪??異붿텧
        text = extract_text(pdf_path)
        if not text:
            print("  ?띿뒪??異붿텧 ?ㅽ뙣 - ?ㅽ궢")
            fail += 1
            continue

        # ?좊꼸由ъ뒪?몃챸
        analyst = extract_analyst_name(text)

        # AI ?붿빟
        result = generate_summary(client, text, report.get("firm", ""), report.get("ticker", ""), delay_state)
        if not result:
            fail += 1
            continue

        # Supabase ?낅뜲?댄듃 (ai_detail -> summary 而щ읆?????
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

        # ?숈쟻 ?쒕젅??
        time.sleep(delay_state["current"])

        # 10媛쒕쭏??以묎컙???
        if success > 0 and success % 10 == 0:
            save_progress(done_ids)
            print(f"  [SAVE] {len(done_ids)} done, delay={delay_state['current']:.1f}s")

        # 50媛쒕쭏???댁떇 + 以묎컙???
        if success > 0 and success % BATCH_SIZE == 0:
            save_progress(done_ids)
            print(f"\n{'='*40}")
            print(f"以묎컙 ??? {success}嫄??꾨즺 / {fail}嫄??ㅽ뙣")
            print(f"{BATCH_DELAY}珥??댁떇...")
            print(f"{'='*40}")
            time.sleep(BATCH_DELAY)

    # 理쒖쥌 ???
    save_progress(done_ids)
    print(f"\n{'='*60}")
    print(f"諛곗튂 泥섎━ ?꾨즺!")
    print(f"?깃났: {success} | ?ㅽ뙣: {fail} | ?ㅽ궢: {skip}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

