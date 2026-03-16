#!/usr/bin/env python3
"""
PDF에서 애널리스트 이름 추출 스크립트
- fitz (pymupdf) get_text("dict")로 span별 텍스트 추출
- 패턴: Analyst 키워드 / 이메일 앞 한글 이름 / 첫 페이지 상단 한글 2-3자
- 최근 1년치 리포트 대상 (summary 있는 것 = PDF 접근 가능)
"""

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

import fitz  # pymupdf

DATA_FILE = Path(__file__).parent.parent / "data" / "analyst_reports.json"
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "analyst_pdf_progress.json"
CUTOFF_DATE = "2025-03-15"

# 이름이 아닌 것 블랙리스트
BLACKLIST = {
    "삼성전자", "삼성전기", "현대자동차", "현대건설", "하이브", "포스코",
    "작성한", "되었습니", "데이", "입장에서", "하는", "간담회", "되지",
    "코멘트", "대상", "했으며", "따라서", "투자자", "하게", "하고",
    "기관투자", "금융투자", "리포트", "종목분석", "기업분석", "은행",
    "투자의견", "목표주가", "현재주가", "시가총액", "매수", "매도",
    "유지", "상향", "하향", "중립", "회사", "증권", "분석",
}


def extract_analyst_from_pdf(pdf_data: bytes) -> dict:
    """PDF 첫 페이지에서 애널리스트 이름과 이메일 추출"""
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        page = doc[0]
        blocks = page.get_text("dict")["blocks"]

        # span별 텍스트 수집 (위치 정보 포함)
        spans = []
        for b in blocks[:30]:
            if "lines" in b:
                for line in b["lines"]:
                    y = line["bbox"][1]
                    for s in line["spans"]:
                        t = s["text"].strip()
                        if t:
                            spans.append({"text": t, "y": y, "size": s["size"]})

        texts = [s["text"] for s in spans]
        joined = " ".join(texts[:60])

        analyst = None
        email = None

        # === 전략 1: "Analyst" 키워드 뒤 한글 이름 ===
        for i, s in enumerate(spans[:40]):
            if re.search(r"Analyst", s["text"], re.IGNORECASE):
                # 같은 span에 이름 포함 ("▶Analyst 김도하" 패턴)
                m = re.search(r"Analyst\s*:?\s*([가-힣]{2,4})", s["text"], re.IGNORECASE)
                if m and m.group(1) not in BLACKLIST:
                    analyst = m.group(1)
                    break
                # 다음 span에 이름
                for j in range(i + 1, min(i + 4, len(spans))):
                    name_match = re.match(r"^([가-힣]{2,4})$", spans[j]["text"])
                    if name_match and name_match.group(1) not in BLACKLIST:
                        analyst = name_match.group(1)
                        break
                    # "최정욱, CFA" 패턴
                    name_match2 = re.match(r"^([가-힣]{2,4})[,\s]", spans[j]["text"])
                    if name_match2 and name_match2.group(1) not in BLACKLIST:
                        analyst = name_match2.group(1)
                        break
                if analyst:
                    break

        # === 전략 2: 이메일 앞 한글 이름 ===
        # 이메일 바로 앞 span이 순수 한글 2-3자 이름인 경우만 (제목 등 혼입 방지)
        if not analyst:
            for i, s in enumerate(spans[:50]):
                if "@" in s["text"]:
                    if not email:
                        email = s["text"].strip()
                    # 이메일 앞 1-3개 span에서 순수 한글 이름만 (2-3자, 정확히 이름만)
                    for j in range(max(0, i - 3), i):
                        t = spans[j]["text"].strip()
                        # 순수 한글 2-3자만 (RA 접미사 허용)
                        name_match = re.match(r"^([가-힣]{2,3})(?:RA)?$", t)
                        if name_match and name_match.group(1) not in BLACKLIST and len(name_match.group(1)) >= 2:
                            analyst = name_match.group(1)
                            break
                    if analyst:
                        break

        # === 전략 3: SK증권 특수 패턴 ("섹터. 이름 / email" 형태) ===
        if not analyst:
            for s in spans[:40]:
                # "IT장비/소재. 이동주 / natelee@sks.co.kr" or "인터넷/게임. 남효지 / hjnam@sks.co.kr"
                m = re.search(r"[가-힣/]+\.\s*([가-힣]{2,3})\s*/\s*\S+@", s["text"])
                if m and m.group(1) not in BLACKLIST:
                    analyst = m.group(1)
                    email_m = re.search(r"([a-zA-Z0-9_.]+@[a-z]+\.[a-z.]+)", s["text"])
                    if email_m:
                        email = email_m.group(1)
                    break

        # === 전략 4: 유진투자증권 패턴 ("이름 / 02)368-xxxx" 또는 이름 뒤 전화번호) ===
        if not analyst:
            for i, s in enumerate(spans[:40]):
                t = s["text"].strip()
                # "임소정" 다음에 전화번호 또는 이메일이 오는 패턴
                if re.match(r"^[가-힣]{2,3}$", t) and t not in BLACKLIST:
                    # 다음 span이 전화번호/이메일인지 확인
                    if i + 1 < len(spans):
                        next_t = spans[i + 1]["text"].strip()
                        if re.search(r"@|02\)|3[0-9]{3}-", next_t):
                            analyst = t
                            email_m = re.search(r"([a-zA-Z0-9_.]+@[a-z]+\.[a-z.]+)", next_t)
                            if email_m:
                                email = email_m.group(1)
                            break

        # === 이메일 fallback ===
        if not email:
            email_match = re.search(r"([a-zA-Z0-9_.]+@[a-z]+\.[a-z.]+)", joined)
            if email_match:
                email = email_match.group(1)

        doc.close()
        return {"analyst": analyst, "email": email}

    except Exception as e:
        return {"analyst": None, "email": None, "error": str(e)}


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": {}, "stats": {"success": 0, "fail": 0, "skip": 0}}


