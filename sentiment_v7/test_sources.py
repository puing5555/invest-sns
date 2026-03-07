"""
한국 시장 심리지수 v7 - 데이터 소스 테스트
각 지표의 데이터 수집 가능 여부 테스트

주의:
- pykrx: Python 3.14 + 최신 KRX API 변경으로 완전 작동 불가 (LOGOUT 400)
- KRX 직접 크롤링: LOGOUT 400 (세션 인증 필요)
- VKOSPI yfinance: 미지원
- 금투협 freesis: JS 동적 로딩
- 대체: 실현변동성(KOSPI), EWY 프록시, ECOS 일별 데이터
"""

import warnings
warnings.filterwarnings('ignore')

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import yfinance as yf

TODAY = datetime.today().strftime('%Y%m%d')
LAST_BIZ_DAY = '20260306'  # 최근 영업일 (금요일)
RESULTS = {}


# ─────────────────────────────────────────────
# 1. 모멘텀: 코스피 vs 50일 이평
# ─────────────────────────────────────────────
def fetch_momentum(date=None):
    """코스피 현재가 vs 50일 이동평균 괴리율 (%)"""
    try:
        ks11 = yf.download("^KS11", period="120d", progress=False, auto_adjust=True)
        if ks11.empty or len(ks11) < 50:
            return None, "데이터 부족", None
        close = ks11['Close'].squeeze()
        current = float(close.iloc[-1])
        ma50 = float(close.iloc[-50:].mean())
        raw = (current - ma50) / ma50 * 100
        return raw, f"코스피={current:,.0f}", f"50일이평={ma50:,.0f}"
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 2. 주가강도: 52주 신고가/신저가 비율 (KRX 세션 필요 → SKIP)
# ─────────────────────────────────────────────
def fetch_price_strength(date=None):
    """pykrx 파손 + KRX API LOGOUT → 작동 불가"""
    return None, "KRX API 세션 인증 필요 (LOGOUT 400)", None


# ─────────────────────────────────────────────
# 3. 시장폭: 상승/하락 종목 비율 (KRX 세션 필요 → SKIP)
# ─────────────────────────────────────────────
def fetch_market_breadth(date=None):
    """pykrx 파손 + KRX API LOGOUT → 작동 불가"""
    return None, "KRX API 세션 인증 필요 (LOGOUT 400)", None


# ─────────────────────────────────────────────
# 4. 풋/콜 비율 (KRX 세션 필요 → SKIP)
# ─────────────────────────────────────────────
def fetch_put_call_ratio(date=None):
    """KRX API LOGOUT → 작동 불가"""
    return None, "KRX API 세션 인증 필요 (LOGOUT 400)", None


# ─────────────────────────────────────────────
# 5. 변동성: KOSPI 실현변동성 (VKOSPI 대체)
# ─────────────────────────────────────────────
def fetch_volatility(date=None):
    """KOSPI 20일 실현변동성 vs 50일 이평 괴리율 (VKOSPI 대체)"""
    try:
        ks11 = yf.download("^KS11", period="120d", progress=False, auto_adjust=True)
        if ks11.empty or len(ks11) < 60:
            return None, "데이터 부족", None
        close = ks11['Close'].squeeze()
        returns = close.pct_change().dropna()
        # 20일 실현변동성 (연율화)
        vol20 = returns.rolling(20).std() * np.sqrt(252) * 100
        vol20 = vol20.dropna()
        if len(vol20) < 10:
            return None, "변동성 데이터 부족", None
        current = float(vol20.iloc[-1])
        ma50 = float(vol20.iloc[-min(50, len(vol20)):].mean())
        raw = (current - ma50) / ma50  # 비율
        return raw, f"현재변동성={current:.1f}%", f"50일평균={ma50:.1f}%"
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 6. 안전자산 수요: 코스피 vs 국채 ETF
# ─────────────────────────────────────────────
def fetch_safe_haven(date=None):
    """코스피 60일 수익률 - 국채ETF(114820.KS) 60일 수익률"""
    try:
        ks11 = yf.download("^KS11", period="90d", progress=False, auto_adjust=True)
        bond = yf.download("114820.KS", period="90d", progress=False, auto_adjust=True)

        if ks11.empty or bond.empty:
            return None, "데이터 없음", None

        ks_close = ks11['Close'].squeeze()
        bond_close = bond['Close'].squeeze()

        n_ks = min(60, len(ks_close))
        n_bond = min(60, len(bond_close))
        ks_ret = float((ks_close.iloc[-1] / ks_close.iloc[-n_ks]) - 1) * 100
        bond_ret = float((bond_close.iloc[-1] / bond_close.iloc[-n_bond]) - 1) * 100

        raw = ks_ret - bond_ret
        return raw, f"코스피60d={ks_ret:.2f}%", f"국채ETF60d={bond_ret:.2f}%"
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 7. 정크본드: 회사채 AA- vs BBB- 스프레드 (ECOS)
# ─────────────────────────────────────────────
def fetch_junk_bond(date=None):
    """한국은행 ECOS API 817Y002 회사채 스프레드 (BBB- - AA-)"""
    try:
        end_date = datetime.today().strftime('%Y%m%d')
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y%m%d')
        api_key = "sample"

        def get_rate(item_code):
            url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/10/817Y002/D/{start_date}/{end_date}/{item_code}"
            r = requests.get(url, timeout=10)
            data = r.json()
            if 'StatisticSearch' not in data:
                return None
            rows = data['StatisticSearch'].get('row', [])
            if not rows:
                return None
            return float(rows[-1].get('DATA_VALUE', 0))

        aa_minus = get_rate("010300000")   # 회사채 3년 AA-
        bbb_minus = get_rate("010320000")  # 회사채 3년 BBB-

        if aa_minus is None or bbb_minus is None:
            # 월별 데이터로 폴백
            def get_monthly(item_code):
                url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/5/721Y001/M/{start_date[:6]}/{end_date[:6]}/{item_code}"
                r = requests.get(url, timeout=10)
                data = r.json()
                if 'StatisticSearch' not in data:
                    return None
                rows = data['StatisticSearch'].get('row', [])
                if not rows:
                    return None
                return float(rows[-1].get('DATA_VALUE', 0))

            aa_minus = get_monthly("7020000")
            bbb_minus = get_monthly("7030000")

        if aa_minus is None or bbb_minus is None:
            return None, f"AA-={aa_minus}, BBB-={bbb_minus}", None

        raw = bbb_minus - aa_minus  # 스프레드 (클수록 공포)
        return raw, f"BBB-={bbb_minus:.3f}%", f"AA-={aa_minus:.3f}%"
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 8. 외국인 수급: EWY 5일 수익률 (프록시)
# ─────────────────────────────────────────────
def fetch_foreign_flow(date=None):
    """EWY(iShares Korea ETF) 5일 수익률로 외국인 수급 프록시"""
    try:
        ewy = yf.download('EWY', period='30d', progress=False, auto_adjust=True)
        if ewy.empty or len(ewy) < 5:
            return None, "EWY 데이터 부족", None

        close = ewy['Close'].squeeze()
        ret5d = float((close.iloc[-1] / close.iloc[-5]) - 1) * 100
        return ret5d, f"EWY5d={ret5d:.2f}%", f"현재={float(close.iloc[-1]):.2f}"
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 9. 신용잔고 (금투협 JS 동적 → SKIP)
# ─────────────────────────────────────────────
def fetch_credit_balance(date=None):
    """금투협 freesis.kofia.or.kr JS 동적 로딩 → 작동 불가"""
    return None, "JavaScript 동적 로딩 (API 없음)", None


