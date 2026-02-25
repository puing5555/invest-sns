import { NewsData } from '../data/newsData';
import SentimentBadge from './SentimentBadge';

interface NewsCardProps {
  news: NewsData;
  onClick: (news: NewsData) => void;
}

export default function NewsCard({ news, onClick }: NewsCardProps) {
  const getSentimentColor = () => {
    switch (news.sentiment) {
      case 'positive':
        return 'bg-[#22c55e]';
      case 'neutral':
        return 'bg-[#eab308]';
      case 'negative':
        return 'bg-[#ef4444]';
      default:
        return 'bg-gray-400';
    }
  };

  const urgentStyle = news.urgent 
    ? 'border-red-400 ring-1 ring-red-200' 
    : 'border-[#f0f0f0]';

  return (
    <div
      className={`relative bg-white rounded-xl shadow-sm border ${urgentStyle} hover:bg-gray-50 cursor-pointer transition-colors`}
      onClick={() => onClick(news)}
    >
      {/* Left sentiment color bar */}
      <div className={`absolute left-0 top-0 h-full w-1 rounded-l-xl ${getSentimentColor()}`} />
      
      <div className="pl-6 pr-4 py-4">
        {/* Urgent badge */}
        {news.urgent && (
          <div className="mb-2">
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700 border border-red-200">
              🔴 긴급
            </span>
          </div>
        )}

        {/* Title */}
        <h3 className="font-bold text-[15px] text-gray-900 mb-2 line-clamp-2">
          {news.title}
        </h3>

        {/* Source and time */}
        <div className="flex items-center text-xs text-gray-500 mb-3">
          <span>{news.source}</span>
          <span className="mx-1">•</span>
          <span>{news.time}</span>
        </div>

        {/* AI Analysis box */}
        <div className="bg-[#f5f6f8] rounded-lg p-2 mb-3">
          <p className="text-sm text-gray-700">
            <span className="mr-1">🤖</span>
            {news.aiAnalysis}
          </p>
        </div>

        {/* Related stock tags */}
        <div className="flex flex-wrap gap-1 mb-3">
          {news.relatedStocks.map((stock, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-[#3182f6] bg-[#f0fdf4] border border-green-200"
            >
              {stock}
            </span>
          ))}
        </div>

        {/* Action buttons */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex gap-4">
            <button className="flex items-center hover:text-gray-700 transition-colors">
              📌 저장 ({news.saves})
            </button>
            <button className="flex items-center hover:text-gray-700 transition-colors">
              💬 토론 ({news.comments})
            </button>
            <button className="flex items-center hover:text-gray-700 transition-colors">
              🔗 원문
            </button>
          </div>
          
          <SentimentBadge sentiment={news.sentiment} size="sm" />
        </div>
      </div>
    </div>
  );
}