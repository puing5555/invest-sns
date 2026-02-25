import { influencerSimulations } from '@/data/labData';

interface InfluencerSimProps {
  onBack: () => void;
}

export default function InfluencerSim({ onBack }: InfluencerSimProps) {
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
        <h1 className="text-2xl font-bold text-gray-900">인플루언서 전략 시뮬레이션</h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Description */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-2">인기 투자 인플루언서를 따라해보세요</h2>
          <p className="text-gray-600">실제 매매 내역을 바탕으로 한 시뮬레이션 결과입니다</p>
        </div>

        {/* Simulation Cards */}
        <div className="space-y-6">
          {influencerSimulations.map((sim) => (
            <div key={sim.id} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👤</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{sim.name}</h3>
                    <p className="text-sm text-gray-600">{sim.duration} 시뮬레이션</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">+{sim.returnPercent}%</p>
                  <p className="text-xs text-gray-500">총 수익률</p>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <p className="text-lg font-bold text-gray-900">
                    {(sim.initialAmount / 100000000).toFixed(1)}억
                  </p>
                  <p className="text-xs text-gray-500">시작 자금</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-green-600">
                    {(sim.currentAmount / 100000000).toFixed(3)}억
                  </p>
                  <p className="text-xs text-gray-500">현재 자산</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-blue-600">{sim.winRate}%</p>
                  <p className="text-xs text-gray-500">승률</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-gray-900">{sim.totalTrades}건</p>
                  <p className="text-xs text-gray-500">총 거래</p>
                </div>
              </div>

              {/* Sparkline Chart */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">수익률 추이</h4>
                <div className="h-16 w-full bg-gray-50 rounded-lg p-3">
                  <svg viewBox="0 0 300 40" className="w-full h-full">
                    <polyline
                      fill="none"
                      stroke="#10B981"
                      strokeWidth="2"
                      points={sim.sparklinePoints.map((point, index) => 
                        `${(index / (sim.sparklinePoints.length - 1)) * 300},${40 - ((point - 100) / 150) * 40}`
                      ).join(' ')}
                    />
                    {/* Current value dot */}
                    <circle
                      cx={300}
                      cy={40 - ((sim.sparklinePoints[sim.sparklinePoints.length - 1] - 100) / 150) * 40}
                      r="3"
                      fill="#10B981"
                    />
                  </svg>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <button className="px-4 py-2 bg-orange-600 text-white text-sm rounded-lg hover:bg-orange-700">
                  따라하기 시작
                </button>
                <button className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200">
                  상세 내역 보기
                </button>
                <button className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200">
                  알림 설정
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* More Influencers Button */}
        <div className="text-center mt-8">
          <button className="px-8 py-4 bg-orange-100 text-orange-600 rounded-lg hover:bg-orange-200 font-medium">
            더 많은 인플루언서 보기
          </button>
        </div>
      </div>
    </div>
  );
}