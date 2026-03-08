#!/usr/bin/env python3
"""
브리핑 마스터 스크립트 - 시황 데이터 수집
Usage: python run_briefing.py --type morning|open|close|night
Output: 포맷된 브리핑 텍스트 (시황 파트, 뉴스는 cron agent가 web_search로 추가)
"""
import argparse
import sys
import io
import os

# Python 3.14 인코딩 패치
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
    sys.exit(1)

try:
    import pytz
    TIMEZONE = pytz.timezone('Asia/Bangkok')
except ImportError:
    from datetime import timezone, timedelta
    TIMEZONE = timezone(timedelta(hours=7))

from datetime import datetime
import json

TICKERS = {
    'SP500':   '^GSPC',
    'NASDAQ':  '^IXIC',
    'DOW':     '^DJI',
    'VIX':     '^VIX',
    'USDKRW':  'USDKRW=X',
    'WTI':     'CL=F',
    'BTC':     'BTC-USD',
    'ETH':     'ETH-USD',
    'KOSPI':   '^KS11',
    'KOSDAQ':  '^KQ11',
}

WEEKDAY_KR = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}


def fetch_quote(sym):
    """yfinance로 종목 최신 시세 + 전일 대비 수익 반환"""
    try:
        t = yf.Ticker(sym)
        hist = t.history(period='3d', interval='1d')
        if hist.empty:
            return None
        today = hist.iloc[-1]
        data = {
            'price': float(today['Close']),
            'open':  float(today['Open']),
            'high':  float(today['High']),
            'low':   float(today['Low']),
        }
        if len(hist) >= 2:
            prev_close = float(hist.iloc[-2]['Close'])
            chg = data['price'] - prev_close
            pct = chg / prev_close * 100
            data['change'] = round(chg, 2)
            data['pct']    = round(pct, 2)
        return data
    except Exception as e:
        return {'error': str(e)}


def fmt_price(data, name, unit=''):
    """시세 데이터를 이모지 포함 1줄 텍스트로 포맷"""
    if not data or 'error' in data:
        return f'  • {name}: ⚠️ 데이터 없음'
    p   = data['price']
    chg = data.get('change')
    pct = data.get('pct')

    if unit == 'won':
        p_str = f'{p:,.0f}원'
    elif unit == '$':
        p_str = f'${p:,.2f}'
    else:
        p_str = f'{p:,.2f}'

    if chg is not None and pct is not None:
        arrow  = '▲' if pct >= 0 else '▼'
        sign   = '+' if pct >= 0 else ''
        if unit == 'won':
            chg_str = f'{chg:+,.0f}원'
        elif unit == '$':
            chg_str = f'{chg:+,.2f}'
        else:
            chg_str = f'{chg:+,.2f}'
        return f'  • {name}: {p_str} {arrow} {chg_str} ({sign}{pct:.2f}%)'
    return f'  • {name}: {p_str}'


def get_investor_lines():
    """pykrx 수급 데이터 파일에서 최신 데이터 읽기"""
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pykrx_data.json')
        with open(path, encoding='utf-8') as f:
            raw = json.load(f)
        latest_date = sorted(raw.keys())[-1]
        inv = raw[latest_date].get('investors', {})
        if inv and any(v is not None for v in inv.values()):
            def fmtv(v):
                if v is None:
                    return 'N/A'
                sign = '+' if v >= 0 else ''
                return f'{sign}{v/100_000_000:.1f}억'
            return (
                f"  • 외국인: {fmtv(inv.get('foreign'))}\n"
                f"  • 기관:   {fmtv(inv.get('institution'))}\n"
                f"  • 개인:   {fmtv(inv.get('individual'))}\n"
                f"  (기준: {latest_date})"
            )
    except Exception:
        pass
    return '  • 수급 데이터 수집 중 (pykrx 픽스 진행 중)'


