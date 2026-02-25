import { MemoData } from '@/data/memoData';

interface MemoCardProps {
  memo: MemoData;
  onClick: (memo: MemoData) => void;
}

export default function MemoCard({ memo, onClick }: MemoCardProps) {
  const getColorBar = (tag: string) => {
    switch (tag) {
      case 'Îß§ÏàòÍ∑ºÍ±∞': return 'border-l-green-500';
      case 'Îß§ÎèÑÍ∑ºÍ±∞': return 'border-l-red-500';
      case 'Í¥ÄÏ∞?: return 'border-l-yellow-500';
      case 'AI?ºÏ?': return 'border-l-blue-500';
      default: return 'border-l-gray-300';
    }
  };

  const getAttachmentIcon = (type: string) => {
    switch (type) {
      case 'Í≥µÏãú': return '?ìã';
      case '?†ÎÑêÎ¶¨Ìè¨??: return '?éØ';
      case '?∏ÌîåÎ£®Ïñ∏?úÏΩú': return '?ë§';
      default: return '?ìÑ';
    }
  };

  const truncateContent = (content: string, maxLength: number = 120) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  return (
    <div
      onClick={() => onClick(memo)}
      className={`border-l-4 ${getColorBar(memo.tag)} ${
        memo.isAI ? 'bg-[#f0f4ff]' : 'bg-white'
      } rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-[#f0f0f0] p-4 cursor-pointer hover:shadow-md transition-shadow`}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          {memo.stock && (
            <span className="bg-[#f2f4f6] text-gray-700 px-3 py-1 rounded-full text-sm font-medium">
              {memo.stock}
            </span>
          )}
          {memo.isAI && (
            <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-medium">
              ?êÎèô ?ùÏÑ±
            </span>
          )}
        </div>
        <span className="text-[#8b95a1] text-sm">{memo.date}</span>
      </div>

      <h3 className="font-bold text-[#191f28] mb-2 line-clamp-1">{memo.title}</h3>
      
      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
        {truncateContent(memo.content)}
      </p>

      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="bg-[#f2f4f6] text-gray-700 px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1">
            {memo.tagIcon} {memo.tag}
          </span>
          
          {memo.attachments.length > 0 && (
            <div className="flex gap-1">
              {memo.attachments.map((attachment, index) => (
                <span
                  key={index}
                  className="bg-blue-50 text-blue-600 px-2 py-1 rounded text-xs font-medium"
                  title={attachment.label}
                >
                  {getAttachmentIcon(attachment.type)}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}