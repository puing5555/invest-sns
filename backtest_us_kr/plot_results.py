"""
plot_results.py — 차트 생성
1. 히트맵: 페어별 × A/B/C 수익률
2. NVDA-SK하이닉스 타임라인
3. 급등 폭별 수익률 바 차트
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import os

# 한글 폰트 설정
def setup_korean_font():
    candidates = [
        "Malgun Gothic", "NanumGothic", "AppleGothic",
        "UnDotum", "DejaVu Sans"
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for c in candidates:
        if c in available:
            matplotlib.rcParams["font.family"] = c
            break
    matplotlib.rcParams["axes.unicode_minus"] = False

setup_korean_font()


def plot_all(all_results, surge_stats, save_path="backtest_results.png"):
    fig = plt.figure(figsize=(20, 18))
    fig.suptitle("미국-한국 연동 단타 전략 백테스트", fontsize=16, fontweight="bold", y=0.98)

    # ── 1. 히트맵 ──────────────────────────────────────
    ax1 = fig.add_subplot(3, 1, 1)

    # 행: us_ticker → kr_name, 열: A/B/C
    rows = []
    for us_t, pairs in all_results.items():
        for kr_code, info in pairs.items():
            s = info["summary"]
            if s.get("signals", 0) == 0:
                continue
            label = f"{us_t}→{info['name']}"
            row = {
                "label": label,
                "A": s["A"].get("avg") if s.get("A") else None,
                "B": s["B"].get("avg") if s.get("B") else None,
                "C": s["C"].get("avg") if s.get("C") else None,
            }
            rows.append(row)

    if rows:
        df_heat = pd.DataFrame(rows).set_index("label")[["A", "B", "C"]]
        df_heat = df_heat.astype(float)
        # 너무 많으면 상위 30개만
        if len(df_heat) > 30:
            df_heat = df_heat.head(30)

        vmax = max(abs(df_heat.values[~np.isnan(df_heat.values)]).max(), 2) if df_heat.notna().any().any() else 5
        im = ax1.imshow(df_heat.values, cmap="RdYlGn", aspect="auto",
                        vmin=-vmax, vmax=vmax)
        ax1.set_xticks(range(3))
        ax1.set_xticklabels(["A(당일종가)", "B(2일후)", "C(3일후)"], fontsize=10)
        ax1.set_yticks(range(len(df_heat)))
        ax1.set_yticklabels(df_heat.index, fontsize=7)
        ax1.set_title("페어별 평균 수익률 히트맵 (%)", fontsize=12, pad=8)
        plt.colorbar(im, ax=ax1, shrink=0.8, label="%")

        # 셀 값 표시
        for i in range(len(df_heat)):
            for j in range(3):
                val = df_heat.values[i, j]
                if not np.isnan(val):
                    ax1.text(j, i, f"{val:.1f}", ha="center", va="center",
                             fontsize=6, color="black")
    else:
        ax1.text(0.5, 0.5, "데이터 없음", ha="center", va="center",
                 transform=ax1.transAxes)
        ax1.set_title("페어별 평균 수익률 히트맵", fontsize=12)

    # ── 2. NVDA-SK하이닉스 타임라인 ────────────────────
    ax2 = fig.add_subplot(3, 1, 2)
    nvda_hynix = None
    if "NVDA" in all_results and "000660" in all_results["NVDA"]:
        nvda_hynix = all_results["NVDA"]["000660"]["results"]

    if nvda_hynix is not None and not nvda_hynix.empty:
        x = range(len(nvda_hynix))
        ax2.bar(x, nvda_hynix["return_A"].fillna(0), label="A(당일종가)",
                alpha=0.6, color="steelblue")
        ax2.bar(x, nvda_hynix["return_B"].fillna(0), label="B(2일후)",
                alpha=0.5, color="orange", width=0.5)
        ax2.axhline(0, color="black", linewidth=0.8)
        ax2.set_title("NVDA 급등 → SK하이닉스 수익률 (시그널별)", fontsize=12)
        ax2.set_xlabel("시그널 번호")
        ax2.set_ylabel("수익률 (%)")
        ax2.legend(fontsize=9)

        # x축에 날짜 일부 표시
        step = max(1, len(nvda_hynix) // 10)
        ax2.set_xticks(list(range(0, len(nvda_hynix), step)))
        ax2.set_xticklabels(
            [str(nvda_hynix.iloc[i]["us_date"])[:10]
             for i in range(0, len(nvda_hynix), step)],
            rotation=30, fontsize=7
        )
    else:
        ax2.text(0.5, 0.5, "NVDA-SK하이닉스 데이터 없음",
                 ha="center", va="center", transform=ax2.transAxes)
        ax2.set_title("NVDA → SK하이닉스 타임라인", fontsize=12)

    # ── 3. 급등 폭별 수익률 바 차트 ────────────────────
    ax3 = fig.add_subplot(3, 1, 3)
    categories = ["5~10%", "10~15%", "15%+"]
    sc_labels = ["A(당일종가)", "B(2일후)", "C(3일후)"]
    colors = ["steelblue", "orange", "green"]

    x = np.arange(len(categories))
    width = 0.25

    for idx, sc in enumerate(["A", "B", "C"]):
        vals = []
        for cat in categories:
            if cat in surge_stats and sc in surge_stats[cat]:
                vals.append(surge_stats[cat][sc] or 0)
            else:
                vals.append(0)
        bars = ax3.bar(x + idx * width, vals, width, label=sc_labels[idx],
                       color=colors[idx], alpha=0.7)
        for bar, v in zip(bars, vals):
            if v != 0:
                ax3.text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + 0.05,
                         f"{v:.2f}%", ha="center", va="bottom", fontsize=8)

    ax3.set_xticks(x + width)
    ax3.set_xticklabels(categories, fontsize=11)
    ax3.set_title("급등 폭별 평균 수익률", fontsize=12)
    ax3.set_ylabel("평균 수익률 (%)")
    ax3.axhline(0, color="black", linewidth=0.8)
    ax3.legend(fontsize=9)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(save_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"차트 저장: {save_path}")


if __name__ == "__main__":
    print("plot_results.py — import only")
