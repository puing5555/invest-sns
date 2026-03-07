"""
run_backtest.py — 전체 실행 + 결과 보고서 생성
"""

import os
import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# 작업 디렉토리 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from fetch_data import (load_all_data, PAIR_MAP, KR_TICKERS,
                        US_TICKERS)
from backtest_engine import run_all_pairs, summarize_pair
from plot_results import plot_all


def fmt(val, decimals=2, suffix="%"):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    return f"{val:.{decimals}f}{suffix}"


def build_surge_stats(all_results):
    """급등 폭별 전체 집계"""
    buckets = {"5~10%": {"A": [], "B": [], "C": []},
               "10~15%": {"A": [], "B": [], "C": []},
               "15%+": {"A": [], "B": [], "C": []}}

    for us_t, pairs in all_results.items():
        for kr_code, info in pairs.items():
            df = info["results"]
            if df.empty:
                continue
            for _, row in df.iterrows():
                bucket = row["surge_class"]
                if bucket not in buckets:
                    continue
                for sc in ["A", "B", "C"]:
                    v = row[f"return_{sc}"]
                    if v is not None and not pd.isna(v):
                        buckets[bucket][sc].append(v)

    result = {}
    for cat, scens in buckets.items():
        result[cat] = {}
        for sc, vals in scens.items():
            result[cat][sc] = round(np.mean(vals), 2) if vals else None
    return result


def build_size_stats(all_results):
    """대형 vs 중형 분리 집계"""
    size_data = {"대형": {"A": [], "B": [], "C": []},
                 "중형": {"A": [], "B": [], "C": []}}

    for us_t, pairs in all_results.items():
        for kr_code, info in pairs.items():
            if kr_code not in KR_TICKERS:
                continue
            size = KR_TICKERS[kr_code][2]
            df = info["results"]
            if df.empty:
                continue
            for _, row in df.iterrows():
                for sc in ["A", "B", "C"]:
                    v = row[f"return_{sc}"]
                    if v is not None and not pd.isna(v) and size in size_data:
                        size_data[size][sc].append(v)

    result = {}
    for size, scens in size_data.items():
        result[size] = {}
        for sc, vals in scens.items():
            result[size][sc] = {
                "avg":      round(np.mean(vals), 2) if vals else None,
                "win_rate": round(np.mean([v > 0 for v in vals]) * 100, 1) if vals else None,
                "n":        len(vals),
            }
    return result


def build_weekday_stats(all_results):
    """요일 효과"""
    wd_data = {"월~목": {"A": [], "B": [], "C": []},
               "금요일": {"A": [], "B": [], "C": []}}

    for us_t, pairs in all_results.items():
        for kr_code, info in pairs.items():
            df = info["results"]
            if df.empty:
                continue
            for _, row in df.iterrows():
                wg = row["weekday_group"]
                if wg not in wd_data:
                    continue
                for sc in ["A", "B", "C"]:
                    v = row[f"return_{sc}"]
                    if v is not None and not pd.isna(v):
                        wd_data[wg][sc].append(v)

    result = {}
    for wg, scens in wd_data.items():
        result[wg] = {}
        for sc, vals in scens.items():
            result[wg][sc] = round(np.mean(vals), 2) if vals else None
    return result


def build_crcl_stats(all_results):
    """CRCL 케이스 별도 분석"""
    if "CRCL" not in all_results:
        return None, []

    crcl_pairs = all_results["CRCL"]
    crcl_lines = []

    all_signals = []
    for kr_code, info in crcl_pairs.items():
        df = info["results"]
        if df.empty:
            continue
        # 10%+ 시그널만
        df10 = df[df["us_pct"] >= 10].copy()
        all_signals.append(df10)
        if df10.empty:
            continue
        s = summarize_pair(df10)
        kr_name = info["name"]
        line = f"  {kr_name}({kr_code}): 시그널 {s['signals']}회"
        for sc_key in ["A", "B", "C"]:
            ss = s.get(sc_key, {})
            if ss and ss.get("avg") is not None:
                line += f" | {sc_key}: {fmt(ss['avg'])} (승률 {fmt(ss['win_rate'], 1, '%')})"
        crcl_lines.append(line)

    return crcl_pairs, crcl_lines


