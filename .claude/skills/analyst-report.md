# 애널리스트 리포트 시스템

## 데이터 구조

### analyst_reports.json (정적 데이터)
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
      "ai_detail": "## 투자포인트\n...",
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

## 프론트엔드 페이지

### 탐색 페이지: `app/explore/analyst/page.tsx`
- 3개 탭: 최신 리포트 / 종목별 / 애널리스트별
- 종목별: 컨센서스 요약 (3개월) + 테이블 리포트 목록
- 기본 정렬: 12개월 forward return
- 리포트 클릭 → `ReportDetailModal` (AI 요약 + PDF)

### 종목 페이지: `app/stock/[code]/` → 애널리스트 탭
- 컨센서스 카드 + 주가 vs 목표가 차트 + 리포트 목록

## 종목 추가 절차

1. `scripts/crawl-naver-research-v2.js`
   - `KR_TICKERS` 배열에 종목코드 추가
   - `TICKER_NAMES`에 한글명 매핑 추가
2. 크롤러 실행 (→ `crawling.md` 참조)
3. 수익률 계산: `python scripts/calc_analyst_returns.py`
4. 프론트엔드 `app/explore/analyst/page.tsx`의 `TICKER_NAMES`에도 추가
5. `npm run build` 확인

## 수익률 기준
- 기본 정렬: 12개월 forward return
- 보조: 3개월, 6개월, 목표가 적중률
- 컨센서스: 최근 3개월 리포트 기준
- 계산 방법 상세 → `crawling.md` 참조
