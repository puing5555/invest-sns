import { Influencer } from '@/data/influencerData';
import AccuracyCircle from './AccuracyCircle';
import CallHistoryItem from './CallHistoryItem';

interface InfluencerCardProps {
  influencer: Influencer;
  onDetailClick: () => void;
}

export default function InfluencerCard({ influencer, onDetailClick }: InfluencerCardProps) {
  const getInitial = (name: string) => name.charAt(0);

  const getPlatformBadgeColor = (platformName: string) => {
    switch (platformName) {
      case '유튜브': return 'bg-red-500 text-white';
      case '텔레그램': return 'bg-blue-500 text-white';
      case '블로그': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-[#f0f0f0] shadow-sm p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-700">
            {getInitial(influencer.name)}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{influencer.name}</h3>
            <div className="flex gap-1 mt-1">
              {influencer.platforms.map((platform, idx) => (
                <span
                  key={idx}
                  className={`px-2 py-0.5 rounded text-xs font-medium ${getPlatformBadgeColor(platform.name)}`}
                >
                  {platform.name}
                </span>
              ))}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600">팔로워</div>
          <div className="font-semibold">{influencer.followers}</div>
        </div>
      </div>

      {/* Stats */}
      <div className="flex items-center justify-center gap-8 mb-6">
        <AccuracyCircle
          percentage={influencer.accuracy}
          successful={influencer.successfulCalls}
          total={influencer.totalCalls}
        />
        <div className="text-center">
          <div className="text-sm text-gray-600">평균 수익률</div>
          <div className={`text-2xl font-bold ${influencer.avgReturn > 0 ? 'text-green-600' : 'text-red-600'}`}>
            +{influencer.avgReturn}%
          </div>
        </div>
      </div>

      {/* Recent Calls */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-2">최근 콜</h4>
        <div className="space-y-1">
          {influencer.recentCalls.map((call, idx) => (
            <CallHistoryItem key={idx} call={call} />
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
          팔로우
        </button>
        <button
          onClick={onDetailClick}
          className="flex-1 px-4 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#00c299] transition-colors"
        >
          상세보기
        </button>
      </div>
    </div>
  );
}