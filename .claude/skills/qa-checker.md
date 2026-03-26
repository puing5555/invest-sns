# qa-checker — 품질 체크

## 실행 절차

### 1. 가격 $0 종목 찾기
```python
import json
prices = json.load(open('data/stockPrices.json', encoding='utf-8'))
zero = [k for k, v in prices.items() if v.get('price') == 0 or v.get('currentPrice') == 0]
print(f"가격 $0 종목: {len(zero)}개", zero)
```

### 2. 종목 페이지 누락 찾기
```python
import json, os
tickers = json.load(open('data/stock_tickers.json', encoding='utf-8'))
# tickers가 리스트인 경우 / dict인 경우 모두 대응
codes = tickers if isinstance(tickers, list) else list(tickers.keys())
missing = [c for c in codes if not os.path.exists(f'out/stock/{c}/index.html')]
print(f"페이지 누락: {len(missing)}개", missing)
```

### 3. 해석 없는 주요 공시 찾기
```python
import json
data = json.load(open('data/disclosures.json', encoding='utf-8'))
disclosures = data.get('disclosures', [])
# 주요 공시 = sentiment가 호재/악재/확인필요인데 ai_analysis가 없는 것
key = [d for d in disclosures
       if d.get('sentiment') in ('호재', '악재', '확인필요')
       and not d.get('ai_analysis')]
print(f"해석 누락 주요 공시: {len(key)}개")
for d in key[:10]:
    print(f"  {d.get('stock_code')} | {d.get('rcept_dt')} | {d.get('report_nm','')[:40]}")
```

### 4. 결과 리포트
```
📊 QA 체크 결과
- 가격 $0: N개 [목록]
- 페이지 누락: N개 [목록]
- 해석 누락 주요 공시: N개 [상위 10개]
→ 조치 필요 항목: ...
```

## 조치 기준
- 가격 $0 → stockPrices.json 업데이트 필요 (Yahoo Finance 재수집)
- 페이지 누락 → generateStaticParams에 종목 추가 또는 tickers 정리
- 해석 누락 → Claude AI 해석 재생성 필요
