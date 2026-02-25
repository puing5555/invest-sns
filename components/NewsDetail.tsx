import { NewsData } from '../data/newsData';
import SentimentBadge from './SentimentBadge';

interface NewsDetailProps {
  news: NewsData | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function NewsDetail({ news, isOpen, onClose }: NewsDetailProps) {
  if (!news) return null;

  const get3LineSummary = (newsId: number) => {
    if (newsId === 1) {
      return [
        "삼성전자가 파운드리 2나노 공정에서 40% 수율을 달성하며 업계 최초 기록",
        "관련 장비주인 한미반도체, 주성엔지니어링 등의 주가 상승 기대",
        "반도체 제조 경쟁력 강화로 TSMC 대비 우위 확보 가능성"
      ];
    }
    return [
      "주요 시장 동향과 영향 요인 분석 중",
      "관련 종목들의 주가 움직임 모니터링 필요",
      "추가 정보 업데이트 예정"
    ];
  };

  const getStockPriceChanges = () => {
    return news.relatedStocks.map((stock) => ({
      name: stock,
      price: Math.floor(Math.random() * 100000) + 50000,
      change: (Math.random() - 0.5) * 10,
      changePercent: (Math.random() - 0.5) * 5
    }));
  };

  return (
    <>
      {/* Dark overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={onClose}
        />
      )}

      {/* Slide-in panel */}
      <div
        className={`fixed top-0 right-0 h-full w-[400px] bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out overflow-y-auto ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="p-6">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl"
          >
            ✕
          </button>

          {/* News title */}
          <h1 className="text-xl font-bold text-gray-900 mb-4 pr-8">
            {news.title}
          </h1>

          {/* Source, time, and sentiment */}
          <div className="flex items-center justify-between mb-6">
            <div className="text-sm text-gray-500">
              <span>{news.source}</span>
              <span className="mx-2">•</span>
              <span>{news.time}</span>
            </div>
            <SentimentBadge sentiment={news.sentiment} size="md" />
          </div>

          {/* AI 3줄 요약 */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">AI 3줄 요약</h2>
            <div className="bg-[#f5f6f8] rounded-lg p-4">
              <ul className="space-y-2">
                {get3LineSummary(news.id).map((point, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start">
                    <span className="mr-2 text-[#00d4aa] font-bold">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          </section>

          {/* AI 상세 영향 분석 */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">AI 상세 영향 분석</h2>
            <div className="text-sm text-gray-700 leading-relaxed">
              <p className="mb-2">{news.aiAnalysis}</p>
              <p>
                이번 뉴스는 관련 업계와 투자자들에게 중요한 의미를 가지며, 
                단기적으로는 관련 종목들의 주가 변동성이 증가할 것으로 예상됩니다. 
                장기적 관점에서 지속적인 모니터링이 필요합니다.
              </p>
            </div>
          </section>

          {/* 관련 종목 가격 변동 */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">관련 종목 가격 변동</h2>
            <div className="space-y-3">
              {getStockPriceChanges().map((stock, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{stock.name}</div>
                    <div className="text-sm text-gray-500">{stock.price.toLocaleString()}원</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-medium ${stock.change >= 0 ? 'text-red-600' : 'text-blue-600'}`}>
                      {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(0)}원
                    </div>
                    <div className={`text-sm ${stock.changePercent >= 0 ? 'text-red-600' : 'text-blue-600'}`}>
                      {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 관련 공시 */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">관련 공시</h2>
            <div className="text-sm text-gray-500 bg-gray-50 rounded-lg p-4">
              {news.id === 1 ? (
                <div>
                  <p className="font-medium text-gray-700 mb-2">최근 관련 공시</p>
                  <p>• 삼성전자 - 반도체 사업부 투자계획 공시 (2024.12.15)</p>
                  <p>• 한미반도체 - 장비 공급계약 체결 공시 (2024.12.20)</p>
                </div>
              ) : (
                <p>관련 공시 없음</p>
              )}
            </div>
          </section>

          {/* 커뮤니티 반응 */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">커뮤니티 반응</h2>
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <div className="w-8 h-8 bg-[#00d4aa] rounded-full flex items-center justify-center text-white text-sm font-medium">
                    투
                  </div>
                  <div className="ml-3">
                    <div className="font-medium text-gray-900">투자고수</div>
                    <div className="text-xs text-gray-500">5분 전</div>
                  </div>
                </div>
                <p className="text-sm text-gray-700">
                  이번 뉴스는 정말 중요한 시사점이 있네요. 관련 종목들 관심 있게 지켜봐야겠습니다.
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    주
                  </div>
                  <div className="ml-3">
                    <div className="font-medium text-gray-900">주식러버</div>
                    <div className="text-xs text-gray-500">12분 전</div>
                  </div>
                </div>
                <p className="text-sm text-gray-700">
                  AI 분석이 꽤 정확한 것 같아요. 장기적으로 봐야 할 뉴스네요.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </>
  );
}