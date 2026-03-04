# 공시 AI 분석 시스템 — Phase 1 기술 스펙

> 기준: `disclosure_spec_v6.txt` | 작성: 2026-03-04 | 환경: Next.js static export + Supabase

---

## 0. 현재 프로젝트 구조 요약

```
app/
  explore/disclosure/page.tsx    ← 공시 대시보드 (탭 4개: 실시간/하이라이트/실적시즌/DB)
  stock/[code]/page.tsx          ← 종목 상세
components/
  disclosure/                    ← RealTimeFeedTab, HighlightsTab, EarningsSeasonTab, DisclosureSearchTab
  stock/                         ← StockAnalystTab, StockDisclosureTab
```

**현재 상태**: 모든 컴포넌트가 **더미 데이터** 사용. Supabase 연동 없음.

**제약**:
- Next.js static export → `getServerSideProps` 불가, 클라이언트에서 Supabase 직접 호출
- GitHub Pages 호스팅 → API route 없음 (Edge Function으로 대체)

---

## 1. DB 스키마 설계

### 1-1. `disclosures` (공시 원본 + AI 분석)

```sql
CREATE TABLE disclosures (
  id              BIGSERIAL PRIMARY KEY,
  rcept_no        VARCHAR(20) UNIQUE,           -- DART 접수번호 (Phase2), AWAKE에선 null 가능
  corp_code       VARCHAR(10),                  -- 기업 고유코드
  corp_name       VARCHAR(100) NOT NULL,
  stock_code      VARCHAR(10) NOT NULL,         -- 종목코드 (6자리)
  report_nm       VARCHAR(500) NOT NULL,        -- 보고서명 원문
  rcept_dt        DATE NOT NULL,                -- 접수일
  rcept_time      TIME,                         -- 접수시간 (15~17시 판단용)
  
  -- 분류
  disclosure_type VARCHAR(50) NOT NULL,         -- CB발행, 실적, 자사주소각, 풍문해명, 수주 등
  sub_condition   VARCHAR(100),                 -- 사모_시총10%+, 흑자전환 등 (27개)
  grade           CHAR(1) NOT NULL CHECK (grade IN ('A','B','C','D')),
  direction       VARCHAR(10) NOT NULL CHECK (direction IN ('bullish','bearish','neutral')),
  
  -- 기업 메타
  market_cap      BIGINT,                       -- 시가총액 (원)
  sector          VARCHAR(50),
  
  -- 파싱된 핵심 수치 (AWAKE 메시지에서 추출)
  parsed_data     JSONB DEFAULT '{}',
  -- 예: { "amount": 500억, "ratio_to_cap": 7.7, "investor_type": "메자닌", "conversion_price": 12000 }
  
  -- AI 분석 결과 (전체 JSON)
  ai_analysis     JSONB,
  -- verdict, verdict_tone, what, so_what, so_what_data, historical,
  -- now_what_holding, now_what_not_holding, risk, key_date,
  -- size_assessment, percentile, tags
  
  -- 메타
  source          VARCHAR(20) DEFAULT 'awake',  -- awake | dart
  raw_message     TEXT,                         -- AWAKE 원문 메시지
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- 인덱스
CREATE INDEX idx_disclosures_stock_code ON disclosures(stock_code);
CREATE INDEX idx_disclosures_rcept_dt ON disclosures(rcept_dt DESC);
CREATE INDEX idx_disclosures_type ON disclosures(disclosure_type);
CREATE INDEX idx_disclosures_grade ON disclosures(grade);
CREATE INDEX idx_disclosures_direction ON disclosures(direction);
CREATE INDEX idx_disclosures_corp_code ON disclosures(corp_code);
CREATE INDEX idx_disclosures_stock_date ON disclosures(stock_code, rcept_dt DESC);

-- RLS
ALTER TABLE disclosures ENABLE ROW LEVEL SECURITY;
CREATE POLICY "disclosures_read_all" ON disclosures FOR SELECT USING (true);
CREATE POLICY "disclosures_insert_service" ON disclosures FOR INSERT WITH CHECK (auth.role() = 'service_role');
CREATE POLICY "disclosures_update_service" ON disclosures FOR UPDATE USING (auth.role() = 'service_role');
```

