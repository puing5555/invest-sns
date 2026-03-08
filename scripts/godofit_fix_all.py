"""
GODofIT 데이터 수정 스크립트
이슈 1: 35개 YouTube 영상 published_at 수집 + DB UPDATE
이슈 4: 136개 시그널 수익률 계산 + signal_prices.json 업데이트
"""

import json, os, subprocess, time, requests, shutil
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.local"
PRICES_FILE = BASE_DIR / "data" / "signal_prices.json"
PUBLIC_PRICES_FILE = BASE_DIR / "public" / "signal_prices.json"

# Load env
env = {}
for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

SUPABASE_URL = env['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

YOUTUBE_IDS = [
    '_u3svqsOjjw', '2BAhDz7TSno', '3F6EwQdcv-8', '6z0BBGCHo8A', 'bentgHJY5vg',
    'btwqHB60U0M', 'ci6PyydMf_o', 'cNjBkWAbMQ4', 'DDA5NpaigGU', 'dkEmOGr9hU8',
    'DspQJVFUyOo', 'ENBTNEnFQoQ', 'F_qIwUinxGo', 'FpHGO-WgoZ8', 'fSpSXtGso1Q',
    'GeOn7MZTETs', 'GJEn-EI8LJQ', 'HHekwqIZ6Hw', 'ivixbgrNrK0', 'iWCy6dGSaYs',
    'k0U5vYhlp5o', 'K4eKFFJQWdM', 'lHQtsG8hZuM', 'mE90UrRQXJk', 'mf2P0Aw3odU',
    'NY9M0DH9vlA', 'oRw2DaFbEjU', 'pQmEyuC7v00', 'R7YD33ePWlI', 'rO4ZZnJMWL4',
    'SDwg2assS2g', 'Tiox3N0yqc0', 'UDYGrugu9tc', 'UpnqwTqYz-8', 'UsgmKUtiOFs'
]

# ============================================================
# STEP 1: yt-dlp로 업로드 날짜 수집 + Supabase DB UPDATE
# ============================================================

def get_upload_date(yt_id):
    """yt_dlp Python 라이브러리로 업로드 날짜 가져오기"""
    try:
        import yt_dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://youtube.com/watch?v={yt_id}', download=False)
            upload_date = info.get('upload_date')  # YYYYMMDD
            if upload_date:
                return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}T00:00:00+00:00"
        return None
    except Exception as e:
        print(f"  [ERR] yt_dlp {yt_id}: {e}")
        return None

def get_db_video_id(yt_id):
    """YouTube ID로 DB 내부 UUID 조회"""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.{yt_id}&select=id",
        headers=headers
    )
    data = r.json()
    if data and len(data) > 0:
        return data[0]['id']
    return None

def update_published_at(db_id, published_at):
    """DB에 published_at 업데이트"""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/influencer_videos?id=eq.{db_id}",
        headers=headers,
        json={'published_at': published_at}
    )
    return r.status_code in (200, 204)

print("=" * 60)
print("STEP 1: YouTube 영상 published_at 수집 + DB UPDATE")
print("=" * 60)

step1_results = {}  # yt_id -> {'db_id': ..., 'published_at': ..., 'status': ...}
success_count = 0
fail_count = 0

for i, yt_id in enumerate(YOUTUBE_IDS):
    print(f"\n[{i+1}/{len(YOUTUBE_IDS)}] {yt_id}")
    
    # DB UUID 조회
    db_id = get_db_video_id(yt_id)
    if not db_id:
        print(f"  [SKIP] DB에서 video_id 못 찾음")
        step1_results[yt_id] = {'db_id': None, 'published_at': None, 'status': 'not_found'}
        fail_count += 1
        time.sleep(1)
        continue
    
    # yt-dlp로 날짜 수집
    published_at = get_upload_date(yt_id)
    if not published_at:
        print(f"  [SKIP] 날짜 수집 실패")
        step1_results[yt_id] = {'db_id': db_id, 'published_at': None, 'status': 'date_fail'}
        fail_count += 1
        time.sleep(2)
        continue
    
    # DB 업데이트
    ok = update_published_at(db_id, published_at)
    if ok:
        print(f"  [OK] {published_at}")
        step1_results[yt_id] = {'db_id': db_id, 'published_at': published_at, 'status': 'updated'}
        success_count += 1
    else:
        print(f"  [ERR] DB 업데이트 실패")
        step1_results[yt_id] = {'db_id': db_id, 'published_at': published_at, 'status': 'update_fail'}
        fail_count += 1
    
    time.sleep(2)  # 레이트리밋 방지

