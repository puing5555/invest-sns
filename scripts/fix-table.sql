-- Drop existing table and recreate with flat schema
DROP TABLE IF EXISTS analyst_reports CASCADE;

CREATE TABLE analyst_reports (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  ticker text NOT NULL,
  analyst_name text,
  firm text NOT NULL,
  title text NOT NULL,
  target_price integer,
  opinion text,
  published_at date NOT NULL,
  pdf_url text,
  summary text,
  ai_summary text,
  created_at timestamptz DEFAULT now(),
  UNIQUE(ticker, firm, published_at, title)
);

CREATE INDEX idx_analyst_reports_ticker ON analyst_reports(ticker);
CREATE INDEX idx_analyst_reports_published_at ON analyst_reports(published_at DESC);

ALTER TABLE analyst_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read" ON analyst_reports FOR SELECT USING (true);
CREATE POLICY "Allow service insert" ON analyst_reports FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service update" ON analyst_reports FOR UPDATE USING (true);
