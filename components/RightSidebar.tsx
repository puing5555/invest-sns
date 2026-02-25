'use client';

const trendingStocks = [
  { stock: '에코프로', change: '+3.2%', isUp: true },
  { stock: 'SK하이닉스', change: '+1.8%', isUp: true },
  { stock: '삼성전자', change: '+0.8%', isUp: true },
  { stock: '아이빔테크놀로지', change: '+5.1%', isUp: true },
  { stock: 'HD한국조선해양', change: '+2.1%', isUp: true },
  { stock: '셀트리온', change: '-0.5%', isUp: false },
];

const marketNews = [
  { title: 'NVIDIA 실적 발표 임박, AI 관련주 주목', time: '12분 전' },
  { title: '한국은행 기준금리 동결 결정', time: '35분 전' },
  { title: '비트코인 $45,000 돌파, 알트코인 강세', time: '1시간 전' },
];

export default function RightSidebar() {
  return (
    <div className="hidden xl:flex flex-col w-[320px] h-screen bg-white border-l border-[#e8e8e8] sticky top-0 overflow-y-auto">
      {/* Trending Stocks */}
      <div className="p-4 border-b border-[#e8e8e8]">
        <h2 className="font-bold text-lg text-[#191f28] mb-3">🔥 실시간 급등주</h2>
        <div className="space-y-3">
          {trendingStocks.map((item, i) => (
            <div key={i} className="flex items-center justify-between p-2 hover:bg-[#f2f4f6] rounded-xl cursor-pointer">
              <span className="font-medium text-sm text-[#191f28]">{item.stock}</span>
              <span className={`text-xs font-semibold ${
                item.isUp ? 'text-[#00c853]' : 'text-[#f44336]'
              }`}>
                {item.change}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Market News */}
      <div className="p-4">
        <h2 className="font-bold text-lg text-[#191f28] mb-3">📰 시장 속보</h2>
        <div className="space-y-3">
          {marketNews.map((news, i) => (
            <div key={i} className="p-2 hover:bg-[#f2f4f6] rounded-xl cursor-pointer">
              <p className="text-sm text-[#191f28] mb-1">{news.title}</p>
              <span className="text-xs text-[#8b95a1]">{news.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}