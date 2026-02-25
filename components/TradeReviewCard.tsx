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
      case '좋은매매':
        return 'bg-green-500';
      case '아쉬운매매':
        return 'bg-yellow-500';
      case '나쁜매매':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getVerdictEmoji = (verdict: string) => {
    switch (verdict) {
      case '좋은매매':
        return '✅';
      case '아쉬운매매':
        return '🟡';
      case '나쁜매매':
        return '❌';
      default:
        return '⚪';
    }
  };

  const getReturnColor = (returnPercent: number) => {
    return returnPercent >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getPriceChangePercent = (currentPrice: number, sellPrice: number) => {
    return ((currentPrice - sellPrice) / sellPrice * 100).toFixed(1);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-[#eff3f4] overflow-hidden hover:shadow-md transition-shadow">
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
              <div className="text-xs text-gray-500">
                {Math.abs(trade.returnPercent) >= 10 ? '큰 수익률' : '소소한 수익률'}
              </div>
            </div>
          </div>

          {/* Trade details */}
          <div className="text-sm text-gray-600 mb-4">
            <div className="flex items-center gap-2">
              <span>매수 {formatNumber(trade.buyPrice)}원 ({trade.buyDate})</span>
              <span>→</span>
              <span>매도 {formatNumber(trade.sellPrice)}원 ({trade.sellDate})</span>
            </div>
          </div>

          {/* Price history timeline */}
          <div className="mb-4">
            <div className="text-sm text-gray-700 font-medium mb-2">그 후 주가</div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex justify-between text-xs text-gray-600">
                <div className="text-center">
                  <div className="font-medium">1주후</div>
                  <div className="mt-1">
                    {formatNumber(trade.priceHistory.oneWeek)}원
                  </div>
                  <div className={`text-xs ${
                    trade.priceHistory.oneWeek >= trade.sellPrice 
                      ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ({getPriceChangePercent(trade.priceHistory.oneWeek, trade.sellPrice)}%)
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-medium">2주후</div>
                  <div className="mt-1">
                    {formatNumber(trade.priceHistory.twoWeek)}원
                  </div>
                  <div className={`text-xs ${
                    trade.priceHistory.twoWeek >= trade.sellPrice 
                      ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ({getPriceChangePercent(trade.priceHistory.twoWeek, trade.sellPrice)}%)
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-medium">1개월후</div>
                  <div className="mt-1">
                    {formatNumber(trade.priceHistory.oneMonth)}원
                  </div>
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
            <span className="text-sm text-gray-500">AI 판정</span>
            <div className="flex items-center gap-2">
              <span>{getVerdictEmoji(trade.verdict)}</span>
              <span className="text-sm font-medium">{trade.verdict}</span>
              {trade.verdict === '아쉬운매매' && (
                <span className="text-xs text-gray-500">(결국 회복)</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}