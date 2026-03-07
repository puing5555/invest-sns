"""
8개 뉴스 브리핑 생성 스크립트
데이터: market_data.json + naver_news.json
"""
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ──────────────────────────────
# 데이터 로드
# ──────────────────────────────
with open("market_data.json", encoding="utf-8") as f:
    mkt = json.load(f)

with open("naver_news.json", encoding="utf-8") as f:
    raw_news = json.load(f)

# ──────────────────────────────
# 헬퍼 함수
# ──────────────────────────────
def fmt_close(data, name, unit=""):
    if name not in data:
        return f"  • {name}: 데이터 없음"
    d = data[name]
    c = d["close"]
    if "pct" in d:
        sign = "+" if d["pct"] >= 0 else ""
        chg_sign = "+" if d["chg"] >= 0 else ""
        if unit == "$":
            return f"  • {name}: ${c:,.2f} ({chg_sign}{d['pct']:.2f}%)"
        elif unit == "won":
            return f"  • {name}: {c:,.0f}원 ({chg_sign}{d['chg']:.0f}원, {sign}{d['pct']:.2f}%)"
        elif unit == "index":
            return f"  • {name}: {c:,.2f} ({chg_sign}{d['chg']:.2f}, {sign}{d['pct']:.2f}%)"
        else:
            return f"  • {name}: {c:,.2f} ({sign}{d['pct']:.2f}%)"
    else:
        return f"  • {name}: {c:,.2f}"

def fmt_open(data, name, prev_close, unit="index"):
    """장시작 시가 기준 포맷"""
    if name not in data:
        return f"  • {name}: 데이터 없음"
    d = data[name]
    o = d["open"]
    chg = o - prev_close
    pct = (chg / prev_close * 100) if prev_close != 0 else 0
    sign = "+" if pct >= 0 else ""
    chg_sign = "+" if chg >= 0 else ""
    if unit == "index":
        return f"  • {name}: {o:,.2f} (전일비 {chg_sign}{chg:.2f}, {sign}{pct:.2f}%)"
    else:
        return f"  • {name}: {o:,.2f} ({sign}{pct:.2f}%)"

def dedup_news(news_list, max_count=20):
    """중복 제목 제거 (같은 사건 다른 언론사 1개만)"""
    seen_words = []
    deduped = []
    for n in news_list:
        title = n["title"]
        # 핵심 단어로 중복 판단 (20자 이상 공통 부분)
        is_dup = False
        t_words = set(title.replace(" ", "")[:30])
        for sw in seen_words:
            overlap = len(t_words & sw)
            if overlap >= 10:
                is_dup = True
                break
        if not is_dup:
            deduped.append(title)
            seen_words.append(t_words)
        if len(deduped) >= max_count:
            break
    return deduped

def fmt_news_list(titles):
    lines = []
    for i, t in enumerate(titles, 1):
        lines.append(f"  {i}. {t}")
    return "\n".join(lines)

# ──────────────────────────────
# 뉴스 분배 (날짜별)
# ──────────────────────────────
news_305_all = dedup_news(raw_news.get("20250305", []), max_count=50)
news_306_all = dedup_news(raw_news.get("20250306", []), max_count=50)

# 시간대별 분배
# 07:00: 1~15번
# 09:05: 1~10번 (겹쳐도 OK - 다른 시점)
# 16:00: 11~25번
# 23:00: 26~35번

def get_news_slice(news_all, start, end):
    return news_all[start:end] if len(news_all) > start else []

# ──────────────────────────────
# 시황 데이터 참조
# ──────────────────────────────
d304 = mkt.get("2025-03-04", {})  # 3/4 미국장 마감 (3/5 모닝용)
d305 = mkt.get("2025-03-05", {})  # 3/5 전체
d306 = mkt.get("2025-03-06", {})  # 3/6 전체
d307 = mkt.get("2025-03-07", {})  # 3/7

