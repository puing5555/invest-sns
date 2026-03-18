'use client';

import { useState, useMemo, useCallback, useRef } from 'react';
import {
  ComposedChart, Area, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, ReferenceDot, ReferenceArea,
} from 'recharts';
import stockPricesData from '@/data/stockPrices.json';
import { formatStockPrice } from '@/lib/currency';

interface Signal {
  date: string;
  influencer: string;
  signal: string;
  quote: string;
  videoUrl: string;
}

interface StockSignalChartProps {
  code: string;
  signals: Signal[];
  periodFilter?: string;
  onSignalClick?: (signal: Signal) => void;
  activeSignalTypes?: string[];
  onSignalTypeToggle?: (type: string) => void;
}

const ALL_SIGNAL_TYPES = ['매수', '긍정', '중립', '부정', '매도'];

const SIGNAL_COLORS: Record<string, string> = {
  '매수': '#22c55e', '긍정': '#3182f6', '중립': '#eab308',
  '부정': '#f97316', '매도': '#ef4444',
};
const SIGNAL_EMOJI: Record<string, string> = {
  '매수': '🟢', '긍정': '🔵', '중립': '🟡', '부정': '🟠', '매도': '🔴',
};

export default function StockSignalChart({
  code, signals, periodFilter, onSignalClick, activeSignalTypes, onSignalTypeToggle,
}: StockSignalChartProps) {
  const activeTypes = activeSignalTypes || ALL_SIGNAL_TYPES;
  const stockData = (stockPricesData as any)[code];

  // Drag state — index into chartData array
  const [dragStartIdx, setDragStartIdx] = useState<number | null>(null);
  const [dragEndIdx, setDragEndIdx] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Build chart data
  const { chartData, signalMarkers } = useMemo(() => {
    if (!stockData?.prices?.length) return { chartData: [], signalMarkers: [] };

    let prices = stockData.prices;
    if (periodFilter && periodFilter !== '전체') {
      const cutoff = new Date();
      switch (periodFilter) {
        case '1개월': cutoff.setMonth(cutoff.getMonth() - 1); break;
        case '6개월': cutoff.setMonth(cutoff.getMonth() - 6); break;
        case '1년': cutoff.setFullYear(cutoff.getFullYear() - 1); break;
        case '3년': cutoff.setFullYear(cutoff.getFullYear() - 3); break;
      }
      const filtered = prices.filter((p: any) => new Date(p.date) >= cutoff);
      if (filtered.length >= 2) prices = filtered;
    }

    const data = prices.map((p: any, i: number) => ({
      idx: i,
      date: p.date,
      close: p.close,
    }));

    // Map signals to nearest price index
    const filteredSigs = signals.filter(s => activeTypes.includes(s.signal));
    const markers = filteredSigs.map(sig => {
      let closestIdx = 0;
      let closestDiff = Infinity;
      prices.forEach((p: any, i: number) => {
        const diff = Math.abs(new Date(p.date).getTime() - new Date(sig.date).getTime());
        if (diff < closestDiff) { closestDiff = diff; closestIdx = i; }
      });
      return { ...sig, dataIdx: closestIdx, priceAtSignal: prices[closestIdx].close };
    });

    return { chartData: data, signalMarkers: markers };
  }, [stockData, signals, activeTypes, periodFilter]);

  // Drag selection computed values
  const dragSelection = useMemo(() => {
    if (dragStartIdx === null || dragEndIdx === null || dragStartIdx === dragEndIdx) return null;
    if (!chartData.length) return null;
    const sIdx = Math.min(dragStartIdx, dragEndIdx);
    const eIdx = Math.max(dragStartIdx, dragEndIdx);
    const startPrice = chartData[sIdx].close;
    const endPrice = chartData[eIdx].close;
    const diff = endPrice - startPrice;
    const pct = (diff / startPrice) * 100;
    return {
      sIdx, eIdx,
      startDate: chartData[sIdx].date, endDate: chartData[eIdx].date,
      startPrice, endPrice, diff, pct,
    };
  }, [dragStartIdx, dragEndIdx, chartData]);

  // Recharts mouse handlers — e.activeTooltipIndex gives exact data index
  const handleMouseDown = useCallback((e: any) => {
    if (!e || e.activeTooltipIndex == null) return;
    setIsDragging(true);
    setDragStartIdx(e.activeTooltipIndex);
    setDragEndIdx(e.activeTooltipIndex);
  }, []);

  const handleMouseMove = useCallback((e: any) => {
    if (!isDragging || !e || e.activeTooltipIndex == null) return;
    setDragEndIdx(e.activeTooltipIndex);
  }, [isDragging]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const clearSelection = useCallback(() => {
    setDragStartIdx(null);
    setDragEndIdx(null);
    setIsDragging(false);
  }, []);

  // Format helpers
  const formatYAxis = (v: number) => {
    if (v >= 1000000) return `${(v / 10000).toFixed(0)}만`;
    if (v >= 1000) return v.toLocaleString();
    return v.toString();
  };

  const formatXTick = (date: string) => {
    const d = new Date(date);
    const period = periodFilter || '전체';
    switch (period) {
      case '1개월': return `${d.getMonth() + 1}/${d.getDate()}`;
      case '6개월': case '1년': return `${d.getFullYear().toString().slice(2)}.${d.getMonth() + 1}`;
      default: {
        // 3년, 전체 모두 분기별 표시
        const q = Math.floor(d.getMonth() / 3) + 1;
        return `${d.getFullYear()} Q${q}`;
      }
    }
  };

  if (!chartData.length) {
    return (
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <h4 className="font-medium text-[#191f28] mb-4">주가 차트 & 신호</h4>
        <div className="h-64 bg-[#f8f9fa] rounded-lg flex items-center justify-center text-[#8b95a1]">
          주가 데이터를 불러올 수 없습니다
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
      <div className="flex justify-between items-center mb-4">
        <h4 className="font-medium text-[#191f28]">주가 차트 & 신호</h4>
        <div className="text-sm text-[#8b95a1]">
          현재가 <span className="font-bold text-[#191f28]">{formatStockPrice(stockData.currentPrice, code)}</span>
        </div>
      </div>

      <div className="relative h-72 bg-[#f8f9fa] rounded-lg select-none">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{ cursor: isDragging ? 'col-resize' : 'crosshair' }}
          >
            <defs>
              <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3182f6" stopOpacity={0.15} />
                <stop offset="100%" stopColor="#3182f6" stopOpacity={0.02} />
              </linearGradient>
            </defs>

            <XAxis
              dataKey="date"
              tickFormatter={formatXTick}
              tick={{ fontSize: 10, fill: '#8b95a1' }}
              tickLine={false}
              axisLine={{ stroke: '#e8e8e8' }}
              interval="preserveStartEnd"
              minTickGap={50}
            />
            <YAxis
              tickFormatter={formatYAxis}
              tick={{ fontSize: 10, fill: '#8b95a1' }}
              tickLine={false}
              axisLine={false}
              domain={['auto', 'auto']}
              width={55}
            />

            {/* Drag highlight area */}
            {dragSelection && (
              <ReferenceArea
                x1={chartData[dragSelection.sIdx].date}
                x2={chartData[dragSelection.eIdx].date}
                fill={dragSelection.pct >= 0 ? '#22c55e' : '#ef4444'}
                fillOpacity={0.12}
              />
            )}

            <Area
              type="monotone"
              dataKey="close"
              stroke="none"
              fill="url(#priceGrad)"
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="close"
              stroke="#3182f6"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />

            {/* Signal markers */}
            {signalMarkers.map((m, i) => (
              <ReferenceDot
                key={`sig-${i}`}
                x={chartData[m.dataIdx]?.date}
                y={m.priceAtSignal}
                r={4}
                fill={SIGNAL_COLORS[m.signal] || '#8b95a1'}
                stroke="white"
                strokeWidth={1.5}
                style={{ cursor: 'pointer' }}
                onClick={() => onSignalClick?.(m)}
              />
            ))}

            {/* Disable default tooltip during drag */}
            <Tooltip
              active={!isDragging}
              content={({ active, payload }) => {
                if (isDragging || !active || !payload?.length) return null;
                const d = payload[0].payload;
                // Find signal at this date
                const sig = signalMarkers.find(s => chartData[s.dataIdx]?.date === d.date);
                return (
                  <div className="bg-white border border-[#e8e8e8] rounded-lg shadow-lg p-3 text-xs">
                    <div className="text-[#8b95a1] mb-1">
                      {new Date(d.date).toLocaleDateString('ko-KR')}
                    </div>
                    <div className="font-bold text-[#191f28]">
                      {formatStockPrice(d.close, code)}
                    </div>
                    {sig && (
                      <div className="mt-1 pt-1 border-t border-[#e8e8e8]">
                        <span className="font-medium" style={{ color: SIGNAL_COLORS[sig.signal] }}>
                          {sig.signal}
                        </span>
                        <span className="text-[#8b95a1] ml-1">{sig.influencer}</span>
                      </div>
                    )}
                  </div>
                );
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>

        {/* Drag selection info banner */}
        {dragSelection && (
          <div
            className="absolute top-2 left-1/2 -translate-x-1/2 z-50 bg-white/95 backdrop-blur-sm border border-[#e8e8e8] rounded-lg shadow-lg px-4 py-2 cursor-pointer"
            onClick={clearSelection}
            title="클릭하여 선택 해제"
          >
            <div className="flex items-center gap-3">
              <span className={`text-lg font-bold ${dragSelection.pct >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                {dragSelection.pct >= 0 ? '+' : ''}{formatStockPrice(dragSelection.diff, code)} ({dragSelection.pct >= 0 ? '+' : ''}{dragSelection.pct.toFixed(2)}%) {dragSelection.pct >= 0 ? '↑' : '↓'}
              </span>
            </div>
            <div className="text-xs text-[#8b95a1] mt-0.5">
              {new Date(dragSelection.startDate).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
              {' — '}
              {new Date(dragSelection.endDate).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
              {' • '}
              {formatStockPrice(dragSelection.startPrice, code)} → {formatStockPrice(dragSelection.endPrice, code)}
            </div>
          </div>
        )}
      </div>

      {/* Signal type filter legend */}
      <div className="flex justify-center gap-3 mt-3">
        {ALL_SIGNAL_TYPES.map(type => {
          const isActive = activeTypes.includes(type);
          return (
            <button
              key={type}
              onClick={() => onSignalTypeToggle?.(type)}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium transition-all ${
                isActive ? 'opacity-100' : 'opacity-30 line-through'
              }`}
              style={{
                backgroundColor: isActive ? (SIGNAL_COLORS[type] || '#8b95a1') + '20' : '#f0f0f0',
                color: isActive ? SIGNAL_COLORS[type] || '#8b95a1' : '#8b95a1',
              }}
            >
              {SIGNAL_EMOJI[type] || '⚪'} {type}
            </button>
          );
        })}
      </div>
    </div>
  );
}
