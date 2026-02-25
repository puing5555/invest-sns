'use client';

import { Guru } from '../data/guruData';

interface GuruCardProps {
  guru: Guru;
  onClick: () => void;
}

export default function GuruCard({ guru, onClick }: GuruCardProps) {
  const getChangesBadges = () => {
    const badges = [];
    
    if (guru.changes.newBuys > 0) {
      badges.push(
        <span key="new" className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs font-medium">
          🟢 신규 {guru.changes.newBuys}건
        </span>
      );
    }
    
    if (guru.changes.increased > 0) {
      badges.push(
        <span key="inc" className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-xs font-medium">
          🔼 확대 {guru.changes.increased}건
        </span>
      );
    }
    
    if (guru.changes.decreased > 0) {
      badges.push(
        <span key="dec" className="bg-orange-500/20 text-orange-400 px-2 py-1 rounded text-xs font-medium">
          🔽 축소 {guru.changes.decreased}건
        </span>
      );
    }
    
    if (guru.changes.sold > 0) {
      badges.push(
        <span key="sold" className="bg-red-500/20 text-red-400 px-2 py-1 rounded text-xs font-medium">
          🔴 매도 {guru.changes.sold}건
        </span>
      );
    }
    
    return badges;
  };

  return (
    <div 
      className="bg-white border border-[#e5e7eb] rounded-lg p-6 cursor-pointer transition-all duration-200 hover:shadow-lg hover:shadow-[#00d4aa]/20 hover:border hover:border-[#00d4aa]/50 group"
      onClick={onClick}
    >
      {/* Header - Avatar and Basic Info */}
      <div className="flex items-center gap-4 mb-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#00d4aa] to-[#00a087] flex items-center justify-center">
          <span className="text-black font-bold text-lg">{guru.initials}</span>
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-[#111827] text-lg">{guru.name}</h3>
          <p className="text-[#374151] text-sm">{guru.fund}</p>
          <p className="text-[#6b7280] text-sm">{guru.aum}</p>
        </div>
      </div>

      {/* Update Status */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-[#6b7280] text-sm">{guru.lastUpdate}</span>
        {guru.isRealtime && (
          <span className="bg-blue-500/20 text-blue-600 px-2 py-1 rounded text-xs font-medium">
            실시간
          </span>
        )}
      </div>

      {/* Realtime Note */}
      {guru.realtimeNote && (
        <div className="text-sm text-blue-600 mb-3 italic">
          {guru.realtimeNote}
        </div>
      )}

      {/* Changes Summary */}
      <div className="flex flex-wrap gap-2 mb-4">
        {getChangesBadges()}
      </div>

      {/* Warning */}
      {guru.hasWarning && guru.warningText && (
        <div className="bg-yellow-500/20 text-yellow-600 px-3 py-2 rounded text-sm mb-4 flex items-center gap-2">
          <span>⚠️</span>
          <span>{guru.warningText}</span>
        </div>
      )}

      {/* TOP3 Holdings */}
      <div className="mb-4">
        <h4 className="text-[#111827] font-semibold text-sm mb-3">TOP 3 보유종목</h4>
        <div className="space-y-2">
          {guru.topHoldings.map((holding, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="text-sm">
                <span className="text-[#111827] font-medium">{holding.name}</span>
                <span className="text-[#6b7280] ml-1">({holding.ticker})</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[#374151] text-sm font-medium">{holding.percentage}%</span>
                <div className="w-16 bg-[#e5e7eb] rounded-full h-1.5">
                  <div 
                    className="bg-[#00d4aa] h-1.5 rounded-full"
                    style={{ width: `${Math.min(holding.percentage * 2, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Button */}
      <button className="w-full bg-[#f7f9fa] hover:bg-[#e5e7eb] text-[#00d4aa] py-2 px-4 rounded font-medium text-sm transition-colors group-hover:bg-[#e5e7eb] border border-[#e5e7eb]">
        상세보기
      </button>
    </div>
  );
}