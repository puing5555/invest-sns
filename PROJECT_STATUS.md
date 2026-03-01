# PROJECT STATUS - invest-sns

## 현재 완료 (2026-03-01)

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