import { swingIdeas } from '@/data/labData';

interface SwingLabProps {
  onBack: () => void;
}

export default function SwingLab({ onBack }: SwingLabProps) {
  const aiIdeas = swingIdeas.filter(idea => idea.type === 'ai');
  const communityIdeas = swingIdeas.filter(idea => idea.type === 'community');

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
        <h1 className="text-2xl font-bold text-[#191f28]">?§Ïúô ?∞Íµ¨??/h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Description */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-[#191f28] mb-2">Ï§ëÏû•Í∏??§Ïúô ?ÑÏù¥?îÏñ¥</h2>
          <p className="text-gray-600">AI Î∂ÑÏÑùÍ≥?Ïª§Î??àÌã∞ ?∏ÏÇ¨?¥Ìä∏Î•??µÌïú ?§Ïúô ?¨Ïûê ?ÑÏù¥?îÏñ¥</p>
        </div>

        {/* AI Recommendations */}
        <div className="mb-8">
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold text-[#191f28]">?§ñ AI Ï∂îÏ≤ú</h3>
            <span className="px-2 py-1 bg-blue-100 text-blue-600 text-xs rounded-full">?§ÏãúÍ∞?Î∂ÑÏÑù</span>
          </div>
          
          <div className="space-y-4">
            {aiIdeas.map((idea) => (
              <div key={idea.id} className="bg-blue-50 border border-blue-200 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-bold text-[#191f28]">{idea.stockName}</h4>
                  <span className="px-3 py-1 bg-blue-600 text-white text-sm rounded-full">
                    AI Ï∂îÏ≤ú
                  </span>
                </div>
                
                <p className="text-gray-700 mb-4">{idea.description}</p>
                
                {/* Price Targets */}
                {idea.entry && idea.target && idea.stop && (
                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <p className="text-xs text-[#8b95a1] mb-1">ÏßÑÏûÖÍ∞Ä</p>
                      <p className="font-bold text-[#191f28]">{idea.entry.toLocaleString()}??/p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-[#8b95a1] mb-1">Î™©ÌëúÍ∞Ä</p>
                      <p className="font-bold text-green-600">{idea.target.toLocaleString()}??/p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-[#8b95a1] mb-1">?êÏ†àÍ∞Ä</p>
                      <p className="font-bold text-red-600">{idea.stop.toLocaleString()}??/p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-[#8b95a1] mb-1">Í∏∞Í∞Ñ</p>
                      <p className="font-bold text-[#191f28]">{idea.timeframe}</p>
                    </div>
                  </div>
                )}
                
                <div className="flex space-x-2">
                  <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-2xl hover:bg-blue-700">
                    ?ÅÏÑ∏ Î∂ÑÏÑù
                  </button>
                  <button className="px-4 py-2 bg-blue-100 text-blue-600 text-sm rounded-2xl hover:bg-blue-200">
                    Í¥Ä?¨Ï¢ÖÎ™?Ï∂îÍ?
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Community Ideas */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold text-[#191f28]">?ë• Ïª§Î??àÌã∞ ?∏Í∏∞</h3>
            <span className="px-2 py-1 bg-teal-100 text-teal-600 text-xs rounded-full">?§ÏãúÍ∞??ÖÎç∞?¥Ìä∏</span>
          </div>
          
          <div className="space-y-4">
            {communityIdeas.map((idea) => (
              <div key={idea.id} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="text-lg font-bold text-[#191f28]">{idea.stockName}</h4>
                      <span className="px-2 py-1 bg-[#f2f4f6] text-gray-600 text-xs rounded-full">
                        ?§Ïúô
                      </span>
                    </div>
                    <p className="text-gray-700 mb-2">{idea.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-[#8b95a1]">
                      <span>by {idea.author}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <div className="flex space-x-4 text-sm text-[#8b95a1]">
                    <span className="flex items-center space-x-1">
                      <span>?ëç</span>
                      <span>{idea.likes}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <span>?í¨</span>
                      <span>{idea.comments}</span>
                    </span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 bg-[#f2f4f6] text-gray-600 text-sm rounded-2xl hover:bg-gray-200">
                      ?ìÍ? Î≥¥Í∏∞
                    </button>
                    <button className="px-3 py-1 bg-teal-100 text-teal-600 text-sm rounded-2xl hover:bg-teal-200">
                      ?∞Îùº?òÍ∏∞
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* More Ideas Button */}
        <div className="text-center mt-8">
          <button className="px-8 py-4 bg-teal-100 text-teal-600 rounded-2xl hover:bg-teal-200 font-medium">
            ??ÎßéÏ? ?ÑÏù¥?îÏñ¥ Î≥¥Í∏∞
          </button>
        </div>
      </div>
    </div>
  );
}