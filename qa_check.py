import json, os, sys, re
from datetime import datetime, timezone
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import urllib.request

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
BASE = r"C:\Users\Mario\work\invest-sns"

def supabase_get(table, select="*", params=""):
    url = SUPABASE_URL + "/rest/v1/" + table + "?select=" + select + params
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": "Bearer " + SUPABASE_KEY,
        "Accept": "application/json",
        "Prefer": "count=exact"
    })
    with urllib.request.urlopen(req) as resp:
        count = resp.headers.get("content-range", "")
        data = json.loads(resp.read())
    return data, count

def fetch_all(table, select="*", extra=""):
    """Fetch all rows using pagination."""
    all_data = []
    offset = 0
    limit = 1000
    while True:
        url = SUPABASE_URL + "/rest/v1/" + table + "?select=" + select + extra + "&limit=" + str(limit) + "&offset=" + str(offset)
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": "Bearer " + SUPABASE_KEY,
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        all_data.extend(data)
        if len(data) < limit:
            break
        offset += limit
    return all_data

print("Fetching signals...")
signals = fetch_all("influencer_signals")
print("Total signals:", len(signals))

print("Fetching videos...")
videos = fetch_all("influencer_videos", "id,video_id,title,published_at")
print("Total videos:", len(videos))

print("Fetching channels...")
channels = fetch_all("influencer_channels", "id,channel_name")
print("Total channels:", len(channels))

# Check if speakers table exists
speakers_exist = False
try:
    sp, _ = supabase_get("speakers", "id", "&limit=1")
    speakers_exist = True
    speakers = fetch_all("speakers", "id")
    speaker_ids_in_db = set(str(s["id"]) for s in speakers)
    print("Speakers table found, count:", len(speakers))
except:
    print("No speakers table found")

report = []
report.append("# QA 점검 리포트")
report.append("**생성일시:** 2026-03-03 01:23 (Asia/Bangkok)")
report.append("**프로젝트:** invest-sns")
report.append("**총 시그널 수:** " + str(len(signals)))
report.append("**총 영상 수:** " + str(len(videos)))
report.append("**총 채널 수:** " + str(len(channels)))
report.append("")
report.append("---")
report.append("")

issues_summary = []

# 1. key_quote > 200 chars
print("Check 1: key_quote length...")
long_quotes = []
for s in signals:
    kq = s.get("key_quote") or ""
    if len(kq) > 200:
        long_quotes.append((s["id"], s.get("stock",""), len(kq)))

