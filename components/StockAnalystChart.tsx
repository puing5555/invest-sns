'use client';

import { useMemo } from 'react';
import dynamic from 'next/dynamic';

// Recharts를 동적 import로 SSG 문제 해결
const LineChart = dynamic(
  () => import('recharts').then((mod) => mod.LineChart),
  { ssr: false }
);
const Line = dynamic(
  () => import('recharts').then((mod) => mod.Line),
  { ssr: false }
);
const XAxis = dynamic(
  () => import('recharts').then((mod) => mod.XAxis),
  { ssr: false }
);
const YAxis = dynamic(
  () => import('recharts').then((mod) => mod.YAxis),
  { ssr: false }
);
const CartesianGrid = dynamic(
  () => import('recharts').then((mod) => mod.CartesianGrid),
  { ssr: false }
);
const Tooltip = dynamic(
  () => import('recharts').then((mod) => mod.Tooltip),
  { ssr: false }
);
const ReferenceLine = dynamic(
  () => import('recharts').then((mod) => mod.ReferenceLine),
  { ssr: false }
);
const Scatter = dynamic(
  () => import('recharts').then((mod) => mod.Scatter),
  { ssr: false }
);
const ScatterChart = dynamic(
  () => import('recharts').then((mod) => mod.ScatterChart),
  { ssr: false }
);
const ResponsiveContainer = dynamic(
  () => import('recharts').then((mod) => mod.ResponsiveContainer),
  { ssr: false }
);
const ComposedChart = dynamic(
  () => import('recharts').then((mod) => mod.ComposedChart),
  { ssr: false }
);

interface Signal {
  date: string;
  signal: string;
  target_price?: number;
  firm: string;
}

interface StockAnalystChartProps {
  code: string;
  signals: Signal[];
  currentPrice: number;
}

// 더미 주가 데이터 생성
const generatePriceData = (signals: Signal[], currentPrice: number) => {
  const data = [];
  const now = new Date();
  
  // 6개월 치 일일 데이터 생성
  for (let i = 180; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    // 기본 주가에 노이즈와 트렌드 추가
    const basePrice = currentPrice;
    const noise = (Math.random() - 0.5) * basePrice * 0.1; // 10% 변동성
    const trend = -i * basePrice * 0.0005; // 약간의 상승 트렌드
    
    const price = Math.max(basePrice * 0.5, basePrice + noise + trend);
    
    data.push({
      date: date.toISOString().split('T')[0],
      price: Math.round(price),
      timestamp: date.getTime()
    });
  }
  
  return data;
};

// 목표주가 평균 계산
const calculateAverageTargetPrice = (signals: Signal[]) => {
  const validTargets = signals.filter(s => s.target_price && s.target_price > 0);
  if (validTargets.length === 0) return null;
  
  const sum = validTargets.reduce((acc, s) => acc + (s.target_price || 0), 0);
  return Math.round(sum / validTargets.length);
};

// 시그널 점 색상
const getSignalColor = (signal: string) => {
  switch (signal.toLowerCase()) {
    case 'buy':
    case '매수': return '#22c55e';
    case 'hold':
    case '중립': return '#eab308';
    case 'sell':
    case '매도': return '#ef4444';
    default: return '#8b95a1';
  }
};

// 한글 시그널명으로 변환
const getSignalName = (signal: string) => {
  switch (signal.toLowerCase()) {
    case 'buy': return '매수';
    case 'hold': return '중립';
    case 'sell': return '매도';
    default: return signal;
  }
};

export default function StockAnalystChart({ code, signals, currentPrice }: StockAnalystChartProps) {
  const chartData = useMemo(() => {
    const priceData = generatePriceData(signals, currentPrice || 50000);
    const avgTargetPrice = calculateAverageTargetPrice(signals);
    
    // 날짜별 데이터 맵 생성
    const dateMap = new Map(priceData.map(d => [d.date, d]));
    
    // 시그널 점들을 주가 데이터와 통합
    const enrichedData = priceData.map(pricePoint => {
      // 해당 날짜의 시그널 찾기
      const signalOnDate = signals.find(s => s.date === pricePoint.date);
      
      if (signalOnDate) {
        return {
          ...pricePoint,
          signalPrice: pricePoint.price, // 실제 주가 위치에 시그널 표시
          signalType: signalOnDate.signal,
          signalFirm: signalOnDate.firm,
          hasSignal: true
        };
      }
      
      return pricePoint;
    });
    
    return { enrichedData, avgTargetPrice };
  }, [signals, currentPrice]);

  if (!chartData.enrichedData.length) {
    return (
      <div className="w-full h-64 bg-[#f8f9fa] rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl mb-2">📈</div>
          <p className="text-[#8b95a1]">차트 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // 커스텀 Dot 컴포넌트 
  const CustomSignalDot = (props: any) => {
    const { payload, cx, cy } = props;
    if (!payload?.hasSignal) return null;
    
    return (
      <circle
        cx={cx}
        cy={cy}
        r={4}
        fill={getSignalColor(payload.signalType)}
        stroke="white"
        strokeWidth={2}
        style={{ cursor: 'pointer' }}
      />
    );
  };

  return (
    <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
      <div className="mb-4">
        <h4 className="font-medium text-[#191f28] mb-2">주가 및 애널리스트 목표가</h4>
        <div className="flex items-center gap-4 text-sm text-[#8b95a1]">
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-[#3182f6]"></div>
            <span>현재주가</span>
          </div>
          {chartData.avgTargetPrice && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-0.5 border-t-2 border-dashed border-[#8b95a1]"></div>
              <span>평균목표가</span>
            </div>
          )}
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
          <ComposedChart data={chartData.enrichedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => new Date(date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
              stroke="#8b95a1"
              fontSize={12}
            />
            <YAxis
              tickFormatter={(value) => `${Math.round(value / 1000)}k`}
              stroke="#8b95a1"
              fontSize={12}
            />
            <Tooltip
              formatter={(value: any, name: string, props: any) => {
                if (name === 'price') {
                  return [`${value.toLocaleString()}원`, '주가'];
                }
                if (name === 'signalPrice' && props.payload?.hasSignal) {
                  return [
                    `${getSignalName(props.payload.signalType)} (${props.payload.signalFirm})`,
                    '시그널'
                  ];
                }
                return [value, name];
              }}
              labelFormatter={(date) => new Date(date).toLocaleDateString('ko-KR')}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e8e8e8',
                borderRadius: '8px',
                fontSize: '12px'
              }}
            />
            
            {/* 주가 라인 차트 */}
            <Line
              type="monotone"
              dataKey="price"
              stroke="#3182f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#3182f6' }}
            />
            
            {/* 시그널 점들 - 주가와 같은 위치에 */}
            <Line
              type="monotone"
              dataKey="signalPrice"
              stroke="transparent"
              strokeWidth={0}
              dot={<CustomSignalDot />}
              activeDot={false}
              connectNulls={false}
            />
            
            {/* 평균 목표주가 점선 */}
            {chartData.avgTargetPrice && (
              <ReferenceLine
                y={chartData.avgTargetPrice}
                stroke="#8b95a1"
                strokeDasharray="5 5"
                label={{
                  value: `목표 ${Math.round(chartData.avgTargetPrice / 10000)}만원`,
                  position: 'right',
                  style: { fontSize: '11px', fill: '#8b95a1' }
                }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}