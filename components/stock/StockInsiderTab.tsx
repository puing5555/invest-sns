'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { getInsiderTrades, getInsiderTradesByName, type InsiderTrade } from '@/lib/supabase';

const ComposedChart = dynamic(() => import('recharts').then(m => m.ComposedChart), { ssr: false });
const Area = dynamic(() => import('recharts').then(m => m.Area), { ssr: false });
const Line = dynamic(() => import('recharts').then(m => m.Line), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(m => m.YAxis), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(m => m.Tooltip), { ssr: false });
const ResponsiveContainer = dynamic(() => import('recharts').then(m => m.ResponsiveContainer), { ssr: false });
const ReferenceDot = dynamic(() => import('recharts').then(m => m.ReferenceDot), { ssr: false });
import { isKoreanStock, formatStockPrice } from '@/lib/currency';
import stockPricesData from '@/data/stockPrices.json';
import { formatStockDisplay } from '@/lib/stockNames';

const TRADE_COLORS: Record<string, string> = { '매수': '#22c55e', '매도': '#ef4444' };

type InsiderGrade = 'S' | 'A' | 'B' | 'C' | 'D' | 'E';
const GRADE_META: Record<InsiderGrade, { label: string; color: string; bg: string; dotSize: number }> = {
  S: { label: '핵심', color: '#dc2626', bg: '#fef2f2', dotSize: 8 },
  A: { label: '경영진', color: '#b45309', bg: '#fef3c7', dotSize: 8 },
  B: { label: '사외이사', color: '#0e7490', bg: '#ecfeff', dotSize: 5 },
  C: { label: '계열사', color: '#7c3aed', bg: '#ede9fe', dotSize: 5 },
  D: { label: '임원', color: '#16a34a', bg: '#f0fdf4', dotSize: 5 },
  E: { label: '기관', color: '#2563eb', bg: '#eff6ff', dotSize: 3 },
};

type FilterKey = 'all' | 'S' | 'A' | 'B' | 'C' | 'D' | 'E';
const FILTER_BUTTONS: { key: FilterKey; label: string }[] = [
  { key: 'all', label: '전체' }, { key: 'S', label: '핵심' }, { key: 'A', label: '경영진' },
  { key: 'B', label: '사외이사' }, { key: 'C', label: '계열사' }, { key: 'D', label: '임원' }, { key: 'E', label: '기관' },
];

const CORP_KEYWORDS = ['홀딩스', '지주', '(주)', '(유)'];
const INST_KEYWORDS = ['공단', '연금', '투자', '자산운용', '은행', '증권', '블랙록', '캐피탈', '보험', '펀드', '신탁', 'BlackRock', 'Capital', 'Fund', 'Insurance'];

function normalizeInsiderName(name: string): string {
  return name.replace(/^\(주\)\s*/, '').replace(/^\(유\)\s*/, '').trim();
}

function gradeInsider(name: string, position: string | null): InsiderGrade {
  // E: 기관 (공단, 연금, 자산운용, 블랙록 등)
  if (INST_KEYWORDS.some(kw => name.includes(kw))) return 'E';
  // C: 계열사 (법인 키워드)
  if (CORP_KEYWORDS.some(kw => name.includes(kw))) return 'C';
  const pos = position || '';
  // B: 사외이사
  if (pos.includes('사외이사') || pos.includes('사외')) return 'B';
  // S: 핵심 (최대주주, 특수관계인, 대표급)
  if (['최대주주', '특수관계인', '대표이사회장', '대표이사부회장', '대표부회장', '대표사장', '대표이사', '회장', '부회장'].some(p => pos.includes(p))) return 'S';
  // A: 경영진 (사장, 부사장, 전무, C-level)
  if (['사장', '부사장', '전무', 'CEO', 'CFO', 'COO', 'CTO'].some(p => pos.includes(p))) return 'A';
  // D: 임원
  if (['상무', '이사', '감사'].some(p => pos.includes(p))) return 'D';
  // position 없으면 핵심으로 (최대주주/특수관계인이 position 비어있는 경우 많음)
  if (!pos) return 'S';
  return 'D';
}

function matchesFilter(grade: InsiderGrade, fk: FilterKey): boolean {
  if (fk === 'all') return true;
  return grade === fk;
}

function findPriceIdx(prices: { date: string }[], td: string): number {
  let lo = 0, hi = prices.length - 1, ci = 0;
  while (lo <= hi) { const mid = (lo + hi) >> 1; if (prices[mid].date <= td) { ci = mid; lo = mid + 1; } else hi = mid - 1; }
  return ci;
}

function getPositionBadge(position: string): { color: string; bg: string } | null {
  if (!position) return null;
  if (['사장', '대표이사', '회장'].some(p => position.includes(p))) return { color: '#92710a', bg: '#fef3c7' };
  if (['부사장', '전무', '부회장'].some(p => position.includes(p))) return { color: '#57606a', bg: '#e8eaed' };
  return { color: '#8b95a1', bg: '#f4f4f4' };
}

