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
              <span className="text-xl">{data.mode === 'loss' ? '?†Ô∏è' : '?ü¢'}</span>
              <div>
                <h3 className="font-bold text-lg">{data.stockName}</h3>
                <div className="text-sm text-gray-600">
                  ?ÑÏû¨Í∞Ä: {formatNumber(data.currentPrice)}??
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
              className="text-[#8b95a1] hover:text-gray-600 text-xl"
            >
              ??
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
            <h4 className="font-medium text-[#191f28] mb-3">?§Î•∏ ?†Ï? ?òÍ≤¨</h4>
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
        <h4 className="font-medium text-[#191f28] mb-2">?ÑÏû¨ ?¨Ï???/h4>
        <div className="bg-[#f2f4f6] rounded-2xl p-3">
          <div className="text-sm space-y-1">
            <div>Îß§ÏàòÍ∞Ä: {formatNumber(data.buyPrice)}??/div>
            {data.lossAmount && (
              <div className="text-red-600">
                ?êÏã§?? {formatNumber(Math.abs(data.lossAmount))}??
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Historical Analysis */}
      <div className="mb-6">
        <h4 className="font-medium text-[#191f28] mb-3">Í≥ºÍ±∞ ?†ÏÇ¨ ?ÅÌô© Î∂ÑÏÑù</h4>
        <div className="space-y-3">
          {data.patterns.map((pattern, index) => (
            <PatternAnalysis key={index} pattern={pattern} />
          ))}
        </div>
      </div>

      {/* Special Conditions */}
      {data.specialConditions && (
        <div className="mb-6">
          <h4 className="font-medium text-[#191f28] mb-3">ÏßÄÍ∏??ÅÌô© ?πÏù¥??/h4>
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
        <h4 className="font-medium text-[#191f28] mb-3">AI Ï¢ÖÌï©</h4>
        <div className="bg-blue-50 rounded-2xl p-3">
          <p className="text-sm text-gray-700">
            ?ÑÏû¨ {data.stockName}??Îß§Ïàò ???®Í∏∞ Ï°∞Ï†ï Íµ¨Í∞Ñ???àÏäµ?àÎã§. 
            Í≥ºÍ±∞ ?†ÏÇ¨ ?®ÌÑ¥ Î∂ÑÏÑù Í≤∞Í≥º, 1Í∞úÏõî ??Î∞òÎì± ?ïÎ•†???íÏúº??
            Ï∂îÍ? ?òÎùΩ Î¶¨Ïä§?¨ÎèÑ Ï°¥Ïû¨?©Îãà?? 
            ?¨Ï???Í¥ÄÎ¶¨Í? Ï§ëÏöî???úÏ†ê?ÖÎãà??
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
        <h4 className="font-medium text-[#191f28] mb-2">?ÑÏû¨ ?òÏùµÎ•?/h4>
        <div className="bg-green-50 rounded-2xl p-3">
          <div className="text-lg font-bold text-green-600">
            +{profitPercent}%
          </div>
          <div className="text-sm text-gray-600">
            Îß§ÏàòÍ∞Ä: {formatNumber(data.buyPrice)}??
          </div>
        </div>
      </div>

      {/* Distance to Next Target */}
      <div className="mb-6">
        <h4 className="font-medium text-[#191f28] mb-2">1Ï∞??µÏ†àÍπåÏ?</h4>
        <div className="bg-[#f2f4f6] rounded-2xl p-3">
          <div className="text-sm text-gray-700">
            1Ï∞??µÏ†àÍπåÏ? ?®Ï? Íµ¨Í∞Ñ: <strong>??2%</strong>
          </div>
        </div>
      </div>

      {/* Pattern Analysis */}
      {data.moreUpProb && data.dropProb && (
        <div className="mb-6">
          <h4 className="font-medium text-[#191f28] mb-3">?®ÌÑ¥ Î∂ÑÏÑù</h4>
          <div className="bg-[#f2f4f6] rounded-2xl p-3">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Ï∂îÍ? ?ÅÏäπ ?ïÎ•†:</span>
                <span className="text-green-600 font-medium">
                  {data.moreUpProb}% (?âÍ∑† +{data.avgMoreUp}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span>Ï°∞Ï†ï ?ïÎ•†:</span>
                <span className="text-red-600 font-medium">
                  {data.dropProb}% (?âÍ∑† {data.avgDrop}%)
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scenarios */}
      {data.scenarios && (
        <div className="mb-6">
          <h4 className="font-medium text-[#191f28] mb-3">?àÏÉÅ ?úÎÇòÎ¶¨Ïò§</h4>
          <div className="space-y-2">
            {data.scenarios.map((scenario, index) => (
              <div key={index} className="bg-[#f2f4f6] rounded-2xl p-2">
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
        <h4 className="font-medium text-[#191f28] mb-3">AI Ï¢ÖÌï©</h4>
        <div className="bg-blue-50 rounded-2xl p-3">
          <p className="text-sm text-gray-700">
            {data.stockName}???ÑÏû¨ ?òÏùµ Íµ¨Í∞Ñ???àÏúºÎ©? 
            1Ï∞??µÏ†à ?Ä?¥Î∞ç??Í∑ºÏ†ë?àÏäµ?àÎã§. 
            Ï∂îÍ? ?ÅÏäπÎ≥¥Îã§??Ï°∞Ï†ï ?ïÎ•†???íÏïÑ 
            Î∂ÄÎ∂??µÏ†à??Í≥†Î†§?¥Î≥º ?úÏ†ê?ÖÎãà??
          </p>
        </div>
      </div>
    </>
  );
}