import { longTermIdeas } from '@/data/labData';

interface LongTermIdeaProps {
  onBack: () => void;
}

export default function LongTermIdea({ onBack }: LongTermIdeaProps) {
  const aiReports = longTermIdeas.filter(idea => idea.type === 'ai-report');
  const communityPosts = longTermIdeas.filter(idea => idea.type === 'community');

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
        <h1 className="text-2xl font-bold text-[#191f28]">?•Í∏∞?¨Ïûê ?ÑÏù¥?îÏñ¥</h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Description */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-[#191f28] mb-2">?•Í∏∞ ?¨Ïûê ?∏ÏÇ¨?¥Ìä∏</h2>
          <p className="text-gray-600">AI Î¶¨Ìè¨?∏Ï? ?ÑÎ¨∏Í∞Ä?§Ïùò ?•Í∏∞ ?¨Ïûê ?ÑÏù¥?îÏñ¥</p>
        </div>

        {/* AI Reports */}
        <div className="mb-8">
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold text-[#191f28]">?§ñ AI Î¶¨Ìè¨??/h3>
            <span className="px-2 py-1 bg-purple-100 text-purple-600 text-xs rounded-full">Îß§Ï£º ?ÖÎç∞?¥Ìä∏</span>
          </div>
          
          <div className="space-y-4">
            {aiReports.map((report) => (
              <div key={report.id} className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-2xl p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-lg font-bold text-[#191f28] mb-2">{report.title}</h4>
                    <p className="text-gray-700 mb-3">{report.description}</p>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                      <span className="flex items-center space-x-1">
                        <span>??/span>
                        <span>{report.readTime}Î∂??ΩÍ∏∞</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <span>??</span>
                        <span>{report.views?.toLocaleString()} Ï°∞Ìöå</span>
                      </span>
                    </div>

                    {/* Related Stocks */}
                    {report.relatedStocks && (
                      <div className="mb-4">
                        <p className="text-sm text-gray-600 mb-2">Í¥Ä??Ï¢ÖÎ™©:</p>
                        <div className="flex flex-wrap gap-2">
                          {report.relatedStocks.map((stock, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full"
                            >
                              {stock}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="ml-4">
                    <span className="px-3 py-1 bg-purple-600 text-white text-sm rounded-full">
                      AI Î¶¨Ìè¨??
                    </span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="px-4 py-2 bg-purple-600 text-white text-sm rounded-2xl hover:bg-purple-700">
                    ?ÑÏ≤¥ Î¶¨Ìè¨???ΩÍ∏∞
                  </button>
                  <button className="px-4 py-2 bg-purple-100 text-purple-600 text-sm rounded-2xl hover:bg-purple-200">
                    ?îÏïΩÎ≥?Î≥¥Í∏∞
                  </button>
                  <button className="px-4 py-2 bg-[#f2f4f6] text-gray-600 text-sm rounded-2xl hover:bg-gray-200">
                    Î∂ÅÎßà??
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Community Posts */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold text-[#191f28]">?ë• Ïª§Î??àÌã∞ ?∏Í∏∞Í∏Ä</h3>
            <span className="px-2 py-1 bg-indigo-100 text-indigo-600 text-xs rounded-full">?êÎîî???êÎ†à?¥ÏÖò</span>
          </div>
          
          <div className="space-y-4">
            {communityPosts.map((post) => (
              <div key={post.id} className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="text-lg font-bold text-[#191f28]">{post.title}</h4>
                      {post.isEditorPick && (
                        <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full flex items-center space-x-1">
                          <span>‚≠?/span>
                          <span>?êÎîî?∞Ï∂îÏ≤?/span>
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 mb-3">{post.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-[#8b95a1]">
                      <span>by {post.author}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <div className="flex space-x-4 text-sm text-[#8b95a1]">
                    <span className="flex items-center space-x-1">
                      <span>?ëç</span>
                      <span>{post.likes}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <span>?í¨</span>
                      <span>{post.comments}</span>
                    </span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 bg-[#f2f4f6] text-gray-600 text-sm rounded-2xl hover:bg-gray-200">
                      ?ÑÏ≤¥ Í∏Ä Î≥¥Í∏∞
                    </button>
                    <button className="px-3 py-1 bg-indigo-100 text-indigo-600 text-sm rounded-2xl hover:bg-indigo-200">
                      Í¥Ä?¨Ï¢ÖÎ™?Ï∂îÍ?
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* More Ideas Button */}
        <div className="text-center mt-8">
          <button className="px-8 py-4 bg-indigo-100 text-indigo-600 rounded-2xl hover:bg-indigo-200 font-medium">
            ??ÎßéÏ? ?ÑÏù¥?îÏñ¥ Î≥¥Í∏∞
          </button>
        </div>
      </div>
    </div>
  );
}