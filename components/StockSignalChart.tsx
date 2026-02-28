'use client';

import { useState, useMemo } from 'react';
import stockPricesData from '@/data/stockPrices.json';

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
}

export default function StockSignalChart({ code, signals, periodFilter, onSignalClick }: StockSignalChartProps) {
  const [hoveredSignal, setHoveredSignal] = useState<Signal | null>(null);
  const [hoverPos, setHoverPos] = useState({ x: 0, y: 0 });

  const stockData = (stockPricesData as any)[code];

  const chartConfig = useMemo(() => {
    if (!stockData?.prices?.length) return null;

    // Filter prices by period
    let prices = stockData.prices;
    if (periodFilter && periodFilter !== '전체') {
      const now = new Date();
      let cutoff = new Date();
      switch (periodFilter) {
        case '1개월': cutoff.setMonth(now.getMonth() - 1); break;
        case '6개월': cutoff.setMonth(now.getMonth() - 6); break;
        case '1년': cutoff.setFullYear(now.getFullYear() - 1); break;
        case '3년': cutoff.setFullYear(now.getFullYear() - 3); break;
      }
      const filtered = prices.filter((p: any) => new Date(p.date) >= cutoff);
      if (filtered.length >= 2) prices = filtered;
    }
    const closes = prices.map((p: any) => p.close);
    const minPrice = Math.min(...closes);
    const maxPrice = Math.max(...closes);
    const priceRange = maxPrice - minPrice || 1;

    // Chart dimensions
    const W = 460, H = 240;
    const padL = 60, padR = 20, padT = 20, padB = 35;
    const chartW = W - padL - padR;
    const chartH = H - padT - padB;

    // Price to Y coordinate
    const priceToY = (price: number) => padT + chartH - ((price - minPrice) / priceRange) * chartH;

    // Date to X coordinate
    const dateToX = (idx: number) => padL + (idx / (prices.length - 1)) * chartW;

    // Build path
    const pathPoints = prices.map((p: any, i: number) => {
      const x = dateToX(i);
      const y = priceToY(p.close);
      return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
    }).join(' ');

    const areaPath = pathPoints + ` L ${dateToX(prices.length - 1).toFixed(1)} ${padT + chartH} L ${padL} ${padT + chartH} Z`;

    // Y axis labels (5 levels)
    const yLabels = [];
    const step = priceRange / 4;
    for (let i = 0; i <= 4; i++) {
      const price = minPrice + step * i;
      yLabels.push({ price: Math.round(price), y: priceToY(price) });
    }

    // X axis labels (show ~6 dates)
    const xLabels = [];
    const xStep = Math.max(1, Math.floor(prices.length / 5));
    for (let i = 0; i < prices.length; i += xStep) {
      const d = new Date(prices[i].date);
      const label = `${d.getMonth() + 1}/${d.getDate()}`;
      xLabels.push({ label, x: dateToX(i) });
    }
    // Always include last
    const lastD = new Date(prices[prices.length - 1].date);
    xLabels.push({ label: `${lastD.getMonth() + 1}/${lastD.getDate()}`, x: dateToX(prices.length - 1) });

    // Map signals to chart coordinates
    const signalMarkers = signals.map(sig => {
      // Find closest price date
      const sigDate = sig.date;
      let closestIdx = prices.length - 1;
      let closestDiff = Infinity;
      prices.forEach((p: any, i: number) => {
        const diff = Math.abs(new Date(p.date).getTime() - new Date(sigDate).getTime());
        if (diff < closestDiff) {
          closestDiff = diff;
          closestIdx = i;
        }
      });
      return {
        ...sig,
        x: dateToX(closestIdx),
        y: priceToY(prices[closestIdx].close),
        priceAtSignal: prices[closestIdx].close,
      };
    });

    const formatPrice = (p: number) => {
      if (p >= 1000000) return `${(p / 10000).toFixed(0)}만`;
      return p.toLocaleString();
    };

    return { W, H, padL, padT, padB, chartH, pathPoints, areaPath, yLabels, xLabels, signalMarkers, formatPrice, currentPrice: stockData.currentPrice };
  }, [stockData, signals, periodFilter]);

  if (!chartConfig) {
    return (
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <h4 className="font-medium text-[#191f28] mb-4">주가 차트 & 신호</h4>
        <div className="h-64 bg-[#f8f9fa] rounded-lg flex items-center justify-center text-[#8b95a1]">
          주가 데이터를 불러올 수 없습니다
        </div>
      </div>
    );
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case '매수': return '#3182f6';
      case '긍정': return '#22c55e';
      case '중립': return '#eab308';
      case '경계': return '#f97316';
      case '매도': return '#ef4444';
      default: return '#8b95a1';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
      <div className="flex justify-between items-center mb-4">
        <h4 className="font-medium text-[#191f28]">주가 차트 & 신호</h4>
        <div className="text-sm text-[#8b95a1]">
          현재가 <span className="font-bold text-[#191f28]">{chartConfig.currentPrice.toLocaleString()}원</span>
        </div>
      </div>
      <div className="relative h-72 bg-[#f8f9fa] rounded-lg overflow-visible">
        <svg className="w-full h-full" viewBox={`0 0 ${chartConfig.W} ${chartConfig.H}`}>
          <defs>
            <linearGradient id="priceGradReal" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3182f6" stopOpacity="0.15"/>
              <stop offset="100%" stopColor="#3182f6" stopOpacity="0.02"/>
            </linearGradient>
          </defs>

          {/* Y axis grid + labels */}
          {chartConfig.yLabels.map((yl: any, i: number) => (
            <g key={`y-${i}`}>
              <line x1={chartConfig.padL} y1={yl.y} x2={chartConfig.W - 20} y2={yl.y} stroke="#e8e8e8" strokeWidth="0.5" strokeDasharray="3,3"/>
              <text x={chartConfig.padL - 5} y={yl.y + 4} textAnchor="end" fontSize="10" fill="#8b95a1">
                {chartConfig.formatPrice(yl.price)}
              </text>
            </g>
          ))}

          {/* X axis labels */}
          {chartConfig.xLabels.map((xl: any, i: number) => (
            <text key={`x-${i}`} x={xl.x} y={chartConfig.H - 5} textAnchor="middle" fontSize="10" fill="#8b95a1">
              {xl.label}
            </text>
          ))}

          {/* Price area fill */}
          <path d={chartConfig.areaPath} fill="url(#priceGradReal)"/>
          
          {/* Price line */}
          <path d={chartConfig.pathPoints} fill="none" stroke="#3182f6" strokeWidth="2.5"/>

          {/* Signal markers */}
          {chartConfig.signalMarkers.map((marker: any, i: number) => (
            <g key={`sig-${i}`} style={{ cursor: 'pointer' }}
              onMouseEnter={(e) => {
                setHoveredSignal(marker);
                const rect = (e.target as SVGElement).closest('svg')?.getBoundingClientRect();
                if (rect) {
                  const svgX = marker.x / chartConfig.W * rect.width;
                  const svgY = marker.y / chartConfig.H * rect.height;
                  setHoverPos({ x: svgX, y: svgY });
                }
              }}
              onMouseLeave={() => setHoveredSignal(null)}
              onClick={() => onSignalClick?.(marker)}
            >
              <circle cx={marker.x} cy={marker.y} r="8" fill={getSignalColor(marker.signal)} stroke="white" strokeWidth="2.5" opacity="0.9"/>
              <text x={marker.x} y={marker.y - 12} textAnchor="middle" fontSize="9" fill={getSignalColor(marker.signal)} fontWeight="bold">
                {marker.signal}
              </text>
            </g>
          ))}
        </svg>

        {/* Hover tooltip */}
        {hoveredSignal && (
          <div
            className="absolute z-50 bg-white border border-[#e8e8e8] rounded-lg shadow-lg p-3 pointer-events-none"
            style={{
              left: Math.min(hoverPos.x, 280),
              top: Math.max(hoverPos.y - 100, 0),
              maxWidth: '220px'
            }}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="font-bold text-sm text-[#191f28]">{(hoveredSignal as any).influencer}</span>
              <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                hoveredSignal.signal === '매수' ? 'text-blue-600 bg-blue-50' :
                hoveredSignal.signal === '긍정' ? 'text-green-600 bg-green-50' :
                'text-gray-600 bg-gray-50'
              }`}>{hoveredSignal.signal}</span>
            </div>
            <div className="text-xs text-[#8b95a1] mb-1">{hoveredSignal.date} • {(hoveredSignal as any).priceAtSignal?.toLocaleString()}원</div>
            <div className="text-xs text-[#191f28] line-clamp-2">&ldquo;{hoveredSignal.quote}&rdquo;</div>
          </div>
        )}

        {/* Legend */}
        <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-lg p-2 text-xs">
          <div className="flex items-center gap-2 mb-1">
            <span>🔵 매수</span><span>🟢 긍정</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🟡 중립</span><span>🟠 경계</span><span>🔴 매도</span>
          </div>
        </div>
      </div>
    </div>
  );
}
