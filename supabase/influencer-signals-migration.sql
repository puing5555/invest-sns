-- ============================================
-- 인플루언서 시그널 파이프라인 테이블
-- Supabase SQL Editor에서 실행
-- 2026-02-27
-- ============================================

-- ============================================
-- 1. influencer_channels (유튜브 채널)
-- ============================================
CREATE TABLE IF NOT EXISTS public.influencer_channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  influencer_id UUID REFERENCES public.influencers(id) ON DELETE CASCADE,
  channel_name TEXT NOT NULL,
  channel_handle TEXT,              -- @3protv, @corinpapa1106 등
  channel_url TEXT,
  platform TEXT NOT NULL DEFAULT 'youtube',
  subscriber_count INT,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(channel_handle, platform)
);

ALTER TABLE public.influencer_channels ENABLE ROW LEVEL SECURITY;
CREATE POLICY "influencer_channels_select" ON public.influencer_channels FOR SELECT USING (true);
CREATE POLICY "influencer_channels_insert" ON public.influencer_channels FOR INSERT WITH CHECK (true);
CREATE POLICY "influencer_channels_update" ON public.influencer_channels FOR UPDATE USING (true);

CREATE INDEX idx_influencer_channels_influencer ON public.influencer_channels(influencer_id);

-- ============================================
-- 2. influencer_videos (분석된 영상)
-- ============================================
CREATE TABLE IF NOT EXISTS public.influencer_videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id UUID REFERENCES public.influencer_channels(id) ON DELETE CASCADE,
  video_id TEXT NOT NULL,           -- YouTube video ID (예: x0TKvrIdIwI)
  title TEXT,
  published_at TIMESTAMPTZ,
  duration_seconds INT,
  has_subtitle BOOLEAN DEFAULT false,
  subtitle_language TEXT DEFAULT 'ko',
  analyzed_at TIMESTAMPTZ,
  pipeline_version TEXT,            -- 'V7', 'V8' 등
  signal_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(video_id)
);

ALTER TABLE public.influencer_videos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "influencer_videos_select" ON public.influencer_videos FOR SELECT USING (true);
CREATE POLICY "influencer_videos_insert" ON public.influencer_videos FOR INSERT WITH CHECK (true);
CREATE POLICY "influencer_videos_update" ON public.influencer_videos FOR UPDATE USING (true);

CREATE INDEX idx_influencer_videos_channel ON public.influencer_videos(channel_id);
CREATE INDEX idx_influencer_videos_pipeline ON public.influencer_videos(pipeline_version);
CREATE INDEX idx_influencer_videos_published ON public.influencer_videos(published_at DESC);

-- ============================================
-- 3. influencer_signals (종목 신호)
-- ============================================
CREATE TABLE IF NOT EXISTS public.influencer_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID REFERENCES public.influencer_videos(id) ON DELETE CASCADE,
  
  -- V7 파이프라인 출력 필드
  speaker TEXT NOT NULL,
  stock TEXT NOT NULL,
  ticker TEXT,                      -- 005930, NVDA 등
  market TEXT NOT NULL CHECK (market IN (
    'KR', 'US', 'JP', 'CN', 'CRYPTO', 'SECTOR', 'INDEX', 'ETF', 'MACRO', 'OTHER'
  )),
  mention_type TEXT NOT NULL CHECK (mention_type IN (
    '결론', '논거', '뉴스', '리포트', '교육', '티저', '보유', '컨센서스'
  )),
  signal TEXT NOT NULL CHECK (signal IN (
    '매수', '긍정', '중립', '경계', '매도'
  )),
  confidence TEXT NOT NULL DEFAULT 'high' CHECK (confidence IN (
    'high', 'medium', 'low'
  )),
  timestamp TEXT,                   -- 영상 내 타임스탬프 (예: "12:34")
  key_quote TEXT,
  reasoning TEXT,
  
  -- 리뷰/검증
  review_status TEXT DEFAULT 'pending' CHECK (review_status IN (
    'pending', 'approved', 'rejected', 'modified'
  )),
  reviewed_by TEXT,                 -- 'human', 'opus', 'auto'
  reviewed_at TIMESTAMPTZ,
  review_note TEXT,
  
  -- 메타
  pipeline_version TEXT,            -- 'V7', 'V8' 등
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.influencer_signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "influencer_signals_select" ON public.influencer_signals FOR SELECT USING (true);
CREATE POLICY "influencer_signals_insert" ON public.influencer_signals FOR INSERT WITH CHECK (true);
CREATE POLICY "influencer_signals_update" ON public.influencer_signals FOR UPDATE USING (true);

CREATE INDEX idx_influencer_signals_video ON public.influencer_signals(video_id);
CREATE INDEX idx_influencer_signals_stock ON public.influencer_signals(stock);
CREATE INDEX idx_influencer_signals_speaker ON public.influencer_signals(speaker);
CREATE INDEX idx_influencer_signals_signal ON public.influencer_signals(signal);
CREATE INDEX idx_influencer_signals_market ON public.influencer_signals(market);
CREATE INDEX idx_influencer_signals_review ON public.influencer_signals(review_status);
CREATE INDEX idx_influencer_signals_pipeline ON public.influencer_signals(pipeline_version);

-- ============================================
-- 4. updated_at 자동 업데이트 트리거
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_influencer_channels_updated
  BEFORE UPDATE ON public.influencer_channels
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_influencer_signals_updated
  BEFORE UPDATE ON public.influencer_signals
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- 완료! 테이블 3개 + 인덱스 + RLS + 트리거
-- ============================================
