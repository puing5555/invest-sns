"""DART insider trade crawler. Usage: python crawl_dart_insider.py [STOCK_CODE] [STOCK_NAME]"""
import requests, json, time, sys, os, zipfile, io, re, xml.etree.ElementTree as ET, warnings
from html import unescape
from collections import Counter
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

API_KEY = "a75002cc56e408585d6e8baee9c33978ee28388b"
BASE = "https://opendart.fss.or.kr/api"

# RPT_RSN 코드 → trade_type 매핑
# 매수/매도가 아닌 보고 유형은 "보고"로 분류
NON_TRADE_CODES = {"31", "33", "34", "35", "36", "37", "38", "39", "59", "99"}  # 신규선임, 신규보고, 수증, 자사주상여금, 기타 등

def get_corp_code(stock_code):
    print(f"[1/4] corp_code for {stock_code}...")
    resp = requests.get(f"{BASE}/corpCode.xml", params={"crtfc_key": API_KEY}, timeout=60, verify=False)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        with zf.open("CORPCODE.xml") as f:
            root = ET.parse(f).getroot()
            for corp in root.findall("list"):
                if corp.findtext("stock_code", "").strip() == stock_code:
                    cc = corp.findtext("corp_code", "").strip()
                    cn = corp.findtext("corp_name", "").strip()
                    print(f"  {cn} -> {cc}")
                    return cc, cn
    return None, None

def get_elestock(corp_code):
    print("[2/4] elestock.json...")
    resp = requests.get(f"{BASE}/elestock.json", params={"crtfc_key": API_KEY, "corp_code": corp_code, "bgn_de": "20160101", "end_de": "20260401"}, timeout=30, verify=False)
    data = resp.json()
    items = data.get("list", []) if data.get("status") == "000" else []
    print(f"  {len(items)} items")
    return items

def get_old_disclosures(corp_code, end_date):
    print(f"[3/4] list.json (20160101~{end_date})...")
    all_items = []
    page = 1
    while True:
        resp = requests.get(f"{BASE}/list.json", params={"crtfc_key": API_KEY, "corp_code": corp_code, "bgn_de": "20160101", "end_de": end_date, "pblntf_ty": "D", "page_no": page, "page_count": 100}, timeout=30, verify=False)
        d = resp.json()
        if d.get("status") != "000": break
        for item in d.get("list", []):
            if any(kw in item.get("report_nm", "") for kw in ["임원", "주요주주", "특정증권"]): all_items.append(item)
        if page >= int(d.get("total_page", 1)): break
        page += 1
        time.sleep(0.3)
    print(f"  {len(all_items)} disclosures")
    return all_items