# 3/4 기준 대비 (3/3 종가 기준 변화)
d303 = mkt.get("2025-03-03", {})

# ──────────────────────────────
# 브리핑 생성
# ──────────────────────────────
briefings = []

# ── 브리핑 #1: 3/5(목) 07:00 모닝 ──
# 3/4 미국장 마감 데이터 사용
b1_news = get_news_slice(news_305_all, 0, 15)
b1 = f"""📰 2025/03/05(목) 07:00 모닝 브리핑

🌏 간밤 미국장 마감 (3/4 현지 기준)
{fmt_close(d304, "S&P500")}
{fmt_close(d304, "NASDAQ")}
{fmt_close(d304, "DOW")}
{fmt_close(d304, "VIX")}

💵 주요 지표
{fmt_close(d304, "USD/KRW", unit="won")}
{fmt_close(d304, "WTI")}
{fmt_close(d304, "BTC", unit="$")}
{fmt_close(d304, "ETH", unit="$")}

📋 오늘 주목할 뉴스 ({len(b1_news)}개)
{fmt_news_list(b1_news)}

📊 오늘 전망
S&P500이 {d304.get('S&P500', {}).get('close', '?'):,} ({d304.get('S&P500', {}).get('pct', 0):+.2f}%)로 마감하며 관세 우려가 지속된 것으로 보인다. VIX가 {d304.get('VIX', {}).get('close', '?')} 수준으로 변동성 경계감이 유지될 것으로 분석된다.
"""

# ── 브리핑 #2: 3/5(목) 09:05 장 시작 ──
# 3/5 코스피 시가 + 3/4 수급(데이터 없음)
kospi_305_prev = d304.get("KOSPI", {}).get("close", 0)
kosdaq_305_prev = d304.get("KOSDAQ", {}).get("close", 0)

b2_news = get_news_slice(news_305_all, 0, 10)
b2 = f"""📈 2025/03/05(목) 09:05 장 시작

🏃 개장 현황
{fmt_open(d305, "KOSPI", kospi_305_prev, "index")}
{fmt_open(d305, "KOSDAQ", kosdaq_305_prev, "index")}

👥 외국인/기관/개인 수급 (pykrx 수집 불가 — 데이터 없음)
  • 외국인: 데이터 없음
  • 기관: 데이터 없음
  • 개인: 데이터 없음

📋 주요 뉴스
{fmt_news_list(b2_news)}

오늘 코스피는 간밤 미국장 변동성({d304.get('VIX', {}).get('close', '?')}) 영향을 받으며 신중하게 출발하는 것으로 보인다. 관세 불확실성 속 방산·원전 섹터로의 자금 이동이 주목된다.
"""

# ── 브리핑 #3: 3/5(목) 16:00 장 마감 ──
b3_news = get_news_slice(news_305_all, 10, 25)
kospi_305_chg = d305.get("KOSPI", {}).get("chg", 0)
kospi_305_pct = d305.get("KOSPI", {}).get("pct", 0)
kosdaq_305_chg = d305.get("KOSDAQ", {}).get("chg", 0)
kosdaq_305_pct = d305.get("KOSDAQ", {}).get("pct", 0)

b3 = f"""📉 2025/03/05(목) 16:00 장 마감

📊 오늘 결과
{fmt_close(d305, "KOSPI", unit="index")}
{fmt_close(d305, "KOSDAQ", unit="index")}

👥 수급 마감 (pykrx 수집 불가 — 데이터 없음)
  • 외국인: 데이터 없음
  • 기관: 데이터 없음
  • 개인: 데이터 없음

📋 오늘 주요 뉴스
{fmt_news_list(b3_news)}

코스피는 {d305.get('KOSPI', {}).get('close', '?'):,}({kospi_305_chg:+.2f}, {kospi_305_pct:+.2f}%)로 마감하며, 미국장 전날 하락 후 반등 기대감이 반영된 것으로 보인다. 달러/원 환율은 {d305.get('USD/KRW', {}).get('close', '?'):,}원 수준으로 안정세를 보인 것으로 분석된다.
"""

