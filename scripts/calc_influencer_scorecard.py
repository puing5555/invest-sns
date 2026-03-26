"""
인플루언서 스코어카드 집계 스크립트 v3
- 적중률: 매수+긍정+매도만 (부정/중립 제외)
- 수익률: 1Y return (stockPrices.json) + Current return, 원본 그대로 (direction-adjusted 제거)
- dedup: 월 1건 (speaker+ticker+YYYY-MM)
- 10건 미만: "시그널 수집 중"
"""
import json, sys, requests
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from statistics import median

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.local"
SLUGS_FILE = BASE_DIR / "data" / "speaker_slugs.json"
STOCK_PRICES_FILE = BASE_DIR / "data" / "stockPrices.json"
OUTPUT_FILE = BASE_DIR / "data" / "influencer_scorecard.json"
PUBLIC_FILE = BASE_DIR / "public" / "influencer_scorecard.json"

MIN_HIT_ELIGIBLE = 10  # 적중률 산출 최소 기준
EVAL_GRACE_DAYS = 90  # 1Y 없을 때 current로 판정하는 최소 경과일 (3개월)

# 적중률 대상: 매수+긍정+매도 (부정/중립 제외)
BUY_SIGNALS = {'매수', '긍정', 'STRONG_BUY', 'BUY', 'POSITIVE'}
SELL_SIGNALS = {'매도', 'SELL', 'STRONG_SELL'}
HIT_SIGNALS = BUY_SIGNALS | SELL_SIGNALS
NEUTRAL_SIGNALS = {'중립', 'NEUTRAL', 'HOLD'}
EXCLUDE_SIGNALS = {'부정', 'CONCERN', 'NEGATIVE'}  # 적중률 미산입, 리스트에는 표시

# --- Supabase setup ---
env = {}
for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

SUPABASE_URL = env['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY', '')
headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}


def fetch_all(table, select, page_size=1000):
    """Supabase REST에서 전체 데이터 fetch (pagination)"""
    all_data = []
    offset = 0
    while True:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select={select}&limit={page_size}&offset={offset}"
        resp = requests.get(url, headers={**headers, 'Prefer': 'count=exact'})
        data = resp.json()
        if not data:
            break
        all_data.extend(data)
        if len(data) < page_size:
            break
        offset += page_size
    return all_data


def find_closest_price(prices, date_str, max_days=30):
    """date_str 기준 ±max_days 내 가장 가까운 종가. prices는 [{date, close}] 정렬됨."""
    target = datetime.strptime(date_str, '%Y-%m-%d')
    best = None
    best_diff = float('inf')
    for p in prices:
        try:
            d = datetime.strptime(p['date'], '%Y-%m-%d')
        except (ValueError, KeyError):
            continue
        diff = abs((d - target).days)
        if diff < best_diff and diff <= max_days:
            best = p['close']
            best_diff = diff
    return best


def calc_returns(ticker, signal_date_str, stock_prices):
    """1Y return + 3Y return + Current return 계산. stockPrices.json 기준."""
    # ticker 탐색: 그대로 → .KS 붙여서
    def get_prices(t):
        v = stock_prices.get(t)
        if v is None:
            return []
        if isinstance(v, list):
            return v  # 직접 [{date, close}] 배열
        if isinstance(v, dict):
            return v.get('prices', [])
        return []

    prices_data = get_prices(ticker)
    if not prices_data and ticker and not ticker.endswith('.KS'):
        prices_data = get_prices(ticker + '.KS')

    if not prices_data or not signal_date_str or len(signal_date_str) < 10:
        return None, None, None

    price_at = find_closest_price(prices_data, signal_date_str)
    if not price_at or price_at == 0:
        return None, None, None

    # Current return: 최신 종가
    price_latest = prices_data[-1]['close']
    return_current = round((price_latest - price_at) / price_at * 100, 2) if price_latest else None

    try:
        signal_date = datetime.strptime(signal_date_str, '%Y-%m-%d')
    except ValueError:
        return None, None, return_current

    # 1Y return: signal_date + 365일 후
    target_1y = signal_date + timedelta(days=365)
    if target_1y > datetime.now():
        return None, None, return_current
    price_1y = find_closest_price(prices_data, target_1y.strftime('%Y-%m-%d'))
    return_1y = round((price_1y - price_at) / price_at * 100, 2) if price_1y else None

    # 3Y return: signal_date + 1095일 후
    target_3y = signal_date + timedelta(days=1095)
    return_3y = None
    if target_3y <= datetime.now():
        price_3y = find_closest_price(prices_data, target_3y.strftime('%Y-%m-%d'))
        return_3y = round((price_3y - price_at) / price_at * 100, 2) if price_3y else None

    return return_1y, return_3y, return_current


