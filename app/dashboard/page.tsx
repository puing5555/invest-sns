'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import { getMarketNews, getNewsByTickers, type StockNews } from '@/lib/supabase';

// ============ TYPES ============
interface MarketItem {
  price: number;
  change: number;
  changePct: number;
  sparkline?: number[]; // 미니차트용
}

interface ExtendedMarketData {
  // 한국장
  KOSPI: MarketItem | null;
  KOSDAQ: MarketItem | null;
  // 미국 선물
  SP_FUTURES: MarketItem | null;
  NQ_FUTURES: MarketItem | null;
  DOW_FUTURES: MarketItem | null;
  VIX: MarketItem | null;
  // 크립토
  BTC: MarketItem | null;
  ETH: MarketItem | null;
  updatedAt: string;
}

interface InvestorEntry {
  individual: number;
  institution: number;
  foreign: number;
}

// ============ DATA FETCH ============
async function fetchYahooChart(ticker: string): Promise<MarketItem | null> {
  try {
    const encoded = encodeURIComponent(ticker);
    const res = await fetch(
      `https://query1.finance.yahoo.com/v8/finance/chart/${encoded}?interval=5m&range=1d`,
      { cache: 'no-store' }
    );
    if (!res.ok) return null;
    const json = await res.json();
    const result = json?.chart?.result?.[0];
    if (!result) return null;
    const meta = result.meta;
    const closes = result.indicators?.quote?.[0]?.close ?? [];
    const filtered = closes.filter((v: number | null) => v !== null && v !== undefined) as number[];

    const price = meta.regularMarketPrice ?? 0;
    const prevClose = meta.previousClose ?? meta.chartPreviousClose ?? price;
    const change = price - prevClose;
    const changePct = prevClose !== 0 ? (change / prevClose) * 100 : 0;

    return {
      price: Math.round(price * 100) / 100,
      change: Math.round(change * 100) / 100,
      changePct: Math.round(changePct * 100) / 100,
      sparkline: filtered.slice(-30), // 최근 30포인트
    };
  } catch {
    return null;
  }
}

function useExtendedMarketData() {
  const [data, setData] = useState<ExtendedMarketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [investorData, setInvestorData] = useState<Record<string, { investors?: InvestorEntry }> | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [kospi, kosdaq, spFut, nqFut, dowFut, vix, btc, eth] = await Promise.all([
        fetchYahooChart('^KS11'),
        fetchYahooChart('^KQ11'),
        fetchYahooChart('ES=F'),
        fetchYahooChart('NQ=F'),
        fetchYahooChart('YM=F'),
        fetchYahooChart('^VIX'),
        fetchYahooChart('BTC-USD'),
        fetchYahooChart('ETH-USD'),
      ]);
      setData({
        KOSPI: kospi,
        KOSDAQ: kosdaq,
        SP_FUTURES: spFut,
        NQ_FUTURES: nqFut,
        DOW_FUTURES: dowFut,
        VIX: vix,
        BTC: btc,
        ETH: eth,
        updatedAt: new Date().toLocaleTimeString('ko-KR'),
      });
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  useEffect(() => {
    fetch('/market-investors.json')
      .then(r => r.ok ? r.json() : null)
      .then(d => setInvestorData(d))
      .catch(() => setInvestorData(null));
  }, []);

  return { data, loading, investorData };
}

// ============ DUMMY DATA ============
const dummyHoldings = [
  { name: '삼성전자', code: '005930', qty: 30, avgPrice: 68500, currentPrice: 74600, returnPct: 8.91 },
  { name: 'SK하이닉스', code: '000660', qty: 10, avgPrice: 175000, currentPrice: 192500, returnPct: 10.0 },
  { name: 'NVIDIA', code: 'NVDA', qty: 5, avgPrice: 700, currentPrice: 824.03, returnPct: 17.72 },
  { name: '카카오', code: '035720', qty: 20, avgPrice: 52000, currentPrice: 41300, returnPct: -20.58 },
];

const dummyWatchlist = [
  { name: '하이트진로', code: '000080', currentPrice: 21500, changePct: 2.1 },
  { name: 'CELH', code: 'CELH', currentPrice: 32.45, changePct: 0.5 },
  { name: '테슬라', code: 'TSLA', currentPrice: 267.89, changePct: -1.2 },
  { name: '한화에어로', code: '012450', currentPrice: 315000, changePct: 4.3 },
  { name: 'SOFI', code: 'SOFI', currentPrice: 12.34, changePct: 3.7 },
];

