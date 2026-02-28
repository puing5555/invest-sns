'use client';

import { useState } from 'react';

// Dummy data for disclosure search
const searchResults = [
  {
    id: '1',
    company: '아이빔테크놀로지',
    date: '2026-02-28',
    title: '단일판매·공급계약 체결',
    type: '공급계약',
    grade: 'A',
    amount: '23.5억',
    sector: 'IT부품',
    returns: {
      d1: '+2.3%',
      d3: '+5.8%',
      d7: '+8.2%',
      d15: '+12.1%',
      d30: '+18.7%'
    },
    tags: ['공급계약', '매출증가', '신규고객']
  },
  {
    id: '2',
    company: '와이엠씨',
    date: '2026-02-28',
    title: '자사주 500,000주 소각',
    type: '자사주',
    grade: 'A',
    amount: '50억',
    sector: '화학',
    returns: {
      d1: '+1.8%',
      d3: '+4.2%',
      d7: '+6.3%',
      d15: '+9.1%',
      d30: '+11.4%'
    },
    tags: ['자사주소각', '주주환원', '주가부양']
  },
  {
    id: '3',
    company: '세아제강지주',
    date: '2026-02-28',
    title: '기업가치 제고 계획 예고',
    type: '기타',
    grade: 'A',
    amount: '-',
    sector: '철강',
    returns: {
      d1: '+0.9%',
      d3: '+2.1%',
      d7: '+4.5%',
      d15: '+7.8%',
      d30: '+13.2%'
    },
    tags: ['기업가치제고', '예고공시', 'PBR개선']
  },
  {
    id: '4',
    company: 'HD한국조선해양',
    date: '2026-02-28',
    title: '해명공시 "미확정"',
    type: '해명',
    grade: 'B',
    amount: '-',
    sector: '조선',
    returns: {
      d1: '+0.5%',
      d3: '+1.2%',
      d7: '+3.1%',
      d15: '+2.8%',
      d30: '+1.9%'
    },
    tags: ['해명공시', '미확정', '합작법인']
  },
  {
    id: '5',
    company: '롯데케미칼',
    date: '2026-02-28',
    title: '사업재편 승인',
    type: '기타',
    grade: 'B',
    amount: '6,000억',
    sector: '화학',
    returns: {
      d1: '-0.2%',
      d3: '+1.1%',
      d7: '+2.1%',
      d15: '+3.4%',
      d30: '+5.7%'
    },
    tags: ['사업재편', '출자', '기업활력법']
  },
  {
    id: '6',
    company: '토비스',
    date: '2026-02-28',
    title: '현금배당 350원',
    type: '배당',
    grade: 'B',
    amount: '35억',
    sector: '소프트웨어',
    returns: {
      d1: '+0.8%',
      d3: '+0.5%',
      d7: '+1.2%',
      d15: '+1.8%',
      d30: '+2.3%'
    },
    tags: ['현금배당', '배당률2.2%', '증배당']
  }
];

const typeReturns = [
  { type: '자사주', avgReturn: '+8.7%', count: 234, winRate: '73%' },
  { type: '공급계약', avgReturn: '+6.2%', count: 456, winRate: '68%' },
  { type: '기타', avgReturn: '+4.1%', count: 789, winRate: '62%' },
  { type: '배당', avgReturn: '+2.3%', count: 123, winRate: '58%' },
  { type: '해명', avgReturn: '+1.8%', count: 345, winRate: '51%' },
  { type: '사업보고서', avgReturn: '+1.2%', count: 567, winRate: '49%' }
];

const popularTags = [
  { tag: '자사주소각', count: 89, trend: 'up' },
  { tag: '공급계약', count: 67, trend: 'up' },
  { tag: '기업가치제고', count: 45, trend: 'up' },
  { tag: '배당', count: 43, trend: 'stable' },
  { tag: '매출증가', count: 38, trend: 'up' },
  { tag: '신규고객', count: 34, trend: 'up' },
  { tag: '해명공시', count: 29, trend: 'down' },
  { tag: '사업재편', count: 27, trend: 'stable' }
];