print(f"\n[STEP1 결과] 성공: {success_count}, 실패: {fail_count}")

# ============================================================
# STEP 2: Godofit 시그널 136개 수익률 계산
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: Godofit 시그널 수익률 계산 + signal_prices.json 업데이트")
print("=" * 60)

# 2-1. Godofit 시그널 전체 조회 (published_at 포함)
print("\n[2-1] Godofit 시그널 수집 중...")

# DB에서 updated된 published_at을 반영하기 위해 시간 약간 대기
time.sleep(3)

all_signals = []
offset = 0
while True:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/influencer_signals"
        f"?select=id,ticker,stock,video_id"
        f"&offset={offset}&limit=500",
        headers=headers
    )
    batch = r.json()
    if not batch:
        break
    all_signals.extend(batch)
    if len(batch) < 500:
        break
    offset += 500

# 채널 영상 목록으로 필터링
channel_videos = requests.get(
    f"{SUPABASE_URL}/rest/v1/influencer_videos"
    f"?channel_id=eq.{CHANNEL_ID}&select=id,published_at&limit=500",
    headers=headers
).json()

video_map = {v['id']: v['published_at'] for v in channel_videos}
channel_video_ids = set(video_map.keys())

godofit_signals = [s for s in all_signals if s.get('video_id') in channel_video_ids]
print(f"  Godofit 시그널: {len(godofit_signals)}개 (전체 {len(all_signals)}개)")

# 2-2. signal_date 매핑 (published_at 우선, 없으면 스킵)
SKIP_TICKERS = {'BTC', 'ETH', 'SOL', 'DOGE', 'KLAY', 'KS11', 'SOXX', 'XLU', 'GLD'}

signal_info = {}
for s in godofit_signals:
    if not s.get('ticker') or s['ticker'] in SKIP_TICKERS:
        continue
    vid_id = s.get('video_id')
    pub = video_map.get(vid_id) if vid_id else None
    if not pub:
        continue
    date_str = pub[:10]
    signal_info[s['id']] = {
        'ticker': s['ticker'],
        'date': date_str,
        'stock': s.get('stock', '')
    }

print(f"  날짜 있는 시그널: {len(signal_info)}개")

if not signal_info:
    print("  [WARN] 처리할 시그널 없음 - published_at 업데이트가 필요합니다")
    print("\n[DONE] 작업 완료")
    exit(0)

# 2-3. yfinance로 가격 데이터 다운로드
try:
    import yfinance as yf
except ImportError:
    print("[ERR] yfinance 설치 필요: pip install yfinance")
    exit(1)

def to_yf(t):
    if '.' in t: return t
    if t.isdigit(): return f"{t}.KS"
    return t

unique_tickers = set(v['ticker'] for v in signal_info.values())
yf_map = {t: to_yf(t) for t in unique_tickers}
all_yf = list(set(yf_map.values()))

all_dates = [v['date'] for v in signal_info.values()]
min_date = min(all_dates)
max_date = max(all_dates)
start = (datetime.strptime(min_date, '%Y-%m-%d') - timedelta(days=10)).strftime('%Y-%m-%d')
end = (datetime.strptime(max_date, '%Y-%m-%d') + timedelta(days=2)).strftime('%Y-%m-%d')

print(f"\n[2-3] yfinance 가격 다운로드")
print(f"  티커: {len(unique_tickers)}개, 기간: {start} ~ {end}")

all_hist = {}
chunk_size = 30
for i in range(0, len(all_yf), chunk_size):
    chunk = all_yf[i:i+chunk_size]
    print(f"  청크 {i//chunk_size+1}/{(len(all_yf)+chunk_size-1)//chunk_size} ({len(chunk)}개)...", flush=True)
    try:
        data = yf.download(chunk, start=start, end=end, group_by='ticker', timeout=30, progress=False)
        if len(chunk) == 1:
            all_hist[chunk[0]] = data
        else:
            for sym in chunk:
                try:
                    if sym in data.columns.get_level_values(0):
                        df = data[sym]
                        if not df.empty:
                            all_hist[sym] = df
                except:
                    pass
    except Exception as e:
        print(f"  [ERR] 청크 실패: {e}")

