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
          <h2 className="font-bold text-lg">리포???�세</h2>
          <button 
            onClick={onClose}
            className="text-[#8b95a1] hover:text-gray-700 text-xl"
          >
            ??          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Stock & Title */}
          <div>
            <h3 className="font-bold text-xl text-[#191f28] mb-1">{report.stockName}</h3>
            <p className="text-gray-700 mb-2">{report.title}</p>
            <p className="text-sm text-gray-600">
              {report.firm} ??{report.analystName} ??{report.date}
            </p>
          </div>

          {/* Full AI Summary */}
          <div className="bg-[#f2f4f6] p-4 rounded-2xl">
            <h4 className="font-semibold mb-2">AI 분석 ?�약</h4>
            <p className="text-sm text-gray-700 leading-relaxed">
              {report.aiSummaryFull}
            </p>
          </div>

          {/* Target Price History */}
          {report.id === '1' && (
            <div>
              <h4 className="font-semibold mb-3">목표가 ?�스?�리</h4>
              <div className="bg-[#f2f4f6] rounded-2xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-[#f2f4f6]">
                    <tr>
                      <th className="text-left p-2 font-medium">?�짜</th>
                      <th className="text-left p-2 font-medium">목표가</th>
                      <th className="text-left p-2 font-medium">?�널리스??/th>
                    </tr>
                  </thead>
                  <tbody>
                    {targetPriceHistory.map((item, index) => (
                      <tr key={index} className="border-t border-gray-200">
                        <td className="p-2">{item.date}</td>
                        <td className="p-2 font-medium">
                          {item.price.toLocaleString()}??                        </td>
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
            <div className="border border-gray-200 rounded-2xl p-3">
              <h4 className="font-semibold mb-2">?�널리스???�로??/h4>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="font-medium text-blue-700">
                    {analyst.name.charAt(0)}
                  </span>
                </div>
                <div>
                  <p className="font-medium">{analyst.name}</p>
                  <p className="text-sm text-gray-600">{analyst.firm} ??{analyst.sector}</p>
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
            <h4 className="font-semibold mb-3">?�일종목 ?�른 ?�널리스??/h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-[#f2f4f6] rounded">
                <div>
                  <span className="font-medium text-sm">박XX (미래?�셋)</span>
                  <span className="text-xs text-gray-600 ml-2">목표가 195,000??/span>
                </div>
                <div className="flex items-center space-x-1">
                  <StarRating rating={3} size="sm" />
                  <span className="text-xs">67%</span>
                </div>
              </div>
              <div className="flex items-center justify-between p-2 bg-[#f2f4f6] rounded">
                <div>
                  <span className="font-medium text-sm">?�YY (KB증권)</span>
                  <span className="text-xs text-gray-600 ml-2">목표가 185,000??/span>
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
            <h4 className="font-semibold mb-3">??리포???�의?</h4>
            <div className="mb-3">
              <div className="flex items-center justify-between text-sm mb-1">
                <span>?�의</span>
                <span>72%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '72%' }}></div>
              </div>
              <div className="flex items-center justify-between text-sm mt-1">
                <span className="text-gray-600">비동??28%</span>
                <span className="text-gray-600">�?147�?참여</span>
              </div>
            </div>
            
            {/* Sample Comments */}
            <div className="space-y-2 text-sm">
              <div className="bg-[#f2f4f6] p-2 rounded">
                <span className="font-medium">?�자고수</span>
                <span className="text-gray-600 ml-2">HBM ?�혜 맞는?? ?�적 좋아�?�?같아??/span>
              </div>
              <div className="bg-[#f2f4f6] p-2 rounded">
                <span className="font-medium">주린??/span>
                <span className="text-gray-600 ml-2">210,000?��? ?�무 ?��? �??�닌가??</span>
              </div>
            </div>
          </div>

          {/* Related Influencer */}
          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-3">
            <div className="flex items-center space-x-2">
              <span className="text-blue-600">?��</span>
              <span className="text-sm text-blue-700">
                <span className="font-medium">코린?�아�?/span>????종목 콜함
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}