'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { getStockSignals, getSignalColor } from '@/lib/supabase';
import StockChart from '@/components/StockChart';
import StockDisclosureTab from '@/components/stock/StockDisclosureTab';
import StockAnalystTab from '@/components/stock/StockAnalystTab';
import FeedCard from '@/components/FeedCard';
import StockSignalChart from '@/components/StockSignalChart';
import { formatStockDisplay } from '@/lib/stockNames';
import SignalDetailModal from '@/components/SignalDetailModal';
import { influencers } from '@/data/influencerData';
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
  { id: 'feed', label: '피드', icon: '📱' },
  { id: 'influencer', label: '인플루언서', icon: '📈' },
  { id: 'analyst', label: '애널리스트', icon: '📊' },
  { id: 'disclosure', label: '공시', icon: '📋' },
  { id: 'earnings', label: '실적', icon: '📈' },
  { id: 'insider', label: '임원매매', icon: '💼' },
  { id: 'calendar', label: '일정', icon: '📅' },
  { id: 'memo', label: '메모', icon: '📝' },
];

import stockPricesData from '@/data/stockPrices.json';

// 종목 데이터 - 실제 Yahoo Finance 데이터 사용 (동적 종목명 지원)
const getStockData = (code: string, dynamicName?: string) => {
  // 확장된 종목명 매핑 (기본 fallback용)
  const nameMap: { [key: string]: string } = {
    '005930': '삼성전자', '000660': 'SK하이닉스', '035420': 'NAVER',
    '051910': 'LG화학', '005380': '현대차', '086520': '에코프로',
    '009540': '한국가스공사', '399720': '퓨처켐', '298040': '효성중공업',
    '036930': '주성엔지니어링', '042700': '한미반도체', '095610': '테스',
    '000720': '현대건설', '004170': '신세계', '006400': '삼성SDI',
    '267260': 'HD현대일렉트릭', '090430': '아모레퍼시픽', '036570': 'NC소프트',
    '207940': '삼성바이오로직스', '079160': 'CGV', '403870': 'HPSP',
    '240810': '원익IPS', '284620': '쿠팡', '005940': 'NH투자증권',
    '016360': '삼성증권', '039490': '키네마스터', '071050': '한국금융지주',
    '352820': 'COI머티리얼즈', '357780': '솔브레인', '084370': '맘스터치',
    // 해외주식
    'NVDA': '엔비디아 (NVDA)', 'TSLA': '테슬라 (TSLA)', 'PLTR': '팔란티어 (PLTR)', 'AMD': 'AMD (AMD)',
    'TSM': 'TSMC (TSM)', 'ASML': 'ASML (ASML)', 'GOOGL': '구글 (GOOGL)', 'MSTR': '마이크로스트래티지 (MSTR)',
    'RKLB': '로켓랩 (RKLB)', 'SQ': '스퀘어 (SQ)', 'RIOT': 'Riot Blockchain (RIOT)',
    'GBTC': '그레이스케일 비트코인 신탁 (GBTC)', 'COIN': '코인베이스 (COIN)', 'IREN': 'IREN (IREN)',
    'GME': '게임스톱 (GME)', 'SOXX': 'SOXX ETF (SOXX)', 'MU': '마이크론 (MU)', 'KS11': '코스피 (KS11)',
    // 코인
    'BTC': '비트코인 (BTC)', 'ETH': '이더리움 (ETH)', 'SOL': '솔라나 (SOL)', 'DOGE': '도지코인 (DOGE)', 'KLAY': '클레이튼 (KLAY)',
  };

  // 한국 종목인지 확인 (숫자로만 이뤄진 코드)
  const isKoreanStock = /^\d+$/.test(code);
  
  // 동적 종목명이 있으면 우선 사용, 없으면 nameMap fallback
  // 해외/코인 종목은 "비트코인 (BTC)" 형식으로 표시
  const baseName = dynamicName || nameMap[code] || code;
  // 공통 유틸 함수로 ticker 중복 방지
  const stockName = isKoreanStock ? baseName : formatStockDisplay(baseName, code);

  const realData = (stockPricesData as any)[code];
  if (realData) {
    return {
      name: stockName,
      price: realData.currentPrice,
      change: realData.change,
      changePercent: realData.changePercent,
    };
  }

  return { name: stockName, price: 0, change: 0, changePercent: 0 };
};

