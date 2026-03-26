스코어카드 v2 + AI 분석 리포트 + 프로필 개선:

## Part A: 스코어카드 v2 필드 추가
calc_influencer_scorecard.py에 추가:
- top3_calls: 수익률 TOP 3 (종목, 수익률, 날짜)
- worst3_calls: 수익률 WORST 3
- homerun_rate: +100% 이상 비율
- expected_return: 적중률 × 평균이익 - (1-적중률) × 평균손실
- style_tag: 🎯스나이퍼(적중60%+,홈런<15%) / 💣홈런히터(적중<55%,홈런20%+) / ⭐올라운더(적중55%+,홈런15%+) / 📊데이터부족(scored<10)
- market_breakdown: 시장별(KR/US/CRYPTO) 적중률 각각
- trend_30d: 최근 30일 적중률 vs 전체 적중률

## Part B: AI 분석 리포트
generate_influencer_report.py 신규 생성:
- scorecard JSON 읽어서 인플루언서별 분석 텍스트 생성
- 포함: a) 한줄 평가 b) 강점/약점(구체적 종목) c) TOP3/WORST3 콜 d) 투자 패턴(선호시장,집중종목) e) 시기별 트렌드 f) 팔로우 시뮬레이션(매 콜 100만원 투입 시 누적수익) g) AI 종합 의견
- AI API 호출 없이 룰 기반 텍스트 생성
- 결과: influencer_reports.json 저장

## Part C: 프로필 페이지 개선
1. "관심 종목" 섹션 삭제 (아래 종목 탭에서 이미 보임)
2. 대신 헤더에 표시: 구독자 수 + 평균 조회수
   - Supabase channels 테이블에 subscriber_count, avg_views 확인
   - 없으면 필드 추가 방안 제시
3. 성과 요약 아래에 "AI 분석 리포트" 섹션 추가
   - 스타일 태그 배지
   - TOP3/WORST3 콜 리스트
   - 홈런 비율 바
   - 리포트 텍스트 (접이식 아코디언)
   - "분석 기준: 2026년 3월" 표시
4. 시그널 카드 클릭 → 모달에 해당 영상 조회수 표시
   - signals 또는 videos 테이블에서 view_count 확인
   - 모달: 제목 + 핵심발언 + 신호 + 수익률 + 조회수

## 주의사항
- git commit 하지 마 (공시 작업이 터미널1에서 진행 중)
- 빌드/배포 하지 마
- JSON 생성 + 코드 수정까지만

Shift+Tab Plan 모드로 시작.
