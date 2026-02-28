# 공시 관련 Supabase 테이블 설계

## 1. disclosures 테이블 (메인 공시 데이터)

```sql
-- 공시 메인 테이블
CREATE TABLE disclosures (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    disclosure_id TEXT UNIQUE NOT NULL, -- DART 공시고유번호
    company_code TEXT NOT NULL, -- 종목코드 (005930)
    company_name TEXT NOT NULL, -- 회사명
    disclosure_date DATE NOT NULL, -- 공시일자
    disclosure_time TIME, -- 공시시간
    title TEXT NOT NULL, -- 공시제목
    summary TEXT, -- 요약
    content TEXT, -- 전문내용
    
    -- 분류
    disclosure_type TEXT NOT NULL, -- 공시유형 (자사주, 실적, 배당, 계약, 해명, 기타)
    grade TEXT CHECK (grade IN ('A', 'B')), -- 등급
    sector TEXT, -- 섹터
    market_cap BIGINT, -- 시가총액 (원)
    
    -- 금액 정보
    amount_value BIGINT, -- 금액 (원)
    amount_text TEXT, -- 금액 텍스트 (23.5억)
    percentage_text TEXT, -- 비율 텍스트 (매출대비 14.77%)
    
    -- AI 분석
    ai_analysis TEXT, -- AI 분석 요약
    ai_confidence DECIMAL(3,2), -- AI 신뢰도 (0.00-1.00)
    
    -- 시장 반응
    price_reaction_1d DECIMAL(5,2), -- 1일 수익률 (%)
    price_reaction_3d DECIMAL(5,2), -- 3일 수익률 (%)
    price_reaction_7d DECIMAL(5,2), -- 7일 수익률 (%)
    price_reaction_15d DECIMAL(5,2), -- 15일 수익률 (%)
    price_reaction_30d DECIMAL(5,2), -- 30일 수익률 (%)
    
    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 인덱스
    CONSTRAINT disclosures_company_code_fkey FOREIGN KEY (company_code) REFERENCES companies(code) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX idx_disclosures_company_code ON disclosures(company_code);
CREATE INDEX idx_disclosures_date ON disclosures(disclosure_date DESC);
CREATE INDEX idx_disclosures_type ON disclosures(disclosure_type);
CREATE INDEX idx_disclosures_grade ON disclosures(grade);
CREATE INDEX idx_disclosures_company_date ON disclosures(company_code, disclosure_date DESC);
```

## 2. disclosure_tags 테이블 (공시 태그)

```sql
-- 공시 태그 테이블
CREATE TABLE disclosure_tags (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    disclosure_id UUID NOT NULL,
    tag_name TEXT NOT NULL, -- 태그명 (자사주소각, 매출증가, 신규고객 등)
    tag_category TEXT, -- 태그 카테고리 (positive, negative, neutral)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT disclosure_tags_disclosure_fkey FOREIGN KEY (disclosure_id) REFERENCES disclosures(id) ON DELETE CASCADE,
    CONSTRAINT unique_disclosure_tag UNIQUE(disclosure_id, tag_name)
);

CREATE INDEX idx_disclosure_tags_disclosure ON disclosure_tags(disclosure_id);
CREATE INDEX idx_disclosure_tags_name ON disclosure_tags(tag_name);
```

## 3. disclosure_metrics 테이블 (공시별 핵심 지표)

```sql
-- 공시별 핵심 지표 (사업보고서용)
CREATE TABLE disclosure_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    disclosure_id UUID NOT NULL,
    metric_name TEXT NOT NULL, -- 지표명 (매출채권, 재고자산, 차입금, R&D비용)
    metric_value TEXT NOT NULL, -- 지표값 (34.2조원)
    metric_change TEXT, -- 변동률 (+8.4%)
    metric_unit TEXT, -- 단위 (원, %, 건)
    display_order INTEGER, -- 표시순서
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT disclosure_metrics_disclosure_fkey FOREIGN KEY (disclosure_id) REFERENCES disclosures(id) ON DELETE CASCADE
);

CREATE INDEX idx_disclosure_metrics_disclosure ON disclosure_metrics(disclosure_id);
```

## 4. analyst_reports 테이블 (애널리스트 리포트)

