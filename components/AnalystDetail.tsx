import { Analyst } from '@/data/analystData';
import AccuracyCircle from './AccuracyCircle';
import StarRating from './StarRating';

interface AnalystDetailProps {
  analyst: Analyst | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function AnalystDetail({ analyst, isOpen, onClose }: AnalystDetailProps) {
  if (!isOpen || !analyst) return null;

  const trustBadgeConfig = {
    verified: { text: '🔵 검증됨', color: 'text-blue-600' },
    accumulating: { text: '🟡 축적중', color: 'text-yellow-600' }
  };

  const badge = trustBadgeConfig[analyst.trustBadge];

  // Mock data for stock-by-stock accuracy
  const stockAccuracy = [
    { stock: 'SK하이닉스', accuracy: 75 },
    { stock: '삼성전자', accuracy: 58 },
    { stock: 'LG에너지솔루션', accuracy: 64 }
  ];

  // Mock monthly accuracy data (6 months)
  const monthlyAccuracy = [
    { month: '9월', accuracy: 65 },
    { month: '10월', accuracy: 72 },
    { month: '11월', accuracy: 58 },
    { month: '12월', accuracy: 69 },
    { month: '1월', accuracy: 61 },
    { month: '2월', accuracy: 67 }
  ];

  // Mock report history
  const reportHistory = [
    { stock: 'SK하이닉스', target: 210000, current: 195000, return: 12.3 },
    { stock: '삼성전자', target: 85000, current: 78000, return: -3.2 },
    { stock: 'LG에너지솔루션', target: 420000, current: 445000, return: 18.7 },
    { stock: 'SK스퀘어', target: 65000, current: 61000, return: -5.1 },
    { stock: 'NAVER', target: 180000, current: 165000, return: -2.8 }
  ];

  // Get semiconductor analysts for comparison (for analyst with id '2')
  const semiAnalysts = analyst.id === '2' ? [
    { name: '김OO', firm: '한국투자', accuracy: 62 },
    { name: '박XX', firm: '미래에셋', accuracy: 67 },
    { name: '이YY', firm: 'KB증권', accuracy: 59 },
    { name: '최ZZ', firm: '삼성증권', accuracy: 71 },
    { name: '정AA', firm: 'NH투자', accuracy: 55 }
  ].sort((a, b) => b.accuracy - a.accuracy) : [];

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
          <h2 className="font-bold text-lg">애널리스트 상세</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Large Profile */}
          <div className="text-center">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="font-bold text-blue-700 text-2xl">
                {analyst.name.charAt(0)}
              </span>
            </div>
            <h3 className="font-bold text-xl text-gray-900 mb-1">{analyst.name}</h3>
            <p className="text-gray-600 mb-1">{analyst.firm} • {analyst.sector}</p>
            <p className="text-sm text-gray-500">활동기간: 2022.03 - 현재</p>
          </div>

          {/* Large AccuracyCircle + Stars */}
          <div className="flex items-center justify-center space-x-8">
            <AccuracyCircle 
              percentage={analyst.accuracy}
              successful={analyst.successful}
              total={analyst.total}
              size={80}
            />
            <div className="text-center">
              <StarRating rating={analyst.starRating} size="lg" />
              <p className={`text-sm font-medium mt-1 ${badge.color}`}>
                {badge.text}
              </p>
              <p className="text-lg font-bold text-green-600 mt-2">
                평균 +{analyst.avgReturn}%
              </p>
            </div>
          </div>

          {/* Stock-by-stock accuracy */}
          <div>
            <h4 className="font-semibold mb-3">종목별 적중률</h4>
            <div className="space-y-2">
              {stockAccuracy.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="font-medium text-sm">{item.stock}</span>
                  <span className={`font-bold text-sm ${
                    item.accuracy >= 60 ? 'text-green-600' : 
                    item.accuracy >= 50 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {item.accuracy}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Monthly accuracy chart */}
          <div>
            <h4 className="font-semibold mb-3">월별 적중률 추이</h4>
            <div className="space-y-2">
              {monthlyAccuracy.map((item, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <span className="w-8 text-sm font-medium">{item.month}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4 relative">
                    <div 
                      className={`h-4 rounded-full ${
                        item.accuracy >= 60 ? 'bg-green-500' : 
                        item.accuracy >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${item.accuracy}%` }}
                    />
                    <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
                      {item.accuracy}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Report history */}
          <div>
            <h4 className="font-semibold mb-3">리포트 히스토리</h4>
            <div className="space-y-2">
              {reportHistory.map((item, index) => (
                <div key={index} className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{item.stock}</span>
                    <span className={`font-bold text-sm ${
                      item.return >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {item.return >= 0 ? '+' : ''}{item.return}%
                    </span>
                  </div>
                  <div className="text-xs text-gray-600">
                    목표: {item.target.toLocaleString()}원 • 
                    현재: {item.current.toLocaleString()}원
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Comparison section (only for semiconductor analyst) */}
          {analyst.id === '2' && (
            <div>
              <h4 className="font-semibold mb-3">반도체 커버 애널 TOP5</h4>
              <div className="space-y-2">
                {semiAnalysts.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div>
                      <span className="font-medium text-sm">{item.name}</span>
                      <span className="text-xs text-gray-600 ml-2">({item.firm})</span>
                    </div>
                    <span className={`font-bold text-sm ${
                      item.accuracy >= 60 ? 'text-green-600' : 
                      item.accuracy >= 50 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      #{index + 1} {item.accuracy}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex space-x-3 pt-4">
            <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors">
              팔로우
            </button>
            <button className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors">
              알림설정
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}