def save_progress(progress: dict):
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False),
        encoding="utf-8",
    )


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # 0 = all

    print("📊 PDF 애널리스트 이름 추출기")
    print(f"📁 데이터: {DATA_FILE}")
    if limit:
        print(f"🔢 제한: {limit}건")
    print()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 대상: 최근 1년 + summary 있는 것 + pdf_url 있는 것 + analyst null
    targets = []
    for ticker, reports in data.items():
        for report in reports:
            if (report.get("published_at", "") >= CUTOFF_DATE
                    and report.get("summary")
                    and report.get("pdf_url")
                    and not report.get("analyst")):
                targets.append(report)

    # 이미 처리된 건 제외
    progress = load_progress()
    completed = progress.get("completed", {})
    targets = [r for r in targets if r.get("nid", r["pdf_url"]) not in completed]

    if limit:
        targets = targets[:limit]

    print(f"📋 대상: {len(targets)}건 (이미 완료: {len(completed)}건)")
    if not targets:
        print("✅ 완료!")
        return

    success = progress["stats"]["success"]
    fail = progress["stats"]["fail"]
    skip = progress["stats"]["skip"]
    start_time = time.time()

    for i, report in enumerate(targets):
        nid = report.get("nid", report["pdf_url"])
        firm = report["firm"]
        title = report["title"][:30]

        print(f"[{i+1}/{len(targets)}] {firm} - {title}...", end=" ", flush=True)

        try:
            req = urllib.request.Request(
                report["pdf_url"],
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                pdf_data = resp.read()

            result = extract_analyst_from_pdf(pdf_data)

            if result.get("analyst"):
                report["analyst"] = result["analyst"]
                completed[nid] = {"analyst": result["analyst"], "email": result.get("email")}
                success += 1
                print(f"✅ {result['analyst']}" + (f" ({result['email']})" if result.get("email") else ""))
            else:
                completed[nid] = {"analyst": None, "email": result.get("email")}
                fail += 1
                email_info = f" (email: {result['email']})" if result.get("email") else ""
                print(f"❌ 이름없음{email_info}")

        except Exception as e:
            completed[nid] = {"analyst": None, "error": str(e)[:50]}
            skip += 1
            print(f"⏭️ {str(e)[:40]}")

        # 10건마다 저장
        if (i + 1) % 10 == 0:
            progress["completed"] = completed
            progress["stats"] = {"success": success, "fail": fail, "skip": skip}
            save_progress(progress)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            elapsed = time.time() - start_time
            rate = (success + fail + skip) / elapsed * 60 if elapsed > 0 else 0
            print(f"  💾 저장 (성공 {success} / 실패 {fail} / 스킵 {skip} / {rate:.1f}건/분)")

        time.sleep(0.3)  # rate limit

    # 최종 저장
    progress["completed"] = completed
    progress["stats"] = {"success": success, "fail": fail, "skip": skip}
    save_progress(progress)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    total = success + fail + skip
    print()
    print("=" * 50)
    print(f"✅ 완료! 총 {total}건 처리")
    print(f"📈 이름 추출 성공: {success}건 ({success/total*100:.0f}%)" if total else "")
    print(f"❌ 이름 없음: {fail}건")
    print(f"⏭️ 에러 스킵: {skip}건")
    print(f"⏱️ 소요시간: {elapsed/60:.1f}분")


if __name__ == "__main__":
    main()