```sql
-- 애널리스트 리포트 테이블
CREATE TABLE analyst_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    report_id TEXT UNIQUE, -- 리포트 고유ID
    company_code TEXT NOT NULL, -- 종목코드
    firm_name TEXT NOT NULL, -- 증권사명
    analyst_name TEXT, -- 애널리스트명
    report_date DATE NOT NULL, -- 리포트 발행일
    
    -- 투자의견
    rating TEXT NOT NULL, -- BUY, HOLD, SELL
    target_price INTEGER, -- 목표주가 (원)
    current_price INTEGER, -- 현재주가 (원)
    upside_percentage DECIMAL(5,2), -- 상승여력 (%)
    
    -- 내용
    title TEXT, -- 리포트 제목
    summary TEXT, -- 요약
    key_points TEXT[], -- 주요 포인트 (배열)
    
    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT analyst_reports_company_code_fkey FOREIGN KEY (company_code) REFERENCES companies(code) ON DELETE CASCADE
);

CREATE INDEX idx_analyst_reports_company ON analyst_reports(company_code);
CREATE INDEX idx_analyst_reports_date ON analyst_reports(report_date DESC);
CREATE INDEX idx_analyst_reports_firm ON analyst_reports(firm_name);
```

## 5. earnings_calendar 테이블 (실적 발표 일정)

```sql
-- 실적 발표 일정 테이블
CREATE TABLE earnings_calendar (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_code TEXT NOT NULL, -- 종목코드
    company_name TEXT NOT NULL, -- 회사명
    quarter TEXT NOT NULL, -- 분기 (2026Q1)
    fiscal_year INTEGER NOT NULL, -- 회계연도
    
    -- 일정
    announcement_date DATE, -- 발표예정일
    actual_announcement_date DATE, -- 실제발표일
    is_announced BOOLEAN DEFAULT FALSE, -- 발표완료 여부
    
    -- 실적 데이터
    revenue BIGINT, -- 매출액 (원)
    operating_income BIGINT, -- 영업이익 (원)
    net_income BIGINT, -- 순이익 (원)
    
    -- 컨센서스 vs 실제
    revenue_consensus BIGINT, -- 매출 컨센서스
    operating_income_consensus BIGINT, -- 영업이익 컨센서스
    net_income_consensus BIGINT, -- 순이익 컨센서스
    
    surprise_type TEXT, -- SURPRISE, SHOCK, NEUTRAL
    beat_margin_percentage DECIMAL(5,2), -- 비트 마진 (%)
    
    -- 시장 반응
    price_reaction_1d DECIMAL(5,2), -- 발표 후 1일 수익률
    price_reaction_3d DECIMAL(5,2), -- 발표 후 3일 수익률
    
    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT earnings_calendar_company_code_fkey FOREIGN KEY (company_code) REFERENCES companies(code) ON DELETE CASCADE,
    CONSTRAINT unique_earnings_quarter UNIQUE(company_code, quarter, fiscal_year)
);

CREATE INDEX idx_earnings_calendar_company ON earnings_calendar(company_code);
CREATE INDEX idx_earnings_calendar_date ON earnings_calendar(announcement_date);
CREATE INDEX idx_earnings_calendar_quarter ON earnings_calendar(quarter);
```

## 6. disclosure_statistics 테이블 (공시 통계)

```sql
-- 공시 통계 테이블 (일별/유형별 집계)
CREATE TABLE disclosure_statistics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stat_date DATE NOT NULL, -- 통계일자
    stat_type TEXT NOT NULL, -- daily, weekly, monthly
    
    -- 전체 통계
    total_disclosures INTEGER DEFAULT 0, -- 전체 공시 수
    a_grade_count INTEGER DEFAULT 0, -- A등급 공시 수
    b_grade_count INTEGER DEFAULT 0, -- B등급 공시 수
    
    -- 유형별 통계 (JSON)
    type_breakdown JSONB, -- {"자사주": 12, "실적": 8, "배당": 3}
    sector_breakdown JSONB, -- {"IT부품": 15, "화학": 8}
    
    -- 시장 영향
    market_impact_percentage DECIMAL(5,2), -- 코스피 영향 (%)
    avg_price_reaction DECIMAL(5,2), -- 평균 주가 반응 (%)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_disclosure_stat UNIQUE(stat_date, stat_type)
);

CREATE INDEX idx_disclosure_statistics_date ON disclosure_statistics(stat_date DESC);
```

## 7. popular_tags 테이블 (인기 키워드 통계)

