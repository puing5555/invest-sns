-- ===================================================================
-- INFLUENCER SIGNALS V9 완전 마이그레이션 SQL (v2)
-- 생성일: 2026-02-27
-- 포함: 테이블 4개 + speakers + 코린이아빠 + 삼프로TV 데이터
-- ===================================================================

DROP TABLE IF EXISTS influencer_signals CASCADE;
DROP TABLE IF EXISTS influencer_videos CASCADE;
DROP TABLE IF EXISTS influencer_channels CASCADE;
DROP TABLE IF EXISTS speakers CASCADE;

-- ===================================================================
-- 1. SPEAKERS 테이블
-- ===================================================================
CREATE TABLE public.speakers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  aliases TEXT[],
  profile_url TEXT,
  bio TEXT,
  total_signals INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_speakers_name ON speakers(name);

ALTER TABLE speakers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "speakers_read" ON speakers FOR SELECT USING (true);
CREATE POLICY "speakers_insert" ON speakers FOR INSERT WITH CHECK (true);
CREATE POLICY "speakers_update" ON speakers FOR UPDATE USING (true);

-- ===================================================================
-- 2. INFLUENCER_CHANNELS 테이블
-- ===================================================================
CREATE TABLE public.influencer_channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
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
CREATE INDEX idx_channels_influencer ON influencer_channels(influencer_id);

ALTER TABLE influencer_channels ENABLE ROW LEVEL SECURITY;
CREATE POLICY "channels_read" ON influencer_channels FOR SELECT USING (true);
CREATE POLICY "channels_insert" ON influencer_channels FOR INSERT WITH CHECK (true);
CREATE POLICY "channels_update" ON influencer_channels FOR UPDATE USING (true);

-- ===================================================================
-- 3. INFLUENCER_VIDEOS 테이블
-- ===================================================================
CREATE TABLE public.influencer_videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id UUID REFERENCES influencer_channels(id) ON DELETE CASCADE,
  video_id TEXT NOT NULL UNIQUE,
  title TEXT,
  published_at TIMESTAMPTZ,
  duration_seconds INT,
  has_subtitle BOOLEAN DEFAULT false,
  subtitle_language TEXT DEFAULT 'ko',
  analyzed_at TIMESTAMPTZ,
  pipeline_version TEXT,
  signal_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_videos_channel ON influencer_videos(channel_id);
CREATE INDEX idx_videos_published ON influencer_videos(published_at DESC);
CREATE INDEX idx_videos_pipeline ON influencer_videos(pipeline_version);

ALTER TABLE influencer_videos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "videos_read" ON influencer_videos FOR SELECT USING (true);
CREATE POLICY "videos_insert" ON influencer_videos FOR INSERT WITH CHECK (true);
CREATE POLICY "videos_update" ON influencer_videos FOR UPDATE USING (true);

-- ===================================================================
-- 4. INFLUENCER_SIGNALS 테이블 (V9 CHECK + speaker FK)
-- ===================================================================
CREATE TABLE public.influencer_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID REFERENCES influencer_videos(id) ON DELETE CASCADE,
  speaker TEXT NOT NULL,
  speaker_id UUID REFERENCES speakers(id) ON DELETE SET NULL,
  stock TEXT NOT NULL,
  ticker TEXT,
  market TEXT NOT NULL CHECK (market IN (
    'KR','US','US_ADR','CRYPTO','CRYPTO_DEFI','SECTOR','INDEX','ETF','OTHER'
  )),
  mention_type TEXT NOT NULL CHECK (mention_type IN (
    '결론','논거','뉴스','리포트','교육','티저','보유','컨센서스','세무','차익거래','시나리오'
  )),
  signal TEXT NOT NULL CHECK (signal IN ('매수','긍정','중립','경계','매도')),
  confidence TEXT NOT NULL DEFAULT 'high' CHECK (confidence IN (
    'very_high','high','medium','low','very_low'
  )),
  timestamp TEXT,
  key_quote TEXT,
  reasoning TEXT,
  review_status TEXT DEFAULT 'pending' CHECK (review_status IN (
    'pending','approved','rejected','modified'
  )),
  reviewed_by TEXT,
  reviewed_at TIMESTAMPTZ,
  review_note TEXT,
  pipeline_version TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_video ON influencer_signals(video_id);
