"""
수급 기반 백테스트 실행 스크립트
결과: results_flow_backtest.md
"""
import os
import sys
import time
import pickle
import warnings
import pandas as pd
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_flow_data import (
    get_kospi200_tickers, collect_all_data, save_data, load_data
)
from backtest_flow import (
    strategy1_foreign_consecutive,
    strategy2_institution_foreign_switch,
    strategy3_smart_money,
    summarize_results,
    top_bottom_tickers,
)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
HOLD_DAYS = [5, 10, 20]


# ── 데이터 수집 ──────────────────────────────────────────────────────────────
def get_data():
    all_flow, all_price, failed = load_data()
    if not all_flow:
        print("📡 pykrx 데이터 수집 중...")
        tickers = get_kospi200_tickers()
        if not tickers:
            print("❌ 종목 리스트 획득 실패")
            sys.exit(1)
        all_flow, all_price, failed = collect_all_data(tickers, max_tickers=50, sleep=0.3)
        save_data(all_flow, all_price, failed)
    return all_flow, all_price, failed


# ── 전략 1 실행 ──────────────────────────────────────────────────────────────
def run_strategy1(all_flow, all_price):
    print("\n📊 전략 1: 외국인 연속 순매수 실행 중...")
    s1_results = {}
    for consec in [2, 3, 5, 7, 10]:
        all_res = []
        for ticker, flow_df in all_flow.items():
            price_df = all_price[ticker]
            res = strategy1_foreign_consecutive(flow_df.copy(), price_df, consec, HOLD_DAYS)
            if res is not None and len(res) > 0:
                res["ticker"] = ticker
                all_res.append(res)
        if all_res:
            s1_results[consec] = pd.concat(all_res, ignore_index=True)
        else:
            s1_results[consec] = pd.DataFrame()
        print(f"  연속 {consec}일: 시그널 {sum(len(r) for r in all_res)}건")
    return s1_results


# ── 전략 2 실행 ──────────────────────────────────────────────────────────────
def run_strategy2(all_flow, all_price):
    print("\n📊 전략 2: 기관+외국인 동시 전환 실행 중...")
    s2_results = {}
    for confirm in [1, 2, 3]:
        all_res = []
        for ticker, flow_df in all_flow.items():
            price_df = all_price[ticker]
            res = strategy2_institution_foreign_switch(flow_df.copy(), price_df, confirm, HOLD_DAYS)
            if res is not None and len(res) > 0:
                res["ticker"] = ticker
                all_res.append(res)
        if all_res:
            s2_results[confirm] = pd.concat(all_res, ignore_index=True)
        else:
            s2_results[confirm] = pd.DataFrame()
        print(f"  확인 {confirm}일: 시그널 {sum(len(r) for r in all_res)}건")
    return s2_results


# ── 전략 3 실행 ──────────────────────────────────────────────────────────────
def run_strategy3(all_flow, all_price):
    print("\n📊 전략 3: 스마트머니 실행 중...")
    s3_results = {}
    for confirm in [1, 2, 3]:
        res = strategy3_smart_money(all_flow, all_price, confirm, HOLD_DAYS, top_n=10)
        s3_results[confirm] = res if res is not None else pd.DataFrame()
        print(f"  확인 {confirm}일: 시그널 {len(s3_results[confirm])}건")
    return s3_results


# ── 보고서 생성 ──────────────────────────────────────────────────────────────
def format_table_row(label, summary, hold_days=[5, 10, 20]):
    r5  = summary.get("5일",  {})
    r10 = summary.get("10일", {})
    r20 = summary.get("20일", {})
    sig = r5.get("시그널수", 0) or r10.get("시그널수", 0) or r20.get("시그널수", 0)

    def fmt(d, key):
        v = d.get(key)
        return f"{v:+.1f}%" if v is not None else "N/A"

    def fmtw(d):
        v = d.get("승률")
        return f"{v:.1f}%" if v is not None else "N/A"

    return (f"| {label:<8} | {sig:>6}회 | "
            f"{fmt(r5,'평균수익률'):>8} | {fmt(r10,'평균수익률'):>9} | {fmt(r20,'평균수익률'):>9} | "
            f"{fmtw(r5):>7} | {fmtw(r10):>7} |")


def find_best(results_dict, metric="평균수익률", hold="10일"):
    best_key = None
    best_val = -9999
    for key, df in results_dict.items():
        if df.empty:
            continue
        s = summarize_results(df, HOLD_DAYS)
        v = s.get(hold, {}).get(metric, None)
        if v is not None and v > best_val:
            best_val = v
            best_key = key
    return best_key, best_val


