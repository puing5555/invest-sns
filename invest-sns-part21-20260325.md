# invest-sns Part 21 핸드오프 (2026-03-25~26)

## 3/25~26 완료한 것

### 1. 스코어카드 v1→v2→v3→v4
- **적중률**: 매수+긍정+매도만 (부정/중립 제외)
- **수익률**: `stockPrices.json` 기반 1Y + 3Y + Current (direction-adjusted 제거)
- **dedup**: 월 1건 (speaker+ticker+YYYY-MM)
- **하이브리드 판정**: 1Y 우선 → 3개월+ 경과 시 current fallback → 3개월 미만 pending
- **3구간 성과 (tiers)**: 스윙(1Y) / 중기(1~3Y) / 장기(3Y+) — 메인 카드로 표시
- **TOP3/WORST3**: current return 기준 정렬, 종목 중복 제거, 날짜(YYYY.MM) 표시
- 스타일 태그 → 헤더 이름 옆 배치
- 홈런 비율, 기대수익률, 팔로우 시뮬레이션 (1Y/현재 각각)
- 성과 요약 단일 적중률/승패/중앙수익률/최고콜/승패바 → 삭제, 3구간 카드가 메인

### 2. AI 분석 리포트 (31명, 룰 기반 텍스트)
- `scripts/generate_influencer_report.py` 신규 생성
- 7개 섹션: 한줄 평가, 강점/약점, TOP3/WORST3, 투자 패턴, 트렌드, 팔로우 시뮬레이션, AI 종합 의견

### 3. V15.2 프롬프트 + 대담 재분석
- `prompts/pipeline_v15.2.md`: 화자 구분 강화 — `{CHANNEL_OWNER}`, `{CHANNEL_TYPE}` 플레이스홀더
- `pipeline_config.py`: `CHANNEL_OWNERS` 16개 채널 + `get_channel_owner()`
- `signal_analyzer_rest.py`: `channel_info` 주입 + `unknown_guest` 감지
- 자막 한도 8000→20000자
- DB: 안경투 `channel_type` → `interview`
- **대담 재분석 27건 완료** (이효석 18건 + 안유화쇼 9건)
  - 게스트 실명 감지: 연수르, 허진, 전철희, 이경원, 유사남, 테이버, 박현근, 에릭, 이혜복, 조철
  - `reanalyze_interviews.py` 전용 스크립트 생성 (--apply 모드)

### 4. DART 공시 6년치 수집 (29,372건)

### 5. 프로필 페이지 개선
- 3구간 카드 메인 레이아웃 (스윙/중기/장기)
- 모든 시그널 수익률 통일 표시 (`allReturnsMap` — dedup 제거 시그널도 표시)
- 수익률 컬러: current 컬러(메인) + 1Y 회색(참고), 3개월 미만만 회색
- 부정/중립 "참고" 표시

### 6. 데이터 정리
- **표상록 speaker 통합**: "표상록"(34건) → "표상록의 코인 포트폴리오"(100건)로 DB 이관
- **코린이아빠 버그 수정**: `getInfluencerProfileBySpeaker()` UUID 타입 에러 — Step 1(speaker_id=이름) 제거, speakers 테이블 경유만
- **슈카 slug 수정**: "syuka" → "슈카" (DB name과 일치)
- **가격 매칭 ±30일**: `find_closest_price` 7일→30일 확대
- **ticker 오매핑 발견**: 두나무→042700(한미반도체), 이오테크닉스→240810(원익IPS), 바벨론→BABY(Babytoken)

### 7. 탐색 페이지 인플루언서 카드
- 적중률/수익률: 장기→중기→스윙 fallback (가장 긴 구간 우선)
- 기준 표시: "적중 80.0% (장기)" 또는 "적중 41.6% (스윙)"
- 평균 수익률 표시 (스윙 avg → 해당 tier avg)

### 8. 배포
- `--force push` 배포 문제 해결 (orphan 방식에서 히스토리 충돌)
- 최종 배포: `00086f1e` (2026-03-26)
- 위즈덤투스 스윙 101건 라이브 확인

---

## 미완료 / 즉시 해야 할 것

### 1. ticker 오매핑 DB 수정
- 두나무: ticker 042700 → null (비상장)
- 이오테크닉스: ticker 240810 → 039030
- 바벨론: ticker BABY → 확인 필요

### 2. 탐색 페이지 소작업
- 유형 카드 4→7개
- 컨센서스 기간 1→3개월

### 3. 코린이아빠 브라우저 캐시 확인
- 코드/데이터 정상 확인 완료, 캐시 문제로 추정

---

## 다음 우선순위

4. YouTube API 연동 (구독자 수, 조회수)
5. GitHub Actions 자동화 (매주 스코어카드, 매월 리포트, 매일 DART)
6. 네러티브 맵 기초작업

---

## 보류/대기
- 기존 시그널 1,000+개 타임스탬프 재분석
- 탭 구조 변경 (TODAY/SNS/탐색/포트폴리오/프로필)
- 인터뷰 채널 대량 크롤링 (삼프로TV 등) — V15.2 준비 완료
- git history 정리 (465MB → 1GB limit 주의)
- V15.2 프롬프트 전체 평가 (280건 정답지 기준)
- fast_analyzer.py / sesang101_pipeline.py 인코딩 깨짐(CP949 mojibake) 수정

---

## 기술 스택 현황 (2026-03-26)
- 시그널: 1,699건 (16개 채널, 60 speakers)
- 적중률 산출 가능: 13명 (hit_eligible ≥ 10, EVAL_GRACE_DAYS=90)
- 가격 매칭: 1,084건 성공 / 73건 실패 (±30일 윈도우)
- 스코어카드: v4 (3구간 tiers, 하이브리드 fallback, current 기준 TOP3)
- 프롬프트: V15.2 운영 (화자 구분 강화, 자막 20000자)
- 모델: claude-sonnet-4-20250514
- 배포: gh-pages (`--force` push, 최종 `00086f1e`)
