'use client';

import { useMemo } from 'react';

interface Signal {
  id: string;
  signal_type: string;
  date: string;
  speaker: string;
  timestamp?: string;
}

interface StockChartProps {
  stockCode: string;
  stockName: string;
  signals: Signal[];
}

export default function StockChart({ stockCode, stockName, signals }: StockChartProps) {
  // 차트 데이터 최적화 (useMemo로 성능 개선)
  const chartData = useMemo(() => {
    const chartWidth = 400;
    const chartHeight = 200;
    const padding = 30;
    
    // 더미 주가 데이터 생성 (실제 환경에서는 API 데이터 사용)
    const priceData = Array.from({ length: 50 }, (_, i) => {
      const progress = i / 49;
      const baseY = chartHeight / 2;
      const noise = (Math.sin(i * 0.3) + Math.sin(i * 0.7) * 0.5) * 20;
      const trend = progress * 30 - 15; // 약간의 상승 트렌드
      
      return {
        x: progress * (chartWidth - 2 * padding) + padding,
        y: Math.max(padding, Math.min(chartHeight - padding, baseY + noise + trend))
      };
    });
    
    // 시그널 점들 (실제 데이터 기반, 시간순 정렬)
    const sortedSignals = [...signals].sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
    
    const signalPoints = sortedSignals.map((signal, index) => {
      const progress = sortedSignals.length > 1 ? index / (sortedSignals.length - 1) : 0.5;
      const x = progress * (chartWidth - 2 * padding) + padding;
      
      // 주가 라인과 연동하여 Y 위치 계산
      const priceIndex = Math.floor(progress * (priceData.length - 1));
      const baseY = priceData[priceIndex]?.y || chartHeight / 2;
      
      // 시그널 타입에 따라 Y 위치 조정
      const yOffset = getSignalYOffset(signal.signal_type);
      const y = Math.max(padding + 10, Math.min(chartHeight - padding - 10, baseY + yOffset));
      
      return {
        x,
        y,
        signal: signal.signal_type,
        speaker: signal.speaker,
        date: signal.date,
        id: signal.id
      };
    });
    
    // 주가 라인을 부드러운 곡선으로 만들기 위한 패스 생성
    const pathD = priceData.reduce((path, point, index) => {
      if (index === 0) {
        return `M ${point.x} ${point.y}`;
      } else {
        const prevPoint = priceData[index - 1];
        const cpx1 = prevPoint.x + (point.x - prevPoint.x) * 0.5;
        const cpx2 = prevPoint.x + (point.x - prevPoint.x) * 0.5;
        return `${path} C ${cpx1} ${prevPoint.y}, ${cpx2} ${point.y}, ${point.x} ${point.y}`;
      }
    }, '');
    
    return { priceData, signalPoints, pathD };
  }, [signals]);

  // 시그널 타입별 Y 오프셋
  const getSignalYOffset = (signalType: string) => {
    switch (signalType) {
      case '매수':
      case 'BUY': return -25;
      case '긍정':
      case 'POSITIVE': return -15;
      case '중립':
      case 'NEUTRAL': return 0;
      case '경계':
      case 'CONCERN': return 15;
      case '매도':
      case 'SELL': return 25;
      default: return 0;
    }
  };

  // 시그널 색상
  const getSignalColor = (signalType: string) => {
    switch (signalType) {
      case '매수':
      case 'BUY': return '#3B82F6';
      case '긍정':
      case 'POSITIVE': return '#10B981';
      case '중립':
      case 'NEUTRAL': return '#F59E0B';
      case '경계':
      case 'CONCERN': return '#F97316';
      case '매도':
      case 'SELL': return '#EF4444';
      default: return '#6B7280';
    }
  };

  // 시그널 텍스트
  const getSignalText = (signalType: string) => {
    switch (signalType) {
      case '매수':
      case 'BUY': return '매수';
      case '긍정':
      case 'POSITIVE': return '긍정';
      case '중립':
      case 'NEUTRAL': return '중립';
      case '경계':
      case 'CONCERN': return '경계';
      case '매도':
      case 'SELL': return '매도';
      default: return signalType;
    }
  };

  return (
    <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
      <div className="flex justify-between items-center mb-4">
        <h4 className="font-medium text-[#191f28]">
          {stockName} 주가 차트 & 시그널
        </h4>
        <div className="text-sm text-[#8b95a1]">
          총 {signals.length}개 시그널
        </div>
      </div>
      
      <div className="relative h-80 bg-[#f8f9fa] rounded-lg overflow-hidden">
        <svg className="w-full h-full" viewBox="0 0 400 200">
          {/* 배경 격자 */}
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e8e8e8" strokeWidth="0.5"/>
            </pattern>
            <linearGradient id="priceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3182f6" stopOpacity="0.2"/>
              <stop offset="100%" stopColor="#3182f6" stopOpacity="0.05"/>
            </linearGradient>
          </defs>
          
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* 주가 영역 (그라데이션) */}
          <path
            d={`${chartData.pathD} L ${chartData.priceData[chartData.priceData.length - 1]?.x || 0} 200 L 30 200 Z`}
            fill="url(#priceGradient)"
          />
          
          {/* 주가 라인 (부드러운 곡선) */}
          <path
            d={chartData.pathD}
            fill="none"
            stroke="#3182f6"
            strokeWidth="3"
            opacity="0.9"
          />
          
          {/* 모든 시그널 점들 표시 (성능 최적화) */}
          <g className="signal-points">
            {chartData.signalPoints.map((point) => (
              <g key={point.id} className="signal-point">
                <circle 
                  cx={point.x} 
                  cy={point.y} 
                  r="8" 
                  fill={getSignalColor(point.signal)} 
                  stroke="white" 
                  strokeWidth="3"
                  className="cursor-pointer hover:r-10 transition-all duration-200"
                  style={{
                    filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
                  }}
                />
                {/* 호버 시 표시할 라벨 */}
                <text
                  x={point.x}
                  y={point.y - 15}
                  textAnchor="middle"
                  className="text-xs font-medium opacity-0 hover:opacity-100 transition-opacity duration-200"
                  fill={getSignalColor(point.signal)}
                >
                  {getSignalText(point.signal)}
                </text>
                
                {/* 툴팁 정보 */}
                <title>
                  {point.speaker} - {getSignalText(point.signal)}
                  {'\n'}날짜: {new Date(point.date).toLocaleDateString('ko-KR')}
                </title>
              </g>
            ))}
          </g>
          
          {/* Y축 라벨 */}
          <text x="10" y="25" className="text-xs fill-gray-500">고점</text>
          <text x="10" y="185" className="text-xs fill-gray-500">저점</text>
          
          {/* X축 라벨 (시간) */}
          <text x="40" y="195" className="text-xs fill-gray-500">과거</text>
          <text x="350" y="195" className="text-xs fill-gray-500">현재</text>
        </svg>
        
        {/* 개선된 범례 */}
        <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg p-4 shadow-lg border border-gray-200">
          <div className="font-medium text-sm mb-3 text-[#191f28]">시그널 타입</div>
          <div className="grid grid-cols-1 gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
              <span>매수 ({chartData.signalPoints.filter(p => ['매수', 'BUY'].includes(p.signal)).length})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-green-500 rounded-full"></span>
              <span>긍정 ({chartData.signalPoints.filter(p => ['긍정', 'POSITIVE'].includes(p.signal)).length})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
              <span>중립 ({chartData.signalPoints.filter(p => ['중립', 'NEUTRAL'].includes(p.signal)).length})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-orange-500 rounded-full"></span>
              <span>경계 ({chartData.signalPoints.filter(p => ['경계', 'CONCERN'].includes(p.signal)).length})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-red-500 rounded-full"></span>
              <span>매도 ({chartData.signalPoints.filter(p => ['매도', 'SELL'].includes(p.signal)).length})</span>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-600">
            총 {chartData.signalPoints.length}개 시그널
          </div>
        </div>
      </div>
      
      {/* 시그널 요약 */}
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div className="p-3 bg-blue-50 rounded-lg">
          <div className="text-lg font-bold text-blue-600">
            {chartData.signalPoints.filter(p => ['매수', 'BUY'].includes(p.signal)).length}
          </div>
          <div className="text-sm text-blue-800">매수 신호</div>
        </div>
        <div className="p-3 bg-green-50 rounded-lg">
          <div className="text-lg font-bold text-green-600">
            {chartData.signalPoints.filter(p => ['긍정', 'POSITIVE'].includes(p.signal)).length}
          </div>
          <div className="text-sm text-green-800">긍정 신호</div>
        </div>
        <div className="p-3 bg-red-50 rounded-lg">
          <div className="text-lg font-bold text-red-600">
            {chartData.signalPoints.filter(p => ['매도', 'SELL'].includes(p.signal)).length}
          </div>
          <div className="text-sm text-red-800">매도 신호</div>
        </div>
      </div>
    </div>
  );
}