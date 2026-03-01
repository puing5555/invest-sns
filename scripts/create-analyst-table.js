const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  'https://arypzhotxflimroprmdk.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
);

async function main() {
  // Try to create by inserting a dummy and deleting - or just use the REST API
  // Supabase doesn't have exec_sql RPC by default, so let's use the SQL editor approach
  // Instead, we'll just try inserting and see if table exists
  const { error } = await supabase.from('analyst_reports').select('id').limit(1);
  if (error && error.code === '42P01') {
    console.log('Table does not exist. Please create it via Supabase SQL editor:');
    console.log(`
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
  created_at timestamptz DEFAULT now(),
  UNIQUE(ticker, firm, published_at, title)
);

CREATE INDEX idx_analyst_reports_ticker ON analyst_reports(ticker);
CREATE INDEX idx_analyst_reports_published_at ON analyst_reports(published_at DESC);

ALTER TABLE analyst_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read" ON analyst_reports FOR SELECT USING (true);
CREATE POLICY "Allow service insert" ON analyst_reports FOR INSERT WITH CHECK (true);
    `);
  } else if (error) {
    console.log('Error:', error.message);
  } else {
    console.log('Table analyst_reports already exists!');
  }
}

main();
