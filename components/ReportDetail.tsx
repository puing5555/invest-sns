import { Report, analysts, targetPriceHistory } from '@/data/analystData';
import StarRating from './StarRating';
import AccuracyCircle from './AccuracyCircle';

interface ReportDetailProps {
  report: Report | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function ReportDetail({ report, isOpen, onClose }: ReportDetailProps) {
  if (!isOpen || !report) return null;

  const analyst = analysts.find(a => a.name === report.analystName);
  
  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div 
        className="flex-1 bg-black/20"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="w-[400px] bg-white h-full shadow-xl overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <h2 className="font-bold text-lg">리포트 상세</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Stock & Title */}
          <div>
            <h3 className="font-bold text-xl text-gray-900 mb-1">{report.stockName}</h3>
            <p className="text-gray-700 mb-2">{report.title}</p>
            <p className="text-sm text-gray-600">
              {report.firm} • {report.analystName} • {report.date}
            </p>
          </div>

          {/* Full AI Summary */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">AI 분석 요약</h4>
            <p className="text-sm text-gray-700 leading-relaxed">
              {report.aiSummaryFull}
            </p>
          </div>

          {/* Target Price History */}
          {report.id === '1' && (
            <div>
              <h4 className="font-semibold mb-3">목표가 히스토리</h4>
              <div className="bg-gray-50 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="text-left p-2 font-medium">날짜</th>
                      <th className="text-left p-2 font-medium">목표가</th>
                      <th className="text-left p-2 font-medium">애널리스트</th>
                    </tr>
                  </thead>
                  <tbody>
                    {targetPriceHistory.map((item, index) => (
                      <tr key={index} className="border-t border-gray-200">
                        <td className="p-2">{item.date}</td>
                        <td className="p-2 font-medium">
                          {item.price.toLocaleString()}원
                        </td>
                        <td className="p-2">{item.analyst} ({item.firm})</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Analyst Profile Mini Card */}
          {analyst && (
            <div className="border border-gray-200 rounded-lg p-3">
              <h4 className="font-semibold mb-2">애널리스트 프로필</h4>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="font-medium text-blue-700">
                    {analyst.name.charAt(0)}
                  </span>
                </div>
                <div>
                  <p className="font-medium">{analyst.name}</p>
                  <p className="text-sm text-gray-600">{analyst.firm} • {analyst.sector}</p>
                </div>
                <div className="flex-1 flex justify-end">
                  <AccuracyCircle 
                    percentage={analyst.accuracy}
                    successful={analyst.successful}
                    total={analyst.total}
                    size={48}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Same Stock Other Analysts */}
          <div>
            <h4 className="font-semibold mb-3">동일종목 다른 애널리스트</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div>
                  <span className="font-medium text-sm">박XX (미래에셋)</span>
                  <span className="text-xs text-gray-600 ml-2">목표가 195,000원</span>
                </div>
                <div className="flex items-center space-x-1">
                  <StarRating rating={3} size="sm" />
                  <span className="text-xs">67%</span>
                </div>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div>
                  <span className="font-medium text-sm">이YY (KB증권)</span>
                  <span className="text-xs text-gray-600 ml-2">목표가 185,000원</span>
                </div>
                <div className="flex items-center space-x-1">
                  <StarRating rating={4} size="sm" />
                  <span className="text-xs">59%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Community Vote */}
          <div>
            <h4 className="font-semibold mb-3">이 리포트 동의?</h4>
            <div className="mb-3">
              <div className="flex items-center justify-between text-sm mb-1">
                <span>동의</span>
                <span>72%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '72%' }}></div>
              </div>
              <div className="flex items-center justify-between text-sm mt-1">
                <span className="text-gray-600">비동의 28%</span>
                <span className="text-gray-600">총 147명 참여</span>
              </div>
            </div>
            
            {/* Sample Comments */}
            <div className="space-y-2 text-sm">
              <div className="bg-gray-50 p-2 rounded">
                <span className="font-medium">투자고수</span>
                <span className="text-gray-600 ml-2">HBM 수혜 맞는듯. 실적 좋아질 것 같아요</span>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <span className="font-medium">주린이</span>
                <span className="text-gray-600 ml-2">210,000원은 너무 높은 것 아닌가요?</span>
              </div>
            </div>
          </div>

          {/* Related Influencer */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <span className="text-blue-600">👤</span>
              <span className="text-sm text-blue-700">
                <span className="font-medium">코린이아빠</span>도 이 종목 콜함
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}