'use client';

import SignalTag from './SignalTag';
import MiniSparkline from './MiniSparkline';

export interface SignalScoreData {
  rank: number;
  stock: string;
  score: number;
  tags: { label: string; score: number }[];
  price: string;
  change: string;
  sparkData: number[];
}

export default function SignalScoreItem({ data: d }: { data: SignalScoreData }) {
  const isPositive = d.change.startsWith('+');
  const barWidth = Math.min(d.score, 100);
  const barColor = d.score >= 80 ? '#00c853' : d.score >= 60 ? '#3182f6' : '#eab308';

  return (
    <div className="flex items-center gap-3 py-3 border-b border-[#f0f0f0] last:border-b-0 hover:bg-[#f2f4f6] px-2 transition-colors cursor-pointer">
      {/* Rank */}
      <span className={`text-lg font-bold w-6 text-center flex-shrink-0 ${d.rank <= 3 ? 'text-[#3182f6]' : 'text-[#8b95a1]'}`}>
        {d.rank}
      </span>

      {/* Score bar + info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-bold text-sm text-[#191f28]">{d.stock}</span>
          <span className="text-xs font-bold text-[#3182f6]">{d.score}점</span>
          <div className="flex-1 h-1.5 bg-[#f2f4f6] rounded-full overflow-hidden">
            <div className="h-full rounded-full" style={{ width: `${barWidth}%`, backgroundColor: barColor }} />
          </div>
        </div>
        <div className="flex gap-1 flex-wrap">
          {d.tags.map((t, i) => (
            <SignalTag key={i} label={t.label} score={t.score} />
          ))}
        </div>
      </div>

      {/* Price + sparkline */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <MiniSparkline data={d.sparkData} color={isPositive ? '#00c853' : '#f44336'} />
        <div className="text-right">
          <p className="text-xs font-bold text-[#191f28]">{d.price}</p>
          <p className={`text-[10px] font-semibold ${isPositive ? 'text-[#00c853]' : 'text-[#f44336]'}`}>{d.change}</p>
        </div>
      </div>
    </div>
  );
}