### 1-2. `price_reactions` (Phase 2 — 스키마만 선정의)

```sql
CREATE TABLE price_reactions (
  id              BIGSERIAL PRIMARY KEY,
  disclosure_id   BIGINT NOT NULL REFERENCES disclosures(id) ON DELETE CASCADE,
  close_d0        INT,
  close_d1        INT,
  close_d5        INT,
  close_d30       INT,
  close_d60       INT,
  return_d1       FLOAT,
  return_d5       FLOAT,
  return_d30      FLOAT,
  return_d60      FLOAT,
  market_return_d30 FLOAT,
  excess_return_d30 FLOAT,
  volume_d1       BIGINT,
  volume_avg_20d  BIGINT,
  volume_ratio_d1 FLOAT,
  gap_d1          FLOAT,
  UNIQUE(disclosure_id)
);

CREATE INDEX idx_price_reactions_disclosure ON price_reactions(disclosure_id);
ALTER TABLE price_reactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "price_reactions_read" ON price_reactions FOR SELECT USING (true);
```

### 1-3. `type_statistics` (유형별 통계 — Phase 1에서 기획서 분포표 수동 입력)

```sql
CREATE TABLE type_statistics (
  id                SERIAL PRIMARY KEY,
  disclosure_type   VARCHAR(50) NOT NULL,
  sub_condition     VARCHAR(100) NOT NULL DEFAULT '_all',
  sample_count      INT NOT NULL,
  avg_return_d1     FLOAT,
  avg_return_d30    FLOAT,
  avg_return_d60    FLOAT,
  median_return_d30 FLOAT,
  stddev_d30        FLOAT,
  positive_rate_d30 FLOAT,           -- 30일 후 양수 비율 %
  avg_excess_d30    FLOAT,
  prompt_summary    TEXT NOT NULL,    -- 프롬프트용 한줄 요약
  UNIQUE(disclosure_type, sub_condition)
);

ALTER TABLE type_statistics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "type_stats_read" ON type_statistics FOR SELECT USING (true);
```

**Phase 1 시드 데이터**: 기획서 섹션 3의 분포표를 `prompt_summary`에 텍스트로 입력.
수익률 데이터(`avg_return_d1` 등)는 Phase 2에서 DART+주가 매칭 후 채움.

### 1-4. `corp_history` (Phase 2)

```sql
CREATE TABLE corp_history (
  corp_code         VARCHAR(10) NOT NULL,
  disclosure_type   VARCHAR(50) NOT NULL,
  count_total       INT DEFAULT 0,
  count_1y          INT DEFAULT 0,
  count_3y          INT DEFAULT 0,
  avg_return_d30    FLOAT,
  last_date         DATE,
  last_return_d30   FLOAT,
  PRIMARY KEY(corp_code, disclosure_type)
);

ALTER TABLE corp_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "corp_history_read" ON corp_history FOR SELECT USING (true);
```

### 1-5. API 뷰

```sql
-- 프론트엔드 공시 목록 조회용 (가벼운 뷰)
CREATE VIEW v_disclosure_feed AS
SELECT
  d.id,
  d.stock_code,
  d.corp_name,
  d.report_nm,
  d.rcept_dt,
  d.rcept_time,
  d.disclosure_type,
  d.sub_condition,
  d.grade,
  d.direction,
  d.market_cap,
  d.ai_analysis->>'verdict' AS verdict,
  d.ai_analysis->>'verdict_tone' AS verdict_tone,
  d.ai_analysis->>'size_assessment' AS size_assessment,
  d.ai_analysis->'tags' AS tags
FROM disclosures d
ORDER BY d.rcept_dt DESC, d.rcept_time DESC NULLS LAST;

-- 종목별 공시 조회용
CREATE VIEW v_stock_disclosures AS
SELECT
  d.id,
  d.stock_code,
  d.corp_name,
  d.report_nm,
  d.rcept_dt,
  d.disclosure_type,
  d.grade,
  d.direction,
  d.ai_analysis->>'verdict' AS verdict,
  d.ai_analysis->>'verdict_tone' AS verdict_tone,
  d.ai_analysis->>'size_assessment' AS size_assessment
FROM disclosures d;
```

