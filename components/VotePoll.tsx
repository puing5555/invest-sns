'use client';

interface PollOption {
  label: string;
  emoji: string;
  percent: number;
  color: string;
}

interface VotePollProps {
  options: PollOption[];
  totalVotes: number;
}

export default function VotePoll({ options, totalVotes }: VotePollProps) {
  return (
    <div className="mt-2 space-y-2">
      {options.map((opt, i) => (
        <div key={i} className="relative h-8 rounded-md overflow-hidden bg-gray-100">
          <div
            className="absolute inset-y-0 left-0 rounded-md opacity-20"
            style={{ width: `${opt.percent}%`, backgroundColor: opt.color }}
          />
          <div className="relative flex items-center justify-between h-full px-3 text-sm">
            <span className="text-gray-800">
              {opt.emoji} {opt.label}
            </span>
            <span className="font-semibold text-gray-700">{opt.percent}%</span>
          </div>
        </div>
      ))}
      <p className="text-xs text-gray-500">{totalVotes}명 참여</p>
    </div>
  );
}
