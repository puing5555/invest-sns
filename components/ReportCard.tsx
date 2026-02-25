import { Report } from '@/data/analystData';
import StarRating from './StarRating';

interface ReportCardProps {
  report: Report;
  onClick: () => void;
}

export default function ReportCard({ report, onClick }: ReportCardProps) {
  const getChangeColor = (type: string) => {
    switch (type) {
      case 'up': return 'border-green-500';
      case 'down': return 'border-red-500';
      case 'new': return 'border-blue-500';
      default: return 'border-gray-400';
    }
  };

  const getPriceChangeDisplay = () => {
    if (report.changeType === 'new') {
      return (
        <div className="flex items-center space-x-1">
          <span className="text-blue-600 font-medium">?�규커버</span>
          <span className="text-blue-600 text-lg">?��</span>
          <span className="font-bold">{report.targetPriceNew.toLocaleString()}??/span>
        </div>
      );
    }

    const arrow = report.changeType === 'up' ? '?�️' : '?�️';
    const color = report.changeType === 'up' ? 'text-green-600' : 'text-red-600';

    return (
      <div className={`flex items-center space-x-1 ${color}`}>
        <span className="text-lg">{arrow}</span>
        <span className="line-through opacity-60">
          {report.targetPriceOld?.toLocaleString()}
        </span>
        <span>??/span>
        <span className="font-bold">
          {report.targetPriceNew.toLocaleString()}??
        </span>
      </div>
    );
  };

  return (
    <div 
      className={`bg-white rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.04)] border-l-4 p-4 cursor-pointer hover:shadow-md transition-shadow ${getChangeColor(report.changeType)}`}
      onClick={onClick}
    >
      {/* Header with stock name and accuracy badge */}
      <div className="flex items-start justify-between mb-2">
        <div>
          <h3 className="font-bold text-lg text-[#191f28]">{report.stockName}</h3>
          <p className="text-gray-700">{report.title}</p>
        </div>
        <div className="flex items-center space-x-2 flex-shrink-0 ml-4">
          <StarRating rating={report.starRating} size="sm" />
          <span className="text-sm font-medium text-gray-700">
            {report.analystAccuracy}%
          </span>
        </div>
      </div>

      {/* Firm, analyst, date */}
      <div className="text-sm text-gray-600 mb-3">
        <span className="font-medium">{report.firm}</span>
        <span className="mx-2">??/span>
        <span>{report.analystName}</span>
        <span className="mx-2">??/span>
        <span>{report.date}</span>
      </div>

      {/* Target price change */}
      <div className="mb-3">
        {getPriceChangeDisplay()}
      </div>

      {/* AI Summary */}
      <div className="bg-[#f2f4f6] p-3 rounded-2xl mb-4">
        <p className="text-sm text-gray-700">{report.aiSummary}</p>
      </div>

      {/* Action buttons */}
      <div className="flex space-x-2">
        <button className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
          ?�세보기
        </button>
        <button className="px-3 py-1.5 text-sm border border-gray-300 text-gray-700 rounded-md hover:bg-[#f2f4f6] transition-colors">
          종목?�이지
        </button>
        <button className="px-3 py-1.5 text-sm border border-gray-300 text-gray-700 rounded-md hover:bg-[#f2f4f6] transition-colors">
          공유
        </button>
      </div>
    </div>
  );
}