---

## 2. 프론트엔드 컴포넌트 설계

### 2-0. 타입 정의 — `lib/types/disclosure.ts`

```typescript
// DB에서 오는 공시 목록 아이템 (v_disclosure_feed)
export interface DisclosureFeedItem {
  id: number;
  stock_code: string;
  corp_name: string;
  report_nm: string;
  rcept_dt: string;        // YYYY-MM-DD
  rcept_time: string | null;
  disclosure_type: string;
  sub_condition: string | null;
  grade: 'A' | 'B' | 'C' | 'D';
  direction: 'bullish' | 'bearish' | 'neutral';
  market_cap: number | null;
  verdict: string;
  verdict_tone: string;
  size_assessment: string | null;
  tags: string[] | null;
}

// AI 분석 전체 (모달용)
export interface DisclosureAIAnalysis {
  verdict: string;
  verdict_tone: 'bullish' | 'bearish' | 'neutral';
  grade: 'A' | 'B' | 'C' | 'D';
  what: string;
  so_what: string;
  so_what_data: Array<{ label: string; value: string; assessment: string }>;
  historical: {
    title: string;
    rows: Array<{ label: string; value: string }>;
  };
  now_what_holding: string;
  now_what_not_holding: string;
  risk: string;
  key_date: string | null;
  size_assessment: string;
  percentile: string;
  tags: string[];
}

// 공시 상세 (모달 열 때 fetch)
export interface DisclosureDetail {
  id: number;
  stock_code: string;
  corp_name: string;
  report_nm: string;
  rcept_dt: string;
  rcept_time: string | null;
  disclosure_type: string;
  sub_condition: string | null;
  grade: 'A' | 'B' | 'C' | 'D';
  direction: 'bullish' | 'bearish' | 'neutral';
  market_cap: number | null;
  parsed_data: Record<string, any>;
  ai_analysis: DisclosureAIAnalysis;
}

// 필터
export interface DisclosureFilter {
  grade?: ('A' | 'B' | 'C' | 'D')[];
  type?: string[];
  direction?: ('bullish' | 'bearish' | 'neutral')[];
  stock_code?: string;
}
```

### 2-1. 데이터 훅 — `lib/hooks/useDisclosures.ts`

```typescript
// Supabase 클라이언트에서 직접 호출 (static export 제약)
export function useDisclosureFeed(filter: DisclosureFilter, page: number): {
  data: DisclosureFeedItem[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
}

export function useStockDisclosures(stockCode: string): {
  data: DisclosureFeedItem[];
  loading: boolean;
}

export function useDisclosureDetail(id: number): {
  data: DisclosureDetail | null;
  loading: boolean;
}
```

**데이터 흐름**: 컴포넌트 → hook → `@supabase/supabase-js` 클라이언트 → Supabase REST API (anon key + RLS)

### 2-2. 컴포넌트 트리

```
components/disclosure/
├── DisclosureCard.tsx          ← 공시 카드 (목록 아이템)
├── DisclosureAnalysisModal.tsx ← AI 분석 모달 (풀스크린)
├── DisclosureFilterBar.tsx     ← 필터 바 (등급/유형/방향)
├── DisclosureGradeBadge.tsx    ← A/B/C/D 뱃지
├── DisclosureFeed.tsx          ← 무한스크롤 피드 (explore용)
├── RealTimeFeedTab.tsx         ← [기존] 수정하여 Supabase 연동
├── HighlightsTab.tsx           ← [기존] 유지
├── EarningsSeasonTab.tsx       ← [기존] 유지
├── DisclosureSearchTab.tsx     ← [기존] 유지

components/stock/
├── StockDisclosureTab.tsx      ← [기존] 수정하여 Supabase 연동
```

### 2-3. 컴포넌트 상세

#### A. `DisclosureGradeBadge.tsx`

```typescript
interface DisclosureGradeBadgeProps {
  grade: 'A' | 'B' | 'C' | 'D';
  size?: 'sm' | 'md' | 'lg';
}
// A=빨강, B=주황, C=파랑, D=회색
// 토스 스타일 rounded-full pill 형태
```

