'use client';

import { useMemo, useState } from 'react';
import dynamic from 'next/dynamic';
import stockPricesData from '@/data/stockPrices.json';

const LineChart = dynamic(() => import('recharts').then((mod) => mod.LineChart), { ssr: false });
const Line = dynamic(() => import('recharts').then((mod) => mod.Line), { ssr: false });
const XAxis = dynamic(() => import('recharts').then((mod) => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then((mod) => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then((mod) => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then((mod) => mod.Tooltip), { ssr: false });
const ResponsiveContainer = dynamic(() => import('recharts').then((mod) => mod.ResponsiveContainer), { ssr: false });
const ComposedChart = dynamic(() => import('recharts').then((mod) => mod.ComposedChart), { ssr: false });
const Scatter = dynamic(() => import('recharts').then((mod) => mod.Scatter), { ssr: false });
const ZAxis = dynamic(() => import('recharts').then((mod) => mod.ZAxis), { ssr: false });

interface Signal {
  date: string;
  signal: string;
  target_price?: number | null;
  firm: string;
  analyst?: string | null;
  title?: string;
}

interface StockAnalystChartProps {
  code: string;
  signals: Signal[];
  currentPrice: number;
}

const getSignalColor = (signal: string) => {
  switch (signal.toUpperCase()) {
    case 'BUY': return '#22c55e';
    case 'HOLD': return '#eab308';
    case 'SELL': return '#ef4444';
    default: return '#8b95a1';
  }
};

export default function StockAnalystChart({ code, signals, currentPrice }: StockAnalystChartProps) {
  const [activeSignal, setActiveSignal] = useState<Signal | null>(null);
  const [popupPos, setPopupPos] = useState<{ x: number; y: number } | null>(null);

  const chartData = useMemo(() => {
    // 실제 주가 데이터 사용
    const stockData = (stockPricesData as any)[code];
    const prices: { date: string; close: number }[] = stockData?.prices || [];
    
    if (prices.length === 0) return null;

    // 주가 데이터를 차트용으로 변환
    const priceData = prices.map(p => ({
      date: p.date,
      price: p.close,
    }));

    // Y축 범위: 주가 + 목표가 모두 고려
    const allValues = prices.map(p => p.close);
    signals.forEach(s => {
      if (s.target_price && s.target_price > 0) allValues.push(s.target_price);
    });
    const minVal = Math.min(...allValues);
    const maxVal = Math.max(...allValues);
    const yMin = Math.floor(minVal * 0.9 / 1000) * 1000;
    const yMax = Math.ceil(maxVal * 1.1 / 1000) * 1000;

    // 시그널 점 데이터 (목표가 위치에 표시)
    const signalDots = signals
      .filter(s => s.target_price && s.target_price > 0)
      .map(s => ({
        date: s.date,
        targetPrice: s.target_price!,
        signal: s.signal,
        firm: s.firm,
        analyst: s.analyst || null,
        title: s.title || '',
      }));

    return { priceData, signalDots, yDomain: [yMin, yMax] as [number, number] };
  }, [code, signals]);

  if (!chartData || chartData.priceData.length === 0) {
    return (
      <div className="w-full h-64 bg-[#f8f9fa] rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl mb-2">📈</div>
          <p className="text-[#8b95a1]">차트 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // 주가 + 시그널을 합친 데이터
  const mergedData = chartData.priceData.map(p => {
    const dot = chartData.signalDots.find(d => d.date === p.date);
    return dot ? { ...p, targetPrice: dot.targetPrice, signalType: dot.signal, signalFirm: dot.firm, signalAnalyst: dot.analyst, signalTitle: dot.title } : p;
  });

  const CustomSignalDot = (props: any) => {
    const { payload, cx, cy } = props;
    if (!payload?.targetPrice) return null;
    return (
      <circle
        cx={cx}
        cy={cy}
        r={5}
        fill={getSignalColor(payload.signalType)}
        stroke="white"
        strokeWidth={2}
        style={{ cursor: 'pointer' }}
        onMouseEnter={(e) => {
          setActiveSignal({ date: payload.date, signal: payload.signalType, target_price: payload.targetPrice, firm: payload.signalFirm, analyst: payload.signalAnalyst, title: payload.signalTitle });
          setPopupPos({ x: e.clientX, y: e.clientY });
        }}
        onMouseLeave={() => { setActiveSignal(null); setPopupPos(null); }}
      />
    );
  };

  return (
    <div className="bg-white rounded-lg border border-[#e8e8e8] p-4 relative">
      <div className="mb-4">
        <h4 className="font-medium text-[#191f28] mb-2">주가 및 애널리스트 목표가</h4>
        <div className="flex items-center gap-4 text-sm text-[#8b95a1] flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-[#3182f6]"></div>
            <span>현재주가</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#22c55e]"></div>
            <span>매수</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#eab308]"></div>
            <span>중립</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#ef4444]"></div>
            <span>매도</span>
          </div>
        </div>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={mergedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => new Date(date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
              stroke="#8b95a1"
              fontSize={12}
            />
            <YAxis
              domain={chartData.yDomain}
              tickFormatter={(value) => `${Math.round(value / 1000)}k`}
              stroke="#8b95a1"
              fontSize={12}
            />
            <Tooltip
              formatter={(value: any, name: string) => {
                if (name === 'price') return [`${value.toLocaleString()}원`, '주가'];
                if (name === 'targetPrice') return [`${value.toLocaleString()}원`, '목표가'];
                return [value, name];
              }}
              labelFormatter={(date) => new Date(date).toLocaleDateString('ko-KR')}
              contentStyle={{ backgroundColor: 'white', border: '1px solid #e8e8e8', borderRadius: '8px', fontSize: '12px' }}
            />
            <Line type="monotone" dataKey="price" stroke="#3182f6" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#3182f6' }} />
            <Line type="monotone" dataKey="targetPrice" stroke="transparent" strokeWidth={0} dot={<CustomSignalDot />} activeDot={false} connectNulls={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* 시그널 팝업 */}
      {activeSignal && popupPos && (
        <div
          className="fixed z-50 bg-white border border-[#e8e8e8] rounded-xl shadow-lg p-3 text-sm pointer-events-none"
          style={{ left: popupPos.x + 12, top: popupPos.y - 60 }}
        >
          <div className="font-bold text-[#191f28] mb-1">{activeSignal.firm}</div>
          {activeSignal.analyst && <div className="text-[#8b95a1] text-xs">{activeSignal.analyst}</div>}
          <div className="text-[#191f28]">목표가: {activeSignal.target_price?.toLocaleString()}원</div>
          <div className="text-[#191f28]">투자의견: {activeSignal.signal}</div>
          {activeSignal.title && <div className="text-[#8b95a1] text-xs mt-1 max-w-[200px] truncate">{activeSignal.title}</div>}
        </div>
      )}
    </div>
  );
}
