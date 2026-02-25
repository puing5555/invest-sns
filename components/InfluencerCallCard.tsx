'use client';

export interface InfluencerCallData {
  name: string;
  initial: string;
  hitRate: number;
  stock: string;
  action: '매수' | '매도';
  returnRate: string;
}

export default function InfluencerCallCard({ d }: { d: InfluencerCallData }) {
  const isPositive = d.returnRate.startsWith('+');
  return (
    <div className="bg-white border border-[#f0f0f0] rounded-2xl p-3 min-w-[200px] w-[200px] flex-shrink-0 hover:bg-[#f2f4f6] transition-colors cursor-pointer">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-full bg-[#1a1a2e] flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
          {d.initial}
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold text-[#191f28] truncate">{d.name}</p>
          <span className="text-[10px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded-full font-medium">
            ?�중 {d.hitRate}%
          </span>
        </div>
      </div>
      <p className="font-bold text-sm text-[#191f28] mb-1">{d.stock}</p>
      <div className="flex items-center justify-between">
        <span
          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
            d.action === '매수'
              ? 'bg-[#dcfce7] text-[#00c853]'
              : 'bg-[#fee2e2] text-[#f44336]'
          }`}
        >
          {d.action}
        </span>
        <span
          className={`text-xs font-semibold ${isPositive ? 'text-[#00c853]' : 'text-[#f44336]'}`}
        >
          {d.returnRate}
        </span>
      </div>
    </div>
  );
}