CREATE INDEX idx_signals_speaker_id ON influencer_signals(speaker_id);
CREATE INDEX idx_signals_stock ON influencer_signals(stock);
CREATE INDEX idx_signals_speaker ON influencer_signals(speaker);
CREATE INDEX idx_signals_signal ON influencer_signals(signal);
CREATE INDEX idx_signals_market ON influencer_signals(market);
CREATE INDEX idx_signals_review ON influencer_signals(review_status);
CREATE INDEX idx_signals_created ON influencer_signals(created_at DESC);

ALTER TABLE influencer_signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "signals_read" ON influencer_signals FOR SELECT USING (true);
CREATE POLICY "signals_insert" ON influencer_signals FOR INSERT WITH CHECK (true);
CREATE POLICY "signals_update" ON influencer_signals FOR UPDATE USING (true);

-- ===================================================================
-- 5. 트리거
-- ===================================================================
CREATE OR REPLACE FUNCTION update_updated_at() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_speakers_updated BEFORE UPDATE ON speakers FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_channels_updated BEFORE UPDATE ON influencer_channels FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_signals_updated BEFORE UPDATE ON influencer_signals FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- signal_count 자동 업데이트
CREATE OR REPLACE FUNCTION update_video_signal_count() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE influencer_videos SET signal_count = signal_count + 1 WHERE id = NEW.video_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE influencer_videos SET signal_count = GREATEST(signal_count - 1, 0) WHERE id = OLD.video_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_signal_count AFTER INSERT OR DELETE ON influencer_signals
FOR EACH ROW EXECUTE FUNCTION update_video_signal_count();

-- speaker total_signals 자동 업데이트
CREATE OR REPLACE FUNCTION update_speaker_signal_count() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' AND NEW.speaker_id IS NOT NULL THEN
    UPDATE speakers SET total_signals = total_signals + 1 WHERE id = NEW.speaker_id;
  ELSIF TG_OP = 'DELETE' AND OLD.speaker_id IS NOT NULL THEN
    UPDATE speakers SET total_signals = GREATEST(total_signals - 1, 0) WHERE id = OLD.speaker_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_speaker_count AFTER INSERT OR DELETE ON influencer_signals
FOR EACH ROW EXECUTE FUNCTION update_speaker_signal_count();

-- ===================================================================
-- 6. SPEAKERS 데이터
-- ===================================================================
INSERT INTO speakers (name, aliases, bio) VALUES
  ('코린이 아빠', ARRAY['코린이아빠','corinpapa','코린이 아빠의 투자일기'], '크립토 분석 유튜버'),
  ('박병창', ARRAY['박병창 이사','교보증권 박병창'], '교보증권 재산관리전략부 이사'),
  ('김장열', ARRAY['김장열 본부장'], '반도체 테크 세션 진행자'),
  ('배재원', ARRAY['배제원'], '더블업 시장전망 패널'),
  ('고연수', ARRAY[], '증권업종 분석가'),
  ('박명성', ARRAY['박명석','글로벌 시황맨','글로벌시황맨'], '글로벌 시황 진행자'),
  ('김장년', ARRAY['김장년 본부장','유니스토리 김장년'], '유니스토리자산운용 본부장'),
  ('장우진', ARRAY['장우진 작가'], '여의도 인사이트 게스트'),
  ('이건희', ARRAY['이건희 대표','이권희'], '클로징벨 게스트'),
  ('김동훈', ARRAY['김동훈 대리','NH증권 김동훈'], 'NH증권 대리'),
  ('박지훈', ARRAY['박지훈 부장'], '아침앤투자 게스트');