const dummyAlerts = [
  { time: '07:15', icon: '🤖', title: '삼성전자 AI 시그널', desc: '매수 시그널 3개 집중 — 반도체 업황 개선 기대감', type: 'signal' },
  { time: '06:50', icon: '📢', title: 'SK하이닉스 공시', desc: '2024년 4분기 실적 발표 — 영업이익 7.7조 원', type: 'disclosure' },
  { time: '06:30', icon: '📈', title: 'NVIDIA 목표가 상향', desc: '골드만삭스 목표가 $950 → $1,100 상향', type: 'signal' },
  { time: '06:00', icon: '⚠️', title: '카카오 손절 검토', desc: 'AI 판단: 손절 라인 도달, 포지션 재검토 필요', type: 'ai' },
];

const dummyNews = [
  { time: '08:00', source: '한경', title: '미국 반도체 수출규제 완화 시그널... 엔비디아 시간외 +3%', tag: '반도체' },
  { time: '07:30', source: '매경', title: '연준 파월 "인플레이션 둔화 확인"... 6월 금리인하 기대↑', tag: '매크로' },
  { time: '07:00', source: 'Bloomberg', title: '비트코인 $90K 돌파 임박, ETF 자금 유입 가속', tag: '크립토' },
  { time: '06:30', source: '로이터', title: '삼성전자-TSMC AI칩 수주 경쟁 격화', tag: '반도체' },
  { time: '06:00', source: '조선비즈', title: '2차전지 섹터 반등세... LG엔솔 외국인 3일 연속 순매수', tag: '2차전지' },
];

const dummyVideos = [
  { id: 1, channel: '이효석아카데미', time: '오늘 07:30', title: '반도체 사이클 2차 랠리 시작된다', category: '한국주식', summary: '필라델피아 반도체 지수가 3일 연속 상승하며 2차 랠리 신호를 보이고 있다.', stocks: ['SK하이닉스', '삼성전자', 'ASML'], hasSignal: true },
  { id: 2, channel: '월가아재', time: '오늘 06:00', title: '미국 고용지표 쇼크, 연준 피벗 앞당겨질까', category: '미국주식', summary: '비농업 고용이 컨센서스 대비 크게 하회하며 경기 둔화 우려가 부각됐다.', stocks: ['SPY', 'QQQ', 'TLT'], hasSignal: true },
  { id: 3, channel: '삼프로TV', time: '오늘 08:00', title: '[마감시황] 외국인 반도체 폭풍매수, 코스피 2600 돌파', category: '한국주식', summary: '외국인이 삼성전자와 SK하이닉스를 중심으로 4거래일 연속 순매수.', stocks: ['삼성전자', 'SK하이닉스'], hasSignal: true },
];

// ============ STYLES ============
const colors = {
  bg: '#F8F9FA',
  card: '#FFFFFF',
  primary: '#1A1A2E',
  accent: '#2563EB',
  red: '#EF4444',
  blue: '#3B82F6',
  green: '#10B981',
  gray: '#6B7280',
  lightGray: '#E5E7EB',
};

const categoryColors: Record<string, { bg: string; text: string }> = {
  '한국주식': { bg: '#DBEAFE', text: '#1E40AF' },
  '미국주식': { bg: '#FEE2E2', text: '#991B1B' },
  '크립토':   { bg: '#FEF3C7', text: '#92400E' },
};

// ============ SPARKLINE SVG ============
const Sparkline = ({ data, isUp, width = 120, height = 44 }: { data: number[]; isUp: boolean; width?: number; height?: number }) => {
  if (!data || data.length < 2) return <div style={{ width, height }} />;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return `${x},${y}`;
  });
  const pathD = `M ${pts.join(' L ')}`;
  const fillD = `M ${pts[0]} L ${pts.join(' L ')} L ${width},${height} L 0,${height} Z`;
  const stroke = isUp ? '#EF4444' : '#3B82F6';
  const fill = isUp ? 'rgba(239,68,68,0.1)' : 'rgba(59,130,246,0.1)';
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ display: 'block' }}>
      <path d={fillD} fill={fill} />
      <path d={pathD} fill="none" stroke={stroke} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

