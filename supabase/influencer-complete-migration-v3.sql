-- ============================================
-- 인플루언서 시그널 파이프라인 - Complete Migration V3
-- speakers 테이블 추가, REAL_ESTATE/JP/CN/MACRO 제거, 더미 데이터 제거
-- 2026-02-27
-- ============================================

-- ============================================
-- 0. speakers (발언자 - 채널과 독립)
-- ============================================
CREATE TABLE IF NOT EXISTS public.speakers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  aliases TEXT[] DEFAULT '{}',       -- 같은 사람 다른 표기 대응
  profile_image_url TEXT,
  bio TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.speakers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "speakers_select" ON public.speakers FOR SELECT USING (true);
CREATE POLICY "speakers_insert" ON public.speakers FOR INSERT WITH CHECK (true);
CREATE POLICY "speakers_update" ON public.speakers FOR UPDATE USING (true);

CREATE INDEX idx_speakers_name ON public.speakers(name);
CREATE INDEX idx_speakers_aliases ON public.speakers USING GIN(aliases);

-- ============================================
-- 1. influencer_channels (유튜브 채널)
-- ============================================
CREATE TABLE IF NOT EXISTS public.influencer_channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_name TEXT NOT NULL,
  channel_handle TEXT,
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

-- ============================================
-- 2. influencer_videos (분석된 영상)
-- ============================================
CREATE TABLE IF NOT EXISTS public.influencer_videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id UUID REFERENCES public.influencer_channels(id) ON DELETE CASCADE,
  video_id TEXT NOT NULL,
  title TEXT,
  published_at TIMESTAMPTZ,
  duration_seconds INT,
  has_subtitle BOOLEAN DEFAULT false,
  subtitle_language TEXT DEFAULT 'ko',
  analyzed_at TIMESTAMPTZ,
  pipeline_version TEXT,
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
  speaker_id UUID REFERENCES public.speakers(id) ON DELETE SET NULL,

  stock TEXT NOT NULL,
  ticker TEXT,
  market TEXT NOT NULL CHECK (market IN (
    'KR', 'US', 'US_ADR', 'CRYPTO', 'CRYPTO_DEFI', 'SECTOR', 'INDEX', 'ETF', 'OTHER'
  )),
  mention_type TEXT NOT NULL CHECK (mention_type IN (
    '결론', '논거', '뉴스', '리포트', '교육', '티저', '보유', '컨센서스', '세무', '차익거래', '시나리오'
  )),
  signal TEXT NOT NULL CHECK (signal IN (
    '매수', '긍정', '중립', '경계', '매도'
  )),
  confidence TEXT NOT NULL DEFAULT 'high' CHECK (confidence IN (
    'very_high', 'high', 'medium', 'low', 'very_low'
  )),
  timestamp TEXT,
  key_quote TEXT,
  reasoning TEXT,

  review_status TEXT DEFAULT 'pending' CHECK (review_status IN (
    'pending', 'approved', 'rejected', 'modified'
  )),
  reviewed_by TEXT,
  reviewed_at TIMESTAMPTZ,
  review_note TEXT,

  pipeline_version TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.influencer_signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "influencer_signals_select" ON public.influencer_signals FOR SELECT USING (true);
CREATE POLICY "influencer_signals_insert" ON public.influencer_signals FOR INSERT WITH CHECK (true);
CREATE POLICY "influencer_signals_update" ON public.influencer_signals FOR UPDATE USING (true);

CREATE INDEX idx_influencer_signals_video ON public.influencer_signals(video_id);
CREATE INDEX idx_influencer_signals_speaker ON public.influencer_signals(speaker_id);
CREATE INDEX idx_influencer_signals_stock ON public.influencer_signals(stock);
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
-- 5. 발언자 데이터 (실제 인물만)
-- ============================================

-- 삼프로TV 발언자
INSERT INTO public.speakers (name, aliases) VALUES
  ('배재원', ARRAY['배재원']),
  ('고연수', ARRAY['고연수']),
  ('김장년', ARRAY['김장년', '김장년 부장']),
  ('김동훈', ARRAY['김동훈']),
  ('박지훈', ARRAY['박지훈']),
  ('박병창', ARRAY['박병창', '박병창 부장']),
  ('김장열', ARRAY['김장열']),
  ('박명성', ARRAY['박명성', '박명석', '글로벌 시황맨']),
  ('장우진', ARRAY['장우진']),
  ('이건희', ARRAY['이건희', '이권희'])
