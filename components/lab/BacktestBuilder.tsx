import { backtestResults, presetStrategies } from '@/data/labData';

interface BacktestBuilderProps {
  onBack: () => void;
}

export default function BacktestBuilder({ onBack }: BacktestBuilderProps) {
  const result = backtestResults[0];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <button
          onClick={onBack}
          className="text-gray-600 hover:text-gray-900 mb-2 flex items-center space-x-1"
        >
          <span>←</span>
          <span>전략연구실</span>
        </button>
        <h1 className="text-2xl font-bold text-gray-900">공시 전략 백테스트</h1>
      </div>

      <div className="max-w-6xl mx-auto p-6">
        {/* Title */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-2">나만의 전략을 만들고 검증하세요</h2>
          <p className="text-gray-600">조건을 설정하고 백테스트로 수익률을 확인해보세요</p>
        </div>

        {/* Strategy Builder */}
        <div className="bg-gray-50 rounded-xl p-6 mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">전략 설정</h3>
          
          <div className="space-y-4">
            {/* IF Conditions */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-medium text-gray-700">IF</span>
              <select className="px-3 py-2 border border-gray-300 rounded-lg bg-white">
                <option>A등급 공시</option>
              </select>
              <span className="text-gray-500">+</span>
              <select className="px-3 py-2 border border-gray-300 rounded-lg bg-white">
                <option>시총 1000억 이하</option>
              </select>
              <span className="text-gray-500">+</span>
              <select className="px-3 py-2 border border-gray-300 rounded-lg bg-white">
                <option>거래량 전일대비 200%+</option>
              </select>
            </div>

            {/* THEN Actions */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-medium text-gray-700">THEN</span>
              <select className="px-3 py-2 border border-gray-300 rounded-lg bg-white">
                <option>다음날 시가 매수</option>
              </select>
              <span className="text-gray-500">→</span>
              <select className="px-3 py-2 border border-gray-300 rounded-lg bg-white">
                <option>3일 후 매도</option>
              </select>
            </div>

            {/* Add Condition Button */}
            <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-100">
              + 조건 추가
            </button>

            {/* Run Backtest Button */}
            <button className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium">
              백테스트 실행
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-6">백테스트 결과</h3>
          
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{result.totalTrades}건</p>
              <p className="text-xs text-gray-500">총 거래</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{result.winRate}%</p>
              <p className="text-xs text-gray-500">승률</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">+{result.avgReturn}%</p>
              <p className="text-xs text-gray-500">평균수익</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">+{result.cumulativeReturn}%</p>
              <p className="text-xs text-gray-500">누적수익</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <p className="text-lg font-bold text-green-600">+{result.maxReturn}%</p>
              <p className="text-xs text-gray-500">최대수익</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-red-600">{result.maxLoss}%</p>
              <p className="text-xs text-gray-500">최대손실</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-gray-900">{result.sharpe}</p>
              <p className="text-xs text-gray-500">샤프 지수</p>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-4">수익률 곡선</h4>
            <div className="h-32 w-full">
              <svg viewBox="0 0 400 100" className="w-full h-full">
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#10B981" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
                  </linearGradient>
                </defs>
                
                {/* Grid lines */}
                <defs>
                  <pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#E5E7EB" strokeWidth="0.5"/>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
                
                {/* Equity curve */}
                <polyline
                  fill="url(#gradient)"
                  stroke="#10B981"
                  strokeWidth="2"
                  points={result.equityPoints.map((point, index) => 
                    `${(index / (result.equityPoints.length - 1)) * 400},${100 - ((point.y - 100) / 100) * 80}`
                  ).join(' ')}
                />
              </svg>
            </div>
          </div>

          {/* Preset Strategies */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">인기 전략 템플릿</h4>
            <div className="flex flex-wrap gap-2">
              {presetStrategies.map((strategy, index) => (
                <button
                  key={index}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-100"
                >
                  {strategy.name} ({strategy.winRate}%)
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}