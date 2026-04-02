# invest-sns

## Purpose
한국 주식 유튜버/인플루언서의 종목 시그널을 AI로 자동 수집·분석하고,
증권사 애널리스트 리포트의 적중률/수익률을 추적하여
개인투자자에게 신뢰도 기반 투자 정보를 제공하는 플랫폼.

사이트: https://puing5555.github.io/invest-sns/

## Stack
- Frontend: Next.js 14 + Tailwind (Static Export → GitHub Pages)
- Backend: Supabase (PostgreSQL + Auth + Storage)
- AI: Claude Sonnet (`claude-sonnet-4-20250514`) — 시그널 분석, 리포트 AI 요약
- Data: yt-dlp (자막), Yahoo Finance / 네이버금융 (가격), 네이버 리서치 (애널리스트 리포트)
- Deploy: GitHub Pages (gh-pages branch, orphan 방식)

## Repo Map
- `app/` → 페이지 (Next.js App Router)
  - `app/explore/analyst/` → 애널리스트 리포트 (최신/종목별/애널리스트별)
  - `app/stock/[code]/` → 종목 상세 페이지
  - `app/profile/` → 인플루언서/애널리스트 프로필
- `components/` → 공통 컴포넌트 (ReportDetailModal 등)
- `lib/` → 유틸리티 (Supabase client, API helpers)
- `scripts/` → 데이터 파이프라인, 크롤러
  - `scripts/crawl-naver-research-v2.js` → 애널리스트 리포트 3년치 크롤러
  - `scripts/calc_analyst_returns.py` → forward return 계산 (yfinance)
  - `scripts/anyuhwa/step5_pipeline.py` → 인플루언서 시그널 파이프라인
- `data/` → JSON 데이터
  - `data/analyst_reports.json` → 애널리스트 리포트 (45종목, 3년치)
  - `data/stockPrices.json` → 종목 가격 (5년치)
- `prompts/pipeline_v14.0.md` → 인플루언서 시그널 분석 프롬프트 (운영)
- `docs/` → 아키텍처, 스펙 문서
  - `docs/RETURNS_SPEC.md` — ⚠️ 수익률/날짜 처리 필수 규칙
- `.claude/` → 자동화 시스템 (skills, hooks, tasks)

## 핵심 시스템

### 1. 인플루언서 시그널 (기존)
- 11개 채널, 1,133개 시그널, 70+ speakers
- 파이프라인: step1_collect → step2_filter → step5_pipeline (자막추출→Claude분석→DB→수익률)
- Eval 정확도: 73.9% (V14.0 프롬프트, 69건 기준)

### 2. 애널리스트 리포트 (신규)
- 45종목, 3년치 네이버 리서치 크롤링
- 수집 필드: 종목, 증권사, 애널리스트, 목표가, 투자의견, 제목, PDF 링크
- 수익률: forward return 3개월/6개월/12개월 (yfinance)
- 기본 정렬: 12개월 수익률
- 컨센서스: 최근 3개월 리포트 기준

## Rules (절대)
1. API 키 소스코드 하드코딩 금지 → .env.local만
2. 배포 전 체크리스트 필수 통과 (.claude/skills/deploy.md)
3. 채널 추가 시 7단계 파이프라인 필수 (.claude/skills/channel-add.md)
4. QA Gate 실패 시 다음 단계 진행 금지
5. 시그널 재분석(Sonnet)은 JAY 승인 없이 실행 금지
6. 크롤링 날짜를 published_at으로 사용 금지
7. 모델 변경 시 전체 파일 grep으로 구버전 제거
8. 프론트엔드 수정 후 반드시 `npm run build` 성공 확인
9. 큰 작업(새 기능, 시스템 변경, 크롤링 확장 등) 시작 시 `.claude/tasks/`에 작업별 폴더 생성하고 plan/context/checklist 3개 문서 작성 필수
10. 작업 계획은 승인 전 실행 금지
11. 작업은 1~2단계 단위로 진행하고, 단계 완료 시 checklist 업데이트
12. 프롬프트 수정 시 eval 69건 필수 실행, 정확도 비교 결과 보고
13. 커밋 메시지 한글로, 변경 내용 구체적으로 (예: "수정" ✕ → "V14.0 운영 반영 + eval 73.9%" ○)
14. 작업 완료 시 보고 필수: (1) 뭘 했는지 (2) 수정된 파일 (3) 판단 근거
15. "이어서" 입력 시 자동으로: (1) `.claude/tasks/` 폴더의 진행중 작업 확인 (2) 가장 최근 핸드오프 문서 읽기 (3) 현재 상태 요약 보고 (4) 다음 작업 제안
16. "마무리" 또는 "체크포인트" 입력 시 자동으로: (1) `.claude/tasks/` 진행중 작업 상태 확인 (2) 마지막 체크포인트 이후 커밋 수집 (3) 핸드오프 문서 생성 (기존 Part 시리즈 형식) (4) 진행중 배치 작업 상태 포함 (5) 미완료 작업 우선순위 정리
17. 새 채널/시그널 추가 후 반드시 `python scripts/qa/gate4_ticker_check.py` 실행하여 ticker 누락 검증
18. 새 채널 dry-run 시 반드시 3가지 수치 보고: (1) 투자 키워드 필터 통과 건수 (2) --stock-filter 통과 건수 (종목명 포함) (3) 비율 (stock/키워드). 비율 20% 이하 → --stock-filter 권장, 50% 이상 → --execute 권장, 20~50% → JAY 판단
19. 새 채널 파이프라인 완료 후 `python scripts/qa/gate5_name_check.py --channel 채널명` 필수 실행하여 ticker↔종목명 일치 검증