def main():
    print("=== 인플루언서 스코어카드 v3 ===", flush=True)

    # 1. Fetch data
    print("1. Supabase에서 데이터 fetch...", flush=True)
    signals = fetch_all('influencer_signals',
                        'id,video_id,speaker_id,stock,ticker,market,signal,confidence')
    videos = fetch_all('influencer_videos', 'id,published_at')
    speakers = fetch_all('speakers', 'id,name')

    video_map = {v['id']: v.get('published_at') for v in videos}
    speaker_map = {s['id']: s['name'] for s in speakers}

    print(f"   시그널: {len(signals)}, 영상: {len(videos)}, 스피커: {len(speakers)}", flush=True)

    # 2. Load stockPrices.json
    print("2. stockPrices.json 로드...", flush=True)
    stock_prices = json.loads(STOCK_PRICES_FILE.read_text(encoding='utf-8'))
    print(f"   종목 수: {len(stock_prices)}", flush=True)

    # 3. Load speaker_slugs.json
    slugs_data = json.loads(SLUGS_FILE.read_text(encoding='utf-8'))
    name_to_slug = {v: k for k, v in slugs_data.items()}

    # 4. Group signals by speaker
    speaker_signals = defaultdict(list)
    now = datetime.now()
    thirty_days_ago = (now - timedelta(days=30)).strftime('%Y-%m-%d')

    for s in signals:
        sid = s.get('speaker_id', '')
        speaker_name = speaker_map.get(sid, sid)
        if not speaker_name:
            continue

        vid = s.get('video_id')
        published_at = video_map.get(vid, '') if vid else ''
        date_str = (published_at or '')[:10]

        speaker_signals[speaker_name].append({
            'id': s.get('id'),
            'stock': s.get('stock', ''),
            'ticker': s.get('ticker', ''),
            'market': s.get('market', 'OTHER'),
            'signal': s.get('signal', ''),
            'date': date_str,
            'confidence': s.get('confidence', ''),
        })

    print(f"   스피커 {len(speaker_signals)}명 집계 시작...", flush=True)

    # 5. Calculate per-speaker metrics
    scorecard = {}
    all_signals_returns = {}  # signal_id → {return_1y, return_3y, return_current}
    price_miss = 0
    price_hit = 0

    for speaker_name, sigs in speaker_signals.items():
        slug = name_to_slug.get(speaker_name)
        if not slug:
            for sl, nm in slugs_data.items():
                if nm == speaker_name:
                    slug = sl
                    break
        if not slug:
            slug = speaker_name.lower().replace(' ', '-')

        total = len(sigs)

        # --- 전체 시그널 수익률 계산 (dedup 전, 표시용) ---
        for s in sigs:
            sid = s.get('id')
            if not sid or sid in all_signals_returns:
                continue
            r1y, r3y, r_cur = calc_returns(s['ticker'], s['date'], stock_prices)
            all_signals_returns[sid] = {
                'return_1y': r1y,
                'return_current': r_cur,
            }

        # --- Dedup: 월 1건 (speaker+ticker+YYYY-MM) ---
        # 중립은 scored에서 제외, 나머지(매수/긍정/매도/부정)는 포함
        scorable = [s for s in sigs if s['signal'] not in NEUTRAL_SIGNALS and s['date']]
        scorable.sort(key=lambda s: s['date'])

        scored = []
        seen_monthly = set()
        for s in scorable:
            key = (s['ticker'] or s['stock']) + '_' + s['date'][:7]
            if key in seen_monthly:
                continue
            seen_monthly.add(key)
            scored.append(s)

        # --- 수익률 계산: stockPrices.json 기준 ---
        for s in scored:
            r1y, r3y, r_cur = calc_returns(s['ticker'], s['date'], stock_prices)
            s['return_1y'] = r1y
            s['return_3y'] = r3y
            s['return_current'] = r_cur
            if r1y is not None or r_cur is not None:
                price_hit += 1
            else:
                price_miss += 1

        scored_count = len(scored)

        # --- 적중률: 매수+긍정+매도만 (부정 제외) ---
        hit_eligible = [s for s in scored if s['signal'] in HIT_SIGNALS]
        hit_eligible_count = len(hit_eligible)

        wins = 0
        losses = 0
        pending = 0
        for s in hit_eligible:
            r1y = s['return_1y']
            rcur = s['return_current']
            sig_date = s.get('date', '')

            # 시그널 날짜로부터 경과 일수
            try:
                days_since = (now - datetime.strptime(sig_date, '%Y-%m-%d')).days
            except ValueError:
                days_since = 0

            # 하이브리드 판정: 1Y → 6개월+ current → pending
            if r1y is not None:
                ret = r1y
                s['return_basis'] = '1y'
            elif days_since >= EVAL_GRACE_DAYS and rcur is not None:
                ret = rcur
                s['return_basis'] = 'current'
            else:
                ret = None
                s['return_basis'] = 'pending'

            if ret is None:
                s['hit'] = None
                pending += 1
            elif s['signal'] in BUY_SIGNALS:
                s['hit'] = ret > 0
                if s['hit']:
                    wins += 1
                else:
                    losses += 1
            elif s['signal'] in SELL_SIGNALS:
                s['hit'] = ret < 0
                if s['hit']:
                    wins += 1
                else:
                    losses += 1

        # 부정 시그널은 hit = None, return_basis도 설정
        for s in scored:
            if s['signal'] not in HIT_SIGNALS:
                s['hit'] = None
                if 'return_basis' not in s:
                    if s.get('return_1y') is not None:
                        s['return_basis'] = '1y'
                    elif s.get('return_current') is not None:
                        s['return_basis'] = 'current'
                    else:
                        s['return_basis'] = 'pending'

        judged = wins + losses
        hit_rate = round(wins / judged * 100, 1) if judged >= MIN_HIT_ELIGIBLE else None

        # --- 수익률 통계 (1Y 기준, 매수+긍정+매도만) ---
        rets_1y = [s['return_1y'] for s in hit_eligible if s['return_1y'] is not None]
        rets_cur = [s['return_current'] for s in hit_eligible if s['return_current'] is not None]

        avg_return_1y = round(sum(rets_1y) / len(rets_1y), 2) if rets_1y else None
        median_return_1y = round(median(rets_1y), 2) if rets_1y else None
        avg_return_current = round(sum(rets_cur) / len(rets_cur), 2) if rets_cur else None
        median_return_current = round(median(rets_cur), 2) if rets_cur else None

        # --- Best/Worst call (current return 기준, 없으면 1Y) ---
        def sort_key(s):
            return s['return_current'] if s['return_current'] is not None else (s['return_1y'] if s['return_1y'] is not None else 0)

        best_call = None
        worst_call = None
        top3_calls = []
        worst3_calls = []
        scored_list = []

        calls_with_return = [s for s in hit_eligible if s['return_current'] is not None or s['return_1y'] is not None]

        if calls_with_return:
            sorted_best = sorted(calls_with_return, key=sort_key, reverse=True)

            def make_call(s):
                return {
                    'stock': s['stock'], 'ticker': s['ticker'],
                    'return_1y': s['return_1y'], 'return_current': s['return_current'],
                    'signal': s['signal'], 'date': s['date']
                }

            best_call = make_call(sorted_best[0])
            worst_call = make_call(sorted_best[-1])

            # TOP3/WORST3: 종목 중복 제거 (서로 다른 종목 3개)
            seen_top = set()
            top3_calls = []
            for s in sorted_best:
                key = s['ticker'] or s['stock']
                if key not in seen_top:
                    top3_calls.append(make_call(s))
                    seen_top.add(key)
                if len(top3_calls) >= 3:
                    break

            seen_worst = set()
            worst3_calls = []
            for s in reversed(sorted_best):
                key = s['ticker'] or s['stock']
                if key not in seen_worst:
                    worst3_calls.append(make_call(s))
                    seen_worst.add(key)
                if len(worst3_calls) >= 3:
                    break

        # scored_list: 전체 scored (부정 포함), 시간순
        scored_list = [{
            'id': s['id'], 'date': s['date'], 'stock': s['stock'],
            'ticker': s['ticker'], 'signal': s['signal'],
            'return_1y': s['return_1y'], 'return_3y': s.get('return_3y'),
            'return_current': s['return_current'],
            'return_basis': s.get('return_basis', 'pending'),
            'hit': s.get('hit'),
        } for s in sorted(scored, key=lambda x: x['date'])]

        # --- Homerun rate (1Y >= 100%, 매수+긍정+매도만) ---
        homerun_count = sum(1 for s in hit_eligible if s['return_1y'] is not None and s['return_1y'] >= 100)
        homerun_denom = sum(1 for s in hit_eligible if s['return_1y'] is not None)
        homerun_rate = round(homerun_count / homerun_denom * 100, 1) if homerun_denom > 0 else 0

        # --- Expected return (1Y 기준) ---
        win_rets_1y = [s['return_1y'] for s in hit_eligible if s.get('hit') is True and s['return_1y'] is not None]
        loss_rets_1y = [abs(s['return_1y']) for s in hit_eligible if s.get('hit') is False and s['return_1y'] is not None]
        avg_win = sum(win_rets_1y) / len(win_rets_1y) if win_rets_1y else 0
        avg_loss = sum(loss_rets_1y) / len(loss_rets_1y) if loss_rets_1y else 0
        hr_ratio = (hit_rate or 0) / 100
        expected_return = round(hr_ratio * avg_win - (1 - hr_ratio) * avg_loss, 2) if judged >= MIN_HIT_ELIGIBLE else None

        # --- Style tag ---
        if judged < MIN_HIT_ELIGIBLE:
            style_tag = '📊시그널 수집 중'
        elif (hit_rate or 0) >= 55 and homerun_rate >= 15:
            style_tag = '⭐올라운더'
        elif (hit_rate or 0) >= 60 and homerun_rate < 15:
            style_tag = '🎯스나이퍼'
        elif (hit_rate or 0) < 55 and homerun_rate >= 20:
            style_tag = '💣홈런히터'
        else:
            style_tag = '📊일반'

        # --- Market breakdown (매수+긍정+매도만) ---
        market_result = {}
        mkt_stats = defaultdict(lambda: {'count': 0, 'hits': 0, 'returns_1y': []})
        for s in hit_eligible:
            m = s.get('market', 'OTHER') or 'OTHER'
            mkt_stats[m]['count'] += 1
            if s.get('hit') is True:
                mkt_stats[m]['hits'] += 1
            if s['return_1y'] is not None:
                mkt_stats[m]['returns_1y'].append(s['return_1y'])
        for mkt, stats in mkt_stats.items():
            cnt = stats['count']
            market_result[mkt] = {
                'count': cnt,
                'hit_rate': round(stats['hits'] / cnt * 100, 1) if cnt >= 2 else None,
                'avg_return_1y': round(sum(stats['returns_1y']) / len(stats['returns_1y']), 2) if stats['returns_1y'] else None
            }

        # --- Recent 30d ---
        recent_eligible = [s for s in hit_eligible if s['date'] >= thirty_days_ago]
        recent_hits = sum(1 for s in recent_eligible if s.get('hit') is True)
        recent_count = len(recent_eligible)
        recent_hit_rate = round(recent_hits / recent_count * 100, 1) if recent_count >= 2 else None
        trend_delta = round(recent_hit_rate - hit_rate, 1) if (recent_hit_rate is not None and hit_rate is not None) else None

        # --- 구간별 성과 (tiers) ---
        def calc_tier_simple(slist, ret_key, min_days):
            items = []
            for s in slist:
                if s['signal'] not in HIT_SIGNALS:
                    continue
                try:
                    days = (now - datetime.strptime(s['date'], '%Y-%m-%d')).days
                except ValueError:
                    continue
                if days < min_days:
                    continue
                ret = s.get(ret_key)
                if ret is None and days >= EVAL_GRACE_DAYS:
                    ret = s.get('return_current')
                if ret is None:
                    continue
                items.append((s, ret))
            if not items:
                return None
            w = sum(1 for s, r in items if (s['signal'] in BUY_SIGNALS and r > 0) or (s['signal'] in SELL_SIGNALS and r < 0))
            l = len(items) - w
            rets = [r for _, r in items]
            return {
                'count': len(items), 'wins': w, 'losses': l,
                'hit_rate': round(w / len(items) * 100, 1) if len(items) >= 5 else None,
                'avg_return': round(sum(rets) / len(rets), 2),
                'median_return': round(median(rets), 2) if rets else None,
            }

        def calc_mid_tier(slist):
            items = []
            for s in slist:
                if s['signal'] not in HIT_SIGNALS:
                    continue
                try:
                    days = (now - datetime.strptime(s['date'], '%Y-%m-%d')).days
                except ValueError:
                    continue
                if days < 365:
                    continue
                if days >= 1095 and s.get('return_3y') is not None:
                    ret = s['return_3y']
                elif s.get('return_current') is not None:
                    ret = s['return_current']
                else:
                    continue
                items.append((s, ret))
            if not items:
                return None
            w = sum(1 for s, r in items if (s['signal'] in BUY_SIGNALS and r > 0) or (s['signal'] in SELL_SIGNALS and r < 0))
            l = len(items) - w
            rets = [r for _, r in items]
            return {
                'count': len(items), 'wins': w, 'losses': l,
                'hit_rate': round(w / len(items) * 100, 1) if len(items) >= 5 else None,
                'avg_return': round(sum(rets) / len(rets), 2),
                'median_return': round(median(rets), 2) if rets else None,
            }

        tiers = {
            'swing': calc_tier_simple(scored, 'return_1y', 90),
            'mid': calc_mid_tier(scored),
            'long': calc_tier_simple(scored, 'return_current', 1095),
        }

        # --- Signal type distribution (전체) ---
        type_counts = defaultdict(int)
        for s in sigs:
            type_counts[s['signal']] += 1

        scorecard[slug] = {
            'name': speaker_name,
            'slug': slug,
            'total_signals': total,
            'scored_signals': scored_count,
            'hit_eligible': hit_eligible_count,
            'hit_rate': hit_rate,
            'wins': wins,
            'losses': losses,
            'pending': pending,
            'avg_return_1y': avg_return_1y,
            'avg_return_current': avg_return_current,
            'median_return_1y': median_return_1y,
            'median_return_current': median_return_current,
            'best_call': best_call,
            'worst_call': worst_call,
            'top3_calls': top3_calls,
            'worst3_calls': worst3_calls,
            'homerun_rate': homerun_rate,
            'expected_return': expected_return,
            'style_tag': style_tag,
            'scored_list': scored_list,
            'market': market_result,
            'tiers': tiers,
            'signal_types': dict(type_counts),
            'recent_30d': {
                'count': recent_count,
                'hit_rate': recent_hit_rate,
                'delta': trend_delta
            }
        }

    # 6. Build rankings
    qualified = [(slug, data) for slug, data in scorecard.items()
                 if data['hit_rate'] is not None]

    by_accuracy = sorted(qualified, key=lambda x: x[1]['hit_rate'], reverse=True)
    by_return = sorted(qualified, key=lambda x: x[1]['avg_return_1y'] or 0, reverse=True)
    by_count = sorted(scorecard.items(), key=lambda x: x[1]['total_signals'], reverse=True)

    result = {
        'generated_at': datetime.now().isoformat(),
        'min_hit_eligible': MIN_HIT_ELIGIBLE,
        'total_speakers': len(scorecard),
        'qualified_speakers': len(qualified),
        'speakers': scorecard,
        'all_signals_returns': all_signals_returns,
        'rankings': {
            'by_accuracy': [s[0] for s in by_accuracy],
            'by_return': [s[0] for s in by_return],
            'by_count': [s[0] for s in by_count]
        }
    }

    # 7. Write output
    out_json = json.dumps(result, ensure_ascii=False, indent=2)
    OUTPUT_FILE.write_text(out_json, encoding='utf-8')
    PUBLIC_FILE.write_text(out_json, encoding='utf-8')

    print(f"\n=== 완료 ===", flush=True)
    print(f"총 스피커: {len(scorecard)}명", flush=True)
    print(f"적중률 산출 가능: {len(qualified)}명 (hit_eligible >= {MIN_HIT_ELIGIBLE})", flush=True)
    print(f"가격 매칭: {price_hit}건 성공 / {price_miss}건 실패", flush=True)

    if by_accuracy:
        print(f"\n[TOP] 적중률 Top 5:", flush=True)
        for slug, data in by_accuracy[:5]:
            print(f"   {data['name']}: {data['hit_rate']}% ({data['wins']}W/{data['losses']}L, 1Y avg {data['avg_return_1y']}%)", flush=True)

    if by_return:
        print(f"\n[TOP] 1Y 평균수익 Top 5:", flush=True)
        for slug, data in by_return[:5]:
            print(f"   {data['name']}: 1Y avg {data['avg_return_1y']}% (hit rate {data['hit_rate']}%)", flush=True)

    print(f"\n출력: {OUTPUT_FILE}", flush=True)
    print(f"공개: {PUBLIC_FILE}", flush=True)


if __name__ == '__main__':
    main()
