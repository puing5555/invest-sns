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
              <h2 className="text-2xl font-bold text-[#191f28]">Íµ¨Î£® ?ÅÏÑ∏</h2>
              <button 
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-[#f2f4f6] hover:bg-gray-200 flex items-center justify-center transition-colors"
              >
                ??
              </button>
            </div>
            
            {/* Large Profile Section */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#3182f6] to-[#00a087] flex items-center justify-center">
                <span className="text-black font-bold text-2xl">{guru.initials}</span>
              </div>
              <div>
                <h3 className="font-bold text-xl text-[#191f28]">{guru.name}</h3>
                <p className="text-gray-600 font-medium">{guru.fund}</p>
                <p className="text-[#8b95a1] text-sm">{guru.aum} ??{guru.lastUpdate}</p>
                {guru.isRealtime && (
                  <span className="inline-block bg-blue-500/20 text-blue-600 px-2 py-1 rounded text-xs font-medium mt-1">
                    ?§ÏãúÍ∞?
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
                  <h3 className="text-xl font-bold text-[#191f28] mb-4">Î≥Ä???¥Ïó≠</h3>
                  <PortfolioChange 
                    newBuys={guru.detail!.newBuys}
                    increased={guru.detail!.increased}
                    decreased={guru.detail!.decreased}
                    soldAll={guru.detail!.soldAll}
                  />
                </div>

                {/* Sector Allocation */}
                <div>
                  <h3 className="text-xl font-bold text-[#191f28] mb-4">?πÌÑ∞ Íµ¨ÏÑ±</h3>
                  <SectorPieChart sectors={guru.detail!.sectors} />
                </div>

                {/* AI Insight */}
                <div>
                  <h3 className="text-xl font-bold text-[#191f28] mb-4">AI ?¥ÏÑù</h3>
                  <div className="bg-[#f0fdf4] border border-green-200 rounded-2xl p-4">
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
                  <h3 className="text-xl font-bold text-[#191f28] mb-4">Ïª§Î??àÌã∞ ?¨Ìëú</h3>
                  <div className="bg-[#f2f4f6] rounded-2xl p-4">
                    <div className="mb-3">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>?∞Îùº?òÍ∏∞ {guru.detail!.vote.follow}%</span>
                        <span>Î∞òÎ? {guru.detail!.vote.against}%</span>
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
                        ?í¨ {guru.detail!.vote.comments}Í∞??ìÍ?
                      </span>
                      <div className="flex gap-2">
                        <button className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors">
                          ?∞Îùº?òÍ∏∞
                        </button>
                        <button className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-3 py-1 rounded text-sm font-medium transition-colors">
                          Î∞òÎ?
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
                  <h3 className="text-xl font-bold text-[#191f28] mb-4">Î≥Ä???îÏïΩ</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {guru.changes.newBuys > 0 && (
                      <div className="bg-green-50 rounded-2xl p-3 text-center">
                        <div className="text-2xl font-bold text-green-600">{guru.changes.newBuys}</div>
                        <div className="text-sm text-green-700">?†Í∑úÎß§Ïàò</div>
                      </div>
                    )}
                    {guru.changes.increased > 0 && (
                      <div className="bg-blue-50 rounded-2xl p-3 text-center">
                        <div className="text-2xl font-bold text-blue-600">{guru.changes.increased}</div>
                        <div className="text-sm text-blue-700">?ïÎ?</div>
                      </div>
                    )}
                    {guru.changes.decreased > 0 && (
                      <div className="bg-orange-50 rounded-2xl p-3 text-center">
                        <div className="text-2xl font-bold text-orange-600">{guru.changes.decreased}</div>
                        <div className="text-sm text-orange-700">Ï∂ïÏÜå</div>
                      </div>
                    )}
                    {guru.changes.sold > 0 && (
                      <div className="bg-red-50 rounded-2xl p-3 text-center">
                        <div className="text-2xl font-bold text-red-600">{guru.changes.sold}</div>
                        <div className="text-sm text-red-700">Îß§ÎèÑ</div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Top Holdings */}
                <div>
                  <h3 className="text-xl font-bold text-[#191f28] mb-4">Ï£ºÏöî Î≥¥Ïú†Ï¢ÖÎ™©</h3>
                  <div className="space-y-3">
                    {guru.topHoldings.map((holding, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-[#f2f4f6] rounded-2xl">
                        <div>
                          <span className="font-bold text-[#191f28]">{holding.name}</span>
                          <span className="text-[#8b95a1] ml-1">({holding.ticker})</span>
                        </div>
                        <div className="font-semibold text-[#191f28]">{holding.percentage}%</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Notice for Limited Data */}
                <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-blue-600 text-sm">?πÔ∏è</span>
                    </div>
                    <p className="text-blue-800 text-sm">
                      ??Íµ¨Î£®???ÅÏÑ∏ ?¨Ìä∏?¥Î¶¨??Î∂ÑÏÑù?Ä Í≥??úÍ≥µ???àÏ†ï?ÖÎãà??
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