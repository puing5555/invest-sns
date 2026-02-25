'use client';

export default function SignalSummary() {
  const today = new Date();
  const dateStr = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`;

  return (
    <div className="bg-white border border-[#f0f0f0] rounded-2xl overflow-hidden">
      <div className="flex">
        <div className="w-1 bg-[#3182f6] flex-shrink-0" />
        <div className="p-4">
          <h2 className="font-bold text-[#191f28] text-[15px]">?“¡ {dateStr} ?œê·¸??/h2>
          <p className="text-sm text-gray-600 mt-1">
            <span className="text-[#f44336] font-semibold">A?±ê¸‰ ê³µì‹œ 3ê±?/span>
            {' | '}
            <span className="text-[#3182f6] font-semibold">?¸í”Œë£¨ì–¸??ì½?2ê±?/span>
            {' | '}
            <span className="text-blue-500 font-semibold">AI ì£¼ëª© 1ê±?/span>
            {' | '}
            <span className="text-orange-500 font-semibold">? ë„ ?í–¥ 4ê±?/span>
          </p>
        </div>
      </div>
    </div>
  );
}
