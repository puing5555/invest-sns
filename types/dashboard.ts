/**
 * 내 종목 대시보드 TypeScript 타입 정의
 * Jay의 프로토타입 (my-dashboard-v3.html)에서 추출한 데이터 구조
 */

// ============================================
// 시장 데이터 타입
// ============================================

export interface MarketIndex {
  name: string;
  value: string;
  change: string;
  positive: boolean;
}

export interface MarketData {
  updated: string; // "03/06 07:00" 형식
  us: MarketIndex[]; // 미국 주요 지수
  kr: MarketIndex[]; // 한국 주요 지수
  issues: string[]; // 핵심 이슈 텍스트 배열
}

// ============================================
// 야간 거래 데이터 타입
// ============================================

export interface OvernightStock {
  name: string;
  prev: number; // 전일 종가
  now: number; // 현재가
  change: string; // "+1.3%" 형식
  positive: boolean;
  note: string; // 변동 이유
}

// ============================================
// 포트폴리오 요약 타입
// ============================================

export interface PortfolioSummary {
  totalValue: number; // 총 자산가치
  totalReturn: number; // 총 수익률 (%)
  totalReturnAmt: number; // 총 수익금액
  todayChange: number; // 오늘 변동금액
  todayPercent: number; // 오늘 변동률 (%)
}

// ============================================
// 알림/alerts 타입
// ============================================

export interface Alert {
  id: number;
  type: '보유' | '관심'; // 보유종목 or 관심종목
  icon: string; // 이모지 아이콘
  stock: string; // 종목명
  title: string; // 알림 제목
  detail: string; // 알림 상세
  time: string; // "10분 전" 형식
  color: string; // HEX 색상코드
}

// ============================================
// 보유 종목 (HOLDINGS) 타입
// ============================================

export interface HoldingStock {
  id: number;
  name: string; // 종목명
  ticker: string; // 종목코드
  cur: '$' | '₩'; // 통화 기호
  shares: number; // 보유 수량
  buy: number; // 평균 매수가
  now: number; // 현재가
  ret: number; // 수익률 (%)
  retAmt: number; // 수익금액
  weight: number; // 포트폴리오 비중 (%)
  today: number; // 오늘 수익률 (%)
  ytb: number; // 유튜버 매수 비율 (%)
  ytbT: number; // 유튜버 언급 횟수
  disc: string | null; // 공시 등급 ('A', 'B', etc.)
  analyst: string; // 애널리스트 의견 ("HOLD $75")
  trend: string | null; // 트렌드 정보 ("FSD 7점")
  ai: string; // AI 분석 코멘트
}

// ============================================
// 관심 종목 (WATCHLIST) 타입  
// ============================================

export interface WatchlistStock {
  id: number;
  name: string; // 종목명
  ticker: string; // 종목코드
  cur: '$' | '₩'; // 통화 기호
  now: number; // 현재가
  target: number; // 관심가(목표가)
  near: boolean; // 관심가 근접 여부
  ytb: number; // 유튜버 매수 비율 (%)
  ytbT: number; // 유튜버 언급 횟수
  trend: string | null; // 트렌드 정보 ("HBM 8점", "🔥무설탕소주 9점")
  analyst: string; // 애널리스트 의견 ("BUY 25만")
  ai: string; // AI 분석 코멘트
  reason: string; // 관심 사유
}

// ============================================
// AI 인사이트 타입
// ============================================

export interface AIInsight {
  icon: string; // 이모지 아이콘
  text: string; // 인사이트 텍스트
  color: string; // HEX 색상코드
}

// ============================================
// 대시보드 전체 데이터 타입 (통합)
// ============================================

export interface DashboardData {
  market: MarketData;
  overnight: OvernightStock[];
  portfolio: PortfolioSummary;
  alerts: Alert[];
  holdings: HoldingStock[];
  watchlist: WatchlistStock[];
  aiInsights: AIInsight[];
}

// ============================================
// UI 상태 관리 타입
// ============================================

export type DashboardTab = '전체' | '보유' | '관심';

export interface DashboardViewState {
  currentTab: DashboardTab;
  expandedStockId: number | null;
  loading: boolean;
  error: string | null;
}

// ============================================
// API 응답 타입 (실제 서버 연동용)
// ============================================

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  loading?: boolean;
}

// 실시간 가격 데이터
export interface RealTimePriceData {
  [stockCode: string]: {
    price: number;
    change: number;
    changePercent: number;
    timestamp: string;
  };
}

// 시그널 데이터 (기존 influencer_signals 테이블과 매핑)
export interface StockSignal {
  id: string;
  ticker: string;
  signal: '매수' | '매도' | '관망' | '긍정' | '부정';
  confidence: number;
  key_quote: string;
  created_at: string;
  video_title: string;
  influencer_name: string;
  review_status: 'approved' | 'pending' | 'rejected';
}