// ============ MARKET MINI CARD ============
const MarketMiniCard = ({
  label,
  item,
  loading,
  prefix = '',
  decimals = 2,
}: {
  label: string;
  item: MarketItem | null | undefined;
  loading: boolean;
  prefix?: string;
  decimals?: number;
}) => {
  const isUp = !item || item.changePct >= 0;
  const upColor = '#EF4444';
  const downColor = '#3B82F6';
  const color = isUp ? upColor : downColor;
  const sign = item && item.changePct >= 0 ? '+' : '';

  return (
    <div style={{
      flex: '1 1 calc(50% - 8px)',
      minWidth: 140,
      background: colors.card,
      borderRadius: 14,
      padding: '14px 16px',
      border: `1px solid ${colors.lightGray}`,
      overflow: 'hidden',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 2 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: colors.primary }}>{label}</span>
        {item && (
          <span style={{ fontSize: 13, fontWeight: 700, color }}>
            {isUp ? '↘' : '↘'} {sign}{item.changePct.toFixed(2)}%
          </span>
        )}
      </div>
      {loading ? (
        <div style={{ fontSize: 12, color: colors.gray }}>로딩중...</div>
      ) : item ? (
        <>
          <div style={{ fontSize: 16, fontWeight: 700, color: colors.primary, marginTop: 2 }}>
            {prefix}{item.price > 1000 ? item.price.toLocaleString() : item.price.toFixed(decimals)}
          </div>
          <div style={{ fontSize: 12, color, marginTop: 1 }}>
            {sign}{item.change > 1000 ? item.change.toLocaleString() : item.change.toFixed(decimals)}
          </div>
          <div style={{ marginTop: 8 }}>
            <Sparkline data={item.sparkline ?? []} isUp={item.changePct >= 0} width={120} height={40} />
          </div>
        </>
      ) : (
        <div style={{ fontSize: 12, color: colors.gray }}>데이터 없음</div>
      )}
    </div>
  );
};

// ============ COMPONENTS ============
const TabBar = ({ active, setActive }: { active: string; setActive: (t: string) => void }) => {
  const tabs = [
    { id: 'now',    label: '지금' },
    { id: 'live',   label: 'LIVE', dot: true },
    { id: 'news',   label: '뉴스' },
    { id: 'signal', label: '시그널' },
  ];
  return (
    <div style={{ display: 'flex', gap: 0, borderBottom: `2px solid ${colors.lightGray}`, marginBottom: 24 }}>
      {tabs.map(t => (
        <button
          key={t.id}
          onClick={() => setActive(t.id)}
          style={{
            padding: '12px 24px', background: 'none', border: 'none',
            borderBottom: active === t.id ? `3px solid ${colors.accent}` : '3px solid transparent',
            color: active === t.id ? colors.accent : colors.gray,
            fontWeight: active === t.id ? 700 : 500, fontSize: 15, cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: 6,
            fontFamily: "'Pretendard', -apple-system, sans-serif", transition: 'all 0.2s',
          }}
        >
          {t.dot && <span style={{ width: 8, height: 8, borderRadius: '50%', background: colors.red, display: 'inline-block' }} />}
          {t.label}
        </button>
      ))}
    </div>
  );
};

const Card = ({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) => (
  <div style={{
    background: colors.card, borderRadius: 16, padding: '20px 24px', marginBottom: 16,
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)', ...style,
  }}>
    {children}
  </div>
);

const SectionHeader = ({ title, action }: { title: string; action?: string }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
    <span style={{ fontSize: 16, fontWeight: 700, color: colors.primary }}>{title}</span>
    {action && <span style={{ fontSize: 13, color: colors.accent, cursor: 'pointer' }}>{action}</span>}
  </div>
);

const FilterPill = ({ label, active, onClick, icon }: { label: string; active: boolean; onClick: () => void; icon?: string }) => (
  <button
    onClick={onClick}
    style={{
      padding: '8px 16px', borderRadius: 20,
      border: active ? 'none' : `1px solid ${colors.lightGray}`,
      background: active ? colors.accent : colors.card,
      color: active ? '#fff' : colors.gray,
      fontSize: 13, fontWeight: 600, cursor: 'pointer',
      display: 'flex', alignItems: 'center', gap: 4,
      fontFamily: "'Pretendard', -apple-system, sans-serif", transition: 'all 0.15s',
    }}
  >
    {icon && <span>{icon}</span>}
    {label}
  </button>
);

