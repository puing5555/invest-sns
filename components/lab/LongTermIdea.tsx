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
          className="text-gray-600 hover:text-gray-900 mb-2 flex items-center space-x-1"
        >
          <span>←</span>
          <span>전략연구실</span>
        </button>
        <h1 className="text-2xl font-bold text-gray-900">장기투자 아이디어</h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Description */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-2">장기 투자 인사이트</h2>
          <p className="text-gray-600">AI 리포트와 전문가들의 장기 투자 아이디어</p>
        </div>

        {/* AI Reports */}
        <div className="mb-8">
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold text-gray-900">🤖 AI 리포트</h3>
            <span className="px-2 py-1 bg-purple-100 text-purple-600 text-xs rounded-full">매주 업데이트</span>
          </div>
          
          <div className="space-y-4">
            {aiReports.map((report) => (
              <div key={report.id} className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-xl p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-lg font-bold text-gray-900 mb-2">{report.title}</h4>
                    <p className="text-gray-700 mb-3">{report.description}</p>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                      <span className="flex items-center space-x-1">
                        <span>⏰</span>
                        <span>{report.readTime}분 읽기</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <span>👀</span>
                        <span>{report.views?.toLocaleString()} 조회</span>
                      </span>
                    </div>

                    {/* Related Stocks */}
                    {report.relatedStocks && (
                      <div className="mb-4">
                        <p className="text-sm text-gray-600 mb-2">관련 종목:</p>
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
                      AI 리포트
                    </span>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700">
                    전체 리포트 읽기
                  </button>
                  <button className="px-4 py-2 bg-purple-100 text-purple-600 text-sm rounded-lg hover:bg-purple-200">
                    요약본 보기
                  </button>
                  <button className="px-4 py-2 bg-gray-100 text-gray-600 text-sm rounded-lg hover:bg-gray-200">
                    북마크
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Community Posts */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold text-gray-900">👥 커뮤니티 인기글</h3>
            <span className="px-2 py-1 bg-indigo-100 text-indigo-600 text-xs rounded-full">에디터 큐레이션</span>
          </div>
          
          <div className="space-y-4">
            {communityPosts.map((post) => (
              <div key={post.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-sm">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="text-lg font-bold text-gray-900">{post.title}</h4>
                      {post.isEditorPick && (
                        <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full flex items-center space-x-1">
                          <span>⭐</span>
                          <span>에디터추천</span>
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 mb-3">{post.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>by {post.author}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <div className="flex space-x-4 text-sm text-gray-500">
                    <span className="flex items-center space-x-1">
                      <span>👍</span>
                      <span>{post.likes}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <span>💬</span>
                      <span>{post.comments}</span>
                    </span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-lg hover:bg-gray-200">
                      전체 글 보기
                    </button>
                    <button className="px-3 py-1 bg-indigo-100 text-indigo-600 text-sm rounded-lg hover:bg-indigo-200">
                      관심종목 추가
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* More Ideas Button */}
        <div className="text-center mt-8">
          <button className="px-8 py-4 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200 font-medium">
            더 많은 아이디어 보기
          </button>
        </div>
      </div>
    </div>
  );
}