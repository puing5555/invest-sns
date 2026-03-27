핸드오프 문서 최종 업데이트 — invest-sns-part22-20260327.md 생성:

git add -A && git commit -m "Part 22: scorecard v4 + news + soomoktube + crypto fix + median"

그리고 invest-sns-part22-20260327.md 생성:

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
- scripts/fetch_news.py — 네이버 증권 KR 종목 뉴스 크롤러
- 112개 KR 종목 5,691건 수집 완료
- 종목 상세 페이지 뉴스 탭 추가
- 탐색 > 뉴스 페이지 신규
- 대시보드 뉴스 섹션 추가

### 수목튜브 채널 추가
- auto_pipeline.py 버그 수정: channel_info 미전달 + published_at NULL
- V15.2 프롬프트 + CLI 기본값 업데이트
- 137건 시그널 정상 수집 (published_at 정상)

### 크립토 가격 수정
- SUI/SEI/STRK yfinance 티커 충돌 수정 (REIT vs 크립토)
- -USD suffix 강제 적용 (재발 방지)
- 크립토 가격 5종 업데이트 (XLM, WLD, POL, STX, PEPE)

### 데이터 정합성
- ticker 오매핑 수정 (두나무/이오테크닉스/바벨론/리노공업/자화전자)
- ticker 정규화 (.HK/.T 제거, 텐센트 통일)
- 종목명 207건 채움
- 애널리스트 중복 495건 제거 (6,296→5,801건)
- 코린이아빠 UUID 쿼리 버그 수정

### 시스템 업데이트
- channel-add.md: V15.2 + 스코어카드 v4 + QA Gate 3 강화
- qa-checker.md: 19항목으로 확장
- auto_pipeline.py: channel_info 전달 + V15.2 기본값
- prompts/pipeline_v15.2.md: 비상장 목록, ticker 정규화, key_quote 원문, 대담 감지

### --force push 배포 문제 해결
- orphan push 히스토리 충돌 → --force push 필수

## 미완료
1. 대시보드 시장 뉴스 (네이버 메인 뉴스 크롤링)
2. US/CRYPTO 뉴스 크롤러 (구글 뉴스)
3. QA Gate에 published_at NULL 검증 추가
4. 신한투자증권 이름 파싱 511건
5. GitHub Actions 자동화 (뉴스 4시간마다, 스코어카드 매주)
6. 탐색 소작업 (유형카드, 컨센서스)
7. ticker NULL 37건 기존 시그널 수정

## 데이터 현황
- 시그널: 1,875건 (16개 채널)
- 애널리스트 리포트: 5,801건
- 종목 페이지: 390개
- 공시: 29,372건
- 뉴스: 5,691건 (KR)
- 스코어카드 qualified: 13명+