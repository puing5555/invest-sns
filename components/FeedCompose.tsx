'use client';

export default function FeedCompose() {
  return (
    <div className="px-4 py-3 border-b border-[#f0f0f0]">
      <div className="flex gap-3">
        {/* Avatar */}
        <div className="w-10 h-10 rounded-full bg-[#3182f6] flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
          Y
        </div>
        {/* Input area */}
        <div className="flex-1 min-w-0">
          <textarea
            placeholder="무슨 일이 일어나고 있나요?"
            className="w-full resize-none border-none outline-none text-[15px] text-gray-800 placeholder-gray-500 bg-transparent py-2 min-h-[52px]"
            rows={2}
          />
          <div className="flex items-center justify-between pt-2 border-t border-[#f0f0f0]">
            <div className="flex items-center gap-1">
              {['🖼️', 'GIF', '📊', '😀', '📅', '📍'].map((icon, i) => (
                <button key={i} className="p-2 hover:bg-[#f2f4f6] rounded-full transition-colors text-[#3182f6]">
                  <span className="text-lg">{icon}</span>
                </button>
              ))}
            </div>
            <button className="bg-[#3182f6] text-white px-5 py-1.5 rounded-2xl text-[14px] font-semibold hover:bg-[#1b64da] transition-colors">
              게시
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}