-- ===================================================================
-- 7. 채널 데이터
-- ===================================================================
INSERT INTO influencer_channels (channel_name, channel_handle, channel_url, platform, subscriber_count, description) VALUES
  ('코린이 아빠의 투자일기', '@corinpapa1106', 'https://www.youtube.com/@corinpapa1106', 'youtube', 50000, '크립토 투자 분석'),
  ('삼프로TV', '@3protv', 'https://www.youtube.com/@3protv', 'youtube', 2000000, '주식 투자 전문 방송');

-- ===================================================================
-- 8. 영상 데이터
-- ===================================================================
-- 코린이 아빠 영상
INSERT INTO influencer_videos (channel_id, video_id, title, has_subtitle, analyzed_at, pipeline_version)
SELECT c.id, v.vid, v.title, true, NOW(), 'V5'
FROM influencer_channels c,
(VALUES
  ('82TEaq8GIfc', '캔톤, 업비트 상장 초읽기'),
  ('PGQW7nyoRRI', '캔톤이 기관 전용 코인?'),
  ('XxlsTMRDR_o', '비트코인 에너지 흡수하는 캔톤'),
  ('pRTYEzspqyU', '이더 에너지 흡수하는 캔톤'),
  ('IiPJSJ42H4o', '리플 에너지 흡수하는 캔톤'),
  ('awXkJ9hK-a0', '캔톤이 다크코인?'),
  ('TjKVuAGhC1M', '명료법 무기한 연기의 여파'),
  ('Vy2jrX-uCbY', 'AI 버블 붕괴에도 캔톤이 살아남는 이유'),
  ('3eeUC7UBaG4', '트럼프 가문과 캔톤 네트워크'),
  ('A7qHwvcGh9A', '실적이 중요한 거야 바보야'),
  ('7AaksU-R3dg', 'XRP 헤어질 결심')
) AS v(vid, title)
WHERE c.channel_handle = '@corinpapa1106';

-- 삼프로TV 영상 (V7 분석된 실제 영상들)
INSERT INTO influencer_videos (channel_id, video_id, title, has_subtitle, analyzed_at, pipeline_version)
SELECT c.id, v.vid, v.title, true, NOW(), 'V7'
FROM influencer_channels c,
(VALUES
  ('R6w3T3eUVIs', '더블업 시장전망'),
  ('hxpOT8n_ICw', '더블업 증권업종'),
  ('-US4r1E1kOQ', '엔비디아 실적 분석'),
  ('XFHD_1M3Mxg', 'NH증권 신세계 분석'),
  ('ldT75QwBB6g', '아침앤투자'),
  ('x0TKvrIdIwI', '여의도 인사이트 박병창'),
  ('irK0YCnox78', '김장열 반도체 테크'),
  ('I4Tt3tevuTU', '클로징벨 라이브'),
  ('qYAiv0Kljas', '클로징벨 김장열 이건희'),
  ('8-hYd-8eojE', '여의도 인사이트 장우진')
) AS v(vid, title)
WHERE c.channel_handle = '@3protv';

-- ===================================================================
-- 9. 시그널 데이터 — 코린이 아빠 (실제 V5 분석 시그널)
-- ===================================================================
INSERT INTO influencer_signals (video_id, speaker, speaker_id, stock, ticker, market, mention_type, signal, confidence, timestamp, key_quote, reasoning, pipeline_version, review_status)
SELECT
  vd.id, s.speaker, sp.id, s.stock, s.ticker, s.market, s.mention_type, s.signal, s.confidence, s.ts, s.key_quote, s.reasoning, 'V5', 'approved'
