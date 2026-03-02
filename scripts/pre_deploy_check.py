#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배포 전 자동 품질 검증 스크립트
Usage:
  python scripts/pre_deploy_check.py [--auto-fix] [--report]
Exit codes: 0=통과, 1=실패(수동 수정 필요)
"""

import argparse
import json
import os
import re
import sys
import glob
from urllib.request import Request, urlopen
from urllib.parse import quote
from collections import Counter, defaultdict
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env.local"

BLACKLIST_STOCKS = [
    "AI 에이전트", "DeFi", "NFT", "스테이블코인", "블록체인", "가상자산",
    "배당주", "금융주", "리츠", "부동산", "없음", "N/A", "n/a", "NA",
    "라울팔", "마이클버리", "워렌버핏", "캐시우드", "짐크레이머",
    "라울 팔", "마이클 버리", "워렌 버핏", "캐시 우드", "짐 크레이머",
]

VALID_SIGNALS = {
    "STRONG_BUY", "BUY", "POSITIVE", "HOLD", "NEUTRAL",
    "CONCERN", "SELL", "STRONG_SELL",
    # Korean equivalents (legacy)
    "강력매수", "매수", "긍정", "보유", "중립",
    "경계", "매도", "강력매도",
}

OVERSEAS_TICKERS = ["BTC", "ETH", "SOL", "DOGE", "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOG", "META"]

PLACEHOLDER_SUMMARIES = [
    "이 리포트에 대한 AI 분석을 확인해보세요",
    "AI 분석 준비 중",
    "분석 결과를 확인해보세요",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_env():
    """Load .env.local and return dict"""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

ENV = load_env()
SUPABASE_URL = ENV.get("NEXT_PUBLIC_SUPABASE_URL", "")
SUPABASE_KEY = ENV.get("SUPABASE_SERVICE_ROLE_KEY", "") or ENV.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")


def supabase_get(table, params="select=*"):
    """Fetch all rows from a Supabase table (handles pagination)."""
    all_rows = []
    limit = 1000
    offset = 0
    while True:
        sep = "&" if params else ""
        url = f"{SUPABASE_URL}/rest/v1/{table}?{params}{sep}limit={limit}&offset={offset}"
        req = Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "count=exact",
        })
        resp = urlopen(req)
        data = json.loads(resp.read())
        if not data:
            break
        all_rows.extend(data)
        if len(data) < limit:
            break
        offset += limit
    return all_rows


def supabase_delete(table, ids):
    """Delete rows by id list."""
    if not ids:
        return 0
    # Delete in batches
    deleted = 0
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        id_filter = ",".join(batch)
        url = f"{SUPABASE_URL}/rest/v1/{table}?id=in.({quote(id_filter)})"
        req = Request(url, method="DELETE", headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "return=minimal",
        })
        urlopen(req)
        deleted += len(batch)
    return deleted


def supabase_patch(table, row_id, data):
    """Update a single row."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}"
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, method="PATCH", headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    })
    urlopen(req)


class CheckResult:
    def __init__(self):
        self.results = []
        self.auto_fixed = 0
        self.manual_needed = 0

    def add(self, level, msg, detail=None):
        self.results.append({"level": level, "msg": msg, "detail": detail})
        if level == "FAIL":
            self.manual_needed += 1

    def add_pass(self, msg, detail=None): self.add("PASS", msg, detail)
    def add_warn(self, msg, detail=None): self.add("WARN", msg, detail)
    def add_fail(self, msg, detail=None): self.add("FAIL", msg, detail)
    def add_fix(self, msg, count=1, detail=None):
        self.results.append({"level": "FIX", "msg": msg, "detail": detail})
        self.auto_fixed += count

    def print_report(self, verbose=False):
        print("\n=== 배포 전 품질 검증 ===")
        for r in self.results:
            prefix = {"PASS": "✅ [PASS]", "WARN": "⚠️  [WARN]", "FAIL": "❌ [FAIL]", "FIX": "🔧 [FIX]"}[r["level"]]
            print(f"{prefix} {r['msg']}")
            if verbose and r.get("detail"):
                for line in r["detail"] if isinstance(r["detail"], list) else [r["detail"]]:
                    print(f"        {line}")
        print("===")
        if self.manual_needed > 0:
            print(f"검증 결과: FAIL (수동 수정 필요 {self.manual_needed}건, 자동 수정 {self.auto_fixed}건)")
            print("배포 불가")
        else:
            print(f"검증 결과: PASS (자동 수정 {self.auto_fixed}건)")
            print("배포 가능")

    @property
    def passed(self):
        return self.manual_needed == 0