# KOSDAQ 재시도
missing_ks = [yf_map[t] for t in unique_tickers if yf_map[t].endswith('.KS') and yf_map[t] not in all_hist]
if missing_ks:
    kq_tickers = [t.replace('.KS', '.KQ') for t in missing_ks]
    print(f"  KOSDAQ 재시도: {len(kq_tickers)}개")
    for i in range(0, len(kq_tickers), chunk_size):
        chunk = kq_tickers[i:i+chunk_size]
        try:
            data = yf.download(chunk, start=start, end=end, group_by='ticker', timeout=30, progress=False)
            if len(chunk) == 1:
                ks = chunk[0].replace('.KQ', '.KS')
                if not data.empty:
                    all_hist[ks] = data
            else:
                for sym in chunk:
                    try:
                        df = data[sym]
                        if df is not None and not df.empty:
                            all_hist[sym.replace('.KQ', '.KS')] = df
                    except:
                        pass
        except:
            pass

print(f"  히스토리 획득: {len(all_hist)}개 티커")

def get_close(hist_df, date_str):
    """날짜 기준 종가 조회 (당일 없으면 가장 가까운 이전 날)"""
    try:
        target = datetime.strptime(date_str, '%Y-%m-%d')
        idx = hist_df.index.tz_localize(None) if hist_df.index.tz else hist_df.index
        hist_df = hist_df.copy()
        hist_df.index = idx
        valid = hist_df[hist_df.index <= target]
        if valid.empty:
            valid = hist_df.head(1)
        if valid.empty:
            return None
        col = 'Close' if 'Close' in valid.columns else valid.columns[3]
        val = float(valid[col].iloc[-1])
        return val if val > 0 else None
    except:
        return None

# 2-4. 현재 signal_prices.json 로드
existing = json.loads(PRICES_FILE.read_text(encoding='utf-8'))

# 2-5. 수익률 계산 + signal_prices.json 업데이트
print("\n[2-5] 수익률 계산 중...")
result = dict(existing)
calc_success = 0
calc_skip = 0
no_hist = []
no_current = []

for sid, info in signal_info.items():
    ticker = info['ticker']
    date_str = info['date']
    yft = yf_map.get(ticker, to_yf(ticker))
    
    hist_df = all_hist.get(yft)
    current_price = existing.get(ticker, {}).get('current_price')
    
    if hist_df is None:
        no_hist.append(ticker)
        calc_skip += 1
        continue
    
    if not current_price:
        no_current.append(ticker)
        calc_skip += 1
        continue
    
    price_at = get_close(hist_df, date_str)
    if not price_at:
        calc_skip += 1
        continue
    
    ret = round((current_price - price_at) / price_at * 100, 2)
    result[sid] = {
        'price_at_signal': round(price_at, 2),
        'price_current': current_price,
        'return_pct': ret,
        'signal_date': date_str,
        'ticker': ticker
    }
    calc_success += 1

# 2-6. 파일 저장
PRICES_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
shutil.copy(PRICES_FILE, PUBLIC_PRICES_FILE)

print(f"  data/signal_prices.json 업데이트 완료 ({len(result)}개 엔트리)")
print(f"  public/signal_prices.json 동기화 완료")

# ============================================================
# 최종 결과 요약
# ============================================================

print("\n" + "=" * 60)
print("최종 결과 요약")
print("=" * 60)
print(f"\n[이슈 1] YouTube published_at 업데이트")
print(f"  성공: {success_count}개")
print(f"  실패: {fail_count}개")

updated_list = [(k, v['published_at']) for k, v in step1_results.items() if v['status'] == 'updated']
if updated_list:
    print(f"  업데이트된 영상:")
    for yt_id, dt in updated_list[:10]:
        print(f"    {yt_id}: {dt[:10]}")
    if len(updated_list) > 10:
        print(f"    ... 외 {len(updated_list)-10}개")

fail_list = [(k, v['status']) for k, v in step1_results.items() if v['status'] != 'updated']
if fail_list:
    print(f"  실패/스킵:")
    for yt_id, status in fail_list:
        print(f"    {yt_id}: {status}")

print(f"\n[이슈 4] 시그널 수익률 계산")
print(f"  Godofit 시그널: {len(godofit_signals)}개")
print(f"  날짜 있는 시그널: {len(signal_info)}개")
print(f"  수익률 계산 성공: {calc_success}개")
print(f"  스킵: {calc_skip}개")
if no_hist:
    unique_no_hist = list(set(no_hist))
    print(f"  히스토리 없는 티커: {unique_no_hist[:20]}")
if no_current:
    unique_no_current = list(set(no_current))
    print(f"  현재가 없는 티커: {unique_no_current[:20]}")

print("\n[DONE] 모든 작업 완료")