// ============ HEATMAP SECTION ============
// TradingView Stock Heatmap 위젯 (공식 embed-widget-stock-heatmap.js)
const HEATMAP_CONFIGS = {
  sp500: {
    label: 'S&P500',
    exchanges: [],
    dataSource: 'SPX500',
    grouping: 'sector',
    blockSize: 'market_cap_basic',
    blockColor: 'change',
    locale: 'en',
    colorTheme: 'light',
    hasTopBar: false,
    isDataSetEnabled: false,
    isZoomEnabled: true,
    hasSymbolTooltip: true,
    isMonoSize: false,
    width: '100%',
    height: 500,
  },
  kospi: {
    label: '코스피',
    exchanges: [],
    dataSource: 'KOSPI',
    grouping: 'sector',
    blockSize: 'market_cap_basic',
    blockColor: 'change',
    locale: 'ko',
    colorTheme: 'light',
    hasTopBar: false,
    isDataSetEnabled: false,
    isZoomEnabled: true,
    hasSymbolTooltip: true,
    isMonoSize: false,
    width: '100%',
    height: 500,
  },
  crypto: {
    label: '크립토',
    exchanges: [],
    dataSource: 'Crypto',
    grouping: 'no_group',
    blockSize: 'market_cap_calc',
    blockColor: 'change',
    locale: 'en',
    colorTheme: 'light',
    hasTopBar: false,
    isDataSetEnabled: false,
    isZoomEnabled: true,
    hasSymbolTooltip: true,
    isMonoSize: false,
    width: '100%',
    height: 500,
  },
} as const;

type HeatmapKey = keyof typeof HEATMAP_CONFIGS;

// 실제 위젯 렌더: 탭 전환 시 스크립트 재주입
const TradingViewHeatmap = ({ config }: { config: typeof HEATMAP_CONFIGS[HeatmapKey] }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    // 이전 위젯 제거
    containerRef.current.innerHTML = '';

    const widgetDiv = document.createElement('div');
    widgetDiv.className = 'tradingview-widget-container__widget';
    widgetDiv.style.cssText = 'height:calc(100% - 32px);width:100%';
    containerRef.current.appendChild(widgetDiv);

    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js';
    script.async = true;
    script.innerHTML = JSON.stringify(config);
    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) containerRef.current.innerHTML = '';
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config.dataSource]);

  return (
    <div
      ref={containerRef}
      className="tradingview-widget-container"
      style={{ height: 500, width: '100%' }}
    />
  );
};

