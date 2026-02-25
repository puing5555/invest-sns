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
        "?¼ì„±?„ìê°€ ?Œìš´?œë¦¬ 2?˜ë…¸ ê³µì •?ì„œ 40% ?˜ìœ¨???¬ì„±?˜ë©° ?…ê³„ ìµœì´ˆ ê¸°ë¡",
        "ê´€???¥ë¹„ì£¼ì¸ ?œë?ë°˜ë„ì²? ì£¼ì„±?”ì??ˆì–´ë§??±ì˜ ì£¼ê? ?ìŠ¹ ê¸°ë?",
        "ë°˜ë„ì²??œì¡° ê²½ìŸ??ê°•í™”ë¡?TSMC ?€ë¹??°ìœ„ ?•ë³´ ê°€?¥ì„±"
      ];
    }
    return [
      "ì£¼ìš” ?œì¥ ?™í–¥ê³??í–¥ ?”ì¸ ë¶„ì„ ì¤?,
      "ê´€??ì¢…ëª©?¤ì˜ ì£¼ê? ?€ì§ì„ ëª¨ë‹ˆ?°ë§ ?„ìš”",
      "ì¶”ê? ?•ë³´ ?…ë°?´íŠ¸ ?ˆì •"
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
            className="absolute top-4 right-4 text-[#8b95a1] hover:text-gray-600 text-xl"
          >
            ??
          </button>

          {/* News title */}
          <h1 className="text-xl font-bold text-[#191f28] mb-4 pr-8">
            {news.title}
          </h1>

          {/* Source, time, and sentiment */}
          <div className="flex items-center justify-between mb-6">
            <div className="text-sm text-[#8b95a1]">
              <span>{news.source}</span>
              <span className="mx-2">??/span>
              <span>{news.time}</span>
            </div>
            <SentimentBadge sentiment={news.sentiment} size="md" />
          </div>

          {/* AI 3ì¤??”ì•½ */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-[#191f28] mb-3">AI 3ì¤??”ì•½</h2>
            <div className="bg-[#f5f6f8] rounded-2xl p-4">
              <ul className="space-y-2">
                {get3LineSummary(news.id).map((point, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start">
                    <span className="mr-2 text-[#3182f6] font-bold">??/span>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          </section>

          {/* AI ?ì„¸ ?í–¥ ë¶„ì„ */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-[#191f28] mb-3">AI ?ì„¸ ?í–¥ ë¶„ì„</h2>
            <div className="text-sm text-gray-700 leading-relaxed">
              <p className="mb-2">{news.aiAnalysis}</p>
              <p>
                ?´ë²ˆ ?´ìŠ¤??ê´€???…ê³„?€ ?¬ì?ë“¤?ê²Œ ì¤‘ìš”???˜ë?ë¥?ê°€ì§€ë©? 
                ?¨ê¸°?ìœ¼ë¡œëŠ” ê´€??ì¢…ëª©?¤ì˜ ì£¼ê? ë³€?™ì„±??ì¦ê???ê²ƒìœ¼ë¡??ˆìƒ?©ë‹ˆ?? 
                ?¥ê¸°??ê´€?ì—??ì§€?ì ??ëª¨ë‹ˆ?°ë§???„ìš”?©ë‹ˆ??
              </p>
            </div>
          </section>

          {/* ê´€??ì¢…ëª© ê°€ê²?ë³€??*/}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-[#191f28] mb-3">ê´€??ì¢…ëª© ê°€ê²?ë³€??/h2>
            <div className="space-y-3">
              {getStockPriceChanges().map((stock, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-[#f2f4f6] rounded-2xl">
                  <div>
                    <div className="font-medium text-[#191f28]">{stock.name}</div>
                    <div className="text-sm text-[#8b95a1]">{stock.price.toLocaleString()}??/div>
                  </div>
                  <div className="text-right">
                    <div className={`font-medium ${stock.change >= 0 ? 'text-red-600' : 'text-blue-600'}`}>
                      {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(0)}??
                    </div>
                    <div className={`text-sm ${stock.changePercent >= 0 ? 'text-red-600' : 'text-blue-600'}`}>
                      {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ê´€??ê³µì‹œ */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-[#191f28] mb-3">ê´€??ê³µì‹œ</h2>
            <div className="text-sm text-[#8b95a1] bg-[#f2f4f6] rounded-2xl p-4">
              {news.id === 1 ? (
                <div>
                  <p className="font-medium text-gray-700 mb-2">ìµœê·¼ ê´€??ê³µì‹œ</p>
                  <p>???¼ì„±?„ì - ë°˜ë„ì²??¬ì—…ë¶€ ?¬ìê³„íš ê³µì‹œ (2024.12.15)</p>
                  <p>???œë?ë°˜ë„ì²?- ?¥ë¹„ ê³µê¸‰ê³„ì•½ ì²´ê²° ê³µì‹œ (2024.12.20)</p>
                </div>
              ) : (
                <p>ê´€??ê³µì‹œ ?†ìŒ</p>
              )}
            </div>
          </section>

          {/* ì»¤ë??ˆí‹° ë°˜ì‘ */}
          <section className="mb-6">
            <h2 className="text-lg font-semibold text-[#191f28] mb-3">ì»¤ë??ˆí‹° ë°˜ì‘</h2>
            <div className="space-y-4">
              <div className="bg-[#f2f4f6] rounded-2xl p-4">
                <div className="flex items-center mb-2">
                  <div className="w-8 h-8 bg-[#3182f6] rounded-full flex items-center justify-center text-white text-sm font-medium">
                    ??
                  </div>
                  <div className="ml-3">
                    <div className="font-medium text-[#191f28]">?¬ìê³ ìˆ˜</div>
                    <div className="text-xs text-[#8b95a1]">5ë¶???/div>
                  </div>
                </div>
                <p className="text-sm text-gray-700">
                  ?´ë²ˆ ?´ìŠ¤???•ë§ ì¤‘ìš”???œì‚¬?ì´ ?ˆë„¤?? ê´€??ì¢…ëª©??ê´€???ˆê²Œ ì§€ì¼œë´?¼ê² ?µë‹ˆ??
                </p>
              </div>

              <div className="bg-[#f2f4f6] rounded-2xl p-4">
                <div className="flex items-center mb-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    ì£?
                  </div>
                  <div className="ml-3">
                    <div className="font-medium text-[#191f28]">ì£¼ì‹?¬ë²„</div>
                    <div className="text-xs text-[#8b95a1]">12ë¶???/div>
                  </div>
                </div>
                <p className="text-sm text-gray-700">
                  AI ë¶„ì„??ê½??•í™•??ê²?ê°™ì•„?? ?¥ê¸°?ìœ¼ë¡?ë´ì•¼ ???´ìŠ¤?¤ìš”.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </>
  );
}