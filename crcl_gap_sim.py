import yfinance as yf
import pandas as pd

tickers = {
    "헥토파이낸셜": "234340.KS",
    "FSN": "214270.KQ",
    "카카오": "035720.KS",
    "카카오페이": "377300.KS",
    "NAVER": "035420.KS",
}

results = []

for name, ticker in tickers.items():
    try:
        df = yf.download(ticker, start="2026-02-24", end="2026-03-03", auto_adjust=True, progress=False)
        if len(df) == 0:
            print(f"❌ {name}: 데이터 없음")
            continue

        # 날짜 인덱스 정리
        df.index = pd.to_datetime(df.index).tz_localize(None)

        # 2/25, 2/26, 2/27 날짜 찾기
        dates = df.index.tolist()
        print(f"\n{name} ({ticker}) 수집된 날짜: {[d.strftime('%Y-%m-%d') for d in dates]}")

        # 전일 종가 (2/25)
        d_prev = pd.Timestamp("2026-02-25")
        # 당일 (2/26)
        d_cur = pd.Timestamp("2026-02-26")
        # 2일 후 (2/27)
        d_next = pd.Timestamp("2026-02-27")

        # 날짜 매핑 (가장 가까운 날짜 사용)
        def find_nearest(target, date_list):
            candidates = [d for d in date_list if abs((d - target).days) <= 2]
            if candidates:
                return min(candidates, key=lambda d: abs((d - target).days))
            return None

        d_prev_actual = find_nearest(d_prev, dates)
        d_cur_actual = find_nearest(d_cur, dates)
        d_next_actual = find_nearest(d_next, dates)

        prev_close = df.loc[d_prev_actual, "Close"].item() if d_prev_actual in df.index else None
        cur_open = df.loc[d_cur_actual, "Open"].item() if d_cur_actual in df.index else None
        cur_high = df.loc[d_cur_actual, "High"].item() if d_cur_actual in df.index else None
        cur_close = df.loc[d_cur_actual, "Close"].item() if d_cur_actual in df.index else None
        next_close = df.loc[d_next_actual, "Close"].item() if d_next_actual in df.index else None

        gap_pct = (cur_open - prev_close) / prev_close * 100 if prev_close and cur_open else None
        ret_close = (cur_close - cur_open) / cur_open * 100 if cur_open and cur_close else None
        ret_high = (cur_high - cur_open) / cur_open * 100 if cur_open and cur_high else None
        ret_2d = (next_close - cur_open) / cur_open * 100 if cur_open and next_close else None

        row = {
            "종목": name,
            "전일종가(2/25)": round(prev_close) if prev_close else "N/A",
            "시가(2/26)": round(cur_open) if cur_open else "N/A",
            "갭업률": f"{gap_pct:+.2f}%" if gap_pct is not None else "N/A",
            "당일고가": round(cur_high) if cur_high else "N/A",
            "당일종가": round(cur_close) if cur_close else "N/A",
            "시가→종가": f"{ret_close:+.2f}%" if ret_close is not None else "N/A",
            "시가→고가(최대)": f"{ret_high:+.2f}%" if ret_high is not None else "N/A",
            "시가→2일후": f"{ret_2d:+.2f}%" if ret_2d is not None else "N/A",
        }
        results.append(row)

        print(f"  전일종가(2/25): {prev_close}")
        print(f"  시가(2/26): {cur_open} | 갭업률: {gap_pct:+.2f}%" if gap_pct else "")
        print(f"  당일고가: {cur_high} | 당일종가: {cur_close}")
        print(f"  시가→종가: {ret_close:+.2f}% | 시가→고가: {ret_high:+.2f}% | 시가→2일후: {ret_2d:+.2f}%" if all(x is not None for x in [ret_close, ret_high, ret_2d]) else "")

    except Exception as e:
        print(f"❌ {name}: {e}")

print("\n\n===== 최종 결과 =====")
if results:
    result_df = pd.DataFrame(results)
    print(result_df.to_string(index=False))
