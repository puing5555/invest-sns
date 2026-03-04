-- Supabase: disclosures 테이블 생성 SQL
CREATE TABLE IF NOT EXISTS disclosures (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  corp_name text NOT NULL,
  corp_code text,
  stock_code text,
  market text CHECK (market IN ('kospi', 'kosdaq')),
  report_nm text NOT NULL,
  rcept_no text UNIQUE NOT NULL,
  rcept_dt date NOT NULL,
  disclosure_type text,
  importance text CHECK (importance IN ('high', 'medium', 'low')) DEFAULT 'medium',
  ai_summary text,
  ai_impact text CHECK (ai_impact IN ('긍정', '부정', '중립')),
  ai_impact_reason text,
  ai_score integer CHECK (ai_score >= 0 AND ai_score <= 100),
  source text DEFAULT 'dart',
  created_at timestamptz DEFAULT now()
);

-- RLS
ALTER TABLE disclosures ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read" ON disclosures FOR SELECT USING (true);

-- Index
CREATE INDEX idx_disclosures_rcept_dt ON disclosures (rcept_dt DESC);
CREATE INDEX idx_disclosures_corp_code ON disclosures (corp_code);
CREATE INDEX idx_disclosures_ai_impact ON disclosures (ai_impact);
