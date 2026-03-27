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
codes = tickers if isinstance(tickers, list) else list(tickers.keys())
missing = [c for c in codes if not os.path.exists(f'out/stock/{c}/index.html')]
print(f"페이지 누락: {len(missing)}개", missing)
```

### 3. 해석 없는 주요 공시 찾기
```python
import json
data = json.load(open('data/disclosures.json', encoding='utf-8'))
disclosures = data.get('disclosures', [])
key = [d for d in disclosures
       if d.get('sentiment') in ('호재', '악재', '확인필요')
       and not d.get('ai_analysis')]
print(f"해석 누락 주요 공시: {len(key)}개")
for d in key[:10]:
    print(f"  {d.get('stock_code')} | {d.get('rcept_dt')} | {d.get('report_nm','')[:40]}")
```

### 4. ticker 오매핑 스캔
```python
import json
sp = json.load(open('data/stockPrices.json', encoding='utf-8'))
# DB에서 전체 시그널의 stock-ticker 쌍 수집 후 stockPrices name과 비교
# stock 첫 3글자가 stockPrices name에 없으면 불일치 의심
```
- 주요 체크: stock=두나무 ticker=042700(한미반도체) 같은 비상장→상장 오매핑
- ticker 접미사(.HK, .T, .KS) 잔존 여부

### 5. 종목 페이지 이름 누락
```python
import json
sp = json.load(open('data/stockPrices.json', encoding='utf-8'))
no_name = [t for t, v in sp.items()
           if (isinstance(v, dict) and not v.get('name',''))
           or isinstance(v, list)]
print(f"이름 없음: {len(no_name)}개", no_name)
```
- 종목 페이지에서 ticker 숫자로만 표시되는 종목 → name 필드 채우기

### 6. 비상장 종목 시그널 체크
```python
# DB에서 ticker가 있는데 비상장인 종목 찾기
# 알려진 비상장: 스페이스X, 오픈AI, 두나무, 토스, 삼성디스플레이
# ticker가 null이 아닌데 stockPrices에 없는 종목 중 비상장 의심
```

### 7. 같은 종목 다른 ticker
```python
# DB에서 같은 stock에 다른 ticker가 있는 건 전체 스캔
# 예: 텐센트(0700/TCEHY), SMIC(0981/0981.HK)
```

### 8. 인플루언서별 수익률 null 비율
```python
import json
d = json.load(open('data/influencer_scorecard.json', encoding='utf-8'))
for slug, card in d['speakers'].items():
    sl = card.get('scored_list', [])
    if not sl: continue
    null_pct = sum(1 for s in sl if s.get('return_current') is None) / len(sl) * 100
    if null_pct >= 10:
        print(f"⚠ {card['name']}: {null_pct:.0f}% null ({sum(1 for s in sl if s.get('return_current') is None)}/{len(sl)})")
```
- 10% 이상이면 경고 → ticker 누락 또는 stockPrices 미수록

### 9. 대담 영상 미감지
```python
# interview 채널인데 speaker_name이 전부 null인 시그널 스캔
# 안유화쇼, 삼프로TV 등에서 게스트 발언이 운영자로 귀속된 건
```

### 10. 결과 리포트
```
📊 QA 체크 결과
- 가격 $0: N개
- 페이지 누락: N개
- 해석 누락 주요 공시: N개
- ticker 오매핑: N종목
- 이름 누락: N종목
- 비상장 ticker: N건
- 같은 종목 다른 ticker: N종목
- 수익률 null 10%+: N명
- 대담 미감지: N건
- 하이브리드 fallback 이상: N건
- 스윙/중기/장기 건수 이상: N명
- 탐색 카드 fallback 이상: N명
- 3개월 미만 회색 / 3개월+ 컬러 이상: N건
- key_quote 20자미만/200자초과: N건
- confidence 5미만: N건
- published_at 크롤링 날짜 의심: N건
- 크립토 동일 코인 dedup 후 scored 적은 건: 정상
→ 조치 필요 항목: ...
```

## 조치 기준
- 가격 $0 → stockPrices.json 업데이트 (Yahoo Finance/CoinGecko 재수집)
- 페이지 누락 → generateStaticParams에 종목 추가
- 해석 누락 → Claude AI 해석 재생성
- ticker 오매핑 → DB PATCH로 수정
- 이름 누락 → stockPrices.json name 필드 채우기 (DB signal stock→ticker 자동 매핑)
- 비상장 ticker → null로 변경
- 같은 종목 다른 ticker → 하나로 통일 (접미사 제거, 원주 기준)
- 수익률 null → stockPrices 가격 데이터 추가
- 대담 미감지 → V15.2 재분석 (reanalyze_interviews.py)