#### B. `DisclosureCard.tsx`

```typescript
interface DisclosureCardProps {
  item: DisclosureFeedItem;
  onClick: (id: number) => void;
  showCorpName?: boolean;  // explore에서는 true, stock 탭에서는 false
}
```

**레이아웃**:
```
┌─────────────────────────────────────────┐
│ [A] 삼성전자  2026-02-28  실적           │
│ 3분기 영업익 15.4조, 컨센 대비 +21.7%    │
│ #어닝서프 #반도체 #HBM                   │
└─────────────────────────────────────────┘
```
- 왼쪽: GradeBadge + 종목명 + 날짜 + 유형
- 중앙: verdict 텍스트
- 하단: tags pill 형태
- direction에 따라 카드 왼쪽 보더 색상 (bullish=초록, bearish=빨강, neutral=회색)

#### C. `DisclosureFilterBar.tsx`

```typescript
interface DisclosureFilterBarProps {
  filter: DisclosureFilter;
  onChange: (filter: DisclosureFilter) => void;
}
```

**UI**: 가로 스크롤 칩 형태 (토스 스타일)
- 등급: A / B / C / D (토글)
- 유형: 실적 / CB / 자사주 / 풍문 / 수주 / 유증 / 기타 (토글)
- 방향: 🟢호재 / 🔴악재 / ⚪중립 (토글)

#### D. `DisclosureAnalysisModal.tsx`

```typescript
interface DisclosureAnalysisModalProps {
  disclosureId: number;
  isOpen: boolean;
  onClose: () => void;
}
```

**내부에서 `useDisclosureDetail(id)` 호출하여 ai_analysis 전체 로드.**

**모달 섹션 구조** (스크롤 가능, 토스 스타일 바텀시트):

```
┌─ 헤더 ──────────────────────────────────┐
│ [A] 삼성전자 · 실적 · 2026-02-28        │
│ "3분기 영업익 15.4조, 컨센 +21.7%"  🟢  │
├─ 이게 뭔데? (what) ─────────────────────┤
│ 초보 설명 텍스트                         │
├─ 그래서? (so_what) ─────────────────────┤
│ 숫자 해석 텍스트                         │
│ ┌──────────┬──────────┬────────┐        │
│ │ 지표      │ 값       │ 평가   │        │
│ │ 영업이익   │ 15.4조   │ 서프   │        │
│ └──────────┴──────────┴────────┘        │
├─ 과거 통계 (historical) ────────────────┤
│ • 유사 공시 47건 중 D+30 상승 68%        │
├─ 보유 중이라면 (now_what_holding) ───────┤
│ 행동 가이드                              │
├─ 미보유라면 (now_what_not_holding) ──────┤
│ 행동 가이드                              │
├─ 리스크 (risk) ─────────────────────────┤
│ 핵심 리스크 한줄                         │
├─ 메타 ──────────────────────────────────┤
│ 📅 key_date  📊 percentile  📏 size     │
│ 🏷️ tags                                 │
└─────────────────────────────────────────┘
```

#### E. `DisclosureFeed.tsx` (explore 전용)

```typescript
interface DisclosureFeedProps {
  filter: DisclosureFilter;
}
// 내부: useDisclosureFeed + 무한스크롤 (IntersectionObserver)
// 렌더: DisclosureCard 반복
```

### 2-4. 기존 컴포넌트 수정 계획

| 파일 | 변경 |
|------|------|
| `RealTimeFeedTab.tsx` | 더미 데이터 → `useDisclosureFeed({}, 1)` + DisclosureCard 사용 |
| `StockDisclosureTab.tsx` | 더미 데이터 → `useStockDisclosures(code)` + DisclosureCard 사용 |
| `app/explore/disclosure/page.tsx` | RealTimeFeedTab에 FilterBar 추가 |

### 2-5. 라우팅 (변경 없음)

- `/explore/disclosure` — 이미 존재. 탭 구조 유지, 데이터만 실제로 교체.
- `/stock/[code]` — 이미 존재. 공시 탭이 StockDisclosureTab 사용.
- **모달은 라우트 변경 없이 오버레이** (static export 친화적).

---

