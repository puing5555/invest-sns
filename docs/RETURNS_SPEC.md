# invest-sns 수익률 및 날짜 처리 스펙 (영구 규칙)

## ⚠️ 이 파일은 절대 무시하지 마세요. 수익률과 날짜 관련 버그가 20회 이상 반복되고 있습니다.

---

## 1. 날짜 (Date) 규칙

### 문제
- 현재: 모든 항목의 날짜가 DB 삽입 시점(오늘 날짜)으로 찍힘
- 예: 2주 전 유튜브 영상의 발언이 "2026년 3월 15일"로 표시됨

### 올바른 로직
```
날짜 = YouTube 영상의 업로드 날짜 (publishedAt)
```

### 구현 방법
1. YouTube Data API v3에서 `snippet.publishedAt` 필드를 사용
2. 영상 업로드 날짜를 ISO 8601 형식으로 저장 (예: "2026-03-01T00:00:00Z")
3. DB 컬럼: `video_published_at` (NOT `created_at`, NOT `inserted_at`)
4. 프론트엔드 표시: `video_published_at`을 "YYYY년 M월 D일" 형식으로 표시

### 절대 하지 말 것
- ❌ `new Date()` 또는 `Date.now()`를 날짜로 사용
- ❌ Supabase의 `created_at` 타임스탬프를 발언 날짜로 사용
- ❌ 데이터 삽입 시점을 발언 날짜로 사용

---

## 2. 수익률 (Returns) 규칙

### 문제
- 현재: 수익률 컬럼이 전부 "-"로 표시됨
- 원인 추정: 가격 데이터를 못 가져오거나, 계산 로직이 없거나, 에러 시 "-" 폴백

### 올바른 로직
```
수익률(%) = ((현재가 - 발언일_종가) / 발언일_종가) × 100
```

### 종목별 가격 소스
| 종목 | 티커 | 가격 소스 |
|------|------|-----------|
| 비트코인 | BTC-USD | Yahoo Finance API |
| 테슬라 | TSLA | Yahoo Finance API |
| 엔비디아 | NVDA | Yahoo Finance API |
| 삼성전자 | 005930.KS | Yahoo Finance API |
| 현대차 | 005380.KS | Yahoo Finance API |

### 구현 방법

#### A. 발언일 종가 (기준가) - 데이터 삽입 시 1회 저장
```javascript
// 발언 데이터 삽입 시, 해당 날짜의 종가를 함께 저장
// Yahoo Finance API 호출 (Webshare 프록시 필수)
const getClosingPrice = async (ticker, date) => {
  // date = video_published_at (영상 업로드 날짜)
  // Yahoo Finance historical data API 사용
  // period1, period2를 해당 날짜로 설정
  // 주말/휴일인 경우 직전 거래일 종가 사용
  
  // 프록시 설정 필수 (Yahoo Finance IP 차단 대응)
  // Webshare residential proxy를 통해 호출
};
```

#### B. 현재가 - 프론트엔드에서 실시간 또는 캐시
```javascript
// 옵션 1: 서버에서 주기적으로 업데이트 (추천)
// - cron job으로 1시간마다 현재가 업데이트
// - Supabase 테이블: current_prices (ticker, price, updated_at)

// 옵션 2: 프론트엔드에서 로드 시 fetch
// - 페이지 로드 시 각 종목 현재가 조회
// - 단, Yahoo Finance CORS 이슈 주의 → 서버 사이드 권장
```

#### C. 수익률 계산
```javascript
const calculateReturn = (currentPrice, basePrice) => {
  if (!currentPrice || !basePrice || basePrice === 0) return null;
  return ((currentPrice - basePrice) / basePrice * 100).toFixed(2);
};
```

#### D. 프론트엔드 표시
```
양수: +12.5% (초록색)
음수: -8.3% (빨간색)
데이터 없음: "계산중" (회색) — 절대 "-"로 표시하지 말 것
```

### 절대 하지 말 것
- ❌ 가격을 못 가져왔을 때 조용히 "-" 표시하고 넘어가기
- ❌ 에러 로깅 없이 catch 블록에서 무시하기
- ❌ 프록시 없이 Yahoo Finance 직접 호출 (IP 차단됨)
- ❌ 한국 주식(삼성전자, 현대차)의 티커를 .KS 없이 사용

---

## 3. DB 스키마 요구사항

```sql
-- influencer_signals 또는 해당 테이블에 다음 컬럼 필수:
ALTER TABLE influencer_signals ADD COLUMN IF NOT EXISTS 
  video_published_at TIMESTAMPTZ;  -- 영상 업로드 날짜

ALTER TABLE influencer_signals ADD COLUMN IF NOT EXISTS 
  base_price DECIMAL;  -- 발언일 종가 (기준가)

ALTER TABLE influencer_signals ADD COLUMN IF NOT EXISTS 
  base_price_ticker VARCHAR;  -- 가격 조회에 사용한 티커
```

---

## 4. 체크리스트 (배포 전 확인)

- [ ] 모든 항목의 날짜가 `video_published_at`에서 오는가?
- [ ] `created_at`이나 `Date.now()`를 날짜 표시에 사용하고 있지 않은가?
- [ ] 수익률이 "-"로 표시되는 항목이 있는가? → 있으면 에러 로그 확인
- [ ] Yahoo Finance 호출 시 Webshare 프록시를 사용하고 있는가?
- [ ] 한국 주식 티커에 .KS 접미사가 붙어있는가?
- [ ] 수익률 색상이 양수=초록, 음수=빨강으로 표시되는가?

---

## 5. 에러 처리

```javascript
// 가격 조회 실패 시
try {
  const price = await fetchPrice(ticker, date);
  if (!price) {
    console.error(`[RETURNS] 가격 조회 실패: ${ticker}, ${date}`);
    // "계산중"으로 표시, 나중에 재시도
    // 절대 조용히 "-"로 넘어가지 말 것
  }
} catch (error) {
  console.error(`[RETURNS] API 에러: ${ticker}`, error.message);
  // Sentry 또는 로그 시스템에 기록
}
```
