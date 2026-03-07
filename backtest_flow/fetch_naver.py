"""
네이버 금융 수급 데이터 수집 모듈
- 기관/외국인 순매매량 일별 데이터
- 주가 데이터 (yfinance 또는 pykrx)
"""
import os
import sys
import time
import pickle
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
START_DATE = "2023-01-01"
END_DATE   = "2026-03-07"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.naver.com/',
    'Accept-Language': 'ko-KR,ko;q=0.9',
}

# ── KOSPI200 대표 종목 (하드코딩 + 동적 보완) ──────────────────────────────
KOSPI200_SAMPLE = [
    "005930", "000660", "005490", "005380", "035420",  # 삼성전자, SK하이닉스, POSCO, 현대차, NAVER
    "000270", "051910", "006400", "028260", "207940",  # 기아, LG화학, 삼성SDI, 삼성물산, 삼성바이오
    "003550", "034730", "012330", "066570", "096770",  # LG, SK, 현대모비스, LG전자, SK이노베이션
    "003490", "032830", "011170", "004020", "010130",  # 대한항공, 삼성생명, 롯데케미칼, 고려아연, 고려아연
    "068270", "000810", "015760", "316140", "105560",  # 셀트리온, 삼성화재, 한국전력, 우리금융, KB금융
    "055550", "086790", "032640", "017670", "030200",  # 신한금융, 하나금융, LG유플러스, SK텔레콤, KT
    "024110", "000100", "047050", "036570", "009150",  # 기업은행, 유한양행, 한국금융지주, NC소프트, 삼성전기
    "011200", "010950", "003670", "005940", "042660",  # HMM, S-Oil, 포스코케미칼, NH투자증권, 대우조선
    "097950", "018260", "000720", "009540", "001040",  # CJ제일제당, 삼성에스디에스, 현대건설, 한국조선해양, CJ
    "001450", "002790", "010140", "021240", "010780",  # 현대해상, 아모레G, 삼성중공업, 코웨이, IS동서
]


def get_kospi_tickers_naver():
    """네이버에서 KOSPI 대형주 리스트 - 시가총액 상위"""
    try:
        url = 'https://finance.naver.com/sise/sise_market_sum.naver'
        params = {'sosok': '0', 'page': 1}  # kospi
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        r.encoding = 'euc-kr'
        soup = BeautifulSoup(r.text, 'html.parser')
        tickers = []
        for a in soup.select('a.tltle'):
            href = a.get('href', '')
            if 'code=' in href:
                code = href.split('code=')[-1].strip()
                if code:
                    tickers.append(code)
        return tickers
    except Exception as e:
        print(f"네이버 종목 조회 실패: {e}")
        return []


def fetch_naver_flow(ticker, start=START_DATE, end=END_DATE, max_pages=42):
    """
    네이버 금융에서 기관/외국인 순매수 일별 데이터 수집
    컬럼: 날짜, 종가, 기관, 외국인, 개인(계산)
    """
    url = 'https://finance.naver.com/item/frgn.naver'
    all_rows = []

    for page in range(1, max_pages + 1):
        try:
            r = requests.get(url, params={'code': ticker, 'page': page},
                           headers=HEADERS, timeout=10)
            r.encoding = 'euc-kr'
            soup = BeautifulSoup(r.text, 'html.parser')

            # type2 테이블 중 날짜/기관/외국인 포함 테이블
            tables = soup.find_all('table', class_='type2')
            data_table = None
            for t in tables:
                headers_row = t.find_all('th')
                header_text = ' '.join([h.get_text(strip=True) for h in headers_row])
                if '날짜' in header_text and '기관' in header_text:
                    data_table = t
                    break

            if data_table is None:
                break

            rows = data_table.find_all('tr')
            page_data = []
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cols) >= 6 and cols[0] and '.' in cols[0]:
                    try:
                        date_str = cols[0].replace('.', '-')
                        page_data.append({
                            '날짜': pd.to_datetime(date_str),
                            '종가': int(cols[1].replace(',', '')),
                            '기관': int(cols[5].replace(',', '').replace('+', '')),
                            '외국인': int(cols[6].replace(',', '').replace('+', '')),
                        })
                    except (ValueError, IndexError):
                        pass

            if not page_data:
                break

            # 날짜 범위 체크
            min_date = min(r['날짜'] for r in page_data)
            all_rows.extend(page_data)

            if min_date < pd.to_datetime(start):
                break

            time.sleep(0.1)

        except Exception as e:
            break

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates('날짜').sort_values('날짜').set_index('날짜')
    df = df[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]

    # 개인 = -(기관 + 외국인) (간략 추정)
    df['개인'] = -(df['기관'] + df['외국인'])

    return df if len(df) > 0 else None


