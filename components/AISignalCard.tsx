'use client';

export interface AISignalData {
  stock: string;
  score: number;
  summary: string;
  tags: string[];
}

export default function AISignalCard({ d }: { d: AISignalData }) {
  const scoreColor =
    d.score >= 80 ? 'text-[#16a34a]' : d.score >= 60 ? 'text-[#ca8a04]' : 'text-[#dc2626]';
  const scoreBg =
    d.score >= 80 ? 'bg-[#dcfce7]' : d.score >= 60 ? 'bg-[#fef9c3]' : 'bg-[#fee2e2]';

  return (
    <div className="bg-white border border-[#f0f0f0] rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer">
      <div className="flex items-center justify-between mb-2">
        <span className="font-bold text-sm text-gray-900">{d.stock}</span>
        <span className={`text-lg font-bold ${scoreColor} ${scoreBg} w-10 h-10 rounded-full flex items-center justify-center`}>
          {d.score}
        </span>
      </div>
      <p className="text-xs text-gray-600 mb-2">{d.summary}</p>
      <div className="flex gap-1 flex-wrap">
        {d.tags.map((tag, i) => (
          <span
            key={i}
            className="text-[10px] bg-[#f0fdf4] text-[#3182f6] border border-[#3182f630] px-2 py-0.5 rounded-full"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
