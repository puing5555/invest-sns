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
          className="text-gray-600 hover:text-gray-900 mb-2 flex items-center space-x-1"
        >
          <span>←</span>
          <span>전략연구실</span>
        </button>
        <h1 className="text-2xl font-bold text-gray-900">AI 퀀트봇 생성</h1>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Description */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-2">나만의 AI 퀀트봇을 만드세요</h2>
          <p className="text-gray-600">조건을 설정하면 AI가 24시간 자동으로 매매합니다</p>
        </div>

        {/* Bot Cards */}
        <div className="space-y-6 mb-8">
          {quantBots.map((bot) => (
            <div key={bot.id} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              {/* Bot Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">🤖</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{bot.name}</h3>
                    <p className="text-sm text-gray-600">{bot.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    bot.status === 'active' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {bot.status === 'active' ? '🟢 운영중' : '⭕ 중단'}
                  </span>
                </div>
              </div>

              {/* Conditions */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">매매 조건</h4>
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
                  <h4 className="text-sm font-medium text-gray-700 mb-2">오늘의 시그널</h4>
                  <div className="space-y-1">
                    {bot.todaySignals.map((signal, index) => (
                      <div key={index} className="text-sm text-gray-900 font-medium">
                        📈 {signal}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Performance */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">6개월 수익률</h4>
                  <div className="text-2xl font-bold text-green-600">
                    +{bot.sixMonthReturn}%
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2 mt-4 pt-4 border-t border-gray-100">
                <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
                  상세보기
                </button>
                <button className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200">
                  설정변경
                </button>
                <button className={`px-4 py-2 text-sm rounded-lg ${
                  bot.status === 'active'
                    ? 'bg-red-100 text-red-600 hover:bg-red-200'
                    : 'bg-green-100 text-green-600 hover:bg-green-200'
                }`}>
                  {bot.status === 'active' ? '중단' : '시작'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Create New Bot Button */}
        <div className="text-center">
          <button className="px-8 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
            + 새 퀀트봇 만들기
          </button>
        </div>
      </div>
    </div>
  );
}