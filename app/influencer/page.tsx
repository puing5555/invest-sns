'use client';

import { useState } from 'react';
import { influencerData } from '@/data/influencerData';
import InfluencerCard from '@/components/InfluencerCard';
import InfluencerDetail from '@/components/InfluencerDetail';

export default function InfluencerPage() {
  const [sortBy, setSortBy] = useState('적중률순');
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const sortOptions = ['적중률순', '수익률순', '팔로워순', '최신콜순'];

  const getSortedData = () => {
    const data = [...influencerData];
    switch (sortBy) {
      case '적중률순':
        return data.sort((a, b) => b.accuracy - a.accuracy);
      case '수익률순':
        return data.sort((a, b) => b.avgReturn - a.avgReturn);
      case '팔로워순':
        return data.sort((a, b) => {
          const aNum = parseFloat(a.followers.replace('만', ''));
          const bNum = parseFloat(b.followers.replace('만', ''));
          return bNum - aNum;
        });
      case '최신콜순':
        return data.sort((a, b) => {
          const aDate = new Date('2026-' + a.recentCalls[0]?.date.replace('/', '-'));
          const bDate = new Date('2026-' + b.recentCalls[0]?.date.replace('/', '-'));
          return bDate.getTime() - aDate.getTime();
        });
      default:
        return data;
    }
  };

  const sortedInfluencers = getSortedData();

  const handleDetailClick = (index: number) => {
    // Only works for first influencer (코린이아빠)
    if (index === 0) {
      setIsDetailOpen(true);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">인플루언서 추적기</h1>
          <p className="text-gray-600">누가 맞추고 누가 틀리나</p>
        </div>

        {/* Sort Dropdown */}
        <div className="flex justify-end mb-6">
          <div className="relative">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
            >
              {sortOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        {/* Influencer Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {sortedInfluencers.map((influencer, index) => (
            <InfluencerCard
              key={influencer.id}
              influencer={influencer}
              onDetailClick={() => handleDetailClick(index)}
            />
          ))}
        </div>
      </div>

      {/* Detail Panel */}
      <InfluencerDetail
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
      />
    </div>
  );
}