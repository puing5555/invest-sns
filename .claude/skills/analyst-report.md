# 애널리스트 리포트 시스템 운영

## 데이터 수집 (크롤링)

### 전체 크롤링 (처음부터)
```bash
node scripts/crawl-naver-research-v2.js
```

### 이어서 크롤링 (중단 후 재개)
```bash
node scripts/crawl-naver-research-v2.js --resume
```

### 크롤링 후 수익률 계산
```bash
pip install yfinance
python scripts/calc_analyst_returns.py
```

### 결과 확인
```bash
# 총 건수, NULL 비율 확인
python -c "
import json
d = json.load(open('data/analyst_reports.json'))
total = sum(len(v) for v in d.values())
null_tp = sum(1 for rs in d.values() for r in rs if not r.get('target_price'))
null_ret = sum(1 for rs in d.values() for r in rs if r.get('return_12m') is None)
print(f'종목: {len(d)}개, 리포트: {total}건')
print(f'target_price NULL: {null_tp}건 ({null_tp/total*100:.1f}%)')
print(f'return_12m NULL: {null_ret}건 ({null_ret/total*100:.1f}%)')
"
```

## 데이터 구조

### analyst_reports.json
```json
{
  "005930": [
    {
      "ticker": "005930",
      "firm": "SK증권",
      "analyst": "김현우",
      "title": "재평가가 필요하다",
      "target_price": 300000,
      "opinion": "BUY",
      "published_at": "2026-02-24",
      "pdf_url": "https://stock.pstatic.net/...",
      "nid": "123456",
      "summary": "AI 한줄 요약",
      "ai_detail": "## 투자포인트\n...\n## 실적전망\n...",
      "return_3m": 12.5,
      "return_6m": 25.3,
      "return_12m": 45.2,
      "price_at_signal": 183500,
      "price_current": 267000,
      "target_achieved": false
    }
  ]
}
```

## 프론트엔드 구조

### 페이지: app/explore/analyst/page.tsx
- 3개 탭: 최신 리포트 / 종목별 / 애널리스트별
- 종목별: 컨센서스 요약 (3개월) + 테이블 형식 리포트 목록
- 리포트 클릭 → ReportDetailModal (AI 요약 + PDF 링크)

### 종목 페이지: app/stock/[code]/ → 애널리스트 탭
- 컨센서스 카드 + 주가 vs 목표가 차트 + 리포트 목록

## 종목 추가 시
1. `scripts/crawl-naver-research-v2.js`의 `KR_TICKERS` 배열에 종목코드 추가
2. `TICKER_NAMES`에 한글명 매핑 추가
3. 크롤러 실행 (`--resume` 가능)
4. 프론트엔드 `app/explore/analyst/page.tsx`의 `TICKER_NAMES`에도 추가

## 수익률 기준
- 기본 정렬: 12개월 forward return
- 보조: 3개월, 6개월, 목표가 적중률
- 컨센서스: 최근 3개월 리포트 기준