def main():
    parser = argparse.ArgumentParser(description='브리핑 시황 데이터 수집')
    parser.add_argument('--type', required=True,
                        choices=['morning', 'open', 'close', 'night'],
                        help='브리핑 유형')
    args = parser.parse_args()

    now = datetime.now(TIMEZONE)
    is_weekend = now.weekday() >= 5  # 5=Sat, 6=Sun
    date_str   = f"{now.strftime('%Y/%m/%d')}({WEEKDAY_KR[now.weekday()]})"

    # 필요한 티커만 가져오기 (속도 최적화)
    type_tickers = {
        'morning': ['SP500', 'NASDAQ', 'DOW', 'VIX', 'USDKRW', 'WTI', 'BTC'],
        'open':    [] if is_weekend else ['KOSPI', 'KOSDAQ'],
        'close':   [] if is_weekend else ['KOSPI', 'KOSDAQ', 'USDKRW'],
        'night':   ['SP500', 'NASDAQ', 'DOW', 'VIX', 'USDKRW', 'BTC', 'ETH'],
    }

    q = {}
    for k in type_tickers[args.type]:
        q[k] = fetch_quote(TICKERS[k])

    # ── 모닝 브리핑 07:00 ──────────────────────────────────────
    if args.type == 'morning':
        lines = [
            f'📰 {date_str} 07:00 모닝 브리핑',
            '',
            '🌏 간밤 미국장 마감',
            fmt_price(q.get('SP500'),  'S&P500'),
            fmt_price(q.get('NASDAQ'), 'NASDAQ'),
            fmt_price(q.get('DOW'),    '다우존스'),
            fmt_price(q.get('VIX'),    'VIX'),
            '',
            '💵 주요 지표',
            fmt_price(q.get('USDKRW'), '달러/원', 'won'),
            fmt_price(q.get('WTI'),    'WTI유'),
            fmt_price(q.get('BTC'),    'BTC', '$'),
        ]
        if is_weekend:
            lines += ['', '⚠️ 주말 — 한국 정규장 휴장']

    # ── 장 시작 브리핑 09:05 ──────────────────────────────────
    elif args.type == 'open':
        if is_weekend:
            lines = [
                f'📈 {date_str} 09:05',
                '',
                '⚠️ 주말 — 정규장 휴장',
                '(월요일 09:05 정상 브리핑 예정)',
            ]
        else:
            lines = [
                f'📈 {date_str} 09:05 장 시작',
                '',
                '🏃 개장 현황',
                fmt_price(q.get('KOSPI'),  '코스피'),
                fmt_price(q.get('KOSDAQ'), '코스닥'),
                '',
                '👥 수급 (전일 기준)',
                get_investor_lines(),
            ]

    # ── 장 마감 브리핑 16:00 ──────────────────────────────────
    elif args.type == 'close':
        if is_weekend:
            lines = [
                f'📉 {date_str} 16:00',
                '',
                '⚠️ 주말 — 정규장 휴장',
                '(월요일 16:00 정상 브리핑 예정)',
            ]
        else:
            lines = [
                f'📉 {date_str} 16:00 장 마감',
                '',
                '📊 마감 현황',
                fmt_price(q.get('KOSPI'),  '코스피'),
                fmt_price(q.get('KOSDAQ'), '코스닥'),
                '',
                '💵 환율',
                fmt_price(q.get('USDKRW'), '달러/원', 'won'),
                '',
                '👥 수급 마감',
                get_investor_lines(),
            ]

    # ── 미국장 개장 브리핑 23:00 ──────────────────────────────
    elif args.type == 'night':
        lines = [
            f'🇺🇸 {date_str} 23:00 미국장',
            '',
            '📈 현황',
            fmt_price(q.get('SP500'),  'S&P500'),
            fmt_price(q.get('NASDAQ'), 'NASDAQ'),
            fmt_price(q.get('DOW'),    '다우존스'),
            fmt_price(q.get('VIX'),    'VIX'),
            '',
            '💵 달러 / 가상자산',
            fmt_price(q.get('USDKRW'), '달러/원', 'won'),
            fmt_price(q.get('BTC'),    'BTC', '$'),
            fmt_price(q.get('ETH'),    'ETH', '$'),
        ]
        if is_weekend:
            lines += ['', '⚠️ 주말 — 미국 정규장 휴장']

    print('\n'.join(lines))


if __name__ == '__main__':
    main()
