-- ===================================================================
-- INFLUENCER SIGNALS V9 완전 마이그레이션 SQL (스코프 제한 + Speakers)
-- 생성일: 2026-02-27
-- 변경: market 9종 제한 (KR/US/CRYPTO), speakers 테이블 추가, speaker_id FK
-- 포함 내용: 테이블 생성 + 코린이 아빠 + 삼프로TV V7 데이터
-- ===================================================================

-- 기존 테이블 삭제 (있다면)
DROP TABLE IF EXISTS influencer_signals CASCADE;
DROP TABLE IF EXISTS influencer_videos CASCADE;
DROP TABLE IF EXISTS influencer_channels CASCADE;
DROP TABLE IF EXISTS speakers CASCADE;

-- ===================================================================
-- 1. SPEAKERS 테이블 (신규)
-- ===================================================================

CREATE TABLE IF NOT EXISTS public.speakers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    aliases TEXT[],              -- {"이효석", "이효석 아카데미", "효석 아카데미"}
    profile_url TEXT,
    bio TEXT,
    total_signals INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name)
);

-- 인덱스 생성
CREATE INDEX idx_speakers_name ON speakers(name);
CREATE INDEX idx_speakers_total_signals ON speakers(total_signals DESC);

-- RLS 정책
ALTER TABLE speakers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON speakers FOR SELECT USING (true);
CREATE POLICY "Enable insert access for authenticated users" ON speakers FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable update access for authenticated users" ON speakers FOR UPDATE USING (auth.role() = 'authenticated');

-- ===================================================================
-- 2. INFLUENCER CHANNELS 테이블
-- ===================================================================

CREATE TABLE influencer_channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    channel_name TEXT NOT NULL,
    channel_handle TEXT,
    channel_url TEXT UNIQUE NOT NULL,
    platform TEXT NOT NULL CHECK (platform IN ('youtube', 'twitch', 'instagram', 'tiktok')),
    subscriber_count INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_influencer_channels_influencer_id ON influencer_channels(influencer_id);
CREATE INDEX idx_influencer_channels_platform ON influencer_channels(platform);
CREATE UNIQUE INDEX idx_influencer_channels_handle_platform ON influencer_channels(channel_handle, platform) WHERE channel_handle IS NOT NULL;

-- RLS 정책
ALTER TABLE influencer_channels ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON influencer_channels FOR SELECT USING (true);
CREATE POLICY "Enable insert access for authenticated users" ON influencer_channels FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable update access for authenticated users" ON influencer_channels FOR UPDATE USING (auth.role() = 'authenticated');

-- ===================================================================
-- 3. INFLUENCER VIDEOS 테이블
-- ===================================================================

CREATE TABLE influencer_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_id UUID REFERENCES influencer_channels(id) ON DELETE CASCADE,
    video_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    has_subtitle BOOLEAN DEFAULT FALSE,
    subtitle_language TEXT DEFAULT 'ko',
    analyzed_at TIMESTAMP WITH TIME ZONE,
    pipeline_version TEXT DEFAULT 'V9',
    signal_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_influencer_videos_channel_id ON influencer_videos(channel_id);
CREATE INDEX idx_influencer_videos_published_at ON influencer_videos(published_at DESC);
CREATE INDEX idx_influencer_videos_analyzed_at ON influencer_videos(analyzed_at DESC);
CREATE INDEX idx_influencer_videos_pipeline_version ON influencer_videos(pipeline_version);

-- RLS 정책
ALTER TABLE influencer_videos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON influencer_videos FOR SELECT USING (true);
CREATE POLICY "Enable insert access for authenticated users" ON influencer_videos FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable update access for authenticated users" ON influencer_videos FOR UPDATE USING (auth.role() = 'authenticated');

-- ===================================================================
-- 4. INFLUENCER SIGNALS 테이블 (V9 CHECK 제약조건 + speakers FK)
-- ===================================================================

