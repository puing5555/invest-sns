# 공시 AI 분석 시스템 — Phase 1 기술 스펙 v2

> 기준: DART OpenAPI 직접 수집 | 작성: 2026-03-04 | 환경: Next.js static export + Supabase + Windows 서버

---

## 0. 변경사항 (v1 → v2)

| 항목 | v1 | v2 |
|------|-----|-----|
| 데이터 소스 | AWAKE 텔레그램 | **DART OpenAPI 직접** |
| 수집 방식 | Telethon 채널 리스닝 | **DART API 폴링 (cron)** |
| 실행 환경 | VPS or 로컬 | **1층 Windows PC** |
| 공시 원문 | AWAKE 메시지 파싱 | **DART report_nm + 원문 XML** |
| UI 시작 | DB 연동 후 | **시드 데이터로 디자인 먼저** |

---

## 1. DART OpenAPI 개요

- **URL**: `https://opendart.fss.or.kr/api/list.json`
- **인증**: API 키 (무료, 하루 10,000건)
- **주요 엔드포인트**:

| API | URL | 용도 |
|-----|-----|------|
| 공시검색 | `/api/list.json` | 신규 공시 감지 (폴링) |
| 기업개황 | `/api/company.json` | 기업 메타정보 (시총, 섹터) |
| 공시서류원본 | `/api/document.xml` | 공시 원문 (AI 분석 입력) |
| 고유번호 | `/api/corpCode.xml` | 전체 기업 코드 매핑 (1회) |

### 공시검색 응답 필드
```json
{
  "corp_cls": "Y",          // 유가/코스닥/코넥스
  "corp_name": "삼성전자",
  "corp_code": "00126380",
  "stock_code": "005930",
  "report_nm": "[기재정정]주요사항보고서(전환사채권발행결정)",
  "rcept_no": "20260304000123",
  "flr_nm": "삼성전자",
  "rcept_dt": "20260304",
  "rm": "유"
}
```

---

## 2. DB 스키마 (v1과 동일, source 필드만 변경)

### 2-1. `disclosures` (공시 원본 + AI 분석)

```sql
CREATE TABLE disclosures (
  id              BIGSERIAL PRIMARY KEY,
  rcept_no        VARCHAR(20) UNIQUE NOT NULL,  -- DART 접수번호 (PK급)
  corp_code       VARCHAR(10) NOT NULL,         -- DART 기업 고유코드
  corp_name       VARCHAR(100) NOT NULL,
  corp_cls        CHAR(1),                      -- Y/K/N/E
  stock_code      VARCHAR(10),                  -- 종목코드 (6자리, 비상장은 null)
  report_nm       VARCHAR(500) NOT NULL,        -- 보고서명 원문
  flr_nm          VARCHAR(100),                 -- 공시 제출인
  rcept_dt        DATE NOT NULL,                -- 접수일
  
  -- DART 분류
  pblntf_ty       CHAR(1),                      -- A~J (공시유형)
  pblntf_detail_ty VARCHAR(4),                  -- A001 등 (공시상세유형)
  
  -- AI 분류 (DART 원문 분석 후)
  disclosure_type VARCHAR(50),                  -- CB발행, 실적, 자사주소각 등
  sub_condition   VARCHAR(100),                 -- 사모_시총10%+, 흑자전환 등
  grade           CHAR(1) CHECK (grade IN ('A','B','C','D')),
  direction       VARCHAR(10) CHECK (direction IN ('bullish','bearish','neutral')),
  
  -- 기업 메타
  market_cap      BIGINT,
  sector          VARCHAR(50),
  
  -- AI 분석 결과 JSON
  ai_analysis     JSONB,
  
  -- 메타
  source          VARCHAR(20) DEFAULT 'dart',
  raw_report_url  TEXT,                         -- DART 원문 뷰어 URL
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- 인덱스
CREATE INDEX idx_disc_stock ON disclosures(stock_code);
CREATE INDEX idx_disc_date ON disclosures(rcept_dt DESC);
CREATE INDEX idx_disc_type ON disclosures(disclosure_type);
CREATE INDEX idx_disc_grade ON disclosures(grade);
CREATE INDEX idx_disc_direction ON disclosures(direction);
CREATE INDEX idx_disc_corp ON disclosures(corp_code);

-- RLS
ALTER TABLE disclosures ENABLE ROW LEVEL SECURITY;
CREATE POLICY "read_all" ON disclosures FOR SELECT USING (true);
CREATE POLICY "insert_service" ON disclosures FOR INSERT WITH CHECK (auth.role() = 'service_role');
CREATE POLICY "update_service" ON disclosures FOR UPDATE USING (auth.role() = 'service_role');
```

