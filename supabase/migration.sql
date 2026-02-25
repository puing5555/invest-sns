-- ============================================
-- DART 크롤러용 disclosures 테이블 확장
-- Supabase SQL Editor에서 실행
-- ============================================

-- 1. disclosures 테이블에 컬럼 추가
ALTER TABLE public.disclosures 
  ADD COLUMN IF NOT EXISTS stock_code TEXT,
  ADD COLUMN IF NOT EXISTS grade TEXT,              -- A / B / C
  ADD COLUMN IF NOT EXISTS sentiment TEXT,          -- positive / negative / neutral
  ADD COLUMN IF NOT EXISTS ai_one_liner TEXT,       -- AI 한줄 요약
  ADD COLUMN IF NOT EXISTS corp_cls TEXT;            -- Y:유가 K:코스닥

-- 2. disclosures에 서비스용 INSERT 정책 추가 (크롤러가 데이터 넣을 수 있도록)
-- anon key로 insert 가능하게 (나중에 service_role로 변경 권장)
CREATE POLICY "Allow insert for anon" ON public.disclosures
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow update for anon" ON public.disclosures
  FOR UPDATE USING (true);

-- 3. disclosure_analysis에도 서비스용 정책 추가
ALTER TABLE public.disclosure_analysis ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Disclosure analysis is public" ON public.disclosure_analysis 
  FOR SELECT USING (true);
CREATE POLICY "Allow insert disclosure analysis" ON public.disclosure_analysis
  FOR INSERT WITH CHECK (true);

-- 4. dart_id에 UNIQUE 인덱스 확인 (이미 있으면 에러 무시)
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_disclosures_dart_id ON public.disclosures(dart_id);

-- 5. 크롤링 상태 추적 테이블
CREATE TABLE IF NOT EXISTS public.crawl_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  crawl_type TEXT NOT NULL,          -- recent / backfill
  date_range TEXT NOT NULL,          -- "20250224 ~ 20250225"
  total_fetched INT DEFAULT 0,
  total_saved INT DEFAULT 0,
  a_grade INT DEFAULT 0,
  b_grade INT DEFAULT 0,
  c_grade INT DEFAULT 0,
  status TEXT DEFAULT 'running',     -- running / completed / failed
  error_message TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

ALTER TABLE public.crawl_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Crawl logs are public" ON public.crawl_logs FOR SELECT USING (true);
CREATE POLICY "Allow insert crawl logs" ON public.crawl_logs FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update crawl logs" ON public.crawl_logs FOR UPDATE USING (true);

-- 6. stock_code 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_disclosures_stock_code ON public.disclosures(stock_code);
CREATE INDEX IF NOT EXISTS idx_disclosures_grade ON public.disclosures(grade);
CREATE INDEX IF NOT EXISTS idx_disclosures_submitted ON public.disclosures(submitted_at DESC);
