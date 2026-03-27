순서대로 실행:

=== 0. prompts/pipeline_v15.2.md 업데이트 ===
- 규칙 3 제외 대상: "비상장기업(스페이스X, 오픈AI, 두나무, 토스 등). 상장 여부 불확실하면 ticker=null"
- 규칙 6-1: "channel_type=solo여도 자막에서 2인 이상 대화 감지 시 규칙 6-3 적용. 단독 판단은 channel_type만으로 하지 말고 자막 내용도 함께 판단"
- 규칙 9 key_quote: "자막 원문에 최대한 가깝게 인용. AI가 문체를 바꾸거나 재작성 금지"
- 규칙 12 ticker: ".HK/.T/.US 접미사 금지. 같은 종목은 항상 동일 ticker 사용"
- 규칙 1 부정: "계속 추천하던 종목에 일시적 우려 표현 = 중립 (맥락 고려)"

=== 1. channel-add.md 업데이트 ===
- V14.0→V15.2 프롬프트 참조 변경
- 4단계: V15.2 + channel_info(CHANNEL_OWNER, CHANNEL_TYPE) 주입 명시
- 6단계: 스코어카드 v4 반영
  - 스윙/중기/장기 3구간, 하이브리드 fallback, EVAL_GRACE_DAYS=90
  - 통합 적중률 제거, 3구간 카드만 메인
  - TOP3/WORST3 current 기준 + 종목 중복 없음
- QA Gate 3 추가:
  - 스윙/중기/장기 카드 표시 확인
  - 탐색 카드 장기>중기>스윙 fallback + "(장기)" 표시 확인
  - 3개월 미만 회색, 3개월+ 컬러 확인
  - published_at이 영상 업로드 날짜인지 확인 (크롤링 날짜 아닌지)
- 7단계 이후: scorecard 재생성 + report 재생성(generate_influencer_report.py) 필수
- 배포: --force push 필수
- 뉴스: stock_news 테이블에 해당 종목 뉴스 자동 수집 여부 확인

=== 2. qa-checker.md 업데이트 ===
- ticker 오매핑 스캔 (.HK/.T 접미사, 비상장 종목, stock vs stockPrices name 불일치)
- ticker 정규화 (같은 종목 다른 ticker: 텐센트 0700/TCEHY 등)
- 종목 페이지 이름 누락 (숫자로만 표시되는 종목)
- 수익률 null 비율 인플루언서별 10%+ 경고
- 크립토: -USD 매핑 + CoinGecko fallback 확인
- 하이브리드 fallback 동작 확인 (1Y 없으면 3개월+ current)
- 스윙/중기/장기 건수 검증
- 탐색 카드 장기>중기>스윙 fallback 확인
- 3개월 미만 회색, 3개월+ 컬러
- 애널리스트 nid=None 중복 체크
- key_quote 20자미만/200자초과, confidence 5미만
- published_at 검증: 영상 업로드 날짜인지 전수 확인
- 크립토 채널: 동일 코인 반복 dedup 후 scored 적은 건 정상

=== 3. auto_pipeline.py 점검 ===
- V15.2 프롬프트 사용하는지 확인
- channel_info (CHANNEL_OWNER, CHANNEL_TYPE) 주입하는지 확인
- published_at이 영상 업로드 날짜로 들어가는지 확인 (크롤링 날짜 아닌지)
- 문제 있으면 수정

=== 4. 수목튜브 시그널 전체 삭제 ===
DB에서 윤수목 speaker의 시그널 + videos 전부 DELETE

=== 5. 수목튜브 처음부터 재실행 ===
python scripts/auto_pipeline.py --channel https://www.youtube.com/@soomoktube --execute

=== 6. 최종 ===
scorecard 재생성 + report 재생성 + 빌드 + --force 배포
