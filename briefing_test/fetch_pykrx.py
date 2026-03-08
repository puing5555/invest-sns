"""
fetch_pykrx.py - KOSPI/KOSDAQ 지수 + 수급 데이터 수집
- KOSPI/KOSDAQ OHLCV: Naver Finance (fchart) - EUC-KR 인코딩 직접 처리
- 수급(외국인/기관/개인): pykrx get_market_trading_value_by_investor
  - Python 3.14 호환: iloc 사용 (컬럼명 인코딩 무관)
"""

import sys
import io
import json
import requests
import re
from datetime import datetime, timedelta

# Python 3.14 UTF-8 mode 우회 - stdout 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

result = {}


# ---------------------
# 1) 날짜 계산 헬퍼
# ---------------------
def get_recent_trading_days(n=7):
    """최근 n영업일 날짜 리스트 (YYYY-MM-DD, 과거순)"""
    days = []
    current = datetime.now()
    while len(days) < n:
        current -= timedelta(days=1)
        if current.weekday() < 5:  # 0=월 ~ 4=금
            days.append(current.strftime('%Y-%m-%d'))
    return sorted(days)


def to_yyyymmdd(d: str) -> str:
    """YYYY-MM-DD → YYYYMMDD"""
    return d.replace('-', '')


# ---------------------
# 2) Naver Finance 지수 OHLCV
# ---------------------
def fetch_naver_index(symbol: str, count: int = 10) -> dict:
    """
    Naver Finance에서 지수 일봉 데이터를 가져온다.
    symbol: 'KOSPI' | 'KOSDAQ'
    returns: {date_str: {open, high, low, close}, ...}
    """
    url = 'http://fchart.stock.naver.com/sise.nhn'
    params = {
        'symbol': symbol,
        'timeframe': 'day',
        'count': str(count),
        'requestType': '0',
    }
    resp = requests.get(url, params=params, timeout=10)
    # Naver 응답은 EUC-KR 인코딩 XML
    text = resp.content.decode('euc-kr', errors='replace')

    data = {}
    # <item data="20260303|2550.00|2580.00|2530.00|2560.00|12345" />
    for m in re.finditer(r'<item data="([^"]+)"', text):
        parts = m.group(1).split('|')
        if len(parts) < 5:
            continue
        raw_date = parts[0]  # YYYYMMDD
        d = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
        try:
            data[d] = {
                'open':  float(parts[1]),
                'high':  float(parts[2]),
                'low':   float(parts[3]),
                'close': float(parts[4]),
            }
        except ValueError:
            pass
    return data


# KOSPI OHLCV
try:
    kospi_data = fetch_naver_index('KOSPI', count=10)
    for d, ohlcv in kospi_data.items():
        result.setdefault(d, {})['KOSPI_pykrx'] = ohlcv
    print(f"KOSPI: {len(kospi_data)}일 데이터 수집 완료")
    for d in sorted(kospi_data)[-3:]:
        print(f"  {d}: {kospi_data[d]}")
except Exception as e:
    print(f"KOSPI error: {e}")

# KOSDAQ OHLCV
try:
    kosdaq_data = fetch_naver_index('KOSDAQ', count=10)
    for d, ohlcv in kosdaq_data.items():
        result.setdefault(d, {})['KOSDAQ_pykrx'] = ohlcv
    print(f"KOSDAQ: {len(kosdaq_data)}일 데이터 수집 완료")
except Exception as e:
    print(f"KOSDAQ error: {e}")


# ---------------------
# 3) 수급 데이터 (pykrx) - iloc 사용 (Python 3.14 EUC-KR 호환)
# ---------------------
# pykrx get_market_trading_value_by_investor
# 행 순서: 개인(0), 기관합계(1), ..., 외국인합계(-2), 전체(-1)
# 컬럼 순서: 매수, 매도, 순매수(마지막 = iloc[:, -1])
try:
    from pykrx import stock

    trading_days = get_recent_trading_days(n=5)
    print(f"\n수급 조회 대상: {trading_days}")

    for date_str_dash in trading_days:
        date_str = to_yyyymmdd(date_str_dash)
        try:
            df = stock.get_market_trading_value_by_investor(date_str, date_str, 'KOSPI')
            if df is None or df.empty:
                print(f"수급 {date_str}: 데이터 없음 (공휴일 또는 API 미응답)")
                continue

            # iloc 사용 - 컬럼명/인덱스 인코딩 무관
            net_col = df.iloc[:, -1]   # 순매수 = 마지막 컬럼

            inv_map = {
                'individual':  int(net_col.iloc[0]),   # 개인 (행 0)
                'institution': int(net_col.iloc[1]),   # 기관합계 (행 1)
                'foreign':     int(net_col.iloc[-2]),  # 외국인합계 (행 -2)
            }
            result.setdefault(date_str_dash, {})['investors'] = inv_map
            print(f"수급 {date_str_dash}: {inv_map}")

        except Exception as e:
            print(f"수급 {date_str} error: {type(e).__name__}: {e}")

except ImportError:
    print("pykrx 미설치 - 수급 데이터 건너뜀")
except Exception as e:
    print(f"pykrx 초기화 error: {e}")


# ---------------------
# 4) JSON 저장
# ---------------------
output_path = 'pykrx_data.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n저장 완료: {output_path}")
print(f"날짜 수: {len(result)}")
print("날짜 목록:", sorted(result.keys()))
