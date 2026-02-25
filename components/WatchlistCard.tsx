import { WatchlistStock } from '@/data/watchlistData';
import { tradeHelperData } from '@/data/tradeData';
import SignalBadge from './SignalBadge';
import TradeHelper from './TradeHelper';

interface WatchlistCardProps {
  stock: WatchlistStock;
  onMemoClick: (stock: WatchlistStock) => void;
  onRemove: (stockId: string) => void;
  onAnalysisClick: (stockName: string) => void;
  onSetupClick: (stockName: string) => void;
}

export default function WatchlistCard({ stock, onMemoClick, onRemove, onAnalysisClick, onSetupClick }: WatchlistCardProps) {
  const tradeData = tradeHelperData[stock.name];
  
  const getCardBorderClass = () => {
    let borderClass = '';
    
    // Check for stop-loss/take-profit proximity
    if (stock.buyPrice && tradeData) {
      const isNearStopLoss = stock.currentPrice <= tradeData.stopLoss * 1.02; // Within 2%
      const isNearTakeProfit = tradeData.tp1 && stock.currentPrice >= tradeData.tp1 * 0.98; // Within 2%
      
      if (isNearStopLoss) {
        borderClass = 'border-red-400';
      } else if (isNearTakeProfit) {
        borderClass = 'border-green-400';
      } else {
        borderClass = 'border-[#f0f0f0]';
      }
    } else {
      borderClass = 'border-[#f0f0f0]';
    }
    
    return borderClass;
  };

  const getLeftBorderColor = () => {
    if (stock.buyPrice === null) return 'border-l-gray-300';
    if (stock.profitRate && stock.profitRate > 0) return 'border-l-[#22c55e]';
    if (stock.profitRate && stock.profitRate < 0) return 'border-l-[#ef4444]';
    return 'border-l-gray-300';
  };
  
  const getWarningIcon = () => {
    if (!stock.buyPrice || !tradeData) return null;
    
    const isNearStopLoss = stock.currentPrice <= tradeData.stopLoss * 1.02;
    const isNearTakeProfit = tradeData.tp1 && stock.currentPrice >= tradeData.tp1 * 0.98;
    
    if (isNearStopLoss) return '?†Ô∏è';
    if (isNearTakeProfit) return '?éâ';
    return null;
  };

  const getPriceChangeColor = () => {
    return stock.changePercent >= 0 ? 'text-[#00c853]' : 'text-[#f44336]';
  };

  const formatNumber = (num: number) => {
    return num.toLocaleString('ko-KR');
  };

  const warningIcon = getWarningIcon();

  return (
    <div className={`bg-white rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.04)] border ${getCardBorderClass()} ${getLeftBorderColor()} border-l-4 p-4 hover:shadow-md transition-shadow`}>
      <div className="flex justify-between">
        {/* Left Section */}
        <div className="flex-1">
          {/* Stock Name and Price */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-lg">{stock.name}</h3>
              {warningIcon && <span className="text-lg">{warningIcon}</span>}
            </div>
            <div className="text-right">
              <div className="font-bold text-lg">{formatNumber(stock.currentPrice)}??/div>
              <div className={`text-sm ${getPriceChangeColor()}`}>
                {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent}%
              </div>
            </div>
          </div>

          {/* Buy Price and Profit */}
          <div className="mb-3">
            {stock.buyPrice ? (
              <div className="text-sm text-gray-600">
                ??Îß§ÏàòÍ∞Ä: {formatNumber(stock.buyPrice)}??| 
                <span className={stock.profitRate && stock.profitRate >= 0 ? 'text-[#00c853]' : 'text-[#f44336]'}>
                  {' '}{stock.profitRate && stock.profitRate >= 0 ? '+' : ''}{stock.profitRate}%
                </span>
              </div>
            ) : (
              <button className="px-3 py-1 text-xs bg-[#f2f4f6] rounded-2xl text-gray-600 hover:bg-gray-200"
                      onClick={() => onMemoClick(stock)}>
                Îß§ÏàòÍ∞Ä ?ÖÎ†•
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
            ?ì¢ {stock.alert.message} <span className="text-xs text-[#8b95a1]">{stock.alert.timeAgo}</span>
          </div>

          {/* Memo Preview */}
          {stock.memo && (
            <div className="bg-[#f5f5f5] rounded-2xl p-2 text-sm italic text-gray-600 flex items-center gap-2 mb-2">
              <span>?èÔ∏è</span>
              <span>{stock.memo}</span>
            </div>
          )}

          {/* Trade Helper Section */}
          <TradeHelper
            stockName={stock.name}
            currentPrice={stock.currentPrice}
            buyPrice={stock.buyPrice}
            onAnalysisClick={onAnalysisClick}
            onSetupClick={onSetupClick}
          />
        </div>

        {/* Right Action Icons */}
        <div className="flex flex-col gap-2 ml-4">
          <button 
            className="p-2 hover:bg-[#f2f4f6] rounded-2xl text-[#8b95a1] hover:text-gray-700"
            onClick={() => onMemoClick(stock)}
            title="Î©îÎ™®"
          >
            ?ìù
          </button>
          <button 
            className="p-2 hover:bg-[#f2f4f6] rounded-2xl text-[#8b95a1] hover:text-gray-700"
            title="?åÎ¶º"
          >
            ?îî
          </button>
          <button 
            className="p-2 hover:bg-[#f2f4f6] rounded-2xl text-[#8b95a1] hover:text-red-500"
            onClick={() => onRemove(stock.id)}
            title="?úÍ±∞"
          >
            ??
          </button>
        </div>
      </div>
    </div>
  );
}