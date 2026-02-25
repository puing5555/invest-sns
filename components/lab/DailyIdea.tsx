import { dailyIdeas } from '@/data/labData';

interface DailyIdeaProps {
  onBack: () => void;
}

export default function DailyIdea({ onBack }: DailyIdeaProps) {
  const today = new Date().toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

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
        <h1 className="text-2xl font-bold text-[#191f28]">?¥Ïùº???®Ì? ?ÑÏù¥?îÏñ¥</h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 mb-6">
          <div className="flex items-center space-x-2">
            <span className="text-blue-600">?ìä</span>
            <div>
              <p className="text-sm text-blue-800">
                Îß§Ïùº ??ÎßàÍ∞ê ??AIÍ∞Ä ?¥Ïùº???®Ì? ?ÑÎ≥¥Î•?Î∂ÑÏÑù?©Îãà??
              </p>
              <p className="text-xs text-blue-600 mt-1">{today} ?ÖÎç∞?¥Ìä∏</p>
            </div>
          </div>
        </div>

        {/* Ideas Grid */}
        <div className="space-y-6">
          {dailyIdeas.map((idea) => (
            <div key={idea.id} className="bg-white border border-gray-200 rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
              {/* Stock Name */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-[#191f28]">{idea.stockName}</h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-[#8b95a1]">?πÎ•†</span>
                  <span className="font-bold text-green-600">{idea.winRate}%</span>
                  <span className="text-xs text-[#8b95a1]">({idea.successCount}/{idea.totalTrades})</span>
                </div>
              </div>

              {/* Idea Text */}
              <p className="text-gray-700 mb-4 leading-relaxed">{idea.idea}</p>

              {/* Price Info */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-xs text-[#8b95a1] mb-1">ÏßÑÏûÖÍ∞Ä</p>
                  <p className="font-bold text-[#191f28]">{idea.entry.toLocaleString()}??/p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-[#8b95a1] mb-1">Î™©ÌëúÍ∞Ä</p>
                  <p className="font-bold text-green-600">
                    {idea.target.toLocaleString()}??
                    <span className="text-xs ml-1">(+{idea.targetPercent}%)</span>
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-[#8b95a1] mb-1">?êÏ†àÍ∞Ä</p>
                  <p className="font-bold text-red-600">
                    {idea.stop.toLocaleString()}??
                    <span className="text-xs ml-1">({idea.stopPercent}%)</span>
                  </p>
                </div>
              </div>

              {/* Success/Fail Bar */}
              <div className="mb-4">
                <div className="flex items-center justify-between text-xs text-[#8b95a1] mb-1">
                  <span>Í≥ºÍ±∞ ?±Í≥º</span>
                  <span>{idea.successCount}??{idea.totalTrades - idea.successCount}??/span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${(idea.successCount / idea.totalTrades) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                {idea.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-[#f2f4f6] text-gray-700 text-xs rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-2xl hover:bg-blue-700">
                  ?ÅÏÑ∏Î∂ÑÏÑù
                </button>
                <button className="px-4 py-2 bg-[#f2f4f6] text-gray-700 text-sm rounded-2xl hover:bg-gray-200">
                  Í¥Ä?¨Ï¢ÖÎ™©Ï∂îÍ∞Ä
                </button>
                <button className="px-4 py-2 bg-[#f2f4f6] text-gray-700 text-sm rounded-2xl hover:bg-gray-200">
                  Í≥µÏú†
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}