# ── 브리핑 #4: 3/5(목) 23:00 미국장 개장 ──
# 3/5 미국장 (yfinance 3/5 데이터 = 현지 3/5 종가)
b4_news = get_news_slice(news_305_all, 25, 35)

b4 = f"""🇺🇸 2025/03/05(목) 23:00 미국장 개장

📈 개장 현황 (3/5 현지 시간 기준)
{fmt_close(d305, "S&P500")}
{fmt_close(d305, "NASDAQ")}
{fmt_close(d305, "DOW")}
{fmt_close(d305, "VIX")}

💵 달러/환율
{fmt_close(d305, "USD/KRW", unit="won")}
{fmt_close(d305, "WTI")}

🔮 가상자산
{fmt_close(d305, "BTC", unit="$")}
{fmt_close(d305, "ETH", unit="$")}

📋 저녁 주요 뉴스
{fmt_news_list(b4_news) if b4_news else "  (뉴스 슬롯 소진 — 당일 앞선 브리핑 참조)"}
"""

# ── 브리핑 #5: 3/6(금) 07:00 모닝 ──
# 3/5 미국장 마감 데이터
b5_news = get_news_slice(news_306_all, 0, 15)

b5 = f"""📰 2025/03/06(금) 07:00 모닝 브리핑

🌏 간밤 미국장 마감 (3/5 현지 기준)
{fmt_close(d305, "S&P500")}
{fmt_close(d305, "NASDAQ")}
{fmt_close(d305, "DOW")}
{fmt_close(d305, "VIX")}

💵 주요 지표
{fmt_close(d305, "USD/KRW", unit="won")}
{fmt_close(d305, "WTI")}
{fmt_close(d305, "BTC", unit="$")}
{fmt_close(d305, "ETH", unit="$")}

📋 오늘 주목할 뉴스 ({len(b5_news)}개)
{fmt_news_list(b5_news)}

📊 오늘 전망
S&P500이 {d305.get('S&P500', {}).get('close', '?'):,} ({d305.get('S&P500', {}).get('pct', 0):+.2f}%)로 상승 마감했으나, ECB 금리 인하 소식과 트럼프 관세 불확실성이 공존하는 것으로 보인다. VIX가 {d305.get('VIX', {}).get('close', '?')} 수준에서 변동성 경계가 유지될 것으로 분석된다.
"""

# ── 브리핑 #6: 3/6(금) 09:05 장 시작 ──
kospi_306_prev = d305.get("KOSPI", {}).get("close", 0)
kosdaq_306_prev = d305.get("KOSDAQ", {}).get("close", 0)

b6_news = get_news_slice(news_306_all, 0, 10)

b6 = f"""📈 2025/03/06(금) 09:05 장 시작

🏃 개장 현황
{fmt_open(d306, "KOSPI", kospi_306_prev, "index")}
{fmt_open(d306, "KOSDAQ", kosdaq_306_prev, "index")}

👥 외국인/기관/개인 수급 (pykrx 수집 불가 — 데이터 없음)
  • 외국인: 데이터 없음
  • 기관: 데이터 없음
  • 개인: 데이터 없음

📋 주요 뉴스
{fmt_news_list(b6_news)}

전일 코스피 상승({kospi_306_prev:,} 종가) 흐름 이후, 미국장 반등({d305.get('S&P500', {}).get('pct', 0):+.2f}%) 영향으로 강세 개장이 예상되나 관세 불확실성 지속으로 변동성에 유의할 것으로 보인다.
"""

# ── 브리핑 #7: 3/6(금) 16:00 장 마감 ──
kospi_306_chg = d306.get("KOSPI", {}).get("chg", 0)
kospi_306_pct = d306.get("KOSPI", {}).get("pct", 0)
kosdaq_306_chg = d306.get("KOSDAQ", {}).get("chg", 0)
kosdaq_306_pct = d306.get("KOSDAQ", {}).get("pct", 0)

