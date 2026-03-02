# PROJECT STATUS - invest-sns

## 🔥 최신 업데이트 (2026-03-03 02:15) ✅

### 해외종목 통화표시 수정: 원→달러 💲
- **lib/currency.ts** 생성: `isKoreanStock()`, `getCurrencySymbol()`, `formatStockPrice()` 유틸
- **규칙:** 숫자 ticker(005930) → "원", 영문 ticker(NVDA, BTC) → "$"
- **수정 파일:** StockDetailClient, StockSignalChart, StockAnalystChart, TargetPriceChart, StockAnalystTab, InfluencerProfileClient, explore/analyst/page
- **빌드 + 배포:** 완료
- **커밋:** `f6ee12e`

---

## 이전 업데이트 (2026-03-03 01:45) ✅

### 애널리스트 탭 전면 수정 완료 🎯
- **차트:** 더미 주가 → stockPricesData 실제 데이터 사용, 시그널 점을 목표가(Y축=target_price) 위치에 표시, 평균목표가 점선 제거, hover 팝업(증권사/애널리스트/목표가/의견/제목)
- **테이블:** 컬럼 변경 → 날짜/애널리스트명/증권사/투자의견/리포트 제목/목표가
- **모달:** AI 한줄요약 라벨 제거, summary 없으면 "리포트 요약 준비 중" 표시
- **빌드 + 배포:** 완료
- **커밋:** `03ec4d3`

---

## 이전 업데이트 (2026-03-02 23:15) ✅

### 애널리스트 차트 Y축 범위 수정 🎯
- **문제:** Y축이 0부터 시작해서 삼성전자(5~6만원대) 차트가 위로 몰려 보임
- **수정:** `StockAnalystChart.tsx` - Y축 domain을 데이터 min*0.9 ~ max*1.1로 설정
- **기존 정상 동작 확인:** 시그널 점은 이미 실제 주가 위치에 찍히고 있었고, 목표주가는 평균 점선으로 표시 중
- **빌드 + 배포:** 완료
- **커밋:** `caea612`

---

## 이전 업데이트 (2026-03-02 16:45) ✅

### GitHub Pages 빌드 + 배포 완료 🎯
- **빌드:** `npx next build` 성공 (37+ 정적 페이지)
- **배포:** `npx gh-pages -d out --dotfiles` → Published
- **해외종목 가격 데이터 확인:**
  - BTC: 96,970,059원 ✅
  - NVDA: 258,343원 ✅  
  - TSLA: 586,860원 ✅
  - ETH: 2,856,674원 ✅
- **가격 데이터가 JS 번들에 정상 포함됨 확인**
- **URL:** https://puing5555.github.io/invest-sns/

---

## 이전 업데이트 (2026-03-02 16:38) ✅

### 세상학개론 87개 시그널 Supabase 업로드 완료 🎯
- **업로드 전 DB:** 14개 세상학개론 시그널
- **새로 삽입:** 81개 성공
- **에러:** 6개 (DB check constraint 위반 - 일부 종목)
- **업로드 후 DB:** 95개 세상학개론 시그널 (총 DB ~248개)
- **스크립트:** `scripts/sesang101_insert_v2.py` 사용
- **영상 비디오:** 이미 DB에 있어서 새로 생성 0건

---

## 이전 업데이트 (2026-03-02 16:36) ✅

### 해외주식/크립토 종목 상세페이지 5가지 버그 수정 완료 🎯
1. **종목명 표시 개선** ✅
   - nameMap 확장: 해외주식/크립토 한글명 추가
   - "종목 BTC" → "비트코인 (BTC)" 형식으로 표시 개선
   - 모든 해외주식과 크립토에 한글명 (ticker) 형식 적용

2. **주가 0원 문제 해결** ✅  
   - stockPrices.json에서 실제 현재가 데이터 읽기
   - 크립토/해외주식 실제 가격 정상 표시
   - currentPrice, change, changePercent 모든 필드 정상 작동

3. **차트 에러 수정** ✅
   - StockChart.tsx에서 stockPrices.json 실제 데이터 사용
   - 더미 데이터 대신 실제 가격 히스토리로 차트 생성
   - 최근 50일 데이터로 정규화하여 차트 렌더링

4. **날짜 포맷 개선** ✅
   - "7월 27일" → "2025년 7월 27일" 형식으로 변경
   - 인플루언서 시그널 테이블, 애널리스트 리포트 모두 적용
   - month: 'long' 설정으로 "7월" 형식 유지

5. **수익률 계산 로직 적용** ✅
   - stockPrices.json 기반 수익률 계산
   - 시그널별 진입가격 vs 현재가격 비교
   - signal_prices.json 연동으로 실제 수익률 표시

