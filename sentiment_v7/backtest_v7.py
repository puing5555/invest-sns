"""
한국 시장 심리지수 v7 - 10년 백테스트 (2015~2026)
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import yfinance as yf
import requests
from scipy.stats import norm
from sentiment_v7 import (
    get_momentum_series,
    get_volatility_series,
    get_safe_haven_series,
    get_junk_bond_series_daily,
    get_ewy_series,
    get_kosdaq_kospi_series,
    zscore_to_percentile,
    INVERTED,
    grade,
)

matplotlib.rcParams['font.family'] = ['Malgun Gothic', 'AppleGothic', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


START = "2015-01-01"
END = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
LOOKBACK_YEARS = 1  # Z-score 정규화 lookback


def load_all_series():
    """전체 기간 데이터 로드"""
    print("전체 시계열 데이터 로드 중...")

    series = {}

    print("  [1/6] 모멘텀...")
    series["모멘텀"] = get_momentum_series(START, END)
    print(f"        {len(series['모멘텀'])}일")

    print("  [2/6] 변동성...")
    series["변동성"] = get_volatility_series(START, END)
    print(f"        {len(series['변동성'])}일")

    print("  [3/6] 안전자산...")
    series["안전자산"] = get_safe_haven_series(START, END)
    print(f"        {len(series['안전자산'])}일")

    print("  [4/6] 정크본드 (월별 ECOS)...")
    # 백테스트용: 연도별 분할 요청
    from sentiment_v7 import get_junk_bond_series_monthly
    series["정크본드"] = get_junk_bond_series_monthly("201501", "202512")
    print(f"        {len(series['정크본드'])}건")

    print("  [5/6] 외국인수급...")
    series["외국인수급"] = get_ewy_series(START, END)
    print(f"        {len(series['외국인수급'])}일")

    print("  [6/6] 코스닥/코스피...")
    series["코스닥코스피"] = get_kosdaq_kospi_series(START, END)
    print(f"        {len(series['코스닥코스피'])}일")

    return series


def compute_rolling_score(all_series: dict, lookback_days: int = 252) -> pd.Series:
    """rolling Z-score CDF로 daily 심리지수 계산"""
    print("\nRolling 심리지수 계산 중...")

    # 공통 날짜 인덱스 (일별 데이터 기준)
    daily_keys = [k for k, s in all_series.items() if len(s) > 100]
    if not daily_keys:
        return pd.Series(dtype=float)

    # 날짜 교집합
    common_idx = all_series[daily_keys[0]].index
    for k in daily_keys[1:]:
        common_idx = common_idx.intersection(all_series[k].index)

    print(f"  공통 날짜: {len(common_idx)}일 ({common_idx[0].date()} ~ {common_idx[-1].date()})")

    # 월별 데이터 (정크본드) - 일별로 forward fill
    monthly_key = "정크본드"
    if monthly_key in all_series and len(all_series[monthly_key]) > 5:
        monthly_s = all_series[monthly_key]
        # 일별 인덱스로 리샘플
        daily_bond = monthly_s.reindex(common_idx, method='ffill')
    else:
        daily_bond = None

    scores = []
    dates = []

    for i, date in enumerate(common_idx):
        if i < lookback_days:
            continue

        lookback_idx = common_idx[i - lookback_days:i + 1]

        score_sum = 0
        count = 0

        for key in daily_keys:
            s = all_series[key]
            s_lb = s.reindex(lookback_idx).dropna()
            current_val = s.get(date, None)

            if current_val is None or pd.isna(current_val) or len(s_lb) < 30:
                continue

            pct = zscore_to_percentile(s_lb, current_val)
            if key in INVERTED:
                pct = 100 - pct
            score_sum += pct
            count += 1

        # 정크본드 (월별)
        if daily_bond is not None:
            bond_lb = daily_bond.reindex(lookback_idx).dropna()
            current_bond = daily_bond.get(date, None)
            if current_bond is not None and not pd.isna(current_bond) and len(bond_lb) >= 10:
                pct = zscore_to_percentile(bond_lb, current_bond)
                pct = 100 - pct  # 역방향
                score_sum += pct
                count += 1

        if count > 0:
            scores.append(score_sum / count)
            dates.append(date)

    result = pd.Series(scores, index=dates, name="sentiment")
    print(f"  계산 완료: {len(result)}일")
    return result


def plot_backtest(sentiment: pd.Series, kospi: pd.Series, output_path: str = "sentiment_v7_backtest.png"):
    """백테스트 차트 생성"""
    print("\n차트 생성 중...")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [2, 1]})
    fig.patch.set_facecolor('#1a1a2e')

    # 심리지수 차트
    ax1.set_facecolor('#16213e')
    ax1.set_xlim(sentiment.index[0], sentiment.index[-1])
    ax1.set_ylim(0, 100)

    # 배경 구간
    ax1.axhspan(0, 20, alpha=0.3, color='darkred', label='극도의공포')
    ax1.axhspan(20, 40, alpha=0.2, color='red', label='공포')
    ax1.axhspan(40, 60, alpha=0.1, color='gray', label='중립')
    ax1.axhspan(60, 80, alpha=0.2, color='green', label='탐욕')
    ax1.axhspan(80, 100, alpha=0.3, color='darkgreen', label='극도의탐욕')

    # 기준선
    for level, color, style in [(20, 'red', '--'), (40, 'salmon', ':'), (60, 'lightgreen', ':'), (80, 'green', '--')]:
        ax1.axhline(y=level, color=color, linestyle=style, alpha=0.5, linewidth=0.8)

    # 심리지수 선
    ax1.plot(sentiment.index, sentiment.values, color='#00d4ff', linewidth=1.2, label='심리지수', zorder=5)
    ax1.fill_between(sentiment.index, sentiment.values, 50, 
                     where=(sentiment.values >= 50), alpha=0.2, color='#00ff88')
    ax1.fill_between(sentiment.index, sentiment.values, 50, 
                     where=(sentiment.values < 50), alpha=0.2, color='#ff4444')

    # 최신 점수 표시
    if not sentiment.empty:
        last_val = sentiment.iloc[-1]
        last_date = sentiment.index[-1]
        grade_str = grade(last_val)
        ax1.scatter([last_date], [last_val], color='#ffff00', s=80, zorder=10)
        ax1.annotate(f'{last_val:.1f} ({grade_str})',
                    xy=(last_date, last_val),
                    xytext=(-80, 15), textcoords='offset points',
                    color='#ffff00', fontsize=11, fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='#ffff00'))

    ax1.set_title('한국 시장 심리지수 v7 (2015~2026)', color='white', fontsize=14, fontweight='bold', pad=10)
    ax1.set_ylabel('심리지수 (0~100)', color='white')
    ax1.tick_params(colors='white')
    ax1.legend(loc='upper left', framealpha=0.3, facecolor='#1a1a2e', labelcolor='white', fontsize=8)
    ax1.spines['bottom'].set_color('#555555')
    ax1.spines['top'].set_color('#555555')
    ax1.spines['left'].set_color('#555555')
    ax1.spines['right'].set_color('#555555')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator())

    # 코스피 차트
    ax2.set_facecolor('#16213e')
    kospi_aligned = kospi.reindex(sentiment.index, method='ffill')
    ax2.plot(kospi_aligned.index, kospi_aligned.values, color='#ffa500', linewidth=1.0, label='코스피')
    ax2.fill_between(kospi_aligned.index, kospi_aligned.values, kospi_aligned.min(), alpha=0.15, color='#ffa500')

    ax2.set_title('코스피 지수', color='white', fontsize=11, pad=5)
    ax2.set_ylabel('포인트', color='white')
    ax2.tick_params(colors='white')
    ax2.legend(loc='upper left', framealpha=0.3, facecolor='#1a1a2e', labelcolor='white', fontsize=8)
    ax2.spines['bottom'].set_color('#555555')
    ax2.spines['top'].set_color('#555555')
    ax2.spines['left'].set_color('#555555')
    ax2.spines['right'].set_color('#555555')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.set_xlim(sentiment.index[0], sentiment.index[-1])

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"  차트 저장: {output_path}")


def get_period_scores(sentiment: pd.Series, year: int, months: list) -> pd.DataFrame:
    """특정 기간 점수 조회"""
    rows = []
    for m in months:
        mask = (sentiment.index.year == year) & (sentiment.index.month == m)
        period_data = sentiment[mask]
        for date, score in period_data.items():
            rows.append({
                "날짜": date.strftime("%Y-%m-%d"),
                "점수": round(score, 1),
                "등급": grade(score)
            })
    return pd.DataFrame(rows)


def main():
    print(f"{'='*60}")
    print(f"한국 시장 심리지수 v7 - 백테스트 ({START} ~ 오늘)")
    print(f"{'='*60}\n")

    # 1. 데이터 로드
    all_series = load_all_series()

    # 2. 코스피 데이터 로드
    print("\n코스피 데이터 로드...")
    ks_df = yf.download("^KS11", start=START, end=END, progress=False, auto_adjust=True)
    kospi = ks_df['Close'].squeeze()

    # 3. Rolling 심리지수 계산
    sentiment = compute_rolling_score(all_series, lookback_days=252)

    if sentiment.empty:
        print("ERROR: 심리지수 계산 실패")
        return

    # 4. 차트 생성
    plot_backtest(sentiment, kospi)

    # 5. 2025년 1~2월 점수 출력
    print("\n=== 2025년 1~2월 심리지수 ===")
    df_2025 = get_period_scores(sentiment, 2025, [1, 2])
    if not df_2025.empty:
        print(df_2025.to_string(index=False))
    else:
        print("2025년 1~2월 데이터 없음")

    # 통계 요약
    print(f"\n=== 백테스트 통계 ===")
    print(f"기간: {sentiment.index[0].date()} ~ {sentiment.index[-1].date()}")
    print(f"평균 점수: {sentiment.mean():.1f}")
    print(f"최저: {sentiment.min():.1f} ({sentiment.idxmin().date()})")
    print(f"최고: {sentiment.max():.1f} ({sentiment.idxmax().date()})")
    print(f"현재: {sentiment.iloc[-1]:.1f} ({grade(sentiment.iloc[-1])})")

    # 결과 저장
    sentiment_df = pd.DataFrame({
        'date': sentiment.index.strftime('%Y-%m-%d'),
        'score': sentiment.round(1).values,
        'grade': [grade(s) for s in sentiment.values]
    })
    sentiment_df.to_csv("backtest_scores.csv", index=False, encoding='utf-8-sig')
    print("\nbacktest_scores.csv 저장 완료")

    return sentiment, df_2025


if __name__ == "__main__":
    sentiment, df_2025 = main()
