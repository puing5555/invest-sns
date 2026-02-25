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
          className="text-gray-600 hover:text-[#191f28] mb-2 flex items-center space-x-1"
        >
          <span>??/span>
          <span>?„ëµ?°êµ¬??/span>
        </button>
        <h1 className="text-2xl font-bold text-[#191f28]">ê³µì‹œ ?„ëµ ë°±í…Œ?¤íŠ¸</h1>
      </div>

      <div className="max-w-6xl mx-auto p-6">
        {/* Title */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-[#191f28] mb-2">?˜ë§Œ???„ëµ??ë§Œë“¤ê³?ê²€ì¦í•˜?¸ìš”</h2>
          <p className="text-gray-600">ì¡°ê±´???¤ì •?˜ê³  ë°±í…Œ?¤íŠ¸ë¡??˜ìµë¥ ì„ ?•ì¸?´ë³´?¸ìš”</p>
        </div>

        {/* Strategy Builder */}
        <div className="bg-[#f2f4f6] rounded-2xl p-6 mb-8">
          <h3 className="text-lg font-bold text-[#191f28] mb-4">?„ëµ ?¤ì •</h3>
          
          <div className="space-y-4">
            {/* IF Conditions */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-medium text-gray-700">IF</span>
              <select className="px-3 py-2 border border-gray-300 rounded-2xl bg-white">
                <option>A?±ê¸‰ ê³µì‹œ</option>
              </select>
              <span className="text-[#8b95a1]">+</span>
              <select className="px-3 py-2 border border-gray-300 rounded-2xl bg-white">
                <option>?œì´ 1000???´í•˜</option>
              </select>
              <span className="text-[#8b95a1]">+</span>
              <select className="px-3 py-2 border border-gray-300 rounded-2xl bg-white">
                <option>ê±°ë˜???„ì¼?€ë¹?200%+</option>
              </select>
            </div>

            {/* THEN Actions */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-medium text-gray-700">THEN</span>
              <select className="px-3 py-2 border border-gray-300 rounded-2xl bg-white">
                <option>?¤ìŒ???œê? ë§¤ìˆ˜</option>
              </select>
              <span className="text-[#8b95a1]">??/span>
              <select className="px-3 py-2 border border-gray-300 rounded-2xl bg-white">
                <option>3????ë§¤ë„</option>
              </select>
            </div>

            {/* Add Condition Button */}
            <button className="px-4 py-2 border border-gray-300 rounded-2xl text-gray-600 hover:bg-[#f2f4f6]">
              + ì¡°ê±´ ì¶”ê?
            </button>

            {/* Run Backtest Button */}
            <button className="w-full px-6 py-3 bg-green-600 text-white rounded-2xl hover:bg-green-700 font-medium">
              ë°±í…Œ?¤íŠ¸ ?¤í–‰
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <h3 className="text-lg font-bold text-[#191f28] mb-6">ë°±í…Œ?¤íŠ¸ ê²°ê³¼</h3>
          
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-[#191f28]">{result.totalTrades}ê±?/p>
              <p className="text-xs text-[#8b95a1]">ì´?ê±°ë˜</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{result.winRate}%</p>
              <p className="text-xs text-[#8b95a1]">?¹ë¥ </p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">+{result.avgReturn}%</p>
              <p className="text-xs text-[#8b95a1]">?‰ê· ?˜ìµ</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">+{result.cumulativeReturn}%</p>
              <p className="text-xs text-[#8b95a1]">?„ì ?˜ìµ</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <p className="text-lg font-bold text-green-600">+{result.maxReturn}%</p>
              <p className="text-xs text-[#8b95a1]">ìµœë??˜ìµ</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-red-600">{result.maxLoss}%</p>
              <p className="text-xs text-[#8b95a1]">ìµœë??ì‹¤</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-[#191f28]">{result.sharpe}</p>
              <p className="text-xs text-[#8b95a1]">?¤í”„ ì§€??/p>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="bg-[#f2f4f6] rounded-2xl p-4 mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-4">?˜ìµë¥?ê³¡ì„ </h4>
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
            <h4 className="text-sm font-medium text-gray-700 mb-3">?¸ê¸° ?„ëµ ?œí”Œë¦?/h4>
            <div className="flex flex-wrap gap-2">
              {presetStrategies.map((strategy, index) => (
                <button
                  key={index}
                  className="px-3 py-2 border border-gray-300 rounded-2xl text-sm hover:bg-[#f2f4f6]"
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