ON CONFLICT (name) DO NOTHING;

-- 코린이 아빠 발언자
INSERT INTO public.speakers (name, aliases) VALUES
  ('코린이 아빠', ARRAY['코린이 아빠', '코린파파', '코린이아빠'])
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 6. 채널 데이터
-- ============================================
INSERT INTO public.influencer_channels (channel_name, channel_handle, channel_url, platform) VALUES
  ('삼프로TV', '@3protv', 'https://www.youtube.com/@3protv', 'youtube'),
  ('코린이 아빠', '@corinpapa1106', 'https://www.youtube.com/@corinpapa1106', 'youtube')
ON CONFLICT (channel_handle, platform) DO NOTHING;

-- ============================================
-- 7. 삼프로TV 실제 영상 (시그널 있는 10개만)
-- ============================================
INSERT INTO public.influencer_videos (channel_id, video_id, title, pipeline_version, signal_count, analyzed_at) VALUES
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   'R6w3T3eUVIs', '배재원 - 삼성전자/코스피', 'V7', 1, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   'hxpOT8n_ICw', '고연수 - 증권 섹터', 'V7', 1, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   '-US4r1E1kOQ', '김장년 - 메모리반도체/엔비디아', 'V7', 2, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   'XFHD_1M3Mxg', '김동훈 - 신세계/삼성전자', 'V7', 2, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   'ldT75QwBB6g', '박지훈 - 효성중공업 외 5종목', 'V7', 6, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   'x0TKvrIdIwI', '박병창 - 반도체/비반도체', 'V7', 2, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   'irK0YCnox78', '김장열 - 삼성전자', 'V7', 1, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   'qYAiv0Kljas', '이건희/김장열 - 현대차/현대건설/SK하이닉스', 'V7', 3, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   'I4Tt3tevuTU', '박명성 - 삼성전자', 'V7', 1, NOW()),
  ((SELECT id FROM public.influencer_channels WHERE channel_handle = '@3protv'),
   '8-hYd-8eojE', '장우진 - 현대차', 'V7', 1, NOW())
ON CONFLICT (video_id) DO NOTHING;

-- ============================================
-- 8. 삼프로TV V7 실제 시그널 (20개)
-- ============================================

-- 매수 8개
INSERT INTO public.influencer_signals (video_id, speaker_id, stock, market, mention_type, signal, confidence, timestamp, key_quote, pipeline_version) VALUES
  ((SELECT id FROM public.influencer_videos WHERE video_id = 'R6w3T3eUVIs'),
   (SELECT id FROM public.speakers WHERE name = '배재원'),
   '삼성전자', 'KR', '결론', '매수', 'high', '06:10',
   '비중 없는 분은 지금이라도 물리더라도 들어가야 된다', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'hxpOT8n_ICw'),
   (SELECT id FROM public.speakers WHERE name = '고연수'),
   '증권 섹터', 'SECTOR', '결론', '매수', 'high', '06:12',
   '증권주는 계속 스트롱 바이로 말씀드리고 있고요', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = '-US4r1E1kOQ'),
   (SELECT id FROM public.speakers WHERE name = '김장년'),
   '메모리 반도체', 'SECTOR', '결론', '매수', 'high', '13:17',
   '삼성전자나 SK하이닉스, 샌디스크, 마이크론 넷 중에 하나는 갖고 있어야지', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'XFHD_1M3Mxg'),
   (SELECT id FROM public.speakers WHERE name = '김동훈'),
   '신세계', 'KR', '결론', '매수', 'high', '08:15',
   '이 종목을 가장 좋게 보고 있거든요', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'ldT75QwBB6g'),
   (SELECT id FROM public.speakers WHERE name = '박지훈'),
   '효성중공업', 'KR', '결론', '매수', 'high', NULL,
   '효중이 전 대장이라고 봐요... 올해도 계속 한다', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'ldT75QwBB6g'),
   (SELECT id FROM public.speakers WHERE name = '박지훈'),
   '솔브레인', 'KR', '결론', '매수', 'high', NULL,
   '삼총사를 갖고 왔습니다... 솔브레인', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'ldT75QwBB6g'),
   (SELECT id FROM public.speakers WHERE name = '박지훈'),
   '삼성전기', 'KR', '결론', '매수', 'high', NULL,
   '2026년에 대박주를 저 삼성전기로 선택', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'ldT75QwBB6g'),
   (SELECT id FROM public.speakers WHERE name = '박지훈'),
   'LG화학', 'KR', '결론', '매수', 'medium', '36:11',
   'LG화학 저는 강추입니다', 'V7');

