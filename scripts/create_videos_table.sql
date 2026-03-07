-- videos 테이블 생성
CREATE TABLE IF NOT EXISTS videos (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  video_id TEXT UNIQUE NOT NULL,
  channel_id TEXT NOT NULL,
  channel_name TEXT NOT NULL,
  title TEXT NOT NULL,
  upload_date TIMESTAMP NOT NULL,
  long_summary TEXT,
  youtube_url TEXT NOT NULL,
  has_signal BOOLEAN DEFAULT FALSE,
  mentioned_stocks TEXT[],
  duration_seconds INTEGER,
  view_count INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_videos_upload_date ON videos(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_videos_channel ON videos(channel_id);
CREATE INDEX IF NOT EXISTS idx_videos_has_signal ON videos(has_signal);
