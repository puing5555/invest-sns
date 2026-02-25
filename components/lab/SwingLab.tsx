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
          className="text-gray-600 hover:text-gray-900 mb-2 flex items-center space-x-1"
        >
          <span>←</span>
          <span>전략연구실</span>
        </button>
        <h1 className="text-2xl font-bold text-gray-900">스윙 연구소</h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Description */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-2">중장기 스윙 아이디어</h2>
          <p className="text-gray-600">AI 분석과 커뮤니티 인사이트를 통한 스윙 투자 아이디어</p>
        </div>

        {/* AI Recommendations */}
        <div className="mb-8">
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold text-gray-900">🤖 AI 추천</h3>
            <span className="px-2 py-1 bg-blue-100 text-blue-600 text-xs rounded-full">실시간 분석</span>
          </div>
          
          <div className="space-y-4">
            {aiIdeas.map((idea) => (
              <div key={idea.id} className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-bold text-gray-900">{idea.stockName}</h4>
                  <span className="px-3 py-1 bg-blue-600 text-white text-sm rounded-full">
                    AI 추천
                  </span>
                </div>
                
                <p className="text-gray-700 mb-4">{idea.description}</p>
                
                {/* Price Targets */}
                {idea.entry && idea.target && idea.stop && (
                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <p className="text-xs text-gray-500 mb-1">진입가</p>
                      <p className="font-bold text-gray-900">{idea.entry.toLocaleString()}원</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-gray-500 mb-1">목표가</p>
                      <p className="font-bold text-green-600">{idea.target.toLocaleString()}원</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-gray-500 mb-1">손절가</p>
                      <p className="font-bold text-red-600">{idea.stop.toLocaleString()}원</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-gray-500 mb-1">기간</p>
                      <p className="font-bold text-gray-900">{idea.timeframe}</p>
                    </div>
                  </div>
                )}
                
                <div className="flex space-x-2">
                  <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
                    상세 분석
                  </button>
                  <button className="px-4 py-2 bg-blue-100 text-blue-600 text-sm rounded-lg hover:bg-blue-200">
                    관심종목 추가
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Community Ideas */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold text-gray-900">👥 커뮤니티 인기</h3>
            <span className="px-2 py-1 bg-teal-100 text-teal-600 text-xs rounded-full">실시간 업데이트</span>
          </div>
          
          <div className="space-y-4">
            {communityIdeas.map((idea) => (
              <div key={idea.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-sm">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="text-lg font-bold text-gray-900">{idea.stockName}</h4>
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                        스윙
                      </span>
                    </div>
                    <p className="text-gray-700 mb-2">{idea.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>by {idea.author}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <div className="flex space-x-4 text-sm text-gray-500">
                    <span className="flex items-center space-x-1">
                      <span>👍</span>
                      <span>{idea.likes}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <span>💬</span>
                      <span>{idea.comments}</span>
                    </span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-lg hover:bg-gray-200">
                      댓글 보기
                    </button>
                    <button className="px-3 py-1 bg-teal-100 text-teal-600 text-sm rounded-lg hover:bg-teal-200">
                      따라하기
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* More Ideas Button */}
        <div className="text-center mt-8">
          <button className="px-8 py-4 bg-teal-100 text-teal-600 rounded-lg hover:bg-teal-200 font-medium">
            더 많은 아이디어 보기
          </button>
        </div>
      </div>
    </div>
  );
}