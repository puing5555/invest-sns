import { quantBots } from '@/data/labData';

interface QuantBotProps {
  onBack: () => void;
}

export default function QuantBot({ onBack }: QuantBotProps) {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <button
          onClick={onBack}
          className="text-gray-600 hover:text-[#191f28] mb-2 flex items-center space-x-1"
        >
          <span>??/span>
          <span>?ÑÎûµ?∞Íµ¨??/span>
        </button>
        <h1 className="text-2xl font-bold text-[#191f28]">AI ?Ä?∏Î¥á ?ùÏÑ±</h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Description */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-[#191f28] mb-2">?òÎßå??AI ?Ä?∏Î¥á??ÎßåÎìú?∏Ïöî</h2>
          <p className="text-gray-600">Ï°∞Í±¥???§Ï†ï?òÎ©¥ AIÍ∞Ä 24?úÍ∞Ñ ?êÎèô?ºÎ°ú Îß§Îß§?©Îãà??/p>
        </div>

        {/* Bot Cards */}
        <div className="space-y-6 mb-8">
          {quantBots.map((bot) => (
            <div key={bot.id} className="bg-white border border-gray-200 rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
              {/* Bot Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">?§ñ</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-[#191f28]">{bot.name}</h3>
                    <p className="text-sm text-gray-600">{bot.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    bot.status === 'active' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-[#f2f4f6] text-gray-600'
                  }`}>
                    {bot.status === 'active' ? '?ü¢ ?¥ÏòÅÏ§? : '‚≠?Ï§ëÎã®'}
                  </span>
                </div>
              </div>

              {/* Conditions */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Îß§Îß§ Ï°∞Í±¥</h4>
                <div className="flex flex-wrap gap-2">
                  {bot.conditions.map((condition, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-50 text-blue-700 text-sm rounded-full"
                    >
                      {condition}
                    </span>
                  ))}
                </div>
              </div>

              {/* Performance and Today's Signals */}
              <div className="grid grid-cols-2 gap-6">
                {/* Today's Signals */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">?§Îäò???úÍ∑∏??/h4>
                  <div className="space-y-1">
                    {bot.todaySignals.map((signal, index) => (
                      <div key={index} className="text-sm text-[#191f28] font-medium">
                        ?ìà {signal}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Performance */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">6Í∞úÏõî ?òÏùµÎ•?/h4>
                  <div className="text-2xl font-bold text-green-600">
                    +{bot.sixMonthReturn}%
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2 mt-4 pt-4 border-t border-gray-100">
                <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-2xl hover:bg-blue-700">
                  ?ÅÏÑ∏Î≥¥Í∏∞
                </button>
                <button className="px-4 py-2 bg-[#f2f4f6] text-gray-700 text-sm rounded-2xl hover:bg-gray-200">
                  ?§Ï†ïÎ≥ÄÍ≤?
                </button>
                <button className={`px-4 py-2 text-sm rounded-2xl ${
                  bot.status === 'active'
                    ? 'bg-red-100 text-red-600 hover:bg-red-200'
                    : 'bg-green-100 text-green-600 hover:bg-green-200'
                }`}>
                  {bot.status === 'active' ? 'Ï§ëÎã®' : '?úÏûë'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Create New Bot Button */}
        <div className="text-center">
          <button className="px-8 py-4 bg-purple-600 text-white rounded-2xl hover:bg-purple-700 font-medium">
            + ???Ä?∏Î¥á ÎßåÎì§Í∏?
          </button>
        </div>
      </div>
    </div>
  );
}