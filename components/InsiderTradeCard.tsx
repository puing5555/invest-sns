'use client';

export default function InsiderTradeCard() {
  return (
    <div className="bg-white border border-[#eff3f4] rounded-xl p-4 hover:bg-gray-50 transition-colors cursor-pointer">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-gray-900">삼성전자</span>
          <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full font-medium">🟢 매수</span>
        </div>
        <span className="text-xs text-gray-400">02/23~02/25</span>
      </div>
      <p className="text-sm text-gray-700 mb-1">👔 부사장 김OO — 50,000주 (약 35억)</p>
      <p className="text-xs text-orange-500 font-medium mb-2">📅 3일 연속 매수 중 🔥</p>
      <p className="text-xs text-[#00d4aa]">🤖 AI: &ldquo;실적 발표 전 임원 연속매수, 과거 75% 서프라이즈 동반&rdquo;</p>
    </div>
  );
}