const HeatmapSection = () => {
  const [activeMap, setActiveMap] = useState<HeatmapKey>('sp500');

  return (
    <Card style={{ padding: '20px 24px' }}>
      <SectionHeader title="🗺️ 히트맵" />

      {/* 탭 */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {(Object.keys(HEATMAP_CONFIGS) as HeatmapKey[]).map(k => (
          <button
            key={k}
            onClick={() => setActiveMap(k)}
            style={{
              padding: '6px 16px', borderRadius: 8, fontSize: 13, fontWeight: 600,
              background: activeMap === k ? colors.accent : colors.bg,
              color: activeMap === k ? '#fff' : colors.gray,
              border: `1px solid ${activeMap === k ? colors.accent : colors.lightGray}`,
              cursor: 'pointer', transition: 'all 0.15s',
            }}
          >
            {HEATMAP_CONFIGS[k].label}
          </button>
        ))}
      </div>

      {/* 위젯 */}
      <div style={{ borderRadius: 12, overflow: 'hidden', height: 500 }}>
        <TradingViewHeatmap config={HEATMAP_CONFIGS[activeMap]} />
      </div>

      <div style={{ fontSize: 11, color: colors.gray, textAlign: 'right', marginTop: 6 }}>
        Powered by TradingView
      </div>
    </Card>
  );
};

// ============ TAB: 지금 ============
// 순서: 1.보유종목 2.오늘알림 3.관심종목 4.시황 5.히트맵
const NowTab = () => {
  const { data, loading } = useExtendedMarketData();

  return (
    <div>
      {/* 1. 보유종목 */}
      <Card>
        <SectionHeader title="🧳 보유종목" action="전체보기 →" />
        <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 4 }}>
          {dummyHoldings.map((s, i) => (
            <div key={i} style={{
              minWidth: 130, padding: '14px 16px', borderRadius: 12,
              background: colors.bg, flexShrink: 0, textAlign: 'center',
              border: `1px solid ${colors.lightGray}`,
            }}>
              <div style={{ fontWeight: 700, fontSize: 14, color: colors.primary }}>{s.name}</div>
              <div style={{ fontWeight: 700, fontSize: 15, color: colors.primary, marginTop: 8 }}>
                {s.currentPrice > 1000
                  ? s.currentPrice.toLocaleString()
                  : s.currentPrice}
              </div>
              <div style={{
                fontSize: 14, fontWeight: 700, marginTop: 4,
                color: s.returnPct >= 0 ? colors.red : colors.blue,
              }}>
                {s.returnPct >= 0 ? '+' : ''}{s.returnPct.toFixed(2)}%
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* 2. 오늘 알림 */}
      {dummyAlerts.length > 0 && (
        <Card>
          <SectionHeader title="🔔 오늘 알림" action="전체 보기 →" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {dummyAlerts.map((a, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'flex-start', gap: 12,
                padding: '12px 0',
                borderBottom: i < dummyAlerts.length - 1 ? `1px solid ${colors.lightGray}` : 'none',
                cursor: 'pointer',
              }}>
                <span style={{ fontSize: 20 }}>{a.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 14, color: colors.primary }}>{a.title}</div>
                  <div style={{ fontSize: 13, color: colors.gray, marginTop: 2 }}>{a.desc}</div>
                </div>
                <span style={{ fontSize: 12, color: colors.gray, whiteSpace: 'nowrap' }}>{a.time}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* 3. 관심종목 */}
      <Card>
        <SectionHeader title="⭐ 관심종목" action="전체보기 →" />
        <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 4 }}>
          {dummyWatchlist.map((s, i) => (
            <div key={i} style={{
              minWidth: 120, padding: '12px 16px', borderRadius: 12,
              background: colors.bg, textAlign: 'center', flexShrink: 0,
            }}>
              <div style={{ fontWeight: 600, fontSize: 13, color: colors.primary }}>{s.name}</div>
              <div style={{
                fontSize: 14, fontWeight: 700, marginTop: 6,
                color: s.changePct >= 0 ? colors.red : colors.blue,
              }}>
                {s.changePct >= 0 ? '+' : ''}{s.changePct}%
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* 4. 시황 — 미니차트 카드 */}
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
          <span style={{ fontSize: 16, fontWeight: 700, color: colors.primary }}>📊 시황</span>
          {!loading && data && (
            <span style={{ fontSize: 11, color: colors.gray }}>{data.updatedAt} 기준</span>
          )}
        </div>

        {/* 미국 선물 */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: colors.gray, marginBottom: 10, letterSpacing: 0.5 }}>
            🇺🇸 미국 선물
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            <MarketMiniCard label="S&P 선물" item={data?.SP_FUTURES} loading={loading} decimals={0} />
            <MarketMiniCard label="나스닥 선물" item={data?.NQ_FUTURES} loading={loading} decimals={0} />
            <MarketMiniCard label="다우 선물" item={data?.DOW_FUTURES} loading={loading} decimals={0} />
            <MarketMiniCard label="VIX" item={data?.VIX} loading={loading} decimals={2} />
          </div>
        </div>

        {/* 한국 */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: colors.gray, marginBottom: 10, letterSpacing: 0.5 }}>
            🇰🇷 한국장
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            <MarketMiniCard label="코스피" item={data?.KOSPI} loading={loading} decimals={2} />
            <MarketMiniCard label="코스닥" item={data?.KOSDAQ} loading={loading} decimals={2} />
          </div>
        </div>

        {/* 크립토 */}
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, color: colors.gray, marginBottom: 10, letterSpacing: 0.5 }}>
            ₿ 크립토
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            <MarketMiniCard label="비트코인" item={data?.BTC} loading={loading} decimals={0} prefix="$" />
            <MarketMiniCard label="이더리움" item={data?.ETH} loading={loading} decimals={0} prefix="$" />
          </div>
        </div>
      </Card>

      {/* 5. 히트맵 */}
      <HeatmapSection />
    </div>
  );
};

