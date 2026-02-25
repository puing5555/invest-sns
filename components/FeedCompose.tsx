'use client';

export default function FeedCompose() {
  return (
    <div className="px-4 py-3 border-b border-[#eff3f4]">
      <div className="flex gap-3">
        {/* Avatar */}
        <div className="w-10 h-10 rounded-full bg-[#00d4aa] flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
          Y
        </div>
        {/* Input area */}
        <div className="flex-1 min-w-0">
          <textarea
            placeholder="무슨 일이 일어나고 있나요?"
            className="w-full resize-none border-none outline-none text-[15px] text-gray-800 placeholder-gray-500 bg-transparent py-2 min-h-[52px]"
            rows={2}
          />
          <div className="flex items-center justify-between pt-2 border-t border-[#eff3f4]">
            <div className="flex items-center gap-1">
              {['🖼', 'GIF', '📊', '😊', '📅', '📍'].map((icon, i) => (
                <button
                  key={i}
                  className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#e8f5e9] text-[#00d4aa] text-sm transition-colors"
                >
                  {icon}
                </button>
              ))}
              <button className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#e8f5e9] text-[#00d4aa] text-sm font-bold transition-colors">
                B
              </button>
              <button className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#e8f5e9] text-[#00d4aa] text-sm italic font-serif transition-colors">
                I
              </button>
            </div>
            <button className="bg-[#00d4aa] text-white font-bold text-sm px-5 py-1.5 rounded-full hover:bg-[#00b894] transition-colors">
              게시하기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
