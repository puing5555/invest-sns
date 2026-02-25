import { WatchlistStock } from '@/data/watchlistData';
import SignalBadge from './SignalBadge';

interface WatchlistCardProps {
  stock: WatchlistStock;
  onMemoClick: (stock: WatchlistStock) => void;
  onRemove: (stockId: string) => void;
}

export default function WatchlistCard({ stock, onMemoClick, onRemove }: WatchlistCardProps) {
  const getLeftBorderColor = () => {
    if (stock.buyPrice === null) return 'border-l-gray-300';
    if (stock.profitRate && stock.profitRate > 0) return 'border-l-[#22c55e]';
    if (stock.profitRate && stock.profitRate < 0) return 'border-l-[#ef4444]';
    return 'border-l-gray-300';
  };

  const getPriceChangeColor = () => {
    return stock.changePercent >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]';
  };

  const formatNumber = (num: number) => {
    return num.toLocaleString('ko-KR');
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-[#eff3f4] ${getLeftBorderColor()} border-l-4 p-4 hover:shadow-md transition-shadow`}>
      <div className="flex justify-between">
        {/* Left Section */}
        <div className="flex-1">
          {/* Stock Name and Price */}
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-lg">{stock.name}</h3>
            <div className="text-right">
              <div className="font-bold text-lg">{formatNumber(stock.currentPrice)}원</div>
              <div className={`text-sm ${getPriceChangeColor()}`}>
                {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent}%
              </div>
            </div>
          </div>

          {/* Buy Price and Profit */}
          <div className="mb-3">
            {stock.buyPrice ? (
              <div className="text-sm text-gray-600">
                내 매수가: {formatNumber(stock.buyPrice)}원 | 
                <span className={stock.profitRate && stock.profitRate >= 0 ? 'text-[#22c55e]' : 'text-[#ef4444]'}>
                  {' '}{stock.profitRate && stock.profitRate >= 0 ? '+' : ''}{stock.profitRate}%
                </span>
              </div>
            ) : (
              <button className="px-3 py-1 text-xs bg-gray-100 rounded-lg text-gray-600 hover:bg-gray-200"
                      onClick={() => onMemoClick(stock)}>
                매수가 입력
              </button>
            )}
          </div>

          {/* Signal Badges */}
          <div className="flex flex-wrap gap-1 mb-3">
            {stock.badges.map((badge, index) => (
              <SignalBadge key={index} icon={badge.icon} label={badge.label} />
            ))}
          </div>

          {/* Recent Alert */}
          <div className="text-sm text-gray-600 mb-2">
            📢 {stock.alert.message} <span className="text-xs text-gray-400">{stock.alert.timeAgo}</span>
          </div>

          {/* Memo Preview */}
          {stock.memo && (
            <div className="bg-[#f5f5f5] rounded-lg p-2 text-sm italic text-gray-600 flex items-center gap-2">
              <span>✏️</span>
              <span>{stock.memo}</span>
            </div>
          )}
        </div>

        {/* Right Action Icons */}
        <div className="flex flex-col gap-2 ml-4">
          <button 
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-gray-700"
            onClick={() => onMemoClick(stock)}
            title="메모"
          >
            📝
          </button>
          <button 
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-gray-700"
            title="알림"
          >
            🔔
          </button>
          <button 
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-red-500"
            onClick={() => onRemove(stock.id)}
            title="제거"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}