#!/usr/bin/env python3
"""
애널리스트 이름 AI 추출 스크립트
- PyMuPDF로 PDF 첫 페이지 + 마지막 페이지 텍스트 추출
- Claude Haiku로 작성자 이름 추출 (regex 없이 AI만 사용)
- 로컬 PDF 우선 처리 후 삭제, 나머지 다운로드→추출→삭제
"""

import io
import json
import os
import sys
import time
import shutil
import urllib.request
from pathlib import Path

# Windows cp949 출력 깨짐 방지
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import fitz  # pymupdf
import anthropic

DATA_FILE = Path(__file__).parent.parent / "data" / "analyst_reports.json"
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "analyst_ai_progress.json"
PDF_DIR = Path(__file__).parent.parent / "data" / "analyst_pdfs"

MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 1000
SAVE_EVERY = 20

client = anthropic.Anthropic()

PROMPT = """이 증권사 리포트 PDF의 텍스트에서 작성자(애널리스트) 이름을 추출해줘.

규칙:
- 한글 이름 2~4글자 (예: 김도하, 박영우, 이승우)
- 여러 명이면 쉼표로 구분 (예: 김도하, 박영우)
- 이름을 찾을 수 없으면 정확히 "N/A"만 출력
- 이름만 출력. 설명이나 다른 텍스트 금지

증권사: {firm}
리포트 제목: {title}

=== 첫 페이지 텍스트 ===
{page_first}

=== 마지막 페이지 텍스트 ===
{page_last}"""


def extract_text_from_pdf(pdf_path_or_bytes, from_bytes=False):
    """PDF 첫 페이지 + 마지막 페이지 텍스트 추출"""
    try:
        if from_bytes:
            doc = fitz.open(stream=pdf_path_or_bytes, filetype="pdf")
        else:
            doc = fitz.open(pdf_path_or_bytes)

        if len(doc) == 0:
            doc.close()
            return None, None

        first_page = doc[0].get_text()[:3000]
        last_page = doc[-1].get_text()[:3000] if len(doc) > 1 else ""

        doc.close()
        return first_page, last_page
    except Exception as e:
        return None, None


def ask_ai(firm, title, page_first, page_last):
    """Claude Haiku로 이름 추출"""
    prompt_text = PROMPT.format(
        firm=firm,
        title=title,
        page_first=page_first or "(텍스트 없음)",
        page_last=page_last or "(없음)",
    )

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=100,
            temperature=0,
            messages=[{"role": "user", "content": prompt_text}],
        )
        answer = resp.content[0].text.strip()
        if answer == "N/A" or not answer:
            return None
        return answer
    except anthropic.RateLimitError:
        print("  ⏳ Rate limit, waiting 30s...")
        time.sleep(30)
        return ask_ai(firm, title, page_first, page_last)
    except Exception as e:
        print(f"  ⚠️ AI error: {e}")
        return None