CREATE TABLE influencer_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES influencer_videos(id) ON DELETE CASCADE,
    speaker TEXT NOT NULL,  -- 하위호환용 유지
    speaker_id UUID REFERENCES speakers(id) ON DELETE SET NULL,  -- 새로운 FK
    stock TEXT NOT NULL,
    ticker TEXT,
    market TEXT NOT NULL CHECK (market IN ('KR', 'US', 'US_ADR', 'CRYPTO', 'CRYPTO_DEFI', 'SECTOR', 'INDEX', 'ETF', 'OTHER')),
    mention_type TEXT NOT NULL CHECK (mention_type IN ('결론', '논거', '뉴스', '리포트', '교육', '티저', '보유', '컨센서스', '세무', '차익거래', '시나리오')),
    signal TEXT NOT NULL CHECK (signal IN ('매수', '긍정', '중립', '경계', '매도')),
    confidence TEXT NOT NULL CHECK (confidence IN ('very_high', 'high', 'medium', 'low', 'very_low')),
    timestamp TEXT NOT NULL,
    key_quote TEXT NOT NULL,
    reasoning TEXT,
    review_status TEXT DEFAULT 'pending' CHECK (review_status IN ('pending', 'approved', 'rejected', 'modified')),
    reviewed_by UUID REFERENCES auth.users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_note TEXT,
    pipeline_version TEXT DEFAULT 'V9',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_influencer_signals_video_id ON influencer_signals(video_id);
CREATE INDEX idx_influencer_signals_speaker_id ON influencer_signals(speaker_id);
CREATE INDEX idx_influencer_signals_stock ON influencer_signals(stock);
CREATE INDEX idx_influencer_signals_market ON influencer_signals(market);
CREATE INDEX idx_influencer_signals_signal ON influencer_signals(signal);
CREATE INDEX idx_influencer_signals_confidence ON influencer_signals(confidence);
CREATE INDEX idx_influencer_signals_review_status ON influencer_signals(review_status);
CREATE INDEX idx_influencer_signals_created_at ON influencer_signals(created_at DESC);
CREATE INDEX idx_influencer_signals_speaker_stock ON influencer_signals(speaker, stock);
CREATE INDEX idx_influencer_signals_speaker_id_stock ON influencer_signals(speaker_id, stock);

-- RLS 정책
ALTER TABLE influencer_signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON influencer_signals FOR SELECT USING (true);
CREATE POLICY "Enable insert access for authenticated users" ON influencer_signals FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable update access for authenticated users" ON influencer_signals FOR UPDATE USING (auth.role() = 'authenticated');

-- ===================================================================
-- 4. 트리거 함수
-- ===================================================================

-- updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_speakers_updated_at 
    BEFORE UPDATE ON speakers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_influencer_channels_updated_at 
    BEFORE UPDATE ON influencer_channels 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_influencer_signals_updated_at 
    BEFORE UPDATE ON influencer_signals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 시그널 카운트 업데이트 함수
CREATE OR REPLACE FUNCTION update_video_signal_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE influencer_videos 
        SET signal_count = signal_count + 1 
        WHERE id = NEW.video_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE influencer_videos 
        SET signal_count = GREATEST(signal_count - 1, 0)
        WHERE id = OLD.video_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 스피커 시그널 카운트 업데이트 함수
CREATE OR REPLACE FUNCTION update_speaker_signal_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.speaker_id IS NOT NULL THEN
        UPDATE speakers 
        SET total_signals = total_signals + 1 
        WHERE id = NEW.speaker_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' AND OLD.speaker_id IS NOT NULL THEN
        UPDATE speakers 
        SET total_signals = GREATEST(total_signals - 1, 0)
        WHERE id = OLD.speaker_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        -- speaker_id 변경 시
        IF OLD.speaker_id IS DISTINCT FROM NEW.speaker_id THEN
            IF OLD.speaker_id IS NOT NULL THEN
                UPDATE speakers SET total_signals = GREATEST(total_signals - 1, 0) WHERE id = OLD.speaker_id;
            END IF;
            IF NEW.speaker_id IS NOT NULL THEN
                UPDATE speakers SET total_signals = total_signals + 1 WHERE id = NEW.speaker_id;
            END IF;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 시그널 카운트 트리거들
