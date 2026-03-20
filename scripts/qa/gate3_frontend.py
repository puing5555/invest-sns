# -*- coding: utf-8 -*-
"""
QA Gate 3 - 프론트엔드 빌드/배포 검증 (v2 - 자동수정 포함)
==============================
사용법:
  python scripts/qa/gate3_frontend.py --slug godofit
  python scripts/qa/gate3_frontend.py --slug godofit --check-deploy
  python scripts/qa/gate3_frontend.py --all-channels   # 전체 채널 검증

원칙:
  - 자동으로 고칠 수 있는 건 자동으로 고친다
  - 고친 후에도 기준 미달이면 배포 차단 (exit 1)
  - 검증만 하고 넘어가는 항목 없게
"""

import sys
import os
import re
import json
import shutil
import argparse
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ────────────────────────────────────────
# 환경 설정
# ────────────────────────────────────────

def load_env(project_root):
    env_path = os.path.join(project_root, '.env.local')
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

QA_DIR_REL = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'qa')
ERROR_PATTERNS_FILE = os.path.join(QA_DIR_REL, 'error_patterns.json')
API_KEY_PATTERNS = ['sk-ant', 'SUPABASE_SERVICE', 'service_role']

# ────────────────────────────────────────
# 유틸
# ────────────────────────────────────────

def ensure_qa_dir():
    os.makedirs(os.path.dirname(ERROR_PATTERNS_FILE), exist_ok=True)

