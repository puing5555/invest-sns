'use client';

interface Report {
  ticker: string;
  firm: string;
  analyst: string | null;
  title: string;
  target_price: number | null;
  opinion: string;
  published_at: string;
  pdf_url: string;
  summary?: string;
}

interface TargetPriceChartProps {
  reports: Report[];
  stockName: string;
}

export default function TargetPriceChart({ reports, stockName }: TargetPriceChartProps) {
  // 목표가가 있는 리포트만 필터링하고 증권사별로 그룹화
  const reportsWithPrice = reports.filter(r => r.target_price && r.target_price > 0);
  
  if (reportsWithPrice.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm text-center">
        <p className="text-gray-500 text-sm">목표가 데이터가 없습니다</p>
      </div>
    );
  }

  // 증권사별 최신 목표가
  const firmTargets = new Map<string, { price: number; date: string; opinion: string }>();
  
  reportsWithPrice.forEach(report => {
    const existing = firmTargets.get(report.firm);
    if (!existing || report.published_at > existing.date) {
      firmTargets.set(report.firm, {
        price: report.target_price!,
        date: report.published_at,
        opinion: report.opinion
      });
    }
  });

  const firmData = Array.from(firmTargets.entries())
    .map(([firm, data]) => ({ firm, ...data }))
    .sort((a, b) => b.price - a.price);

  const maxPrice = Math.max(...firmData.map(d => d.price));
  const minPrice = Math.min(...firmData.map(d => d.price));
  const priceRange = maxPrice - minPrice;

  const getOpinionColor = (opinion: string) => {
    switch (opinion) {
      case 'BUY': return 'bg-green-500';
      case 'HOLD': return 'bg-yellow-500';
      case 'SELL': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const formatPrice = (price: number) => {
    if (price >= 10000) {
      return `${Math.floor(price / 10000)}만원`;
    } else if (price >= 1000) {
      return `${Math.floor(price / 1000)}천원`;
    }
    return `${price}원`;
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900">📊 증권사별 목표가 비교</h3>
        <span className="text-sm text-gray-500">{stockName}</span>
      </div>

      <div className="space-y-4">
        {firmData.map((item, index) => {
          const barWidth = priceRange > 0 ? ((item.price - minPrice) / priceRange) * 100 : 100;
          const widthPercent = Math.max(barWidth, 10); // 최소 10% 폭 보장
          
          return (
            <div key={item.firm} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700">{item.firm}</span>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full text-white ${getOpinionColor(item.opinion)}`}>
                    {item.opinion}
                  </span>
                  <span className="font-bold text-gray-900">{formatPrice(item.price)}</span>
                </div>
              </div>
              
              <div className="relative">
                <div className="w-full h-8 bg-gray-100 rounded-lg overflow-hidden">
                  <div 
                    className={`h-full ${getOpinionColor(item.opinion)} transition-all duration-500 ease-out flex items-center justify-end px-2`}
                    style={{ width: `${widthPercent}%` }}
                  >
                    {widthPercent > 30 && (
                      <span className="text-white text-xs font-medium">
                        {formatPrice(item.price)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="text-xs text-gray-400 text-right">
                {new Date(item.date).toLocaleDateString('ko-KR', { 
                  year: '2-digit', 
                  month: '2-digit', 
                  day: '2-digit' 
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>평균 목표가</span>
          <span className="font-medium text-gray-700">
            {formatPrice(Math.round(firmData.reduce((sum, item) => sum + item.price, 0) / firmData.length))}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm text-gray-500 mt-1">
          <span>목표가 범위</span>
          <span className="font-medium text-gray-700">
            {formatPrice(minPrice)} ~ {formatPrice(maxPrice)}
          </span>
        </div>
      </div>
    </div>
  );
}