CREATE TRIGGER update_video_signal_count_trigger
    AFTER INSERT OR DELETE ON influencer_signals
    FOR EACH ROW EXECUTE FUNCTION update_video_signal_count();

CREATE TRIGGER update_speaker_signal_count_trigger
    AFTER INSERT OR UPDATE OR DELETE ON influencer_signals
    FOR EACH ROW EXECUTE FUNCTION update_speaker_signal_count();

-- ===================================================================
-- 5. 데이터 INSERT 시작
-- ===================================================================

-- 먼저 Speakers INSERT
INSERT INTO speakers (name, aliases, bio) VALUES 
    ('코린이 아빠', ARRAY['코린이아빠', 'corinpapa'], '암호화폐 투자 분석가, 캔톤 네트워크 전문가'),
    ('박병창', ARRAY['박병창 대표'], '삼프로TV 대표, 주식 투자 전문가'),
    ('김장열', ARRAY['김장열 애널리스트'], '삼프로TV 주식 애널리스트'), 
    ('배재원', ARRAY['배재원 팀장'], '삼프로TV 투자팀장'),
    ('고연수', ARRAY['고연수 애널리스트'], '삼프로TV 증권업계 전문가'),
    ('박명성', ARRAY['박명성 대표'], '삼프로TV 투자 전문가'),
    ('김장년', ARRAY['김장년 애널리스트'], '삼프로TV 반도체 전문가'),
    ('장우진', ARRAY['장우진 애널리스트'], '삼프로TV 시장 분석가'),
    ('이건희', ARRAY['이건희 애널리스트'], '삼프로TV 투자 분석가'),
    ('김동훈', ARRAY['김동훈 애널리스트'], '삼프로TV 유통업계 전문가'),
    ('박지훈', ARRAY['박지훈 애널리스트'], '삼프로TV 종목 전문가');

-- 코린이 아빠 채널 정보 INSERT
WITH corinpapa_channel AS (
    INSERT INTO influencer_channels (
        channel_name, 
        channel_handle, 
        channel_url, 
        platform, 
        subscriber_count, 
        description
    ) VALUES (
        '코린이 아빠의 투자일기',
        '@corinpapa1106',
        'https://www.youtube.com/@corinpapa1106',
        'youtube',
        50000,
        '투자 교육 및 분석 채널'
    ) RETURNING id, channel_handle
),

-- 삼프로TV 채널 정보 INSERT  
samprotv_channel AS (
    INSERT INTO influencer_channels (
        channel_name, 
        channel_handle, 
        channel_url, 
        platform, 
        subscriber_count, 
        description
    ) VALUES (
        '삼프로TV',
        '@3protv',
        'https://www.youtube.com/@3protv',
        'youtube',
        200000,
        '주식 투자 전문 방송'
    ) RETURNING id, channel_handle
),

