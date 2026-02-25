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
          className="text-gray-600 hover:text-[#191f28] mb-2 flex items-center space-x-1"
        >
          <span>??/span>
          <span>?ÑÎûµ?∞Íµ¨??/span>
        </button>
        <h1 className="text-2xl font-bold text-[#191f28]">?∏ÌîåÎ£®Ïñ∏???ÑÎûµ ?úÎ??àÏù¥??/h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Description */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-[#191f28] mb-2">?∏Í∏∞ ?¨Ïûê ?∏ÌîåÎ£®Ïñ∏?úÎ? ?∞Îùº?¥Î≥¥?∏Ïöî</h2>
          <p className="text-gray-600">?§Ï†ú Îß§Îß§ ?¥Ïó≠??Î∞îÌÉï?ºÎ°ú ???úÎ??àÏù¥??Í≤∞Í≥º?ÖÎãà??/p>
        </div>

        {/* Simulation Cards */}
        <div className="space-y-6">
          {influencerSimulations.map((sim) => (
            <div key={sim.id} className="bg-white border border-gray-200 rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">?ë§</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-[#191f28]">{sim.name}</h3>
                    <p className="text-sm text-gray-600">{sim.duration} ?úÎ??àÏù¥??/p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">+{sim.returnPercent}%</p>
                  <p className="text-xs text-[#8b95a1]">Ï¥??òÏùµÎ•?/p>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <p className="text-lg font-bold text-[#191f28]">
                    {(sim.initialAmount / 100000000).toFixed(1)}??
                  </p>
                  <p className="text-xs text-[#8b95a1]">?úÏûë ?êÍ∏à</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-green-600">
                    {(sim.currentAmount / 100000000).toFixed(3)}??
                  </p>
                  <p className="text-xs text-[#8b95a1]">?ÑÏû¨ ?êÏÇ∞</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-blue-600">{sim.winRate}%</p>
                  <p className="text-xs text-[#8b95a1]">?πÎ•†</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-[#191f28]">{sim.totalTrades}Í±?/p>
                  <p className="text-xs text-[#8b95a1]">Ï¥?Í±∞Îûò</p>
                </div>
              </div>

              {/* Sparkline Chart */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">?òÏùµÎ•?Ï∂îÏù¥</h4>
                <div className="h-16 w-full bg-[#f2f4f6] rounded-2xl p-3">
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
                <button className="px-4 py-2 bg-orange-600 text-white text-sm rounded-2xl hover:bg-orange-700">
                  ?∞Îùº?òÍ∏∞ ?úÏûë
                </button>
                <button className="px-4 py-2 bg-[#f2f4f6] text-gray-700 text-sm rounded-2xl hover:bg-gray-200">
                  ?ÅÏÑ∏ ?¥Ïó≠ Î≥¥Í∏∞
                </button>
                <button className="px-4 py-2 bg-[#f2f4f6] text-gray-700 text-sm rounded-2xl hover:bg-gray-200">
                  ?åÎ¶º ?§Ï†ï
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* More Influencers Button */}
        <div className="text-center mt-8">
          <button className="px-8 py-4 bg-orange-100 text-orange-600 rounded-2xl hover:bg-orange-200 font-medium">
            ??ÎßéÏ? ?∏ÌîåÎ£®Ïñ∏??Î≥¥Í∏∞
          </button>
        </div>
      </div>
    </div>
  );
}