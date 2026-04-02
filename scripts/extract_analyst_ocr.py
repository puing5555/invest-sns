#!/usr/bin/env python3
"""
이미지 PDF 애널리스트 이름 OCR 추출
- PyMuPDF 텍스트 < 200자 → 이미지 PDF 판정
- EasyOCR로 첫 페이지 OCR → Claude Haiku로 이름 추출
"""

import io
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import anthropic
import easyocr
import fitz

DATA_FILE = Path(__file__).parent.parent / "data" / "analyst_reports.json"
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "analyst_ocr_progress.json"

MODEL = "claude-haiku-4-5-20251001"
SAVE_EVERY = 10

PROMPT = """이 증권사 애널리스트 리포트의 OCR 텍스트에서 작성자(애널리스트) 이름을 추출해줘.

규칙:
- 증권사명(예: 미래에셋증권, 교보증권)은 이름이 아님
- 한국인 이름 2~4글자 (예: 정태준, 김도하) 또는 영문 이름만 추출
- 여러 명이면 쉼표로 구분
- 이름을 찾을 수 없으면 정확히 "N/A"만 출력
- 이름만 출력. 설명이나 다른 텍스트 절대 금지

증권사: {firm}
리포트 제목: {title}

=== OCR 텍스트 ===
{text}"""

client = anthropic.Anthropic()


def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": {}, "stats": {"success": 0, "fail": 0, "skip": 0}}


def save_progress(progress):
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    print("🔍 이미지 PDF OCR 애널리스트 추출")

    reader = easyocr.Reader(["ko", "en"], gpu=False)
    print("EasyOCR loaded")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    ai_progress = json.load(
        open(
            Path(__file__).parent.parent / "data" / "analyst_ai_progress.json",
            encoding="utf-8",
        )
    )
    ai_completed = ai_progress["completed"]

    progress = load_progress()
    ocr_completed = progress["completed"]

    # 대상: AI 실패 + analyst null + pdf_url 있음
    targets = []
    for ticker, reports in data.items():
        for r in reports:
            nid = str(r.get("nid", ""))
            if (
                not r.get("analyst")
                and nid in ai_completed
                and not ai_completed[nid].get("analyst")
                and r.get("pdf_url")
                and nid not in ocr_completed
                and ai_completed[nid].get("reason") != "download_fail"
            ):
                targets.append({"nid": nid, "report": r, "ticker": ticker})

    print(f"대상: {len(targets)}건 (이미 완료: {len(ocr_completed)}건)")
    if not targets:
        print("완료!")
        return

    success = progress["stats"]["success"]
    fail = progress["stats"]["fail"]
    skip = progress["stats"]["skip"]
    start_time = time.time()

    for i, t in enumerate(targets):
        nid = t["nid"]
        r = t["report"]
        firm = r["firm"]
        title = r.get("title", "")[:30]

        print(f"[{i+1}/{len(targets)}] {firm} | {title}...", end=" ", flush=True)

        # PDF 다운로드
        try:
            req = urllib.request.Request(
                r["pdf_url"], headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                pdf_data = resp.read()
        except Exception:
            ocr_completed[nid] = {"analyst": None, "reason": "download_fail"}
            skip += 1
            print("SKIP(download)")
            continue

        # PyMuPDF 텍스트 체크
        try:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            text = doc[0].get_text()
            if len(text.strip()) >= 200:
                # 텍스트 PDF — 이미 AI가 실패한 것이므로 이름 없는 포맷
                doc.close()
                ocr_completed[nid] = {"analyst": None, "reason": "text_pdf_no_name"}
                fail += 1
                print("SKIP(text PDF)")
                continue

            # 이미지 PDF → OCR
            page = doc[0]
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            doc.close()
        except Exception:
            ocr_completed[nid] = {"analyst": None, "reason": "pdf_error"}
            skip += 1
            print("SKIP(pdf)")
            continue

        # EasyOCR
        try:
            result = reader.readtext(img_bytes)
            ocr_text = " ".join([r[1] for r in result])[:5000]
        except Exception:
            ocr_completed[nid] = {"analyst": None, "reason": "ocr_error"}
            skip += 1
            print("SKIP(ocr)")
            continue

        # AI 추출
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=50,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": PROMPT.format(
                            firm=firm, title=r.get("title", ""), text=ocr_text
                        ),
                    }
                ],
            )
            answer = resp.content[0].text.strip()

            # 오염 방지: 10자 초과이거나 "찾을 수 없" 포함이면 무시
            if (
                answer == "N/A"
                or not answer
                or len(answer) > 20
                or "찾을 수 없" in answer
                or "죄송" in answer
                or "텍스트" in answer
            ):
                ocr_completed[nid] = {"analyst": None, "reason": "ocr_ai_not_found"}
                fail += 1
                print("FAIL")
            else:
                ocr_completed[nid] = {"analyst": answer}
                success += 1
                print(f"✅ {answer}")
        except anthropic.RateLimitError:
            print("⏳ Rate limit, waiting 30s...")
            time.sleep(30)
            ocr_completed[nid] = {"analyst": None, "reason": "rate_limit"}
            skip += 1
        except Exception as e:
            ocr_completed[nid] = {"analyst": None, "reason": str(e)[:30]}
            skip += 1
            print(f"ERR")

        # 주기적 저장
        if (i + 1) % SAVE_EVERY == 0:
            progress["completed"] = ocr_completed
            progress["stats"] = {"success": success, "fail": fail, "skip": skip}
            save_progress(progress)
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed * 60 if elapsed > 0 else 0
            print(
                f"  💾 저장 (성공 {success} / 실패 {fail} / 스킵 {skip} / {rate:.1f}건/분)"
            )

    # 최종: analyst_reports.json 업데이트
    updated = 0
    for ticker, reports in data.items():
        for r in reports:
            nid = str(r.get("nid", ""))
            if (
                nid in ocr_completed
                and ocr_completed[nid].get("analyst")
                and not r.get("analyst")
            ):
                r["analyst"] = ocr_completed[nid]["analyst"]
                updated += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    progress["completed"] = ocr_completed
    progress["stats"] = {"success": success, "fail": fail, "skip": skip}
    save_progress(progress)

    elapsed = time.time() - start_time
    total = success + fail + skip
    print()
    print("=" * 50)
    print(f"✅ 완료! 총 {total}건 처리 ({elapsed/60:.1f}분)")
    if total:
        print(f"📈 OCR 이름 추출 성공: {success}건 ({success/total*100:.0f}%)")
    print(f"❌ 실패: {fail}건")
    print(f"⏭️ 스킵: {skip}건")
    print(f"📝 analyst_reports.json 업데이트: {updated}건")


if __name__ == "__main__":
    main()
