'use client';

import { useState } from 'react';
import { gurus, getGurusWithNewBuys, getGurusWithChanges, Guru } from '../../data/guruData';
import GuruCard from '../../components/GuruCard';
import GuruDetail from '../../components/GuruDetail';

type FilterType = 'all' | 'changes' | 'newBuys';

export default function GuruPage() {
  const [selectedFilter, setSelectedFilter] = useState<FilterType>('all');
  const [selectedGuru, setSelectedGuru] = useState<Guru | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const getFilteredGurus = () => {
    switch (selectedFilter) {
      case 'changes':
        return getGurusWithChanges();
      case 'newBuys':
        return getGurusWithNewBuys();
      default:
        return gurus;
    }
  };

  const filteredGurus = getFilteredGurus();

  const handleGuruClick = (guru: Guru) => {
    setSelectedGuru(guru);
    setIsDetailOpen(true);
  };

  const handleCloseDetail = () => {
    setIsDetailOpen(false);
    setSelectedGuru(null);
  };

  const filterOptions = [
    { key: 'all' as FilterType, label: '전체', count: gurus.length },
    { key: 'changes' as FilterType, label: '최근 변동 있음', count: getGurusWithChanges().length },
    { key: 'newBuys' as FilterType, label: '신규매수 있음', count: getGurusWithNewBuys().length },
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header Section */}
      <div className="border-b border-[#e5e7eb] bg-white sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-[#111827] mb-2">🐋 투자 구루</h1>
            <p className="text-[#6b7280]">세계적인 투자 구루들의 13F 포트폴리오를 실시간으로 추적하세요</p>
          </div>

          {/* Filter Tabs */}
          <div className="flex flex-wrap gap-2">
            {filterOptions.map((option) => (
              <button
                key={option.key}
                onClick={() => setSelectedFilter(option.key)}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                  selectedFilter === option.key
                    ? 'bg-[#00d4aa] text-black'
                    : 'bg-[#f7f9fa] text-[#6b7280] hover:bg-[#e5e7eb] hover:text-[#374151]'
                }`}
              >
                {option.label} ({option.count})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Results Summary */}
        <div className="mb-6">
          <p className="text-[#6b7280]">
            {filteredGurus.length}명의 구루 
            {selectedFilter === 'changes' && ' (최근 변동 있음)'}
            {selectedFilter === 'newBuys' && ' (신규 매수 있음)'}
          </p>
        </div>

        {/* Guru Cards Grid */}
        {filteredGurus.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredGurus.map((guru) => (
              <GuruCard
                key={guru.id}
                guru={guru}
                onClick={() => handleGuruClick(guru)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-[#111827] mb-2">구루를 찾을 수 없습니다</h3>
            <p className="text-[#6b7280]">선택한 필터에 맞는 구루가 없습니다. 다른 필터를 시도해보세요.</p>
          </div>
        )}
      </div>

      {/* Guru Detail Panel */}
      <GuruDetail
        guru={selectedGuru}
        isOpen={isDetailOpen}
        onClose={handleCloseDetail}
      />
    </div>
  );
}