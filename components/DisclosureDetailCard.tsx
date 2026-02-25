'use client';

import VotePoll from './VotePoll';

interface DisclosureData {
  id: string;
  grade: 'A?±Í∏â' | 'B?±Í∏â' | 'C?±Í∏â';
  companyName: string;
  marketCap: string;
  time: string;
  title: string;
  subtitle: string;
  aiComment: string;
  pastPattern: {
    count: number;
    period: string;
    returnRate: string;
    winRate: number;
  };
  votes: {
    positive: number;
    negative: number;
    neutral: number;
    totalVoters: number;
  };
  interactions: {
    comments: number;
    reposts: number;
    likes: number;
  };
}

interface DisclosureDetailCardProps {
  data: DisclosureData;
  onAnalysisClick: () => void;
}

export default function DisclosureDetailCard({ data, onAnalysisClick }: DisclosureDetailCardProps) {
  const getGradeBadgeColor = (grade: string) => {
    switch (grade) {
      case 'A?±Í∏â': return '#ff4444';
      case 'B?±Í∏â': return '#ffaa00';
      case 'C?±Í∏â': return '#888';
      default: return '#888';
    }
  };

  const pollOptions = [
    {
      label: '?∏Ïû¨',
      emoji: '?ü¢',
      percent: data.votes.positive,
      color: '#22c55e'
    },
    {
      label: '?ÖÏû¨',
      emoji: '?î¥',
      percent: data.votes.negative,
      color: '#ef4444'
    },
    {
      label: 'Î™®Î•¥Í≤†Îã§',
      emoji: '?ü°',
      percent: data.votes.neutral,
      color: '#eab308'
    }
  ];

  return (
    <div className="bg-white border border-[#f0f0f0] rounded-2xl p-4 mb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span
            className="px-2 py-1 text-sm font-medium text-white rounded"
            style={{ backgroundColor: getGradeBadgeColor(data.grade) }}
          >
            {data.grade}
          </span>
          <span className="font-medium text-[#191f28]">{data.companyName}</span>
          <span className="text-sm text-[#8b95a1]">?úÏ¥ù {data.marketCap}</span>
        </div>
        <span className="text-sm text-[#8b95a1]">{data.time}</span>
      </div>

      {/* Disclosure Title */}
      <div className="mb-3">
        <h3 className="text-lg font-medium text-[#191f28] mb-1">
          ?ìã {data.title}
        </h3>
        <p className="text-gray-600">{data.subtitle}</p>
      </div>

      {/* AI Comment */}
      <div className="mb-4">
        <h4 className="text-gray-700 mb-2">?§ñ AI ?úÏ§Ñ??</h4>
        <p className="text-[#3182f6] font-medium">&quot;{data.aiComment}&quot;</p>
      </div>

      {/* Past Pattern */}
      <div className="mb-4">
        <p className="text-gray-700">
          ?ìä Í≥ºÍ±∞ ?®ÌÑ¥: {data.pastPattern.count}Í±?| {data.pastPattern.period} {data.pastPattern.returnRate} | ?πÎ•† {data.pastPattern.winRate}%
        </p>
      </div>

      {/* Vote Poll */}
      <div className="bg-[#f0faf7] rounded-2xl p-3 mb-4">
        <VotePoll options={pollOptions} totalVotes={data.votes.totalVoters} />
      </div>

      {/* Interactions */}
      <div className="flex items-center gap-4 mb-4 text-[#8b95a1]">
        <span className="flex items-center gap-1">
          ?í¨ {data.interactions.comments}
        </span>
        <span className="flex items-center gap-1">
          ?îÑ {data.interactions.reposts}
        </span>
        <span className="flex items-center gap-1">
          ?§Ô∏è {data.interactions.likes}
        </span>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 flex-wrap">
        <button
          onClick={onAnalysisClick}
          className="px-4 py-2 bg-[#3182f6] text-white rounded-md hover:bg-[#00b89a] transition-colors"
        >
          AI ?ÅÏÑ∏Î∂ÑÏÑù Î≥¥Í∏∞
        </button>
        <button className="px-4 py-2 bg-[#f2f4f6] text-gray-700 rounded-md hover:bg-gray-200 transition-colors">
          ?êÎ¨∏ Î≥¥Í∏∞
        </button>
        <button className="px-4 py-2 bg-[#f2f4f6] text-gray-700 rounded-md hover:bg-gray-200 transition-colors">
          ?ºÎìú??Í≥µÏú†
        </button>
      </div>
    </div>
  );
}