# ─── Checks ───────────────────────────────────────────────────────────────────

def check_build_output(cr, verbose):
    """1. 빌드 결과 검증"""
    out_dir = PROJECT_ROOT / "out" / "stock"
    if not out_dir.exists():
        cr.add_warn("out/stock/ 폴더 없음 (빌드 안 됨 — 빌드 후 재검증 필요)")
        return

    html_files = list(out_dir.glob("*.html"))
    if not html_files:
        cr.add_fail("out/stock/ HTML 파일 0개")
        return

    # Check for error strings in HTML
    error_pages = []
    error_patterns = [
        r'\bError\b', r'\bundefined\b', r'\bNaN\b',
        r'404', r'Something went wrong',
    ]
    for f in html_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            # Only check visible text, skip script/style
            # Simple heuristic: check <body> content
            body_match = re.search(r'<body[^>]*>(.*)</body>', content, re.DOTALL | re.IGNORECASE)
            text = body_match.group(1) if body_match else content
            # Remove script/style tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            
            for pat in error_patterns:
                if re.search(pat, text):
                    # "Error" in Korean contexts might be OK, be selective
                    if pat == r'\bError\b' and ('Error' in text[:500] or 'error' in text[:500].lower()):
                        error_pages.append(f.name)
                        break
                    elif pat != r'\bError\b':
                        error_pages.append(f.name)
                        break
        except Exception:
            error_pages.append(f"{f.name} (읽기 실패)")

    if error_pages:
        cr.add_warn(f"종목 페이지: {len(html_files)}개 중 {len(error_pages)}개에 에러 문자열 감지",
                     error_pages[:10])
    else:
        cr.add_pass(f"종목 페이지: {len(html_files)}개 전부 존재, 에러 없음")


def check_chart_data(cr, verbose):
    """2. 차트 데이터 검증"""
    prices_file = PROJECT_ROOT / "data" / "stockPrices.json"
    if not prices_file.exists():
        cr.add_fail("data/stockPrices.json 없음")
        return

    prices = json.loads(prices_file.read_text(encoding="utf-8"))
    empty_stocks = []
    zero_overseas = []

    for ticker, data in prices.items():
        price_list = data.get("prices", []) if isinstance(data, dict) else data
        if not price_list or price_list is None:
            empty_stocks.append(ticker)
        if ticker.upper() in OVERSEAS_TICKERS:
            current = data.get("currentPrice", 0) if isinstance(data, dict) else 0
            if current == 0:
                zero_overseas.append(ticker)

    if empty_stocks:
        cr.add_fail(f"차트 데이터: {len(empty_stocks)}개 종목 가격 없음", empty_stocks)
    elif zero_overseas:
        cr.add_warn(f"해외종목 가격 0: {zero_overseas}")
    else:
        cr.add_pass(f"차트 데이터: {len(prices)}개 종목 전부 OK")

    # signal_prices.json
    sp_file = PROJECT_ROOT / "data" / "signal_prices.json"
    if not sp_file.exists():
        cr.add_fail("data/signal_prices.json 없음")
    else:
        sp = json.loads(sp_file.read_text(encoding="utf-8"))
        cr.add_pass(f"시그널 가격: {len(sp)}개 시그널 가격 데이터 존재")
        return sp

    return None


