'use client';

export default function InsiderTradeCard() {
  return (
    <div className="bg-white border border-[#f0f0f0] rounded-2xl p-4 hover:bg-[#f2f4f6] transition-colors cursor-pointer shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-[#191f28]">삼성전자</span>
          <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full font-medium">임원 매수</span>
        </div>
        <span className="text-xs text-[#8b95a1]">02/23~02/25</span>
      </div>
      <p className="text-sm text-gray-700 mb-1">임원 부사장 김OO 外 50,000주(약 35억)</p>
      <p className="text-xs text-orange-500 font-medium mb-2">최근 3일 연속 매수 감지</p>
      <p className="text-xs text-[#3182f6]">🤖 AI: &ldquo;실적 발표 전 임원 연속매수, 과거 75% 서프라이즈 반복&rdquo;</p>
    </div>
  );
}