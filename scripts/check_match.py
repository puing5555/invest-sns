import os, requests, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env.local')
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
r = requests.get(f'{url}/rest/v1/analyst_reports?select=id,firm,ticker,published_at&ai_summary=is.null&pdf_url=not.is.null', headers={'apikey': key, 'Authorization': f'Bearer {key}'})
reports = r.json()
pdf_dir = Path('data/analyst_pdfs')
found = 0
missing = []
for rpt in reports:
    fname = f"{rpt['ticker']}_{rpt['firm']}_{rpt['published_at']}.pdf"
    f = pdf_dir / fname
    if f.exists():
        found += 1
    else:
        missing.append(fname)
print(f'Total: {len(reports)}, Found: {found}, Missing: {len(missing)}')
for m in missing[:5]:
    print(f'  MISSING: {m}')