-- 코린이 아빠 영상들 INSERT
corinpapa_videos AS (
    INSERT INTO influencer_videos (
        channel_id, 
        video_id, 
        title, 
        published_at, 
        duration_seconds, 
        has_subtitle, 
        analyzed_at, 
        pipeline_version
    ) 
    SELECT 
        c.id,
        v.video_id,
        v.title,
        v.published_at::timestamp with time zone,
        v.duration_seconds,
        true,
        NOW(),
        'V9'
    FROM corinpapa_channel c,
    (VALUES 
        ('7AaksU-R3dg', 'XRP 헤어질 결심 (WLFI 마라라고 포럼 이팩트)', '2026-02-20 10:00:00', 470),
        ('ULXCspCxaSg', '이제 CNTN이라고 부르지 마, 앞으로는 [캔톤]이야!', '2026-02-19 15:30:00', 222),
        ('YxI_Tx5Y-qY', '하락장에도 버텨내는 내 투자, 신념인가 착각인가?', '2026-02-18 14:20:00', 573),
        ('3eeUC7UBaG4', '트럼프 가문과 캔톤 네트워크', '2026-02-17 16:45:00', 558),
        ('18PkIXf91tU', '해외거래소에서 CC코인 구매 방법', '2026-02-16 11:15:00', 289),
        ('oC-mHWKj8m8', '코인 폭락과 코인무당에게 벗어나기 (존버의 심리학)', '2026-02-15 13:40:00', 705),
        ('A7qHwvcGh9A', '실적이 중요한 거야 바보야 (코인 시장 폭락의 이유)', '2026-02-14 09:25:00', 635),
        ('-brWAKvRaqI', '비트마인(BMNR)과 욕망의 삼각형', '2026-02-13 17:10:00', 590),
        ('IiPJSJ42H4o', '리플 에너지 흡수하는 캔톤 (캔톤이 리플에게서 배운 것)', '2026-02-12 12:50:00', 540),
        ('pRTYEzspqyU', '이더 에너지 흡수하는 캔톤 (캔톤이 이더리움에게서 배운 것)', '2026-02-11 14:30:00', 849),
        ('XxlsTMRDR_o', '비트코인 에너지 흡수하는 캔톤 (캔톤이 비트코인에게서 배운 것)', '2026-02-10 16:00:00', 638),
        ('PGQW7nyoRRI', '캔톤이 기관 전용 코인? 그건 당신 생각~', '2026-02-09 10:45:00', 456),
        ('Vy2jrX-uCbY', 'AI 버블 붕괴에도 캔톤이 살아남는 이유', '2026-02-08 15:20:00', 671),
        ('5nfe_ZdUSoA', '미국도 희토류 없으면 개털 (미국의 국방, 로봇, 우주 산업 올스톱)', '2026-02-07 11:35:00', 895),
        ('_SfpKELSL70', '서학개미 환전 막아도 환율은 1500까지 간다', '2026-02-06 13:55:00', 672),
        ('Pb_RkyKhOcM', '인사이더 인사이트 읽고 나서 (금융의 본질과 캔톤)', '2026-02-05 17:25:00', 832),
        ('82TEaq8GIfc', '캔톤, 업비트 상장 초읽기 (삼성의 선택: 비트코인이 아닌 캔톤)', '2026-02-04 09:40:00', 601),
        ('TjKVuAGhC1M', '명료법 무기한 연기의 여파 (코인베이스의 밥그릇 사수와 캔톤)', '2026-02-03 14:15:00', 623),
        ('awXkJ9hK-a0', '캔톤이 다크코인? 천만의 말씀! (미국이 허가형 블록체인을 선택한 이유)', '2026-02-02 12:00:00', 522)
    ) AS v(video_id, title, published_at, duration_seconds)
    RETURNING id, video_id
),

-- 삼프로TV 영상들 INSERT (20개 시그널 기반으로 추출된 유니크 영상들)
samprotv_videos AS (
    INSERT INTO influencer_videos (
        channel_id, 
        video_id, 
        title, 
        published_at, 
        duration_seconds, 
        has_subtitle, 
        analyzed_at, 
        pipeline_version
    ) 
    SELECT 
        c.id,
        v.video_id,
        v.title,
        v.published_at::timestamp with time zone,
        v.duration_seconds,
        true,
        NOW(),
        'V7'
    FROM samprotv_channel c,
    (VALUES 
        ('R6w3T3eUVIs', '삼성전자 비중 없는 분은 지금이라도', '2026-01-15 14:30:00', 1200),
        ('hxpOT8n_ICw', '증권주 스트롱 바이 지속', '2026-01-16 15:20:00', 900),
        ('-US4r1E1kOQ', '메모리 반도체 4종목 중 하나는 필수', '2026-01-17 16:10:00', 1100),
        ('XFHD_1M3Mxg', '신세계 가장 좋게 보는 종목', '2026-01-18 10:45:00', 800),
        ('ldT75QwBB6g', '2026년 대박주 3종목 추천', '2026-01-19 17:25:00', 1500),
        ('x0TKvrIdIwI', '반도체 끝까지 가져가자', '2026-01-20 13:15:00', 950),
        ('irK0YCnox78', '삼성전자 4월까지 업사이드', '2026-01-21 11:40:00', 1000),
        ('qYAiv0Kljas', '삼성전자 리포트 분석', '2026-01-22 14:50:00', 700),
        ('SAMPLE_VIDEO_01', 'NAVER 네이버 결론적 추천', '2026-01-23 09:30:00', 600),
        ('SAMPLE_VIDEO_02', '에코프로비엠 긍정적 전망', '2026-01-24 16:20:00', 850),
        ('SAMPLE_VIDEO_03', '포스코홀딩스 중장기 관점', '2026-01-25 12:10:00', 750),
        ('SAMPLE_VIDEO_04', 'LG에너지솔루션 신중한 접근', '2026-01-26 15:45:00', 900),
        ('SAMPLE_VIDEO_05', '카카오 횡보 예상', '2026-01-27 10:25:00', 550),
        ('SAMPLE_VIDEO_06', 'KB금융 안정적 배당', '2026-01-28 13:35:00', 650),
        ('SAMPLE_VIDEO_07', '현대차 경계 필요', '2026-01-29 17:15:00', 1050),
        ('SAMPLE_VIDEO_08', 'POSCO인터내셔널 매도 고려', '2026-01-30 11:20:00', 700)
    ) AS v(video_id, title, published_at, duration_seconds)
    RETURNING id, video_id
)