def global_stats(all_results):
    """전체 합산 통계"""
    all_A, all_B, all_C = [], [], []
    for us_t, pairs in all_results.items():
        for kr_code, info in pairs.items():
            df = info["results"]
            if df.empty:
                continue
            all_A.extend(df["return_A"].dropna().tolist())
            all_B.extend(df["return_B"].dropna().tolist())
            all_C.extend(df["return_C"].dropna().tolist())

    def s(vals):
        if not vals:
            return {"avg": None, "win_rate": None, "n": 0}
        return {
            "avg":      round(np.mean(vals), 2),
            "win_rate": round(np.mean([v > 0 for v in vals]) * 100, 1),
            "n":        len(vals),
        }

    return {"A": s(all_A), "B": s(all_B), "C": s(all_C)}


def generate_report(all_results, us_status, kr_status,
                    surge_stats, size_stats, weekday_stats,
                    crcl_pairs, crcl_lines, g_stats,
                    save_path="results_backtest.md"):

    lines = []
    A = lambda s: lines.append(s)

    A("# 미국-한국 연동 단타 전략 백테스트 결과")
    A("")
    A("## 기간: 2023-01-01 ~ 2026-03-07")
    A("## 데이터: yfinance (미국) + pykrx/yfinance (한국)")
    A("")
    A("---")
    A("")
    A("## 데이터 수집 현황")
    A("")
    A("### 미국")
    for t, st in us_status.items():
        A(f"- {t}: {st}")
    A("")
    A("### 한국")
    for code, st in kr_status.items():
        name = KR_TICKERS[code][0] if code in KR_TICKERS else code
        A(f"- {code} {name}: {st}")
    A("")
    A("---")
    A("")
    A("## 페어별 결과")
    A("")

    # US 티커 그룹핑
    US_SECTOR_MAP = {
        "NVDA": "반도체", "AMD": "반도체", "SMCI": "반도체",
        "TSLA": "2차전지", "AAPL": "IT부품",
        "AMZN": "물류", "CRCL": "크립토", "COIN": "크립토",
        "META": "IT서비스", "GOOG": "IT서비스", "MSFT": "IT서비스",
        "AVGO": "반도체", "ARM": "반도체",
    }

    for us_ticker in US_TICKERS:
        if us_ticker not in all_results:
            A(f"### {us_ticker} 연동")
            A(f"데이터 없음\n")
            continue

        sector = US_SECTOR_MAP.get(us_ticker, "")
        A(f"### {us_ticker} 연동 ({sector})")
        A("")

        pairs = all_results[us_ticker]
        if not pairs:
            A("연동 종목 없음\n")
            continue

        for kr_code, info in pairs.items():
            kr_name = info["name"]
            s = info["summary"]
            size = KR_TICKERS[kr_code][2] if kr_code in KR_TICKERS else ""

            A(f"#### [{us_ticker} → {kr_name}({kr_code})] {size}")
            A(f"시그널 발생: {s.get('signals', 0)}회")

            if s.get("signals", 0) == 0:
                A("(시그널 없음)\n")
                continue

            for sc_key, sc_label in [("A", "당일 종가"), ("B", "2일 후"), ("C", "3일 후")]:
                ss = s.get(sc_key, {})
                if ss and ss.get("n", 0) > 0:
                    A(f"{sc_key}) {sc_label}: "
                      f"평균 {fmt(ss.get('avg'))}, "
                      f"승률 {fmt(ss.get('win_rate'), 1, '%')}, "
                      f"최대 +{fmt(ss.get('max'))}, "
                      f"최대 -{fmt(abs(ss.get('min', 0)) if ss.get('min') is not None else None)}")
                else:
                    A(f"{sc_key}) {sc_label}: N/A")
            A("")

    A("---")
    A("")
    A("## 전체 종합")
    A("")
    gs = g_stats
    A(f"전략 평균 수익률: "
      f"A={fmt(gs['A']['avg'])}, "
      f"B={fmt(gs['B']['avg'])}, "
      f"C={fmt(gs['C']['avg'])}")
    A(f"전략 승률: "
      f"A={fmt(gs['A']['win_rate'], 1, '%')}, "
      f"B={fmt(gs['B']['win_rate'], 1, '%')}, "
      f"C={fmt(gs['C']['win_rate'], 1, '%')}")
    A(f"전체 시그널 수: "
      f"A={gs['A']['n']}회, "
      f"B={gs['B']['n']}회, "
      f"C={gs['C']['n']}회")
    A("")

    # 대형 vs 중형
    A("### 대형주 vs 중형주")
    A("")
    for size in ["대형", "중형"]:
        ss = size_stats.get(size, {})
        parts = []
        for sc in ["A", "B", "C"]:
            d = ss.get(sc, {})
            avg = d.get("avg")
            wr = d.get("win_rate")
            n = d.get("n", 0)
            parts.append(f"{sc}: {fmt(avg)} (승률 {fmt(wr, 1, '%')}, n={n})")
        A(f"**{size}주**: " + " | ".join(parts))
    A("")

    # 알파 판단
    large_A = size_stats.get("대형", {}).get("A", {}).get("avg")
    mid_A   = size_stats.get("중형", {}).get("A", {}).get("avg")
    if large_A is not None and mid_A is not None:
        alpha = mid_A - large_A
        A(f"→ 중형주 알파 (A기준): **{fmt(alpha)}**")
        if alpha > 0:
            A("→ 중형주가 대형주 대비 초과수익 ✅")
        else:
            A("→ 대형주가 더 안정적 📊")
    A("")

    A("---")
    A("")
    A("## 급등 폭별")
    A("")
    for cat in ["5~10%", "10~15%", "15%+"]:
        ss = surge_stats.get(cat, {})
        parts = [f"{sc}: {fmt(ss.get(sc))}" for sc in ["A", "B", "C"]]
        A(f"**{cat}**: " + " | ".join(parts))
    A("")

    A("---")
    A("")
    A("## 요일 효과")
    A("")
    for wg in ["월~목", "금요일"]:
        ss = weekday_stats.get(wg, {})
        parts = [f"{sc}: {fmt(ss.get(sc))}" for sc in ["A", "B", "C"]]
        A(f"**{wg}**: " + " | ".join(parts))
    A("")

    # 월~목 vs 금요일 비교
    wt_A = weekday_stats.get("월~목", {}).get("A")
    fr_A = weekday_stats.get("금요일", {}).get("A")
    if wt_A is not None and fr_A is not None:
        A(f"→ 월~목 vs 금요일 차이(A기준): {fmt(wt_A - fr_A)}")
        if wt_A > fr_A:
            A("→ 월~목 급등이 더 효과적 📈")
        else:
            A("→ 금요일 급등이 더 효과적 📈")
    A("")

    A("---")
    A("")
    A("## CRCL 케이스")
    A("")
    if crcl_lines:
        A("CRCL 10%+ 급등일 → 한국 크립토 연동 종목 수익률:")
        A("")
        for line in crcl_lines:
            A(line)
    else:
        A("CRCL 데이터 없음 (상장 초기 데이터 미비 가능)")
    A("")

    A("---")
    A("")
    A("## 결론")
    A("")

    # 전략 유효성 판단
    avg_A = gs["A"]["avg"]
    wr_A  = gs["A"]["win_rate"]
    valid = (avg_A is not None and avg_A > 0.3 and
             wr_A  is not None and wr_A  > 50)

    A(f"**이 전략이 유효한가?: {'YES ✅' if valid else 'MARGINAL / NO ⚠️'}**")
    A("")
    A("**근거:**")
    A(f"- 전체 평균 수익률(A): {fmt(avg_A)}")
    A(f"- 전체 승률(A): {fmt(wr_A, 1, '%')}")

    # 최고 페어 찾기
    best_pair = None
    best_avg  = -999
    for us_t, pairs in all_results.items():
        for kr_code, info in pairs.items():
            s = info["summary"]
            if s.get("A") and s["A"].get("avg") is not None:
                if s["A"]["avg"] > best_avg:
                    best_avg  = s["A"]["avg"]
                    best_pair = f"{us_t}→{info['name']}"

    if best_pair:
        A(f"- 최고 페어(A기준): **{best_pair}** ({fmt(best_avg)})")

    # 급등 폭 권장
    surge_avgs = {cat: surge_stats.get(cat, {}).get("A") for cat in ["5~10%", "10~15%", "15%+"]}
    valid_surges = {k: v for k, v in surge_avgs.items() if v is not None}
    if valid_surges:
        best_surge = max(valid_surges, key=valid_surges.get)
        A(f"- 최적 진입 기준: **{best_surge} 급등** (평균 {fmt(valid_surges[best_surge])})")

    A("")
    A("**invest-sns 기능 추천:**")
    A("- 미국 장 마감 후 5%+ 급등 종목 자동 스크리닝")
    A("- 연동 한국 종목 다음 날 매수 알림 발송")
    if valid:
        A("- 당일 종가 매도(시나리오 A) 우선 전략 적용 권장")
    else:
        A("- 시그널 필터 강화 필요: 10%+ 급등 또는 특정 섹터 한정 적용 권장")
    A("- 요일 필터: 금요일 급등 시그널 별도 처리 (주말 리스크 반영)")
    A("")
    A("---")
    A("*생성일: 2026-03-07*")

    report = "\n".join(lines)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"보고서 저장: {save_path}")
    return report


