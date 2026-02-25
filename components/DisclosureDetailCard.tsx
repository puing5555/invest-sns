'use client';

import VotePoll from './VotePoll';

interface DisclosureData {
  id: string;
  grade: 'A등급' | 'B등급' | 'C등급';
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
      case 'A등급': return '#ff4444';
      case 'B등급': return '#ffaa00';
      case 'C등급': return '#888';
      default: return '#888';
    }
  };

  const pollOptions = [
    {
      label: '호재',
      emoji: '🟢',
      percent: data.votes.positive,
      color: '#22c55e'
    },
    {
      label: '악재',
      emoji: '🔴',
      percent: data.votes.negative,
      color: '#ef4444'
    },
    {
      label: '모르겠다',
      emoji: '🟡',
      percent: data.votes.neutral,
      color: '#eab308'
    }
  ];

  return (
    <div className="bg-white border border-[#eff3f4] rounded-lg p-4 mb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span
            className="px-2 py-1 text-sm font-medium text-white rounded"
            style={{ backgroundColor: getGradeBadgeColor(data.grade) }}
          >
            {data.grade}
          </span>
          <span className="font-medium text-gray-900">{data.companyName}</span>
          <span className="text-sm text-gray-500">시총 {data.marketCap}</span>
        </div>
        <span className="text-sm text-gray-500">{data.time}</span>
      </div>

      {/* Disclosure Title */}
      <div className="mb-3">
        <h3 className="text-lg font-medium text-gray-900 mb-1">
          📋 {data.title}
        </h3>
        <p className="text-gray-600">{data.subtitle}</p>
      </div>

      {/* AI Comment */}
      <div className="mb-4">
        <h4 className="text-gray-700 mb-2">🤖 AI 한줄평:</h4>
        <p className="text-[#00d4aa] font-medium">&quot;{data.aiComment}&quot;</p>
      </div>

      {/* Past Pattern */}
      <div className="mb-4">
        <p className="text-gray-700">
          📊 과거 패턴: {data.pastPattern.count}건 | {data.pastPattern.period} {data.pastPattern.returnRate} | 승률 {data.pastPattern.winRate}%
        </p>
      </div>

      {/* Vote Poll */}
      <div className="bg-[#f0faf7] rounded-lg p-3 mb-4">
        <VotePoll options={pollOptions} totalVotes={data.votes.totalVoters} />
      </div>

      {/* Interactions */}
      <div className="flex items-center gap-4 mb-4 text-gray-500">
        <span className="flex items-center gap-1">
          💬 {data.interactions.comments}
        </span>
        <span className="flex items-center gap-1">
          🔄 {data.interactions.reposts}
        </span>
        <span className="flex items-center gap-1">
          ❤️ {data.interactions.likes}
        </span>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 flex-wrap">
        <button
          onClick={onAnalysisClick}
          className="px-4 py-2 bg-[#00d4aa] text-white rounded-md hover:bg-[#00b89a] transition-colors"
        >
          AI 상세분석 보기
        </button>
        <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors">
          원문 보기
        </button>
        <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors">
          피드에 공유
        </button>
      </div>
    </div>
  );
}