export default function StockInsiderTab({ code }: { code: string }) {
  const [allTrades, setAllTrades] = useState<InsiderTrade[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | '매수' | '매도'>('all');
  const [selectedInsider, setSelectedInsider] = useState<string | null>(null);
  const [periodFilter, setPeriodFilter] = useState('1년');
  const [showAllChips, setShowAllChips] = useState(false);
  const [showAllCards, setShowAllCards] = useState(false);
  const [perfSort, setPerfSort] = useState<'amount' | 'profit' | 'return'>('amount');
  const [typeFilter, setTypeFilter] = useState<FilterKey>('all');
  const [visibleCount, setVisibleCount] = useState(30);
  const [modalInsider, setModalInsider] = useState<string | null>(null);
  const [otherTrades, setOtherTrades] = useState<InsiderTrade[]>([]);
  const [otherLoading, setOtherLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    (async () => {
      const data = await getInsiderTrades(code);
      setAllTrades(data.map(t => ({ ...t, insider_name: normalizeInsiderName(t.insider_name) })));
      setLoading(false);
    })();
  }, [code]);

  // 기간 필터는 차트/거래 리스트용 trades만 파생 (수익률 카드는 allTrades 사용)
  const trades = useMemo(() => {
    if (allTrades.length === 0) return [];
    if (periodFilter === '전체') return allTrades;
    const cutoff = new Date();
    switch (periodFilter) {
      case '1개월': cutoff.setMonth(cutoff.getMonth() - 1); break;
      case '6개월': cutoff.setMonth(cutoff.getMonth() - 6); break;
      case '1년': cutoff.setFullYear(cutoff.getFullYear() - 1); break;
      case '3년': cutoff.setFullYear(cutoff.getFullYear() - 3); break;
    }
    const since = cutoff.toISOString().slice(0, 10);
    return allTrades.filter(t => !t.trade_date || t.trade_date >= since);
  }, [allTrades, periodFilter]);

  const stockData = (stockPricesData as any)[code];
  const gradeMap = useMemo(() => { const gm = new Map<string, InsiderGrade>(); allTrades.forEach(t => { if (!gm.has(t.insider_name)) gm.set(t.insider_name, gradeInsider(t.insider_name, t.position)); }); return gm; }, [allTrades]);

  const { topChips, restChips } = useMemo(() => {
    const filtered = typeFilter === 'all' ? trades : trades.filter(t => matchesFilter(gradeMap.get(t.insider_name) || 'C', typeFilter));
    const countMap = new Map<string, number>(); const amountMap = new Map<string, number>();
    filtered.forEach(t => { countMap.set(t.insider_name, (countMap.get(t.insider_name) || 0) + 1); if (t.trade_type === '매수') amountMap.set(t.insider_name, (amountMap.get(t.insider_name) || 0) + (t.shares || 0)); });
    const all = Array.from(countMap.entries()).map(([name, count]) => ({ name, count, buyShares: amountMap.get(name) || 0 })).sort((a, b) => b.buyShares - a.buyShares);
    if (all.length <= 30) return { topChips: all, restChips: [] as typeof all };
    return { topChips: all.slice(0, 30), restChips: all.slice(30) };
  }, [trades, typeFilter, gradeMap]);

  const filteredTrades = useMemo(() => {
    let result = trades;
    if (typeFilter !== 'all') result = result.filter(t => matchesFilter(gradeMap.get(t.insider_name) || 'C', typeFilter));
    if (filter !== 'all') result = result.filter(t => t.trade_type === filter);
    if (selectedInsider) result = result.filter(t => t.insider_name === selectedInsider);
    return result;
  }, [trades, filter, selectedInsider, typeFilter, gradeMap]);

  useEffect(() => { setVisibleCount(30); setShowAllChips(false); setShowAllCards(false); }, [filter, selectedInsider, periodFilter, typeFilter]);

  const openModal = useCallback(async (name: string) => { setModalInsider(name); setSelectedInsider(name); setOtherLoading(true); const data = await getInsiderTradesByName(name); setOtherTrades(data.map(t => ({ ...t, insider_name: normalizeInsiderName(t.insider_name) }))); setOtherLoading(false); }, []);
  const closeModal = useCallback(() => { setModalInsider(null); setSelectedInsider(null); }, []);

  const { chartData, groupedMarkers } = useMemo(() => {
    if (!stockData?.prices?.length) return { chartData: [], groupedMarkers: [] };
    let prices = stockData.prices;
    if (periodFilter && periodFilter !== '전체') {
      const cutoff = new Date();
      switch (periodFilter) { case '1개월': cutoff.setMonth(cutoff.getMonth() - 1); break; case '6개월': cutoff.setMonth(cutoff.getMonth() - 6); break; case '1년': cutoff.setFullYear(cutoff.getFullYear() - 1); break; case '3년': cutoff.setFullYear(cutoff.getFullYear() - 3); break; }
      const f = prices.filter((p: any) => new Date(p.date) >= cutoff); if (f.length >= 2) prices = f;
    }
    const data = prices.map((p: any, i: number) => ({ idx: i, date: p.date, timestamp: new Date(p.date).getTime(), close: p.close }));
    const rawMarkers = filteredTrades.filter(t => t.trade_date).map(t => { const ci = findPriceIdx(prices, t.trade_date!); return { ...t, dataIdx: ci, priceAtTrade: prices[ci].close, timestamp: data[ci].timestamp }; });
    const groupMap = new Map<string, { dataIdx: number; priceAtTrade: number; trade_type: string; timestamp: number; trades: typeof rawMarkers }>();
    rawMarkers.forEach(m => { const key = `${m.dataIdx}-${m.trade_type}`; const ex = groupMap.get(key); if (ex) ex.trades.push(m); else groupMap.set(key, { dataIdx: m.dataIdx, priceAtTrade: m.priceAtTrade, trade_type: m.trade_type, timestamp: m.timestamp, trades: [m] }); });
    return { chartData: data, groupedMarkers: Array.from(groupMap.values()) };
  }, [stockData, filteredTrades, periodFilter]);

  const allPerf = useMemo(() => {
    const pp = stockData?.prices || [];
    const currentPrice = stockData?.currentPrice ?? (pp.length > 0 ? pp[pp.length - 1].close : null);
    if (!currentPrice) return [];
    const map = new Map<string, { name: string; position: string; buyShares: number; sellShares: number; buyPrices: number[]; buyDates: string[] }>();
    const src = typeFilter === 'all' ? allTrades : allTrades.filter(t => matchesFilter(gradeMap.get(t.insider_name) || 'C', typeFilter));
    src.filter(t => t.trade_date).forEach(t => {
      let price: number | null = null;
      if (pp.length) { const ci = findPriceIdx(pp, t.trade_date!); price = pp[ci].close; }
      const ex = map.get(t.insider_name);
      if (ex) { if (t.trade_type === '매수') { ex.buyShares += t.shares || 0; if (price) { ex.buyPrices.push(price); ex.buyDates.push(t.trade_date!); } } else ex.sellShares += t.shares || 0; }
      else map.set(t.insider_name, { name: t.insider_name, position: t.position || '', buyShares: t.trade_type === '매수' ? (t.shares || 0) : 0, sellShares: t.trade_type === '매도' ? (t.shares || 0) : 0, buyPrices: t.trade_type === '매수' && price ? [price] : [], buyDates: t.trade_type === '매수' && t.trade_date ? [t.trade_date] : [] });
    });
    return Array.from(map.values()).filter(i => i.buyPrices.length > 0).map(i => {
      const avgBuyPrice = i.buyPrices.reduce((a, b) => a + b, 0) / i.buyPrices.length;
      const lastDate = i.buyDates.sort().reverse()[0];
      const totalBuyAmount = i.buyShares * avgBuyPrice;
      const hasPreExisting = i.sellShares > i.buyShares;
      const preExistingSellShares = hasPreExisting ? i.sellShares - i.buyShares : 0;
      const estHoldings = Math.max(i.buyShares - i.sellShares, 0);
      // Compute sell avg price from stockPrices for sell trades
      const sellTrades = (typeFilter === 'all' ? allTrades : allTrades.filter(t => matchesFilter(gradeMap.get(t.insider_name) || 'C', typeFilter)))
        .filter(t => t.insider_name === i.name && t.trade_type === '매도' && t.trade_date);
      let avgSellPrice = 0;
      if (sellTrades.length > 0 && pp.length) {
        const sp = sellTrades.map(t => pp[findPriceIdx(pp, t.trade_date!)].close as number).filter(Boolean);
        if (sp.length) avgSellPrice = sp.reduce((a: number, b: number) => a + b, 0) / sp.length;
      }
      // 기존 보유분 매도 시: 크롤링 기간 내 매수분에 대해서만 수익률 계산
      const matchedSellShares = Math.min(i.sellShares, i.buyShares);
      const realizedProfit = matchedSellShares > 0 ? (avgSellPrice - avgBuyPrice) * matchedSellShares : 0;
      const unrealizedProfit = estHoldings > 0 ? (currentPrice - avgBuyPrice) * estHoldings : 0;
      const totalProfit = hasPreExisting ? realizedProfit : realizedProfit + unrealizedProfit;
      const returnPct = hasPreExisting ? (totalBuyAmount > 0 ? (realizedProfit / totalBuyAmount) * 100 : 0) : (totalBuyAmount > 0 ? (totalProfit / totalBuyAmount) * 100 : 0);
      // Case: 'sold_all' | 'holding' | 'partial' | 'pre_existing'
      const profitCase = hasPreExisting ? 'pre_existing' as const : estHoldings === 0 ? 'sold_all' as const : i.sellShares === 0 ? 'holding' as const : 'partial' as const;
      return { ...i, avgPrice: avgBuyPrice, avgSellPrice, returnPct, lastDate, tradeCount: i.buyPrices.length, totalAmount: totalBuyAmount, estHoldings, realizedProfit, unrealizedProfit, totalProfit, profitCase, hasPreExisting, preExistingSellShares };
    });
  }, [allTrades, stockData, typeFilter, gradeMap]);

  const { topPerf, restPerf } = useMemo(() => {
    const sorted = [...allPerf].sort((a, b) => { switch (perfSort) { case 'profit': return b.totalProfit - a.totalProfit; case 'return': return b.returnPct - a.returnPct; default: return b.totalAmount - a.totalAmount; } });
    if (sorted.length <= 20) return { topPerf: sorted, restPerf: [] as typeof sorted };
    return { topPerf: sorted.slice(0, 20), restPerf: sorted.slice(20) };
  }, [allPerf, perfSort]);

  const formatDate = (d: string | null) => { if (!d) return '-'; const dt = new Date(d); return `${dt.getFullYear()}.${String(dt.getMonth() + 1).padStart(2, '0')}.${String(dt.getDate()).padStart(2, '0')}`; };
  const formatYAxis = (v: number) => { if (v >= 1000000) return `${(v / 10000).toFixed(0)}만`; if (v >= 1000) return v.toLocaleString(); return v.toString(); };
  const formatXTick = (ts: number) => { const d = new Date(ts); switch (periodFilter) { case '1개월': return `${d.getMonth() + 1}/${d.getDate()}`; case '6개월': case '1년': return `${d.getFullYear().toString().slice(2)}.${d.getMonth() + 1}`; default: { const q = Math.floor(d.getMonth() / 3) + 1; return `${d.getFullYear()} Q${q}`; } } };
  const formatAmount = (v: number) => { if (Math.abs(v) >= 1e12) return `${(v / 1e12).toFixed(1)}조`; if (Math.abs(v) >= 1e8) return `${(v / 1e8).toFixed(1)}억`; if (Math.abs(v) >= 1e4) return `${(v / 1e4).toFixed(0)}만`; return v.toLocaleString(); };

  if (!isKoreanStock(code)) return <div className="text-center py-12"><div className="text-4xl mb-4">💼</div><h3 className="text-lg font-bold text-[#191f28] mb-2">내부자 거래</h3><p className="text-[#8b95a1]">Form 4 연동 예정</p></div>;
  if (loading) return <div className="text-center py-12 text-[#8b95a1]">로딩중...</div>;
  if (allTrades.length === 0) return <div className="text-center py-12"><div className="text-4xl mb-4">💼</div><h3 className="text-lg font-bold text-[#191f28] mb-2">내부자 거래</h3><p className="text-[#8b95a1]">수집된 내부자 거래가 없습니다</p></div>;

  const buyCount = trades.filter(t => t.trade_type === '매수').length;
  const sellCount = trades.filter(t => t.trade_type === '매도').length;
  const visibleChips = showAllChips ? [...topChips, ...restChips] : topChips;
  const visiblePerf = showAllCards ? [...topPerf, ...restPerf] : topPerf;

  const renderPerfCard = (p: typeof topPerf[0]) => {
    const g = gradeMap.get(p.name) || 'C'; const gm = GRADE_META[g];
    const pc = p.totalProfit >= 0 ? 'text-green-600' : 'text-red-500';
    return (
      <div key={p.name} className="bg-white rounded-lg border border-[#e8e8e8] p-4 cursor-pointer hover:border-[#3182f6] transition-colors" onClick={() => openModal(p.name)}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="text-sm font-bold text-[#191f28] truncate">{p.name}</span>
            <span className="text-[10px] font-medium px-1.5 py-0.5 rounded-full whitespace-nowrap flex-shrink-0" style={{ color: gm.color, backgroundColor: gm.bg }}>{gm.label}</span>
            {p.position && <span className="text-[10px] text-[#8b95a1] whitespace-nowrap flex-shrink-0">{p.position}</span>}
            {p.profitCase === 'sold_all' && <span className="text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500 whitespace-nowrap flex-shrink-0">매도 완료</span>}
          </div>
          {p.profitCase === 'pre_existing'
            ? <span className="text-xs text-[#8b95a1] flex-shrink-0 ml-2">기존 보유분 매도</span>
            : <span className={`text-lg font-bold flex-shrink-0 ml-2 ${p.returnPct >= 0 ? 'text-green-600' : 'text-red-500'}`}>{p.returnPct >= 0 ? '+' : ''}{p.returnPct.toFixed(1)}%</span>}
        </div>
        <div className="grid grid-cols-4 gap-2 text-xs">
          <div><div className="text-[#8b95a1]">평균 매수가</div><div className="font-medium text-[#191f28]">{formatStockPrice(Math.round(p.avgPrice), code)}</div></div>
          <div><div className="text-[#8b95a1]">{p.profitCase === 'pre_existing' ? '보유 상태' : p.profitCase === 'sold_all' ? '매도수량' : '추정 보유'}</div><div className="font-medium text-[#191f28]">{p.profitCase === 'pre_existing' ? <span className="text-[10px] text-[#8b95a1] leading-tight">공시 기간 외 보유분</span> : p.profitCase === 'sold_all' ? `${p.sellShares.toLocaleString()}주` : `${p.estHoldings.toLocaleString()}주`}</div></div>
          <div><div className="text-[#8b95a1]">매수 총액</div><div className="font-medium text-[#191f28]">{formatAmount(p.totalAmount)}원</div></div>
          <div><div className="text-[#8b95a1]">{p.profitCase === 'pre_existing' ? '매수분 수익' : p.profitCase === 'sold_all' ? '실현 수익' : p.profitCase === 'holding' ? '미실현 수익' : '총 수익'}</div><div className={`font-medium ${pc}`}>{p.totalProfit >= 0 ? '+' : ''}{formatAmount(p.totalProfit)}원</div></div>
        </div>
        <div className="text-xs text-[#8b95a1] mt-2">매수 {p.tradeCount}회 · 최근 {formatDate(p.lastDate)}{p.hasPreExisting ? ` · 기존 보유분 매도 ${p.preExistingSellShares.toLocaleString()}주 (수익률 산정 불가)` : ''}</div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center gap-1.5 text-sm"><span className="font-bold" style={{ color: TRADE_COLORS['매수'] }}>{buyCount}</span><span className="text-[#8b95a1]">매수</span></div>
        <div className="w-px h-3 bg-[#e8e8e8]" />
        <div className="flex items-center gap-1.5 text-sm"><span className="font-bold" style={{ color: TRADE_COLORS['매도'] }}>{sellCount}</span><span className="text-[#8b95a1]">매도</span></div>
        <div className="w-px h-3 bg-[#e8e8e8]" />
        <div className="flex items-center gap-1.5 text-sm"><span className="font-bold text-[#191f28]">{topChips.length + restChips.length}</span><span className="text-[#8b95a1]">명</span></div>
      </div>

      <div className="flex gap-2 mb-3">
        {['1개월', '6개월', '1년', '3년', '전체'].map(p => (
          <button key={p} onClick={() => setPeriodFilter(p)} className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${periodFilter === p ? 'bg-[#191f28] text-white' : 'bg-[#f4f4f4] text-[#8b95a1] hover:bg-[#e8e8e8]'}`}>{p}</button>
        ))}
      </div>

      <div className="flex gap-1.5 mb-4 flex-wrap">
        {FILTER_BUTTONS.map(({ key, label }) => (
          <button key={key} onClick={() => { setTypeFilter(key); setSelectedInsider(null); }} className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-colors ${typeFilter === key ? 'bg-[#191f28] text-white' : 'bg-[#f4f4f4] text-[#8b95a1] hover:bg-[#e8e8e8]'}`}>{label}</button>
        ))}
      </div>

      {chartData.length > 0 && (
        <div className="bg-white rounded-lg border border-[#e8e8e8] p-4 mb-4">
          <div className="flex justify-between items-center mb-3">
            <h4 className="font-medium text-[#191f28] text-sm">주가 차트 & 내부자 매매</h4>
            {stockData?.currentPrice && <span className="text-xs text-[#8b95a1]">현재가 <span className="font-bold text-[#191f28]">{formatStockPrice(stockData.currentPrice, code)}</span></span>}
          </div>
          <div className="h-64 bg-[#f8f9fa] rounded-lg">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} style={{ cursor: 'crosshair' }}>
                <defs><linearGradient id="insiderPriceGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3182f6" stopOpacity={0.15} /><stop offset="100%" stopColor="#3182f6" stopOpacity={0.02} /></linearGradient></defs>
                <XAxis dataKey="timestamp" type="number" scale="time" domain={['dataMin', 'dataMax']} tickFormatter={formatXTick} tick={{ fontSize: 10, fill: '#8b95a1' }} tickLine={false} axisLine={{ stroke: '#e8e8e8' }} minTickGap={50} />
                <YAxis tickFormatter={formatYAxis} tick={{ fontSize: 10, fill: '#8b95a1' }} tickLine={false} axisLine={false} domain={['auto', 'auto']} width={55} />
                <Area type="monotone" dataKey="close" stroke="none" fill="url(#insiderPriceGrad)" isAnimationActive={false} />
                <Line type="monotone" dataKey="close" stroke="#3182f6" strokeWidth={2} dot={false} isAnimationActive={false} />
                {groupedMarkers.map((mg, i) => {
                  const hasSel = !!selectedInsider; const isHi = hasSel && mg.trades.some(t => t.insider_name === selectedInsider);
                  const bestG = mg.trades.reduce((best, t) => { const tg = gradeMap.get(t.insider_name) || 'C'; return GRADE_META[tg].dotSize > GRADE_META[best].dotSize ? tg : best; }, 'C' as InsiderGrade);
                  return <ReferenceDot key={`g-${i}`} x={mg.timestamp} y={mg.priceAtTrade} r={isHi ? GRADE_META[bestG].dotSize + 3 : GRADE_META[bestG].dotSize} fill={TRADE_COLORS[mg.trade_type] || '#8b95a1'} stroke={isHi ? '#191f28' : 'white'} strokeWidth={isHi ? 2.5 : 1.5} fillOpacity={hasSel && !isHi ? 0.2 : 1} style={{ cursor: 'pointer' }} />;
                })}
                <Tooltip content={({ active, payload }) => {
                  if (!active || !payload?.length) return null; const d = payload[0].payload;
                  const matching = groupedMarkers.filter(g => g.timestamp === d.timestamp);
                  return (<div className="bg-white border border-[#e8e8e8] rounded-lg shadow-lg p-3 text-xs max-w-[250px]">
                    <div className="text-[#8b95a1] mb-1">{new Date(d.date).toLocaleDateString('ko-KR')}</div>
                    <div className="font-bold text-[#191f28] mb-1">{formatStockPrice(d.close, code)}</div>
                    {matching.map((g, gi) => (<div key={gi} className="pt-1 border-t border-[#e8e8e8]"><span className="font-bold" style={{ color: TRADE_COLORS[g.trade_type] }}>{g.trade_type === '매수' ? '▲' : '▼'} {g.trades.length > 1 ? `${g.trades.length}명 ` : ''}{g.trade_type}</span>{g.trades.slice(0, 3).map((t, ti) => <div key={ti} className="text-[#4e5968]">{t.insider_name} {t.shares?.toLocaleString()}주</div>)}{g.trades.length > 3 && <div className="text-[#8b95a1]">+{g.trades.length - 3}명</div>}</div>))}
                  </div>);
                }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-3">
            {(['매수', '매도'] as const).map(type => (
              <button key={type} onClick={() => setFilter(filter === type ? 'all' : type)} className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all ${filter === 'all' || filter === type ? 'opacity-100' : 'opacity-30'}`} style={{ backgroundColor: (filter === 'all' || filter === type ? TRADE_COLORS[type] + '20' : '#f0f0f0'), color: (filter === 'all' || filter === type ? TRADE_COLORS[type] : '#8b95a1') }}>{type === '매수' ? '▲' : '▼'} {type} {type === '매수' ? buyCount : sellCount}건</button>
            ))}
          </div>
        </div>
      )}

      {(topChips.length + restChips.length) > 1 && (
        <div className="mb-4"><div className="flex flex-wrap gap-2">
          <button onClick={() => setSelectedInsider(null)} className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${!selectedInsider ? 'bg-[#191f28] text-white' : 'bg-[#f4f4f4] text-[#8b95a1] hover:bg-[#e8e8e8]'}`}>전체</button>
          {visibleChips.map(o => { const g = gradeMap.get(o.name) || 'C'; const gm = GRADE_META[g]; return (
            <button key={o.name} onClick={() => setSelectedInsider(selectedInsider === o.name ? null : o.name)} className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors flex items-center gap-1 ${selectedInsider === o.name ? 'bg-[#191f28] text-white' : 'bg-[#f4f4f4] text-[#8b95a1] hover:bg-[#e8e8e8]'}`}>
              <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: gm.color }} />{o.name} ({o.count})
            </button>); })}
          {restChips.length > 0 && <button onClick={() => setShowAllChips(!showAllChips)} className="px-3 py-1.5 rounded-full text-xs font-medium text-[#3182f6] bg-blue-50 hover:bg-blue-100 transition-colors">{showAllChips ? '접기' : `기타 ${restChips.length}명 더보기`}</button>}
        </div></div>
      )}

      {(topPerf.length + restPerf.length) > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-bold text-[#191f28]">내부자 매수 수익률</h4>
            <div className="flex gap-1">{([['amount', '매수총액'], ['profit', '수익금'], ['return', '수익률']] as const).map(([key, label]) => (
              <button key={key} onClick={() => setPerfSort(key)} className={`px-2 py-1 rounded text-[10px] font-medium transition-colors ${perfSort === key ? 'bg-[#191f28] text-white' : 'bg-[#f4f4f4] text-[#8b95a1]'}`}>{label}순</button>
            ))}</div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">{visiblePerf.map(renderPerfCard)}</div>
          {restPerf.length > 0 && <button onClick={() => setShowAllCards(!showAllCards)} className="mt-3 w-full py-2 rounded-lg text-xs font-medium text-[#3182f6] bg-blue-50 hover:bg-blue-100 transition-colors">{showAllCards ? '접기' : `나머지 ${restPerf.length}명 더보기`}</button>}
        </div>
      )}

      <h4 className="text-sm font-bold text-[#191f28] mb-3">거래 내역 ({filteredTrades.length}건)</h4>
      <div className="space-y-2">
        {filteredTrades.slice(0, visibleCount).map((t) => { const badge = getPositionBadge(t.position || ''); return (
          <div key={t.id} className="bg-white rounded-lg border border-[#e8e8e8] px-4 py-3">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${t.trade_type === '매수' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>{t.trade_type === '매수' ? '▲' : '▼'} {t.trade_type}</span>
                <button onClick={() => setSelectedInsider(selectedInsider === t.insider_name ? null : t.insider_name)} className="text-sm font-bold text-[#191f28] hover:text-[#3182f6] transition-colors">{t.insider_name}</button>
                {t.position && badge && <span className="text-[10px] font-medium px-1.5 py-0.5 rounded-full" style={{ color: badge.color, backgroundColor: badge.bg }}>{t.position}</span>}
              </div>
              <span className="text-xs text-[#8b95a1]">{formatDate(t.trade_date)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#4e5968]">{t.shares?.toLocaleString()}주</span>
              {t.source_url && <a href={t.source_url} target="_blank" rel="noopener noreferrer" className="text-xs text-[#3182f6] hover:underline">DART 공시 ↗</a>}
            </div>
          </div>); })}
        {filteredTrades.length === 0 && <div className="text-center py-8 text-[#8b95a1] text-sm">해당 조건의 거래가 없습니다</div>}
        {visibleCount < filteredTrades.length && <button onClick={() => setVisibleCount(prev => prev + 30)} className="w-full py-3 rounded-lg text-sm font-medium text-[#3182f6] bg-blue-50 hover:bg-blue-100 transition-colors">더 불러오기 ({filteredTrades.length - visibleCount}건 남음)</button>}
      </div>

      {modalInsider && (() => {
        const it = trades.filter(t => t.insider_name === modalInsider);
        const buys = it.filter(t => t.trade_type === '매수'); const sells = it.filter(t => t.trade_type === '매도');
        const totalBuyShares = buys.reduce((s, t) => s + (t.shares || 0), 0); const totalSellShares = sells.reduce((s, t) => s + (t.shares || 0), 0);
        const mHasPreExisting = totalSellShares > totalBuyShares;
        const mPreExistingSellShares = mHasPreExisting ? totalSellShares - totalBuyShares : 0;
        const estHoldings = Math.max(totalBuyShares - totalSellShares, 0); const cp = stockData?.currentPrice || 0;
        let avgBP = 0; let avgSP = 0;
        if (stockData?.prices?.length) {
          const sp = stockData.prices;
          if (buys.length > 0) { const bp = buys.filter(t => t.trade_date).map(t => sp[findPriceIdx(sp, t.trade_date!)].close as number).filter(Boolean); if (bp.length) avgBP = bp.reduce((a: number, b: number) => a + b, 0) / bp.length; }
          if (sells.length > 0) { const slp = sells.filter(t => t.trade_date).map(t => sp[findPriceIdx(sp, t.trade_date!)].close as number).filter(Boolean); if (slp.length) avgSP = slp.reduce((a: number, b: number) => a + b, 0) / slp.length; }
        }
        const matchedSells = Math.min(totalSellShares, totalBuyShares);
        const realized = matchedSells > 0 ? (avgSP - avgBP) * matchedSells : 0;
        const unrealized = estHoldings > 0 ? (cp - avgBP) * estHoldings : 0;
        const mCase = mHasPreExisting ? 'pre_existing' : estHoldings === 0 ? 'sold_all' : totalSellShares === 0 ? 'holding' : 'partial';
        const pos = it[0]?.position || ''; const g = gradeMap.get(modalInsider) || 'C'; const gm = GRADE_META[g];
        const otherStocks = otherTrades.filter(t => t.ticker !== code).reduce((acc, t) => { if (!acc.has(t.ticker)) acc.set(t.ticker, { ticker: t.ticker, stockName: t.stock_name || t.ticker, count: 0 }); acc.get(t.ticker)!.count++; return acc; }, new Map<string, { ticker: string; stockName: string; count: number }>());
        return (
          <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center" onClick={closeModal}><div className="absolute inset-0 bg-black/40" />
            <div className="relative bg-white w-full sm:max-w-lg sm:rounded-2xl rounded-t-2xl max-h-[85vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
              <div className="sticky top-0 bg-white border-b border-[#e8e8e8] px-5 py-4 flex items-center justify-between z-10">
                <div className="flex items-center gap-2"><span className="text-lg font-bold text-[#191f28]">{modalInsider}</span><span className="text-xs font-medium px-2 py-0.5 rounded-full" style={{ color: gm.color, backgroundColor: gm.bg }}>{gm.label}</span>{pos && <span className="text-xs text-[#8b95a1]">{pos}</span>}</div>
                <button onClick={closeModal} className="text-[#8b95a1] hover:text-[#191f28] text-xl">&times;</button>
              </div>
              <div className="px-5 py-4 space-y-5">
                {stockData?.prices?.length > 0 && (() => {
                  const pp = stockData.prices;
                  const modalChartData = pp.map((p: any) => ({ date: p.date, timestamp: new Date(p.date).getTime(), close: p.close }));
                  const personalTrades = it.filter(t => t.trade_date).map(t => {
                    const ci = findPriceIdx(pp, t.trade_date!);
                    return { trade_type: t.trade_type, shares: t.shares, trade_date: t.trade_date, timestamp: new Date(pp[ci].date).getTime(), price: pp[ci].close };
                  });
                  return (
                    <div className="bg-[#f8f9fa] rounded-lg p-3">
                      <div className="h-[200px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <ComposedChart data={modalChartData}>
                            <defs><linearGradient id="modalPriceGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3182f6" stopOpacity={0.1} /><stop offset="100%" stopColor="#3182f6" stopOpacity={0.01} /></linearGradient></defs>
                            <XAxis dataKey="timestamp" type="number" scale="time" domain={['dataMin', 'dataMax']} tickFormatter={(ts: number) => { const d = new Date(ts); return `${d.getFullYear().toString().slice(2)}.${d.getMonth() + 1}`; }} tick={{ fontSize: 9, fill: '#8b95a1' }} tickLine={false} axisLine={{ stroke: '#e8e8e8' }} minTickGap={40} />
                            <YAxis tickFormatter={(v: number) => v >= 1000000 ? `${(v / 10000).toFixed(0)}만` : v >= 1000 ? v.toLocaleString() : v.toString()} tick={{ fontSize: 9, fill: '#8b95a1' }} tickLine={false} axisLine={false} domain={['auto', 'auto']} width={50} />
                            <Area type="monotone" dataKey="close" stroke="none" fill="url(#modalPriceGrad)" isAnimationActive={false} />
                            <Line type="monotone" dataKey="close" stroke="#3182f6" strokeWidth={1.5} dot={false} isAnimationActive={false} />
                            {personalTrades.map((pt, pi) => (
                              <ReferenceDot key={`modal-dot-${pi}`} x={pt.timestamp} y={pt.price} r={5} fill={pt.trade_type === '매수' ? '#22c55e' : '#ef4444'} stroke="white" strokeWidth={1.5} />
                            ))}
                            <Tooltip content={({ active, payload }) => {
                              if (!active || !payload?.length) return null;
                              const d = payload[0].payload;
                              const hits = personalTrades.filter(pt => pt.timestamp === d.timestamp);
                              return (<div className="bg-white border border-[#e8e8e8] rounded-lg shadow-lg p-2 text-xs">
                                <div className="text-[#8b95a1] mb-0.5">{new Date(d.date).toLocaleDateString('ko-KR')}</div>
                                <div className="font-bold text-[#191f28] mb-0.5">{formatStockPrice(d.close, code)}</div>
                                {hits.map((h, hi) => <div key={hi} className="font-medium" style={{ color: h.trade_type === '매수' ? '#22c55e' : '#ef4444' }}>{h.trade_type === '매수' ? '▲' : '▼'} {h.trade_type} {h.shares?.toLocaleString()}주</div>)}
                              </div>);
                            }} />
                          </ComposedChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  );
                })()}
                <div className="bg-[#f8f9fa] rounded-lg p-3 mb-2">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-xs text-[#8b95a1]">추정 보유량</div>
                    {mHasPreExisting
                      ? <div className="text-sm text-[#191f28]"><span className="font-normal text-[#8b95a1]">(매수 {totalBuyShares.toLocaleString()} &lt; 매도 {totalSellShares.toLocaleString()})</span></div>
                      : <div className="text-sm font-bold text-[#191f28]">{estHoldings.toLocaleString()}주 <span className="font-normal text-[#8b95a1]">(매수 {totalBuyShares.toLocaleString()} - 매도 {totalSellShares.toLocaleString()})</span></div>}
                  </div>
                  {mHasPreExisting && <div className="text-xs text-amber-600 bg-amber-50 rounded px-2 py-1.5 mb-2">데이터 범위 이전 보유분 있음 (DART 공시 기간 외) · 기존 보유분 매도 {mPreExistingSellShares.toLocaleString()}주</div>}
                  {avgBP > 0 && <div className="text-xs text-[#8b95a1] mb-2">평균 매수가 {formatStockPrice(Math.round(avgBP), code)}{avgSP > 0 ? ` · 평균 매도가 ${formatStockPrice(Math.round(avgSP), code)}` : ''} · 현재가 {formatStockPrice(cp, code)}</div>}
                </div>
                <div className={`grid ${mCase === 'partial' ? 'grid-cols-2' : 'grid-cols-1'} gap-3`}>
                  {mCase === 'pre_existing' && (
                    <div className="bg-[#f8f9fa] rounded-lg p-3">
                      <div className="text-xs text-[#8b95a1] mb-1">크롤링 기간 내 매수분 수익</div>
                      <div className={`text-lg font-bold ${realized >= 0 ? 'text-green-600' : 'text-red-500'}`}>{realized >= 0 ? '+' : ''}{formatAmount(realized)}원</div>
                      <div className="text-xs text-[#8b95a1]">매수분 매도 {matchedSells.toLocaleString()}주</div>
                      <div className="text-xs text-amber-600 mt-1.5">기존 보유분 매도 {mPreExistingSellShares.toLocaleString()}주 — 수익률 산정 불가</div>
                    </div>
                  )}
                  {(mCase === 'sold_all' || mCase === 'partial') && (
                    <div className="bg-[#f8f9fa] rounded-lg p-3"><div className="text-xs text-[#8b95a1] mb-1">실현 수익</div><div className={`text-lg font-bold ${realized >= 0 ? 'text-green-600' : 'text-red-500'}`}>{realized >= 0 ? '+' : ''}{formatAmount(realized)}원</div><div className="text-xs text-[#8b95a1]">매도 {matchedSells.toLocaleString()}주</div></div>
                  )}
                  {(mCase === 'holding' || mCase === 'partial') && (
                    <div className="bg-[#f8f9fa] rounded-lg p-3"><div className="text-xs text-[#8b95a1] mb-1">미실현 수익</div><div className={`text-lg font-bold ${unrealized >= 0 ? 'text-green-600' : 'text-red-500'}`}>{unrealized >= 0 ? '+' : ''}{formatAmount(unrealized)}원</div><div className="text-xs text-[#8b95a1]">보유 {estHoldings.toLocaleString()}주</div></div>
                  )}
                </div>
                <div><h4 className="text-sm font-bold text-[#191f28] mb-3">매매 이력 ({it.length}건)</h4><div className="space-y-1.5 max-h-60 overflow-y-auto">{it.map((t, i) => (
                  <div key={i} className="flex items-center justify-between text-xs py-1.5 border-b border-[#f4f4f4] last:border-0">
                    <div className="flex items-center gap-2"><span className={`font-bold px-1.5 py-0.5 rounded ${t.trade_type === '매수' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>{t.trade_type}</span><span className="text-[#8b95a1]">{formatDate(t.trade_date)}</span></div>
                    <div className="flex items-center gap-3"><span className="text-[#191f28] font-medium">{t.shares?.toLocaleString()}주</span>{t.price && <span className="text-[#8b95a1]">@{t.price.toLocaleString()}원</span>}{t.source_url && <a href={t.source_url} target="_blank" rel="noopener noreferrer" className="text-[#3182f6]">↗</a>}</div>
                  </div>))}</div></div>
                {(otherLoading || otherStocks.size > 0) && <div><h4 className="text-sm font-bold text-[#191f28] mb-3">이 사람의 다른 종목</h4>
                  {otherLoading ? <div className="text-xs text-[#8b95a1] py-4 text-center">로딩중...</div>
                    : <div className="space-y-1.5">{Array.from(otherStocks.values()).sort((a, b) => b.count - a.count).map(s => (
                      <a key={s.ticker} href={`/invest-sns/stock/${s.ticker}`} className="flex items-center justify-between text-xs py-2 px-3 bg-[#f8f9fa] rounded-lg hover:bg-[#e8e8e8] transition-colors"><div><span className="font-medium text-[#191f28]">{s.stockName || formatStockDisplay(s.ticker).name}</span> <span className="text-[#8b95a1]">{s.ticker}</span></div><span className="text-[#8b95a1]">{s.count}건</span></a>))}</div>}
                </div>}
              </div>
            </div>
          </div>);
      })()}
    </div>
  );
}
