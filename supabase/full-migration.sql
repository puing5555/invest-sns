-- ============================================
-- invest-sns 전체 DB 스키마
-- Supabase SQL Editor에서 실행
-- ============================================

-- 1. disclosures 기본 테이블 생성
CREATE TABLE IF NOT EXISTS public.disclosures (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  dart_id TEXT UNIQUE,
  corp_name TEXT NOT NULL,
  title TEXT NOT NULL,
  disclosure_type TEXT,
  report_url TEXT,
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.disclosures ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Disclosures are public" ON public.disclosures 
  FOR SELECT USING (true);

-- 2. disclosures 크롤러용 컬럼 추가
ALTER TABLE public.disclosures 
  ADD COLUMN IF NOT EXISTS stock_code TEXT,
  ADD COLUMN IF NOT EXISTS grade TEXT,
  ADD COLUMN IF NOT EXISTS sentiment TEXT,
  ADD COLUMN IF NOT EXISTS ai_one_liner TEXT,
  ADD COLUMN IF NOT EXISTS corp_cls TEXT;

-- 3. disclosures INSERT/UPDATE 정책
CREATE POLICY "Allow insert for anon" ON public.disclosures
  FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update for anon" ON public.disclosures
  FOR UPDATE USING (true);

-- 4. disclosure_analysis 테이블
CREATE TABLE IF NOT EXISTS public.disclosure_analysis (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  disclosure_id UUID REFERENCES public.disclosures(id),
  analysis_text TEXT,
  impact_score INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.disclosure_analysis ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Disclosure analysis is public" ON public.disclosure_analysis 
  FOR SELECT USING (true);
CREATE POLICY "Allow insert disclosure analysis" ON public.disclosure_analysis 
  FOR INSERT WITH CHECK (true);

-- 5. 크롤링 로그 테이블
CREATE TABLE IF NOT EXISTS public.crawl_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  crawl_type TEXT NOT NULL,
  date_range TEXT NOT NULL,
  total_fetched INT DEFAULT 0,
  total_saved INT DEFAULT 0,
  a_grade INT DEFAULT 0,
  b_grade INT DEFAULT 0,
  c_grade INT DEFAULT 0,
  status TEXT DEFAULT 'running',
  error_message TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

ALTER TABLE public.crawl_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Crawl logs are public" ON public.crawl_logs FOR SELECT USING (true);
CREATE POLICY "Allow insert crawl logs" ON public.crawl_logs FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update crawl logs" ON public.crawl_logs FOR UPDATE USING (true);

-- 6. 인덱스
CREATE INDEX IF NOT EXISTS idx_disclosures_stock_code ON public.disclosures(stock_code);
CREATE INDEX IF NOT EXISTS idx_disclosures_grade ON public.disclosures(grade);
CREATE INDEX IF NOT EXISTS idx_disclosures_submitted ON public.disclosures(submitted_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_disclosures_dart_id ON public.disclosures(dart_id);