export default function StockDetailClient({ code }: StockDetailClientProps) {
  const [activeTab, setActiveTab] = useState('feed');
  const [isWatched, setIsWatched] = useState(false);
  const [realStockSignals, setRealStockSignals] = useState<any[]>([]);
  const [dynamicStockName, setDynamicStockName] = useState<string>('');
  const searchParams = useSearchParams();
  const router = useRouter();
  const stockData = getStockData(code, dynamicStockName);
  const timeline = getStockTimeline(code);

  // URL 쿼리 파라미터에서 탭 설정
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam && tabs.some(tab => tab.id === tabParam)) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  // Supabase에서 실제 시그널 데이터와 종목명 정보 가져오기
  useEffect(() => {
    const fetchRealStockData = async () => {
      try {
        const signals = await getStockSignals(code);
        setRealStockSignals(signals);
        
        // 시그널 데이터에서 종목명 추출 (첫 번째로 찾은 stock 정보 사용)
        const signalWithStock = signals.find((signal: any) => signal.stock);
        if (signalWithStock && signalWithStock.stock) {
          setDynamicStockName(signalWithStock.stock);
        }
      } catch (error) {
        console.error('Error fetching real stock data:', error);
      }
    };

    fetchRealStockData();
  }, [code]);

  // 해당 종목의 시그널 가져오기
  const getStockSignals = (code: string, name: string) => {
    const stockMapping: { [key: string]: string[] } = {
      '005930': ['삼성전자', '삼성'],
      '000660': ['SK하이닉스', '하이닉스'],
      '035420': ['네이버', 'NAVER'],
      '051910': ['LG화학'],
      '005380': ['현대차', '현대자동차'],
      '005490': ['POSCO홀딩스', '포스코'],
      'BTC': ['비트코인', 'Bitcoin'],
      'ETH': ['이더리움', 'Ethereum']
    };

    const possibleNames = stockMapping[code] || [name];
    const signals: any[] = [];
    
    influencers.forEach(influencer => {
      influencer.recentCalls.forEach(call => {
        const isMatch = possibleNames.some(stockName => 
          call.stock.includes(stockName) || stockName.includes(call.stock)
        );
        
        if (isMatch) {
          signals.push({
            id: `${influencer.id}-${call.stock}`,
            stock: call.stock,
            signal_type: call.direction,
            speaker: influencer.name,
            content_snippet: `${call.stock} ${call.direction} 추천`,
            date: call.date,
            video_published_at: call.date,
            accuracy_rate: influencer.accuracy,
            return_rate: call.returnRate,
            status: call.status
          });
        }
      });
    });
    
    return signals;
  };

  const stockSignals = getStockSignals(code, stockData.name);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'feed':
        return (
          <div className="space-y-4">
            {timeline.map((event) => (
              <FeedCard
                key={event.id}
                icon={event.icon}
                categoryName={event.categoryName}
                title={event.title}
                date={event.time}
                onClick={() => setActiveTab(event.tab)}
              />
            ))}
          </div>
        );

      case 'influencer':
        return <InfluencerTab code={code} />;

      case 'analyst':
        return <StockAnalystTab code={code} />;

      case 'disclosure':
        return <StockDisclosureTab code={code} />;

      case 'earnings':
        return (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-bold text-[#191f28] mb-2">실적 분석</h3>
            <p className="text-[#8b95a1]">상세 실적 분석을 준비중입니다</p>
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

          <div className="flex justify-between items-start">
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
              
              {/* Coverage Stats */}
              <div className="flex items-center gap-4 mt-3 text-sm text-[#8b95a1]">
                <span>인플루언서 12명</span>
                <span>•</span>
                <span>애널리스트 8명</span>
                <span>•</span>
                <span>투자자 5명</span>
                <span>•</span>
                <span>팔로워 3,247명</span>
              </div>
            </div>
            
            {/* Watch Button */}
            <button
              onClick={() => setIsWatched(!isWatched)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isWatched
                  ? 'bg-green-100 text-green-700 border border-green-200'
                  : 'bg-[#3182f6] text-white hover:bg-[#2171e5]'
              }`}
            >
              {isWatched ? '✓ 관심종목 등록됨' : '+ 관심종목 추가'}
            </button>
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

// 애널리스트 탭 컴포넌트 (테이블형 + 실데이터)
function AnalystTab({ code }: { code: string }) {
  const [reports, setReports] = useState<any[]>([]);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const stockData = getStockData(code);

  useEffect(() => {
    const loadReports = async () => {
      try {
        setLoading(true);
        const allReports = (await import('@/data/analyst_reports.json')).default as Record<string, any[]>;
        const tickerReports = (allReports as any)[code] || [];
        setReports(tickerReports);
      } catch {
        setReports([]);
      } finally {
        setLoading(false);
      }
    };
    loadReports();
  }, [code]);

  const getOpinionLabel = (op: string) => {
    switch (op) {
      case 'BUY': return '매수';
      case 'HOLD': return '중립';
      case 'SELL': return '매도';
      default: return op;
    }
  };

  const getOpinionColor = (op: string) => {
    switch (op) {
      case 'BUY': return 'text-green-600 bg-green-100';
      case 'HOLD': return 'text-yellow-600 bg-yellow-100';
      case 'SELL': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getOpinionEmoji = (op: string) => {
    switch (op) {
      case 'BUY': return '🟢';
      case 'HOLD': return '🟡';
      case 'SELL': return '🔴';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="text-lg text-[#8b95a1]">데이터를 불러오는 중...</div>
      </div>
    );
  }

  const avgTarget = reports.filter(r => r.target_price).reduce((s, r) => s + r.target_price, 0) / (reports.filter(r => r.target_price).length || 1);
  const buyCount = reports.filter(r => r.opinion === 'BUY').length;

  return (
    <div className="space-y-6">
      {/* 요약 카드 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-sm text-[#8b95a1] mb-1">평균 목표가</div>
            <div className="text-lg font-bold text-[#191f28]">
              {avgTarget > 0 ? Math.round(avgTarget).toLocaleString() + '원' : '-'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-[#8b95a1] mb-1">리포트 수</div>
            <div className="text-lg font-bold text-[#191f28]">{reports.length}건</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-[#8b95a1] mb-1">매수 의견</div>
            <div className="text-lg font-bold text-blue-600">
              {buyCount}/{reports.length}
            </div>
          </div>
        </div>
      </div>

      {/* 리포트 테이블 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
        <div className="p-6 border-b border-[#e8e8e8]">
          <h4 className="font-medium text-[#191f28]">애널리스트 리포트 이력</h4>
        </div>
        {reports.length === 0 ? (
          <div className="p-8 text-center text-[#8b95a1]">이 종목의 애널리스트 리포트가 없습니다.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#f8f9fa]">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">날짜</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">증권사</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">투자의견</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">리포트 제목</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">목표가</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">리포트</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f0f0f0]">
                {reports.map((report, index) => (
                  <tr
                    key={index}
                    className="hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                    onClick={() => setSelectedReport(report)}
                  >
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">
                      {new Date(report.published_at).toLocaleDateString('ko-KR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </td>
                    <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">
                      {report.firm}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getOpinionEmoji(report.opinion)}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getOpinionColor(report.opinion)}`}>
                          {getOpinionLabel(report.opinion)}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-sm text-[#191f28] max-w-xs">
                      <div className="truncate" title={report.title}>{report.title}</div>
                    </td>
                    <td className="px-4 py-4 text-sm font-medium text-[#191f28] whitespace-nowrap">
                      {report.target_price ? report.target_price.toLocaleString() + '원' : '-'}
                    </td>
                    <td className="px-4 py-4">
                      {report.pdf_url ? (
                        <a
                          href={report.pdf_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#3182f6] hover:text-[#2171e5] text-sm font-medium"
                          onClick={(e) => e.stopPropagation()}
                        >
                          PDF →
                        </a>
                      ) : (
                        <span className="text-[#8b95a1] text-sm">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 리포트 상세 모달 */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setSelectedReport(null)}>
          <div className="bg-white rounded-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="p-6">
              {/* 헤더 */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-[#191f28] mb-2">{selectedReport.title}</h3>
                  <div className="flex items-center gap-2 text-sm text-[#8b95a1]">
                    <span>{selectedReport.firm}</span>
                    <span>·</span>
                    <span>{new Date(selectedReport.published_at).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}</span>
                  </div>
                </div>
                <button onClick={() => setSelectedReport(null)} className="text-[#8b95a1] hover:text-[#191f28] text-xl">✕</button>
              </div>

              {/* 투자의견 + 목표가 */}
              <div className="bg-[#f8f9fa] rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{getOpinionEmoji(selectedReport.opinion)}</span>
                    <span className={`px-3 py-1.5 rounded-full text-sm font-bold ${getOpinionColor(selectedReport.opinion)}`}>
                      {getOpinionLabel(selectedReport.opinion)}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-[#8b95a1]">목표가</div>
                    <div className="text-xl font-bold text-[#191f28]">
                      {selectedReport.target_price ? selectedReport.target_price.toLocaleString() + '원' : '-'}
                    </div>
                  </div>
                </div>
              </div>

              {/* PDF 링크 */}
              {selectedReport.pdf_url && (
                <a
                  href={selectedReport.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full text-center bg-[#3182f6] text-white py-3 rounded-lg font-medium hover:bg-[#2171e5] transition-colors mb-4"
                >
                  📄 PDF 원문 보기
                </a>
              )}

              {/* 종목 정보 */}
              <div className="border-t border-[#e8e8e8] pt-4">
                <div className="text-sm text-[#8b95a1]">
                  종목: {stockData.name} ({code})
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// 인플루언서 탭 컴포넌트
function InfluencerTab({ code }: { code: string }) {
  const [periodFilter, setPeriodFilter] = useState('전체');
  const [influencerFilter, setInfluencerFilter] = useState('전체');
  const [signalData, setSignalData] = useState<any[]>([]);
  const [influencerOptions, setInfluencerOptions] = useState([
    { name: '전체', count: null }
  ]);
  const [loading, setLoading] = useState(true);
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [activeSignalTypes, setActiveSignalTypes] = useState(['매수', '긍정', '중립', '경계', '매도']);
  const [priceData, setPriceData] = useState<Record<string, { price_at_signal: number; price_current: number; return_pct: number }>>({});
  const [likeCounts, setLikeCounts] = useState<Record<string, number>>({});

  const periodOptions = ['1개월', '6개월', '1년', '3년', '전체'];

  // 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        const { getStockSignals, getSignalVoteCounts } = await import('@/lib/supabase');
        const videoSummaries = (await import('@/data/video_summaries.json')).default as Record<string, string>;
        const [signals] = await Promise.all([
          getStockSignals(code),
          fetch('/invest-sns/signal_prices.json')
            .then(r => r.ok ? r.json() : {})
            .then(d => setPriceData(d))
            .catch(() => {}),
        ]);
        
        // 데이터를 UI용 형태로 변환
        const transformedSignals = signals.map((signal: any) => {
          const publishedDate = signal.influencer_videos?.published_at 
            ? new Date(signal.influencer_videos.published_at)
            : new Date();
          
          const videoUrl = (() => {
            const vid = signal.influencer_videos?.video_id;
            if (!vid) return '#';
            let url = `https://youtube.com/watch?v=${vid}`;
            const ts = signal.timestamp;
            if (ts && ts !== 'N/A' && ts !== 'null') {
              const parts = ts.split(':').map(Number);
              const secs = parts.length === 3 ? parts[0]*3600+parts[1]*60+parts[2] : parts.length === 2 ? parts[0]*60+parts[1] : parts[0];
              if (secs > 0) url += `&t=${secs}`;
            }
            return url;
          })();

          const speakerName = signal.speakers?.name || '';
          const channelName = signal.influencer_videos?.influencer_channels?.channel_name || '';
          // 호스트: 채널명만. 게스트: 화자 이름만
          const isHost = !speakerName || !channelName || speakerName === channelName || channelName.includes(speakerName) || speakerName.includes(channelName);
          const influencerDisplay = isHost
            ? (channelName || speakerName || 'Unknown')
            : speakerName;

          return {
            signalId: signal.id,
            date: publishedDate.toISOString().split('T')[0],
            influencer: influencerDisplay,
            signal: signal.signal,
            quote: signal.key_quote || '키 인용문이 없습니다.',
            return: 'N/A',
            videoUrl,
            price: 0,
            confidence: signal.confidence,
            analysis_reasoning: signal.influencer_videos?.video_summary || videoSummaries[signal.video_id] || signal.reasoning,
            mention_type: signal.mention_type,
            timestamp: signal.timestamp,
            videoTitle: signal.influencer_videos?.title,
            channelName,
          };
        });
        
        // published_at 우선 최신순 정렬
        transformedSignals.sort((a: any, b: any) => (b.date || '').localeCompare(a.date || ''));
        setSignalData(transformedSignals);

        // 좋아요 카운트 가져오기
        if (transformedSignals.length > 0) {
          const signalIds = transformedSignals.map((s: any) => s.signalId).filter(Boolean);
          if (signalIds.length > 0) {
            try {
              const counts = await getSignalVoteCounts(signalIds);
              setLikeCounts(counts);
            } catch (e) {
              console.error('Failed to load like counts:', e);
            }
          }
        }
        
        // 인플루언서별 카운트 생성
        const influencerCounts = transformedSignals.reduce((acc: any, signal: any) => {
          acc[signal.influencer] = (acc[signal.influencer] || 0) + 1;
          return acc;
        }, {});
        
        const influencerOpts = [
          { name: '전체', count: null },
          ...Object.entries(influencerCounts).map(([name, count]) => ({
            name,
            count: count as number
          }))
        ];
        
        setInfluencerOptions(influencerOpts);
      } catch (error) {
        console.error('Error loading stock signals:', error);
        setSignalData([]);
      } finally {
        setLoading(false);
      }
    };

    if (code) {
      loadData();
    }
  }, [code]);

  const getLocalSignalColor = (signal: string) => {
    switch (signal) {
      case '매수':
      case 'BUY': return 'text-green-600 bg-green-100';
      case '긍정':
      case 'POSITIVE': return 'text-blue-600 bg-blue-100';
      case '중립':
      case 'NEUTRAL': return 'text-yellow-600 bg-yellow-100';
      case '경계':
      case 'CONCERN': return 'text-orange-600 bg-orange-100';
      case '매도':
      case 'SELL': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSignalEmoji = (signal: string) => {
    switch (signal) {
      case '매수':
      case 'BUY': return '🟢';
      case '긍정':
      case 'POSITIVE': return '🔵';
      case '중립':
      case 'NEUTRAL': return '🟡';
      case '경계':
      case 'CONCERN': return '🟠';
      case '매도':
      case 'SELL': return '🔴';
      default: return '⚪';
    }
  };

  const getSignalText = (signal: string) => {
    // DB는 한글로 저장되어 있으므로 그대로 반환
    return signal;
  };

  // 필터링된 데이터 계산
  const getFilteredSignals = () => {
    let filtered = [...signalData];
    
    // 인플루언서 필터
    if (influencerFilter !== '전체') {
      filtered = filtered.filter(signal => signal.influencer === influencerFilter);
    }
    
    // 기간 필터 (간단한 구현)
    if (periodFilter !== '전체') {
      const now = new Date();
      let cutoffDate = new Date();
      
      switch (periodFilter) {
        case '1개월':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case '6개월':
          cutoffDate.setMonth(now.getMonth() - 6);
          break;
        case '1년':
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
        case '3년':
          cutoffDate.setFullYear(now.getFullYear() - 3);
          break;
      }
      
      filtered = filtered.filter(signal => new Date(signal.date) >= cutoffDate);
    }
    
    return filtered;
  };

  const handleSignalTypeToggle = (type: string) => {
    setActiveSignalTypes(prev => {
      if (prev.includes(type)) {
        // Don't allow deselecting all
        if (prev.length === 1) return prev;
        return prev.filter(t => t !== type);
      }
      return [...prev, type];
    });
  };

  const filteredSignals = getFilteredSignals().filter(s => activeSignalTypes.includes(s.signal));

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="text-lg text-[#8b95a1]">데이터를 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 필터 섹션 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
        <div className="space-y-4">
          {/* 기간 필터 */}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">기간</h4>
            <div className="flex gap-2 flex-wrap">
              {periodOptions.map((period) => (
                <button
                  key={period}
                  onClick={() => setPeriodFilter(period)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    periodFilter === period
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          </div>

          {/* 인플루언서 필터 */}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">인플루언서</h4>
            <div className="flex gap-2 flex-wrap">
              {influencerOptions.map((option) => (
                <button
                  key={option.name}
                  onClick={() => setInfluencerFilter(option.name)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    influencerFilter === option.name
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-[#f8f9fa] text-[#8b95a1] hover:bg-[#e9ecef]'
                  }`}
                >
                  {option.name}
                  {option.count && `(${option.count})`}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 차트 영역 - 실제 Yahoo Finance 데이터 */}
      <StockSignalChart
        code={code}
        signals={getFilteredSignals()}
        periodFilter={periodFilter}
        onSignalClick={(sig) => setSelectedSignal(sig)}
        activeSignalTypes={activeSignalTypes}
        onSignalTypeToggle={handleSignalTypeToggle}
      />

      {/* 신호 테이블 */}
      <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
        <div className="p-6 border-b border-[#e8e8e8]">
          <h4 className="font-medium text-[#191f28]">인플루언서 신호 이력</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#f8f9fa]">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">날짜</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">인플루언서</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">신호</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">핵심발언</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">수익률</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">좋아요</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">영상링크</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f0f0f0]">
              {filteredSignals.map((signal, index) => (
                <tr
                  key={index}
                  className="hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                  onClick={() => setSelectedSignal({
                    ...signal,
                    id: signal.signalId,
                    likeCount: likeCounts[signal.signalId] || 0
                  })}
                >
                  <td className="px-4 py-4 text-sm text-[#191f28]">
                    {new Date(signal.date).toLocaleDateString('ko-KR', { 
                      year: 'numeric',
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </td>
                  <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">
                    {signal.influencer}
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getSignalEmoji(signal.signal)}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getLocalSignalColor(signal.signal)}`}>
                        {getSignalText(signal.signal)}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm text-[#191f28] max-w-xs">
                    <div className="truncate" title={signal.quote}>{signal.quote}</div>
                  </td>
                  <td className="px-4 py-4 text-sm font-medium whitespace-nowrap">
                    {(() => {
                      if (signal.signal === '중립') return <span className="text-[#8b95a1]">N/A</span>;
                      const pd = priceData[signal.signalId];
                      if (!pd || pd.return_pct == null) return <span className="text-[#8b95a1]">-</span>;
                      const ret = pd.return_pct;
                      const isBullish = signal.signal === '매수' || signal.signal === '긍정';
                      const isGood = isBullish ? ret >= 0 : ret <= 0;
                      const color = isGood ? 'text-[#22c55e]' : 'text-[#ef4444]';
                      const arrow = ret >= 0 ? '▲' : '▼';
                      return (
                        <span className={color} title={`${pd.price_at_signal?.toLocaleString()}원 → ${pd.price_current?.toLocaleString()}원`}>
                          {arrow} {ret >= 0 ? '+' : ''}{ret}%
                        </span>
                      );
                    })()}
                  </td>
                  <td className="px-4 py-4 text-sm text-[#8b95a1] whitespace-nowrap">
                    {likeCounts[signal.signalId] > 0 && (
                      <span className="text-red-500">❤️ {likeCounts[signal.signalId]}</span>
                    )}
                  </td>
                  <td className="px-4 py-4">
                    <a
                      href={signal.videoUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#3182f6] hover:text-[#2171e5] text-sm font-medium"
                      onClick={(e) => e.stopPropagation()}
                    >
                      영상보기 →
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 시그널 상세 모달 */}
      <SignalDetailModal
        signal={selectedSignal}
        onClose={() => setSelectedSignal(null)}
      />
    </div>
  );
}