FROM (VALUES
  ('82TEaq8GIfc','코린이 아빠','CC','CC','CRYPTO','결론','매수','high','05:30','업비트 상장 시간 문제. 삼성이 선택한 건 캔톤','삼성 파트너십+업비트 상장 분석'),
  ('PGQW7nyoRRI','코린이 아빠','CC','CC','CRYPTO','결론','매수','high','04:15','캔톤이 기관 전용? 개인도 쉽게 접근 가능','접근성 개선'),
  ('XxlsTMRDR_o','코린이 아빠','CC','CC','CRYPTO','결론','매수','high','08:20','비트코인 희소성 흡수한 캔톤','BTC 특성 흡수 기술적 진화'),
  ('pRTYEzspqyU','코린이 아빠','CC','CC','CRYPTO','결론','매수','high','12:45','이더리움 스마트계약 뛰어넘는 캔톤 RWA','ETH 대비 우위 RWA 선점'),
  ('IiPJSJ42H4o','코린이 아빠','CC','CC','CRYPTO','결론','매수','high','07:10','리플 결제시스템 학습한 캔톤 기관 솔루션','XRP 벤치마킹 기관 확대'),
  ('awXkJ9hK-a0','코린이 아빠','CC','CC','CRYPTO','논거','긍정','medium','06:35','허가형 블록체인이 미국 정부가 원하는 방향','규제 친화적 구조'),
  ('TjKVuAGhC1M','코린이 아빠','CC','CC','CRYPTO','뉴스','긍정','medium','09:15','코인베이스가 반대하는 이유가 캔톤 위협','경쟁사 견제로 시장 지위 확인'),
  ('Vy2jrX-uCbY','코린이 아빠','CC','CC','CRYPTO','결론','매수','high','10:30','AI 버블 터져도 캔톤은 실체 있는 솔루션','펀더멘털 기반 안정성'),
  ('3eeUC7UBaG4','코린이 아빠','CC','CC','CRYPTO','논거','매수','high','08:45','트럼프 RWA 전략에 캔톤 핵심','정치적 배경+정책 연계'),
  ('A7qHwvcGh9A','코린이 아빠','BTC','BTC','CRYPTO','논거','경계','medium','05:20','실적 없는 코인 정리 시점, 캔톤은 다르다','시장 선별 차별화'),
  ('7AaksU-R3dg','코린이 아빠','XRP','XRP','CRYPTO','결론','매도','high','03:45','XRP 헤어질 시간. 캔톤으로 갈아타야','XRP→CC 전환 필요')
) AS s(vid, speaker, stock, ticker, market, mention_type, signal, confidence, ts, key_quote, reasoning)
JOIN influencer_videos vd ON vd.video_id = s.vid
JOIN speakers sp ON sp.name = s.speaker;

-- ===================================================================
-- 10. 시그널 데이터 — 삼프로TV V7 (실제 20개 시그널)
-- ===================================================================
INSERT INTO influencer_signals (video_id, speaker, speaker_id, stock, ticker, market, mention_type, signal, confidence, timestamp, key_quote, reasoning, pipeline_version, review_status)
SELECT
  vd.id, s.speaker, sp.id, s.stock, s.ticker, s.market, s.mention_type, s.signal, s.confidence, s.ts, s.key_quote, s.reasoning, 'V7', 'approved'