## .claude/ 자동화 시스템

### skills/ (상황별 참조 문서)
- `index.md` — 상황→skill 매핑 목차
- `frontend.md` — Next.js/Tailwind 컨벤션, 시그널 색상, 레이아웃
- `supabase.md` — DB 테이블 15개+ 스키마, RPC, Edge Function
- `crawling.md` — 네이버 크롤러, yfinance 수익률, 프록시
- `eval.md` — 69건 정답지, 3그룹 분석법, eval 프로세스
- `prompt.md` — V14.0 핵심 규칙, 프롬프트 수정 절차
- `analyst-report.md` — 리포트 데이터 구조, 종목 추가
- `channel-add.md` — 인플루언서 채널 추가 7단계 파이프라인
- `deploy.md` — 배포 체크리스트, gh-pages push

### hooks/ (자동 트리거)
- **PreToolUse**: 파일 경로 기반 관련 skill 자동 안내 (app/→frontend, scripts/crawl→crawling 등)
- **PostToolUse**: .py 구문 검증 (py_compile) + .ts/.tsx 빌드 안내

### tasks/ (작업 기억)
- 큰 작업 시 작업별 폴더 생성 → plan/context/checklist 3개 문서
- 템플릿: `.claude/tasks/_templates/`
- 사용법: `.claude/tasks/README.md`

## Commands
- `npm run build` → Static export (out/)
- `npm run dev` → 로컬 개발 서버
- `node scripts/crawl-naver-research-v2.js` → 애널리스트 리포트 크롤링
- `node scripts/crawl-naver-research-v2.js --resume` → 이어서 크롤링
- `python scripts/calc_analyst_returns.py` → forward return 계산
- `python scripts/qa/run_all_gates.py` → QA 전체 실행

## 현재 상태 (2026-03-15)
- 인플루언서 시그널: 1,133개 (11개 채널)
- 애널리스트 리포트: 크롤링 진행 중 (45종목 3년치)
- 기존 타임스탬프 1,000+개 재분석 필요
- 탭 구조 변경 예정 (TODAY/SNS/탐색/포트폴리오/프로필)

## 작업 규칙
1. 모든 작업은 Plan 모드로 시작 (shift+tab). 계획 승인 후 실행.
2. 한 커밋에 5개 이상 파일 변경 시 반드시 Plan 모드.
3. 작업 완료 후 자기 검증:
   - npm run build 성공 필수
   - 삼성전자(005930) + BTC + AAPL 종목 페이지 빌드 정상
   - 새 컴포넌트 import 시 dynamic import + 에러 바운더리
   - optional chaining (?.) 필수
4. 크래시 방지:
   - 새 탭/컴포넌트 추가 시 데이터 없는 종목에서도 테스트
   - 미국/크립토에 한국 전용 기능 접근 시 fallback 필수
5. 빌드 안 하고 배포 절대 금지

## 실수 기록
- StockDisclosureTab dynamic import 누락으로 전체 종목 크래시 (2026-03-20)
- mt-1.5 Tailwind purge 문제 (2026-03-20)