def check_db_signals(cr, auto_fix, verbose):
    """3. DB 시그널 검증"""
    signals = supabase_get("influencer_signals")
    if not signals:
        cr.add_warn("DB에 시그널 0개 (비어있음)")
        return signals

    cr.add_pass(f"DB 시그널: {len(signals)}개")

    # ─── 3a. 블랙리스트 종목 ───
    blacklisted = []
    for s in signals:
        stock = s.get("stock", "") or ""
        for bl in BLACKLIST_STOCKS:
            if bl.lower() in stock.lower():
                blacklisted.append(s)
                break

    if blacklisted:
        if auto_fix:
            ids = [s["id"] for s in blacklisted]
            deleted = supabase_delete("influencer_signals", ids)
            cr.add_fix(f"블랙리스트 종목 {len(blacklisted)}개 → 자동 삭제 완료", len(blacklisted),
                       [f"  {s.get('stock','')} (id: {s['id'][:8]}...)" for s in blacklisted[:10]])
            signals = [s for s in signals if s["id"] not in set(ids)]
        else:
            cr.add_fail(f"블랙리스트 종목 {len(blacklisted)}개 발견 (--auto-fix로 삭제 가능)",
                        [f"  {s.get('stock','')} (id: {s['id'][:8]}...)" for s in blacklisted[:10]])

    # ─── 3b. 중복 시그널 ───
    seen = {}
    duplicates = []
    for s in signals:
        key = (s.get("video_id"), (s.get("stock") or "").strip(), s.get("signal"))
        if key in seen:
            # Keep the one with ticker, mark the other for deletion
            existing = seen[key]
            if s.get("ticker") and not existing.get("ticker"):
                duplicates.append(existing)
                seen[key] = s
            else:
                duplicates.append(s)
        else:
            seen[key] = s

    if duplicates:
        if auto_fix:
            ids = [s["id"] for s in duplicates]
            deleted = supabase_delete("influencer_signals", ids)
            cr.add_fix(f"중복 시그널 {len(duplicates)}개 → 자동 삭제 완료", len(duplicates))
            signals = [s for s in signals if s["id"] not in set(ids)]
        else:
            cr.add_fail(f"중복 시그널 {len(duplicates)}개 발견 (--auto-fix로 삭제 가능)")

    # ─── 3c. speaker-channel 불일치 ───
    videos = supabase_get("influencer_videos")
    speakers = supabase_get("speakers")
    channels = supabase_get("influencer_channels")

    video_map = {v["id"]: v for v in videos}  # video_id -> video (has channel_id)
    speaker_map = {s["id"]: s for s in speakers}
    channel_map = {c["id"]: c for c in channels}

    # Build channel -> expected speaker mapping
    # A channel's speaker = the speaker most frequently used in that channel's signals
    channel_speaker_counts = defaultdict(lambda: Counter())
    for s in signals:
        vid = video_map.get(s.get("video_id"))
        if vid and s.get("speaker_id"):
            channel_speaker_counts[vid.get("channel_id")][s["speaker_id"]] += 1

    channel_primary_speaker = {}
    for ch_id, counter in channel_speaker_counts.items():
        if counter:
            channel_primary_speaker[ch_id] = counter.most_common(1)[0][0]

    mismatches = []
    for s in signals:
        vid = video_map.get(s.get("video_id"))
        if not vid:
            continue
        ch_id = vid.get("channel_id")
        expected_speaker = channel_primary_speaker.get(ch_id)
        if expected_speaker and s.get("speaker_id") and s["speaker_id"] != expected_speaker:
            mismatches.append((s, expected_speaker))

    if mismatches:
        if auto_fix:
            fixed = 0
            for s, expected in mismatches:
                try:
                    supabase_patch("influencer_signals", s["id"], {"speaker_id": expected})
                    fixed += 1
                except Exception:
                    pass
            cr.add_fix(f"speaker-channel 불일치 {len(mismatches)}개 → {fixed}개 자동 수정", fixed)
        else:
            cr.add_fail(f"speaker-channel 불일치 {len(mismatches)}개 (--auto-fix로 수정 가능)")

    # ─── 3d. 타임스탬프 0:00 비율 ───
    zero_ts = [s for s in signals if (s.get("timestamp") or "") in ("0:00", "00:00", "0:0", "")]
    ratio = len(zero_ts) / len(signals) * 100 if signals else 0
    if ratio >= 20:
        cr.add_warn(f"타임스탬프 0:00: {ratio:.0f}% ({len(zero_ts)}/{len(signals)}) — 20% 이상 경고")
    else:
        cr.add_pass(f"타임스탬프 0:00: {ratio:.0f}% ({len(zero_ts)}/{len(signals)})")

    # ─── 3e. 수익률 null 비율 ───
    # (return_pct is in signal_prices, not in signals table — skip or check signal_prices)

    # ─── 3f. 시그널 타입 검증 ───
    invalid_signals = [s for s in signals if s.get("signal") not in VALID_SIGNALS]
    if invalid_signals:
        invalid_types = Counter(s.get("signal") for s in invalid_signals)
        cr.add_fail(f"잘못된 시그널 타입 {len(invalid_signals)}개: {dict(invalid_types)}")
    else:
        cr.add_pass(f"시그널 타입: 전부 유효 ({len(signals)}개)")

    # ─── 3g. 날짜 형식 검증 ───
    # Check video published_at dates
    bad_dates = []
    for v in videos:
        pa = v.get("published_at", "")
        if pa and not re.match(r'\d{4}-\d{2}-\d{2}', str(pa)):
            bad_dates.append(v.get("title", v["id"])[:30])
    if bad_dates:
        cr.add_warn(f"날짜 형식 이상 {len(bad_dates)}개", bad_dates[:5])
    else:
        cr.add_pass("날짜 형식: 전부 정상")

    # ─── 3h. 종목명 형식 검증 ───
    # Expected: "종목명 (TICKER)" or just Korean name
    no_ticker = [s for s in signals if s.get("stock") and not s.get("ticker")]
    if no_ticker:
        ratio = len(no_ticker) / len(signals) * 100
        cr.add_warn(f"ticker 없는 시그널: {len(no_ticker)}개 ({ratio:.0f}%)")
    else:
        cr.add_pass("종목명-ticker: 전부 매칭됨")

    return signals


