'use client';

interface SignalTagProps {
  label: string;
  score: number;
}

export default function SignalTag({ label, score }: SignalTagProps) {
  return (
    <span className="inline-flex items-center gap-0.5 text-[10px] bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full whitespace-nowrap">
      {label} <span className="text-[#3182f6] font-semibold">+{score}</span>
    </span>
  );
}
