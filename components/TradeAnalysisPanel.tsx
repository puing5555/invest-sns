import { AnalysisPanelData, analysisPanelData } from '@/data/tradeData';
import PatternAnalysis from './PatternAnalysis';
import VotePoll from './VotePoll';

interface TradeAnalysisPanelProps {
  isOpen: boolean;
  onClose: () => void;
  stockName: string | null;
}

export default function TradeAnalysisPanel({ isOpen, onClose, stockName }: TradeAnalysisPanelProps) {
  if (!isOpen || !stockName) return null;

  const data = analysisPanelData[stockName];
  if (!data) return null;

  const formatNumber = (num: number) => {
    return num.toLocaleString('ko-KR');
  };

  const lossPercent = data.mode === 'loss' && data.lossAmount 
    ? ((data.lossAmount / data.buyPrice) * 100).toFixed(1)
    : '0';

  return (
    <div className="fixed inset-0 z-50">
      {/* Background overlay */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-30"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className={`absolute right-0 top-0 h-full w-[400px] bg-white shadow-xl transform transition-transform duration-300 ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        {/* Header */}
        <div className={`p-4 border-b ${data.mode === 'loss' ? 'bg-red-50' : 'bg-green-50'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">{data.mode === 'loss' ? '⚠️' : '🟢'}</span>
              <div>
                <h3 className="font-bold text-lg">{data.stockName}</h3>
                <div className="text-sm text-gray-600">
                  현재가: {formatNumber(data.currentPrice)}원
                  {data.mode === 'loss' && (
                    <span className="text-red-600 ml-2">
                      ({lossPercent}%)
                    </span>
                  )}
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-xl"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 h-full overflow-y-auto pb-20">
          {data.mode === 'loss' ? (
            <LossAnalysisContent data={data} formatNumber={formatNumber} />
          ) : (
            <ProfitAnalysisContent data={data} formatNumber={formatNumber} />
          )}

          {/* Vote Section */}
          <div className="mt-6">
            <h4 className="font-medium text-gray-900 mb-3">다른 유저 의견</h4>
            <VotePoll 
              options={data.vote.options}
              totalVotes={data.vote.totalVotes}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function LossAnalysisContent({ data, formatNumber }: { 
  data: AnalysisPanelData; 
  formatNumber: (num: number) => string; 
}) {
  return (
    <>
      {/* Current Position */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-2">현재 포지션</h4>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm space-y-1">
            <div>매수가: {formatNumber(data.buyPrice)}원</div>
            {data.lossAmount && (
              <div className="text-red-600">
                손실액: {formatNumber(Math.abs(data.lossAmount))}원
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Historical Analysis */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">과거 유사 상황 분석</h4>
        <div className="space-y-3">
          {data.patterns.map((pattern, index) => (
            <PatternAnalysis key={index} pattern={pattern} />
          ))}
        </div>
      </div>

      {/* Special Conditions */}
      {data.specialConditions && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-3">지금 상황 특이점</h4>
          <div className="space-y-2">
            {data.specialConditions.map((condition, index) => (
              <div key={index} className="text-sm">
                {condition}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Summary */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">AI 종합</h4>
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-sm text-gray-700">
            현재 {data.stockName}는 매수 후 단기 조정 구간에 있습니다. 
            과거 유사 패턴 분석 결과, 1개월 내 반등 확률이 높으나 
            추가 하락 리스크도 존재합니다. 
            포지션 관리가 중요한 시점입니다.
          </p>
        </div>
      </div>
    </>
  );
}

function ProfitAnalysisContent({ data, formatNumber }: { 
  data: AnalysisPanelData; 
  formatNumber: (num: number) => string; 
}) {
  const profitPercent = ((data.currentPrice - data.buyPrice) / data.buyPrice * 100).toFixed(1);

  return (
    <>
      {/* Current Position */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-2">현재 수익률</h4>
        <div className="bg-green-50 rounded-lg p-3">
          <div className="text-lg font-bold text-green-600">
            +{profitPercent}%
          </div>
          <div className="text-sm text-gray-600">
            매수가: {formatNumber(data.buyPrice)}원
          </div>
        </div>
      </div>

      {/* Distance to Next Target */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-2">1차 익절까지</h4>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm text-gray-700">
            1차 익절까지 남은 구간: <strong>약 2%</strong>
          </div>
        </div>
      </div>

      {/* Pattern Analysis */}
      {data.moreUpProb && data.dropProb && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-3">패턴 분석</h4>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>추가 상승 확률:</span>
                <span className="text-green-600 font-medium">
                  {data.moreUpProb}% (평균 +{data.avgMoreUp}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span>조정 확률:</span>
                <span className="text-red-600 font-medium">
                  {data.dropProb}% (평균 {data.avgDrop}%)
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scenarios */}
      {data.scenarios && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-3">예상 시나리오</h4>
          <div className="space-y-2">
            {data.scenarios.map((scenario, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-2">
                <div className="text-sm text-gray-700">
                  {scenario}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Summary */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">AI 종합</h4>
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-sm text-gray-700">
            {data.stockName}는 현재 수익 구간에 있으며, 
            1차 익절 타이밍이 근접했습니다. 
            추가 상승보다는 조정 확률이 높아 
            부분 익절을 고려해볼 시점입니다.
          </p>
        </div>
      </div>
    </>
  );
}