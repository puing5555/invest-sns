-- ============================================
-- invest-sns 인플루언서 시스템 마이그레이션 v2 (수정본)
-- 수정사항:
--   - STEP 5: '코린이아빠' → '코린이 아빠' (띄어쓰기 수정)
--   - STEP 5: 이형수/IT의신 → Godofit 채널명으로 매칭
--   - STEP 5 전: 이형수, 부읽남 speakers 테이블 INSERT 추가
-- ============================================

-- ============================================
-- STEP 0: 누락된 speaker INSERT (이형수, 부읽남)
-- ============================================
INSERT INTO speakers (name, aliases)
VALUES ('이형수', ARRAY['IT의신', 'IT의 신', 'GODofIT'])
ON CONFLICT (name) DO NOTHING;

INSERT INTO speakers (name, aliases)
VALUES ('부읽남', ARRAY['부읽남TV'])
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- STEP 1: speakers 테이블에 컬럼 추가
-- ============================================
ALTER TABLE speakers ADD COLUMN IF NOT EXISTS slug TEXT UNIQUE;
ALTER TABLE speakers ADD COLUMN IF NOT EXISTS specialty TEXT[] DEFAULT '{}';
ALTER TABLE speakers ADD COLUMN IF NOT EXISTS tier TEXT DEFAULT 'standard' CHECK (tier IN ('top', 'standard', 'emerging'));
ALTER TABLE speakers ADD COLUMN IF NOT EXISTS total_signals INTEGER DEFAULT 0;
ALTER TABLE speakers ADD COLUMN IF NOT EXISTS accuracy_rate NUMERIC(5,2);
ALTER TABLE speakers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE speakers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- slug 인덱스
CREATE INDEX IF NOT EXISTS idx_speakers_slug ON speakers(slug);

-- ============================================
-- STEP 2: 기존 70명 slug 자동 생성
-- ============================================
UPDATE speakers
SET slug = LOWER(REPLACE(REPLACE(name, ' ', '-'), '.', ''))
WHERE slug IS NULL;

-- ============================================
-- STEP 3: influencer_channels에 channel_type 추가
-- ============================================
ALTER TABLE influencer_channels ADD COLUMN IF NOT EXISTS
  channel_type TEXT DEFAULT 'solo' CHECK (channel_type IN ('solo', 'interview'));

-- ============================================
-- STEP 4: channel_speakers 조인 테이블 (N:N)
-- ============================================
CREATE TABLE IF NOT EXISTS channel_speakers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  channel_id UUID NOT NULL REFERENCES influencer_channels(id) ON DELETE CASCADE,
  speaker_id UUID NOT NULL REFERENCES speakers(id) ON DELETE CASCADE,
  role TEXT DEFAULT 'guest' CHECK (role IN ('owner', 'regular', 'guest')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(channel_id, speaker_id)
);

CREATE INDEX IF NOT EXISTS idx_cs_channel ON channel_speakers(channel_id);
CREATE INDEX IF NOT EXISTS idx_cs_speaker ON channel_speakers(speaker_id);

-- ============================================
-- STEP 5: 채널 owner 연결
-- ============================================

-- 이효석 채널 → 이효석 speaker (owner)
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%이효석%' AND s.name = '이효석'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 코린이아빠 채널 → 코린이 아빠 speaker (owner) [수정: 띄어쓰기 추가]
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%코린이%' AND s.name = '코린이 아빠'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- Godofit 채널 → 이형수 speaker (owner) [수정: Godofit 채널명으로 매칭]
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%Godofit%' AND s.name = '이형수'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 안유화 채널 → 안유화 speaker (owner)
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE (c.channel_name LIKE '%안유화%' OR c.channel_name LIKE '%안경투%') AND s.name = '안유화'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 부읽남 채널 → 부읽남 speaker (owner) [신규 추가]
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%부읽남%' AND s.name = '부읽남'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 슈카월드 채널 → 슈카 speaker (owner)
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%슈카%' AND s.name = '슈카'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 월가아재 채널 → 월가아재 speaker (owner)
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%월가아재%' AND s.name = '월가아재'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 달란트투자 채널 → 달란트투자 speaker (owner)
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%달란트%' AND s.name = '달란트투자'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 세상학개론 채널 → 세상학개론 speaker (owner)
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%세상학%' AND s.name = '세상학개론'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 올랜도 킴 채널 → 올랜도 킴 speaker (owner)
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%올랜도%' AND s.name = '올랜도 킴'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- 삼프로TV 채널 → 삼프로TV speaker (owner, 있으면)
INSERT INTO channel_speakers (channel_id, speaker_id, role)
SELECT c.id, s.id, 'owner'
FROM influencer_channels c, speakers s
WHERE c.channel_name LIKE '%삼프로%' AND s.name = '삼프로TV'
ON CONFLICT (channel_id, speaker_id) DO NOTHING;

-- ============================================
-- STEP 6: resolve_speaker 함수
-- ============================================
CREATE OR REPLACE FUNCTION resolve_speaker(
  p_speaker_name TEXT,
  p_channel_id UUID
) RETURNS UUID AS $$
DECLARE
  v_speaker_id UUID;
  v_channel_type TEXT;
BEGIN
  IF p_speaker_name IS NOT NULL THEN
    SELECT id INTO v_speaker_id
    FROM speakers
    WHERE name = p_speaker_name
    LIMIT 1;

    IF v_speaker_id IS NOT NULL THEN
      RETURN v_speaker_id;
    END IF;

    SELECT id INTO v_speaker_id
    FROM speakers
    WHERE p_speaker_name = ANY(aliases)
    LIMIT 1;

    IF v_speaker_id IS NOT NULL THEN
      RETURN v_speaker_id;
    END IF;
  END IF;

  SELECT channel_type INTO v_channel_type
  FROM influencer_channels
  WHERE id = p_channel_id;

  IF v_channel_type = 'solo' THEN
    SELECT cs.speaker_id INTO v_speaker_id
    FROM channel_speakers cs
    WHERE cs.channel_id = p_channel_id
      AND cs.role = 'owner'
    LIMIT 1;

    RETURN v_speaker_id;
  END IF;

  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- STEP 7: 미매핑 시그널 백필 (solo 채널 owner로)
-- ============================================
UPDATE influencer_signals s
SET speaker_id = cs.speaker_id
FROM influencer_videos v
JOIN channel_speakers cs ON cs.channel_id = v.channel_id AND cs.role = 'owner'
WHERE s.video_id = v.id
  AND s.speaker_id IS NULL;

-- ============================================
-- STEP 8: total_signals 캐시 업데이트
-- ============================================
UPDATE speakers sp
SET total_signals = sub.cnt
FROM (
  SELECT speaker_id, COUNT(*) as cnt
  FROM influencer_signals
  WHERE speaker_id IS NOT NULL
  GROUP BY speaker_id
) sub
WHERE sp.id = sub.speaker_id;

-- ============================================
-- STEP 9: updated_at 자동 갱신 트리거
-- ============================================
CREATE OR REPLACE FUNCTION update_speakers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_speakers_updated_at ON speakers;
CREATE TRIGGER trg_speakers_updated_at
  BEFORE UPDATE ON speakers
  FOR EACH ROW
  EXECUTE FUNCTION update_speakers_updated_at();

-- ============================================
-- STEP 10: 검증 쿼리
-- ============================================
SELECT COUNT(*) as channel_speakers_count FROM channel_speakers;
SELECT COUNT(*) as null_speaker_signals FROM influencer_signals WHERE speaker_id IS NULL;
SELECT name, slug, total_signals FROM speakers WHERE total_signals > 0 ORDER BY total_signals DESC;