def check_data_consistency(cr, signals, verbose):
    """4. 데이터 정합성"""
    sp_file = PROJECT_ROOT / "data" / "signal_prices.json"
    if not sp_file.exists():
        return

    sp = json.loads(sp_file.read_text(encoding="utf-8"))
    db_count = len(signals) if signals else 0
    file_count = len(sp)

    diff = abs(db_count - file_count)
    if diff > 10:
        cr.add_warn(f"시그널 수 불일치: DB {db_count}개 vs signal_prices.json {file_count}개 (차이 {diff})")
    else:
        cr.add_pass(f"데이터 정합성: DB {db_count}개, signal_prices {file_count}개 (차이 {diff})")

    # 인플루언서별 시그널 수
    if signals:
        speaker_counts = Counter(s.get("speaker_id") for s in signals)
        speakers = supabase_get("speakers")
        speaker_names = {s["id"]: s.get("name", "?") for s in speakers}
        detail = [f"{speaker_names.get(sid, sid[:8])}: {cnt}개" for sid, cnt in speaker_counts.most_common(10)]
        cr.add_pass(f"인플루언서별 시그널 (상위 {min(10, len(speaker_counts))}명)", detail if verbose else None)


def check_content_quality(cr, verbose):
    """5. 콘텐츠 품질"""
    # 5a. 영상보기 URL에 t= 파라미터
    signals = supabase_get("influencer_signals")
    videos = supabase_get("influencer_videos")
    video_map = {v["id"]: v for v in videos}

    # Check if timestamps are being used (t= param would be constructed at frontend)
    # We check if timestamp field exists and is meaningful
    no_timestamp = [s for s in signals if not s.get("timestamp") or s.get("timestamp") in ("0:00", "00:00")]
    if no_timestamp:
        ratio = len(no_timestamp) / len(signals) * 100 if signals else 0
        if ratio > 30:
            cr.add_warn(f"유효 타임스탬프 없는 시그널: {ratio:.0f}% — 영상보기 t= 파라미터 부정확할 수 있음")

    # 5b. 애널리스트 리포트 placeholder 확인
    reports = supabase_get("analyst_reports")
    if reports:
        placeholder_reports = []
        null_analyst = []
        for r in reports:
            summary = r.get("ai_summary") or r.get("summary") or ""
            for ph in PLACEHOLDER_SUMMARIES:
                if ph in summary:
                    placeholder_reports.append(r)
                    break
            analyst = r.get("analyst_name") or r.get("analyst") or ""
            if not analyst or analyst in ("-", "null", "None"):
                null_analyst.append(r)

        if placeholder_reports:
            cr.add_warn(f"애널리스트 리포트 placeholder 요약: {len(placeholder_reports)}개")
        else:
            cr.add_pass(f"애널리스트 리포트: {len(reports)}개 요약 정상")

        if null_analyst:
            ratio = len(null_analyst) / len(reports) * 100
            cr.add_warn(f"애널리스트명 null/'-': {len(null_analyst)}개 ({ratio:.0f}%)")
    else:
        cr.add_warn("애널리스트 리포트 0개")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="배포 전 품질 검증")
    parser.add_argument("--auto-fix", action="store_true", help="자동 수정 가능한 항목 수정")
    parser.add_argument("--report", action="store_true", help="상세 보고서 출력")
    args = parser.parse_args()

    # Fix Windows encoding
    import io
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    verbose = args.report
    auto_fix = args.auto_fix
    cr = CheckResult()

    print("🔍 품질 검증 시작...\n")

    # 1. 빌드 결과
    check_build_output(cr, verbose)

    # 2. 차트 데이터
    check_chart_data(cr, verbose)

    # 3. DB 시그널
    signals = check_db_signals(cr, auto_fix, verbose)

    # 4. 데이터 정합성
    check_data_consistency(cr, signals, verbose)

    # 5. 콘텐츠 품질
    check_content_quality(cr, verbose)

    # 결과 출력
    cr.print_report(verbose)

    sys.exit(0 if cr.passed else 1)


if __name__ == "__main__":
    main()
