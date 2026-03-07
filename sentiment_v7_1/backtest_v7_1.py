"""
한국 시장 심리지수 v7.1 - 10년 백테스트 (2015~2026)
"""
import warnings
warnings.filterwarnings('ignore')

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import yfinance as yf

from sentiment_v7_1 import (
    get_momentum_series,
    get_stock_strength_series,
    get_market_breadth_series,
    get_volatility_series,
    get_safe_haven_series,
    get_junk_bond_series_daily,
    get_ewy_series,
    get_credit_balance_series,
    get_customer_deposit_series,
    get_kosdaq_kospi_series,
    zscore_to_percentile,
    INVERTED,
    grade,
)

matplotlib.rcParams['font.family'] = ['Malgun Gothic', 'AppleGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

START = "2015-01-01"
END = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
LOOKBACK_DAYS = 252  # Z-score 정규화 lookback (1년)


def load_all_series(include_stock_indices=True):
    """전체 기간 데이터 로드"""
    print("전체 시계열 데이터 로드 중...")
    series = {}

    print("  [1/10] 모멘텀...")
    series["모멘텀"] = get_momentum_series(START, END)

    if include_stock_indices:
        print("  [2/10] 주가강도 (느림, 20개 종목 다운로드)...")
        series["주가강도"] = get_stock_strength_series(START, END)

        print("  [3/10] 시장폭...")
        series["시장폭"] = get_market_breadth_series(START, END)

    print("  [4/10] 변동성...")
    series["변동성"] = get_volatility_series(START, END)

    print("  [5/10] 안전자산...")
    series["안전자산"] = get_safe_haven_series(START, END)

    print("  [6/10] 정크본드 (ECOS - 느림)...")
    series["정크본드"] = get_junk_bond_series_daily(START, datetime.today().strftime("%Y-%m-%d"))

    print("  [7/10] 외국인수급 (EWY)...")
    series["외국인수급"] = get_ewy_series(START, END)

    print("  [8/10] 신용잔고 (KOFIA)...")
    series["신용잔고"] = get_credit_balance_series("2015-01-01", END)

    print("  [9/10] 고객예탁금 (KOFIA)...")
    series["고객예탁금"] = get_customer_deposit_series("2015-01-01", END)

    print("  [10/10] 코스닥/코스피...")
    series["코스닥코스피"] = get_kosdaq_kospi_series(START, END)

    for k, v in series.items():
        if v is not None:
            print(f"    {k}: {len(v)}일")

    return series


def compute_daily_scores(series_map: dict) -> pd.Series:
    """
    각 날짜별 rolling Z-score CDF로 점수 계산
    lookback: 1년(252 거래일)
    """
    valid_keys = [k for k, v in series_map.items() if v is not None and not v.empty]
    print(f"\n점수 계산 중... 지표: {valid_keys}")

    # 공통 날짜 범위 확보
    # KOFIA 데이터는 주간 업데이트이므로 forward-fill
    all_dates = set()
    for key in valid_keys:
        s = series_map[key]
        if s is not None and not s.empty:
            all_dates.update(s.index.tolist())

    all_dates = sorted(all_dates)

    # KOSPI 거래일 기준으로 맞추기
    ks = yf.download("^KS11", start=START, end=END, progress=False, auto_adjust=True)
    trading_days = ks.index.tolist()

    scores = {}
    total = len(trading_days)

    for i, date in enumerate(trading_days):
        if i % 200 == 0:
            print(f"    {date.strftime('%Y-%m-%d')} ({i}/{total})")

        window_start_idx = max(0, i - LOOKBACK_DAYS)
        window_days = trading_days[window_start_idx:i+1]

        if len(window_days) < 50:
            continue

        component_scores = []
        for key in valid_keys:
            s = series_map[key]
            if s is None or s.empty:
                continue

            # rolling window
            window_data = s[s.index.isin(window_days)]
            if window_data.empty:
                # Try to find nearest available date
                available = s[s.index <= date]
                if available.empty:
                    continue
                # Forward-fill gap (KOFIA data)
                window_data_all = s[s.index <= date].tail(LOOKBACK_DAYS)
                if len(window_data_all) < 5:
                    continue
                current_val = window_data_all.iloc[-1]
                window_data = window_data_all
            else:
                current_val = window_data.iloc[-1]

            if len(window_data) < 5:
                continue

            score = zscore_to_percentile(window_data, current_val)
            if key in INVERTED:
                score = 100 - score
            component_scores.append(score)

        if component_scores:
            weight = 1.0 / len(component_scores)
            total_score = sum(s * weight for s in component_scores)
            scores[date] = round(total_score, 1)

    return pd.Series(scores, dtype=float)


def plot_backtest(scores: pd.Series, ks_prices: pd.Series):
    """백테스트 차트 생성"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True,
                                    gridspec_kw={'height_ratios': [1, 2]})

    # 심리지수 색상 구역
    ax1.fill_between(scores.index, 0, 20, alpha=0.15, color='darkred', label='극도의공포')
    ax1.fill_between(scores.index, 20, 40, alpha=0.15, color='red', label='공포')
    ax1.fill_between(scores.index, 40, 60, alpha=0.15, color='gray', label='중립')
    ax1.fill_between(scores.index, 60, 80, alpha=0.15, color='lightgreen', label='탐욕')
    ax1.fill_between(scores.index, 80, 100, alpha=0.15, color='darkgreen', label='극도의탐욕')
    ax1.plot(scores.index, scores.values, color='navy', linewidth=1.2, label='심리지수 v7.1')
    ax1.axhline(50, color='black', linestyle='--', alpha=0.3)
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("심리지수 (0~100)")
    ax1.set_title("한국 시장 심리지수 v7.1 (10개 지표, 2015~2026)", fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=8, ncol=5)

    # 최근 값 표시
    if not scores.empty:
        latest_date = scores.index[-1]
        latest_val = scores.iloc[-1]
        ax1.annotate(f"{latest_val:.1f} ({grade(latest_val)})",
                     xy=(latest_date, latest_val),
                     xytext=(10, -20), textcoords='offset points',
                     fontsize=10, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    # KOSPI 차트
    if ks_prices is not None and not ks_prices.empty:
        ax2.plot(ks_prices.index, ks_prices.values, color='steelblue', linewidth=1.2, label='KOSPI')
        ax2.set_ylabel("KOSPI")
        ax2.legend(loc='upper left')

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=0)
    plt.tight_layout()

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentiment_v7_1_backtest.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"차트 저장: {output_path}")
    return output_path


def get_period_scores(scores: pd.Series, start_date: str, end_date: str) -> pd.DataFrame:
    """특정 기간 일별 점수 반환"""
    mask = (scores.index >= pd.Timestamp(start_date)) & (scores.index <= pd.Timestamp(end_date))
    period_scores = scores[mask].copy()
    df = pd.DataFrame({
        'date': period_scores.index,
        'score': period_scores.values,
        'grade': [grade(s) for s in period_scores.values]
    })
    return df


if __name__ == "__main__":
    import json

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 1. 데이터 로드
    print("="*65)
    print("한국 시장 심리지수 v7.1 - 10년 백테스트")
    print("="*65)

    # Note: include_stock_indices=False for faster backtest
    # Individual stock data takes a long time
    # Set to True for full 10-indicator backtest
    FULL_BACKTEST = True  # Set False for quick test without stocks

    series = load_all_series(include_stock_indices=FULL_BACKTEST)

    # 2. 일별 점수 계산
    print("\n일별 점수 계산 시작...")
    scores = compute_daily_scores(series)
    print(f"총 {len(scores)}일 계산 완료")

    # 3. 저장
    scores.to_csv("backtest_scores_v7_1.csv", header=["score"])
    print("backtest_scores_v7_1.csv 저장 완료")

    # 4. KOSPI 가격
    ks = yf.download("^KS11", start=START, end=END, progress=False, auto_adjust=True)
    ks_close = ks['Close'].squeeze()

    # 5. 차트
    print("차트 생성 중...")
    plot_backtest(scores, ks_close)

    # 6. 통계
    print("\n=== 백테스트 통계 ===")
    print(f"기간: {scores.index[0].strftime('%Y-%m-%d')} ~ {scores.index[-1].strftime('%Y-%m-%d')}")
    print(f"평균: {scores.mean():.1f}")
    print(f"최저: {scores.min():.1f} ({scores.idxmin().strftime('%Y-%m-%d')})")
    print(f"최고: {scores.max():.1f} ({scores.idxmax().strftime('%Y-%m-%d')})")
    print(f"현재: {scores.iloc[-1]:.1f} ({grade(scores.iloc[-1])})")

    # 7. 2025년 1~2월 점수
    print("\n=== 2025년 1~2월 일별 점수 ===")
    df_2025 = get_period_scores(scores, "2025-01-01", "2025-02-28")
    for _, row in df_2025.iterrows():
        print(f"  {row['date'].strftime('%Y-%m-%d')}: {row['score']:.1f} ({row['grade']})")

    # 8. JSON 결과
    result = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "latest_date": scores.index[-1].strftime("%Y-%m-%d"),
        "latest_score": float(scores.iloc[-1]),
        "latest_grade": grade(float(scores.iloc[-1])),
        "stats": {
            "mean": float(scores.mean()),
            "min": float(scores.min()),
            "min_date": scores.idxmin().strftime('%Y-%m-%d'),
            "max": float(scores.max()),
            "max_date": scores.idxmax().strftime('%Y-%m-%d'),
        },
        "period_2025_jan_feb": df_2025.to_dict('records') if not df_2025.empty else []
    }
    with open("backtest_result_v7_1.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print("\nbacktest_result_v7_1.json 저장 완료")
