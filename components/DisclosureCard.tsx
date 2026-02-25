'use client';

export interface DisclosureData {
  company: string;
  marketCap: string;
  title: string;
  ai: string;
  time: string;
  bullPercent: number;
}

export default function DisclosureCard({ d }: { d: DisclosureData }) {
  const bearPercent = 100 - d.bullPercent;
  return (
    <div className="bg-white border border-[#f0f0f0] rounded-2xl p-4 hover:bg-[#f2f4f6] transition-colors cursor-pointer">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-[#191f28]">{d.company}</span>
          <span className="text-xs text-[#8b95a1]">{d.marketCap}</span>
        </div>
        <span className="text-xs text-[#8b95a1]">{d.time}</span>
      </div>
      <p className="text-sm text-gray-700 mb-1">{d.title}</p>
      <p className="text-xs text-[#3182f6] mb-2">?¤– {d.ai}</p>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 rounded-full bg-[#f2f4f6] overflow-hidden flex">
          <div className="h-full bg-[#00c853]" style={{ width: `${d.bullPercent}%` }} />
          <div className="h-full bg-[#f44336]" style={{ width: `${bearPercent}%` }} />
        </div>
        <span className="text-[10px] text-[#8b95a1] whitespace-nowrap">?¸ìž¬ {d.bullPercent}%</span>
      </div>
    </div>
  );
}
