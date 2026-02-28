'use client';

interface FeedCardProps {
  icon: string;
  categoryName: string;
  title: string;
  date: string;       // 실제 날짜 문자열 (예: "2월 23일")
  signal?: string;
  commentCount?: number;
  likeCount?: number;
  onClick?: () => void;
}

export default function FeedCard({
  icon,
  categoryName,
  title,
  date,
  signal,
  commentCount,
  likeCount,
  onClick,
}: FeedCardProps) {
  const getSignalStyle = (sig: string) => {
    switch (sig) {
      case '매수': case 'BUY': return 'text-green-600 bg-green-50';
      case '긍정': case 'POSITIVE': return 'text-blue-600 bg-blue-50';
      case '중립': case 'NEUTRAL': return 'text-yellow-600 bg-yellow-50';
      case '경계': case 'CONCERN': return 'text-orange-600 bg-orange-50';
      case '매도': case 'SELL': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
      <div
        onClick={onClick}
        className="px-4 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg flex-shrink-0">
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-[#8b95a1] bg-[#f2f4f6] px-2 py-0.5 rounded">
                {categoryName}
              </span>
              {signal && (
                <span className={`text-xs font-medium px-2 py-0.5 rounded ${getSignalStyle(signal)}`}>
                  {signal}
                </span>
              )}
            </div>
            <h3 className="text-[15px] font-medium text-[#191f28] leading-[1.4] mb-1">
              {title}
            </h3>
            <span className="text-sm text-[#8b95a1]">{date}</span>
          </div>
          <div className="text-[#8b95a1] text-sm">→</div>
        </div>
      </div>

      {/* Comment/Like Stats */}
      <div className="border-t border-[#f0f0f0] px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#8b95a1]">
            💬 댓글 {commentCount ?? Math.floor(Math.random() * 10) + 1}개
          </span>
          <span className="text-xs text-[#8b95a1]">•</span>
          <span className="text-xs text-[#8b95a1]">
            ❤️ 좋아요 {likeCount ?? Math.floor(Math.random() * 50) + 5}개
          </span>
        </div>
      </div>
    </div>
  );
}