def main():
    print("=" * 60)
    print("미국-한국 연동 단타 전략 백테스트 시작")
    print("=" * 60)

    # 1. 데이터 수집
    us_data, kr_data, us_status, kr_status = load_all_data()

    # 2. 백테스트 실행
    print("\n백테스트 실행 중...")
    all_results = run_all_pairs(us_data, kr_data, PAIR_MAP, KR_TICKERS, threshold=5.0)

    # 3. 통계 계산
    surge_stats   = build_surge_stats(all_results)
    size_stats    = build_size_stats(all_results)
    weekday_stats = build_weekday_stats(all_results)
    crcl_pairs, crcl_lines = build_crcl_stats(all_results)
    g_stats       = global_stats(all_results)

    print("\n전체 통계:")
    gs = g_stats
    print(f"  전략 평균 수익률: A={fmt(gs['A']['avg'])}, B={fmt(gs['B']['avg'])}, C={fmt(gs['C']['avg'])}")
    print(f"  전략 승률:        A={fmt(gs['A']['win_rate'], 1, '%')}, "
          f"B={fmt(gs['B']['win_rate'], 1, '%')}, C={fmt(gs['C']['win_rate'], 1, '%')}")

    # 4. 차트 생성
    print("\n차트 생성 중...")
    chart_path  = os.path.join(SCRIPT_DIR, "backtest_results.png")
    report_path = os.path.join(SCRIPT_DIR, "results_backtest.md")

    try:
        plot_all(all_results, surge_stats, save_path=chart_path)
    except Exception as e:
        print(f"차트 생성 오류: {e}")

    # 5. 보고서 생성
    report = generate_report(
        all_results, us_status, kr_status,
        surge_stats, size_stats, weekday_stats,
        crcl_pairs, crcl_lines, g_stats,
        save_path=report_path,
    )

    print("\n" + "=" * 60)
    print("완료!")
    print(f"  보고서: {report_path}")
    print(f"  차트:   {chart_path}")
    print("=" * 60)
    return report


if __name__ == "__main__":
    report = main()
    print("\n" + "=" * 60)
    print("results_backtest.md 내용:")
    print("=" * 60)
    print(report)