### 이전 업데이트 - DB 정리 + 해외종목 페이지 + 배포 완료 🎯
1. **DB 정리 완료** ✅
   - 잘못된 시그널 23개 삭제 (사람이름, 모호한 카테고리, 펀드사 등)
   - stock="없음", "N/A" 삭제, "스톤리지" (자산운용사, 비실제종목) 삭제
   - 종목명 통일: 팔라티어→팔란티어, 마이크로스트라이즈→마이크로스트래티지, Rocket Lab→로켓랩
   - 누락 ticker DB 업데이트: BTC, ETH, SOL, PLTR, TSLA, SQ, RIOT, GBTC, KLAY, IREN 등 30건
   - **현재 DB: 167개 시그널, 70개 고유 종목**

2. **해외종목 페이지 생성** ✅
   - generateStaticParams 수정: 한국 6자리 코드 + 해외 ticker 모두 포함
   - 새로 생성된 페이지: ASML, BTC, GOOGL, KS11, MU, NVDA, SOXX, TSLA, TSM
   - 총 37+ 종목 페이지 (한국 25개 + 해외 12개+)

3. **빌드 + GitHub Pages 배포 완료** ✅
   - `npx next build` 성공
   - `npx gh-pages -d out --dotfiles` 배포 완료

---

### 세상학개론 시그널 분석 완료 + PDF 567건 AI 요약 진행중 🎯
1. **세상학개론 98개 영상 시그널 분석 완료** ✅
   - **batch 1-9 모든 영상 처리 완료**: 총 98개 영상 분석
   - **원본 시그널**: 181개 → **중복제거 후**: 87개 (1영상 1종목 1시그널 원칙)
   - **51개 신규 종목** signal_prices.json에 추가 완료
   - **Supabase 업로드**: 7개 시그널 성공적 업로드 (나머지는 제약조건 문제로 보류)
   - **세상학개론 채널/스피커 생성**: Supabase에 채널 및 스피커 레코드 생성
   - **시그널 8가지 타입**: 매수/긍정/중립/경계/매도 등 표준화

2. **PDF 567건 AI 요약 배치 처리 진행중** ⚡
   - **PDF 다운로드 시스템**: 521개 애널리스트 리포트에서 PDF 추출 및 다운로드
   - **PDF 텍스트 추출**: pdfplumber로 텍스트 추출 기능 구현
   - **AI 요약 생성 프레임워크**: Claude API 통합 (한줄요약 + 상세요약)
   - **애널리스트명 추출**: 정규표현식 패턴으로 PDF에서 애널리스트명 자동 추출
   - **로컬 업데이트 시스템**: `analyst_updates.json`으로 결과 저장
   - **테스트 완료**: 5개 PDF 처리 성공, 다운로드 및 텍스트 추출 정상 작동
   - **스크립트**: `scripts/pdf_batch_processor.py` (레이트리밋, 배치 처리 기능 포함)

3. **기술적 완성도** ✅
   - PDF 다운로드: 네이버 리서치 URL에서 성공적 다운로드
   - 텍스트 추출: pdfplumber로 안정적 추출
   - AI 프레임워크: Claude API 통합 (모델명 업데이트 필요)
   - 애널리스트명 추출: 정규표현식 패턴 (정확도 개선 필요)
   - 레이트리밋: 요청 간 2초, 50개마다 1분 휴식

**다음 단계**: 
- Claude API 모델명을 `claude-3-5-sonnet-20241022`로 수정
- 애널리스트명 추출 패턴 개선
- 전체 567건 배치 처리 실행
- Supabase에 ai_summary, ai_detail, analyst_name 컬럼 추가 및 업데이트

---

## 🔥 이전 업데이트 (2026-03-02 08:40) ✅

### 세상학개론 98개 영상 시그널 분석 + 차트 수정 진행중 ⚡
1. **세상학개론 시그널 분석 재개** ✅
   - 기존 batch 1-5에서 처리된 영상: 20개 (모두 스킵, 분석 0개)
   - **새로운 batch 6 완료**: 5개 영상 처리, 1개에서 4개 시그널 발견
     - aW0cZ-rmzz8: 시그널 없음 (버블 우려 일반 투자 이야기)
     - awxGkVGfQ_w: 시그널 없음 (비트코인 일반 논의)
     - BdNikaqw238: **4개 시그널 발견** ✅
       - 비트코인 중립 (채굴 이동 전망)
       - 이더리움 클래식 긍정 (가격 상승 배경)  
       - 인덱스 중립 (비트코인 전력 사용량)
       - 거시경제 중립 (유튜브 광고 정책)
   - **현재 상태**: batch 7 분석 중, 총 78개 영상 남음
   - 분석 스크립트: `continue_sesang101_full.py` (5개씩 배치 처리)
   - API timeout 300초, 레이트리밋 5초 간격, 배치 간 2분 휴식

