import json, os, time, re, requests, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(BASE_DIR, "data", "analyst_pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

def sanitize(s):
    return re.sub(r'[<>:"/\\|?*]', '_', s)

with open(os.path.join(BASE_DIR, "data", "analyst_reports.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

reports = []
for ticker, items in data.items():
    for item in items:
        if item.get("pdf_url"):
            fname = f"{ticker}_{sanitize(item['firm'])}_{item['published_at']}.pdf"
            reports.append((item["pdf_url"], fname))

existing = set(os.listdir(PDF_DIR))
to_download = [(url, fname) for url, fname in reports if fname not in existing]
print(f"Total: {len(reports)}, Existing: {len(existing)}, To download: {len(to_download)}")
sys.stdout.flush()

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://finance.naver.com/"})

downloaded = 0
failed = 0
for i, (url, fname) in enumerate(to_download):
    try:
        resp = session.get(url, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(os.path.join(PDF_DIR, fname), "wb") as f:
                f.write(resp.content)
            downloaded += 1
        else:
            print(f"SKIP {fname}: {resp.status_code} ({len(resp.content)}b)")
            failed += 1
    except Exception as e:
        print(f"FAIL {fname}: {e}")
        failed += 1
    
    if (i + 1) % 20 == 0:
        print(f"Progress: {i+1}/{len(to_download)} (ok={downloaded}, fail={failed})")
        sys.stdout.flush()
    
    time.sleep(2)
    if (i + 1) % 50 == 0 and i + 1 < len(to_download):
        print(f"Resting 60s...")
        sys.stdout.flush()
        time.sleep(60)

total = len([f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')])
print(f"\nDONE: {downloaded} downloaded, {failed} failed, {total} total PDFs on disk")
