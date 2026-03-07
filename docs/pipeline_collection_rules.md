# 파이프라인 영상 수집 룰 (V11 기준)

## 제외 규칙
1. **쇼츠 제외**: duration_seconds < 60인 영상 → INSERT 금지
2. **중복 제외**: 같은 방송의 풀영상+클립이 있으면 클립만 수집 (duration_seconds 짧은 것 우선)

## 카테고리 분류 (category 컬럼)
- `stock_analysis`: 종목 분석, 특정 종목 매수/매도 의견
- `market_overview`: 전체 시황, 지수 전망
- `education`: 투자 교육, 개념 설명
- `macro`: 거시경제, 금리, 달러, 정책
- `general`: 기타

## videos 테이블 흐름
1. 자막 추출 + 긴 요약 생성 (Sonnet)
2. 카테고리 자동 분류
3. videos 테이블 INSERT (has_signal = FALSE 기본값)
4. V11 시그널 분석 → 시그널 있으면 has_signal = TRUE
5. influencer_signals 테이블 INSERT

## 주의
- 과거 영상: 기존 제목 필터링 유지
- 신규 영상 (사이트 오픈 후): 제목 필터링 없이 전체 수집
