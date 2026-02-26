'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
interface StockDetailClientProps {
  code: string;
}

// 종목별 타임라인 이벤트
interface StockTimelineEvent {
  id: number;
  type: string;
  icon: string;
  categoryName: string;
  title: string;
  time: string;
  tab: string;
}

const getStockTimeline = (code: string): StockTimelineEvent[] => {
  const timelines: { [key: string]: StockTimelineEvent[] } = {
    '005930': [
      { id: 1, type: 'disclosure', icon: '🔵', categoryName: '공시', title: 'A등급 공시 - 3분기 실적 컨센서스 상회', time: '3분 전', tab: 'disclosure' },
      { id: 2, type: 'influencer', icon: '🟢', categoryName: '인플루언서', title: '슈카월드 긍정 신호', time: '1시간 전', tab: 'influencer' },
      { id: 3, type: 'report', icon: '📊', categoryName: '리포트', title: '한국투자증권 목표가 상향', time: '2시간 전', tab: 'reports' },
      { id: 4, type: 'insider', icon: '👔', categoryName: '임원매매', title: '이재용 사장 매수 5만주', time: '3시간 전', tab: 'insider' },
      { id: 5, type: 'earnings', icon: '📈', categoryName: '실적', title: '3분기 영업이익 컨센서스 상회', time: '5시간 전', tab: 'earnings' },
      { id: 6, type: 'influencer', icon: '🟢', categoryName: '인플루언서', title: '코린이아빠 매수 신호', time: '8시간 전', tab: 'influencer' },
      { id: 7, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '자사주 매입 결정', time: '1일 전', tab: 'disclosure' },
    ],
    '005380': [
      { id: 1, type: 'report', icon: '📊', categoryName: '리포트', title: '한국투자증권 목표가 상향', time: '2시간 전', tab: 'reports' },
      { id: 2, type: 'earnings', icon: '📈', categoryName: '실적', title: '3분기 영업이익 컨센서스 상회', time: '5시간 전', tab: 'earnings' },
      { id: 3, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '전기차 신모델 출시 공시', time: '1일 전', tab: 'disclosure' },
    ],
  };
  return timelines[code] || [
    { id: 1, type: 'disclosure', icon: '🔵', categoryName: '공시', title: '최근 공시 없음', time: '-', tab: 'disclosure' },
  ];
};

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

export default function StockDetailClient({ code }: StockDetailClientProps) {
  const [activeTab, setActiveTab] = useState('realtime');
  const searchParams = useSearchParams();
  const router = useRouter();
  const stockData = getStockData(code);
  const timeline = getStockTimeline(code);

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
          <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
            <div className="divide-y divide-[#f0f0f0]">
              {timeline.map((event) => (
                <div
                  key={event.id}
                  onClick={() => setActiveTab(event.tab)}
                  className="px-4 py-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#f8f9fa] flex items-center justify-center text-lg flex-shrink-0">
                      {event.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-[#8b95a1] bg-[#f2f4f6] px-2 py-0.5 rounded">
                          {event.categoryName}
                        </span>
                      </div>
                      <h3 className="text-[15px] font-medium text-[#191f28] leading-[1.4] mb-1">
                        {event.title}
                      </h3>
                      <span className="text-sm text-[#8b95a1]">{event.time}</span>
                    </div>
                    <div className="text-[#8b95a1] text-sm">→</div>
                  </div>
                </div>
              ))}
            </div>
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
        <div>
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
        <div className="px-4">
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
      <div className="px-4 py-6">
        {renderTabContent()}
      </div>
    </div>
  );
}