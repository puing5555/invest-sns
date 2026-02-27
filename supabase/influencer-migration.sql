-- Supabase 인플루언서 테이블 생성 스크립트
-- 실행일: 2026-02-27
-- 작성자: OpenClaw Agent

-- 1. influencer_channels 테이블 생성
CREATE TABLE IF NOT EXISTS public.influencer_channels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  influencer_id UUID REFERENCES public.influencers(id),
  channel_name TEXT NOT NULL,
  channel_url TEXT,
  platform TEXT DEFAULT 'youtube',
  subscriber_count INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. influencer_videos 테이블 생성
CREATE TABLE IF NOT EXISTS public.influencer_videos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES public.influencer_channels(id),
  video_id TEXT NOT NULL UNIQUE,
  title TEXT,
  published_at TIMESTAMPTZ,
  duration_seconds INT,
  has_subtitle BOOLEAN DEFAULT false,
  analyzed_at TIMESTAMPTZ,
  pipeline_version TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. influencer_signals 테이블 생성
CREATE TABLE IF NOT EXISTS public.influencer_signals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  video_id UUID REFERENCES public.influencer_videos(id),
  speaker TEXT NOT NULL,
  stock TEXT NOT NULL,
  ticker TEXT,
  market TEXT,
  mention_type TEXT,
  signal TEXT NOT NULL,
  confidence TEXT DEFAULT 'high',
  timestamp TEXT,
  key_quote TEXT,
  reasoning TEXT,
  review_status TEXT DEFAULT 'pending',
  reviewed_by TEXT,
  reviewed_at TIMESTAMPTZ,
  pipeline_version TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. RLS 정책 설정 (Row Level Security)

-- influencer_channels 테이블 RLS 정책
ALTER TABLE public.influencer_channels ENABLE ROW LEVEL SECURITY;

CREATE POLICY "influencer_channels_select_policy" ON public.influencer_channels
  FOR SELECT USING (true);

CREATE POLICY "influencer_channels_insert_policy" ON public.influencer_channels
  FOR INSERT WITH CHECK (true);

CREATE POLICY "influencer_channels_update_policy" ON public.influencer_channels
  FOR UPDATE USING (true) WITH CHECK (true);

-- influencer_videos 테이블 RLS 정책
ALTER TABLE public.influencer_videos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "influencer_videos_select_policy" ON public.influencer_videos
  FOR SELECT USING (true);

CREATE POLICY "influencer_videos_insert_policy" ON public.influencer_videos
  FOR INSERT WITH CHECK (true);

CREATE POLICY "influencer_videos_update_policy" ON public.influencer_videos
  FOR UPDATE USING (true) WITH CHECK (true);

-- influencer_signals 테이블 RLS 정책
ALTER TABLE public.influencer_signals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "influencer_signals_select_policy" ON public.influencer_signals
  FOR SELECT USING (true);

CREATE POLICY "influencer_signals_insert_policy" ON public.influencer_signals
  FOR INSERT WITH CHECK (true);

CREATE POLICY "influencer_signals_update_policy" ON public.influencer_signals
  FOR UPDATE USING (true) WITH CHECK (true);

-- 5. 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_influencer_channels_influencer_id ON public.influencer_channels(influencer_id);
CREATE INDEX IF NOT EXISTS idx_influencer_videos_channel_id ON public.influencer_videos(channel_id);
CREATE INDEX IF NOT EXISTS idx_influencer_videos_video_id ON public.influencer_videos(video_id);
CREATE INDEX IF NOT EXISTS idx_influencer_signals_video_id ON public.influencer_signals(video_id);
CREATE INDEX IF NOT EXISTS idx_influencer_signals_stock ON public.influencer_signals(stock);
CREATE INDEX IF NOT EXISTS idx_influencer_signals_signal ON public.influencer_signals(signal);
CREATE INDEX IF NOT EXISTS idx_influencer_signals_review_status ON public.influencer_signals(review_status);

-- 완료
SELECT 'Influencer tables and policies created successfully!' as message;