## 3. 데이터 파이프라인 설계 (Phase 1)

### 3-1. 아키텍처 개요

```
AWAKE 텔레그램 채널
        │
        ▼
[Python Script] ─── 텔레그램 메시지 수신 (Telethon/Pyrogram)
        │
        ├─ 1. 메시지 파싱 (정규식으로 종목/유형/수치 추출)
        ├─ 2. 유형/세부조건 분류
        ├─ 3. type_statistics에서 통계 조회
        ├─ 4. 프롬프트 조합 → Claude API 호출
        ├─ 5. AI 분석 JSON 파싱
        └─ 6. Supabase에 INSERT (disclosures 테이블)
                │
                ▼
        [Supabase PostgreSQL]
                │
                ▼
        [프론트엔드] ← Supabase JS 클라이언트로 직접 조회
```

### 3-2. 왜 Python Script인가 (Edge Function 아님)

| 요소 | Edge Function | Python Script |
|------|--------------|---------------|
| 텔레그램 수신 | ❌ webhook만 가능 (AWAKE는 공개채널, bot 아님) | ✅ Telethon으로 채널 리스닝 |
| 장시간 실행 | ❌ 타임아웃 50초 | ✅ 데몬 실행 |
| Claude API | ✅ | ✅ |
| 배포 | Supabase 내장 | 별도 서버 (VPS or 로컬) |

**결론**: Phase 1은 **Python 스크립트** (로컬 or VPS에서 데몬 실행).

Edge Function은 나중에 프론트엔드용 API 래퍼로만 사용 (필요 시).

### 3-3. AWAKE 메시지 파싱 상세

AWAKE 메시지 패턴 (예시 기반 추정):
```
[CB발행] 삼성SDI(006400) 시총 15.2조
사모 CB 1,500억원 (시총 대비 9.9%)
전환가 380,000원 (현재가 대비 -12%)
투자자: OO캐피탈 (메자닌)
리픽싱 하한: 70%
만기이율: 2.0%
```

**파싱 전략**:
1. 첫 줄 `[유형]` 태그로 `disclosure_type` 결정
2. 정규식으로 종목명, 종목코드, 시총, 금액, 비율 추출
3. 유형별 전용 파서 (CB파서, 실적파서, 자사주파서 등)
4. `parsed_data` JSONB에 구조화된 수치 저장

### 3-4. AI 분석 생성 흐름

```python
# 기획서 섹션 5-4 구현
def generate_analysis(parsed_msg):
    # 1. 분류
    dtype = parsed_msg['disclosure_type']
    sub = classify_sub_condition(parsed_msg)
    
    # 2. 통계 조회 (Supabase)
    stats = supabase.table('type_statistics') \
        .select('*') \
        .eq('disclosure_type', dtype) \
        .eq('sub_condition', sub) \
        .single().execute()
    
    # 3. 프롬프트 조합 (기획서 섹션 1 시스템 프롬프트 + 섹션 3 분포표 + 섹션 4 판단체인)
    prompt = build_prompt(
        system=SYSTEM_PROMPT_V6,
        stats=stats.data,
        parsed=parsed_msg
    )
    
    # 4. Claude 호출
    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    
    # 5. JSON 파싱 + 검증
    analysis = json.loads(response.content[0].text)
    validate_analysis(analysis)  # grade, verdict 등 필수 필드 체크
    
    # 6. DB 저장
    supabase.table('disclosures').insert({
        'corp_name': parsed_msg['corp_name'],
        'stock_code': parsed_msg['stock_code'],
        'report_nm': parsed_msg['title'],
        'rcept_dt': parsed_msg['date'],
        'disclosure_type': dtype,
        'sub_condition': sub,
        'grade': analysis['grade'],
        'direction': analysis['verdict_tone'],
        'market_cap': parsed_msg.get('market_cap'),
        'parsed_data': parsed_msg,
        'ai_analysis': analysis,
        'source': 'awake',
        'raw_message': parsed_msg['raw_text']
    }).execute()
```

### 3-5. 실시간 vs 배치

