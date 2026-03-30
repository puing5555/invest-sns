# -*- coding: utf-8 -*-
# fetch_supply_demand_batch.py - stock_tickers.json KR 종목 전체 수급 크롤링
import sys, os, json, time, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from fetch_supply_demand import fetch_naver_supply, upload_to_supabase

def get_kr_tickers():
    """stock_tickers.json에서 KR 6자리 코드만 추출 (중복 제거)"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stock_tickers.json')
    tickers = json.load(open(data_path, encoding='utf-8'))
    kr = set()
    for t in tickers:
        code = t.replace('.KS', '')
        if re.match(r'^\d{6}$', code):
            kr.add(code)
    return sorted(kr)


def main():
    tickers = get_kr_tickers()
    print(f'[일괄 크롤링] KR 종목 {len(tickers)}개, 최근 1년치 (30페이지)')
    print(f'종목 목록: {", ".join(tickers[:10])}... 총 {len(tickers)}개')
    print()

    results = {'success': 0, 'fail': 0, 'skip': 0, 'details': []}

    for i, ticker in enumerate(tickers):
        print(f'[{i+1:3d}/{len(tickers)}] {ticker}', end=' ')
        try:
            rows = fetch_naver_supply(ticker, max_pages=30)
            if not rows:
                print('-> 0건 (skip)')
                results['skip'] += 1
                results['details'].append({'ticker': ticker, 'status': 'skip', 'count': 0})
                continue

            uploaded = upload_to_supabase(rows)
            print(f'-> {len(rows)}건 수집, {uploaded}건 업로드 ({rows[0]["trade_date"]}~{rows[-1]["trade_date"]})')
            results['success'] += 1
            results['details'].append({
                'ticker': ticker, 'status': 'ok',
                'count': len(rows), 'uploaded': uploaded,
                'from': rows[0]['trade_date'], 'to': rows[-1]['trade_date']
            })
        except Exception as e:
            print(f'-> ERROR: {e}')
            results['fail'] += 1
            results['details'].append({'ticker': ticker, 'status': 'error', 'error': str(e)})

        time.sleep(0.5)  # rate limit

    print(f'\n=== 완료 ===')
    print(f'성공: {results["success"]}, 실패: {results["fail"]}, 스킵: {results["skip"]}')

    # Save results
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'supply_demand_batch_result.json')
    json.dump(results, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'결과 저장: {out_path}')


if __name__ == '__main__':
    main()
