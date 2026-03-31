"""DART insider trade crawler. Usage: python crawl_dart_insider.py [STOCK_CODE] [STOCK_NAME]"""
import requests, json, time, sys, os, zipfile, io, re, xml.etree.ElementTree as ET
from html import unescape
from collections import Counter
from bs4 import BeautifulSoup

API_KEY = "a75002cc56e408585d6e8baee9c33978ee28388b"
BASE = "https://opendart.fss.or.kr/api"

def get_corp_code(stock_code):
    print(f"[1/4] corp_code for {stock_code}...")
    resp = requests.get(f"{BASE}/corpCode.xml", params={"crtfc_key": API_KEY}, timeout=60)
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
    resp = requests.get(f"{BASE}/elestock.json", params={"crtfc_key": API_KEY, "corp_code": corp_code, "bgn_de": "20160101", "end_de": "20260329"}, timeout=30)
    data = resp.json()
    items = data.get("list", []) if data.get("status") == "000" else []
    print(f"  {len(items)} items")
    return items

def get_old_disclosures(corp_code, end_date):
    print(f"[3/4] list.json (20160101~{end_date})...")
    all_items = []
    page = 1
    while True:
        resp = requests.get(f"{BASE}/list.json", params={"crtfc_key": API_KEY, "corp_code": corp_code, "bgn_de": "20160101", "end_de": end_date, "pblntf_ty": "D", "page_no": page, "page_count": 100}, timeout=30)
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
    resp = requests.get(f"{BASE}/document.xml", params={"crtfc_key": API_KEY, "rcept_no": rcept_no}, timeout=30)
    if resp.status_code != 200: return []
    trades = []
    try:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            for name in zf.namelist():
                raw = zf.read(name)
                content = None
                for enc in ["euc-kr", "cp949", "utf-8"]:
                    try: content = raw.decode(enc); break
                    except: continue
                if not content: content = raw.decode("utf-8", errors="replace")
                clean = re.sub(r"<[^>]+>", " ", content)
                clean = re.sub(r"\s+", " ", clean).strip()
                clean = unescape(clean).replace("&cr;", " ")
                # 이름 추출: regex 우선 (BS보다 정확)
                name_val = ""
                nm = re.search(r"성명\s*\(?명칭\)?\s*한\s*글\s+([^\s]+)", clean)
                if nm:
                    name_val = nm.group(1)
                # fallback: BeautifulSoup
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
                # 최종 필터: 헤더 패턴이면 빈 문자열
                if name_val and HEADER_PATTERNS.search(name_val):
                    name_val = ""
                # 1글자 이름 경고
                if len(name_val) == 1:
                    print(f"  ⚠ 이름 1글자: '{name_val}' (rcpNo={rcept_no}) - 확인: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}")
                pm = re.search(r"직\s*위\s*명\s+([가-힣A-Za-z()]+)", clean)
                pos_val = pm.group(1).strip() if pm else ""
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
                    dd = f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}"
                    trades.append({"ticker": stock_code, "stock_name": stock_name, "insider_name": name_val, "position": pos_val or None, "trade_type": "매도" if change < 0 else "매수", "shares": abs(change), "price": price, "total_amount": price * abs(change) if price else None, "trade_date": td, "disclosure_date": dd, "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"})
                    found = True
                if not found and name_val:
                    cm = re.search(r"증\s*감\s+(-?[\d,]+)", clean)
                    if cm:
                        ch = int(cm.group(1).replace(",", ""))
                        if ch != 0:
                            dm = re.search(r"보고의무발생일\s*:?\s*(\d{4})\s*[년.]?\s*(\d{1,2})\s*[월.]?\s*(\d{1,2})", clean)
                            td = f"{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3)):02d}" if dm else f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}"
                            dd = f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}"
                            pm2 = re.search(r"취득/처분단가[^0-9]*([\d,]+)", clean)
                            pr = int(pm2.group(1).replace(",", "")) if pm2 else None
                            trades.append({"ticker": stock_code, "stock_name": stock_name, "insider_name": name_val, "position": pos_val or None, "trade_type": "매도" if ch < 0 else "매수", "shares": abs(ch), "price": pr, "total_amount": pr * abs(ch) if pr else None, "trade_date": td, "disclosure_date": dd, "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"})
    except: pass
    return trades

def main():
    stock_code = sys.argv[1] if len(sys.argv) > 1 else "036710"
    stock_name = sys.argv[2] if len(sys.argv) > 2 else None

    corp_code, corp_name = get_corp_code(stock_code)
    if not corp_code: print("ERROR: corp_code not found"); sys.exit(1)
    if not stock_name: stock_name = corp_name

    # elestock
    ele_items = get_elestock(corp_code)
    trades = []
    for row in ele_items:
        irds = row.get("sp_stock_lmp_irds_cnt", "0").replace(",", "").strip()
        if not irds or irds in ("0", "-"): continue
        try: shares = int(irds)
        except: continue
        if shares == 0: continue
        trades.append({"ticker": stock_code, "stock_name": stock_name, "insider_name": row.get("repror", "").strip(), "position": row.get("isu_exctv_ofcps", "").strip() or None, "trade_type": "매도" if shares < 0 else "매수", "shares": abs(shares), "price": None, "total_amount": None, "trade_date": row.get("rcept_dt", ""), "disclosure_date": row.get("rcept_dt", ""), "source_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row.get('rcept_no', '')}"})
    print(f"  elestock trades: {len(trades)}")

    # older docs
    ele_dates = [t["trade_date"] for t in trades if t["trade_date"]]
    end_old = min(ele_dates).replace("-", "") if ele_dates else "20260101"
    old_discs = get_old_disclosures(corp_code, end_old)
    old_trades = []
    errors = 0
    for i, disc in enumerate(old_discs):
        if (i + 1) % 50 == 0: print(f"  {i+1}/{len(old_discs)} (found: {len(old_trades)}, errors: {errors})")
        parsed = parse_document(disc["rcept_no"], disc["rcept_dt"], stock_code, stock_name)
        old_trades.extend(parsed)
        if not parsed: errors += 1
        time.sleep(0.2)
    print(f"  doc trades: {len(old_trades)} (errors: {errors})")

    # merge + dedup
    all_trades = trades + old_trades
    seen = set()
    unique = []
    for t in all_trades:
        key = (t["insider_name"], t["trade_date"], t["trade_type"], t["shares"])
        if key not in seen: seen.add(key); unique.append(t)
    unique.sort(key=lambda x: x.get("trade_date") or "", reverse=True)

    print(f"\n[4/4] Total: {len(unique)}")
    buys = [t for t in unique if t["trade_type"] == "매수"]
    sells = [t for t in unique if t["trade_type"] == "매도"]
    print(f"  Buy: {len(buys)}, Sell: {len(sells)}")
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
