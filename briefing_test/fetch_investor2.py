"""
KRX 투자자별 매매동향 - 다른 API 시도
"""
import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://data.krx.co.kr/",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

result = {}

for date_str in ["20250305", "20250306"]:
    # Try different BLD endpoint for investor trading
    payload = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT02303",
        "locale": "ko_KR", 
        "mktId": "ALL",
        "trdDd": date_str,
        "share": "1",
        "money": "3",
        "csvxls_isNo": "false"
    }
    
    try:
        session = requests.Session()
        # First get the page to set cookies
        session.get("https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020506", 
                   headers={"User-Agent": headers["User-Agent"]}, timeout=10)
        
        r = session.post(
            "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
            headers=headers,
            data=payload,
            timeout=15
        )
        print(f"{date_str}: HTTP {r.status_code}")
        print(f"  Content preview: {r.text[:300]}")
        
        if r.status_code == 200 and r.text.strip():
            data = r.json()
            print(f"  Keys: {list(data.keys())}")
    except Exception as e:
        print(f"  Error: {e}")

# Try naver finance investor data instead
print("\n\nTrying Naver Finance investor data...")
for date_str in ["20250305", "20250306"]:
    # Naver Finance market cap and investor by date
    url = f"https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
    try:
        r = requests.get(url, headers={"User-Agent": headers["User-Agent"]}, timeout=10)
        r.encoding = 'euc-kr'
        print(f"  {date_str} Naver status: {r.status_code}")
        print(f"  Content: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    break  # Just test once
