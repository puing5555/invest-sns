import { TradeReviewData } from '@/data/tradeData';

interface TradeReviewCardProps {
  trade: TradeReviewData;
}

export default function TradeReviewCard({ trade }: TradeReviewCardProps) {
  const formatNumber = (num: number) => {
    return num.toLocaleString('ko-KR');
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'Ï¢ãÏ?Îß§Îß§':
        return 'bg-green-500';
      case '?ÑÏâ¨?¥Îß§Îß?:
        return 'bg-yellow-500';
      case '?òÏÅúÎß§Îß§':
        return 'bg-red-500';
      default:
        return 'bg-[#f2f4f6]0';
    }
  };

  const getVerdictEmoji = (verdict: string) => {
    switch (verdict) {
      case 'Ï¢ãÏ?Îß§Îß§':
        return '??;
      case '?ÑÏâ¨?¥Îß§Îß?:
        return '?ü°';
      case '?òÏÅúÎß§Îß§':
        return '??;
      default:
        return '??;
    }
  };

  const getReturnColor = (returnPercent: number) => {
    return returnPercent >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getPriceChangePercent = (currentPrice: number, sellPrice: number) => {
    return ((currentPrice - sellPrice) / sellPrice * 100).toFixed(1);
  };

  return (
    <div className="bg-white rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-[#f0f0f0] overflow-hidden hover:shadow-md transition-shadow">
      {/* Left color bar */}
      <div className="flex">
        <div className={`w-1 ${getVerdictColor(trade.verdict)}`} />
        
        <div className="flex-1 p-4">
          {/* Header - Stock name and return */}
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-lg">{trade.stockName}</h3>
            <div className="text-right">
              <div className={`font-bold text-lg ${getReturnColor(trade.returnPercent)}`}>
                {trade.returnPercent >= 0 ? '+' : ''}{trade.returnPercent}%
              </div>
              <div className="text-xs text-[#8b95a1]">
                {Math.abs(trade.returnPercent) >= 10 ? '???òÏùµÎ•? : '?åÏÜå???òÏùµÎ•?}
              </div>
            </div>
          </div>

          {/* Trade details */}
          <div className="text-sm text-gray-600 mb-4">
            <div className="flex items-center gap-2">
              <span>Îß§Ïàò {formatNumber(trade.buyPrice)}??({trade.buyDate})</span>
              <span>??/span>
              <span>Îß§ÎèÑ {formatNumber(trade.sellPrice)}??({trade.sellDate})</span>
            </div>
          </div>

          {/* Price history timeline */}
          <div className="mb-4">
            <div className="text-sm text-gray-700 font-medium mb-2">Í∑???Ï£ºÍ?</div>
            <div className="bg-[#f2f4f6] rounded-2xl p-3">
              <div className="flex justify-between text-xs text-gray-600">
                <div className="text-center">
                  <div className="font-medium">1Ï£ºÌõÑ</div>
                  <div className="mt-1">
                    {formatNumber(trade.priceHistory.oneWeek)}??                  </div>
                  <div className={`text-xs ${
                    trade.priceHistory.oneWeek >= trade.sellPrice 
                      ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ({getPriceChangePercent(trade.priceHistory.oneWeek, trade.sellPrice)}%)
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-medium">2Ï£ºÌõÑ</div>
                  <div className="mt-1">
                    {formatNumber(trade.priceHistory.twoWeek)}??                  </div>
                  <div className={`text-xs ${
                    trade.priceHistory.twoWeek >= trade.sellPrice 
                      ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ({getPriceChangePercent(trade.priceHistory.twoWeek, trade.sellPrice)}%)
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-medium">1Í∞úÏõî??/div>
                  <div className="mt-1">
                    {formatNumber(trade.priceHistory.oneMonth)}??                  </div>
                  <div className={`text-xs ${
                    trade.priceHistory.oneMonth >= trade.sellPrice 
                      ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ({getPriceChangePercent(trade.priceHistory.oneMonth, trade.sellPrice)}%)
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Verdict badge */}
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#8b95a1]">AI ?êÏ†ï</span>
            <div className="flex items-center gap-2">
              <span>{getVerdictEmoji(trade.verdict)}</span>
              <span className="text-sm font-medium">{trade.verdict}</span>
              {trade.verdict === '?ÑÏâ¨?¥Îß§Îß? && (
                <span className="text-xs text-[#8b95a1]">(Í≤∞Íµ≠ ?åÎ≥µ)</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}