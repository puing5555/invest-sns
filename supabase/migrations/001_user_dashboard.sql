-- ====================================================
-- 내 종목 대시보드용 DB 스키마
-- Created: 2026-03-06
-- Description: 사용자별 종목 관리 및 개인화 대시보드
-- ====================================================

-- 1. 사용자 프로필 테이블 (auth.users 확장)
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  display_name TEXT,
  avatar_url TEXT,
  dashboard_preferences JSONB DEFAULT '{
    "default_view": "portfolio",
    "show_notifications": true,
    "show_ai_insights": true
  }'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at ON public.user_profiles(created_at);

-- RLS 활성화
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS 정책: 사용자는 자신의 프로필만 접근 가능
CREATE POLICY "users_own_profile" ON public.user_profiles 
  FOR ALL USING (auth.uid() = id);

-- updated_at 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ====================================================

-- 2. 사용자 보유 종목 테이블
CREATE TABLE IF NOT EXISTS public.user_stocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  stock_code TEXT NOT NULL,        -- '005930', 'NVDA', 'TSLA'
  stock_name TEXT NOT NULL,        -- '삼성전자', 'NVIDIA Corp', 'Tesla Inc'
  market TEXT NOT NULL CHECK (market IN ('KR', 'US', 'JP', 'CN', 'CRYPTO')),
  
  -- 매수 정보
  quantity DECIMAL(15,4) NOT NULL CHECK (quantity > 0),
  avg_buy_price DECIMAL(15,4) NOT NULL CHECK (avg_buy_price > 0),
  total_investment DECIMAL(15,2) GENERATED ALWAYS AS (quantity * avg_buy_price) STORED,
  
  -- 메타데이터
  first_bought_at TIMESTAMPTZ DEFAULT NOW(),
  last_updated_at TIMESTAMPTZ DEFAULT NOW(),
  notes TEXT,                      -- 매수 이유, 메모 등
  
  -- 제약조건: 사용자당 종목 중복 불가
  UNIQUE(user_id, stock_code)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_user_stocks_user_id ON public.user_stocks(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stocks_market ON public.user_stocks(market);
CREATE INDEX IF NOT EXISTS idx_user_stocks_stock_code ON public.user_stocks(stock_code);
CREATE INDEX IF NOT EXISTS idx_user_stocks_total_investment ON public.user_stocks(total_investment DESC);

-- RLS 활성화
ALTER TABLE public.user_stocks ENABLE ROW LEVEL SECURITY;

-- RLS 정책: 사용자는 자신의 종목만 접근 가능
CREATE POLICY "users_own_stocks" ON public.user_stocks 
  FOR ALL USING (auth.uid() = user_id);

-- updated_at 자동 업데이트 트리거
CREATE TRIGGER update_user_stocks_updated_at
  BEFORE UPDATE ON public.user_stocks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ====================================================

-- 3. 사용자 관심 종목 테이블
CREATE TABLE IF NOT EXISTS public.user_watchlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  stock_code TEXT NOT NULL,
  stock_name TEXT NOT NULL,
  market TEXT NOT NULL CHECK (market IN ('KR', 'US', 'JP', 'CN', 'CRYPTO')),
  
  -- 알림 설정
  alert_on_signals BOOLEAN DEFAULT true,        -- 시그널 발생시 알림
  alert_price_target DECIMAL(15,4),             -- 목표가 알림
  alert_price_type TEXT CHECK (alert_price_type IN ('above', 'below', NULL)),
  
  -- 메타데이터
  added_at TIMESTAMPTZ DEFAULT NOW(),
  notes TEXT,                                   -- 관심 사유, 메모 등
  
  -- 제약조건: 사용자당 종목 중복 불가
  UNIQUE(user_id, stock_code)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_user_watchlist_user_id ON public.user_watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_user_watchlist_stock_code ON public.user_watchlist(stock_code);
CREATE INDEX IF NOT EXISTS idx_user_watchlist_market ON public.user_watchlist(market);
CREATE INDEX IF NOT EXISTS idx_user_watchlist_alerts ON public.user_watchlist(user_id) 
  WHERE alert_on_signals = true;

-- RLS 활성화
ALTER TABLE public.user_watchlist ENABLE ROW LEVEL SECURITY;

-- RLS 정책: 사용자는 자신의 관심종목만 접근 가능
CREATE POLICY "users_own_watchlist" ON public.user_watchlist 
  FOR ALL USING (auth.uid() = user_id);

-- ====================================================

-- 4. 사용자 알림 설정 테이블
CREATE TABLE IF NOT EXISTS public.user_notification_settings (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- 글로벌 알림 설정
  enabled BOOLEAN DEFAULT true,
  
  -- 카테고리별 알림 설정
  portfolio_alerts BOOLEAN DEFAULT true,        -- 보유종목 시그널
  watchlist_alerts BOOLEAN DEFAULT true,        -- 관심종목 시그널
  price_alerts BOOLEAN DEFAULT true,            -- 가격 알림
  analyst_reports BOOLEAN DEFAULT true,         -- 애널리스트 리포트
  market_summary BOOLEAN DEFAULT false,         -- 시장 요약
  ai_insights BOOLEAN DEFAULT true,             -- AI 인사이트
  
  -- 알림 방식 (향후 확장용)
  email_enabled BOOLEAN DEFAULT false,
  push_enabled BOOLEAN DEFAULT true,
  
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS 활성화
ALTER TABLE public.user_notification_settings ENABLE ROW LEVEL SECURITY;

-- RLS 정책
CREATE POLICY "users_own_notification_settings" ON public.user_notification_settings 
  FOR ALL USING (auth.uid() = user_id);

-- updated_at 자동 업데이트 트리거
CREATE TRIGGER update_user_notification_settings_updated_at
  BEFORE UPDATE ON public.user_notification_settings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ====================================================

-- 5. 사용자 알림 기록 테이블
CREATE TABLE IF NOT EXISTS public.user_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  
  -- 알림 내용
  type TEXT NOT NULL CHECK (type IN (
    'signal',           -- 시그널 알림
    'price_target',     -- 목표가 도달
    'analyst_report',   -- 애널리스트 리포트
    'market_summary',   -- 시장 요약
    'ai_insight',       -- AI 인사이트
    'portfolio_alert'   -- 포트폴리오 알림
  )),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  stock_code TEXT,                              -- 관련 종목 (선택사항)
  
  -- 상태
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  read_at TIMESTAMPTZ,
  
  -- 메타데이터 (JSON)
  metadata JSONB DEFAULT '{}'::jsonb           -- 시그널 ID, 리포트 URL, 가격 정보 등
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON public.user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_unread ON public.user_notifications(user_id, created_at DESC) 
  WHERE is_read = false;
CREATE INDEX IF NOT EXISTS idx_user_notifications_created ON public.user_notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_notifications_type ON public.user_notifications(type);
CREATE INDEX IF NOT EXISTS idx_user_notifications_stock ON public.user_notifications(stock_code);

-- RLS 활성화
ALTER TABLE public.user_notifications ENABLE ROW LEVEL SECURITY;

-- RLS 정책
CREATE POLICY "users_own_notifications" ON public.user_notifications 
  FOR ALL USING (auth.uid() = user_id);

-- ====================================================

-- 6. 초기 데이터 및 헬퍼 함수들

-- 사용자 프로필 자동 생성 함수 (회원가입 시 호출)
CREATE OR REPLACE FUNCTION create_user_profile()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, display_name)
  VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1)));
  
  INSERT INTO public.user_notification_settings (user_id)
  VALUES (NEW.id);
  
  RETURN NEW;