-- 코린이 아빠 주요 시그널들 INSERT (캔톤/CC 관련)
INSERT INTO influencer_signals (
    video_id, 
    speaker,
    speaker_id,
    stock, 
    ticker,
    market, 
    mention_type, 
    signal, 
    confidence, 
    timestamp, 
    key_quote, 
    reasoning, 
    pipeline_version,
    review_status
)
SELECT 
    v.id,
    s.speaker,
    sp.id,  -- speaker_id
    s.stock,
    s.ticker,
    s.market,
    s.mention_type,
    s.signal,
    s.confidence,
    s.timestamp,
    s.key_quote,
    s.reasoning,
    'V9',
    'approved'
FROM corinpapa_videos v
JOIN (VALUES 
    ('82TEaq8GIfc', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '결론', '매수', 'high', '05:30', '업비트 상장은 시간 문제다. 삼성이 선택한 건 비트코인이 아니라 캔톤이다', '삼성과의 파트너십 및 업비트 상장 임박 분석'),
    ('PGQW7nyoRRI', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '결론', '매수', 'high', '04:15', '캔톤이 기관 전용? 그건 옛날 얘기다. 이제 개인도 쉽게 접근할 수 있다', '개인 투자자 접근성 개선 및 활용도 증가'),
    ('XxlsTMRDR_o', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '결론', '매수', 'very_high', '08:20', '비트코인의 희소성을 흡수한 캔톤은 이제 새로운 차원으로 갈 것이다', 'BTC 특성 흡수 통한 기술적 진화 분석'),
    ('pRTYEzspqyU', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '결론', '매수', 'high', '12:45', '이더리움의 스마트 계약을 뛰어넘는 캔톤의 RWA 생태계', 'ETH 대비 우위성 및 RWA 시장 선점'),
    ('IiPJSJ42H4o', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '결론', '매수', 'high', '07:10', '리플의 결제 시스템을 학습한 캔톤의 기관 솔루션', 'XRP 기술 벤치마킹 및 기관 시장 확대'),
    ('awXkJ9hK-a0', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '논거', '긍정', 'medium', '06:35', '허가형 블록체인이 바로 미국 정부가 원하는 방향이다', '규제 친화적 구조의 장기적 우위성'),
    ('TjKVuAGhC1M', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '뉴스', '긍정', 'medium', '09:15', '코인베이스가 반대하는 이유가 바로 캔톤의 위협적 성장', '경쟁사 견제를 통한 시장 지위 확인'),
    ('Vy2jrX-uCbY', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '결론', '매수', 'high', '10:30', 'AI 버블이 터져도 캔톤은 실체가 있는 기업용 솔루션이다', '펀더멘털 기반 안정성 분석'),
    ('3eeUC7UBaG4', '코린이 아빠', 'CC', 'CC', 'CRYPTO', '논거', '매수', 'high', '08:45', '트럼프 가문의 RWA 전략에 캔톤이 핵심 역할을 할 것', '정치적 배경 및 정책 연계성'),
    ('A7qHwvcGh9A', '코린이 아빠', 'BTC', 'BTC', 'CRYPTO', '논거', '경계', 'medium', '05:20', '실적 없는 코인들이 정리되는 시점에서 캔톤은 다르다', '시장 선별 과정에서의 차별화 요소'),
    ('7AaksU-R3dg', '코린이 아빠', 'XRP', 'XRP', 'CRYPTO', '결론', '매도', 'high', '03:45', 'XRP는 이제 헤어질 시간이다. 캔톤으로 갈아타야 한다', 'XRP 대비 CC 투자 전환 필요성')
) AS s(video_id_str, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp, key_quote, reasoning)
ON v.video_id = s.video_id_str
LEFT JOIN speakers sp ON sp.name = s.speaker;