def parse_document(rcept_no, rcept_dt, stock_code, stock_name):
    resp = requests.get(f"{BASE}/document.xml", params={"crtfc_key": API_KEY, "rcept_no": rcept_no}, timeout=30, verify=False)
    if resp.status_code != 200: return []
    trades = []
    try:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            for fname in zf.namelist():
                raw = zf.read(fname)
                content = None
                for enc in ["euc-kr", "cp949", "utf-8"]:
                    try: content = raw.decode(enc); break
                    except: continue
                if not content: content = raw.decode("utf-8", errors="replace")
                clean = re.sub(r"<[^>]+>", " ", content)
                clean = re.sub(r"\s+", " ", clean).strip()
                clean = unescape(clean).replace("&cr;", " ")

                # ── 이름 추출 ──
                name_val = ""
                nm = re.search(r"성명\s*\(?명칭\)?\s*한\s*글\s+([^\s]+)", clean)
                if nm:
                    name_val = nm.group(1)
                HEADER_PATTERNS = re.compile(r"한자|영문|성명|명칭|직위|관계|생년|사업자|주소")
                if not name_val or HEADER_PATTERNS.search(name_val):
                    try:
                        soup = BeautifulSoup(content, "html.parser")
                        for cell in soup.find_all(["td", "th"]):
                            if re.search(r"한\s*글", cell.get_text(strip=True)):
                                next_cell = cell.find_next("td")
                                if next_cell:
                                    candidate = next_cell.get_text(strip=True)
                                    if candidate and candidate != cell.get_text(strip=True) and not HEADER_PATTERNS.search(candidate):
                                        name_val = candidate
                                        break
                    except Exception:
                        pass
                if name_val and HEADER_PATTERNS.search(name_val):
                    name_val = ""
                if len(name_val) == 1:
                    print(f"  WARN: 이름 1글자: '{name_val}' (rcpNo={rcept_no})")

                # ── 직위 추출 ──
                pm = re.search(r"직\s*위\s*명\s+([가-힣A-Za-z()]+)", clean)
                pos_val = pm.group(1).strip() if pm else ""

                # ── 퇴임일 추출 ──
                retire_date = None
                tm = re.search(r"퇴임일\s+(\d{4})\s*년?\s*(\d{1,2})\s*월?\s*(\d{1,2})\s*일?", clean)
                if tm:
                    retire_date = f"{tm.group(1)}-{int(tm.group(2)):02d}-{int(tm.group(3)):02d}"

                dd = f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}"

                # ── 방법 1: <tu>/<te> 커스텀 태그 파싱 (우선) ──
                soup = BeautifulSoup(content, "html.parser")
                extraction_tables = soup.find_all("table", attrs={"aclass": "EXTRACTION"})
                tu_found = False
                for etable in extraction_tables:
                    for row in etable.find_all("tr"):
                        tus = {t.get("aunit", ""): t for t in row.find_all("tu")}
                        tes = {t.get("acode", ""): t for t in row.find_all("te")}
                        if "RPT_RSN" not in tus or "MDF_STK_CNT" not in tes:
                            continue
                        # 종류 확인: 보통주만 (aunitvalue=1)
                        str_knd = tus.get("STR_KND")
                        if str_knd and str_knd.get("aunitvalue") != "1":
                            continue

                        reason_code = tus["RPT_RSN"].get("aunitvalue", "")
                        reason = tus["RPT_RSN"].get_text(strip=True)
                        # (+)/(-) 제거하여 깔끔하게
                        reason = re.sub(r"\s*\([+-]\)\s*$", "", reason)

                        change_text = tes["MDF_STK_CNT"].get_text(strip=True).replace(",", "")
                        try: change = int(change_text)
                        except: continue
                        if change == 0: continue

                        # 날짜
                        mdf_dm = tus.get("MDF_DM")
                        if mdf_dm:
                            dv = mdf_dm.get("aunitvalue", "")
                            if len(dv) == 8:
                                td = f"{dv[:4]}-{dv[4:6]}-{dv[6:8]}"
                            else:
                                dm2 = re.search(r"(\d{4})\s*년?\s*(\d{1,2})\s*월?\s*(\d{1,2})", mdf_dm.get_text(strip=True))
                                td = f"{dm2.group(1)}-{int(dm2.group(2)):02d}-{int(dm2.group(3)):02d}" if dm2 else dd
                        else:
                            td = dd

                        # 가격
                        price = None
                        if "ACI_AMT2" in tes:
                            try: price = int(float(tes["ACI_AMT2"].get_text(strip=True).replace(",", "")))
                            except: pass

                        # trade_type 결정
                        if reason_code in NON_TRADE_CODES:
                            trade_type = "보고"
                        elif change < 0:
                            trade_type = "매도"
                        else:
                            trade_type = "매수"

                        trades.append({
                            "ticker": stock_code, "stock_name": stock_name,
                            "insider_name": name_val, "position": pos_val or None,
                            "trade_type": trade_type, "shares": abs(change),
                            "price": price, "total_amount": price * abs(change) if price else None,
                            "trade_date": td, "disclosure_date": dd,
                            "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
                            "reason": reason, "reason_code": reason_code,
                            "retire_date": retire_date,
                        })
                        tu_found = True

                if tu_found:
                    continue  # <tu> 태그로 파싱 성공 → regex fallback 불필요

                # ── 방법 2: regex fallback (기존 로직, reason 추가) ──
                detail = clean.split("세부변동내역")[-1] if "세부변동내역" in clean else clean
                detail = detail.split("합 계")[0] if "합 계" in detail else detail
                tp = re.compile(r"(장내매[수도]|장외매[수도]|시간외매[수도]|무상(?:신주)?취득|유상(?:신주)?취득|증여취득|상속취득|주식매수선택권행사|스톡옵션행사|처분|취득|신규선임)[^0-9]*?(\d{4})\s*년?\s*(\d{1,2})\s*월?\s*(\d{1,2})\s*일?[^0-9]*?보통주[^0-9]*?([\d,]+)\s+(-?[\d,]+)\s+([\d,]+)\s+([\d,.]+)")
                found = False
                for m in tp.finditer(detail):
                    change = int(m.group(6).replace(",", ""))
                    if change == 0: continue
                    try: price = int(float(m.group(8).replace(",", "")))
                    except: price = None
                    td = f"{m.group(2)}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"
                    reason_text = m.group(1)
                    # 신규선임 등 비거래 → "보고"
                    is_non_trade = reason_text in ("신규선임",)
                    trade_type = "보고" if is_non_trade else ("매도" if change < 0 else "매수")
                    trades.append({
                        "ticker": stock_code, "stock_name": stock_name,
                        "insider_name": name_val, "position": pos_val or None,
                        "trade_type": trade_type, "shares": abs(change),
                        "price": price, "total_amount": price * abs(change) if price else None,
                        "trade_date": td, "disclosure_date": dd,
                        "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
                        "reason": reason_text, "reason_code": None,
                        "retire_date": retire_date,
                    })
                    found = True
                if not found and name_val:
                    cm = re.search(r"증\s*감\s+(-?[\d,]+)", clean)
                    if cm:
                        ch = int(cm.group(1).replace(",", ""))
                        if ch != 0:
                            dm = re.search(r"보고의무발생일\s*:?\s*(\d{4})\s*[년.]?\s*(\d{1,2})\s*[월.]?\s*(\d{1,2})", clean)
                            td = f"{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3)):02d}" if dm else dd
                            pm2 = re.search(r"취득/처분단가[^0-9]*([\d,]+)", clean)
                            pr = int(pm2.group(1).replace(",", "")) if pm2 else None
                            trades.append({
                                "ticker": stock_code, "stock_name": stock_name,
                                "insider_name": name_val, "position": pos_val or None,
                                "trade_type": "매도" if ch < 0 else "매수", "shares": abs(ch),
                                "price": pr, "total_amount": pr * abs(ch) if pr else None,
                                "trade_date": td, "disclosure_date": dd,
                                "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
                                "reason": None, "reason_code": None,
                                "retire_date": retire_date,
                            })
    except Exception as e:
        if str(e): print(f"  WARN: parse error (rcpNo={rcept_no}): {e}")
    return trades

