'use client';

import { useState, useEffect, useRef } from 'react';
import { getCachedStockData, setCachedStockData } from '@/lib/stock-cache';

interface StockChartV2Props {
  stockCode: string;
  stockName: string;
  signals?: any[];
  mode?: 'realtime' | 'influencer' | 'analyst';
}

interface ChartPeriod {
  id: string;
  label: string;
  days: number;
}

const CHART_PERIODS: ChartPeriod[] = [
  { id: '1M', label: '1개월', days: 30 },
  { id: '6M', label: '6개월', days: 180 },
  { id: '1Y', label: '1년', days: 365 },
  { id: '3Y', label: '3년', days: 1095 },
  { id: 'ALL', label: '전체', days: -1 }
];

// V9 시그널 색상 매핑 (한글 시그널)
const SIGNAL_COLORS: { [key: string]: string } = {
  '매수': '#2563eb',     // 파란색
  '긍정': '#16a34a',     // 초록색
  '중립': '#6b7280',     // 회색
  '경계': '#f59e0b',     // 주황색
  '매도': '#dc2626'      // 빨간색
};

// 영문 시그널도 지원
const ENGLISH_SIGNAL_MAPPING: { [key: string]: string } = {
  'BUY': '매수',
  'POSITIVE': '긍정',
  'NEUTRAL': '중립',
  'CONCERN': '경계',
  'SELL': '매도'
};

const normalizeSignal = (signal: string): string => {
  return ENGLISH_SIGNAL_MAPPING[signal] || signal;
};

