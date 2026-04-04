"""
Regenerate reason/reason_code/retire_date for all insider_trades.
Only downloads document.xml for rcept_nos already in the DB (from source_url).
Much faster than re-crawling all disclosures.

Usage: python scripts/regen_insider_reasons.py [--start-from TICKER]
"""
import requests, json, time, sys, os, re, zipfile, io, warnings, functools
from datetime import datetime
from collections import defaultdict
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()
print = functools.partial(print, flush=True)

API_KEY = "a75002cc56e408585d6e8baee9c33978ee28388b"
DART_BASE = "https://opendart.fss.or.kr/api"
SUPA_URL = "https://arypzhotxflimroprmdk.supabase.co/rest/v1"
SUPA_KEY = None
NON_TRADE_CODES = {"31", "33", "34", "35", "36", "37", "38", "39", "59", "99"}

def load_supa_key():
    global SUPA_KEY
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env.local")
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                SUPA_KEY = line.strip().split("=", 1)[1]
                return

def supa_headers():
    return {"apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}", "Content-Type": "application/json"}

def parse_doc_reasons(rcept_no):
    """Parse document.xml -> list of {reason, reason_code, trade_type, change, shares, trade_date}, insider_name, retire_date"""
    resp = requests.get(f"{DART_BASE}/document.xml", params={
        "crtfc_key": API_KEY, "rcept_no": rcept_no
    }, timeout=10, verify=False)
    if resp.status_code != 200:
        return [], None, None

    results = []
    insider_name = None
    retire_date = None

    try:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            for fname in zf.namelist():
                raw = zf.read(fname)
                content = None
                for enc in ["euc-kr", "cp949", "utf-8"]:
                    try: content = raw.decode(enc); break
                    except: continue
                if not content: continue

                clean = re.sub(r"<[^>]+>", " ", content)
                clean = re.sub(r"\s+", " ", clean).strip()

                # name
                nm = re.search(r"성명\s*\(?명칭\)?\s*한\s*글\s+([^\s]+)", clean)
                if nm:
                    c = nm.group(1)
                    if not re.search(r"한자|영문|성명|명칭|직위|관계|생년|사업자|주소", c):
                        insider_name = c

                # retire
                tm = re.search(r"퇴임일\s+(\d{4})\s*년?\s*(\d{1,2})\s*월?\s*(\d{1,2})\s*일?", clean)
                if tm:
                    retire_date = f"{tm.group(1)}-{int(tm.group(2)):02d}-{int(tm.group(3)):02d}"

                # <tu>/<te> tags
                soup = BeautifulSoup(content, "html.parser")
                for etable in soup.find_all("table", attrs={"aclass": "EXTRACTION"}):
                    for row in etable.find_all("tr"):
                        tus = {t.get("aunit", ""): t for t in row.find_all("tu")}
                        tes = {t.get("acode", ""): t for t in row.find_all("te")}
                        if "RPT_RSN" not in tus or "MDF_STK_CNT" not in tes:
                            continue
                        str_knd = tus.get("STR_KND")
                        if str_knd and str_knd.get("aunitvalue") != "1":
                            continue

                        reason_code = tus["RPT_RSN"].get("aunitvalue", "")
                        reason = re.sub(r"\s*\([+-]\)\s*$", "", tus["RPT_RSN"].get_text(strip=True))

                        change_text = tes["MDF_STK_CNT"].get_text(strip=True).replace(",", "")
                        try: change = int(change_text)
                        except: continue
                        if change == 0: continue

                        td = None
                        mdf_dm = tus.get("MDF_DM")
                        if mdf_dm:
                            dv = mdf_dm.get("aunitvalue", "")
                            if len(dv) == 8:
                                td = f"{dv[:4]}-{dv[4:6]}-{dv[6:8]}"
                            else:
                                dm2 = re.search(r"(\d{4})\s*년?\s*(\d{1,2})\s*월?\s*(\d{1,2})", mdf_dm.get_text(strip=True))
                                if dm2: td = f"{dm2.group(1)}-{int(dm2.group(2)):02d}-{int(dm2.group(3)):02d}"

                        trade_type = "보고" if reason_code in NON_TRADE_CODES else ("매도" if change < 0 else "매수")
                        results.append({
                            "reason": reason, "reason_code": reason_code,
                            "trade_type": trade_type, "shares": abs(change), "trade_date": td,
                        })
    except Exception:
        pass

    return results, insider_name, retire_date

