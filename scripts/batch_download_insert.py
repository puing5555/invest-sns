#!/usr/bin/env python3
"""Batch: Download PDFs + Insert to Supabase analyst_reports"""
import json, os, time, requests, re

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PDF_DIR = os.path.join(DATA_DIR, "analyst_pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

def sanitize(s):
    return re.sub(r'[<>:"/\\|?*]', '_', s)

def load_reports():
    with open(os.path.join(DATA_DIR, "analyst_reports.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    reports = []
    for ticker, items in data.items():
        for item in items:
            item["ticker"] = ticker
            reports.append(item)
    return reports

def pdf_filename(r):
    return f"{r['ticker']}_{sanitize(r['firm'])}_{r['published_at']}.pdf"

def download_pdfs(reports):
    existing = set(os.listdir(PDF_DIR))
    to_download = [(r, pdf_filename(r)) for r in reports if r.get("pdf_url") and pdf_filename(r) not in existing]
    print(f"PDFs: {len(existing)} existing, {len(to_download)} to download")
    
    downloaded = 0
    failed = 0
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://finance.naver.com/"})
    
    for i, (r, fname) in enumerate(to_download):
        try:
            resp = session.get(r["pdf_url"], timeout=30)
            if resp.status_code == 200 and len(resp.content) > 1000:
                with open(os.path.join(PDF_DIR, fname), "wb") as f:
                    f.write(resp.content)
                downloaded += 1
            else:
                print(f"  SKIP {fname}: status={resp.status_code} size={len(resp.content)}")
                failed += 1
        except Exception as e:
            print(f"  FAIL {fname}: {e}")
            failed += 1
        
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(to_download)} (ok={downloaded}, fail={failed})")
        
        time.sleep(2)
        if (i + 1) % 50 == 0:
            print(f"  Resting 60s after {i+1} downloads...")
            time.sleep(60)
    
    total_pdfs = len(os.listdir(PDF_DIR))
    print(f"Download done: {downloaded} new, {failed} failed, {total_pdfs} total PDFs")
    return downloaded, failed

def insert_to_supabase(reports):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal"
    }
    
    rows = []
    for r in reports:
        rows.append({
            "ticker": r["ticker"],
            "firm": r["firm"],
            "analyst_name": r.get("analyst", ""),
            "title": r["title"],
            "target_price": r.get("target_price"),
            "opinion": r.get("opinion", ""),
            "published_at": r["published_at"],
            "pdf_url": r.get("pdf_url", ""),
            "summary": r.get("summary", "")
        })
    
    # Insert in batches of 50
    inserted = 0
    errors = 0
    for i in range(0, len(rows), 50):
        batch = rows[i:i+50]
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/analyst_reports",
            headers=headers,
            json=batch
        )
        if resp.status_code in (200, 201):
            inserted += len(batch)
        else:
            print(f"  Batch {i}-{i+len(batch)} error: {resp.status_code} {resp.text[:200]}")
            errors += len(batch)
        
        if (i + 50) % 200 == 0:
            print(f"  Insert progress: {min(i+50, len(rows))}/{len(rows)}")
    
    print(f"Insert done: {inserted} ok, {errors} errors, total attempted: {len(rows)}")
    return inserted, errors

if __name__ == "__main__":
    reports = load_reports()
    print(f"Loaded {len(reports)} reports")
    
    # Step 1: Insert to DB first (fast)
    print("\n=== DB INSERT ===")
    ins_ok, ins_err = insert_to_supabase(reports)
    
    # Step 2: Download PDFs (slow)
    print("\n=== PDF DOWNLOAD ===")
    dl_ok, dl_fail = download_pdfs(reports)
    
    print(f"\n=== SUMMARY ===")
    print(f"DB: {ins_ok} inserted, {ins_err} errors")
    print(f"PDF: {dl_ok} downloaded, {dl_fail} failed")