END;
$$ language 'plpgsql' security definer;

-- auth.users에 새 사용자가 생성되면 프로필도 자동 생성
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION create_user_profile();

-- ====================================================

-- 7. 개인화된 시그널 조회를 위한 뷰 (성능 최적화)
CREATE OR REPLACE VIEW user_personalized_signals AS
SELECT DISTINCT 
  u.user_id,
  s.*
FROM (
  -- 보유종목의 시그널
  SELECT user_id, stock_code, 'portfolio' as source_type
  FROM public.user_stocks
  UNION
  -- 관심종목의 시그널
  SELECT user_id, stock_code, 'watchlist' as source_type  
  FROM public.user_watchlist
  WHERE alert_on_signals = true
) u
INNER JOIN public.influencer_signals s ON s.ticker = u.stock_code
WHERE s.review_status = 'approved';

-- ====================================================

-- 8. 알림 생성 헬퍼 함수
CREATE OR REPLACE FUNCTION create_user_notification(
  p_user_id UUID,
  p_type TEXT,
  p_title TEXT,
  p_message TEXT,
  p_stock_code TEXT DEFAULT NULL,
  p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID AS $$
DECLARE
  notification_id UUID;
  settings RECORD;
BEGIN
  -- 알림 설정 확인
  SELECT * INTO settings 
  FROM public.user_notification_settings 
  WHERE user_id = p_user_id;
  
  -- 알림이 비활성화되어 있으면 생성하지 않음
  IF NOT FOUND OR NOT settings.enabled THEN
    RETURN NULL;
  END IF;
  
  -- 타입별 알림 설정 확인
  CASE p_type
    WHEN 'signal' THEN
      IF NOT (settings.portfolio_alerts OR settings.watchlist_alerts) THEN
        RETURN NULL;
      END IF;
    WHEN 'price_target' THEN
      IF NOT settings.price_alerts THEN
        RETURN NULL;
      END IF;
    WHEN 'analyst_report' THEN
      IF NOT settings.analyst_reports THEN
        RETURN NULL;
      END IF;
    WHEN 'ai_insight' THEN
      IF NOT settings.ai_insights THEN
        RETURN NULL;
      END IF;
    ELSE
      -- 기타 타입은 기본적으로 생성
  END CASE;
  
  -- 알림 생성
  INSERT INTO public.user_notifications (
    user_id, type, title, message, stock_code, metadata
  )
  VALUES (
    p_user_id, p_type, p_title, p_message, p_stock_code, p_metadata
  )
  RETURNING id INTO notification_id;
  
  RETURN notification_id;
END;
$$ language 'plpgsql' security definer;

-- ====================================================

-- 9. 데이터 정합성 검증 쿼리들 (개발/테스트용)

-- 사용자별 종목 중복 체크
CREATE OR REPLACE FUNCTION check_user_stock_duplicates()
RETURNS TABLE(user_id UUID, stock_code TEXT, count BIGINT) AS $$
BEGIN
  RETURN QUERY
  SELECT s.user_id, s.stock_code, COUNT(*)
  FROM public.user_stocks s
  GROUP BY s.user_id, s.stock_code
  HAVING COUNT(*) > 1;
END;
$$ language 'plpgsql';

-- 관심종목 중복 체크
CREATE OR REPLACE FUNCTION check_user_watchlist_duplicates()
RETURNS TABLE(user_id UUID, stock_code TEXT, count BIGINT) AS $$
BEGIN
  RETURN QUERY
  SELECT w.user_id, w.stock_code, COUNT(*)
  FROM public.user_watchlist w
  GROUP BY w.user_id, w.stock_code
  HAVING COUNT(*) > 1;
END;
$$ language 'plpgsql';

-- ====================================================

COMMENT ON TABLE public.user_profiles IS '사용자 프로필 정보 (auth.users 확장)';
COMMENT ON TABLE public.user_stocks IS '사용자 보유 종목 정보';
COMMENT ON TABLE public.user_watchlist IS '사용자 관심 종목 (워치리스트)';
COMMENT ON TABLE public.user_notification_settings IS '사용자별 알림 설정';
COMMENT ON TABLE public.user_notifications IS '사용자 알림 기록';

COMMENT ON COLUMN public.user_stocks.total_investment IS '총 투자금액 (자동계산: quantity * avg_buy_price)';
COMMENT ON COLUMN public.user_watchlist.alert_price_target IS '목표가 알림 설정 가격';
COMMENT ON COLUMN public.user_notifications.metadata IS '알림 관련 메타데이터 (시그널 ID, URL 등)';

-- 완료 메시지
SELECT 'User Dashboard Database Schema Created Successfully!' as result;