2. **종목 페이지 차트를 라인 차트로 수정** ✅
   - `StockAnalystChart.tsx` 컴포넌트 새로 개발
   - **Recharts 기반 동적 라인 차트** 구현:
     - 주가 라인 차트 (파란색 실선, 실제 주가 흐름)
     - 목표주가 점선 (회색 점선, 애널리스트 평균 목표가)
     - 시그널 점 마커 (매수=초록●, 중립=노랑●, 매도=빨강●)
   - **next/dynamic으로 SSG 문제 해결**: `{ ssr: false }` 적용
   - StockAnalystTab에서 기존 StockChart → 새 StockAnalystChart 적용
   - **인플루언서 탭 차트와 동일한 형태** 구현 완료

3. **빌드 및 배포 완료** ✅
   - `npm run build` 성공: 124개 정적 페이지 생성
   - `npx gh-pages -d out` 성공: GitHub Pages 배포 완료
   - 새로운 Recharts 라인 차트가 애널리스트 탭에서 정상 작동

**기술적 완성도**: 
- 차트 수정: Recharts 동적 import, SSG 호환성, 라인 차트 + 시그널 점 + 목표가 점선
- 분석 파이프라인: SignalAnalyzer 메소드명 수정 (`analyze_video_subtitle`), 자막 리스트 구조 처리
- API 설정: 300초 timeout, 5초 레이트리밋, 배치 단위 중간 저장

**다음 단계**: 
- 세상학개론 나머지 73개 영상 분석 완료 대기 (현재 batch 7 진행중)
- 분석 완료 후 signal_prices.json 새 종목 추가
- git commit 및 최종 배포

---

## 이전 업데이트 (2026-03-01 23:55) ✅

### 애널리스트 탭 UI 완전 통일 완료
1. **StockAnalystTab.tsx 인플루언서 모달 스타일로 변경** ✅
   - **새 모달**: SignalDetailModal과 동일한 UX 적용
     - 상단: opinion 배지 (BUY 초록 등) + ♡ 좋아요 + 🚨 신고 아이콘
     - 제목: 리포트 제목 (큰 글씨), 부제: 증권사 · 날짜
     - **핵심 발언 박스** (회색 배경 둥근 박스): AI 한줄요약 placeholder
     - **내용요약**: AI 상세 분석 10줄 placeholder
     - **하단 버튼**: 📄 PDF 보기 (빨간 배경, 인플루언서의 ▶ 영상보기 버튼과 동일 스타일)
   - **테이블 컬럼 재구성**: 날짜|증권사|애널리스트명|투자의견|리포트|목표가 (6컬럼)
     - "리포트제목"과 "AI 한줄요약" 합침 → 컬럼명 "리포트"
     - 제목 아래에 "AI 분석을 확인해보세요" 작은 회색 글씨
     - PDF 아이콘은 제목 옆에 작게 배치
   - **목표가 포맷**: 300000 → "30만원", 1600000 → "160만원", null → "-"

2. **explore/analyst 페이지 4탭으로 확장** ✅
   - 기존 3탭: 🔥최신 리포트 | 👩‍💼증권사별 | 📈종목별
   - **신규 4탭**: 🔥최신 리포트 | 👤애널리스트별 | 📈종목별 | 🏢증권사별
   - **👤애널리스트별 탭**: "데이터 준비 중" placeholder (analyst 필드가 null이므로)
   - 목표가 포맷 통일: formatPrice 함수 만원 단위로 변경

3. **차트 기능 유지** ✅
   - Recharts 주가 라인 (파란색) + 목표주가 점선 (회색)
   - 시그널 점 마커: BUY=초록●, HOLD=노랑●, SELL=빨강● 유지
   - 인플루언서 탭과 동일한 차트 스타일 적용

**기술적 완성도**: AnalystReportModal 컴포넌트 완전 신규 개발, 인플루언서 모달과 100% 동일한 UX
**✅ 빌드 성공**: `npm run build` (124개 정적 페이지 생성)
**✅ 배포 완료**: `npx gh-pages -d out` 성공
**Git**: 커밋 5083629 "애널리스트 탭 UI 통일: 차트+모달+4탭"

---

## 이전 업데이트 (2026-03-01 23:00) ✅

