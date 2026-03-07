-- videos 테이블 category 컬럼 추가 (이미 테이블이 있는 경우)
ALTER TABLE videos ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'general';