def process_ticker(ticker, stats):
    """Process one ticker: get existing trades, parse their documents, batch update."""
    # Get existing trades
    existing = []
    offset = 0
    while True:
        resp = requests.get(
            f"{SUPA_URL}/insider_trades?ticker=eq.{ticker}&select=id,insider_name,trade_date,trade_type,shares,source_url,reason&order=trade_date&offset={offset}&limit=1000",
            headers=supa_headers(), verify=False
        )
        data = resp.json()
        if isinstance(data, dict) and "code" in data: break
        if not data: break
        existing.extend(data)
        if len(data) < 1000: break
        offset += 1000

    if not existing:
        return

    # Skip if all already have reason
    needs_update = [e for e in existing if not e.get("reason")]
    if not needs_update:
        stats["skipped_done"] += 1
        return

    # Extract unique rcept_nos from source_url
    rcept_nos = set()
    for e in existing:
        url = e.get("source_url", "")
        m = re.search(r"rcpNo=(\d+)", url)
        if m:
            rcept_nos.add(m.group(1))

    if not rcept_nos:
        return

    if len(rcept_nos) > 50:
        print(f"    {ticker}: {len(rcept_nos)} docs to parse...")

    # Parse each document
    doc_data = {}
    for j, rcept_no in enumerate(rcept_nos):
        try:
            rows, name, retire = parse_doc_reasons(rcept_no)
            if rows:
                doc_data[rcept_no] = (name, retire, rows)
        except Exception:
            pass  # timeout etc
        time.sleep(0.1)

    if not doc_data:
        return

    # Match existing trades to parsed data and collect updates
    update_groups = defaultdict(list)  # (reason, reason_code, retire_date) -> [ids]

    for e in needs_update:
        url = e.get("source_url", "")
        m = re.search(r"rcpNo=(\d+)", url)
        if not m: continue
        rcept_no = m.group(1)
        if rcept_no not in doc_data: continue

        name, retire, rows = doc_data[rcept_no]

        # Find matching row by trade_date + shares + trade_type
        best = None
        for r in rows:
            if r["trade_date"] == e.get("trade_date") and r["shares"] == e.get("shares"):
                # Prefer exact trade_type match
                if r["trade_type"] == e["trade_type"]:
                    best = r
                    break
                # Also match if DB has 매수/매도 but doc says 보고
                if best is None:
                    best = r

        if not best:
            # Fallback: match by shares only (date might differ slightly)
            for r in rows:
                if r["shares"] == e.get("shares"):
                    best = r
                    break

        if best:
            key = (best["reason"], best["reason_code"], retire)
            update_groups[key].append(e["id"])

    # Batch PATCH
    updated = 0
    for (reason, reason_code, retire_date), ids in update_groups.items():
        for i in range(0, len(ids), 100):
            chunk = ids[i:i+100]
            id_filter = ",".join(chunk)
            body = {"reason": reason, "reason_code": reason_code}
            if retire_date:
                body["retire_date"] = retire_date
            resp = requests.patch(
                f"{SUPA_URL}/insider_trades?id=in.({id_filter})",
                headers=supa_headers(), json=body, verify=False
            )
            if resp.status_code < 300:
                updated += len(chunk)

    stats["updated"] += updated
    stats["docs_parsed"] += len(doc_data)

def main():
    load_supa_key()

    start_from = None
    if "--start-from" in sys.argv:
        idx = sys.argv.index("--start-from")
        if idx + 1 < len(sys.argv):
            start_from = sys.argv[idx + 1]

    tickers_path = os.path.join(os.path.dirname(__file__), "..", "tmp_insider_tickers.txt")
    with open(os.path.normpath(tickers_path), "r") as f:
        tickers = [line.strip() for line in f if line.strip()]

    if start_from:
        try:
            idx = tickers.index(start_from)
            tickers = tickers[idx:]
            print(f"Starting from {start_from} ({len(tickers)} remaining)")
        except ValueError:
            pass

    total = len(tickers)
    stats = {"updated": 0, "docs_parsed": 0, "errors": 0, "skipped_done": 0}
    error_log = []
    start_time = time.time()

    print(f"Processing {total} tickers...")
    print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
    print()

    for i, ticker in enumerate(tickers):
        try:
            process_ticker(ticker, stats)
        except Exception as e:
            stats["errors"] += 1
            error_log.append(f"{ticker}: {e}")

        if (i + 1) % 50 == 0 or i == total - 1:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed * 60 if elapsed > 0 else 0
            eta_min = (total - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1}/{total}] updated={stats['updated']} docs={stats['docs_parsed']} errors={stats['errors']} skip={stats['skipped_done']} ({rate:.0f}/min, ETA {eta_min:.0f}min)")

        time.sleep(0.5)  # gentle rate limit between tickers

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed/60:.1f} min")
    print(f"  Updated: {stats['updated']}")
    print(f"  Docs parsed: {stats['docs_parsed']}")
    print(f"  Errors: {stats['errors']}")
    print(f"  Already done (skipped): {stats['skipped_done']}")

    if error_log:
        log_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "regen_errors.log"))
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(error_log))
        print(f"  Error log: {log_path}")

if __name__ == "__main__":
    main()
