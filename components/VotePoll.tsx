'use client';

interface PollOption {
  label: string;
  emoji: string;
  percent: number;
  color: string;
}

interface Poll {
  options: PollOption[];
  totalVotes: number;
}

export default function VotePoll({ poll, className = '' }: { poll: Poll; className?: string }) {
  return (
    <div className={`border border-[#f0f0f0] rounded-2xl p-3 ${className}`}>
      <div className="space-y-2">
        {poll.options.map((option, i) => (
          <div key={i} className="relative">
            <div
              className="flex items-center justify-between p-2 rounded-xl transition-colors cursor-pointer hover:bg-[#f2f4f6]"
              style={{ backgroundColor: `${option.color}10` }}
            >
              <div className="flex items-center gap-2">
                <span className="text-sm">{option.emoji}</span>
                <span className="text-sm font-medium text-[#191f28]">{option.label}</span>
              </div>
              <span className="text-sm font-bold text-[#191f28]">{option.percent}%</span>
            </div>
            <div
              className="absolute left-0 top-0 bottom-0 rounded-xl opacity-20"
              style={{
                width: `${option.percent}%`,
                backgroundColor: option.color,
              }}
            />
          </div>
        ))}
      </div>
      <p className="text-xs text-[#8b95a1] mt-2">{poll.totalVotes.toLocaleString()}명 참여</p>
    </div>
  );
}