report.append("## 1. key_quote 200자 초과 시그널")
if long_quotes:
    severity = "🟡 Warning"
    report.append("**심각도:** " + severity)
    report.append("**발견:** " + str(len(long_quotes)) + "건")
    report.append("")
    report.append("| ID | 종목 | 글자수 |")
    report.append("|---|---|---|")
    for row in long_quotes[:30]:
        report.append("| " + str(row[0]) + " | " + str(row[1]) + " | " + str(row[2]) + " |")
    if len(long_quotes) > 30:
        report.append("| ... | 외 " + str(len(long_quotes)-30) + "건 | |")
    report.append("")
    report.append("**제안:** key_quote를 200자 이내로 요약 또는 트리밍")
    issues_summary.append(("1. key_quote 초과", len(long_quotes), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 없음 ✅")
    issues_summary.append(("1. key_quote 초과", 0, "🟢 Info"))
report.append("")

# 2. ticker null
print("Check 2: ticker null...")
null_tickers = []
for s in signals:
    if s.get("ticker") is None or s.get("ticker") == "":
        null_tickers.append((s["id"], s.get("stock",""), s.get("signal","")))

report.append("## 2. ticker가 null인 시그널")
if null_tickers:
    severity = "🔴 Critical"
    report.append("**심각도:** " + severity)
    report.append("**발견:** " + str(len(null_tickers)) + "건")
    report.append("")
    report.append("| ID | 종목(stock) | signal |")
    report.append("|---|---|---|")
    for row in null_tickers[:30]:
        report.append("| " + str(row[0]) + " | " + str(row[1]) + " | " + str(row[2]) + " |")
    if len(null_tickers) > 30:
        report.append("| ... | 외 " + str(len(null_tickers)-30) + "건 | |")
    report.append("")
    report.append("**제안:** ticker 매핑 로직 점검. stock명으로 ticker 재매핑 필요")
    issues_summary.append(("2. ticker null", len(null_tickers), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 없음 ✅")
    issues_summary.append(("2. ticker null", 0, "🟢 Info"))
report.append("")

# 3. 같은 video_id + 유사 종목 중복 시그널
print("Check 3: duplicate signals...")
by_video = defaultdict(list)
for s in signals:
    vid = s.get("video_id","")
    if vid:
        by_video[vid].append(s)

duplicates = []
for vid, sigs in by_video.items():
    if len(sigs) < 2:
        continue
    for i in range(len(sigs)):
        for j in range(i+1, len(sigs)):
            s1 = sigs[i].get("stock","") or ""
            s2 = sigs[j].get("stock","") or ""
            if s1 == s2 or SequenceMatcher(None, s1, s2).ratio() > 0.6:
                kq1 = sigs[i].get("key_quote","") or ""
                kq2 = sigs[j].get("key_quote","") or ""
                if kq1 and kq2 and SequenceMatcher(None, kq1, kq2).ratio() > 0.6:
                    duplicates.append((vid, sigs[i]["id"], sigs[j]["id"], s1, s2))

report.append("## 3. 같은 영상 내 유사 중복 시그널")
if duplicates:
    severity = "🟡 Warning"
    report.append("**심각도:** " + severity)
    report.append("**발견:** " + str(len(duplicates)) + "쌍")
    report.append("")
    report.append("| video_id | ID1 | ID2 | stock1 | stock2 |")
    report.append("|---|---|---|---|---|")
    for row in duplicates[:20]:
        report.append("| " + str(row[0])[:11] + "... | " + str(row[1]) + " | " + str(row[2]) + " | " + str(row[3]) + " | " + str(row[4]) + " |")
    if len(duplicates) > 20:
        report.append("| ... | 외 " + str(len(duplicates)-20) + "쌍 | | | |")
    report.append("")
    report.append("**제안:** 중복 시그널 병합 또는 제거")
    issues_summary.append(("3. 중복 시그널", len(duplicates), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 없음 ✅")
    issues_summary.append(("3. 중복 시그널", 0, "🟢 Info"))
report.append("")

# 4. speaker_id별 시그널 수
print("Check 4: speaker signal counts...")
speaker_counts = Counter()
for s in signals:
    sid = s.get("speaker_id","unknown")
    speaker_counts[sid] += 1

report.append("## 4. speaker_id별 시그널 수")
report.append("**심각도:** 🟢 Info")
report.append("")
report.append("| speaker_id | 시그널 수 |")
report.append("|---|---|")
for sid, cnt in speaker_counts.most_common(15):
    flag = " ⚠️" if cnt > 50 else ""
    report.append("| " + str(sid) + " | " + str(cnt) + flag + " |")
abnormal = [(sid,cnt) for sid,cnt in speaker_counts.items() if cnt > 50]
if abnormal:
    report.append("")
    report.append("**⚠️ 50건 초과 speaker:** " + str(len(abnormal)) + "명")
    issues_summary.append(("4. speaker 비정상", len(abnormal), "🟡 Warning"))
else:
    issues_summary.append(("4. speaker 비정상", 0, "🟢 Info"))
report.append("")

# 5. stock 컬럼에 종목이 아닌 것
print("Check 5: invalid stock names...")
invalid_stocks = []
bad_patterns = ["없음", "N/A", "n/a", "null", "None", "카테고리", "분류", "기타", "전체", "시장", "경제", "산업", "섹터"]
for s in signals:
    stock = s.get("stock","") or ""
    stock_stripped = stock.strip()
    if not stock_stripped:
        invalid_stocks.append((s["id"], stock, "빈 값"))
    elif stock_stripped in bad_patterns or len(stock_stripped) <= 1:
        invalid_stocks.append((s["id"], stock, "의심"))

report.append("## 5. stock 컬럼 이상값")
if invalid_stocks:
    severity = "🟡 Warning"
    report.append("**심각도:** " + severity)
    report.append("**발견:** " + str(len(invalid_stocks)) + "건")
    report.append("")
    report.append("| ID | stock | 사유 |")
    report.append("|---|---|---|")
    for row in invalid_stocks[:20]:
        report.append("| " + str(row[0]) + " | " + str(row[1]) + " | " + str(row[2]) + " |")
    report.append("")
    report.append("**제안:** 유효 종목명으로 교체 또는 삭제")
    issues_summary.append(("5. stock 이상값", len(invalid_stocks), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 없음 ✅")
    issues_summary.append(("5. stock 이상값", 0, "🟢 Info"))
report.append("")

# 6. signal 컬럼 이상값
print("Check 6: signal values...")
allowed_signals = {"매수", "긍정", "중립", "경계", "매도",
                   "STRONG_BUY", "BUY", "POSITIVE", "HOLD", "NEUTRAL", "CONCERN", "SELL", "STRONG_SELL"}
signal_counts = Counter()
bad_signals = []
for s in signals:
    sig = s.get("signal","") or ""
    signal_counts[sig] += 1
    if sig not in allowed_signals:
        bad_signals.append((s["id"], s.get("stock",""), sig))

report.append("## 6. signal 컬럼 이상값")
report.append("")
report.append("**signal 분포:**")
report.append("")
report.append("| signal | 건수 |")
report.append("|---|---|")
for sig, cnt in signal_counts.most_common():
    flag = " ❌" if sig not in allowed_signals else ""
    report.append("| " + str(sig) + " | " + str(cnt) + flag + " |")
report.append("")
if bad_signals:
    severity = "🔴 Critical"
    report.append("**심각도:** " + severity)
    report.append("**이상값:** " + str(len(bad_signals)) + "건")
    report.append("")
    report.append("| ID | stock | signal |")
    report.append("|---|---|---|")
    for row in bad_signals[:20]:
        report.append("| " + str(row[0]) + " | " + str(row[1]) + " | " + str(row[2]) + " |")
    if len(bad_signals) > 20:
        report.append("| ... | 외 " + str(len(bad_signals)-20) + "건 | |")
    report.append("")
    report.append("**제안:** 허용된 8가지 시그널 타입으로 재매핑")
    issues_summary.append(("6. signal 이상값", len(bad_signals), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 모두 정상 ✅")
    issues_summary.append(("6. signal 이상값", 0, "🟢 Info"))
report.append("")

# 7. mention_type 이상값
print("Check 7: mention_type...")
mt_counts = Counter()
for s in signals:
    mt = s.get("mention_type","") or ""
    mt_counts[mt] += 1

report.append("## 7. mention_type 분포")
report.append("")
report.append("| mention_type | 건수 |")
report.append("|---|---|")
for mt, cnt in mt_counts.most_common():
    report.append("| " + str(mt) + " | " + str(cnt) + " |")
report.append("")
issues_summary.append(("7. mention_type", 0, "🟢 Info"))
report.append("")

# 8. 날짜 이상
print("Check 8: date anomalies...")
date_issues = []
now = datetime(2026, 3, 3, tzinfo=timezone.utc)
for s in signals:
    ca = s.get("created_at","")
    if ca:
        try:
            dt = datetime.fromisoformat(ca.replace("Z","+00:00"))
            if dt > now:
                date_issues.append((s["id"], ca, "미래"))
            elif dt.year < 2019:
                date_issues.append((s["id"], ca, "2019년 이전"))
        except:
            date_issues.append((s["id"], ca, "파싱 실패"))

report.append("## 8. 날짜 이상 (created_at)")
if date_issues:
    severity = "🟡 Warning"
    report.append("**심각도:** " + severity)
    report.append("**발견:** " + str(len(date_issues)) + "건")
    report.append("")
    report.append("| ID | created_at | 사유 |")
    report.append("|---|---|---|")
    for row in date_issues[:20]:
        report.append("| " + str(row[0]) + " | " + str(row[1]) + " | " + str(row[2]) + " |")
    issues_summary.append(("8. 날짜 이상", len(date_issues), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 없음 ✅")
    issues_summary.append(("8. 날짜 이상", 0, "🟢 Info"))
report.append("")

# 9. out/stock/ vs DB ticker
print("Check 9: stock pages vs DB...")
stock_dir = os.path.join(BASE, "out", "stock")
stock_pages = set()
if os.path.isdir(stock_dir):
    for f in os.listdir(stock_dir):
        if f.endswith(".html"):
            stock_pages.add(f.replace(".html",""))

db_tickers = set()
for s in signals:
    t = s.get("ticker","")
    if t:
        db_tickers.add(t)

missing_pages = db_tickers - stock_pages
extra_pages = stock_pages - db_tickers

report.append("## 9. 종목 페이지 vs DB ticker 비교")
report.append("**DB ticker 수:** " + str(len(db_tickers)))
report.append("**종목 페이지 수:** " + str(len(stock_pages)))
report.append("")
if missing_pages:
    severity = "🟡 Warning"
    report.append("**시그널은 있는데 페이지 없는 ticker:** " + str(len(missing_pages)) + "개")
    report.append("")
    for t in sorted(missing_pages):
        report.append("- " + t)
    report.append("")
    issues_summary.append(("9. 페이지 누락", len(missing_pages), severity))
else:
    report.append("**결과:** 모두 매칭 ✅")
    issues_summary.append(("9. 페이지 누락", 0, "🟢 Info"))
if extra_pages:
    report.append("**페이지는 있는데 DB에 시그널 없는 ticker:** " + str(len(extra_pages)) + "개")
    for t in sorted(extra_pages):
        report.append("- " + t)
report.append("")

# 10. stockPrices.json empty prices
print("Check 10: stockPrices.json...")
sp_path = os.path.join(BASE, "data", "stockPrices.json")
empty_prices = []
sp_tickers = set()
if os.path.exists(sp_path):
    with open(sp_path, "r", encoding="utf-8") as f:
        sp_data = json.load(f)
    sp_tickers = set(sp_data.keys())
    for k, v in sp_data.items():
        prices = v.get("prices", []) if isinstance(v, dict) else v
        if not prices:
            empty_prices.append(k)

report.append("## 10. stockPrices.json 빈 prices")
if empty_prices:
    severity = "🟡 Warning"
    report.append("**심각도:** " + severity)
    report.append("**발견:** " + str(len(empty_prices)) + "개")
    report.append("")
    for t in empty_prices[:20]:
        report.append("- " + t)
    issues_summary.append(("10. 빈 prices", len(empty_prices), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 없음 ✅")
    issues_summary.append(("10. 빈 prices", 0, "🟢 Info"))
report.append("")

# 11. stockPrices.json vs DB ticker
print("Check 11: stockPrices keys vs DB...")
sp_missing = db_tickers - sp_tickers

report.append("## 11. stockPrices.json 키 vs DB ticker 비교")
report.append("**stockPrices 키 수:** " + str(len(sp_tickers)))
report.append("**DB ticker 수:** " + str(len(db_tickers)))
if sp_missing:
    severity = "🟡 Warning"
    report.append("**DB에 있지만 stockPrices에 없는 ticker:** " + str(len(sp_missing)) + "개")
    report.append("")
    for t in sorted(sp_missing):
        report.append("- " + t)
    issues_summary.append(("11. stockPrices 누락", len(sp_missing), severity))
else:
    report.append("**결과:** 모두 매칭 ✅")
    issues_summary.append(("11. stockPrices 누락", 0, "🟢 Info"))
report.append("")

# 12. Live site check
print("Check 12: live site...")
report.append("## 12. 라이브 사이트 접근 확인")
live_base = "https://puing5555.github.io/invest-sns/"
pages_to_check = [
    ("메인", ""),
    ("index.html", "index.html"),
]
# Add a couple stock pages
sample_tickers = sorted(stock_pages)[:2]
for t in sample_tickers:
    pages_to_check.append(("종목:" + t, "stock/" + t + ".html"))

report.append("")
report.append("| 페이지 | URL | 상태 |")
report.append("|---|---|---|")
live_issues = 0
for name, path in pages_to_check:
    url = live_base + path
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            size = len(resp.read())
        result = "✅ " + str(status) + " (" + str(size) + "B)"
    except Exception as e:
        result = "❌ " + str(e)[:50]
        live_issues += 1
    report.append("| " + name + " | " + url + " | " + result + " |")

if live_issues:
    issues_summary.append(("12. 라이브 사이트", live_issues, "🔴 Critical"))
else:
    issues_summary.append(("12. 라이브 사이트", 0, "🟢 Info"))
report.append("")

# 13. signal_prices.json
print("Check 13: signal_prices.json...")
sigp_path = os.path.join(BASE, "data", "signal_prices.json")
uuid_keys = []
report.append("## 13. signal_prices.json 구조 점검")
if os.path.exists(sigp_path):
    with open(sigp_path, "r", encoding="utf-8") as f:
        sigp_data = json.load(f)
    report.append("**총 키 수:** " + str(len(sigp_data)))
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
    for k in sigp_data:
        if uuid_pattern.match(str(k)):
            uuid_keys.append(k)
    if uuid_keys:
        severity = "🟡 Warning"
        report.append("**UUID 키 발견:** " + str(len(uuid_keys)) + "개")
        for k in uuid_keys[:10]:
            report.append("- " + k)
        issues_summary.append(("13. UUID 키", len(uuid_keys), severity))
    else:
        report.append("**결과:** UUID 키 없음 ✅")
        issues_summary.append(("13. UUID 키", 0, "🟢 Info"))
else:
    report.append("**결과:** 파일 없음 ⚠️")
    issues_summary.append(("13. signal_prices.json", 1, "🟡 Warning"))
report.append("")

# 14. orphan video_id
print("Check 14: orphan video_id...")
video_ids_in_db = set(v.get("video_id","") for v in videos)
orphan_videos = []
for s in signals:
    vid = s.get("video_id","")
    if vid and vid not in video_ids_in_db:
        orphan_videos.append((s["id"], vid, s.get("stock","")))

report.append("## 14. video_id 고아 시그널 (influencer_videos에 없음)")
if orphan_videos:
    severity = "🔴 Critical"
    report.append("**심각도:** " + severity)
    report.append("**발견:** " + str(len(orphan_videos)) + "건")
    report.append("")
    report.append("| signal ID | video_id | stock |")
    report.append("|---|---|---|")
    for row in orphan_videos[:20]:
        report.append("| " + str(row[0]) + " | " + str(row[1]) + " | " + str(row[2]) + " |")
    if len(orphan_videos) > 20:
        report.append("| ... | 외 " + str(len(orphan_videos)-20) + "건 | |")
    report.append("")
    report.append("**제안:** 누락된 video 레코드 추가 또는 고아 시그널 정리")
    issues_summary.append(("14. 고아 video_id", len(orphan_videos), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 없음 ✅")
    issues_summary.append(("14. 고아 video_id", 0, "🟢 Info"))
report.append("")

# 15. orphan speaker_id
print("Check 15: orphan speaker_id...")
report.append("## 15. speaker_id 고아 시그널")
if speakers_exist:
    orphan_speakers = []
    for s in signals:
        sid = str(s.get("speaker_id",""))
        if sid and sid not in speaker_ids_in_db:
            orphan_speakers.append((s["id"], sid, s.get("stock","")))
    if orphan_speakers:
        severity = "🟡 Warning"
        report.append("**심각도:** " + severity)
        report.append("**발견:** " + str(len(orphan_speakers)) + "건")
        report.append("")
        report.append("| signal ID | speaker_id | stock |")
        report.append("|---|---|---|")
        for row in orphan_speakers[:20]:
            report.append("| " + str(row[0]) + " | " + str(row[1]) + " | " + str(row[2]) + " |")
        issues_summary.append(("15. 고아 speaker_id", len(orphan_speakers), severity))
    else:
        report.append("**심각도:** 🟢 Info")
        report.append("**결과:** 없음 ✅")
        issues_summary.append(("15. 고아 speaker_id", 0, "🟢 Info"))
else:
    report.append("**결과:** speakers 테이블 없음 — 스킵")
    issues_summary.append(("15. 고아 speaker_id", 0, "🟢 Info (no table)"))
report.append("")

# 16. review_status 분포
print("Check 16: review_status...")
rs_counts = Counter()
for s in signals:
    rs = s.get("review_status","") or "null"
    rs_counts[rs] += 1

report.append("## 16. review_status 분포")
report.append("")
report.append("| review_status | 건수 | 비율 |")
report.append("|---|---|---|")
total = len(signals)
for rs, cnt in rs_counts.most_common():
    pct = round(cnt / total * 100, 1) if total else 0
    report.append("| " + str(rs) + " | " + str(cnt) + " | " + str(pct) + "% |")
report.append("")
issues_summary.append(("16. review_status", 0, "🟢 Info"))
report.append("")

# 17. 같은 stock 다른 ticker
print("Check 17: stock-ticker mismatch...")
stock_to_tickers = defaultdict(set)
for s in signals:
    stock = s.get("stock","") or ""
    ticker = s.get("ticker","") or ""
    if stock and ticker:
        stock_to_tickers[stock].add(ticker)

mismatches = {k: v for k, v in stock_to_tickers.items() if len(v) > 1}

report.append("## 17. 같은 stock, 다른 ticker")
if mismatches:
    severity = "🔴 Critical"
    report.append("**심각도:** " + severity)
    report.append("**발견:** " + str(len(mismatches)) + "건")
    report.append("")
    report.append("| stock | tickers |")
    report.append("|---|---|")
    for stock, tickers in sorted(mismatches.items()):
        report.append("| " + stock + " | " + ", ".join(sorted(tickers)) + " |")
    report.append("")
    report.append("**제안:** ticker 통일 필요")
    issues_summary.append(("17. stock-ticker 불일치", len(mismatches), severity))
else:
    report.append("**심각도:** 🟢 Info")
    report.append("**결과:** 없음 ✅")
    issues_summary.append(("17. stock-ticker 불일치", 0, "🟢 Info"))
report.append("")

# Summary
report.append("---")
report.append("")
report.append("## 📊 종합 요약")
report.append("")
critical = sum(1 for _,cnt,sev in issues_summary if "Critical" in sev and cnt > 0)
warning = sum(1 for _,cnt,sev in issues_summary if "Warning" in sev and cnt > 0)
info_ok = sum(1 for _,cnt,sev in issues_summary if cnt == 0)
report.append("| 심각도 | 항목 수 |")
report.append("|---|---|")
report.append("| 🔴 Critical | " + str(critical) + " |")
report.append("| 🟡 Warning | " + str(warning) + " |")
report.append("| 🟢 정상 | " + str(info_ok) + " |")
report.append("")
report.append("### 항목별 결과")
report.append("")
report.append("| 항목 | 문제 수 | 심각도 |")
report.append("|---|---|---|")
for name, cnt, sev in issues_summary:
    report.append("| " + name + " | " + str(cnt) + " | " + sev + " |")

report.append("")
if critical > 0:
    report.append("⚠️ **Critical 이슈가 " + str(critical) + "건 있습니다. 우선 수정이 필요합니다.**")
if warning > 0:
    report.append("📋 **Warning " + str(warning) + "건은 데이터 품질 향상을 위해 검토가 권장됩니다.**")

out_path = os.path.join(BASE, "QA_REPORT.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("Report saved to", out_path)
print("Done!")