def fetch_naver_price(ticker, start=START_DATE, end=END_DATE):
    """네이버 금융 주가 데이터"""
    try:
        # pykrx로 시도
        from pykrx import stock
        df = stock.get_market_ohlcv_by_date(
            start.replace('-', ''), end.replace('-', ''), ticker
        )
        if df is not None and not df.empty:
            df.index = pd.to_datetime(df.index)
            return df
    except Exception:
        pass

    # yfinance 폴백
    try:
        import yfinance as yf
        yt = f"{ticker}.KS"
        df = yf.download(yt, start=start, end=end, auto_adjust=True, progress=False)
        if df is not None and not df.empty:
            # 컬럼명 한글로 변환
            col_map = {'Open': '시가', 'High': '고가', 'Low': '저가', 'Close': '종가', 'Volume': '거래량'}
            df = df.rename(columns=col_map)
            df.index = pd.to_datetime(df.index)
            return df
    except Exception:
        pass

    return None


def collect_data(tickers, max_tickers=50):
    """전체 데이터 수집"""
    all_flow = {}
    all_price = {}
    failed = []

    sample = tickers[:max_tickers]
    print(f"\n📦 네이버 금융 수급 데이터 수집: {len(sample)}개 종목")
    print(f"   기간: {START_DATE} ~ {END_DATE}")

    for idx, ticker in enumerate(tqdm(sample, desc="수집")):
        try:
            flow  = fetch_naver_flow(ticker)
            price = fetch_naver_price(ticker)

            if flow is not None and price is not None and len(flow) > 50:
                all_flow[ticker]  = flow
                all_price[ticker] = price
            else:
                failed.append(ticker)

            time.sleep(0.1)
        except Exception as e:
            print(f"\n오류 {ticker}: {e}")
            failed.append(ticker)

        # 10개마다 중간 저장
        if (idx + 1) % 10 == 0 or (idx + 1) == len(sample):
            save_data(all_flow, all_price, failed)
            print(f"\n[중간저장] {idx+1}/{len(sample)} 완료, 수집 {len(all_flow)}개")

    print(f"\n✅ 수집 완료: {len(all_flow)}개 / 실패: {len(failed)}개")
    if failed:
        print(f"   실패 종목(일부): {failed[:10]}")

    return all_flow, all_price, failed


def save_data(all_flow, all_price, failed, fname="naver_flow_data.pkl"):
    path = os.path.join(DATA_DIR, fname)
    with open(path, "wb") as f:
        pickle.dump({"flow": all_flow, "price": all_price, "failed": failed}, f)
    print(f"💾 저장: {path}")


def load_data(fname="naver_flow_data.pkl"):
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        return None, None, []
    with open(path, "rb") as f:
        d = pickle.load(f)
    print(f"📂 캐시 로드: {len(d['flow'])}개 종목")
    return d["flow"], d["price"], d.get("failed", [])


if __name__ == "__main__":
    all_flow, all_price, failed = load_data()

    if not all_flow:
        # 종목 리스트
        tickers = KOSPI200_SAMPLE
        print(f"샘플 종목 {len(tickers)}개 사용")

        all_flow, all_price, failed = collect_data(tickers, max_tickers=50)
        save_data(all_flow, all_price, failed)

    if all_flow:
        sample = next(iter(all_flow))
        print(f"\n수급 샘플 ({sample}):")
        print(all_flow[sample].tail(5))
        print(f"\n주가 샘플 ({sample}):")
        print(all_price[sample].tail(3))
        print(f"\n수급 컬럼: {all_flow[sample].columns.tolist()}")
        print(f"주가 컬럼: {all_price[sample].columns.tolist()}")
