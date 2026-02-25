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
      case '?†ÌäúÎ∏?: return 'bg-red-500 text-white';
      case '?îÎ†àÍ∑∏Îû®': return 'bg-blue-500 text-white';
      case 'Î∏îÎ°úÍ∑?: return 'bg-green-500 text-white';
      default: return 'bg-[#f2f4f6]0 text-white';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-[#f0f0f0] shadow-[0_2px_8px_rgba(0,0,0,0.04)] p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-700">
            {getInitial(influencer.name)}
          </div>
          <div>
            <h3 className="font-semibold text-[#191f28]">{influencer.name}</h3>
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
          <div className="text-sm text-gray-600">?îÎ°ú??/div>
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
          <div className="text-sm text-gray-600">?âÍ∑† ?òÏùµÎ•?/div>
          <div className={`text-2xl font-bold ${influencer.avgReturn > 0 ? 'text-green-600' : 'text-red-600'}`}>
            +{influencer.avgReturn}%
          </div>
        </div>
      </div>

      {/* Recent Calls */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-2">ÏµúÍ∑º ÏΩ?/h4>
        <div className="space-y-1">
          {influencer.recentCalls.map((call, idx) => (
            <CallHistoryItem key={idx} call={call} />
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button className="flex-1 px-4 py-2 border border-gray-300 rounded-2xl text-gray-700 hover:bg-[#f2f4f6] transition-colors">
          ?îÎ°ú??
        </button>
        <button
          onClick={onDetailClick}
          className="flex-1 px-4 py-2 bg-[#3182f6] text-white rounded-2xl hover:bg-[#00c299] transition-colors"
        >
          ?ÅÏÑ∏Î≥¥Í∏∞
        </button>
      </div>
    </div>
  );
}