def main():
    stock_code = sys.argv[1] if len(sys.argv) > 1 else "036710"
    stock_name = sys.argv[2] if len(sys.argv) > 2 else None

    corp_code, corp_name = get_corp_code(stock_code)
    if not corp_code: print("ERROR: corp_code not found"); sys.exit(1)
    if not stock_name: stock_name = corp_name

    # elestock (reason 없음 — 구조화 API에 해당 필드 없음)
    ele_items = get_elestock(corp_code)
    trades = []
    for row in ele_items:
        irds = row.get("sp_stock_lmp_irds_cnt", "0").replace(",", "").strip()
        if not irds or irds in ("0", "-"): continue
        try: shares = int(irds)
        except: continue
        if shares == 0: continue
        trades.append({
            "ticker": stock_code, "stock_name": stock_name,
            "insider_name": row.get("repror", "").strip(),
            "position": row.get("isu_exctv_ofcps", "").strip() or None,
            "trade_type": "매도" if shares < 0 else "매수",
            "shares": abs(shares), "price": None, "total_amount": None,
            "trade_date": row.get("rcept_dt", ""),
            "disclosure_date": row.get("rcept_dt", ""),
            "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row.get('rcept_no', '')}",
            "reason": None, "reason_code": None, "retire_date": None,
        })
    print(f"  elestock trades: {len(trades)}")

    # ALL disclosures (전체 기간 — elestock 범위 포함하여 reason/retire_date 확보)
    all_discs = get_old_disclosures(corp_code, "20260401")
    doc_trades = []
    errors = 0
    for i, disc in enumerate(all_discs):
        if (i + 1) % 50 == 0: print(f"  {i+1}/{len(all_discs)} (found: {len(doc_trades)}, errors: {errors})")
        parsed = parse_document(disc["rcept_no"], disc["rcept_dt"], stock_code, stock_name)
        doc_trades.extend(parsed)
        if not parsed: errors += 1
        time.sleep(0.2)
    print(f"  doc trades: {len(doc_trades)} (errors: {errors})")

    # merge: doc_trades 우선 (reason/retire_date 있음), elestock으로 보완
    # elestock 중 document.xml에서 동일 공시(source_url)가 이미 파싱된 건 제외
    doc_urls = {t["source_url"] for t in doc_trades if t.get("source_url")}
    ele_filtered = [t for t in trades if t.get("source_url") not in doc_urls]
    if len(ele_filtered) < len(trades):
        print(f"  elestock {len(trades) - len(ele_filtered)}건 doc_trades와 중복 제거")
    all_trades = doc_trades + ele_filtered
    seen = set()
    unique = []
    for t in all_trades:
        key = (t["insider_name"], t["trade_date"], t["trade_type"], t["shares"])
        if key not in seen: seen.add(key); unique.append(t)
    unique.sort(key=lambda x: x.get("trade_date") or "", reverse=True)

    print(f"\n[4/4] Total: {len(unique)}")
    buys = [t for t in unique if t["trade_type"] == "매수"]
    sells = [t for t in unique if t["trade_type"] == "매도"]
    reports = [t for t in unique if t["trade_type"] == "보고"]
    print(f"  Buy: {len(buys)}, Sell: {len(sells)}, Report(비거래): {len(reports)}")
    retired = [t for t in unique if t.get("retire_date")]
    if retired:
        print(f"  퇴임자: {len(retired)}건")
        for t in retired:
            print(f"    {t['insider_name']} 퇴임일={t['retire_date']} ({t['trade_type']} {t['shares']}주)")
    rc = Counter(t.get("reason") for t in unique if t.get("reason"))
    if rc:
        print(f"  보고사유 분포:")
        for r, c in rc.most_common(): print(f"    {r}: {c}")
    yc = Counter((t.get("trade_date", "")[:4]) for t in unique)
    for y in sorted(yc.keys()): print(f"  {y}: {yc[y]}")
    nc = Counter(t["insider_name"] for t in unique)
    for n, c in nc.most_common(10): print(f"  {n}: {c}")

    out = os.path.join(os.path.dirname(__file__), "..", "data", f"insider_trades_{stock_code}.json")
    with open(os.path.normpath(out), "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {out}")

if __name__ == "__main__":
    main()