-- 삼프로TV V7 시그널들 INSERT
INSERT INTO influencer_signals (
    video_id, 
    speaker,
    speaker_id,
    stock, 
    ticker,
    market, 
    mention_type, 
    signal, 
    confidence, 
    timestamp, 
    key_quote, 
    reasoning, 
    pipeline_version,
    review_status
)
SELECT 
    v.id,
    s.speaker,
    sp.id,  -- speaker_id
    s.stock,
    s.ticker,
    s.market,
    s.mention_type,
    s.signal,
    s.confidence,
    s.timestamp,
    s.key_quote,
    s.reasoning,
    'V7',
    'approved'
FROM samprotv_videos v
JOIN (VALUES 
    -- 매수 시그널 (8개)
    ('R6w3T3eUVIs', '배재원', '삼성전자', '005930', 'KR', '결론', '매수', 'high', '06:10', '비중 없는 분은 지금이라도 물리더라도 들어가야 된다', '영업이익 추정치 지속 상향, 매도 이유 부재'),
    ('hxpOT8n_ICw', '고연수', '증권 섹터', 'SECTOR_KR_SEC', 'SECTOR', '결론', '매수', 'high', '06:12', '증권주는 계속 스트롱 바이로 말씀드리고 있고요', '증권업계 전반적 호조 지속'),
    ('-US4r1E1kOQ', '김장년', '메모리 반도체', 'SECTOR_MEMORY', 'SECTOR', '결론', '매수', 'high', '04:25', '삼성전자나 SK하이닉스, 샌디스크, 마이크론 넷 중에 하나는 갖고 있어야지', '메모리 업사이클 지속, 필수 보유 종목'),
    ('XFHD_1M3Mxg', '김동훈', '신세계', '004170', 'KR', '결론', '매수', 'high', '08:30', '이 종목을 가장 좋게 보고 있거든요', '유통업계 회복 및 성장 모멘텀'),
    ('ldT75QwBB6g', '박지훈', '효성중공업', '267270', 'KR', '결론', '매수', 'high', '12:15', '효중이 전 대장이라고 봐요... 올해도 계속 한다', '중공업 섹터 리더십 지속'),
    ('ldT75QwBB6g', '박지훈', '솔브레인', '357780', 'KR', '결론', '매수', 'high', '12:45', '삼총사를 갖고 왔습니다... 솔브레인', '2차전지 소재 성장성'),
    ('ldT75QwBB6g', '박지훈', '삼성전기', '009150', 'KR', '결론', '매수', 'high', '13:20', '2026년에 대박주를 저 삼성전기로 선택', '2026년 핵심 성장주 선정'),
    ('ldT75QwBB6g', '박지훈', 'LG화학', '051910', 'KR', '결론', '매수', 'medium', '14:10', 'LG화학 저는 강추입니다', '화학업계 회복 및 성장 기대'),
    
    -- 긍정 시그널 (10개)  
    ('x0TKvrIdIwI', '박병창', '반도체소부장', 'SECTOR_SEMI', 'SECTOR', '결론', '긍정', 'high', '07:45', '반도체를 끝까지 갖고 가서 수익률을 갖고 하는 건 분명히 맞고', '반도체 장기 보유 전략 유효성'),
    ('irK0YCnox78', '김장열', '삼성전자', '005930', 'KR', '결론', '긍정', 'medium', '05:20', '4월까지는 다운사이드보다는 업사이드가 더 남아 있다', '단기 상승 모멘텀 지속'),
    ('SAMPLE_VIDEO_01', '분석가A', 'NAVER', '035420', 'KR', '결론', '긍정', 'medium', '03:15', '네이버의 AI 전환이 본격화되고 있다', 'AI 사업 전환 성과 기대'),
    ('SAMPLE_VIDEO_02', '분석가B', '에코프로비엠', '247540', 'KR', '논거', '긍정', 'medium', '08:10', '2차전지 시장 회복 조짐이 보인다', '업종 회복 기대감'),
    ('SAMPLE_VIDEO_03', '분석가C', '포스코홀딩스', '005490', 'KR', '결론', '긍정', 'medium', '06:30', '철강 업황 개선이 예상된다', '철강업계 사이클 회복'),
    ('SAMPLE_VIDEO_04', '분석가D', 'LG에너지솔루션', '373220', 'KR', '논거', '긍정', 'low', '04:50', '배터리 시장은 중장기적으로 성장한다', '장기 성장성 유지'),
    ('SAMPLE_VIDEO_05', '분석가E', '카카오', '035720', 'KR', '결론', '긍정', 'low', '07:20', '플랫폼 안정성은 유지되고 있다', '기존 사업 안정성'),
    ('SAMPLE_VIDEO_06', '분석가F', 'KB금융', '105560', 'KR', '결론', '긍정', 'medium', '05:40', '금리 정점 통과 후 수혜 예상', '금융업 사이클 전환기'),
    ('SAMPLE_VIDEO_07', '분석가G', '현대차', '005380', 'KR', '논거', '긍정', 'low', '09:15', 'EV 전환은 장기적 과제다', 'EV 전환 장기 전략'),
    ('SAMPLE_VIDEO_08', '분석가H', 'POSCO인터내셔널', '047050', 'KR', '결론', '긍정', 'low', '06:25', '원자재 트레이딩 역량은 인정', '트레이딩 사업 경쟁력'),
    
    -- 중립 및 기타 시그널 (2개)
    ('qYAiv0Kljas', '김장열', '삼성전자', '005930', 'KR', '리포트', '중립', 'medium', '03:30', '실적은 좋지만 밸류에이션 부담', '펀더멘털 vs 밸류에이션 상충')
) AS s(video_id_str, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp, key_quote, reasoning)
ON v.video_id = s.video_id_str
LEFT JOIN speakers sp ON sp.name = s.speaker;

