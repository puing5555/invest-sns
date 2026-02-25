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
          className="text-gray-600 hover:text-gray-900 mb-2 flex items-center space-x-1"
        >
          <span>←</span>
          <span>전략연구실</span>
        </button>
        <h1 className="text-2xl font-bold text-gray-900">내일의 단타 아이디어</h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center space-x-2">
            <span className="text-blue-600">📊</span>
            <div>
              <p className="text-sm text-blue-800">
                매일 장 마감 후 AI가 내일의 단타 후보를 분석합니다.
              </p>
              <p className="text-xs text-blue-600 mt-1">{today} 업데이트</p>
            </div>
          </div>
        </div>

        {/* Ideas Grid */}
        <div className="space-y-6">
          {dailyIdeas.map((idea) => (
            <div key={idea.id} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              {/* Stock Name */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">{idea.stockName}</h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">승률</span>
                  <span className="font-bold text-green-600">{idea.winRate}%</span>
                  <span className="text-xs text-gray-500">({idea.successCount}/{idea.totalTrades})</span>
                </div>
              </div>

              {/* Idea Text */}
              <p className="text-gray-700 mb-4 leading-relaxed">{idea.idea}</p>

              {/* Price Info */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-xs text-gray-500 mb-1">진입가</p>
                  <p className="font-bold text-gray-900">{idea.entry.toLocaleString()}원</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-500 mb-1">목표가</p>
                  <p className="font-bold text-green-600">
                    {idea.target.toLocaleString()}원
                    <span className="text-xs ml-1">(+{idea.targetPercent}%)</span>
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-500 mb-1">손절가</p>
                  <p className="font-bold text-red-600">
                    {idea.stop.toLocaleString()}원
                    <span className="text-xs ml-1">({idea.stopPercent}%)</span>
                  </p>
                </div>
              </div>

              {/* Success/Fail Bar */}
              <div className="mb-4">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                  <span>과거 성과</span>
                  <span>{idea.successCount}승 {idea.totalTrades - idea.successCount}패</span>
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
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
                  상세분석
                </button>
                <button className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200">
                  관심종목추가
                </button>
                <button className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200">
                  공유
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}