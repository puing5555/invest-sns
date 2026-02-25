'use client';

export default function SignalSummary() {
  const today = new Date();
  const dateStr = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`;

  return (
    <div className="bg-white border border-[#f0f0f0] rounded-lg overflow-hidden">
      <div className="flex">
        <div className="w-1 bg-[#3182f6] flex-shrink-0" />
        <div className="p-4">
          <h2 className="font-bold text-gray-900 text-[15px]">📡 {dateStr} 시그널</h2>
          <p className="text-sm text-gray-600 mt-1">
            <span className="text-[#ff4444] font-semibold">A등급 공시 3건</span>
            {' | '}
            <span className="text-[#3182f6] font-semibold">인플루언서 콜 2건</span>
            {' | '}
            <span className="text-blue-500 font-semibold">AI 주목 1건</span>
            {' | '}
            <span className="text-orange-500 font-semibold">애널 상향 4건</span>
          </p>
        </div>
      </div>
    </div>
  );
}