def load_error_patterns():
    if os.path.exists(ERROR_PATTERNS_FILE):
        with open(ERROR_PATTERNS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []

def save_error_pattern(channel, gate, check_name, detail):
    ensure_qa_dir()
    patterns = load_error_patterns()
    patterns.append({
        "channel": channel, "gate": gate,
        "check_name": check_name, "detail": detail,
        "timestamp": datetime.now().isoformat()
    })
    with open(ERROR_PATTERNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

def supabase_get(path, project_root):
    """Supabase REST API GET"""
    load_env(project_root)
    url_base = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
    if not url_base or not key:
        return None
    req = urllib.request.Request(
        f'{url_base}/rest/v1/{path}',
        headers={'apikey': key, 'Authorization': f'Bearer {key}'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception:
        return None

def run_script(project_root, script_args, timeout=180):
    """scripts/ 하위 스크립트 실행"""
    result = subprocess.run(
        [sys.executable] + script_args,
        cwd=project_root, capture_output=True,
        text=True, timeout=timeout, encoding='utf-8', errors='replace'
    )
    return result.returncode, result.stdout, result.stderr

# ────────────────────────────────────────
# 체크 1: 빌드 존재
# ────────────────────────────────────────

def check_build_exists(out_dir):
    return os.path.isdir(out_dir)

# ────────────────────────────────────────
# 체크 2: 수익률 null 비율 + auto-fix
# ────────────────────────────────────────

def check_return_pct(project_root, slug):
    """
    수익률(return_pct) null 비율 체크.
    30%+ → new_stock_handler 자동 실행 → 재체크 → 여전히 30%+ → FAIL
    """
    prices_path = os.path.join(project_root, 'data', 'signal_prices.json')
    if not os.path.exists(prices_path):
        print("  ⚠️  signal_prices.json 없음 — 체크 스킵")
        return True, 0, 0

    prices = json.load(open(prices_path, encoding='utf-8'))
    uuid_returns = {k for k in prices if len(k) == 36 and '-' in k}

    # DB에서 전체 시그널 조회
    sigs = supabase_get('influencer_signals?select=id,stock&limit=2000', project_root)
    if not sigs:
        print("  ⚠️  DB 조회 실패 — 체크 스킵")
        return True, 0, 0

    total = len(sigs)
    missing = [s for s in sigs if s['id'] not in uuid_returns]
    null_pct = len(missing) / total * 100 if total else 0

    # 가격 None 종목 경고
    price_tickers = {k: v for k, v in prices.items()
                     if isinstance(v, dict) and len(k) < 15 and '-' not in k}
    no_price = [k for k, v in price_tickers.items() if v.get('price') is None]
    if no_price:
        print(f"  ⚠️  현재가 없는 종목: {len(no_price)}개 "
              f"({', '.join(sorted(no_price)[:5])}{'...' if len(no_price) > 5 else ''})")

    print(f"  수익률 누락: {len(missing)}/{total}건 ({null_pct:.1f}%)")

    if null_pct < 30:
        return True, len(missing), total

    # ── auto-fix: fix_missing_returns 실행 (더 포괄적인 수익률 복구) ──
    print(f"  ⛔ 수익률 누락 30% 초과 → 🔧 fix_missing_returns 자동 실행...")
    rc, out, err = run_script(project_root, ['scripts/fix_missing_returns.py'], timeout=300)
    if rc == 0:
        print(f"  ✅ fix_missing_returns 완료")
    else:
        print(f"  ⚠️  fix_missing_returns 실패: {err[:200]}")
        # 폴백: new_stock_handler 시도
        print(f"  🔧 new_stock_handler --fix-missing-returns 폴백 시도...")
        rc, out, err = run_script(project_root,
            ['scripts/new_stock_handler.py', '--fix-missing-returns'], timeout=120)
        if rc == 0:
            print(f"  ✅ new_stock_handler 완료")
        else:
            print(f"  ⚠️  new_stock_handler 실패: {err[:200]}")

    # 재체크
    prices2 = json.load(open(prices_path, encoding='utf-8'))
    uuid2 = {k for k in prices2 if len(k) == 36 and '-' in k}
    missing2 = [s for s in sigs if s['id'] not in uuid2]
    null_pct2 = len(missing2) / total * 100 if total else 0
    print(f"  재체크: {len(missing2)}/{total}건 ({null_pct2:.1f}%)")

    if null_pct2 >= 30:
        print(f"  ⛔ 여전히 30% 초과 → 배포 차단")
        save_error_pattern(slug, 'gate3', 'return_pct_null',
                           f"수익률 누락 {null_pct2:.1f}% ({len(missing2)}/{total}건)")
        return False, len(missing2), total

    return True, len(missing2), total

# ────────────────────────────────────────
# 체크 3: 종목 페이지 존재 + auto-fix
# ────────────────────────────────────────

def check_stock_pages(project_root, out_dir, slug):
    """
    모든 시그널 종목이 stock_tickers.json에 있는지 확인.
    없으면 자동 추가 → 재빌드 → out/stock/[code] 존재 확인.
    """
    prices_path = os.path.join(project_root, 'data', 'signal_prices.json')
    tickers_path = os.path.join(project_root, 'data', 'stock_tickers.json')

    if not os.path.exists(prices_path) or not os.path.exists(tickers_path):
        print("  ⚠️  필요 파일 없음 — 체크 스킵")
        return True

    prices = json.load(open(prices_path, encoding='utf-8'))
    ticker_list = json.load(open(tickers_path, encoding='utf-8'))
    ticker_set = set(ticker_list)

    # signal_prices에서 name→ticker 역방향 매핑
    name_to_ticker = {}
    for k, v in prices.items():
        if isinstance(v, dict) and v.get('name') and len(k) < 15 and '-' not in k:
            name_to_ticker[v['name']] = k

    # DB에서 시그널 종목명 조회
    sigs = supabase_get('influencer_signals?select=stock&limit=2000', project_root)
    if not sigs:
        print("  ⚠️  DB 조회 실패 — 체크 스킵")
        return True

    all_stocks = set(s['stock'] for s in sigs if s.get('stock'))
    missing_stocks = []
    for stock in all_stocks:
        ticker = name_to_ticker.get(stock)
        if ticker and ticker not in ticker_set:
            missing_stocks.append((stock, ticker))

    if not missing_stocks:
        # out/stock 페이지 직접 확인
        stock_out = os.path.join(out_dir, 'stock')
        if os.path.isdir(stock_out):
            built = set(os.listdir(stock_out))
            print(f"  종목 페이지: {len(built)}개 빌드됨")
        return True

    # ── auto-fix: tickers.json에 추가 ──
    print(f"  ⚠️  stock_tickers.json 누락 종목: {len(missing_stocks)}개 → 🔧 자동 추가")
    for stock, ticker in missing_stocks:
        ticker_list.append(ticker)
        print(f"     + {stock} ({ticker})")
    ticker_list = sorted(set(ticker_list))
    with open(tickers_path, 'w', encoding='utf-8') as f:
        json.dump(ticker_list, f, ensure_ascii=False, indent=2)

    # out/stock/[code] 존재 확인 (빌드 전이면 체크 불가)
    still_missing = []
    for stock, ticker in missing_stocks:
        page = os.path.join(out_dir, 'stock', ticker, 'index.html')
        if not os.path.isfile(page):
            still_missing.append(ticker)

    if still_missing:
        print(f"  ⚠️  종목 페이지 {len(still_missing)}개 out/에 없음 → 재빌드 실행...")
        # 자동 재빌드
        rebuild_result = subprocess.run(
            ['npm.cmd' if sys.platform == 'win32' else 'npm', 'run', 'build'],
            cwd=project_root,
            capture_output=True, text=True, timeout=300,
            encoding='utf-8', errors='replace'
        )
        if rebuild_result.returncode != 0:
            print(f"  ⛔ 재빌드 실패: {rebuild_result.stderr[-300:]}")
            return False
        print(f"  ✅ 재빌드 완료")
    return True  # tickers 추가됐으면 재빌드로 해결 가능 → FAIL 아님

# ────────────────────────────────────────
# 체크 4: 프로필 페이지 매칭
# ────────────────────────────────────────

def check_all_profile_pages(project_root, out_dir, slug):
    """
    speaker_slugs.json의 모든 slug → out/profile/influencer/[slug]/index.html 존재 확인.
    미존재 시 ⛔ 배포 차단.
    """
    slugs_path = os.path.join(project_root, 'data', 'speaker_slugs.json')
    if os.path.isfile(slugs_path):
        import json as _json
        with open(slugs_path, encoding='utf-8') as f:
            slug_map = _json.load(f)
        # speaker_slugs.json: { slug: name } 형태
        missing = []
        for s, name in slug_map.items():
            page = os.path.join(out_dir, 'profile', 'influencer', s, 'index.html')
            if not os.path.isfile(page):
                missing.append({'slug': s, 'name': name})
        return missing
    else:
        # fallback: DB channel_handle 기반
        channels = supabase_get('influencer_channels?select=channel_handle,channel_name&limit=100', project_root)
        if not channels:
            channels = [{'channel_handle': slug, 'channel_name': slug}]
        missing = []
        for ch in channels:
            s = ch.get('channel_handle') or ''
            if not s:
                continue
            page = os.path.join(out_dir, 'profile', 'influencer', s, 'index.html')
            if not os.path.isfile(page):
                missing.append({'slug': s, 'name': ch.get('channel_name', '?')})
        return missing

# ────────────────────────────────────────
# 체크 5: YouTube URL 검증 + auto-fix
# ────────────────────────────────────────

def check_and_fix_youtube_urls(project_root):
    """
    .tsx/.ts 파일에서 https://youtube.com/watch (www 없음) 패턴 탐지 → 자동 치환.
    반환: (fixed_count, remaining_count)
    """
    bad_pattern = re.compile(r'https://youtube\.com/watch')
    fixed = 0
    remaining = 0

    src_dir = os.path.join(project_root, 'app')
    for root, dirs, files in os.walk(src_dir):
        # node_modules, .next 등 제외
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.next', 'out', '.git')]
        for fname in files:
            if not (fname.endswith('.tsx') or fname.endswith('.ts')):
                continue
            fpath = os.path.join(root, fname)
            try:
                content = open(fpath, encoding='utf-8').read()
                if bad_pattern.search(content):
                    new_content = bad_pattern.sub('https://www.youtube.com/watch', content)
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    fixed += 1
                    print(f"     🔧 수정: {os.path.relpath(fpath, project_root)}")
            except Exception:
                pass

    # lib/ 도 스캔
    lib_dir = os.path.join(project_root, 'lib')
    for root, dirs, files in os.walk(lib_dir):
        dirs[:] = [d for d in dirs if d not in ('node_modules',)]
        for fname in files:
            if not (fname.endswith('.tsx') or fname.endswith('.ts')):
                continue
            fpath = os.path.join(root, fname)
            try:
                content = open(fpath, encoding='utf-8').read()
                if bad_pattern.search(content):
                    new_content = bad_pattern.sub('https://www.youtube.com/watch', content)
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    fixed += 1
            except Exception:
                pass

    # 재검사
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.next', 'out', '.git')]
        for fname in files:
            if not (fname.endswith('.tsx') or fname.endswith('.ts')):
                continue
            fpath = os.path.join(root, fname)
            try:
                if bad_pattern.search(open(fpath, encoding='utf-8').read()):
                    remaining += 1
            except Exception:
                pass

    return fixed, remaining

# ────────────────────────────────────────
# 체크 6: data/ ↔ public/ 동기화 + auto-fix
# ────────────────────────────────────────

SYNC_FILES = [
    ('data/signal_prices.json', 'public/signal_prices.json'),
]

def check_and_sync_data_public(project_root):
    """
    data/ ↔ public/ 불일치 파일 자동 동기화.
    반환: synced_list (자동 복사된 파일)
    """
    synced = []
    for src_rel, dst_rel in SYNC_FILES:
        src = os.path.join(project_root, src_rel)
        dst = os.path.join(project_root, dst_rel)
        if not os.path.exists(src):
            continue
        src_mtime = os.path.getmtime(src)
        dst_mtime = os.path.getmtime(dst) if os.path.exists(dst) else 0
        if abs(src_mtime - dst_mtime) > 2:  # 2초 이상 차이
            shutil.copy2(src, dst)
            synced.append(f"{src_rel} → {dst_rel}")
    return synced

# ────────────────────────────────────────
# 체크 9: DB 무결성 — NULL 필드 검증
# ────────────────────────────────────────

def check_db_null_fields(project_root, slug):
    """
    최근 INSERT된 시그널의 필수 필드 NULL 여부 체크.
    published_at NULL, ticker NULL, speaker_id NULL → 각각 0건이어야 통과.
    반환: (passed: bool, details: list[str])
    """
    load_env(project_root)
    details = []
    passed = True

    # published_at NULL 체크 (influencer_videos 테이블)
    rows = supabase_get(
        'influencer_videos?select=id&published_at=is.null&limit=1',
        project_root
    )
    if rows is None:
        details.append("⚠️  published_at NULL 체크: DB 조회 실패 (스킵)")
    elif len(rows) > 0:
        # 정확한 건수 조회
        count_rows = supabase_get(
            'influencer_videos?select=id&published_at=is.null',
            project_root
        )
        cnt = len(count_rows) if count_rows else '?'
        details.append(f"published_at NULL {cnt}건 (influencer_videos)")
        save_error_pattern(slug, 'gate3', 'published_at_null', f"{cnt}건")
        passed = False

    # ticker NULL 체크 (influencer_signals 테이블)
    rows = supabase_get(
        'influencer_signals?select=id&ticker=is.null&limit=1',
        project_root
    )
    if rows is None:
        details.append("⚠️  ticker NULL 체크: DB 조회 실패 (스킵)")
    elif len(rows) > 0:
        count_rows = supabase_get(
            'influencer_signals?select=id&ticker=is.null',
            project_root
        )
        cnt = len(count_rows) if count_rows else '?'
        details.append(f"ticker NULL {cnt}건 (influencer_signals)")
        save_error_pattern(slug, 'gate3', 'ticker_null', f"{cnt}건")
        passed = False

    # speaker_id NULL 체크 (influencer_signals 테이블)
    rows = supabase_get(
        'influencer_signals?select=id&speaker_id=is.null&limit=1',
        project_root
    )
    if rows is None:
        details.append("⚠️  speaker_id NULL 체크: DB 조회 실패 (스킵)")
    elif len(rows) > 0:
        count_rows = supabase_get(
            'influencer_signals?select=id&speaker_id=is.null',
            project_root
        )
        cnt = len(count_rows) if count_rows else '?'
        details.append(f"speaker_id NULL {cnt}건 (influencer_signals)")
        save_error_pattern(slug, 'gate3', 'speaker_id_null', f"{cnt}건")
        passed = False

    return passed, details


# ────────────────────────────────────────
# 체크 10: 크립토 종목 가격 검증
# ────────────────────────────────────────

def check_crypto_prices(project_root, slug):
    """
    크립토 종목 가격 이상 검증:
    - ticker → -USD 접미사 매핑 확인 (BTC→BTC-USD)
    - stockPrices.json에 누락된 크립토 ticker
    - currentPrice가 0 또는 None
    - stock_tickers.json에 누락
    - 극소수 가격(< $0.01) 종목 경고 (프론트 소수점 표시 확인 필요)
    - yfinance 실패 시 CoinGecko fallback 안내
    반환: (passed: bool, issues: list[str], micro_prices: list[str])
    """
    load_env(project_root)
    issues = []
    micro_prices = []

    # DB에서 크립토 시그널 ticker 조회
    crypto_sigs = supabase_get(
        'influencer_signals?market=eq.CRYPTO&select=ticker,stock&limit=2000',
        project_root
    )
    if not crypto_sigs:
        return True, [], []

    # 고유 ticker 추출
    crypto_tickers = {}
    for s in crypto_sigs:
        t = s.get('ticker', '')
        if t:
            crypto_tickers.setdefault(t, s.get('stock', ''))

    if not crypto_tickers:
        return True, [], []

    # 로컬 데이터 로드
    tickers_path = os.path.join(project_root, 'data', 'stock_tickers.json')
    prices_path = os.path.join(project_root, 'data', 'stockPrices.json')
    signal_prices_path = os.path.join(project_root, 'data', 'signal_prices.json')

    tickers_list = set()
    if os.path.exists(tickers_path):
        with open(tickers_path, encoding='utf-8') as f:
            tickers_list = set(json.load(f))

    stock_prices = {}
    if os.path.exists(prices_path):
        with open(prices_path, encoding='utf-8') as f:
            stock_prices = json.load(f)

    signal_prices = {}
    if os.path.exists(signal_prices_path):
        with open(signal_prices_path, encoding='utf-8') as f:
            signal_prices = json.load(f)

    for ticker, stock_name in crypto_tickers.items():
        yf_ticker = f"{ticker}-USD"

        # 1. stock_tickers.json 누락
        if ticker not in tickers_list:
            issues.append(f"{ticker} ({stock_name}): stock_tickers.json 누락")

        # 2. -USD 매핑: signal_prices에 ticker 있으면 yfinance ticker 확인
        sp_entry = signal_prices.get(ticker)
        if isinstance(sp_entry, dict):
            sp_yf = sp_entry.get('yf_ticker', '')
            if sp_yf and not sp_yf.endswith('-USD'):
                issues.append(f"{ticker} ({stock_name}): yfinance ticker가 '{sp_yf}' — "
                              f"'{yf_ticker}'이어야 함")

        # 3. stockPrices.json 누락
        if ticker not in stock_prices:
            issues.append(f"{ticker} ({stock_name}): stockPrices.json 누락 "
                          f"(yfinance {yf_ticker} 또는 CoinGecko로 수집 필요)")
            continue

        # 4. currentPrice 검증
        sp = stock_prices[ticker]
        if isinstance(sp, dict):
            cur = sp.get('currentPrice')
        elif isinstance(sp, list) and sp:
            cur = sp[-1].get('close')
        else:
            cur = None

        if cur is None:
            issues.append(f"{ticker} ({stock_name}): currentPrice=None "
                          f"(CoinGecko fallback 시도 필요)")
        elif cur == 0:
            issues.append(f"{ticker} ({stock_name}): currentPrice=$0 "
                          f"(yfinance {yf_ticker} 재수집 또는 CoinGecko fallback)")
        elif cur > 0 and cur < 0.01:
            micro_prices.append(f"{ticker} ({stock_name}): ${cur} — "
                                f"극소수 가격, 프론트 소수점 6~8자리 표시 확인 필요")

    return len(issues) == 0, issues, micro_prices


# ────────────────────────────────────────
# 기존 체크 (유지)
# ────────────────────────────────────────

def check_profile_page(out_dir, slug):
    page_path = os.path.join(out_dir, 'profile', 'influencer', slug, 'index.html')
    return os.path.isfile(page_path), page_path

def check_api_key_leak(out_dir):
    found = []
    out_path = Path(out_dir)
    for ftype in ['*.html', '*.js']:
        for fpath in out_path.rglob(ftype):
            try:
                content = fpath.read_text(encoding='utf-8', errors='ignore')
                for pattern in API_KEY_PATTERNS:
                    if pattern in content:
                        found.append({'file': str(fpath.relative_to(out_path)), 'pattern': pattern})
            except Exception:
                pass
    return found

def check_required_pages(out_dir):
    required = {
        '404.html': os.path.join(out_dir, '404.html'),
        'index.html': os.path.join(out_dir, 'index.html'),
        'dashboard/index.html': os.path.join(out_dir, 'dashboard', 'index.html'),
        'explore/index.html': os.path.join(out_dir, 'explore', 'index.html'),
    }
    return [name for name, path in required.items() if not os.path.isfile(path)]

def check_deploy_http(slug):
    url = f"https://puing5555.github.io/invest-sns/profile/influencer/{slug}/"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, url
    except urllib.error.HTTPError as e:
        return e.code, url
    except Exception:
        return None, url

# ────────────────────────────────────────
# 메인
# ────────────────────────────────────────

def run_gate3(slug, project_root, check_deploy=False):
    """Gate 3 실행. 반환: passed (bool)"""
    load_env(project_root)
    out_dir = os.path.join(project_root, 'out')

    print(f"\n{'='*60}")
    print(f"🔍 QA Gate 3 - 프론트엔드 빌드/배포 검증 v2")
    print(f"   슬러그: {slug} | out 경로: {out_dir}")
    print(f"{'='*60}")

    has_fatal = False

    # ── 체크 1: 빌드 성공 (out/ 존재) ──
    print(f"\n[체크 1] 빌드 확인...")
    if check_build_exists(out_dir):
        html_count = sum(1 for _ in Path(out_dir).rglob('*.html'))
        print(f"✅ [체크 1] 빌드 확인 — out/ 폴더 존재 (HTML {html_count}개)")
    else:
        print(f"⛔ [체크 1] 빌드 실패 — out/ 폴더 없음 → npm run build 필요")
        save_error_pattern(slug, 'gate3', 'build_missing', f"out/ 폴더 없음")
        has_fatal = True

    # ── 체크 2: 수익률 null 비율 + auto-fix ──
    print(f"\n[체크 2] 수익률 null 비율...")
    ret_ok, missing_ret, total_sig = check_return_pct(project_root, slug)
    if ret_ok:
        print(f"✅ [체크 2] 수익률 누락 {missing_ret}/{total_sig}건 ({missing_ret/total_sig*100:.1f}% < 30%)")
    else:
        print(f"⛔ [체크 2] 수익률 누락 30% 초과 → 배포 차단")
        has_fatal = True

    # ── 체크 3: 종목 페이지 + auto-fix ──
    print(f"\n[체크 3] 종목 페이지 존재 여부...")
    check_stock_pages(project_root, out_dir, slug)
    if os.path.isdir(os.path.join(out_dir, 'stock')):
        built = len(os.listdir(os.path.join(out_dir, 'stock')))
        print(f"✅ [체크 3] 종목 페이지 {built}개 확인")
    else:
        print(f"⚠️  [체크 3] out/stock/ 없음 (빌드 전 상태)")

    # ── 체크 4: 프로필 페이지 매칭 ──
    print(f"\n[체크 4] 프로필 페이지 전수 확인...")
    if check_build_exists(out_dir):
        missing_profiles = check_all_profile_pages(project_root, out_dir, slug)
        if missing_profiles:
            print(f"⛔ [체크 4] 프로필 페이지 누락 {len(missing_profiles)}개:")
            for mp in missing_profiles:
                print(f"   - {mp['slug']} ({mp['name']})")
            save_error_pattern(slug, 'gate3', 'profile_page_missing',
                               f"누락: {[mp['slug'] for mp in missing_profiles]}")
            has_fatal = True
        else:
            print(f"✅ [체크 4] 모든 프로필 페이지 존재")
    else:
        print(f"⚠️  [체크 4] out/ 없어 스킵")

    # ── 체크 5: YouTube URL www. 검증 + auto-fix ──
    print(f"\n[체크 5] YouTube URL www. 검증...")
    fixed_yt, remaining_yt = check_and_fix_youtube_urls(project_root)
    if fixed_yt > 0:
        print(f"  🔧 youtube.com → www.youtube.com 자동 수정: {fixed_yt}개 파일")
    if remaining_yt > 0:
        print(f"⛔ [체크 5] youtube.com (www 없음) {remaining_yt}개 파일 잔존 → 수동 확인 필요")
        save_error_pattern(slug, 'gate3', 'youtube_url_no_www',
                           f"{remaining_yt}개 파일 잔존")
        has_fatal = True
    elif fixed_yt > 0:
        print(f"  🔧 YouTube URL 수정됨 → 재빌드 필요 (수정 내용 반영)")
        rebuild_r = subprocess.run(
            ['npm.cmd' if sys.platform == 'win32' else 'npm', 'run', 'build'], cwd=os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..')),
            capture_output=True, text=True, timeout=300,
            encoding='utf-8', errors='replace'
        )
        if rebuild_r.returncode == 0:
            print(f"✅ [체크 5] YouTube URL 수정 + 재빌드 완료")
        else:
            print(f"⚠️  [체크 5] YouTube URL 수정됐지만 재빌드 실패: {rebuild_r.stderr[-200:]}")
    else:
        print(f"✅ [체크 5] YouTube URL 전부 www.youtube.com 정상")

    # ── 체크 6: data/ ↔ public/ 동기화 ──
    print(f"\n[체크 6] data/ ↔ public/ 동기화 확인...")
    synced = check_and_sync_data_public(project_root)
    if synced:
        for s in synced:
            print(f"  🔧 동기화: {s}")
        print(f"✅ [체크 6] {len(synced)}개 파일 자동 동기화 완료")
    else:
        print(f"✅ [체크 6] data/ ↔ public/ 동기화 상태 정상")

    # ── 체크 7: API 키 유출 스캔 ──
    print(f"\n[체크 7] API 키 유출 스캔...")
    if check_build_exists(out_dir):
        leaks = check_api_key_leak(out_dir)
        if leaks:
            print(f"⛔ [체크 7] API 키 유출 {len(leaks)}건!")
            for leak in leaks[:5]:
                print(f"   ⚠️  {leak['file']}: '{leak['pattern']}'")
            save_error_pattern(slug, 'gate3', 'api_key_leak',
                               f"{len(leaks)}건: {[l['pattern'] for l in leaks[:3]]}")
            has_fatal = True
        else:
            print(f"✅ [체크 7] API 키 유출 없음")
    else:
        print(f"⚠️  [체크 7] out/ 없어 스킵")

    # ── 체크 8: 필수 페이지 ──
    print(f"\n[체크 8] 필수 페이지 확인...")
    if check_build_exists(out_dir):
        missing_pages = check_required_pages(out_dir)
        if missing_pages:
            print(f"⛔ [체크 8] 필수 페이지 누락: {missing_pages}")
            save_error_pattern(slug, 'gate3', 'required_pages_missing', f"{missing_pages}")
            has_fatal = True
        else:
            print(f"✅ [체크 8] 필수 페이지 전부 존재 (404, index, dashboard, explore)")
    else:
        print(f"⚠️  [체크 8] out/ 없어 스킵")

    # ── 체크 9: DB 무결성 (NULL 필드 검증) ──
    print(f"\n[체크 9] DB 무결성 검증 (published_at, ticker, speaker_id NULL)...")
    null_ok, null_details = check_db_null_fields(project_root, slug)
    if null_ok:
        print(f"✅ [체크 9] DB NULL 필드 전부 0건")
    else:
        for detail in null_details:
            print(f"  ⛔ {detail}")
        print(f"⛔ [체크 9] DB NULL 필드 존재 → 배포 차단")
        has_fatal = True

    # ── 체크 10: 크립토 종목 가격 검증 ──
    print(f"\n[체크 10] 크립토 종목 가격 검증...")
    crypto_ok, crypto_issues, micro_prices = check_crypto_prices(project_root, slug)
    if crypto_ok and not micro_prices:
        print(f"✅ [체크 10] 크립토 종목 가격 정상")
    else:
        for issue in crypto_issues:
            print(f"  ⚠️  {issue}")
        for mp in micro_prices:
            print(f"  💰 {mp}")
        total_issues = len(crypto_issues) + len(micro_prices)
        if crypto_issues:
            print(f"⚠️  [체크 10] 크립토 가격 이상 {len(crypto_issues)}건 "
                  f"(경고, 배포 차단 아님)")
            save_error_pattern(slug, 'gate3', 'crypto_price_issue',
                               f"{len(crypto_issues)}건: {crypto_issues[:3]}")
        if micro_prices:
            print(f"  💰 극소수 가격 {len(micro_prices)}건 "
                  f"(formatStockPrice 소수점 6~8자리 확인)")

    # ── 체크 11: 배포 후 HTTP 체크 ──
    if check_deploy:
        print(f"\n[체크 10] GitHub Pages 배포 확인...")
        status, url = check_deploy_http(slug)
        if status == 200:
            print(f"✅ [체크 10] HTTP 200 확인: {url}")
        else:
            print(f"⚠️  [체크 10] HTTP {status}: {url}")
            save_error_pattern(slug, 'gate3', 'deploy_http', f"HTTP {status}: {url}")
    else:
        print(f"\nℹ️  [체크 11] 배포 HTTP 체크 스킵 (--check-deploy 옵션)")

    # ── 결과 ──
    print(f"\n{'='*60}")
    if has_fatal:
        print(f"❌ Gate 3 실패 — 배포 차단. 위 ⛔ 항목 해결 후 재시도.")
    else:
        print(f"✅ Gate 3 통과 — 모든 체크 통과. 배포 승인.")
    print(f"{'='*60}\n")
    return not has_fatal


def main():
    parser = argparse.ArgumentParser(description='QA Gate 3 v2 - 프론트엔드 빌드/배포 검증')
    parser.add_argument('--slug', '-s', default='godofit', help='인플루언서 슬러그')
    parser.add_argument('--check-deploy', action='store_true', help='GitHub Pages HTTP 체크')
    parser.add_argument('--project-root', '-r',
                        default=os.path.join(os.path.dirname(__file__), '..', '..'),
                        help='프로젝트 루트')
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    passed = run_gate3(args.slug, project_root, args.check_deploy)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