def download_pdf(url):
    """PDF 다운로드"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read()
    except Exception:
        return None


def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": {}, "stats": {"success": 0, "fail": 0, "skip": 0}}


def save_progress(progress):
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    # phase: "local" = 로컬 PDF만, "download" = 다운로드 필요한 것만, "all" = 전부

    print(f"🔍 애널리스트 이름 AI 추출 (phase={phase})")
    print(f"📁 모델: {MODEL}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    progress = load_progress()
    completed = progress.get("completed", {})

    # 대상 수집: analyst null인 모든 리포트
    targets_local = []
    targets_download = []

    for ticker, reports in data.items():
        for report in reports:
            if report.get("analyst"):
                continue
            nid = str(report.get("nid", ""))
            if not nid or nid in completed:
                continue
            if not report.get("pdf_url"):
                continue

            pdf_name = f"{ticker}_{report['firm']}_{report['published_at']}.pdf"
            pdf_path = PDF_DIR / pdf_name

            entry = {
                "ticker": ticker,
                "nid": nid,
                "firm": report["firm"],
                "title": report.get("title", ""),
                "pdf_url": report["pdf_url"],
                "pdf_name": pdf_name,
                "pdf_path": pdf_path,
            }

            if pdf_path.exists():
                targets_local.append(entry)
            else:
                targets_download.append(entry)

    print(f"📋 로컬 PDF: {len(targets_local)}건")
    print(f"📋 다운로드 필요: {len(targets_download)}건")
    print(f"📋 이미 완료: {len(completed)}건")

    if phase == "local":
        targets = targets_local
    elif phase == "download":
        targets = targets_download
    else:
        targets = targets_local + targets_download

    if not targets:
        print("✅ 처리할 대상 없음!")
        return

    print(f"\n🚀 처리 시작: {len(targets)}건")

    success = progress["stats"]["success"]
    fail = progress["stats"]["fail"]
    skip = progress["stats"]["skip"]
    start_time = time.time()
    batch_deleted = 0

    for i, t in enumerate(targets):
        nid = t["nid"]
        is_local = t["pdf_path"].exists()

        print(f"[{i+1}/{len(targets)}] {t['firm']} {t['title'][:25]}...", end=" ", flush=True)

        # PDF 텍스트 추출
        if is_local:
            page_first, page_last = extract_text_from_pdf(str(t["pdf_path"]))
        else:
            pdf_bytes = download_pdf(t["pdf_url"])
            if not pdf_bytes:
                completed[nid] = {"analyst": None, "reason": "download_fail"}
                skip += 1
                print("⏭️ 다운로드 실패")
                continue
            page_first, page_last = extract_text_from_pdf(pdf_bytes, from_bytes=True)

        if page_first is None:
            completed[nid] = {"analyst": None, "reason": "pdf_parse_fail"}
            skip += 1
            print("⏭️ PDF 파싱 실패")
            continue

        # AI 추출
        name = ask_ai(t["firm"], t["title"], page_first, page_last)

        if name:
            completed[nid] = {"analyst": name}
            success += 1
            print(f"✅ {name}")
        else:
            completed[nid] = {"analyst": None, "reason": "ai_not_found"}
            fail += 1
            print("❌")

        # 주기적 저장
        if (i + 1) % SAVE_EVERY == 0:
            progress["completed"] = completed
            progress["stats"] = {"success": success, "fail": fail, "skip": skip}
            save_progress(progress)
            elapsed = time.time() - start_time
            processed = success + fail + skip - (progress["stats"].get("_prev", 0))
            rate = (i + 1) / elapsed * 60 if elapsed > 0 else 0
            print(f"  💾 저장 (성공 {success} / 실패 {fail} / 스킵 {skip} / {rate:.0f}건/분)")

        # 배치 삭제: 로컬 PDF 처리 후 삭제
        if is_local and t["pdf_path"].exists():
            t["pdf_path"].unlink()
            batch_deleted += 1

        # 다운로드 배치: BATCH_SIZE마다 중간 저장
        if not is_local and (i + 1) % BATCH_SIZE == 0:
            progress["completed"] = completed
            progress["stats"] = {"success": success, "fail": fail, "skip": skip}
            save_progress(progress)
            print(f"\n📦 배치 {(i+1)//BATCH_SIZE} 완료, 저장됨\n")

    # === 최종: analyst_reports.json 업데이트 ===
    updated = 0
    for ticker, reports in data.items():
        for report in reports:
            nid = str(report.get("nid", ""))
            if nid in completed and completed[nid].get("analyst") and not report.get("analyst"):
                report["analyst"] = completed[nid]["analyst"]
                updated += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    progress["completed"] = completed
    progress["stats"] = {"success": success, "fail": fail, "skip": skip}
    save_progress(progress)

    elapsed = time.time() - start_time
    total = success + fail + skip
    print()
    print("=" * 50)
    print(f"✅ 완료! 총 {total}건 처리 ({elapsed/60:.1f}분)")
    print(f"📈 이름 추출 성공: {success}건 ({success/total*100:.0f}%)" if total else "")
    print(f"❌ 이름 없음: {fail}건")
    print(f"⏭️ 스킵: {skip}건")
    print(f"📝 analyst_reports.json 업데이트: {updated}건")
    if batch_deleted:
        print(f"🗑️ PDF 삭제: {batch_deleted}개")


if __name__ == "__main__":
    main()