export default function StockChartV2({ 
  stockCode, 
  stockName, 
  signals = [],
  mode = 'realtime' 
}: StockChartV2Props) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('6M');
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cacheUsed, setCacheUsed] = useState(false);

  // 실제 주가 데이터 가져오기 (캐싱 적용)
  const fetchStockData = async (symbol: string, period: string) => {
    setLoading(true);
    setError(null);
    setCacheUsed(false);

    try {
      // 캐시 확인
      const cachedData = getCachedStockData(symbol, period);
      if (cachedData) {
        setChartData(cachedData);
        setCacheUsed(true);
        setLoading(false);
        return;
      }

      let data: any[] = [];
      
      // 종목 코드에 따라 API 선택
      if (symbol.match(/^[0-9]{6}$/)) {
        // 한국 주식 (6자리 숫자)
        data = await fetchKoreanStock(symbol, period);
      } else if (['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'SOL'].includes(symbol.toUpperCase())) {
        // 암호화폐
        data = await fetchCrypto(symbol, period);
      } else {
        // 미국 주식
        data = await fetchUSStock(symbol, period);
      }

      // 캐시에 저장
      setCachedStockData(symbol, period, data);
      setChartData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '데이터를 가져올 수 없습니다');
      // 에러 시 더미 데이터 사용
      const dummyData = generateDummyData(30);
      setChartData(dummyData);
    }

    setLoading(false);
  };

  // 한국 주식 데이터 (Yahoo Finance via AllOrigins)
  const fetchKoreanStock = async (symbol: string, period: string): Promise<any[]> => {
    const koreanSymbol = symbol + '.KS'; // 코스피 종목
    const url = `https://api.allorigins.win/raw?url=${encodeURIComponent(`https://query1.finance.yahoo.com/v8/finance/chart/${koreanSymbol}?interval=1d&range=${period.toLowerCase()}`)}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('한국 주식 데이터 조회 실패');
    
    const data = await response.json();
    const result = data.chart?.result?.[0];
    
    if (!result) throw new Error('주식 데이터가 없습니다');
    
    const timestamps = result.timestamp || [];
    const prices = result.indicators?.quote?.[0]?.close || [];
    
    return timestamps.map((timestamp: number, index: number) => ({
      date: new Date(timestamp * 1000),
      price: prices[index] || 0
    })).filter((item: any) => item.price > 0);
  };

  // 암호화폐 데이터 (CoinGecko)
  const fetchCrypto = async (symbol: string, period: string): Promise<any[]> => {
    const coinId = getCoinGeckoId(symbol);
    const days = CHART_PERIODS.find(p => p.id === period)?.days || 180;
    
    const url = `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=krw&days=${days}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('암호화폐 데이터 조회 실패');
    
    const data = await response.json();
    const prices = data.prices || [];
    
    return prices.map(([timestamp, price]: [number, number]) => ({
      date: new Date(timestamp),
      price: price
    }));
  };

  // 미국 주식 데이터 (Yahoo Finance)
  const fetchUSStock = async (symbol: string, period: string): Promise<any[]> => {
    const url = `https://api.allorigins.win/raw?url=${encodeURIComponent(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=${period.toLowerCase()}`)}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('미국 주식 데이터 조회 실패');
    
    const data = await response.json();
    const result = data.chart?.result?.[0];
    
    if (!result) throw new Error('주식 데이터가 없습니다');
    
    const timestamps = result.timestamp || [];
    const prices = result.indicators?.quote?.[0]?.close || [];
    
    return timestamps.map((timestamp: number, index: number) => ({
      date: new Date(timestamp * 1000),
      price: prices[index] || 0
    })).filter((item: any) => item.price > 0);
  };

  // CoinGecko ID 매핑
  const getCoinGeckoId = (symbol: string): string => {
    const mapping: { [key: string]: string } = {
      'BTC': 'bitcoin',
      'ETH': 'ethereum',
      'XRP': 'ripple',
      'ADA': 'cardano',
      'DOT': 'polkadot',
      'SOL': 'solana'
    };
    return mapping[symbol.toUpperCase()] || symbol.toLowerCase();
  };

  // 더미 데이터 생성 (에러 시 사용)
  const generateDummyData = (days: number) => {
    const data = [];
    const now = new Date();
    let price = 50000 + Math.random() * 50000;

    for (let i = days; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      price = price * (0.95 + Math.random() * 0.1); // ±5% 변동
      data.push({ date, price });
    }

    return data;
  };

  // 시그널과 주가 데이터 매핑 개선
  const getSignalPosition = (signal: any) => {
    const signalDate = new Date(signal.date || signal.video_published_at || signal.published_at);
    
    // 더 정교한 매칭: 날짜 차이가 가장 적은 데이터포인트 찾기
    let bestMatch = null;
    let smallestDiff = Infinity;

    chartData.forEach((dataPoint, index) => {
      const diff = Math.abs(dataPoint.date.getTime() - signalDate.getTime());
      if (diff < smallestDiff) {
        smallestDiff = diff;
        bestMatch = { dataPoint, index };
      }
    });

    // 7일 이내의 차이만 유효한 매칭으로 간주
    if (bestMatch && smallestDiff <= 7 * 24 * 60 * 60 * 1000) {
      return bestMatch;
    }

    return null;
  };

  // 차트 그리기 (개선된 시그널 표시)
  const drawChart = () => {
    const canvas = chartRef.current;
    if (!canvas || chartData.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 캔버스 크기 설정
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * devicePixelRatio;
    canvas.height = rect.height * devicePixelRatio;
    ctx.scale(devicePixelRatio, devicePixelRatio);

    const width = rect.width;
    const height = rect.height;
    const padding = { top: 20, right: 40, bottom: 40, left: 80 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // 클리어
    ctx.clearRect(0, 0, width, height);

    // 배경
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);

    // 가격 범위 계산
    const prices = chartData.map(d => d.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;

    // 그리드 그리기
    ctx.strokeStyle = '#f0f0f0';
    ctx.lineWidth = 1;

    // 수평 그리드 (가격)
    for (let i = 0; i <= 5; i++) {
      const y = padding.top + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartWidth, y);
      ctx.stroke();

      // 가격 레이블
      const price = maxPrice - (priceRange / 5) * i;
      ctx.fillStyle = '#666';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(price.toLocaleString(), padding.left - 10, y + 4);
    }

    // 차트 라인 그리기 (파란색)
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();

    chartData.forEach((point, index) => {
      const x = padding.left + (chartWidth / (chartData.length - 1)) * index;
      const y = padding.top + chartHeight - ((point.price - minPrice) / priceRange) * chartHeight;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // 개선된 시그널 점 그리기
    let renderedSignals = 0;
    signals.forEach((signal, signalIndex) => {
      const position = getSignalPosition(signal);

      if (position) {
        const { dataPoint, index } = position;
        const x = padding.left + (chartWidth / (chartData.length - 1)) * index;
        const y = padding.top + chartHeight - ((dataPoint.price - minPrice) / priceRange) * chartHeight;

        // 시그널 타입 정규화
        const normalizedSignal = normalizeSignal(signal.signal_type || signal.signal || signal.direction);
        const color = SIGNAL_COLORS[normalizedSignal] || '#6b7280';

        // 시그널 점 그리기
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, 2 * Math.PI);
        ctx.fill();

        // 흰색 테두리
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        // 시그널 번호 (겹치는 시그널 구분용)
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText((signalIndex + 1).toString(), x, y + 3);

        renderedSignals++;
      }
    });

    console.log(`시그널 렌더링: ${renderedSignals}/${signals.length}개`);
  };

  // 데이터 로드
  useEffect(() => {
    fetchStockData(stockCode, selectedPeriod);
  }, [stockCode, selectedPeriod]);

  // 차트 그리기
  useEffect(() => {
    if (chartData.length > 0) {
      drawChart();
    }
  }, [chartData, signals]);

  // 윈도우 리사이즈 처리
  useEffect(() => {
    const handleResize = () => {
      setTimeout(drawChart, 100); // 리사이즈 후 잠시 대기
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [chartData, signals]);

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{stockName} 주가 차트</h3>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span>실시간 주가와 {mode === 'influencer' ? '인플루언서' : '애널리스트'} 시그널</span>
            {cacheUsed && (
              <span className="bg-green-100 text-green-600 px-2 py-0.5 rounded text-xs">
                캐시됨
              </span>
            )}
          </div>
        </div>

        {/* 시그널 범례 */}
        <div className="flex items-center space-x-3 text-xs">
          {Object.entries(SIGNAL_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center space-x-1">
              <div 
                className="w-3 h-3 rounded-full border border-white"
                style={{ backgroundColor: color }}
              ></div>
              <span className="text-gray-600">{type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 기간 선택 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          {CHART_PERIODS.map(period => (
            <button
              key={period.id}
              onClick={() => setSelectedPeriod(period.id)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedPeriod === period.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {period.label}
            </button>
          ))}
        </div>

        {/* 시그널 매칭 상태 */}
        <div className="text-sm text-gray-500">
          시그널 매칭: {signals.filter(signal => getSignalPosition(signal)).length}/{signals.length}
        </div>
      </div>

      {/* 차트 */}
      <div className="relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 rounded-lg z-10">
            <div className="flex items-center gap-2 text-gray-500">
              <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
              <span>차트 {cacheUsed ? '캐시 로딩' : '데이터 로딩'} 중...</span>
            </div>
          </div>
        )}
        
        {error && (
          <div className="absolute top-2 left-2 bg-yellow-100 text-yellow-800 px-3 py-1 rounded-lg text-sm z-10">
            ⚠️ {error} (더미 데이터 표시)
          </div>
        )}

        <canvas 
          ref={chartRef}
          className="w-full h-80 border border-gray-200 rounded-lg"
          style={{ width: '100%', height: '320px' }}
        />

        {/* 시그널 상세 정보 (오버레이) */}
        {signals.length > 0 && (
          <div className="absolute bottom-2 right-2 bg-white/90 backdrop-blur-sm rounded-lg p-3 text-xs">
            <div className="grid grid-cols-2 gap-2 max-w-48">
              {signals.slice(0, 4).map((signal, index) => {
                const normalizedSignal = normalizeSignal(signal.signal_type || signal.signal || signal.direction);
                const color = SIGNAL_COLORS[normalizedSignal] || '#6b7280';
                return (
                  <div key={index} className="flex items-center gap-1">
                    <div 
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: color }}
                    ></div>
                    <span className="truncate">{signal.speaker || 'Unknown'}</span>
                  </div>
                );
              })}
              {signals.length > 4 && (
                <div className="text-gray-400 col-span-2">
                  +{signals.length - 4}개 더
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 통계 */}
      <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-100">
        <div className="text-center">
          <div className="text-sm text-gray-500">시그널 수</div>
          <div className="font-bold text-gray-900">{signals.length}개</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-500">매칭됨</div>
          <div className="font-bold text-gray-900">
            {signals.filter(signal => getSignalPosition(signal)).length}개
          </div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-500">기간</div>
          <div className="font-bold text-gray-900">{CHART_PERIODS.find(p => p.id === selectedPeriod)?.label}</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-500">캐시 상태</div>
          <div className={`font-bold ${cacheUsed ? 'text-green-600' : 'text-gray-900'}`}>
            {cacheUsed ? '캐시됨' : '실시간'}
          </div>
        </div>
      </div>
    </div>
  );
}