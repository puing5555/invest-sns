'use client';

import { useEffect } from 'react';
import { Guru } from '../data/guruData';
import PortfolioChange from './PortfolioChange';
import SectorPieChart from './SectorPieChart';

interface GuruDetailProps {
  guru: Guru | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function GuruDetail({ guru, isOpen, onClose }: GuruDetailProps) {
  // Handle ESC key to close panel
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      // Prevent body scroll when panel is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !guru) return null;

  const hasDetailData = guru.detail !== undefined;

  return (
    <>
      {/* Dark Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />
      
      {/* Slide-in Panel */}
      <div className={`fixed right-0 top-0 h-full w-[420px] bg-white shadow-2xl z-50 transform transition-transform duration-300 ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="h-full overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900">구루 상세</h2>
              <button 
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
              >
                ✕
              </button>
            </div>
            
            {/* Large Profile Section */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#3182f6] to-[#00a087] flex items-center justify-center">
                <span className="text-black font-bold text-2xl">{guru.initials}</span>
              </div>
              <div>
                <h3 className="font-bold text-xl text-gray-900">{guru.name}</h3>
                <p className="text-gray-600 font-medium">{guru.fund}</p>
                <p className="text-gray-500 text-sm">{guru.aum} • {guru.lastUpdate}</p>
                {guru.isRealtime && (
                  <span className="inline-block bg-blue-500/20 text-blue-600 px-2 py-1 rounded text-xs font-medium mt-1">
                    실시간
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="p-6 space-y-8">
            {hasDetailData ? (
              <>
                {/* Portfolio Changes */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">변동 내역</h3>
                  <PortfolioChange 
                    newBuys={guru.detail!.newBuys}
                    increased={guru.detail!.increased}
                    decreased={guru.detail!.decreased}
                    soldAll={guru.detail!.soldAll}
                  />
                </div>

                {/* Sector Allocation */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">섹터 구성</h3>
                  <SectorPieChart sectors={guru.detail!.sectors} />
                </div>

                {/* AI Insight */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">AI 해석</h3>
                  <div className="bg-[#f0fdf4] border border-green-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                        <span className="text-green-600 text-sm font-bold">AI</span>
                      </div>
                      <p className="text-gray-800 leading-relaxed">{guru.detail!.aiInsight}</p>
                    </div>
                  </div>
                </div>

                {/* Community Vote */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">커뮤니티 투표</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="mb-3">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>따라하기 {guru.detail!.vote.follow}%</span>
                        <span>반대 {guru.detail!.vote.against}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div 
                          className="bg-green-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${guru.detail!.vote.follow}%` }}
                        />
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">
                        💬 {guru.detail!.vote.comments}개 댓글
                      </span>
                      <div className="flex gap-2">
                        <button className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors">
                          따라하기
                        </button>
                        <button className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-3 py-1 rounded text-sm font-medium transition-colors">
                          반대
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* Basic Info for Gurus without Detail Data */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">변동 요약</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {guru.changes.newBuys > 0 && (
                      <div className="bg-green-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-green-600">{guru.changes.newBuys}</div>
                        <div className="text-sm text-green-700">신규매수</div>
                      </div>
                    )}
                    {guru.changes.increased > 0 && (
                      <div className="bg-blue-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-blue-600">{guru.changes.increased}</div>
                        <div className="text-sm text-blue-700">확대</div>
                      </div>
                    )}
                    {guru.changes.decreased > 0 && (
                      <div className="bg-orange-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-orange-600">{guru.changes.decreased}</div>
                        <div className="text-sm text-orange-700">축소</div>
                      </div>
                    )}
                    {guru.changes.sold > 0 && (
                      <div className="bg-red-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-red-600">{guru.changes.sold}</div>
                        <div className="text-sm text-red-700">매도</div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Top Holdings */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">주요 보유종목</h3>
                  <div className="space-y-3">
                    {guru.topHoldings.map((holding, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <span className="font-bold text-gray-900">{holding.name}</span>
                          <span className="text-gray-500 ml-1">({holding.ticker})</span>
                        </div>
                        <div className="font-semibold text-gray-900">{holding.percentage}%</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Notice for Limited Data */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-blue-600 text-sm">ℹ️</span>
                    </div>
                    <p className="text-blue-800 text-sm">
                      이 구루의 상세 포트폴리오 분석은 곧 제공될 예정입니다.
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}