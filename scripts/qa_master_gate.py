"""
qa_master_gate.py — QA_CHECKLIST_MASTER.md A1~A8 자동 검증 스크립트
Supabase에서 시그널 조회 → 검증 → 리포트 출력

사용법:
  python qa_master_gate.py                  # 전체 시그널 검증
  python qa_master_gate.py --recent 100     # 최근 100개만
  python qa_master_gate.py --video VIDEO_ID # 특정 영상만
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

# .env.local에서 Supabase 키 읽기
def load_env():
    env_paths = [
        Path(__file__).parent.parent / ".env.local",
        Path(__file__).parent.parent / ".env",
    ]
    env = {}
    for p in env_paths:
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_env()
SUPABASE_URL = env.get("NEXT_PUBLIC_SUPABASE_URL") or env.get("SUPABASE_URL", "")
SUPABASE_KEY = env.get("SUPABASE_SERVICE_ROLE_KEY") or env.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ SUPABASE_URL 또는 SUPABASE_KEY를 .env.local에서 찾을 수 없음")
    sys.exit(1)

try:
    from supabase import create_client
except ImportError:
    print("❌ supabase 패키지 필요: pip install supabase")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── 블랙리스트 ───
CRYPTO_TICKERS = {"BTC", "ETH", "XRP", "SOL", "DOGE", "ADA", "BNB", "AVAX", "DOT", "MATIC", "LINK", "UNI", "ATOM", "LTC", "BCH", "SHIB", "APT", "ARB", "OP", "FIL"}
CRYPTO_NAMES = {"비트코인", "이더리움", "리플", "솔라나", "도지코인", "에이다", "바이낸스", "아발란체", "폴카닷", "매틱", "체인링크", "유니스왑", "라이트코인"}
COMMODITY_TICKERS = {"GLD", "SLV", "GC", "SI", "CL", "NG", "HG", "WTI", "BRENT"}
COMMODITY_NAMES = {"금", "은", "구리", "천연가스", "원유", "팔라듐", "백금", "철광석"}
CURRENCY_NAMES = {"달러", "엔", "유로", "위안", "파운드", "원화"}
CURRENCY_TICKERS = {"DXY", "USDKRW", "USDJPY", "EURUSD"}
UNLISTED = {"스페이스x", "spacex", "오픈ai", "openai", "웨이모", "야놀자", "화웨이", "바이트댄스", "삼성파운드리", "삼성디스플레이"}

VALID_SIGNAL_TYPES = {"STRONG_BUY", "BUY", "POSITIVE", "HOLD", "NEUTRAL", "CONCERN", "SELL", "STRONG_SELL"}

# ─── 검증 함수 ───

def check_a1(sig):
    """비종목 필터링"""
    ticker = (sig.get("ticker") or "").upper()
    name = (sig.get("stock_name") or "").lower()
    if ticker in CRYPTO_TICKERS or any(c in name for c in CRYPTO_NAMES):
        return False, f"암호화폐: {ticker or name}"
    if ticker in COMMODITY_TICKERS or any(c in name for c in COMMODITY_NAMES):
        return False, f"원자재: {ticker or name}"
    if ticker in CURRENCY_TICKERS or any(c in name for c in CURRENCY_NAMES):
        return False, f"통화: {ticker or name}"
    return True, ""

def check_a2(sig):
    """비상장기업"""
    name = (sig.get("stock_name") or "").lower()
    ticker = (sig.get("ticker") or "").strip()
    if any(u in name for u in UNLISTED):
        return False, f"비상장: {sig.get('stock_name')}"
    if not ticker:
        return False, f"ticker 없음: {sig.get('stock_name')}"
    return True, ""

def check_a3(sig):
    """key_quote 품질"""
    kq = sig.get("key_quote") or ""
    issues = []
    if len(kq) < 20:
        issues.append(f"길이 {len(kq)}자 < 20자")
    if len(kq) > 200:
        issues.append(f"길이 {len(kq)}자 > 200자")
    # 자동자막 오류: 한글+영어 랜덤 혼합 (공백 기준 토큰의 절반 이상이 영어)
    if kq:
        tokens = kq.split()
        if len(tokens) > 3:
            en_tokens = sum(1 for t in tokens if re.match(r'^[a-zA-Z]+$', t))
            ko_tokens = sum(1 for t in tokens if re.search(r'[가-힣]', t))
            if en_tokens > 0 and ko_tokens > 0 and en_tokens / len(tokens) > 0.4:
                issues.append("자동자막 오류 의심 (한영 혼합)")
    if issues:
        return False, "; ".join(issues)
    return True, ""

def check_a4(sig):
    """signal_date"""
    sd = sig.get("signal_date") or ""
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    if sd == today:
        return False, f"오늘 날짜 사용: {sd}"
    if sd >= tomorrow:
        return False, f"미래 날짜: {sd}"
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', sd):
        return False, f"날짜 형식 오류: {sd}"
    return True, ""

def check_a5(sig):
    """timestamp"""
    ts = sig.get("timestamp") or "00:00"
    if ts in ("00:00", "0:00", "00:00:00"):
        return False, "timestamp 00:00"
    return True, ""

def check_a7(sig):
    """signal_type 유효성"""
    st = (sig.get("signal_type") or "").strip()
    if not st:
        return False, "signal_type 빈값"
    if st not in VALID_SIGNAL_TYPES:
        return False, f"잘못된 signal_type: {st}"
    return True, ""

def check_a8(sig):
    """confidence 범위"""
    c = sig.get("confidence")
    if c is None:
        return False, "confidence 없음"
    try:
        c = float(c)
    except (ValueError, TypeError):
        return False, f"confidence 숫자 아님: {c}"
    if c < 0 or c > 1:
        return False, f"confidence 범위 밖: {c}"
    if c < 0.5:
        return False, f"confidence 0.5 미만: {c}"
    return True, ""

# ─── 메인 ───

def fetch_signals(args):
    query = supabase.table("signals").select("*")
    if args.video:
        query = query.eq("video_id", args.video)
    if args.recent:
        query = query.order("created_at", desc=True).limit(args.recent)
    else:
        query = query.order("created_at", desc=True).limit(5000)
    res = query.execute()
    return res.data or []

def check_a6(signals):
    """중복 체크 — 전체 시그널 대상"""
    seen_vid_ticker = {}
    issues = {}
    for s in signals:
        key = (s.get("video_id"), s.get("ticker"))
        sid = s.get("id", "?")
        if key[0] and key[1]:
            if key in seen_vid_ticker:
                issues[sid] = f"중복: video={key[0]}, ticker={key[1]} (기존 id={seen_vid_ticker[key]})"
            else:
                seen_vid_ticker[key] = sid
    return issues

def run_qa(args):
    print("📡 Supabase에서 시그널 조회 중...")
    signals = fetch_signals(args)
    total = len(signals)
    print(f"📊 총 시그널 수: {total}\n")

    if total == 0:
        print("시그널 없음. 종료.")
        return

    checks = {
        "A1": ("비종목 필터링", check_a1),
        "A2": ("비상장기업", check_a2),
        "A3": ("key_quote 품질", check_a3),
        "A4": ("signal_date", check_a4),
        "A5": ("timestamp", check_a5),
        "A7": ("signal_type", check_a7),
        "A8": ("confidence", check_a8),
    }

    results = {k: {"pass": 0, "fail": 0, "errors": []} for k in checks}
    results["A6"] = {"pass": 0, "fail": 0, "errors": []}

    # A1~A5, A7, A8: 개별 시그널 검증
    for sig in signals:
        sid = sig.get("id", "?")
        for code, (name, fn) in checks.items():
            ok, msg = fn(sig)
            if ok:
                results[code]["pass"] += 1
            else:
                results[code]["fail"] += 1
                results[code]["errors"].append(f"signal_id={sid}: {msg}")

    # A6: 중복 체크
    dup_issues = check_a6(signals)
    results["A6"]["fail"] = len(dup_issues)
    results["A6"]["pass"] = total - len(dup_issues)
    results["A6"]["errors"] = [f"signal_id={k}: {v}" for k, v in dup_issues.items()]

    # A5 추가: 00:00 비율 체크
    zero_ts = results["A5"]["fail"]
    if total > 0 and zero_ts / total > 0.1:
        print(f"⚠️  timestamp '00:00' 비율: {zero_ts}/{total} ({zero_ts/total*100:.1f}%) — 10% 초과!\n")

    # A8 추가: 동일 confidence 체크
    confs = [sig.get("confidence") for sig in signals if sig.get("confidence") is not None]
    if confs and len(set(confs)) == 1 and total > 5:
        results["A8"]["errors"].append(f"모든 시그널 confidence 동일: {confs[0]}")

    # A4 추가: 동일 날짜 체크
    dates = [sig.get("signal_date") for sig in signals if sig.get("signal_date")]
    if dates and len(set(dates)) == 1 and total > 10:
        results["A4"]["errors"].append(f"⚠️ 모든 시그널 동일 날짜: {dates[0]} (배치 버그 의심)")

    # ─── 리포트 출력 ───
    print("═" * 50)
    print("  QA 검증 결과 리포트")
    print(f"  실행일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 50)
    print(f"\n📊 총 시그널 수: {total}\n")
    print("🔴 A섹션: 시그널 데이터 품질")

    total_pass = 0
    total_checks = 0
    check_order = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
    check_names = {
        "A1": "비종목 필터링", "A2": "비상장기업", "A3": "key_quote 품질",
        "A4": "signal_date", "A5": "timestamp", "A6": "중복 체크",
        "A7": "signal_type", "A8": "confidence",
    }

    for code in check_order:
        r = results[code]
        p, f = r["pass"], r["fail"]
        total_pass += p
        total_checks += p + f
        icon = "✅" if f == 0 else "❌"
        print(f"  {code} {check_names[code]:12s}: {p}/{p+f} {icon}")

    rate = (total_pass / total_checks * 100) if total_checks > 0 else 0
    print(f"\n  A섹션 통과율: {rate:.1f}%")

    if rate >= 95:
        verdict = "✅ 통과 — INSERT 진행 가능"
    elif rate >= 80:
        verdict = "⚠️ 부분수정 — 이슈 항목 수정 후 재검증"
    else:
        verdict = "🚫 전체재작업 — 파이프라인부터 재실행"

    print(f"\n{'═' * 50}")
    print(f"  최종 판정: {verdict}")
    print(f"{'═' * 50}")

    # 오류 목록 (최대 30개)
    all_errors = []
    for code in check_order:
        severity = "🔴" if code in ("A1", "A2", "A4", "A7") else "🟡"
        for e in results[code]["errors"]:
            all_errors.append(f"  {severity} [{code}] {e}")

    if all_errors:
        print(f"\n❌ 오류 목록 (상위 {min(30, len(all_errors))}건 / 총 {len(all_errors)}건):")
        for e in all_errors[:30]:
            print(e)
        if len(all_errors) > 30:
            print(f"  ... 외 {len(all_errors) - 30}건")

    return rate >= 95

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA Master Gate — A1~A8 자동 검증")
    parser.add_argument("--recent", type=int, help="최근 N개 시그널만 검증")
    parser.add_argument("--video", type=str, help="특정 video_id만 검증")
    args = parser.parse_args()

    passed = run_qa(args)
    sys.exit(0 if passed else 1)
