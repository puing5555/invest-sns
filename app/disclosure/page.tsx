'use client';

import { useState } from 'react';
import DisclosureFilter from '@/components/DisclosureFilter';
import DisclosureDetailCard from '@/components/DisclosureDetailCard';
import AIAnalysisPanel from '@/components/AIAnalysisPanel';

// Dummy data as specified
const dummyDisclosures = [
  {
    id: '1',
    grade: 'A등급' as const,
    companyName: '아이빔테크놀로지',
    marketCap: '983억',
    time: '09:32',
    title: '단일판매·공급계약 체결',
    subtitle: '계약금액: 23.5억 (매출대비 14.77%)',
    aiComment: '매출대비 14.77%, 과거 유사 47건 D+3 +8.2%',
    pastPattern: {
      count: 47,
      period: 'D+3',
      returnRate: '+8.2%',
      winRate: 72
    },
    votes: {
      positive: 78,
      negative: 3,
      neutral: 19,
      totalVoters: 142
    },
    interactions: {
      comments: 23,
      reposts: 12,
      likes: 89
    },
    type: '공급계약'
  },
  {
    id: '2',
    grade: 'A등급' as const,
    companyName: '와이엠씨',
    marketCap: '1,337억',
    time: '10:05',
    title: '자사주 500,000주 소각',
    subtitle: '시총대비 3.75%',
    aiComment: '소형주 소각 D+5 +6.3%',
    pastPattern: {
      count: 31,
      period: 'D+5',
      returnRate: '+6.3%',
      winRate: 68
    },
    votes: {
      positive: 92,
      negative: 2,
      neutral: 6,
      totalVoters: 89
    },
    interactions: {
      comments: 18,
      reposts: 8,
      likes: 67
    },
    type: '자사주'
  },
  {
    id: '3',
    grade: 'A등급' as const,
    companyName: '세아제강지주',
    marketCap: '4,200억',
    time: '10:30',
    title: '기업가치 제고 계획 예고',
    subtitle: 'PBR 0.38',
    aiComment: '예고→확정 36%',
    pastPattern: {
      count: 28,
      period: 'D+3',
      returnRate: '+4.5%',
      winRate: 64
    },
    votes: {
      positive: 85,
      negative: 5,
      neutral: 10,
      totalVoters: 76
    },
    interactions: {
      comments: 15,
      reposts: 6,
      likes: 54
    },
    type: '기타'
  },
  {
    id: '4',
    grade: 'B등급' as const,
    companyName: 'HD한국조선해양',
    marketCap: '33조',
    time: '10:27',
    title: '해명공시 "미확정"',
    subtitle: '인도 합작법인',
    aiComment: '미확정 후 확정 36%',
    pastPattern: {
      count: 52,
      period: 'D+3',
      returnRate: '+3.1%',
      winRate: 58
    },
    votes: {
      positive: 61,
      negative: 12,
      neutral: 27,
      totalVoters: 203
    },
    interactions: {
      comments: 45,
      reposts: 23,
      likes: 112
    },
    type: '해명'
  },
  {
    id: '5',
    grade: 'B등급' as const,
    companyName: '롯데케미칼',
    marketCap: '3.8조',
    time: '10:26',
    title: '사업재편 승인',
    subtitle: '출자 6,000억',
    aiComment: '기업활력법 D+5 +2.1%',
    pastPattern: {
      count: 18,
      period: 'D+5',
      returnRate: '+2.1%',
      winRate: 56
    },
    votes: {
      positive: 55,
      negative: 15,
      neutral: 30,
      totalVoters: 67
    },
    interactions: {
      comments: 12,
      reposts: 5,
      likes: 34
    },
    type: '기타'
  },
  {
    id: '6',
    grade: 'B등급' as const,
    companyName: '토비스',
    marketCap: '2,483억',
    time: '10:15',
    title: '현금배당 350원',
    subtitle: '배당률 2.2%',
    aiComment: '전년 대비 +16.7% 증가',
    pastPattern: {
      count: 85,
      period: 'D+3',
      returnRate: '+1.2%',
      winRate: 52
    },
    votes: {
      positive: 70,
      negative: 8,
      neutral: 22,
      totalVoters: 45
    },
    interactions: {
      comments: 8,
      reposts: 3,
      likes: 28
    },
    type: '배당'
  }
];

export default function DisclosurePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [grade, setGrade] = useState('전체');
  const [type, setType] = useState('전체');
  const [sort, setSort] = useState('latest');
  const [isAnalysisPanelOpen, setIsAnalysisPanelOpen] = useState(false);

  // Filter and sort the data
  const filteredAndSortedData = dummyDisclosures
    .filter((disclosure) => {
      // Search filter
      const matchesSearch = searchTerm === '' || 
        disclosure.companyName.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Grade filter
      const matchesGrade = grade === '전체' || disclosure.grade === grade;
      
      // Type filter
      const matchesType = type === '전체' || disclosure.type === type;
      
      return matchesSearch && matchesGrade && matchesType;
    })
    .sort((a, b) => {
      switch (sort) {
        case 'latest':
          // Sort by time (latest first) - simple string comparison works for HH:MM format
          return b.time.localeCompare(a.time);
        case 'marketCap':
          // Sort by market cap (largest first)
          const aValue = parseFloat(a.marketCap.replace(/[조억,]/g, '')) * (a.marketCap.includes('조') ? 10000 : 1);
          const bValue = parseFloat(b.marketCap.replace(/[조억,]/g, '')) * (b.marketCap.includes('조') ? 10000 : 1);
          return bValue - aValue;
        case 'favorability':
          // Sort by positive vote percentage (highest first)
          return b.votes.positive - a.votes.positive;
        default:
          return 0;
      }
    });

  const handleAnalysisClick = () => {
    setIsAnalysisPanelOpen(true);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Filter Component */}
      <DisclosureFilter
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        grade={grade}
        onGradeChange={setGrade}
        type={type}
        onTypeChange={setType}
        sort={sort}
        onSortChange={setSort}
      />

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6">
        <div className="space-y-4">
          {filteredAndSortedData.length > 0 ? (
            filteredAndSortedData.map((disclosure) => (
              <DisclosureDetailCard
                key={disclosure.id}
                data={disclosure}
                onAnalysisClick={handleAnalysisClick}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">조건에 맞는 공시가 없습니다.</p>
            </div>
          )}
        </div>
      </div>

      {/* AI Analysis Panel */}
      <AIAnalysisPanel
        isOpen={isAnalysisPanelOpen}
        onClose={() => setIsAnalysisPanelOpen(false)}
      />
    </div>
  );
}