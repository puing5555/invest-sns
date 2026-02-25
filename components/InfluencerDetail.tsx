import { influencerData } from '@/data/influencerData';
import AccuracyCircle from './AccuracyCircle';
import CallHistoryItem from './CallHistoryItem';

interface InfluencerDetailProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function InfluencerDetail({ isOpen, onClose }: InfluencerDetailProps) {
  // Hardcoded for 코린이아빠 (first influencer)
  const influencer = influencerData[0];

  if (!isOpen) return null;

  const getPlatformBadgeColor = (platformName: string) => {
    switch (platformName) {
      case '유튜브': return 'bg-red-500 text-white';
      case '텔레그램': return 'bg-blue-500 text-white';
      case '블로그': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getInitial = (name: string) => name.charAt(0);

  return (
    <>
      {/* Dark overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      
      {/* Slide-in panel */}
      <div className="fixed right-0 top-0 h-full w-[400px] bg-white shadow-xl z-50 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">인플루언서 상세</h2>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="p-4 space-y-6">
          {/* Profile Section */}
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-700 text-2xl mx-auto mb-3">
              {getInitial(influencer.name)}
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">{influencer.name}</h3>
            
            <div className="flex justify-center gap-2 mb-2">
              {influencer.platforms.map((platform, idx) => (
                <span
                  key={idx}
                  className={`px-3 py-1 rounded text-sm font-medium ${getPlatformBadgeColor(platform.name)}`}
                >
                  {platform.name}
                </span>
              ))}
            </div>
            
            <div className="text-lg font-semibold text-gray-700 mb-2">팔로워 {influencer.followers}</div>
            <p className="text-gray-600 text-sm">{influencer.bio}</p>
          </div>

          {/* Stats Section */}
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <AccuracyCircle
                percentage={influencer.accuracy}
                successful={influencer.successfulCalls}
                total={influencer.totalCalls}
                size={80}
              />
            </div>
            <div className="space-y-2">
              <div>
                <div className="text-sm text-gray-600">평균 수익률</div>
                <div className={`text-xl font-bold ${influencer.avgReturn > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  +{influencer.avgReturn}%
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">전체 콜</div>
                <div className="text-lg font-semibold text-gray-900">
                  {influencer.totalCalls}개
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">활동 기간</div>
                <div className="text-sm font-medium text-gray-900">
                  {influencer.activityPeriod}
                </div>
              </div>
            </div>
          </div>

          {/* Monthly Accuracy Chart */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">월별 적중률</h4>
            <div className="space-y-2">
              {influencer.monthlyAccuracy?.map((month, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <div className="w-8 text-sm text-gray-600">{month.month}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
                    <div
                      className="bg-[#3182f6] h-2 rounded-full"
                      style={{ width: `${month.rate}%` }}
                    />
                  </div>
                  <div className="w-10 text-sm font-medium text-gray-900 text-right">
                    {month.rate}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Full Call History */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">전체 콜 내역</h4>
            <div className="border border-gray-200 rounded-lg">
              {influencer.fullCallHistory?.map((call, idx) => (
                <div key={idx} className={idx !== 0 ? 'border-t border-gray-200' : ''}>
                  <CallHistoryItem call={call} />
                </div>
              ))}
            </div>
          </div>

          {/* Top 3 Best Stocks */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">베스트 종목 TOP 3</h4>
            <div className="space-y-2">
              {influencer.topStocks?.map((stock, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                  <div className="w-6 h-6 rounded-full bg-green-500 text-white text-sm flex items-center justify-center font-bold">
                    {idx + 1}
                  </div>
                  <span className="text-green-700 font-medium">{stock}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3 pt-4 border-t border-gray-200">
            <button className="w-full px-4 py-3 bg-[#3182f6] text-white rounded-lg hover:bg-[#00c299] transition-colors font-medium">
              팔로우
            </button>
            <button className="w-full px-4 py-3 border border-[#3182f6] text-[#3182f6] rounded-lg hover:bg-[#3182f6] hover:text-white transition-colors font-medium">
              알림설정
            </button>
            <button className="w-full px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium">
              피드에서 보기
            </button>
          </div>
        </div>
      </div>
    </>
  );
}