// ============ TAB: 뉴스 ============
const NewsItem = ({ n, showBadge, isLast }: { n: StockNews; showBadge?: boolean; isLast?: boolean }) => (
  <a
    href={n.url}
    target="_blank"
    rel="noopener noreferrer"
    style={{
      display: 'flex', alignItems: 'center', gap: 12,
      padding: '12px 0', textDecoration: 'none',
      borderBottom: isLast ? 'none' : `1px solid ${colors.lightGray}`,
    }}
  >
    {showBadge && n.stock_name && n.stock_name !== '시장뉴스' && (
      <span style={{
        padding: '3px 8px', borderRadius: 4, fontSize: 11, fontWeight: 600,
        background: '#EFF6FF', color: '#3182f6', whiteSpace: 'nowrap',
      }}>{n.stock_name}</span>
    )}
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{
        fontSize: 14, fontWeight: 500, color: colors.primary,
        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
      }}>{n.title}</div>
      <div style={{ fontSize: 12, color: colors.gray, marginTop: 2 }}>
        {n.source && `${n.source} · `}{formatNewsTime(n.published_at)}
      </div>
    </div>
  </a>
);

const formatNewsTime = (dateStr: string | null) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffH = Math.floor(diffMs / (1000 * 60 * 60));
  if (diffH < 1) return `${Math.max(1, Math.floor(diffMs / (1000 * 60)))}분 전`;
  if (diffH < 24) return `${diffH}시간 전`;
  const diffD = Math.floor(diffH / 24);
  if (diffD < 7) return `${diffD}일 전`;
  return `${d.getMonth() + 1}/${d.getDate()}`;
};

const NewsTab = () => {
  const [marketNews, setMarketNews] = useState<StockNews[]>([]);
  const [myNews, setMyNews] = useState<StockNews[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const myTickers = [
      ...dummyHoldings.map(h => h.code),
      ...dummyWatchlist.map(w => w.code),
    ].filter(c => c.length === 6 && /^\d+$/.test(c));

    Promise.all([
      getMarketNews(10),
      myTickers.length > 0 ? getNewsByTickers(myTickers, 20) : Promise.resolve([]),
    ]).then(([market, my]) => {
      setMarketNews(market);
      setMyNews(my);
      setLoading(false);
    });
  }, []);

  if (loading) return <Card style={{ padding: '20px 24px' }}><div style={{ textAlign: 'center', padding: 24, color: colors.gray, fontSize: 14 }}>로딩중...</div></Card>;

  return (
    <div>
      {/* 시장 주요 뉴스 */}
      <Card style={{ padding: '20px 24px' }}>
        <SectionHeader title="📰 시장 주요 뉴스" />
        {marketNews.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 16, color: colors.gray, fontSize: 14 }}>시장 뉴스가 없습니다</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {marketNews.map((n, i) => (
              <NewsItem key={n.id} n={n} isLast={i === marketNews.length - 1} />
            ))}
          </div>
        )}
      </Card>

      {/* 내 종목 뉴스 */}
      <Card style={{ padding: '20px 24px' }}>
        <SectionHeader title="📋 내 종목 뉴스" />
        {myNews.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 16, color: colors.gray, fontSize: 14 }}>종목 뉴스가 없습니다</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {myNews.map((n, i) => (
              <NewsItem key={n.id} n={n} showBadge isLast={i === myNews.length - 1} />
            ))}
          </div>
        )}
        <Link href="/explore/news" style={{
          display: 'block', textAlign: 'center', marginTop: 16,
          fontSize: 13, fontWeight: 600, color: colors.accent, textDecoration: 'none',
        }}>
          더 보기 →
        </Link>
      </Card>
    </div>
  );
};

