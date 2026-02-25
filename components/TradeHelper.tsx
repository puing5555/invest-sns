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
      <div className="bg-[#f8f9fa] rounded-lg p-3 mt-3">
        <div className="text-sm text-gray-600 mb-2">📊 매매 판단 보조</div>
        <div className="text-sm text-gray-500">
          매수가를 입력하면 매매 판단을 도와드려요
        </div>
        <button
          onClick={() => onSetupClick(stockName)}
          className="mt-2 px-3 py-1 text-xs bg-[#3182f6] text-white rounded-lg hover:bg-[#00c499] transition-colors"
        >
          매수가 입력
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
    <div className="bg-[#f8f9fa] rounded-lg p-3 mt-3">
      <div className="text-sm text-gray-600 mb-3">📊 매매 판단 보조</div>
      
      {/* Stop Loss Line */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-red-600">
          손절가: {formatNumber(tradeData.stopLoss)}원 ({stopLossPercent}%)
          {isNearStopLoss && <span className="ml-1">⚠️</span>}
        </span>
        <button 
          onClick={() => onSetupClick(stockName)}
          className="px-2 py-1 text-xs border border-gray-300 rounded text-gray-600 hover:bg-gray-50"
        >
          수정
        </button>
      </div>

      {/* Take Profit Lines */}
      {isLosing ? (
        // Losing stock - show single take profit
        tradeData.takeProfit && (
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-green-600">
              익절가: {formatNumber(tradeData.takeProfit)}원 
              ({calculatePercent(tradeData.takeProfit, buyPrice)}%)
            </span>
            <button 
              onClick={() => onSetupClick(stockName)}
              className="px-2 py-1 text-xs border border-gray-300 rounded text-gray-600 hover:bg-gray-50"
            >
              수정
            </button>
          </div>
        )
      ) : (
        // Winning stock - show tp1 and tp2
        <div className="space-y-2 mb-2">
          {tradeData.tp1 && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-green-600">
                1차 익절: {formatNumber(tradeData.tp1)}원 
                ({calculatePercent(tradeData.tp1, buyPrice)}%)
                {tradeData.isNearTarget && <span className="ml-1 text-xs">← 근접! 🎯</span>}
              </span>
              <button 
                onClick={() => onSetupClick(stockName)}
                className="px-2 py-1 text-xs border border-gray-300 rounded text-gray-600 hover:bg-gray-50"
              >
                수정
              </button>
            </div>
          )}
          {tradeData.tp2 && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-green-600">
                2차 익절: {formatNumber(tradeData.tp2)}원 
                ({calculatePercent(tradeData.tp2, buyPrice)}%)
              </span>
              <button 
                onClick={() => onSetupClick(stockName)}
                className="px-2 py-1 text-xs border border-gray-300 rounded text-gray-600 hover:bg-gray-50"
              >
                수정
              </button>
            </div>
          )}
        </div>
      )}

      {/* Pattern Summary */}
      <div className="text-xs text-gray-500 mb-3">
        유사 패턴 {tradeData.patternCount}건 분석
        {tradeData.weekRebound && ` | 1주 반등률 ${tradeData.weekRebound}%`}
        {tradeData.moreUpProb && ` | 추가상승 확률 ${tradeData.moreUpProb}%`}
      </div>

      {/* Analysis Button */}
      <button
        onClick={() => onAnalysisClick(stockName)}
        className="w-full px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
      >
        상세 분석 보기
      </button>
    </div>
  );
}