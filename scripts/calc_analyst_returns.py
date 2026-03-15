"""
애널리스트 리포트 Forward Return 계산기

리포트 발행일 기준으로 3개월/6개월/12개월 후 주가를 yfinance로 조회하여
실제 수익률을 계산합니다.

사용법: python scripts/calc_analyst_returns.py
옵션:  python scripts/calc_analyst_returns.py --force  (전부 재계산)

필요 패키지: pip install yfinance
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("❌ yfinance 패키지 필요: pip install yfinance")
    sys.exit(1)

# ============================================================
# 설정
# ============================================================
DATA_DIR = Path(__file__).parent.parent / "data"
REPORTS_FILE = DATA_DIR / "analyst_reports.json"
OUT_FILE = DATA_DIR / "analyst_reports.json"  # 같은 파일에 덮어쓰기

# KRX 종목코드 → yfinance ticker 매핑
def to_yf_ticker(ticker_code):
    """KRX 6자리 코드 → yfinance 한국 종목 형식"""
    return f"{ticker_code}.KS"

# Forward return 기간 (일)
PERIODS = {
    "return_3m": 90,
    "return_6m": 180,
    "return_12m": 365,
}

# ============================================================
# 가격 캐시 (API 호출 최소화)
# ============================================================
price_cache = {}  # {ticker: DataFrame}

def get_price_on_date(ticker_code, target_date_str):
    """특정 날짜의 종가 조회 (±5 영업일 허용)"""
    yf_ticker = to_yf_ticker(ticker_code)
    
    if yf_ticker not in price_cache:
        try:
            # 3년 + 여유분 데이터 한번에 다운로드
            stock = yf.Ticker(yf_ticker)
            hist = stock.history(period="5y")
            if hist.empty:
                price_cache[yf_ticker] = None
                return None
            price_cache[yf_ticker] = hist
        except Exception as e:
            print(f"  ⚠️ {yf_ticker} 가격 다운로드 실패: {e}")
            price_cache[yf_ticker] = None
            return None
    
    hist = price_cache[yf_ticker]
    if hist is None:
        return None
    
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    
    # ±5 영업일 범위에서 가장 가까운 거래일 찾기
    for delta in range(0, 6):
        for sign in [0, 1, -1]:
            check_date = target_date + timedelta(days=delta * (1 if sign >= 0 else -1))
            check_str = check_date.strftime("%Y-%m-%d")
            
            matching = hist.index[hist.index.strftime("%Y-%m-%d") == check_str]
            if len(matching) > 0:
                return float(hist.loc[matching[0], "Close"])
    
    return None


def calc_forward_return(ticker_code, published_at, days):
    """발행일 기준 N일 후 수익률 계산"""
    pub_date = datetime.strptime(published_at, "%Y-%m-%d")
    target_date = pub_date + timedelta(days=days)
    
    # 아직 미래면 계산 불가
    if target_date > datetime.now():
        return None
    
    price_at_pub = get_price_on_date(ticker_code, published_at)
    price_at_target = get_price_on_date(ticker_code, target_date.strftime("%Y-%m-%d"))
    
    if price_at_pub and price_at_target and price_at_pub > 0:
        return round(((price_at_target - price_at_pub) / price_at_pub) * 100, 2)
    
    return None


# ============================================================
# 메인
# ============================================================
def main():
    force = "--force" in sys.argv
    
    print("📊 애널리스트 리포트 Forward Return 계산기")
    print(f"📁 입력: {REPORTS_FILE}")
    
    # 데이터 로드
    with open(REPORTS_FILE, "r", encoding="utf-8") as f:
        reports_data = json.load(f)
    
    total = sum(len(v) for v in reports_data.values())
    print(f"📋 총 {total}건 / {len(reports_data)}개 종목")
    
    # 종목별 처리
    processed = 0
    calculated = 0
    skipped = 0
    
    tickers = list(reports_data.keys())
    
    for idx, ticker in enumerate(tickers):
        reports = reports_data[ticker]
        ticker_name = ticker  # 이름은 JSON에 없으니 코드로 표시
        
        print(f"\n[{idx+1}/{len(tickers)}] {ticker} ({len(reports)}건)")
        
        # 가격 데이터 사전 로드
        yf_ticker = to_yf_ticker(ticker)
        if yf_ticker not in price_cache:
            try:
                stock = yf.Ticker(yf_ticker)
                hist = stock.history(period="5y")
                price_cache[yf_ticker] = hist if not hist.empty else None
                if hist.empty:
                    print(f"  ⚠️ 가격 데이터 없음, 스킵")
                    continue
                print(f"  ✅ 가격 데이터 로드: {len(hist)}일")
            except Exception as e:
                print(f"  ❌ 가격 로드 실패: {e}")
                price_cache[yf_ticker] = None
                continue
        
        for report in reports:
            processed += 1
            
            # 이미 계산된 건 스킵 (force 아닐 때)
            if not force and report.get("return_12m") is not None:
                skipped += 1
                continue
            
            pub_date = report.get("published_at")
            if not pub_date:
                continue
            
            # 발행일 주가
            price_at_signal = get_price_on_date(ticker, pub_date)
            if price_at_signal:
                report["price_at_signal"] = round(price_at_signal)
            
            # 현재가
            hist = price_cache.get(yf_ticker)
            if hist is not None and not hist.empty:
                report["price_current"] = round(float(hist.iloc[-1]["Close"]))
            
            # Forward returns
            for key, days in PERIODS.items():
                ret = calc_forward_return(ticker, pub_date, days)
                report[key] = ret
                if ret is not None:
                    calculated += 1
            
            # 목표가 달성 여부
            if report.get("target_price") and report.get("price_current"):
                report["target_achieved"] = report["price_current"] >= report["target_price"]
        
        # 중간 출력
        ticker_calced = sum(1 for r in reports if r.get("return_12m") is not None)
        print(f"  📈 수익률 계산: {ticker_calced}/{len(reports)}건")
    
    # 저장
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(reports_data, f, ensure_ascii=False, indent=2)
    
    # 통계
    all_reports = [r for reports in reports_data.values() for r in reports]
    has_3m = sum(1 for r in all_reports if r.get("return_3m") is not None)
    has_6m = sum(1 for r in all_reports if r.get("return_6m") is not None)
    has_12m = sum(1 for r in all_reports if r.get("return_12m") is not None)
    
    print(f"\n{'='*50}")
    print(f"✅ 완료!")
    print(f"📊 처리: {processed}건 (스킵: {skipped}건)")
    print(f"📈 3개월 수익률: {has_3m}건")
    print(f"📈 6개월 수익률: {has_6m}건")  
    print(f"📈 12개월 수익률: {has_12m}건")
    print(f"📁 저장: {OUT_FILE}")


if __name__ == "__main__":
    main()