FROM (VALUES
  -- 매수 8개
  ('R6w3T3eUVIs','배재원','삼성전자','005930','KR','결론','매수','high','06:10','비중 없는 분은 지금이라도 물리더라도 들어가야 된다','영업이익 추정치 상향 매도 이유 없음'),
  ('hxpOT8n_ICw','고연수','증권 섹터',NULL,'SECTOR','결론','매수','high','10:18','증권주는 계속 스트롱 바이로 말씀드리고 있고요','증권업 전반 호조'),
  ('-US4r1E1kOQ','김장년','메모리 반도체',NULL,'SECTOR','결론','매수','high','13:17','삼성전자나 SK하이닉스 넷 중 하나는 갖고 있어야지','Agent AI 메모리 수요 증가'),
  ('XFHD_1M3Mxg','김동훈','신세계','004170','KR','결론','매수','high','01:01','이 종목을 가장 좋게 보고 있거든요','인바운드 수혜+자산가치 저평가'),
  ('ldT75QwBB6g','박지훈','효성중공업','298040','KR','결론','매수','high','16:30','효중이 전 대장이라고 봐요 올해도 계속 한다','전력 섹터 대장주'),
  ('ldT75QwBB6g','박지훈','솔브레인','357780','KR','결론','매수','high','27:51','삼총사를 갖고 왔습니다 솔브레인','소재주 1순위'),
  ('ldT75QwBB6g','박지훈','삼성전기','009150','KR','결론','매수','high','25:47','2026년에 대박주를 삼성전기로 선택','피지컬AI 로봇 부품'),
  ('ldT75QwBB6g','박지훈','LG화학','051910','KR','결론','매수','medium','36:11','LG화학 저는 강추입니다','행동주의펀드+PBR 0.8배 저평가'),
  -- 긍정 10개
  ('x0TKvrIdIwI','박병창','반도체소부장',NULL,'SECTOR','결론','긍정','high','09:16','반도체를 끝까지 갖고 가서 수익률 갖고 하는 건 맞고','반도체 소부장 장기보유'),
  ('irK0YCnox78','김장열','삼성전자','005930','KR','결론','긍정','medium','14:21','4월까지는 다운사이드보다 업사이드 더 남아있다','조건부: 4월까지'),
  ('I4Tt3tevuTU','박명성','삼성전자','005930','KR','결론','긍정','high','08:13','2027년 포워드 PER 3-4배 계속 가도 이상하지 않다','밸류에이션 정당화'),
  ('-US4r1E1kOQ','김장년','엔비디아','NVDA','US','결론','긍정','medium','13:17','안 갖고 있는 사람들은 한 30% 배팅 해놓고','미보유자 포지션 빌드업'),
  ('8-hYd-8eojE','장우진','현대차','005380','KR','결론','긍정','high','42:10','도요타보다도 오히려 더 받아야 된다','로봇/자율주행 밸류'),
  ('qYAiv0Kljas','이건희','현대차','005380','KR','결론','긍정','high','34:58','6만자를 바라볼 가능성 높다','차트+외국인 매수세'),
  ('qYAiv0Kljas','이건희','현대건설','000720','KR','결론','긍정','medium','51:27','현대건설은 업사이드가 더 있다','원전AP1400+SMR'),
  ('ldT75QwBB6g','박지훈','HD현대일렉트릭','267260','KR','결론','긍정','high','16:30','유럽의 수주를 드디어','유럽 수주 기대감'),
  ('ldT75QwBB6g','박지훈','NC소프트','036570','KR','결론','긍정','high','32:04','올해는 충분히 기대를 해 보자','어닝 모멘텀 회복'),
  ('XFHD_1M3Mxg','김동훈','삼성전자','005930','KR','논거','긍정','medium','16:30','삼성전자 34만원 목표주가 상향','신세계 추천 배경 논거'),
  -- 중립 1개
  ('qYAiv0Kljas','김장열','SK하이닉스','000660','KR','리포트','중립','medium','19:29','SK하이닉스 170만원 메커리증권 리포트','리포트 전달'),
  -- 경계 1개
  ('x0TKvrIdIwI','박병창','비반도체섹터',NULL,'SECTOR','결론','경계','medium','09:16','반도체 빼고 나머지는 현금화 좀 하면','비반도체 현금화 권유')
) AS s(vid, speaker, stock, ticker, market, mention_type, signal, confidence, ts, key_quote, reasoning)
JOIN influencer_videos vd ON vd.video_id = s.vid
JOIN speakers sp ON sp.name = s.speaker;

-- ===================================================================
-- 완료 확인
-- ===================================================================
SELECT '=== 마이그레이션 완료 ===' AS status;
SELECT 'speakers' AS tbl, COUNT(*) AS cnt FROM speakers
UNION ALL SELECT 'channels', COUNT(*) FROM influencer_channels
UNION ALL SELECT 'videos', COUNT(*) FROM influencer_videos
UNION ALL SELECT 'signals', COUNT(*) FROM influencer_signals;
