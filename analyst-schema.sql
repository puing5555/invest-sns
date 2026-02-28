-- 애널리스트 테이블 스키마
-- 증권사 리포트 기반 시그널 시스템

-- 1. 애널리스트 정보 테이블
CREATE TABLE analysts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL, -- 증권사명
    sector VARCHAR(50), -- 전문 섹터 (반도체, 바이오, 금융 등)
    accuracy_rate DECIMAL(5,2) DEFAULT 0.0, -- 적중률 (%)
    total_reports INTEGER DEFAULT 0,
    successful_predictions INTEGER DEFAULT 0,
    avg_return DECIMAL(8,2) DEFAULT 0.0, -- 평균 수익률 (%)
    experience_years INTEGER DEFAULT 0, -- 경력 연수
    profile_image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 리포트 테이블
CREATE TABLE analyst_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analyst_id UUID REFERENCES analysts(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    target_price INTEGER, -- 목표주가
    current_price INTEGER, -- 발행 당시 주가
    investment_opinion VARCHAR(50) NOT NULL, -- 투자의견 (매수, 중립, 매도)
    previous_target_price INTEGER, -- 이전 목표주가
    previous_opinion VARCHAR(50), -- 이전 투자의견
    upside_potential DECIMAL(5,2), -- 상승여력 (%)
    report_url TEXT, -- 리포트 원문 링크
    summary TEXT, -- 리포트 요약
    key_points JSONB, -- 핵심 포인트들 (배열)
    published_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_analyst_reports_stock (stock_code),
    INDEX idx_analyst_reports_analyst (analyst_id),
    INDEX idx_analyst_reports_date (published_at DESC)
);

-- 3. 리포트 기반 시그널 테이블
CREATE TABLE analyst_signals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    report_id UUID REFERENCES analyst_reports(id) ON DELETE CASCADE,
    analyst_id UUID REFERENCES analysts(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    signal_type VARCHAR(20) NOT NULL, -- BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL
    confidence_level VARCHAR(10) NOT NULL, -- high, medium, low
    rationale TEXT, -- 근거/이유
    target_price INTEGER,
    stop_loss INTEGER, -- 손절가
    time_horizon VARCHAR(20), -- 투자 기간 (단기, 중기, 장기)
    sector VARCHAR(50),
    market_cap_category VARCHAR(20), -- 대형주, 중형주, 소형주
    risk_level VARCHAR(10), -- high, medium, low
    published_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ, -- 시그널 만료일
    status VARCHAR(20) DEFAULT 'active', -- active, hit, stopped, expired
    actual_return DECIMAL(8,2), -- 실제 수익률 (종료 시)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_analyst_signals_stock (stock_code),
    INDEX idx_analyst_signals_analyst (analyst_id),
    INDEX idx_analyst_signals_type (signal_type),
    INDEX idx_analyst_signals_date (published_at DESC)
);

-- 4. 애널리스트 성과 추적 테이블
CREATE TABLE analyst_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analyst_id UUID REFERENCES analysts(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    signal_id UUID REFERENCES analyst_signals(id) ON DELETE CASCADE,
    entry_price INTEGER NOT NULL,
    exit_price INTEGER,
    return_rate DECIMAL(8,2), -- 수익률 (%)
    hit_target BOOLEAN DEFAULT FALSE, -- 목표가 달성 여부
    days_to_target INTEGER, -- 목표가까지 걸린 일수
    max_drawdown DECIMAL(8,2), -- 최대 하락률
    entry_date DATE NOT NULL,
    exit_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_performance_analyst (analyst_id),
    INDEX idx_performance_date (entry_date DESC)
);

-- 5. RLS (Row Level Security) 정책
ALTER TABLE analysts ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyst_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyst_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyst_performance ENABLE ROW LEVEL SECURITY;

-- 읽기 전용 정책 (익명 사용자)
CREATE POLICY "Public read access for analysts" ON analysts FOR SELECT USING (true);
CREATE POLICY "Public read access for reports" ON analyst_reports FOR SELECT USING (true);
CREATE POLICY "Public read access for signals" ON analyst_signals FOR SELECT USING (true);
CREATE POLICY "Public read access for performance" ON analyst_performance FOR SELECT USING (true);

-- 6. 업데이트 트리거 (updated_at 자동 갱신)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_analysts_updated_at BEFORE UPDATE ON analysts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 샘플 데이터 삽입
INSERT INTO analysts (name, company, sector, accuracy_rate, total_reports, successful_predictions, avg_return, experience_years) VALUES
('김선우', '한국투자증권', '반도체', 72.5, 45, 33, 8.3, 7),
('이미래', '삼성증권', '바이오', 68.2, 38, 26, 6.7, 5),
('박테크', 'NH투자증권', '테크', 74.1, 52, 39, 9.1, 9),
('최금융', '대신증권', '금융', 69.8, 41, 29, 7.2, 6),
('정에너지', 'KB증권', '에너지', 71.3, 33, 24, 8.8, 8);