b7_news = get_news_slice(news_306_all, 10, 25)

b7 = f"""📉 2025/03/06(금) 16:00 장 마감

📊 오늘 결과
{fmt_close(d306, "KOSPI", unit="index")}
{fmt_close(d306, "KOSDAQ", unit="index")}

👥 수급 마감 (pykrx 수집 불가 — 데이터 없음)
  • 외국인: 데이터 없음
  • 기관: 데이터 없음
  • 개인: 데이터 없음

📋 오늘 주요 뉴스
{fmt_news_list(b7_news)}

코스피는 {d306.get('KOSPI', {}).get('close', '?'):,}({kospi_306_chg:+.2f}, {kospi_306_pct:+.2f}%)로 마감하며 코스닥은 {d306.get('KOSDAQ', {}).get('close', '?'):,}({kosdaq_306_chg:+.2f}, {kosdaq_306_pct:+.2f}%) 약세를 보인 것으로 분석된다. 달러/원이 {d306.get('USD/KRW', {}).get('close', '?'):,}원으로 강세를 보인 것으로 보인다.
"""

# ── 브리핑 #8: 3/6(금) 23:00 미국장 개장 ──
b8_news = get_news_slice(news_306_all, 25, 35)

b8 = f"""🇺🇸 2025/03/06(금) 23:00 미국장 개장

📈 개장 현황 (3/6 현지 시간 기준)
{fmt_close(d306, "S&P500")}
{fmt_close(d306, "NASDAQ")}
{fmt_close(d306, "DOW")}
{fmt_close(d306, "VIX")}

💵 달러/환율
{fmt_close(d306, "USD/KRW", unit="won")}
{fmt_close(d306, "WTI")}

🔮 가상자산
{fmt_close(d306, "BTC", unit="$")}
{fmt_close(d306, "ETH", unit="$")}

📋 저녁 주요 뉴스
{fmt_news_list(b8_news) if b8_news else "  (뉴스 슬롯 소진 — 당일 앞선 브리핑 참조)"}
"""

# ──────────────────────────────
# 출력 조립
# ──────────────────────────────
output = f"""# 뉴스 브리핑 실전 테스트 — 2025/03/05~06

## 데이터 수집 현황
- 시황 데이터 (yfinance): ✅ — S&P500/NASDAQ/DOW/VIX/달러원/WTI/BTC/ETH/코스피/코스닥
- pykrx 수급 (외국인/기관/개인): ❌ — Python 3.14 환경 EUC-KR 인코딩 오류
- 네이버 뉴스 3/5: {len(raw_news.get('20250305', []))}개 수집 ✅
- 네이버 뉴스 3/6: {len(raw_news.get('20250306', []))}개 수집 ✅

---

## 브리핑 #1 — 3/5(목) 07:00 모닝

{b1}
---

## 브리핑 #2 — 3/5(목) 09:05 장 시작

{b2}
---

## 브리핑 #3 — 3/5(목) 16:00 장 마감

{b3}
---

## 브리핑 #4 — 3/5(목) 23:00 미국장 개장

{b4}
---

## 브리핑 #5 — 3/6(금) 07:00 모닝

{b5}
---

## 브리핑 #6 — 3/6(금) 09:05 장 시작

{b6}
---

## 브리핑 #7 — 3/6(금) 16:00 장 마감

{b7}
---

## 브리핑 #8 — 3/6(금) 23:00 미국장 개장

{b8}
---
"""

with open("briefings_305_306.md", "w", encoding="utf-8") as f:
    f.write(output)

print("=== 브리핑 생성 완료 ===")
print(f"파일: briefings_305_306.md")
print(f"총 문자 수: {len(output):,}")
print("\n=== 미리보기 (처음 500자) ===")
print(output[:500])
