import { CallRecord } from '@/data/influencerData';

interface CallHistoryItemProps {
  call: CallRecord;
}

export default function CallHistoryItem({ call }: CallHistoryItemProps) {
  const isPositive = call.returnRate > 0;
  const statusIcon = isPositive || call.status === '?ì¤‘' ? '?Ÿ¢' : '?”´';
  
  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'ì§„í–‰ì¤?: return 'bg-blue-500 text-white';
      case '?ì¤‘': return 'bg-green-500 text-white';
      case '?ì ˆ': return 'bg-red-500 text-white';
      default: return 'bg-[#f2f4f6]0 text-white';
    }
  };

  const getDirectionBadgeColor = (direction: string) => {
    return direction === 'ë§¤ìˆ˜' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700';
  };

  return (
    <div className="flex items-center justify-between py-2 px-3 hover:bg-[#f2f4f6] transition-colors">
      <div className="flex items-center gap-2 flex-1">
        <span className="text-lg">{statusIcon}</span>
        <div className="flex-1">
          <span className="font-medium text-[#191f28]">{call.stock}</span>
          <span className="text-sm text-[#8b95a1] ml-2">{call.date}</span>
        </div>
        <span 
          className={`px-2 py-1 rounded-full text-xs font-medium ${getDirectionBadgeColor(call.direction)}`}
        >
          {call.direction}
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        <span 
          className={`font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}
        >
          {isPositive ? '+' : ''}{call.returnRate}%
        </span>
        <span 
          className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadgeColor(call.status)}`}
        >
          {call.status}
        </span>
      </div>
    </div>
  );
}