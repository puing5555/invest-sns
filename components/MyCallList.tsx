import React from 'react';
import { callsData, profileData } from '@/data/profileData';
import AccuracyCircle from '@/components/AccuracyCircle';

const MyCallList = () => {
  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 rounded text-xs font-medium";
    switch (status) {
      case 'ÏßÑÌñâÏ§?:
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case '?ÅÏ§ë':
        return `${baseClasses} bg-green-100 text-green-800`;
      case '?êÏ†à':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-[#f2f4f6] text-gray-800`;
    }
  };

  const getStatusDot = (status: string) => {
    switch (status) {
      case 'ÏßÑÌñâÏ§?:
        return '?îµ';
      case '?ÅÏ§ë':
        return '?ü¢';
      case '?êÏ†à':
        return '?î¥';
      default:
        return '??;
    }
  };

  const getReturnColor = (returnRate: number) => {
    return returnRate >= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="space-y-4">
      {/* Performance Summary Card */}
      <div className="bg-white rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.04)] p-6 border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1">
            <div className="flex gap-6 text-center">
              <div>
                <div className="font-bold text-lg">{profileData.totalCalls}Í±?/div>
                <div className="text-[#8b95a1] text-sm">Ï¥?ÏΩ?/div>
              </div>
              <div className="border-l border-gray-200 pl-6">
                <div className="font-bold text-lg">{profileData.winRate}%</div>
                <div className="text-[#8b95a1] text-sm">?πÎ•†</div>
              </div>
              <div className="border-l border-gray-200 pl-6">
                <div className="font-bold text-lg text-green-600">+{profileData.avgReturn}%</div>
                <div className="text-[#8b95a1] text-sm">?âÍ∑† ?òÏùµ</div>
              </div>
            </div>
          </div>
          <div className="flex-shrink-0 ml-6">
            <AccuracyCircle 
              percentage={profileData.winRate} 
              successful={Math.round(profileData.totalCalls * profileData.winRate / 100)} 
              total={profileData.totalCalls}
              size={80}
            />
          </div>
        </div>
      </div>

      {/* Call History List */}
      <div className="space-y-2">
        {callsData.map((call) => (
          <div key={call.id} className="bg-white rounded-2xl border p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-lg">{getStatusDot(call.status)}</span>
                <div>
                  <div className="font-medium text-[#191f28]">{call.stockName}</div>
                  <div className="text-sm text-[#8b95a1]">
                    {call.type} {call.price.toLocaleString()}????{call.date}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className={`font-bold ${getReturnColor(call.returnRate)}`}>
                  {call.returnRate > 0 ? '+' : ''}{call.returnRate}%
                </div>
                <span className={getStatusBadge(call.status)}>
                  {call.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MyCallList;