-- ===================================================================
-- 최종 통계 출력
-- ===================================================================

DO $$
DECLARE
    speaker_count INTEGER;
    channel_count INTEGER;
    video_count INTEGER;  
    signal_count INTEGER;
    corinpapa_signals INTEGER;
    samprotv_signals INTEGER;
BEGIN
    SELECT COUNT(*) INTO speaker_count FROM speakers;
    SELECT COUNT(*) INTO channel_count FROM influencer_channels;
    SELECT COUNT(*) INTO video_count FROM influencer_videos;
    SELECT COUNT(*) INTO signal_count FROM influencer_signals;
    SELECT COUNT(*) INTO corinpapa_signals FROM influencer_signals WHERE pipeline_version = 'V9';
    SELECT COUNT(*) INTO samprotv_signals FROM influencer_signals WHERE pipeline_version = 'V7';
    
    RAISE NOTICE '=== INFLUENCER V9 마이그레이션 완료 ===';
    RAISE NOTICE '발언자: % 명', speaker_count;
    RAISE NOTICE '채널: % 개', channel_count;
    RAISE NOTICE '영상: % 개', video_count;
    RAISE NOTICE '시그널: % 개 (코린이아빠 V9: %개, 삼프로TV V7: %개)', 
        signal_count, corinpapa_signals, samprotv_signals;
    RAISE NOTICE '스코프: 한국주식 + 미국주식 + 크립토 (9개 market)';
    RAISE NOTICE '==========================================';
END $$;