# ─────────────────────────────────────────────
# 10. 고객예탁금 (금투협 JS 동적 → SKIP)
# ─────────────────────────────────────────────
def fetch_customer_deposit(date=None):
    """금투협 freesis.kofia.or.kr JS 동적 로딩 → 작동 불가"""
    return None, "JavaScript 동적 로딩 (API 없음)", None


# ─────────────────────────────────────────────
# 11. 코스닥/코스피 상대강도
# ─────────────────────────────────────────────
def fetch_kosdaq_kospi_ratio(date=None):
    """코스닥/코스피 60일 상대강도 변화"""
    try:
        kq = yf.download("^KQ11", period="90d", progress=False, auto_adjust=True)
        ks = yf.download("^KS11", period="90d", progress=False, auto_adjust=True)

        if kq.empty or ks.empty:
            return None, "데이터 없음", None

        kq_close = kq['Close'].squeeze()
        ks_close = ks['Close'].squeeze()

        current_ratio = float(kq_close.iloc[-1]) / float(ks_close.iloc[-1])
        n = min(60, len(kq_close), len(ks_close))
        prev_ratio = float(kq_close.iloc[-n]) / float(ks_close.iloc[-n])

        raw = (current_ratio - prev_ratio) / prev_ratio * 100
        return raw, f"현재비율={current_ratio:.4f}", f"60일전비율={prev_ratio:.4f}"
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 실행 & 결과 출력
# ─────────────────────────────────────────────
def run_tests():
    tests = [
        ("1. 모멘텀 (코스피 vs 50일 이평)", fetch_momentum),
        ("2. 주가강도 (52주 신고/신저)", fetch_price_strength),
        ("3. 시장폭 (상승/하락 비율)", fetch_market_breadth),
        ("4. 풋/콜 비율", fetch_put_call_ratio),
        ("5. 변동성 (실현변동성 VKOSPI대체)", fetch_volatility),
        ("6. 안전자산 수요 (코스피 vs 국채)", fetch_safe_haven),
        ("7. 정크본드 (AA- vs BBB- 스프레드)", fetch_junk_bond),
        ("8. 외국인 수급 (EWY 프록시)", fetch_foreign_flow),
        ("9. 신용잔고", fetch_credit_balance),
        ("10. 고객예탁금", fetch_customer_deposit),
        ("11. 코스닥/코스피 상대강도", fetch_kosdaq_kospi_ratio),
    ]

    results = {}
    print(f"\n{'='*65}")
    print(f"한국 시장 심리지수 v7 - 데이터 소스 테스트")
    print(f"테스트 날짜: {datetime.today().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*65}\n")

    for name, func in tests:
        try:
            result = func()
            if isinstance(result, tuple):
                raw, detail1, detail2 = result
            else:
                raw = result
                detail1 = detail2 = None

            if raw is not None:
                d2str = f" / {detail2}" if detail2 else ""
                print(f"[OK] {name}: raw={raw:.4f} | {detail1}{d2str}")
                results[name] = {"status": "OK", "raw": raw}
            else:
                print(f"[SKIP] {name}: {detail1}")
                results[name] = {"status": "SKIP", "error": str(detail1)}
        except Exception as e:
            print(f"[FAIL] {name}: 예외 - {e}")
            results[name] = {"status": "FAIL", "error": str(e)}

        time.sleep(0.3)

    print(f"\n{'='*65}")
    ok_count = sum(1 for v in results.values() if v['status'] == 'OK')
    skip_count = sum(1 for v in results.values() if v['status'] != 'OK')
    print(f"성공: {ok_count}/{len(tests)} | 실패/스킵: {skip_count}")
    print(f"{'='*65}\n")

    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("test_results.json 저장 완료")

    return results


if __name__ == "__main__":
    run_tests()
