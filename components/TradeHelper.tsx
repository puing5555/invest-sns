import { tradeHelperData } from '@/data/tradeData';

interface TradeHelperProps {
  stockName: string;
  currentPrice: number;
  buyPrice: number | null;
  onAnalysisClick: (stockName: string) => void;
  onSetupClick: (stockName: string) => void;
}

export default function TradeHelper({ 
  stockName, 
  currentPrice, 
  buyPrice, 
  onAnalysisClick, 
  onSetupClick 
}: TradeHelperProps) {
  const tradeData = tradeHelperData[stockName];
  
  if (!buyPrice) {
    return (
      <div className="bg-[#f8f9fa] rounded-2xl p-3 mt-3">
        <div className="text-sm text-gray-600 mb-2">?ìä Îß§Îß§ ?êÎã® Î≥¥Ï°∞</div>
        <div className="text-sm text-[#8b95a1]">
          Îß§ÏàòÍ∞ÄÎ•??ÖÎ†•?òÎ©¥ Îß§Îß§ ?êÎã®???ÑÏ??úÎ†§??
        </div>
        <button
          onClick={() => onSetupClick(stockName)}
          className="mt-2 px-3 py-1 text-xs bg-[#3182f6] text-white rounded-2xl hover:bg-[#00c499] transition-colors"
        >
          Îß§ÏàòÍ∞Ä ?ÖÎ†•
        </button>
      </div>
    );
  }

  if (!tradeData) {
    return null;
  }

  const formatNumber = (num: number) => {
    return num.toLocaleString('ko-KR');
  };

  const calculatePercent = (target: number, base: number) => {
    return ((target - base) / base * 100).toFixed(1);
  };

  const isLosing = currentPrice < buyPrice;
  const stopLossPercent = calculatePercent(tradeData.stopLoss, buyPrice);
  const isNearStopLoss = currentPrice <= tradeData.stopLoss * 1.02; // Within 2% of stop loss

  return (
    <div className="bg-[#f8f9fa] rounded-2xl p-3 mt-3">
      <div className="text-sm text-gray-600 mb-3">?ìä Îß§Îß§ ?êÎã® Î≥¥Ï°∞</div>
      
      {/* Stop Loss Line */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-red-600">
          ?êÏ†àÍ∞Ä: {formatNumber(tradeData.stopLoss)}??({stopLossPercent}%)
          {isNearStopLoss && <span className="ml-1">?†Ô∏è</span>}
        </span>
        <button 
          onClick={() => onSetupClick(stockName)}
          className="px-2 py-1 text-xs border border-gray-300 rounded text-gray-600 hover:bg-[#f2f4f6]"
        >
          ?òÏ†ï
        </button>
      </div>

      {/* Take Profit Lines */}
      {isLosing ? (
        // Losing stock - show single take profit
        tradeData.takeProfit && (
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-green-600">
              ?µÏ†àÍ∞Ä: {formatNumber(tradeData.takeProfit)}??
              ({calculatePercent(tradeData.takeProfit, buyPrice)}%)
            </span>
            <button 
              onClick={() => onSetupClick(stockName)}
              className="px-2 py-1 text-xs border border-gray-300 rounded text-gray-600 hover:bg-[#f2f4f6]"
            >
              ?òÏ†ï
            </button>
          </div>
        )
      ) : (
        // Winning stock - show tp1 and tp2
        <div className="space-y-2 mb-2">
          {tradeData.tp1 && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-green-600">
                1Ï∞??µÏ†à: {formatNumber(tradeData.tp1)}??
                ({calculatePercent(tradeData.tp1, buyPrice)}%)
                {tradeData.isNearTarget && <span className="ml-1 text-xs">??Í∑ºÏ†ë! ?éØ</span>}
              </span>
              <button 
                onClick={() => onSetupClick(stockName)}
                className="px-2 py-1 text-xs border border-gray-300 rounded text-gray-600 hover:bg-[#f2f4f6]"
              >
                ?òÏ†ï
              </button>
            </div>
          )}
          {tradeData.tp2 && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-green-600">
                2Ï∞??µÏ†à: {formatNumber(tradeData.tp2)}??
                ({calculatePercent(tradeData.tp2, buyPrice)}%)
              </span>
              <button 
                onClick={() => onSetupClick(stockName)}
                className="px-2 py-1 text-xs border border-gray-300 rounded text-gray-600 hover:bg-[#f2f4f6]"
              >
                ?òÏ†ï
              </button>
            </div>
          )}
        </div>
      )}

      {/* Pattern Summary */}
      <div className="text-xs text-[#8b95a1] mb-3">
        ?†ÏÇ¨ ?®ÌÑ¥ {tradeData.patternCount}Í±?Î∂ÑÏÑù
        {tradeData.weekRebound && ` | 1Ï£?Î∞òÎì±Î•?${tradeData.weekRebound}%`}
        {tradeData.moreUpProb && ` | Ï∂îÍ??ÅÏäπ ?ïÎ•† ${tradeData.moreUpProb}%`}
      </div>

      {/* Analysis Button */}
      <button
        onClick={() => onAnalysisClick(stockName)}
        className="w-full px-4 py-2 bg-white border border-gray-200 rounded-2xl text-sm text-gray-700 hover:bg-[#f2f4f6] transition-colors"
      >
        ?ÅÏÑ∏ Î∂ÑÏÑù Î≥¥Í∏∞
      </button>
    </div>
  );
}