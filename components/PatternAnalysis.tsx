import { PatternData } from '@/data/tradeData';

interface PatternAnalysisProps {
  pattern: PatternData;
}

export default function PatternAnalysis({ pattern }: PatternAnalysisProps) {
  const getBarColor = (percent: number) => {
    if (percent >= 60) return '#22c55e'; // Green
    if (percent >= 40) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  };

  const getBarWidth = (percent: number) => {
    return Math.min(Math.max(percent, 5), 100); // Minimum 5%, maximum 100%
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      {/* Title with count badge */}
      <div className="flex items-center gap-2 mb-3">
        <span className="font-medium text-gray-900">{pattern.category}</span>
        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
          {pattern.count}건
        </span>
      </div>

      {/* Pattern stats */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">1주후 반등률</span>
          <div className="flex items-center gap-2 flex-1 ml-4">
            <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
              <div 
                className="absolute left-0 top-0 h-full rounded-full"
                style={{ 
                  backgroundColor: getBarColor(pattern.weekRebound),
                  width: `${getBarWidth(pattern.weekRebound)}%`
                }}
              />
            </div>
            <span className="text-sm font-medium text-gray-900 w-10 text-right">
              {pattern.weekRebound}%
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">2주후 반등률</span>
          <div className="flex items-center gap-2 flex-1 ml-4">
            <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
              <div 
                className="absolute left-0 top-0 h-full rounded-full"
                style={{ 
                  backgroundColor: getBarColor(pattern.biWeekRebound),
                  width: `${getBarWidth(pattern.biWeekRebound)}%`
                }}
              />
            </div>
            <span className="text-sm font-medium text-gray-900 w-10 text-right">
              {pattern.biWeekRebound}%
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">1개월후 반등률</span>
          <div className="flex items-center gap-2 flex-1 ml-4">
            <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
              <div 
                className="absolute left-0 top-0 h-full rounded-full"
                style={{ 
                  backgroundColor: getBarColor(pattern.monthRebound),
                  width: `${getBarWidth(pattern.monthRebound)}%`
                }}
              />
            </div>
            <span className="text-sm font-medium text-gray-900 w-10 text-right">
              {pattern.monthRebound}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}