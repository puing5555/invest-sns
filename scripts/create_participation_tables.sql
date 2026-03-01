-- 유저 참여 시스템 1단계 테이블

-- 기존 signal_reports 테이블에 AI 관련 컬럼 추가
ALTER TABLE signal_reports ADD COLUMN IF NOT EXISTS ai_review text;
ALTER TABLE signal_reports ADD COLUMN IF NOT EXISTS ai_suggestion text;

-- 시그널 좋아요 테이블
CREATE TABLE IF NOT EXISTS signal_votes (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  signal_id uuid REFERENCES influencer_signals(id),
  vote_type text DEFAULT 'like',
  memo text,
  created_at timestamptz DEFAULT now(),
  UNIQUE(signal_id, id)
);

ALTER TABLE signal_votes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can insert votes" ON signal_votes FOR INSERT WITH CHECK (true);
CREATE POLICY "Anyone can read votes" ON signal_votes FOR SELECT USING (true);

-- 시그널 메모 테이블
CREATE TABLE IF NOT EXISTS signal_memos (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  signal_id uuid REFERENCES influencer_signals(id),
  user_id text,
  memo text NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE signal_memos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can insert memos" ON signal_memos FOR INSERT WITH CHECK (true);
CREATE POLICY "Anyone can read memos" ON signal_memos FOR SELECT USING (true);