**Phase 1: 준실시간 (이벤트 드리븐)**
- Telethon으로 AWAKE 채널 리스닝 → 메시지 도착 시 즉시 처리
- 공시 1건당 처리 시간: 파싱 ~1초 + Claude API ~5초 = **~6초**
- 장중 공시 빈도: 분당 0~5건 → 충분히 실시간 처리 가능

**실패 처리**:
- Claude API 실패 → 3회 재시도 후 `ai_analysis = null`로 저장, 나중에 배치 재처리
- 파싱 실패 → `raw_message`만 저장, 수동 확인

---

## 4. Phase 1 구현 순서

### Step 1: DB 세팅 (2시간)
- [ ] Supabase에 4개 테이블 생성 (SQL 실행)
- [ ] RLS 정책 적용
- [ ] 뷰 2개 생성
- [ ] `type_statistics` 시드 데이터 입력 (기획서 분포표 기반, ~27행)
- **의존성**: 없음

### Step 2: 타입 + 훅 (2시간)
- [ ] `lib/types/disclosure.ts` 생성
- [ ] `lib/hooks/useDisclosures.ts` 생성 (Supabase 쿼리)
- [ ] 기존 Supabase 클라이언트 설정 확인/수정
- **의존성**: Step 1

### Step 3: 공통 컴포넌트 (3시간)
- [ ] `DisclosureGradeBadge.tsx`
- [ ] `DisclosureCard.tsx`
- [ ] `DisclosureFilterBar.tsx`
- [ ] `DisclosureAnalysisModal.tsx`
- **의존성**: Step 2

### Step 4: 기존 페이지 연동 (2시간)
- [ ] `RealTimeFeedTab.tsx` 리팩토링 (더미 → Supabase)
- [ ] `StockDisclosureTab.tsx` 리팩토링
- [ ] `app/explore/disclosure/page.tsx`에 필터바 추가
- **의존성**: Step 3

### Step 5: 파이프라인 기본 (4시간)
- [ ] Python 프로젝트 셋업 (`scripts/disclosure_pipeline/`)
- [ ] AWAKE 메시지 파서 (유형별 정규식)
- [ ] 유형/세부조건 분류기 (27개 조건)
- [ ] Supabase 연동 (supabase-py)
- **의존성**: Step 1

### Step 6: AI 분석 생성 (3시간)
- [ ] 프롬프트 빌더 (시스템 프롬프트 + 통계 + 판단체인 조합)
- [ ] Claude API 연동
- [ ] JSON 검증 + DB 저장
- **의존성**: Step 5

### Step 7: 텔레그램 리스너 (2시간)
- [ ] Telethon으로 AWAKE 채널 리스닝
- [ ] 메시지 수신 → 파서 → AI → DB 연결
- [ ] 에러 핸들링 + 로깅
- **의존성**: Step 6

### Step 8: 테스트 + 시드 데이터 (2시간)
- [ ] AWAKE 과거 메시지 10~20건 수동 파싱하여 DB에 시드
- [ ] 프론트엔드 동작 확인
- [ ] 모달 UI 검증
- **의존성**: Step 4 + Step 7

**총 예상: ~20시간 (풀타임 2.5일)**

```
Step1(DB) ──→ Step2(타입) ──→ Step3(컴포넌트) ──→ Step4(페이지연동)
    │                                                      │
    └──→ Step5(파서) ──→ Step6(AI) ──→ Step7(리스너) ──→ Step8(테스트)
```

Step 1~4 (프론트) 와 Step 5~7 (백엔드)는 **Step 1 이후 병렬 진행 가능**.

---

## 5. Phase 1 범위 명확화 (In/Out)

### ✅ Phase 1 포함
- AWAKE 텔레그램 → AI 분석 → DB 저장 파이프라인
- 공시 목록/피드 UI (explore + stock 탭)
- AI 분석 모달
- 등급/유형/방향 필터
- type_statistics 수동 시드 (기획서 분포표)

### ❌ Phase 1 미포함 (Phase 2+)
- DART API 직접 수집
- 주가 데이터 매칭 (price_reactions)
- corp_history 자동 생성
- 실시간 주가 반응 표시
- 복수 공시 자동 합산 (유한양행 케이스)
- 정정공시 원본 매칭
- 소형주(시총 500억 미만) 커버