// 개인화된 피드 아이템
export interface PersonalizedFeedItem {
  type: 'signal' | 'news' | 'analyst' | 'ai_insight';
  stockCode: string;
  stockName: string;
  title: string;
  content: string;
  timestamp: string;
  source: string;
  isPortfolio: boolean; // 보유종목 여부
  isWatchlist: boolean; // 관심종목 여부
  metadata?: Record<string, any>;
}

// ============================================
// 폼/입력 관련 타입
// ============================================

export interface StockSearchResult {
  code: string;
  name: string;
  market: 'KR' | 'US' | 'JP' | 'CN' | 'CRYPTO';
  exchange?: string;
}

export interface AddStockFormData {
  stock_code: string;
  stock_name: string;
  market: 'KR' | 'US' | 'JP' | 'CN' | 'CRYPTO';
  quantity?: number; // 포트폴리오 전용
  avg_buy_price?: number; // 포트폴리오 전용
  alert_price_target?: number; // 관심종목 전용
  alert_price_type?: 'above' | 'below'; // 관심종목 전용
  notes?: string;
}

// ============================================
// 차트/시각화 관련 타입
// ============================================

export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface PortfolioChartData {
  allocation: { // 자산 배분
    market: string;
    value: number;
    percentage: number;
    color: string;
  }[];
  performance: ChartDataPoint[]; // 포트폴리오 성과
  comparison: { // 시장 대비 성과
    portfolio: ChartDataPoint[];
    benchmark: ChartDataPoint[];
  };
}

// ============================================
// 알림 설정 타입 (확장)
// ============================================

export interface NotificationPreferences {
  enabled: boolean;
  portfolio_alerts: boolean;
  watchlist_alerts: boolean;
  price_alerts: boolean;
  analyst_reports: boolean;
  market_summary: boolean;
  ai_insights: boolean;
  email_enabled: boolean;
  push_enabled: boolean;
  quiet_hours?: {
    enabled: boolean;
    start: string; // "22:00"
    end: string; // "08:00"
  };
}

// ============================================
// 사용자 프로필 확장 타입
// ============================================

export interface UserDashboardProfile {
  id: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
  dashboard_preferences: {
    default_view: 'portfolio' | 'watchlist' | 'feed';
    show_notifications: boolean;
    show_ai_insights: boolean;
    currency_display: 'KRW' | 'USD' | 'auto';
    theme: 'light' | 'dark' | 'auto';
  };
  created_at: string;
  updated_at: string;
}

// ============================================
// 헬퍼 타입들
// ============================================

export type MarketCode = 'KR' | 'US' | 'JP' | 'CN' | 'CRYPTO';
export type Currency = 'KRW' | 'USD' | 'JPY' | 'CNY' | 'BTC';
export type SignalType = '매수' | '매도' | '관망' | '긍정' | '부정';
export type AlertType = 'signal' | 'price_target' | 'analyst_report' | 'market_summary' | 'ai_insight' | 'portfolio_alert';

// 유틸리티 타입: 선택적 필드를 가진 업데이트용 타입들
export type PartialHoldingStock = Partial<HoldingStock> & Pick<HoldingStock, 'id'>;
export type PartialWatchlistStock = Partial<WatchlistStock> & Pick<WatchlistStock, 'id'>;

// ============================================
// 상수 정의
// ============================================

export const MARKET_NAMES: Record<MarketCode, string> = {
  KR: '한국',
  US: '미국', 
  JP: '일본',
  CN: '중국',
  CRYPTO: '암호화폐'
};

export const CURRENCY_SYMBOLS: Record<Currency, string> = {
  KRW: '₩',
  USD: '$',
  JPY: '¥', 
  CNY: '¥',
  BTC: '₿'
};

export const SIGNAL_COLORS: Record<SignalType, string> = {
  '매수': '#22c55e',
  '긍정': '#22c55e', 
  '관망': '#f59e0b',
  '부정': '#ef4444',
  '매도': '#ef4444'
};

// ============================================
// 타입 가드 함수들
// ============================================

export function isHoldingStock(item: any): item is HoldingStock {
  return item && typeof item.shares === 'number' && typeof item.buy === 'number';
}

export function isWatchlistStock(item: any): item is WatchlistStock {
  return item && typeof item.target === 'number' && typeof item.reason === 'string';
}

export function isValidMarketCode(market: string): market is MarketCode {
  return ['KR', 'US', 'JP', 'CN', 'CRYPTO'].includes(market);
}

export function isValidSignalType(signal: string): signal is SignalType {
  return ['매수', '매도', '관망', '긍정', '부정'].includes(signal);
}