// ============ TAB: LIVE ============
const LiveTab = () => {
  const [filter, setFilter] = useState('전체');
  const [catFilter, setCatFilter] = useState('전체');
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  const categories = ['전체', '한국주식', '미국주식', '크립토'];
  const myStocks = [
    ...dummyHoldings.map(h => h.name),
    ...dummyWatchlist.map(w => w.name),
  ];

  const filtered = dummyVideos.filter(v => {
    if (catFilter !== '전체' && v.category !== catFilter) return false;
    if (filter === '내 종목') return v.stocks.some(s => myStocks.includes(s));
    return true;
  });

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
        <FilterPill label="내 종목" icon="⭐" active={filter === '내 종목'} onClick={() => setFilter(filter === '내 종목' ? '전체' : '내 종목')} />
        <FilterPill label="전체" active={filter === '전체' && catFilter === '전체'} onClick={() => { setFilter('전체'); setCatFilter('전체'); }} />
      </div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {categories.map(c => (
          <FilterPill key={c} label={c} active={catFilter === c} onClick={() => setCatFilter(c)} />
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {filtered.map(v => {
          const isExpanded = expanded[v.id];
          const catColor = categoryColors[v.category] || { bg: '#F3F4F6', text: '#374151' };
          const hasMyStock = v.stocks.some(s => myStocks.includes(s));
          return (
            <Card key={v.id} style={{
              border: hasMyStock ? `2px solid ${colors.accent}` : '1px solid #F3F4F6',
              background: hasMyStock ? '#F8FAFF' : colors.card,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: '50%', background: '#E5E7EB',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 14, fontWeight: 700, color: '#374151',
                  }}>
                    {v.channel[0]}
                  </div>
                  <span style={{ fontWeight: 700, fontSize: 14, color: colors.primary }}>{v.channel}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{
                    padding: '3px 8px', borderRadius: 6, fontSize: 11, fontWeight: 600,
                    background: catColor.bg, color: catColor.text,
                  }}>{v.category}</span>
                  <span style={{ fontSize: 12, color: colors.gray }}>{v.time}</span>
                </div>
              </div>

              <div style={{ fontWeight: 700, fontSize: 15, color: colors.primary, marginBottom: 8, lineHeight: 1.4 }}>
                {v.title}
              </div>

              <div style={{
                fontSize: 13, color: '#4B5563', lineHeight: 1.6, marginBottom: 10,
                overflow: 'hidden', maxHeight: isExpanded ? 'none' : 65,
              }}>
                {v.summary}
              </div>

              {v.summary.length > 100 && (
                <button
                  onClick={() => setExpanded(prev => ({ ...prev, [v.id]: !prev[v.id] }))}
                  style={{
                    background: 'none', border: 'none', color: colors.accent,
                    fontSize: 12, fontWeight: 600, cursor: 'pointer', padding: 0, marginBottom: 10,
                  }}
                >
                  {isExpanded ? '접기 ▲' : '더보기 ▼'}
                </button>
              )}

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {v.stocks.length > 0 && (
                    <>
                      <span style={{ fontSize: 12, color: colors.gray }}>📌</span>
                      {v.stocks.map((s, i) => (
                        <span key={i} style={{
                          padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 600,
                          background: myStocks.includes(s) ? '#DBEAFE' : '#F3F4F6',
                          color: myStocks.includes(s) ? '#1E40AF' : '#6B7280',
                        }}>{s}</span>
                      ))}
                    </>
                  )}
                </div>
                <button style={{
                  padding: '6px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                  background: colors.red, color: '#fff', border: 'none', cursor: 'pointer',
                }}>
                  🎬 영상 보기
                </button>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

// ============ TAB: 시그널 ============
const signalTypeStyle: Record<string, { bg: string; color: string; label: string }> = {
  매수:   { bg: '#FEE2E2', color: '#DC2626', label: '매수' },
  매도:   { bg: '#DBEAFE', color: '#2563EB', label: '매도' },
  긍정:   { bg: '#D1FAE5', color: '#059669', label: '긍정' },
  부정:   { bg: '#F3F4F6', color: '#6B7280', label: '부정' },
  중립:   { bg: '#FEF3C7', color: '#D97706', label: '중립' },
  저평가: { bg: '#EDE9FE', color: '#7C3AED', label: '저평가' },
};

const dummySignals = [
  {
    id: 1,
    source: '인플루언서',
    author: '이효석',
    avatar: '이',
    time: '07:15',
    quote: '"엔비디아 지금 당장 사야해"',
    stock: '엔비디아',
    ticker: 'NVDA',
    signal: '매수',
    link: 'https://www.youtube.com/watch?v=dummylink1',
    linkType: '영상',
    linkIcon: '🎬',
  },
  {
    id: 2,
    source: '구루',
    author: '워런 버핏',
    avatar: '버',
    time: '06:30',
    quote: '"지금 당장 현금 비중 늘려라"',
    stock: '시장 전체',
    ticker: null,
    signal: '매도',
    link: 'https://twitter.com/WarrenBuffett',
    linkType: 'X',
    linkIcon: '𝕏',
  },
  {
    id: 3,
    source: 'AI',
    author: '알고리즘',
    avatar: '🤖',
    time: '06:00',
    quote: '삼성전자 PBR 0.89 — 역대 최저',
    stock: '삼성전자',
    ticker: '005930',
    signal: '저평가',
    link: '#chart',
    linkType: '차트',
    linkIcon: '📈',
  },
  {
    id: 4,
    source: '인플루언서',
    author: '코린이아빠',
    avatar: '코',
    time: '05:45',
    quote: '"SK하이닉스 실적 보고 확신 생겼다"',
    stock: 'SK하이닉스',
    ticker: '000660',
    signal: '매수',
    link: 'https://www.youtube.com/watch?v=dummylink4',
    linkType: '영상',
    linkIcon: '🎬',
  },
  {
    id: 5,
    source: '공시',
    author: '공시',
    avatar: '📢',
    time: '05:00',
    quote: '대표이사 주식 50만주 매도',
    stock: '카카오',
    ticker: '035720',
    signal: '매도',
    link: 'https://dart.fss.or.kr',
    linkType: '공시',
    linkIcon: '📋',
  },
];

const sourceStyle: Record<string, { bg: string; color: string }> = {
  인플루언서: { bg: '#DBEAFE', color: '#1E40AF' },
  구루:       { bg: '#FEF3C7', color: '#92400E' },
  AI:         { bg: '#EDE9FE', color: '#6D28D9' },
  공시:       { bg: '#D1FAE5', color: '#065F46' },
};

const SignalTab = () => (
  <div>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {dummySignals.map(s => {
        const sig = signalTypeStyle[s.signal] || signalTypeStyle['중립'];
        const src = sourceStyle[s.source] || { bg: '#F3F4F6', color: '#374151' };
        const isEmoji = s.avatar.length <= 2 && /\p{Emoji}/u.test(s.avatar);
        return (
          <div key={s.id} style={{
            background: colors.card, borderRadius: 16, padding: '16px 18px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            borderLeft: `4px solid ${sig.color}`,
          }}>
            {/* 헤더 */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%',
                background: isEmoji ? '#F3F4F6' : colors.accent,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: isEmoji ? 18 : 14, fontWeight: 700,
                color: isEmoji ? undefined : '#fff', flexShrink: 0,
              }}>
                {s.avatar}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontWeight: 700, fontSize: 14, color: colors.primary }}>{s.author}</span>
                  <span style={{
                    padding: '2px 7px', borderRadius: 4, fontSize: 11, fontWeight: 600,
                    background: src.bg, color: src.color,
                  }}>{s.source}</span>
                </div>
                <span style={{ fontSize: 12, color: colors.gray }}>{s.time}</span>
              </div>
              {/* 시그널 배지 */}
              <span style={{
                padding: '5px 12px', borderRadius: 20, fontSize: 13, fontWeight: 700,
                background: sig.bg, color: sig.color,
              }}>{sig.label}</span>
            </div>

            {/* 인용 */}
            <div style={{
              fontSize: 14, color: '#374151', lineHeight: 1.55, marginBottom: 10,
              fontStyle: s.quote.startsWith('"') ? 'italic' : 'normal',
            }}>
              {s.quote}
            </div>

            {/* 종목 + 링크 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{
                  padding: '3px 10px', borderRadius: 6, fontSize: 12, fontWeight: 700,
                  background: sig.bg, color: sig.color,
                }}>
                  {s.stock}{s.ticker ? ` (${s.ticker})` : ''}
                </span>
              </div>
              <a
                href={s.link}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex', alignItems: 'center', gap: 4,
                  padding: '6px 12px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                  background: colors.bg, color: colors.accent,
                  border: `1px solid ${colors.lightGray}`,
                  textDecoration: 'none',
                }}
              >
                {s.linkIcon} {s.linkType}
              </a>
            </div>
          </div>
        );
      })}
    </div>
  </div>
);

// ============ MAIN ============
export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('now');

  return (
    <div style={{
      maxWidth: 800, margin: '0 auto', padding: '24px 16px',
      background: colors.bg, minHeight: '100vh',
      fontFamily: "'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif",
    }}>
      <div style={{ marginBottom: 8 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: colors.primary, margin: 0 }}>📊 대시보드</h1>
        <p style={{ fontSize: 13, color: colors.gray, margin: '4px 0 0' }}>내 종목 현황</p>
      </div>

      <TabBar active={activeTab} setActive={setActiveTab} />

      {activeTab === 'now'    && <NowTab />}
      {activeTab === 'live'   && <LiveTab />}
      {activeTab === 'news'   && <NewsTab />}
      {activeTab === 'signal' && <SignalTab />}
    </div>
  );
}
