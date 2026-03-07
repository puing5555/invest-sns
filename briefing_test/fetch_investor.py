"""
KRX 투자자별 매매동향 수집
POST https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd
"""
import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020506",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

result = {}

for date_str in ["20250305", "20250306"]:
    # KOSPI investor trading by date
    payload = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT02303",
        "locale": "ko_KR",
        "mktId": "STK",  # KOSPI
        "trdDd": date_str,
        "share": "1",
        "money": "3",  # 억원
        "csvxls_isNo": "false"
    }
    try:
        r = requests.post(
            "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
            headers=headers,
            data=payload,
            timeout=15
        )
        data = r.json()
        print(f"\n{date_str} KOSPI investor data keys: {list(data.keys())}")
        
        # Parse investor data
        if "output" in data:
            inv_result = {}
            for row in data["output"]:
                print(f"  Row: {row}")
                inv_name = row.get("INVST_TP_NM", row.get("invstTpNm", ""))
                net_buy = row.get("NETBUY_TRDVAL", row.get("netbuyTrdval", 0))
                if "외국인" in str(inv_name):
                    inv_result["foreign"] = net_buy
                elif "기관" in str(inv_name):
                    inv_result["institution"] = net_buy
                elif "개인" in str(inv_name):
                    inv_result["individual"] = net_buy
            d = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
            result[d] = {"investors": inv_result}
            print(f"  Parsed: {inv_result}")
        else:
            print(f"  No 'output' key. Full response: {str(data)[:500]}")
    except Exception as e:
        print(f"  Error: {e}")

with open("investor_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\nSaved to investor_data.json")
