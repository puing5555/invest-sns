-- signal_reports 테이블 생성
CREATE TABLE IF NOT EXISTS signal_reports (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  signal_id uuid REFERENCES influencer_signals(id),
  reason text NOT NULL,  -- '시그널이 틀림' / '종목명 오류' / '발언 내용 왜곡' / '기타'
  detail text,  -- 기타 선택 시 텍스트
  created_at timestamptz DEFAULT now(),
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'resolved'))
);

-- RLS 활성화
ALTER TABLE signal_reports ENABLE ROW LEVEL SECURITY;

-- 정책 생성
CREATE POLICY "Anyone can insert reports" ON signal_reports FOR INSERT WITH CHECK (true);
CREATE POLICY "Anyone can read reports" ON signal_reports FOR SELECT USING (true);
CREATE POLICY "Anyone can update reports" ON signal_reports FOR UPDATE USING (true);