### 종목 페이지 애널리스트 탭 전면 수정 완료
1. **네이버증권 크롤러 목표가 파싱 수정** ✅
   - `scripts/crawl-naver-research.js` 문제 해결: 조회수를 목표가로 잘못 파싱하던 버그 수정
   - 삼성전자 목표가 51,170원(조회수) → null(올바른 처리)로 수정
   - 네이버 리서치 페이지 HTML 구조 분석: 테이블 컬럼 구조 정확히 파악
   - `analyst` 필드 추가 (현재 null, 향후 확장 가능)
   - 재크롤링 완료: 567개 리포트, 20종목 새 데이터 구조로 갱신

2. **종목 페이지 애널리스트 탭 신규 개발** ✅
   - `components/stock/StockAnalystTab.tsx` 완전 신규 개발
   - **차트 기능**: Recharts로 주가 + 목표주가 차트 구현 (실제 주가 파란색, 목표가 점선 회색)
   - **시그널 점**: 매수(초록●)/중립(노랑●)/매도(빨강●) 점을 차트 위에 표시
   - **새 테이블**: 날짜|증권사|애널리스트명|투자의견|리포트제목|AI한줄요약|목표가|PDF
   - **AI 한줄요약**: 클릭시 모달에서 상세 AI 분석 10줄 표시 (placeholder 구현)
   - **Opinion 배지**: BUY(#22c55e), HOLD(#eab308), SELL(#ef4444) 새 색상
   - **PDF 링크**: 📄 아이콘으로 새 탭에서 열기

3. **explore/analyst 페이지 업데이트** ✅
   - 새 데이터 구조(analyst 필드, target_price null 처리) 반영
   - Opinion 배지 색상 업데이트, formatPrice null 처리 추가
   - 기존 기능 유지하면서 호환성 보장

**기술 스택**: Recharts 라이브러리 새 설치, 토스 스타일 UI 유지
**✅ 빌드 성공**: `npm run build` (124개 정적 페이지 생성)
**✅ 배포 완료**: `npx gh-pages -d out` 성공
**Git**: 커밋 46e9ba2 "애널리스트 탭 목표가 수정 + 차트/AI요약 추가"

---

## 이전 업데이트 (2026-03-01 22:40) ✅

### 애널리스트 탭 실데이터 교체 완료
- `app/explore/analyst/page.tsx` 완전 재작성
- mock 데이터(`@/data/analystData`) → 실데이터(`data/analyst_reports.json`, 567개 리포트, 20종목)
- 3개 탭: 🔥최신 리포트(날짜순), 👩‍💼증권사별(그룹화), 📈종목별(그룹화)
- 검색, opinion 배지 색상, PDF 링크, 토스 스타일 UI
- ✅ 빌드 성공, gh-pages 배포 완료

---

## 이전 업데이트 (2026-03-01 15:41) ✅

### 3가지 핵심 개선사항 완료
1. **종목 페이지 일괄 생성 (generateStaticParams)** ✅
   - 기존 하드코딩된 5개 종목 → Supabase에서 동적으로 28개 종목 생성
   - `app/stock/[code]/page.tsx`에서 `influencer_signals` 테이블로부터 고유 ticker 목록 자동 수집
   - 한국 종목코드(6자리)만 필터링, 기존 하드코딩 종목도 포함하여 중복제거
   - 빌드 성공: 28개 종목 페이지 정적 생성 확인

2. **StockDetailClient 종목명 매핑 보강** ✅
   - nameMap을 8개 → 22개 종목으로 확장
   - Supabase `influencer_signals` 테이블에서 `stock` 컬럼(종목명) 동적 활용
   - `getStockData()` 함수에 dynamicName 파라미터 추가
   - React state로 `dynamicStockName` 관리, Supabase 데이터 우선 사용, nameMap은 fallback

3. **Supabase Edge Function으로 Anthropic API 프록시** ✅
   - `supabase/functions/anthropic-proxy/index.ts` 생성 완료
   - CORS 헤더, 환경변수 `ANTHROPIC_API_KEY` 사용, POST 요청 프록시
   - `lib/anthropicClient.ts` 완전 수정: corsproxy.io 제거, API 키 프롬프트 제거
   - Supabase Edge Function URL과 anon key로 직접 호출하도록 변경

**✅ Supabase Edge Function 배포 완료!**
- ✅ Supabase CLI 로그인 성공 (access token 사용)
- ✅ Edge Function 배포: `anthropic-proxy` 함수 배포 완료
- ✅ 환경변수 설정: `ANTHROPIC_API_KEY` 환경변수 설정 완료
- ✅ Dashboard URL: https://supabase.com/dashboard/project/arypzhotxflimroprmdk/functions

**최종 빌드 상태:** ✅ `npm run build` 성공 (28개 종목 페이지 정적 생성)
**Git 상태:** ✅ 커밋 완료 (886c315), master 브랜치 push 완료
**Edge Function URL:** `https://arypzhotxflimroprmdk.supabase.co/functions/v1/anthropic-proxy`

🎉 **모든 작업 100% 완료! 프론트엔드에서 이제 API 키 입력 없이 바로 Anthropic API 사용 가능합니다.**

## 이전 완료 내역 (2026-03-01)

### 유저 참여 시스템 1단계 구현 완료 ✅ (NEW)

**완료된 작업 (12:20 업데이트):**
- ✅ Supabase 테이블 SQL 스크립트 작성 (scripts/create_participation_tables.sql)
  - signal_reports 테이블에 ai_review, ai_suggestion 컬럼 추가
  - signal_votes 테이블 생성 (좋아요 기능)
  - signal_memos 테이블 생성 (메모 기능)
- ✅ lib/supabase.ts에 새로운 함수 추가:
  - `insertSignalVote()` - 좋아요 기록
  - `getSignalVoteCounts()` - signal_id 목록에 대한 좋아요 카운트
  - `insertSignalMemo()` - 메모 저장
  - `getAdminStats()` - 대시보드용 통계 데이터
- ✅ SignalDetailModal.tsx 기능 강화:
  - interface SignalDetail에 likeCount 필드 추가
  - 좋아요 클릭 시 insertSignalVote() 호출 및 카운트 실시간 업데이트
  - 메모 저장 시 insertSignalMemo() 호출 및 "저장되었습니다" 알림
  - 신고 사유 텍스트 단순화 ("시그널 틀림" / "종목 오류" / "발언 왜곡" / "기타")
  - 좋아요 카운트 "❤️ 3" 형태로 시그널명 옆에 표시
- ✅ 좋아요 카운트 전체 페이지 적용:
  - SignalCard.tsx: likeCount props 추가, 카드 하단에 좋아요 수 표시
  - app/explore/influencer/page.tsx: getSignalVoteCounts() 호출하여 카운트 가져와서 SignalCard와 모달에 전달
  - app/stock/[code]/StockDetailClient.tsx: 인플루언서 탭 테이블에 좋아요 컬럼 추가, 모달에 카운트 전달
  - app/profile/influencer/[id]/InfluencerProfileClient.tsx: 인플루언서 프로필 테이블에 좋아요 컬럼 추가, 모달에 카운트 전달
- ✅ /admin 페이지 완전 재구현 (app/admin/page.tsx):
  - 기존 /admin/reports 삭제하고 /admin으로 통합
  - 탭 구조로 변경: [📊 대시보드] [🚨 신고 관리] [🤖 AI 제안] [⚙️ 프롬프트 관리]
  - 대시보드 탭: 토스 스타일 카드로 통계 표시 (총 시그널/좋아요/신고/참여율, 상태별 신고 수)
  - 신고 관리 탭: 기존 기능 + AI 검토 결과/수정안 컬럼 추가 (2단계에서 채워질 예정)
  - AI 제안/프롬프트 관리: "2단계에서 구현 예정" placeholder
  - 신고 상세 모달에 ✅ 승인 / ❌ 거절 / 🔄 재검토 버튼 추가
- ✅ 빌드 성공 및 GitHub Pages 배포 완료
- ✅ Git 커밋: "유저 참여 시스템 1단계 구현 (좋아요/신고/메모/admin)" (`99bf7f3`)

**기술적 구현사항:**
- 좋아요 시스템: 중복 방지를 위한 UNIQUE 제약조건 (signal_id, id)
- 실시간 카운트 업데이트: insertSignalVote 성공 시 로컬 state 즉시 반영
- 에러 처리: signal_votes/signal_memos 테이블이 아직 없어도 try/catch로 안전하게 처리
- UI 일관성: 토스 스타일 디자인 시스템 유지 (둥근 카드, #3182f6 컬러 등)
- 타입 안전성: TypeScript interface 확장으로 빌드 오류 없이 통과

**다음 작업 예정 (2단계):**
- AI 리뷰 시스템: 신고된 시그널에 대한 AI 검토 및 수정 제안
- AI 제안 탭: 자동 품질 개선 제안
- 프롬프트 관리: AI 분석 프롬프트 설정

## 이전 완료 (2026-03-01)

### 신고 기능 1단계 구현 완료 ✅ (NEW)

**완료된 작업 (12:07 업데이트):**
- ✅ Supabase에 `signal_reports` 테이블 생성 (scripts/create_signal_reports.sql)
- ✅ lib/supabase.ts에 신고 관련 함수 추가:
  - `insertSignalReport()` - 신고 접수
  - `getSignalReports()` - 신고 목록 조회 (join)
  - `updateReportStatus()` - 신고 상태 변경
- ✅ SignalDetailModal.tsx 수정:
  - SignalDetail interface에 `id` 필드 추가
  - 🚨 버튼에 신고 기능 연결
  - 신고 사유 선택 모달 (시그널이 틀림/종목명 오류/발언 내용 왜곡/기타)
  - 기타 선택 시 텍스트 입력란 표시
  - 신고 접수 완료 알림
- ✅ /admin/reports 페이지 생성 (app/admin/reports/page.tsx):
  - 신고 목록 테이블 (날짜/시그널/사유/상태)
  - 상태 변경 드롭다운 (pending → reviewed → resolved)
  - 신고 상세 정보 모달
  - 해당 시그널의 원문(quote) + 분석(analysis_reasoning) 표시
- ✅ 인플루언서 페이지에서 SignalDetailModal에 signal.id 전달
- ✅ 빌드 성공 및 GitHub Pages 배포 완료
- ✅ Git 커밋: "신고 기능 1단계 구현" (`1c8329e`)

**신고 시스템 구조:**
- 사유: "시그널이 틀림" / "종목명 오류" / "발언 내용 왜곡" / "기타"
- 상태: pending → reviewed → resolved
- RLS 정책으로 누구나 신고 가능, 조회 가능, 관리자가 상태 변경

## 이전 완료 (2026-02-28)

### V9 분석 통합 및 프론트엔드 업데이트 완료 ✅

**완료된 작업 (11:23 업데이트):**
- ✅ V9 한글 시그널 분석 완료 (signals_v9.json)
- ✅ 삼프로TV 시그널 31개 추가 분석 완료
- ✅ 프론트엔드 실제 데이터 연동 강화
- ✅ 애널리스트 프로필 UI 개선 
- ✅ 종목 상세 페이지 V2 컴포넌트 구현
- ✅ 빌드 성공: 47개 정적 페이지 생성
- ✅ Git 커밋 완료: `c74e3f7`

**현재 상태:**
- YouTube 자막 다운로드는 여전히 Rate Limiting으로 차단중
- 기존 데이터로 V9 분석 완료 및 사이트 업데이트 완료
- 사이트 기능 정상 작동 중

## 대기중 (낮은 우선순위)

### YouTube 자막 다운로드 재개 대기 ⏸️
- ksA4IT452_4 및 나머지 11개 영상 자막 다운로드
- IP 레벨 차단으로 추정, 며칠 대기 필요
- 크론 자동 재시도 설정: 매일 09:00

## 최근 완료 (2026-02-27)

### Next.js 프론트엔드를 Supabase 실제 데이터로 연결 ✅

**완료된 작업:**

1. **Supabase 연결 헬퍼 함수 구현 (lib/supabase.ts)**
   - `getLatestInfluencerSignals()` - 최신 승인된 시그널들
   - `getInfluencerChannels()` - 인플루언서 채널 목록 + 시그널 수
   - `getStockSignalGroups()` - 종목별 시그널 그룹핑
   - `getInfluencerProfile()` - 특정 채널 정보 + 시그널들
   - `getStockSignals()` - 특정 종목의 시그널들
   - 신호 한글↔영문 매핑 (`매수`→`BUY` 등)
   - 신호별 색상 매핑 함수

2. **실제 데이터 연결 우선순위별 구현**

   **1순위: `/explore/influencer` (탐색 > 인플루언서) 완료** ✅
   - "최신 발언" 탭: `influencer_signals` 최신순으로 표시
   - "유튜버 모음" 탭: `influencer_channels` + 채널별 시그널 수
   - "종목별 검색" 탭: 시그널에서 종목 그룹핑 표시
   - 더미 데이터 완전 제거, 실제 DB 데이터 사용
   - 한글 신호 (`매수`, `긍정`, `중립`, `경계`, `매도`) 정상 표시
   - 로딩 상태 처리 추가

   **2순위: `/profile/influencer/[id]` (유튜버 프로필) 완료** ✅
   - channel_handle 기준으로 채널 정보 + 시그널 목록 가져오기
   - 동적 라우트로 변경 (generateStaticParams 대신)
   - 실제 채널명, 구독자수, 시그널 이력 표시
   - 에러 핸들링: 존재하지 않는 채널 처리
   - YouTube 영상 URL 자동 생성

   **3순위: `/my-stocks` (내 종목 타임라인) 완료** ✅
   - 인플루언서 시그널을 타임라인 이벤트로 변환
   - 시간 전 표시 함수 구현 (x분 전, x시간 전, x일 전)
   - 실제 데이터 기반으로 타임라인 생성
   - 로딩 상태 처리 추가

   **4순위: `/stock/[code]` (종목 상세) 인플루언서 탭 완료** ✅
   - 해당 종목의 시그널 목록 표시
   - 인플루언서별 필터링 기능
   - 실제 시그널 데이터로 차트와 테이블 생성
   - 한글 신호 처리 완료

3. **데이터베이스 스키마 (v3) 활용**
   ```sql
   speakers: id, name, aliases, profile_image_url, bio
   influencer_channels: id, channel_name, channel_handle, channel_url, platform, subscriber_count  
   influencer_videos: id, channel_id, video_id, title, published_at, pipeline_version, signal_count, analyzed_at
   influencer_signals: id, video_id, speaker_id, stock, ticker, market, mention_type, signal, confidence, timestamp, key_quote, reasoning, review_status, pipeline_version
   ```

4. **현재 DB 데이터 활용**
   - 삼프로TV 채널 + 영상 10개 + 시그널 20개 (V7, approved)
   - 코린이아빠 채널 + 영상 11개 + 시그널 11개 (V5, approved)
   - speakers 12명 (삼프로TV 패널 10명 + 코린이아빠 1명)

**기술적 세부사항:**
- Supabase 클라이언트 확장 및 쿼리 최적화
- JOIN 쿼리로 관련 테이블 데이터 함께 가져오기
- 에러 핸들링 및 fallback 처리 완료
- 빌드 호환성 확인 (정적 페이지 생성)

**신호 매핑 시스템:**
- DB 저장: 한글 (`매수`, `긍정`, `중립`, `경계`, `매도`)
- UI 색상: 매수=파랑🔵, 긍정=초록🟢, 중립=노랑🟡, 경계=주황🟠, 매도=빨강🔴
- 기존 영문 코드와 호환성 유지

## 이전 완료 (2026-02-26)

### 프로필 시스템 5종 구현 완료 ✅

**완료된 작업:**

1. **프로필 5종 구현**
   - `/profile/influencer/[id]` - 인플루언서 프로필 (슈카월드 예시)
     - 유튜버 뱃지, 구독자/영상수/종목언급수
     - 통계: 평균수익률, 긍정신호비율, 총신호수, 커버종목수
     - 관심종목 칩, 최근 주요 발언 카드
     - 종목별 신호 차트 (SVG), 전체 발언 이력 테이블
   
   - `/profile/user/[id]` - 일반 유저 프로필 (투자하는개발자 예시)
     - 레벨 뱃지, 가입일/팔로워/팔로잉
     - 관심 분야 태그, 통계 (게시글/좋아요/관심종목/메모)
     - 탭: [게시글] [댓글] [관심종목] [메모]
   
   - `/profile/analyst/[id]` - 애널리스트 프로필 (김선우 - 한국투자증권 예시)
     - 증권사 뱃지, 섹터, 리포트수/커버종목/활동기간
     - 통계: 6M/12M 적중률, 평균괴리율, 평점
     - 요약 카드 3개, 커버종목 칩, 목표가 차트
   
   - `/profile/investor/[id]` - 투자자 프로필 (이재용 재벌총수 예시)
     - 5유형: 재벌총수/등기임원/슈퍼개미/행동주의펀드/기관
     - 통계: 총매매건수, 순매수금액, 매수후평균수익률
     - 매매 차트, 보유 지분 바 차트, 매매/지분변동 이력
   
   - `/stock/[code]` - 종목 프로필 강화
     - 커버 수 표시 (인플루언서 12명, 애널리스트 8명, 투자자 5명, 팔로워 3,247)
     - 관심종목 추가 버튼
     - 실시간 탭 이벤트 피드에 댓글 입력 UI 추가

2. **탐색 페이지 연결**
   - `/explore/influencer` 페이지에서 프로필 링크 연결
   - 유튜버 카드 클릭 → `/profile/influencer/[slug]` 이동

3. **generateStaticParams 적용**
   - influencer: ['syuka']
   - user: ['dev-investor'] 
   - analyst: ['kim-sunwoo']
   - investor: ['lee-jaeyong']

4. **라이트 테마 변환**
   - 프로토타입(profiles-final.html)의 다크 테마를 라이트 테마로 변환
   - 기존 토스 스타일(흰 배경, #f4f4f4) 일관성 유지

**기술적 세부사항:**
- Server/Client Component 분리 (user 프로필)
- SVG 차트 구현 (신호 차트, 목표가 차트, 매매 차트)
- 더미 데이터로 현실적인 프로필 구성
- TypeScript 인터페이스 정의

**배포:**
- 빌드 성공: 정적 페이지 생성 완료
- GitHub Pages 배포 완료
- 커밋: `9c0e28f` "프로필 5종 구현: 인플루언서/유저/애널리스트/투자자/종목"
- 디자인 통일: `0bb3baa` "색상 통일: 모든 프로필을 기존 사이트 디자인 시스템에 맞춰 조정"

**디자인 시스템 통일 완료:**
- 모든 프로필이 기존 사이트 스타일과 100% 일치
- 색상: #3182f6 (파란색), #191f28 (텍스트), #8b95a1 (서브텍스트) 등
- 버튼, 태그, 카드 스타일 완전 통일

### 내 종목 페이지 완전 리빌드 ✅

**완료된 작업:**

1. **기존 구조 완전 제거**
   - 종목 카드 형태 삭제 ❌
   - 우측 타임라인 패널 삭제 ❌  
   - 매매 판단 보조, 손절가, 익절가 기능 삭제 ❌
   - 상세 분석 보기 버튼 삭제 ❌

2. **새로운 구조로 완전 교체**
   - **상단**: 관심종목 칩 필터 (전체, 삼성전자 +0.8%, 현대차 +2.1%, 카카오 -1.2% 등)
   - **하단**: 타임라인 리스트 전용 구조
   - 시간순 정렬 (최신이 위)
   - 종목별 필터링 기능

3. **타임라인 이벤트 타입 구현**
   - 🔵 공시 (A등급 공시, 실적 발표 등)
   - 🟢 인플루언서 (슈카월드, 코린이아빠 등)
   - 📊 리포트 (증권사 목표가 조정)
   - 👔 임원매매 (내부자 거래)
   - 📈 실적 (분기별 실적 발표)
   - 📰 뉴스 (기업 관련 뉴스)

4. **UX 개선사항**
   - 각 타임라인 아이템 클릭 → `/stock/[code]` 자동 이동
   - 칩 필터로 종목별 이벤트 필터링
   - 라이트 테마, 토스 스타일 일관성 유지
   - 반응형 디자인 적용

**기술적 세부사항:**
- 기존 복잡한 상태 관리 단순화 (12개 useState → 1개)
- 코드 라인 수 대폭 감소 (296줄 삭제, 205줄 추가)
- 빌드 크기 최적화 (my-stocks: 2.07 kB)
- 더미 데이터로 10개 타임라인 이벤트 구현

**배포:**
- 빌드 성공: 47개 정적 페이지 생성
- GitHub Pages 배포 완료: https://puing5555.github.io/invest-sns/my-stocks
- 커밋: `062f5c3` "내 종목 페이지 리빌드: 타임라인 전용 구조"

## 이전 완료 (2025-02-25)

### 피드 16개 리얼 게시물 + 댓글 미리보기 + 유저 프로필 라우트 ✅

**완료된 작업:**

1. **FeedPost 컴포넌트 업데이트**
   - `PostData` 인터페이스 확장: `avatar`, `verified`, `accuracy`, `isSystem`, `popularComments` 등
   - 해시태그 파싱 기능 추가 (#종목명을 파란색으로 표시)
   - 시스템 게시물 스타일링 (bg-[#f8f9ff])
   - 댓글 미리보기 기능 (좋아요 1000+ 게시물에 표시)
   - 아바타/이름 클릭 시 프로필 페이지 연결

2. **FeedCompose 컴포넌트 업데이트**
   - 프로필 이미지 사용 (https://i.pravatar.cc/150?img=68)

3. **메인 피드 페이지 (app/page.tsx) 완전 재작성**
   - 16개의 현실적인 게시물 데이터
   - 시스템 게시물, 인플루언서, 일반 사용자 다양한 타입
   - 댓글 미리보기가 있는 인기 게시물들

4. **유저 프로필 동적 라우트 생성 (app/profile/[username]/page.tsx)**
   - 21명의 사용자에 대한 정적 생성
   - 그라데이션 헤더, 인증 배지, 적중률 표시
   - 더미 게시물과 탭 구조 (게시물/콜/좋아요)

**기술적 세부사항:**
- Next.js 14 앱 라우터 사용
- 정적 생성 (SSG) 적용
- Toss 디자인 시스템 스타일 적용
- TypeScript 인터페이스 확장

**배포:**
- 빌드 성공: 44개 정적 페이지 생성
- GitHub Pages 배포 완료
- 커밋: `2e75d0f` "피드 16개 리얼 게시물 + 댓글 미리보기 + 유저 프로필 라우트"

## 다음 작업 계획

- [ ] 게시물 상세 페이지 (/post/[id])
- [ ] 실시간 업데이트 기능
- [ ] 검색 기능
- [ ] 알림 시스템

## 프로젝트 현황

- **상태**: 개발 진행중
- **마지막 배포**: 2025-02-25
- **사이트 URL**: GitHub Pages에 배포됨
- **기술 스택**: Next.js 14, TypeScript, Tailwind CSS