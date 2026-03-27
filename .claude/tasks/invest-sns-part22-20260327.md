# Part 22 핸드오프 — 2026-03-27 (최종)

## 3/26~3/27 완료

### 스코어카드 v4
- 스윙/중기/장기 3구간 분리 (1Y/3Y/현재)
- 하이브리드 fallback (1Y 없으면 3개월+ current)
- EVAL_GRACE_DAYS 180→90
- TOP3/WORST3 current 기준 + 종목 중복 제거
- 통합 적중률 제거, 3구간 카드 메인
- 탐색 카드 장기>중기>스윙 fallback + "(장기)" 표시
- 평균수익률 → 중앙수익률(median) 변경

### 뉴스 기능
- Supabase stock_news 테이블 생성
- scripts/fetch_news.py — KR/US/CRYPTO 뉴스 크롤러
  - --market: 네이버 증권 시장 뉴스 (ticker=MARKET)
  - --all: KR 종목별 뉴스
  - --us: US 20개 종목 (Google News RSS)
  - --crypto: CRYPTO 10개 종목 (Google News RSS)
- 시장 뉴스 60건 + US 100건 + CRYPTO 50건 + KR 5,691건 수집
- 대시보드 시장뉴스 + 내 종목 뉴스 UI 완성
- 탐색 > 뉴스 페이지 신규

### 수목튜브 채널 추가
- auto_pipeline.py: channel_info 전달 + published_at NULL 수정
- V15.2 프롬프트 + CLI 기본값 업데이트
- 137건 시그널 정상 수집

### 크립토 가격 수정
- SUI/SEI/STRK yfinance 티커 충돌 수정
- -USD suffix 강제 적용 (stock_normalizer 참조 통일)

### 데이터 정합성
- ticker NULL 37건 → 0건 (22건 매핑 + 15건 삭제)
- ticker 오매핑/정규화/종목명 채움
- 애널리스트 중복 495건 제거

### 시스템 업데이트
- GitHub Actions: news-crawl.yml (4시간마다), weekly-scorecard.yml (주간)
- channel-add.md, qa-checker.md 업데이트
- auto_pipeline.py: channel_info + V15.2

### 탐색 페이지 강화
- 유형별 필터 (올라운더/스나이퍼/홈런히터) 추가
- 컨센서스 탭 신규: 최근 30일 종목별 강세/약세 분석

## 미완료
1. 신한투자증권 이름 파싱 511건 — pdf_url null이라 PDF 다운 불가. nid 기반 pdf_url 재수집 필요
2. GitHub Actions 시크릿 설정 필요: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

## 데이터 현황
- 시그널: 1,860건 (16개 채널, ticker NULL 0건)
- 애널리스트 리포트: 5,801건 (analyst NULL 617건, 신한 511건)
- 종목 페이지: 390개
- 공시: 29,372건
- 뉴스: 5,901건 (KR 5,691 + US 100 + CRYPTO 50 + 시장 60)
- 스코어카드 qualified: 14명
