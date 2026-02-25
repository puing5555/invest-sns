'use client';

export interface AnalystTargetData {
  stock: string;
  firm: string;
  analyst: string;
  prev: string;
  next: string;
  direction: 'up' | 'down';
  accuracy: number;
}

export default function AnalystTargetItem({ d }: { d: AnalystTargetData }) {
  const isUp = d.direction === 'up';
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-[#f0f0f0] last:border-b-0 hover:bg-[#f2f4f6] px-1 transition-colors cursor-pointer">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-[#191f28]">{d.stock}</span>
          <span className="text-xs text-[#8b95a1]">{d.firm} {d.analyst}</span>
        </div>
        <div className="flex items-center gap-1 mt-0.5">
          <span className="text-xs text-[#8b95a1]">{d.prev}</span>
          <span className="text-xs text-[#8b95a1]">→</span>
          <span className={`text-xs font-semibold ${isUp ? 'text-[#00c853]' : 'text-[#2563eb]'}`}>
            {d.next} {isUp ? '↗' : '↘'}
          </span>
        </div>
      </div>
      <span className="text-[10px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium flex-shrink-0">
        적중 {d.accuracy}%
      </span>
    </div>
  );
}