# 위즈덤투스 채널 추가

## 목표
투자 유튜버 "위즈덤투스" 채널을 시그널 파이프라인에 추가

## 배경
- 채널: 위즈덤투스 (`@위즈덤투스`)
- URL: https://www.youtube.com/@위즈덤투스
- 콘텐츠: 미국 주식 중심 투자 분석 (NVIDIA, Netflix, Tempus AI 등)
- 영상 50개+ 확인됨, 대부분 10~25분 길이, 조회수 1.5만~8만
- 영어 제목으로 표시되나 한국어 콘텐츠 (자막 확인 필요)

## 단계별 계획

### 1단계: 채널 등록 + 메타데이터 수집
- [ ] channel_name: "위즈덤투스", handle: "@위즈덤투스", slug: "wisdomtooth"
- [ ] yt-dlp로 영상 목록 수집 (전체)
- [ ] 필터링: Shorts 제외, 투자 관련 영상 선별
- [ ] QA Gate 1 통과 확인

### 2단계: 자막 추출 + 시그널 분석
- [ ] yt-dlp로 ko 자막 추출
- [ ] V14.0 프롬프트로 Claude Sonnet 분석
- [ ] QA Gate 2 통과 확인

### 3단계: DB 저장 + 프론트 검증
- [ ] Supabase INSERT (중복 체크)
- [ ] 신규 종목 가격 수집
- [ ] 프론트엔드 프로필 페이지 확인
- [ ] QA Gate 3 통과 확인

## 예상 결과
- 위즈덤투스 채널 시그널 DB 등록 (예상 30~50개 시그널)
- 프로필 페이지: /profile/influencer/wisdomtooth
- 총 채널 수: 11 → 12개

## 완료 기준
- [ ] QA Gate 1/2/3 전부 통과
- [ ] npm run build 성공
- [ ] 프로필 페이지 렌더링 확인

## 예상 영향 범위
| 영역 | 변경 | 유형 |
|------|------|------|
| Supabase | influencer_channels, videos, signals | INSERT |
| data/signal_prices.json | 신규 종목 가격 | 수정 |
| data/stock_tickers.json | 신규 종목 | 수정 |
| out/profile/influencer/wisdomtooth/ | 정적 페이지 | 신규 |

## 리스크
- 영어 제목이지만 한국어 콘텐츠인지 확인 필요 (자막 언어)
- Shorts/라이브 혼재 가능
