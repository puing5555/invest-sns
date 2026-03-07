"""
수급 기반 백테스트 - 데이터 수집 모듈
KOSPI200 종목의 투자자별 순매수 + 주가 데이터 수집
"""
import os
import time
import pickle
import pandas as pd
from tqdm import tqdm

try:
    from pykrx import stock
    PYKRX_OK = True
except ImportError:
    PYKRX_OK = False
    print("⚠️ pykrx 없음")

START = "20230101"
END   = "20260307"
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def get_kospi200_tickers():
    """KOSPI200 구성종목 리스트"""
    try:
        tickers = stock.get_index_portfolio_deposit_file("1028")
        print(f"KOSPI200 종목 수: {len(tickers)}")
        return list(tickers)
    except Exception as e:
        print(f"❌ KOSPI200 종목 조회 실패: {e}")
        return []


def fetch_investor_flow(ticker, start=START, end=END):
    """종목별 투자자 순매수 일별 데이터"""
    try:
        df = stock.get_market_trading_value_by_date(start, end, ticker)
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        return None


def fetch_price_data(ticker, start=START, end=END):
    """종목별 OHLCV 데이터"""
    try:
        df = stock.get_market_ohlcv_by_date(start, end, ticker)
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        return None


def collect_all_data(tickers, max_tickers=50, sleep=0.3):
    """전체 종목 데이터 수집"""
    all_flow = {}
    all_price = {}
    failed = []

    sample = tickers[:max_tickers]
    print(f"\n📦 데이터 수집 시작: {len(sample)}개 종목 ({START} ~ {END})")

    for ticker in tqdm(sample, desc="수집"):
        flow = fetch_investor_flow(ticker)
        price = fetch_price_data(ticker)

        if flow is not None and price is not None:
            all_flow[ticker] = flow
            all_price[ticker] = price
        else:
            failed.append(ticker)

        time.sleep(sleep)

    print(f"\n✅ 수집 완료: {len(all_flow)}개 / 실패: {len(failed)}개")
    if failed:
        print(f"   실패 종목: {failed[:10]}{'...' if len(failed)>10 else ''}")

    return all_flow, all_price, failed


def save_data(all_flow, all_price, failed):
    path = os.path.join(DATA_DIR, "flow_data.pkl")
    with open(path, "wb") as f:
        pickle.dump({"flow": all_flow, "price": all_price, "failed": failed}, f)
    print(f"💾 저장 완료: {path}")


def load_data():
    path = os.path.join(DATA_DIR, "flow_data.pkl")
    if not os.path.exists(path):
        return None, None, []
    with open(path, "rb") as f:
        d = pickle.load(f)
    print(f"📂 캐시 로드: {len(d['flow'])}개 종목")
    return d["flow"], d["price"], d.get("failed", [])


if __name__ == "__main__":
    # 캐시 있으면 재사용
    all_flow, all_price, failed = load_data()
    if not all_flow:
        tickers = get_kospi200_tickers()
        if not tickers:
            print("종목 리스트 획득 실패 - 종료")
            exit(1)
        all_flow, all_price, failed = collect_all_data(tickers, max_tickers=50)
        save_data(all_flow, all_price, failed)

    # 컬럼명 확인용
    if all_flow:
        sample_ticker = next(iter(all_flow))
        print(f"\n📋 수급 컬럼 ({sample_ticker}): {all_flow[sample_ticker].columns.tolist()}")
        print(f"📋 주가 컬럼 ({sample_ticker}): {all_price[sample_ticker].columns.tolist()}")
