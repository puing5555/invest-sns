import { Analyst, reports } from '@/data/analystData';
import AccuracyCircle from './AccuracyCircle';
import StarRating from './StarRating';

interface AnalystCardProps {
  analyst: Analyst;
  onClick: () => void;
}

export default function AnalystCard({ analyst, onClick }: AnalystCardProps) {
  const trustBadgeConfig = {
    verified: { text: '🔵 검증됨', color: 'text-blue-600' },
    accumulating: { text: '🟡 축적중', color: 'text-yellow-600' }
  };

  const badge = trustBadgeConfig[analyst.trustBadge];

  // Get recent reports details
  const recentReports = analyst.recentReports
    .map(reportId => reports.find(r => r.id === reportId))
    .filter(Boolean)
    .slice(0, 2);

  return (
    <div 
      className="bg-white rounded-xl shadow-sm p-4 cursor-pointer hover:shadow-md transition-shadow border border-gray-100"
      onClick={onClick}
    >
      {/* Header with avatar, name, firm */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="font-bold text-blue-700 text-lg">
              {analyst.name.charAt(0)}
            </span>
          </div>
          <div>
            <h3 className="font-bold text-gray-900">{analyst.name}</h3>
            <p className="text-sm text-gray-600">{analyst.firm}</p>
          </div>
        </div>
        <AccuracyCircle 
          percentage={analyst.accuracy}
          successful={analyst.successful}
          total={analyst.total}
          size={56}
        />
      </div>

      {/* Sector badge */}
      <div className="mb-3">
        <span className="inline-block bg-gray-100 text-gray-700 text-xs font-medium px-2 py-1 rounded-full">
          {analyst.sector}
        </span>
      </div>

      {/* Stats row */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <StarRating rating={analyst.starRating} size="sm" />
          <span className={`text-sm font-medium ${badge.color}`}>
            {badge.text}
          </span>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">평균 수익률</p>
          <p className="font-bold text-green-600">+{analyst.avgReturn}%</p>
        </div>
      </div>

      {/* Recent reports */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-2">최근 리포트</h4>
        <div className="space-y-2">
          {recentReports.map((report, index) => (
            <div key={index} className="bg-gray-50 p-2 rounded text-xs">
              <div className="flex items-center justify-between">
                <span className="font-medium">{report?.stockName}</span>
                <span className={`font-medium ${
                  report?.changeType === 'up' ? 'text-green-600' : 
                  report?.changeType === 'down' ? 'text-red-600' : 
                  report?.changeType === 'new' ? 'text-blue-600' : 'text-gray-600'
                }`}>
                  {report?.changeType === 'up' && '상향'}
                  {report?.changeType === 'down' && '하향'}
                  {report?.changeType === 'new' && '신규'}
                  {report?.changeType === 'maintain' && '유지'}
                </span>
              </div>
              <p className="text-gray-600 truncate mt-1">{report?.title}</p>
            </div>
          ))}
          {recentReports.length === 0 && (
            <p className="text-xs text-gray-500 py-2">최근 리포트 없음</p>
          )}
        </div>
      </div>
    </div>
  );
}