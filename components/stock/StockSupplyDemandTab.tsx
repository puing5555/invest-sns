'use client';

import { useState, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { getSupplyDemand, type SupplyDemand } from '@/lib/supabase';
import { isKoreanStock, formatStockPrice } from '@/lib/currency';
import stockPricesData from '@/data/stockPrices.json';

const ComposedChart = dynamic(() => import('recharts').then(m => m.ComposedChart), { ssr: false });
const Bar = dynamic(() => import('recharts').then(m => m.Bar), { ssr: false });
const Line = dynamic(() => import('recharts').then(m => m.Line), { ssr: false });
const Area = dynamic(() => import('recharts').then(m => m.Area), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(m => m.YAxis), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(m => m.Tooltip), { ssr: false });
const ResponsiveContainer = dynamic(() => import('recharts').then(m => m.ResponsiveContainer), { ssr: false });

const PERIOD_OPTIONS = ['1개월', '3개월', '6개월', '1년'] as const;
const B = 1e8; // 억

function fmtEok(v: number): string {
  const eok = v / B;
  if (Math.abs(eok) >= 1000) return `${(eok / 10000).toFixed(1)}조`;
  if (Math.abs(eok) >= 1) return `${eok >= 0 ? '+' : ''}${eok.toFixed(0)}억`;
  return `${v >= 0 ? '+' : ''}${(v / 1e4).toFixed(0)}만`;
}

function fmtAxisEok(v: number): string {
  const eok = v / B;
  if (Math.abs(eok) >= 1000) return `${(eok / 10000).toFixed(0)}조`;
  return `${eok.toFixed(0)}억`;
}

export default function StockSupplyDemandTab({ code }: { code: string }) {
  const [data, setData] = useState<SupplyDemand[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState<typeof PERIOD_OPTIONS[number]>('3개월');

  useEffect(() => {
    setLoading(true);
    const cutoff = new Date();
    switch (period) {
      case '1개월': cutoff.setMonth(cutoff.getMonth() - 1); break;
      case '3개월': cutoff.setMonth(cutoff.getMonth() - 3); break;
      case '6개월': cutoff.setMonth(cutoff.getMonth() - 6); break;
      case '1년': cutoff.setFullYear(cutoff.getFullYear() - 1); break;
    }
    getSupplyDemand(code, cutoff.toISOString().slice(0, 10)).then(d => {
      setData(d);
      setLoading(false);
    });
  }, [code, period]);

  const stockData = (stockPricesData as any)[code];

  const chartData = useMemo(() => {
    if (!data.length) return [];
    const priceMap = new Map<string, number>();
    if (stockData?.prices) {
      stockData.prices.forEach((p: any) => priceMap.set(p.date, p.close));
    }
    return data.map(d => ({
      date: d.trade_date,
      timestamp: new Date(d.trade_date).getTime(),
      institution: d.institution,
      foreign_investor: d.foreign_investor,
      individual: d.individual,
      close: priceMap.get(d.trade_date) || null,
    }));
  }, [data, stockData]);

  const cumulativeData = useMemo(() => {
    if (!chartData.length) return [];
    let cumInst = 0, cumForeign = 0, cumIndiv = 0;
    return chartData.map(d => {
      cumInst += d.institution;
      cumForeign += d.foreign_investor;
      cumIndiv += d.individual;
      return { date: d.date, timestamp: d.timestamp, institution: cumInst, foreign_investor: cumForeign, individual: cumIndiv };
    });
  }, [chartData]);

  const summary = useMemo(() => ({
    institution: data.reduce((s, d) => s + d.institution, 0),
    foreign_investor: data.reduce((s, d) => s + d.foreign_investor, 0),
    individual: data.reduce((s, d) => s + d.individual, 0),
  }), [data]);

  if (!isKoreanStock(code)) {
    return <div className="text-center py-12"><div className="text-4xl mb-4">📊</div><h3 className="text-lg font-bold text-[#191f28] mb-2">수급 분석</h3><p className="text-[#8b95a1]">한국 주식만 지원됩니다</p></div>;
  }
  if (loading) {
    return <div className="text-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#3182f6] mx-auto mb-4" /><p className="text-[#8b95a1] text-sm">수급 데이터 로딩중...</p></div>;
  }
  if (!data.length) {
    return <div className="text-center py-12"><div className="text-4xl mb-4">📊</div><h3 className="text-lg font-bold text-[#191f28] mb-2">수급 데이터</h3><p className="text-[#8b95a1]">아직 수급 데이터가 없습니다</p></div>;
  }

  const formatXTick = (ts: number) => {
    const d = new Date(ts);
    if (period === '1개월') return `${d.getMonth() + 1}/${d.getDate()}`;
    return `${d.getFullYear().toString().slice(2)}.${d.getMonth() + 1}`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-[#191f28]">투자자별 수급</h3>
        <div className="flex gap-1">
          {PERIOD_OPTIONS.map(p => (
            <button key={p} onClick={() => setPeriod(p)} className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-colors ${period === p ? 'bg-[#191f28] text-white' : 'bg-[#f4f4f4] text-[#8b95a1] hover:bg-[#e8e8e8]'}`}>{p}</button>
          ))}
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-2">
        {[
          { label: '기관', value: summary.institution, color: '#2563eb' },
          { label: '외국인', value: summary.foreign_investor, color: '#dc2626' },
          { label: '개인', value: summary.individual, color: '#16a34a' },
        ].map(({ label, value }) => (
          <div key={label} className="bg-[#f8f9fa] rounded-lg p-3 text-center">
            <div className="text-[10px] text-[#8b95a1] mb-1">{label} 누적</div>
            <div className="text-sm font-bold" style={{ color: value >= 0 ? '#16a34a' : '#dc2626' }}>
              {fmtEok(value)}원
            </div>
          </div>
        ))}
      </div>

      {/* Main chart: price line + institution/foreign bars (grouped) */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-medium text-[#8b95a1]">주가 + 투자자별 순매수</h4>
          <div className="flex items-center gap-3 text-[10px] text-[#8b95a1]">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-[#2563eb] inline-block" />기관</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-[#dc2626] inline-block" />외국인</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-[#16a34a] inline-block" />개인</span>
            <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-[#3182f6] inline-block" />주가</span>
          </div>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} barGap={0} barCategoryGap="20%">
              <defs>
                <linearGradient id="supplyPriceGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3182f6" stopOpacity={0.08} />
                  <stop offset="100%" stopColor="#3182f6" stopOpacity={0.01} />
                </linearGradient>
              </defs>
              <XAxis dataKey="timestamp" type="number" scale="time" domain={['dataMin', 'dataMax']} tickFormatter={formatXTick} tick={{ fontSize: 9, fill: '#8b95a1' }} tickLine={false} axisLine={{ stroke: '#e8e8e8' }} minTickGap={40} />
              <YAxis yAxisId="volume" orientation="left" tickFormatter={fmtAxisEok} tick={{ fontSize: 9, fill: '#8b95a1' }} tickLine={false} axisLine={false} width={45} />
              <YAxis yAxisId="price" orientation="right" tickFormatter={(v: number) => v >= 1e6 ? `${(v / 1e4).toFixed(0)}만` : v.toLocaleString()} tick={{ fontSize: 9, fill: '#8b95a1' }} tickLine={false} axisLine={false} width={50} />
              <Tooltip content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const d = payload[0]?.payload;
                if (!d) return null;
                return (
                  <div className="bg-white border border-[#e8e8e8] rounded-lg shadow-lg p-3 text-xs">
                    <div className="text-[#8b95a1] mb-1">{new Date(d.date).toLocaleDateString('ko-KR')}</div>
                    {d.close && <div className="font-bold text-[#191f28] mb-1">{formatStockPrice(d.close, code)}</div>}
                    <div className="space-y-0.5">
                      <div className="flex justify-between gap-4"><span style={{ color: '#2563eb' }}>기관</span><span className="font-medium" style={{ color: d.institution >= 0 ? '#16a34a' : '#dc2626' }}>{fmtEok(d.institution)}원</span></div>
                      <div className="flex justify-between gap-4"><span style={{ color: '#dc2626' }}>외국인</span><span className="font-medium" style={{ color: d.foreign_investor >= 0 ? '#16a34a' : '#dc2626' }}>{fmtEok(d.foreign_investor)}원</span></div>
                      <div className="flex justify-between gap-4"><span style={{ color: '#16a34a' }}>개인</span><span className="font-medium" style={{ color: d.individual >= 0 ? '#16a34a' : '#dc2626' }}>{fmtEok(d.individual)}원</span></div>
                    </div>
                  </div>
                );
              }} />
              <Area yAxisId="price" type="monotone" dataKey="close" stroke="none" fill="url(#supplyPriceGrad)" isAnimationActive={false} />
              <Bar yAxisId="volume" dataKey="institution" fill="#2563eb" fillOpacity={0.75} isAnimationActive={false} />
              <Bar yAxisId="volume" dataKey="foreign_investor" fill="#dc2626" fillOpacity={0.75} isAnimationActive={false} />
              <Bar yAxisId="volume" dataKey="individual" fill="#16a34a" fillOpacity={0.75} isAnimationActive={false} />
              <Line yAxisId="price" type="monotone" dataKey="close" stroke="#3182f6" strokeWidth={1.5} dot={false} isAnimationActive={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cumulative chart */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-medium text-[#8b95a1]">누적 순매수 추이 (억원)</h4>
          <div className="flex items-center gap-3 text-[10px] text-[#8b95a1]">
            <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-[#2563eb] inline-block" />기관</span>
            <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-[#dc2626] inline-block" />외국인</span>
            <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-[#16a34a] inline-block" />개인</span>
          </div>
        </div>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={cumulativeData}>
              <XAxis dataKey="timestamp" type="number" scale="time" domain={['dataMin', 'dataMax']} tickFormatter={formatXTick} tick={{ fontSize: 9, fill: '#8b95a1' }} tickLine={false} axisLine={{ stroke: '#e8e8e8' }} minTickGap={40} />
              <YAxis tickFormatter={fmtAxisEok} tick={{ fontSize: 9, fill: '#8b95a1' }} tickLine={false} axisLine={false} width={50} />
              <Tooltip content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const d = payload[0]?.payload;
                if (!d) return null;
                return (
                  <div className="bg-white border border-[#e8e8e8] rounded-lg shadow-lg p-3 text-xs">
                    <div className="text-[#8b95a1] mb-1">{new Date(d.date).toLocaleDateString('ko-KR')}</div>
                    <div className="space-y-0.5">
                      <div className="flex justify-between gap-4"><span style={{ color: '#2563eb' }}>기관</span><span className="font-medium">{fmtEok(d.institution)}원</span></div>
                      <div className="flex justify-between gap-4"><span style={{ color: '#dc2626' }}>외국인</span><span className="font-medium">{fmtEok(d.foreign_investor)}원</span></div>
                      <div className="flex justify-between gap-4"><span style={{ color: '#16a34a' }}>개인</span><span className="font-medium">{fmtEok(d.individual)}원</span></div>
                    </div>
                  </div>
                );
              }} />
              <Line type="monotone" dataKey="institution" stroke="#2563eb" strokeWidth={2} dot={false} isAnimationActive={false} />
              <Line type="monotone" dataKey="foreign_investor" stroke="#dc2626" strokeWidth={2} dot={false} isAnimationActive={false} />
              <Line type="monotone" dataKey="individual" stroke="#16a34a" strokeWidth={2} dot={false} isAnimationActive={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