def generate_report(all_flow, all_price, failed, s1, s2, s3):
    lines = []
    lines.append("# 수급 기반 단타/스윙 전략 백테스트 결과")
    lines.append("")
    lines.append(f"- **백테스트 기간**: 2023-01-01 ~ 2026-03-07")
    lines.append(f"- **분석 종목 수**: {len(all_flow)}개 (KOSPI200 샘플 50개)")
    lines.append(f"- **수집 실패 종목**: {len(failed)}개")
    if failed:
        lines.append(f"  - 실패 목록(일부): {', '.join(failed[:20])}")
    lines.append("")

    # ── 전략 1 ──
    lines.append("---")
    lines.append("## 전략 1: 외국인 연속 순매수 — 연속 일수별 비교")
    lines.append("")
    lines.append("| 연속일수 | 시그널수 | 5일수익률 | 10일수익률 | 20일수익률 | 5일승률 | 10일승률 |")
    lines.append("|---------|---------|---------|----------|----------|--------|--------|")

    s1_summaries = {}
    for consec in [2, 3, 5, 7, 10]:
        df = s1.get(consec, pd.DataFrame())
        s = summarize_results(df, HOLD_DAYS) if not df.empty else {}
        s1_summaries[consec] = s
        lines.append(format_table_row(f"{consec}일", s))

    lines.append("")

    # 최적 연속일수 판단 (10일 수익률 기준)
    best_consec, best_s1_val = find_best(s1, "평균수익률", "10일")
    if best_consec is not None:
        best_s = s1_summaries[best_consec]
        r10 = best_s.get("10일", {})
        lines.append(f"**최적 진입 일수: {best_consec}일**  "
                     f"(10일 평균수익률 {best_s1_val:+.2f}%, "
                     f"승률 {r10.get('승률','N/A')}%, "
                     f"시그널수 {r10.get('시그널수','N/A')}건)")

    # 상위 종목
    if best_consec and not s1.get(best_consec, pd.DataFrame()).empty:
        top, bot = top_bottom_tickers(s1[best_consec], hold_day=10, n=5)
        if top:
            lines.append("")
            lines.append(f"**상위 5 종목 (10일 평균수익률, 연속 {best_consec}일 조건):**")
            for tk, val in top.items():
                lines.append(f"  - {tk}: {val:+.2f}%")
        if bot:
            lines.append(f"**하위 5 종목:**")
            for tk, val in bot.items():
                lines.append(f"  - {tk}: {val:+.2f}%")

    lines.append("")

    # ── 전략 2 ──
    lines.append("---")
    lines.append("## 전략 2: 기관+외국인 동시 순매수 전환 — 확인 일수별")
    lines.append("")
    lines.append("| 확인일수 | 시그널수 | 5일수익률 | 10일수익률 | 20일수익률 | 5일승률 | 10일승률 |")
    lines.append("|---------|---------|---------|----------|----------|--------|--------|")

    s2_summaries = {}
    for confirm in [1, 2, 3]:
        df = s2.get(confirm, pd.DataFrame())
        s = summarize_results(df, HOLD_DAYS) if not df.empty else {}
        s2_summaries[confirm] = s
        lines.append(format_table_row(f"{confirm}일", s))

    lines.append("")

    # 1일 vs 2일 비교
    r1_10 = s2_summaries.get(1, {}).get("10일", {}).get("평균수익률", None)
    r2_10 = s2_summaries.get(2, {}).get("10일", {}).get("평균수익률", None)
    if r1_10 is not None and r2_10 is not None:
        diff = r2_10 - r1_10
        lines.append(f"**1일 뽀록 vs 2일 확인 수익률 차이 (10일 기준): {diff:+.2f}%p**")
        if diff > 0:
            lines.append("→ 2일 확인이 더 효과적 (노이즈 필터링 효과)")
        else:
            lines.append("→ 1일 진입이 더 빠른 모멘텀 포착에 유리")
    lines.append("")

    best_confirm2, _ = find_best(s2, "평균수익률", "10일")
    if best_confirm2 is not None:
        r = s2_summaries.get(best_confirm2, {}).get("10일", {})
        lines.append(f"**최적 확인 일수: {best_confirm2}일** "
                     f"(10일 평균수익률 {r.get('평균수익률','N/A')}%, "
                     f"승률 {r.get('승률','N/A')}%)")
    lines.append("")

    # ── 전략 3 ──
    lines.append("---")
    lines.append("## 전략 3: 스마트머니 (개인 폭매도 + 외국인 폭매수 교집합) — 확인 일수별")
    lines.append("")
    lines.append("| 확인일수 | 시그널수 | 5일수익률 | 10일수익률 | 20일수익률 | 5일승률 | 10일승률 |")
    lines.append("|---------|---------|---------|----------|----------|--------|--------|")

    s3_summaries = {}
    for confirm in [1, 2, 3]:
        df = s3.get(confirm, pd.DataFrame())
        s = summarize_results(df, HOLD_DAYS) if not df.empty else {}
        s3_summaries[confirm] = s
        lines.append(format_table_row(f"{confirm}일", s))

    lines.append("")
    best_confirm3, _ = find_best(s3, "평균수익률", "10일")
    if best_confirm3 is not None:
        r = s3_summaries.get(best_confirm3, {}).get("10일", {})
        lines.append(f"**최적 확인 일수: {best_confirm3}일** "
                     f"(10일 평균수익률 {r.get('평균수익률','N/A')}%, "
                     f"승률 {r.get('승률','N/A')}%)")
    lines.append("")

    # ── 종합 비교 ──
    lines.append("---")
    lines.append("## 종합 비교")
    lines.append("")
    lines.append("| 전략 | 최고 10일 수익률 | 최고 10일 승률 | 추천 설정 |")
    lines.append("|------|--------------|-------------|---------|")

    def get_best_row(summaries_dict, strategy_name):
        best_ret = -9999
        best_wr  = -9999
        best_key = None
        for key, s in summaries_dict.items():
            r = s.get("10일", {})
            ret = r.get("평균수익률", -9999)
            wr  = r.get("승률", -9999)
            if ret > best_ret:
                best_ret = ret
                best_wr  = wr
                best_key = key
        if best_key is None:
            return f"| {strategy_name} | N/A | N/A | N/A |"
        best_s = summaries_dict[best_key].get("10일", {})
        return (f"| {strategy_name} | "
                f"{best_s.get('평균수익률','N/A'):+.2f}% | "
                f"{best_s.get('승률','N/A')}% | "
                f"{best_key}일 설정 + 10일 보유 |")

    lines.append(get_best_row(s1_summaries, "전략1 외국인 연속"))
    lines.append(get_best_row(s2_summaries, "전략2 기관+외국인 전환"))
    lines.append(get_best_row(s3_summaries, "전략3 스마트머니"))
    lines.append("")

    # 최종 추천
    candidates = {}
    for name, sums in [("전략1", s1_summaries), ("전략2", s2_summaries), ("전략3", s3_summaries)]:
        best_val_r = max((s.get("10일", {}).get("평균수익률", -9999) for s in sums.values()), default=-9999)
        candidates[name] = best_val_r

    best_strategy = max(candidates, key=candidates.get) if candidates else "N/A"
    best_strategy_val = candidates.get(best_strategy, 0)

    reasons = {
        "전략1": "외국인 모멘텀이 지속적으로 주가에 선행하는 패턴 확인",
        "전략2": "기관+외국인 동시 매수 전환은 강한 수급 전환 신호",
        "전략3": "개인 폭매도 + 외국인 폭매수 교집합은 역발상 스마트머니 포착"
    }
    lines.append(f"**최종 추천: {best_strategy}** "
                 f"(10일 평균수익률 {best_strategy_val:+.2f}%, "
                 f"이유: {reasons.get(best_strategy, '')})")
    lines.append("")

    # ── 상세 통계 ──
    lines.append("---")
    lines.append("## 상세 통계")
    lines.append("")

    for strategy_name, sums, results_dict in [
        ("전략 1 (외국인 연속)", s1_summaries, s1),
        ("전략 2 (기관+외국인 전환)", s2_summaries, s2),
        ("전략 3 (스마트머니)", s3_summaries, s3),
    ]:
        lines.append(f"### {strategy_name}")
        for key in sorted(sums.keys()):
            s = sums[key]
            lines.append(f"\n#### 설정: {key}일 연속/확인")
            for hold_label, stats in s.items():
                lines.append(f"- **{hold_label} 보유**: "
                             f"시그널 {stats['시그널수']}건 | "
                             f"평균 {stats['평균수익률']:+.2f}% | "
                             f"승률 {stats['승률']}% | "
                             f"최대수익 {stats['최대수익']:+.2f}% | "
                             f"최대손실 {stats['최대손실']:+.2f}% | "
                             f"중간값 {stats['중간값']:+.2f}%")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by backtest_flow.py*")
    return "\n".join(lines)


# ── 메인 ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    t0 = time.time()

    print("=" * 60)
    print("수급 기반 단타/스윙 전략 백테스트")
    print("=" * 60)

    # 1. 데이터 수집
    print("\n[1/4] 데이터 수집...")
    all_flow, all_price, failed = get_data()
    print(f"  수집 완료: {len(all_flow)}개 종목 | 실패: {len(failed)}개")

    if not all_flow:
        print("❌ 데이터 없음 - 종료")
        sys.exit(1)

    # 2. 전략 실행
    print("\n[2/4] 전략 1 실행...")
    s1 = run_strategy1(all_flow, all_price)

    print("\n[3/4] 전략 2 실행...")
    s2 = run_strategy2(all_flow, all_price)

    print("\n[4/4] 전략 3 실행...")
    s3 = run_strategy3(all_flow, all_price)

    # 3. 보고서 생성
    print("\n📝 보고서 생성 중...")
    report = generate_report(all_flow, all_price, failed, s1, s2, s3)

    out_path = os.path.join(DATA_DIR, "results_flow_backtest.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    elapsed = time.time() - t0
    print(f"\n✅ 완료! 소요시간: {elapsed:.1f}초")
    print(f"📄 결과: {out_path}")
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