export default function DisclosureSearchTab() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    period: 'all',
    grade: 'all',
    type: 'all',
    sector: 'all',
    sortBy: 'date'
  });

  const [activeView, setActiveView] = useState<'search' | 'returns' | 'tags'>('search');

  const filteredResults = searchResults.filter(result => {
    const matchesSearch = searchTerm === '' || 
      result.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      result.title.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesGrade = filters.grade === 'all' || result.grade === filters.grade;
    const matchesType = filters.type === 'all' || result.type === filters.type;
    const matchesSector = filters.sector === 'all' || result.sector === filters.sector;
    
    return matchesSearch && matchesGrade && matchesType && matchesSector;
  });

  return (
    <div className="py-6 space-y-6">
      {/* Header and View Toggle */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">공시 데이터베이스</h2>
        
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveView('search')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              activeView === 'search' ? 'bg-blue-500 text-white' : 'text-gray-700 hover:text-gray-900'
            }`}
          >
            🔍 검색
          </button>
          <button
            onClick={() => setActiveView('returns')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              activeView === 'returns' ? 'bg-green-500 text-white' : 'text-gray-700 hover:text-gray-900'
            }`}
          >
            📊 수익률
          </button>
          <button
            onClick={() => setActiveView('tags')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              activeView === 'tags' ? 'bg-purple-500 text-white' : 'text-gray-700 hover:text-gray-900'
            }`}
          >
            🏷️ 키워드
          </button>
        </div>
      </div>

      {/* Search and Filter Section */}
      {activeView === 'search' && (
        <>
          {/* Search Bar */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="회사명, 공시 제목으로 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                검색
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">기간</label>
                <select 
                  value={filters.period}
                  onChange={(e) => setFilters({...filters, period: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="all">전체</option>
                  <option value="1day">1일</option>
                  <option value="1week">1주</option>
                  <option value="1month">1개월</option>
                  <option value="3months">3개월</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-1">등급</label>
                <select 
                  value={filters.grade}
                  onChange={(e) => setFilters({...filters, grade: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="all">전체</option>
                  <option value="A">A등급</option>
                  <option value="B">B등급</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-1">유형</label>
                <select 
                  value={filters.type}
                  onChange={(e) => setFilters({...filters, type: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="all">전체</option>
                  <option value="자사주">자사주</option>
                  <option value="공급계약">공급계약</option>
                  <option value="배당">배당</option>
                  <option value="해명">해명</option>
                  <option value="기타">기타</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-1">섹터</label>
                <select 
                  value={filters.sector}
                  onChange={(e) => setFilters({...filters, sector: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="all">전체</option>
                  <option value="IT부품">IT부품</option>
                  <option value="화학">화학</option>
                  <option value="철강">철강</option>
                  <option value="조선">조선</option>
                  <option value="소프트웨어">소프트웨어</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-1">정렬</label>
                <select 
                  value={filters.sortBy}
                  onChange={(e) => setFilters({...filters, sortBy: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="date">최신순</option>
                  <option value="return">수익률순</option>
                  <option value="company">회사명순</option>
                </select>
              </div>
            </div>
          </div>

          {/* Search Results */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                검색 결과 ({filteredResults.length}건)
              </h3>
            </div>

            {/* Results Table Header */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                <div className="grid grid-cols-7 gap-4 text-xs font-medium text-gray-600 uppercase tracking-wide">
                  <div className="col-span-2">회사명 / 공시제목</div>
                  <div>유형/등급</div>
                  <div>D+1</div>
                  <div>D+7</div>
                  <div>D+15</div>
                  <div>D+30</div>
                </div>
              </div>

              {/* Results */}
              <div className="divide-y divide-gray-200">
                {filteredResults.map((result) => (
                  <div key={result.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="grid grid-cols-7 gap-4 items-center">
                      <div className="col-span-2">
                        <div className="flex items-center space-x-2 mb-1">
                          <h4 className="font-medium text-gray-900">{result.company}</h4>
                          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                            {result.sector}
                          </span>
                          <span className="text-xs text-gray-500">{result.date}</span>
                        </div>
                        <p className="text-sm text-gray-700">{result.title}</p>
                        {result.amount !== '-' && (
                          <p className="text-xs text-gray-500">규모: {result.amount}</p>
                        )}
                        
                        {/* Tags */}
                        <div className="flex flex-wrap gap-1 mt-2">
                          {result.tags.map((tag, index) => (
                            <span key={index} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center space-x-1">
                        <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                          {result.type}
                        </span>
                        <span className={`w-5 h-5 text-xs font-bold text-white rounded text-center leading-5 ${
                          result.grade === 'A' ? 'bg-red-500' : 'bg-orange-500'
                        }`}>
                          {result.grade}
                        </span>
                      </div>

                      <div className={`font-medium ${
                        result.returns.d1.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                      }`}>
                        {result.returns.d1}
                      </div>

                      <div className={`font-medium ${
                        result.returns.d7.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                      }`}>
                        {result.returns.d7}
                      </div>

                      <div className={`font-medium ${
                        result.returns.d15.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                      }`}>
                        {result.returns.d15}
                      </div>

                      <div className={`font-medium ${
                        result.returns.d30.startsWith('+') ? 'text-red-500' : 'text-blue-500'
                      }`}>
                        {result.returns.d30}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Type Returns Section */}
      {activeView === 'returns' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">유형별 평균 수익률</h3>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {typeReturns.map((item, index) => (
              <div key={index} className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{item.type}</h4>
                  <span className="text-sm bg-gray-100 text-gray-600 px-2 py-1 rounded">
                    {item.count}건
                  </span>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">평균 수익률</span>
                    <span className={`font-bold ${
                      item.avgReturn.startsWith('+') ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {item.avgReturn}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">승률</span>
                    <span className="font-medium text-gray-900">{item.winRate}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-blue-50 p-4 rounded-xl">
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 font-medium text-sm">💡 분석 인사이트:</span>
              <div className="text-sm text-gray-700">
                자사주 매입·소각 공시가 가장 높은 수익률과 승률을 보이며, 
                해명공시의 경우 불확실성으로 인해 상대적으로 낮은 수익률을 기록하고 있습니다.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Popular Tags Section */}
      {activeView === 'tags' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">인기 키워드</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {popularTags.map((tag, index) => (
              <div key={index} className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg transition-shadow cursor-pointer">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">#{tag.tag}</h4>
                  <span className={`text-xs ${
                    tag.trend === 'up' ? 'text-green-600' : 
                    tag.trend === 'down' ? 'text-red-600' : 'text-gray-500'
                  }`}>
                    {tag.trend === 'up' ? '📈' : tag.trend === 'down' ? '📉' : '➡️'}
                  </span>
                </div>
                <div className="text-sm text-gray-600">{tag.count}건</div>
              </div>
            ))}
          </div>

          <div className="bg-purple-50 p-4 rounded-xl">
            <div className="flex items-start space-x-2">
              <span className="text-purple-600 font-medium text-sm">🔥 트렌드:</span>
              <div className="text-sm text-gray-700">
                현재 '자사주소각', '기업가치제고' 관련 키워드가 상승세를 보이며, 
                주주환원 정책에 대한 시장의 관심이 높아지고 있습니다.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}