### 2-2~2-4. (v1과 동일: price_reactions, type_statistics, corp_history)

### 2-5. API 뷰

```sql
CREATE VIEW v_disclosure_feed AS
SELECT
  d.id, d.rcept_no, d.stock_code, d.corp_name, d.corp_cls,
  d.report_nm, d.rcept_dt, d.pblntf_ty, d.pblntf_detail_ty,
  d.disclosure_type, d.sub_condition, d.grade, d.direction,
  d.market_cap, d.raw_report_url,
  d.ai_analysis->>'verdict' AS verdict,
  d.ai_analysis->>'verdict_tone' AS verdict_tone,
  d.ai_analysis->>'size_assessment' AS size_assessment,
  d.ai_analysis->'tags' AS tags
FROM disclosures d
WHERE d.grade IS NOT NULL  -- AI 분석 완료된 것만
ORDER BY d.rcept_dt DESC;
```

---

## 3. 데이터 파이프라인 (DART → AI → DB)

### 3-1. 아키텍처

```
[DART OpenAPI] ←── 폴링 (5분 간격)
       │
       ▼
[Python Script on 1층 PC] ─── Windows Task Scheduler (cron)
       │
       ├─ 1. /api/list.json 호출 (최근 공시 목록)
       ├─ 2. 이미 처리한 rcept_no 스킵 (Supabase 조회)
       ├─ 3. 신규 공시 → report_nm에서 유형 분류
       ├─ 4. 주요사항(B)/거래소(I)/자기주식(E) → AI 분석 대상
       ├─ 5. /api/document.xml로 원문 다운로드 (선택)
       ├─ 6. Claude API로 AI 분석
       └─ 7. Supabase에 INSERT
              │
              ▼
       [Supabase PostgreSQL]
              │
              ▼
       [프론트엔드] ← Supabase JS 직접 조회
```

### 3-2. 폴링 전략

```python
# 5분 간격 폴링 (장중 09:00~18:00)
# 야간은 30분 간격 또는 OFF

POLL_INTERVAL = 300  # 5분
DART_API_KEY = os.environ['DART_API_KEY']

def poll_new_disclosures():
    """최근 공시 목록 조회"""
    today = datetime.now().strftime('%Y%m%d')
    
    resp = requests.get('https://opendart.fss.or.kr/api/list.json', params={
        'crtfc_key': DART_API_KEY,
        'bgn_de': today,
        'end_de': today,
        'page_count': 100,
        'sort': 'date',
        'sort_mth': 'desc',
        'corp_cls': 'Y',  # 유가증권만 (코스닥은 'K' 별도 호출)
    })
    
    data = resp.json()
    if data['status'] != '000':
        return []
    
    return data['list']
```

### 3-3. 공시 필터링 (AI 분석 대상 선별)

```python
# 분석 대상 공시 유형
TARGET_TYPES = {
    'B': '주요사항보고',     # CB, 유증, 합병, 분할 등
    'C': '발행공시',         # 증권신고
    'E': '자기주식 등',      # 자사주 취득/처분
    'I': '거래소공시',       # 수시공시, 공정공시
}

# report_nm에서 유형 분류
TYPE_PATTERNS = {
    'CB발행': ['전환사채', 'CB'],
    '실적': ['영업실적', '매출액', '실적'],
    '자사주': ['자기주식', '자사주'],
    '유증': ['유상증자'],
    '풍문해명': ['풍문', '조회공시'],
    '수주': ['수주', '공급계약'],
    '합병': ['합병'],
    '분할': ['분할'],
    '대주주변동': ['대량보유', '주요주주'],
}
```

### 3-4. AI 분석 플로우