```sql
-- 인기 키워드 통계
CREATE TABLE popular_tags (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tag_name TEXT NOT NULL, -- 태그명
    usage_count INTEGER DEFAULT 0, -- 사용 횟수
    trend_direction TEXT CHECK (trend_direction IN ('up', 'down', 'stable')), -- 트렌드
    last_week_count INTEGER DEFAULT 0, -- 지난주 사용 횟수
    
    -- 기간별 집계
    current_week_count INTEGER DEFAULT 0, -- 이번주 사용 횟수
    current_month_count INTEGER DEFAULT 0, -- 이번달 사용 횟수
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_popular_tag UNIQUE(tag_name)
);

CREATE INDEX idx_popular_tags_count ON popular_tags(usage_count DESC);
CREATE INDEX idx_popular_tags_trend ON popular_tags(trend_direction);
```

## 8. RLS (Row Level Security) 설정

```sql
-- RLS 활성화
ALTER TABLE disclosures ENABLE ROW LEVEL SECURITY;
ALTER TABLE disclosure_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE disclosure_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyst_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE earnings_calendar ENABLE ROW LEVEL SECURITY;

-- 읽기 정책 (모든 사용자가 읽기 가능)
CREATE POLICY "Public read access" ON disclosures FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "Public read access" ON disclosure_tags FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "Public read access" ON disclosure_metrics FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "Public read access" ON analyst_reports FOR SELECT TO PUBLIC USING (true);
CREATE POLICY "Public read access" ON earnings_calendar FOR SELECT TO PUBLIC USING (true);
```

## 9. 함수 및 트리거

```sql
-- updated_at 자동 업데이트 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_disclosures_updated_at 
    BEFORE UPDATE ON disclosures 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analyst_reports_updated_at 
    BEFORE UPDATE ON analyst_reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_earnings_calendar_updated_at 
    BEFORE UPDATE ON earnings_calendar 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## 10. 샘플 데이터 삽입

```sql
-- 샘플 공시 데이터
INSERT INTO disclosures (
    disclosure_id, company_code, company_name, disclosure_date, disclosure_time,
    title, summary, disclosure_type, grade, sector, market_cap,
    amount_value, amount_text, percentage_text,
    ai_analysis, ai_confidence,
    price_reaction_1d, price_reaction_3d, price_reaction_7d, price_reaction_15d, price_reaction_30d
) VALUES 
(
    '20260228-005930-001', '005930', '삼성전자', '2026-02-28', '13:45:00',
    '3분기 실적 컨센서스 상회 발표', 
    '영업이익 15조 3,842억원 (컨센서스 대비 +21.7%)',
    '실적', 'A', '반도체', 500000000000000,
    15384200000000, '15조 3,842억원', '컨센서스 대비 +21.7%',
    '반도체 업사이클 진입, HBM 점유율 확대로 수익성 개선', 0.95,
    5.4, 8.2, 12.1, 18.7, 24.3
);

-- 샘플 태그 데이터
INSERT INTO disclosure_tags (disclosure_id, tag_name, tag_category) 
SELECT id, unnest(ARRAY['실적서프라이즈', '반도체호황', 'AI칩수요', 'HBM']), 'positive' 
FROM disclosures WHERE disclosure_id = '20260228-005930-001';
```

## 11. API 연동을 위한 뷰

```sql
-- 공시 요약 뷰 (API 최적화)
CREATE VIEW disclosure_summary AS
SELECT 
    d.id,
    d.disclosure_id,
    d.company_code,
    d.company_name,
    d.disclosure_date,
    d.title,
    d.summary,
    d.disclosure_type,
    d.grade,
    d.sector,
    d.amount_text,
    d.percentage_text,
    d.ai_analysis,
    d.price_reaction_1d,
    d.price_reaction_7d,
    d.price_reaction_30d,
    array_agg(dt.tag_name) as tags
FROM disclosures d
LEFT JOIN disclosure_tags dt ON d.id = dt.disclosure_id
GROUP BY d.id, d.disclosure_id, d.company_code, d.company_name, 
         d.disclosure_date, d.title, d.summary, d.disclosure_type, 
         d.grade, d.sector, d.amount_text, d.percentage_text, 
         d.ai_analysis, d.price_reaction_1d, d.price_reaction_7d, d.price_reaction_30d;
```

이 테이블 설계는 DART API와 연동하여 실시간 공시 데이터를 저장하고, 
토스 스타일의 세련된 UI로 표시할 수 있도록 구성되었습니다.