-- 긍정 10개
INSERT INTO public.influencer_signals (video_id, speaker_id, stock, market, mention_type, signal, confidence, timestamp, key_quote, pipeline_version) VALUES
  ((SELECT id FROM public.influencer_videos WHERE video_id = 'x0TKvrIdIwI'),
   (SELECT id FROM public.speakers WHERE name = '박병창'),
   '반도체소부장', 'SECTOR', '결론', '긍정', 'high', '13:19',
   '반도체를 끝까지 갖고 가서 수익률을 갖고 하는 건 분명히 맞고', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'irK0YCnox78'),
   (SELECT id FROM public.speakers WHERE name = '김장열'),
   '삼성전자', 'KR', '결론', '긍정', 'medium', '13:17',
   '4월까지는 다운사이드보다는 업사이드가 더 남아 있다', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'I4Tt3tevuTU'),
   (SELECT id FROM public.speakers WHERE name = '박명성'),
   '삼성전자', 'KR', '결론', '긍정', 'high', '08:13',
   '2027년 포워드 PER 3-4배, 계속 가도 이상하지 않다', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = '-US4r1E1kOQ'),
   (SELECT id FROM public.speakers WHERE name = '김장년'),
   '엔비디아', 'US', '결론', '긍정', 'medium', NULL,
   '안 갖고 있는 사람들은 한 30% 배팅을 좀 해 놓고', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = '8-hYd-8eojE'),
   (SELECT id FROM public.speakers WHERE name = '장우진'),
   '현대차', 'KR', '결론', '긍정', 'high', '18:30',
   '도요타보다도 오히려 더 받아야 된다', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'qYAiv0Kljas'),
   (SELECT id FROM public.speakers WHERE name = '이건희'),
   '현대차', 'KR', '결론', '긍정', 'high', '13:18',
   '6만자를 바라볼 가능성은 높다', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'qYAiv0Kljas'),
   (SELECT id FROM public.speakers WHERE name = '이건희'),
   '현대건설', 'KR', '결론', '긍정', 'medium', NULL,
   '현대건설은 업사이드가 더 있다', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'ldT75QwBB6g'),
   (SELECT id FROM public.speakers WHERE name = '박지훈'),
   'HD현대일렉트릭', 'KR', '결론', '긍정', 'high', NULL,
   '유럽의 수주를 드디어', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'ldT75QwBB6g'),
   (SELECT id FROM public.speakers WHERE name = '박지훈'),
   'NC소프트', 'KR', '결론', '긍정', 'high', NULL,
   '올해는 충분히 기대를 해 보자', 'V7'),

  ((SELECT id FROM public.influencer_videos WHERE video_id = 'XFHD_1M3Mxg'),
   (SELECT id FROM public.speakers WHERE name = '김동훈'),
   '삼성전자', 'KR', '논거', '긍정', 'medium', '08:15',
   '삼성전자 34만 원 목표주가 상향', 'V7');

-- 중립 1개
INSERT INTO public.influencer_signals (video_id, speaker_id, stock, market, mention_type, signal, confidence, timestamp, key_quote, pipeline_version) VALUES
  ((SELECT id FROM public.influencer_videos WHERE video_id = 'qYAiv0Kljas'),
   (SELECT id FROM public.speakers WHERE name = '김장열'),
   'SK하이닉스', 'KR', '리포트', '중립', 'medium', NULL,
   'SK하이닉스 170만 원 (메커리증권 리포트 전달)', 'V7');

-- 경계 1개
INSERT INTO public.influencer_signals (video_id, speaker_id, stock, market, mention_type, signal, confidence, timestamp, key_quote, pipeline_version) VALUES
  ((SELECT id FROM public.influencer_videos WHERE video_id = 'x0TKvrIdIwI'),
   (SELECT id FROM public.speakers WHERE name = '박병창'),
   '비반도체섹터', 'SECTOR', '결론', '경계', 'medium', '07:12',
   '반도체 빼고 나머지는 현금화 좀 하면', 'V7');

-- ============================================
-- 완료! speakers + channels + videos + signals
-- 테이블 4개 + 인덱스 + RLS + 트리거
-- 더미 데이터 없음. 실제 V7 시그널 20개만.
-- market 9종: KR/US/US_ADR/CRYPTO/CRYPTO_DEFI/SECTOR/INDEX/ETF/OTHER
-- ============================================