```python
def analyze_disclosure(disclosure: dict):
    """공시 1건 AI 분석"""
    
    # 1. report_nm에서 유형 분류
    dtype = classify_type(disclosure['report_nm'])
    
    # 2. 기업개황 조회 (시총, 섹터)
    corp_info = get_corp_info(disclosure['corp_code'])
    
    # 3. type_statistics에서 통계 조회
    stats = supabase.table('type_statistics') \
        .select('*') \
        .eq('disclosure_type', dtype) \
        .execute()
    
    # 4. 프롬프트 구성
    prompt = f"""
    다음 공시를 분석하세요.
    
    종목: {disclosure['corp_name']} ({disclosure['stock_code']})
    시총: {corp_info.get('market_cap', '미확인')}
    공시: {disclosure['report_nm']}
    접수일: {disclosure['rcept_dt']}
    DART 원문: https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disclosure['rcept_no']}
    
    유형별 과거 통계:
    {format_stats(stats.data)}
    
    [분석 지시사항 - grade/verdict/what/so_what 등 생성]
    """
    
    # 5. Claude Sonnet 호출
    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    
    # 6. DB INSERT
    analysis = json.loads(response.content[0].text)
    
    supabase.table('disclosures').insert({
        'rcept_no': disclosure['rcept_no'],
        'corp_code': disclosure['corp_code'],
        'corp_name': disclosure['corp_name'],
        'corp_cls': disclosure['corp_cls'],
        'stock_code': disclosure['stock_code'],
        'report_nm': disclosure['report_nm'],
        'flr_nm': disclosure['flr_nm'],
        'rcept_dt': disclosure['rcept_dt'],
        'pblntf_ty': disclosure.get('pblntf_ty'),
        'disclosure_type': dtype,
        'grade': analysis['grade'],
        'direction': analysis['verdict_tone'],
        'market_cap': corp_info.get('market_cap'),
        'ai_analysis': analysis,
        'source': 'dart',
        'raw_report_url': f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disclosure['rcept_no']}"
    }).execute()
```

### 3-5. Windows Task Scheduler 설정

```
# 1층 PC에서 실행
# Task: DART_공시_폴링
# 트리거: 매 5분 (09:00~18:00 평일)
# 동작: python C:\scripts\dart_poller.py
# 조건: 네트워크 연결 시에만
```

### 3-6. API 사용량 예상

| 항목 | 일일 호출 수 |
|------|------------|
| 공시목록 폴링 (5분×9시간) | ~108건 |
| 유가+코스닥 (×2) | ~216건 |
| 기업개황 (신규 공시당) | ~50건 |
| 원문 다운로드 | ~20건 |
| **합계** | **~286건/일** (제한: 10,000건) |

---

## 4. 프론트엔드 (v1과 동일, 변경 없음)

UI 컴포넌트 설계는 v1과 동일:
- DisclosureCard, DisclosureAnalysisModal, DisclosureFilterBar 등
- 토스 스타일, 모달 바텀시트

### 4-1. UI 우선 개발 (시드 데이터)

**시드 데이터 10~20건 수동 생성** → UI 디자인 완성 → JAY 피드백 → 파이프라인 연결

시드 데이터 구성:
- 다양한 유형: CB 3건, 실적 5건, 자사주 2건, 유증 2건, 수주 2건, 풍문 2건, 기타 4건
- 다양한 등급: A 3건, B 5건, C 8건, D 4건
- 다양한 방향: bullish 8건, bearish 5건, neutral 7건
- 실제 DART에서 최근 공시 가져와서 AI 분석 붙이기

---

## 5. 구현 순서 (수정)

### Step 1: 시드 데이터 생성 (2시간)
- [ ] DART API에서 최근 공시 20건 조회
- [ ] Claude로 각각 AI 분석 생성
- [ ] JSON 시드 파일 생성 (`data/disclosure_seeds.json`)

### Step 2: DB 세팅 (1시간)
- [ ] Supabase 테이블 생성
- [ ] 시드 데이터 INSERT

### Step 3: UI 컴포넌트 (4시간)
- [ ] 타입 정의 + 훅
- [ ] DisclosureCard, GradeBadge, FilterBar
- [ ] DisclosureAnalysisModal
- [ ] RealTimeFeedTab 연동

### Step 4: JAY 피드백 → UI 수정

### Step 5: DART 폴링 스크립트 (3시간)
- [ ] Python 스크립트 (`scripts/dart_poller.py`)
- [ ] 공시 필터링 + 유형 분류
- [ ] Claude AI 분석 생성
- [ ] Supabase INSERT

### Step 6: 1층 PC 배포 (1시간)
- [ ] Windows Task Scheduler 설정
- [ ] 로그/에러 알림 설정
- [ ] 테스트 운영

**총 예상: ~11시간 (풀타임 1.5일)**

---

## 6. Phase 1 범위

### ✅ 포함
- DART OpenAPI → AI 분석 → DB 저장 파이프라인
- 유가증권 + 코스닥 상장사 공시
- 공시 목록/피드 UI + AI 분석 모달
- 등급/유형/방향 필터
- type_statistics 시드 데이터
- Windows cron 자동 폴링

### ❌ 미포함 (Phase 2+)
- 주가 데이터 매칭 (price_reactions)
- corp_history 자동 생성
- 실시간 주가 반응 표시
- 공시서류 원문 전문 분석 (Phase 1은 report_nm 기반)
- 소형주(코넥스) 커버
