'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import FeedPost, { PostData } from '@/components/FeedPost';

interface StockDetailClientProps {
  code: string;
}

// 탭 정의
const tabs = [
  { id: 'realtime', label: '실시간', icon: '⚡' },
  { id: 'influencer', label: '인플루언서', icon: '👤' },
  { id: 'analyst', label: '애널리스트', icon: '🎯' },
  { id: 'disclosure', label: '공시', icon: '📋' },
  { id: 'earnings', label: '실적', icon: '📊' },
  { id: 'reports', label: '리포트', icon: '📄' },
  { id: 'insider', label: '임원매매', icon: '💼' },
  { id: 'calendar', label: '일정', icon: '📅' },
  { id: 'memo', label: '메모', icon: '📝' },
];

// 더미 종목 데이터
const getStockData = (code: string) => {
  const stockMap: { [key: string]: any } = {
    '005930': { name: '삼성전자', price: 68500, change: 1200, changePercent: 1.78 },
    '000660': { name: 'SK하이닉스', price: 178000, change: -2100, changePercent: -1.16 },
    '035420': { name: 'NAVER', price: 185500, change: 3200, changePercent: 1.76 },
    '051910': { name: 'LG화학', price: 412000, change: -5500, changePercent: -1.32 },
    '005380': { name: '현대차', price: 221000, change: 4500, changePercent: 2.08 },
  };

  return stockMap[code] || { name: `종목 ${code}`, price: 50000, change: 0, changePercent: 0 };
};

// 더미 데이터들
const realtimePosts: PostData[] = [
  {
    id: 1,
    name: 'A등급 공시 속보',
    handle: 'system',
    avatar: 'system',
    time: '5분전',
    text: '3분기 실적 컨센서스 상회 발표\n\n🤖 AI 분석: 메모리 슈퍼사이클 본격화\n시그널 스코어 85점 🔥',
    isSystem: true,
    comments_count: 156,
    reposts: 234,
    likes: 1890,
    views: 89000,
  },
  {
    id: 2,
    name: '코린이아빠',
    handle: 'korini_papa',
    avatar: 'https://i.pravatar.cc/150?img=11',
    verified: true,
    accuracy: 68,
    time: '12분전',
    text: '분할매수 1차 진입했습니다.\n목표가까지 아직 20% 여유 있어서\n2차 분할 준비하고 있어요.\n\n⚠️ 투자 판단은 본인 책임',
    comments_count: 89,
    reposts: 156,
    likes: 1234,
    views: 45000,
  }
];

export default function StockDetailClient({ code }: StockDetailClientProps) {
  const [activeTab, setActiveTab] = useState('realtime');
  const searchParams = useSearchParams();
  const router = useRouter();
  const stockData = getStockData(code);

  // URL 쿼리 파라미터에서 탭 설정
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam && tabs.some(tab => tab.id === tabParam)) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'realtime':
        return (
          <div className="space-y-4">
            {realtimePosts.map((post) => (
              <FeedPost key={post.id} post={post} />
            ))}
          </div>
        );

      case 'influencer':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">👤</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">인플루언서 콜</h3>
            <p className="text-[#8b95a1]">이 종목에 대한 인플루언서 분석을 준비중입니다</p>
          </div>
        );

      case 'analyst':
        return (
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <h4 className="font-bold text-[#191f28] mb-4">애널리스트 의견</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-[#f8f9fa] rounded-lg">
                  <div>
                    <div className="font-medium">한국투자증권 김○○</div>
                    <div className="text-sm text-[#8b95a1]">목표가 75,000원</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-blue-600">매수</div>
                    <div className="text-xs text-[#8b95a1]">적중률 72%</div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-4 bg-[#f8f9fa] rounded-lg">
                  <div>
                    <div className="font-medium">미래에셋증권 이○○</div>
                    <div className="text-sm text-[#8b95a1]">목표가 72,000원</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-600">매수</div>
                    <div className="text-xs text-[#8b95a1]">적중률 68%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'disclosure':
        return (
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <h4 className="font-bold text-[#191f28] mb-4">최근 공시</h4>
              <div className="space-y-3">
                <div className="p-3 border-l-4 border-blue-500 bg-blue-50">
                  <div className="font-medium text-blue-800">3분기 실적 발표</div>
                  <div className="text-sm text-blue-600">2시간 전</div>
                </div>
                <div className="p-3 border-l-4 border-green-500 bg-green-50">
                  <div className="font-medium text-green-800">자사주 매입 결정</div>
                  <div className="text-sm text-green-600">1일 전</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'earnings':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">실적 분석</h3>
            <p className="text-[#8b95a1]">상세 실적 분석을 준비중입니다</p>
          </div>
        );

      case 'reports':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📄</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">리서치 리포트</h3>
            <p className="text-[#8b95a1]">증권사 리포트를 준비중입니다</p>
          </div>
        );

      case 'insider':
        return (
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <h4 className="font-bold text-[#191f28] mb-4">임원 매매 현황</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div>
                    <div className="font-medium text-red-800">김○○ 전무 매도</div>
                    <div className="text-sm text-red-600">5억원 규모 • 3일 전</div>
                  </div>
                  <div className="text-red-600 font-bold">-1.2%</div>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <div className="font-medium text-blue-800">박○○ 상무 매수</div>
                    <div className="text-sm text-blue-600">3억원 규모 • 1주 전</div>
                  </div>
                  <div className="text-blue-600 font-bold">+0.8%</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'calendar':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📅</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">종목 일정</h3>
            <p className="text-[#8b95a1]">실적발표, 주주총회 등 일정을 준비중입니다</p>
          </div>
        );

      case 'memo':
        return (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
            <h4 className="font-bold text-[#191f28] mb-4">내 메모</h4>
            <div className="space-y-4">
              <textarea
                placeholder="이 종목에 대한 메모를 작성해보세요..."
                className="w-full h-32 p-3 border border-[#e8e8e8] rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
              />
              <div className="flex justify-end">
                <button className="px-4 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#2171e5] transition-colors">
                  저장
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return <div>준비중</div>;
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Stock Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-6">
        <div className="max-w-4xl mx-auto">
          {/* 뒤로가기 버튼 */}
          <div className="mb-4">
            <button
              onClick={() => router.push('/my-stocks')}
              className="flex items-center gap-2 text-[#8b95a1] hover:text-[#191f28] transition-colors"
            >
              <span className="text-lg">←</span>
              <span className="text-sm">내 종목으로</span>
            </button>
          </div>

          <div>
            <h1 className="text-2xl font-bold text-[#191f28]">
              {stockData.name}
              <span className="text-lg text-[#8b95a1] font-normal ml-2">
                {code}
              </span>
            </h1>
            <div className="flex items-center gap-4 mt-2">
              <span className="text-3xl font-bold text-[#191f28]">
                {stockData.price.toLocaleString()}원
              </span>
              <span className={`text-lg font-medium ${
                stockData.change >= 0 ? 'text-red-500' : 'text-blue-500'
              }`}>
                {stockData.change >= 0 ? '+' : ''}{stockData.change.toLocaleString()}원
                ({stockData.change >= 0 ? '+' : ''}{stockData.changePercent}%)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-[#e8e8e8]">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-shrink-0 flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative ${
                  activeTab === tab.id
                    ? 'text-[#3182f6]'
                    : 'text-[#8b95a1] hover:text-[#191f28]'
                }`}
              >
                <span>{tab.icon}</span>
                {tab.label}
                {activeTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#3182f6]" />
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        {renderTabContent()}
      </div>
    </div>
  );
}