'use client';

import { useState } from 'react';
import { WatchlistStock, watchlistStocks } from '@/data/watchlistData';
import { tradeReviewData } from '@/data/tradeData';
import WatchlistCard from '@/components/WatchlistCard';
import AddStockModal from '@/components/AddStockModal';
import MemoEditModal from '@/components/MemoEditModal';
import TradeSetupModal from '@/components/TradeSetupModal';
import TradeAnalysisPanel from '@/components/TradeAnalysisPanel';
import TradeReviewCard from '@/components/TradeReviewCard';
import FeedPost, { PostData } from '@/components/FeedPost';

// 관심종목 칩 데이터
const stockChips = [
  { name: '전체', isActive: true },
  { name: '삼성전자', change: '+0.8%', isPositive: true },
  { name: '현대차', change: '+2.1%', isPositive: true },
  { name: 'SK하이닉스', change: '-1.2%', isPositive: false },
  { name: 'LG에너지', change: '+0.5%', isPositive: true },
  { name: 'NAVER', change: '-0.3%', isPositive: false },
];

// 타임라인 샘플 데이터 (기존 피드 데이터 재활용)
const timelinePosts: PostData[] = [
  {
    id: 1,
    name: 'A등급 공시 속보',
    handle: 'system',
    avatar: 'system',
    time: '3분전',
    text: '삼성전자 — 3분기 실적 컨센서스 상회 발표\n\n🤖 AI 분석: 메모리 슈퍼사이클 본격화. HBM 매출 비중 확대\n시그널 스코어 82점 🔥',
    isSystem: true,
    comments_count: 245,
    reposts: 334,
    likes: 2100,
    views: 156000,
    poll: {
      options: [
        { label: '매수', emoji: '🟢', percent: 78, color: '#00c853' },
        { label: '매도', emoji: '🔴', percent: 8, color: '#f44336' },
        { label: '관망', emoji: '🟡', percent: 14, color: '#eab308' },
      ],
      totalVotes: 3247,
    },
  },
  {
    id: 2,
    name: '코린이아빠',
    handle: 'korini_papa',
    avatar: 'https://i.pravatar.cc/150?img=11',
    verified: true,
    accuracy: 68,
    time: '15분전',
    text: '현대차 220,000 돌파했네요! 🚗\n\n제가 205,000에 추천했던 구간이었는데\n+7.3% 수익률입니다.\n\n전기차 전환 이슈보다\n중국 진출 확대가 더 중요한 포인트였습니다.\n\n목표가: 240,000\n손절: 200,000\n\n⚠️ 단타보다는 스윙 추천',
    comments_count: 156,
    reposts: 234,
    likes: 1580,
    views: 67000,
  },
  {
    id: 3,
    name: '반도체 전문가',
    handle: 'semi_expert',
    avatar: 'https://i.pravatar.cc/150?img=25',
    verified: true,
    accuracy: 74,
    time: '1시간전',
    text: 'SK하이닉스 실적 발표 임박 📊\n\nHBM3E 출하량이 예상보다 20% 증가\n마진율도 개선되고 있어서\n이번 분기 깜짝 실적 가능성 높습니다.\n\n현재가 기준으로도 충분히 매력적\n\n#SK하이닉스 #HBM #메모리',
    comments_count: 89,
    reposts: 145,
    likes: 956,
    views: 45000,
  },
  {
    id: 4,
    name: '💼 임원매매 알림',
    handle: 'system', 
    avatar: 'system',
    time: '2시간전',
    text: 'LG에너지솔루션 임원 매매 현황\n\n김○○ 상무: 5억원 규모 매수 (3일차)\n박○○ 전무: 8억원 규모 매수 (2일차)\n\n🔍 분석: 대규모 임원 매수 집중\n내부 정보 기반 포지션 확대로 해석',
    isSystem: true,
    comments_count: 67,
    reposts: 123,
    likes: 834,
    views: 34000,
  },
  {
    id: 5,
    name: '애널리스트 정○○',
    handle: 'analyst_jung',
    avatar: 'https://i.pravatar.cc/150?img=42',
    verified: true,
    time: '3시간전',
    text: 'NAVER 목표가 상향 조정 📈\n\n기존: 180,000 → 신규: 200,000\n투자의견: Buy 유지\n\n클라우드 사업 본격 성장\n웹툰/게임 해외 진출 가속화\n\n현재 밸류에이션 매력적 수준',
    comments_count: 78,
    reposts: 156,
    likes: 1234,
    views: 56000,
  }
];

type FilterType = 'all' | 'profit' | 'loss' | 'signals';

export default function MyStocksPage() {
  const [stocks, setStocks] = useState<WatchlistStock[]>(watchlistStocks);
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [selectedChip, setSelectedChip] = useState('전체');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isMemoModalOpen, setIsMemoModalOpen] = useState(false);
  const [isTradeSetupModalOpen, setIsTradeSetupModalOpen] = useState(false);
  const [isAnalysisPanelOpen, setIsAnalysisPanelOpen] = useState(false);
  const [selectedStock, setSelectedStock] = useState<WatchlistStock | null>(null);
  const [selectedStockName, setSelectedStockName] = useState<string | null>(null);

  const filterTabs = [
    { key: 'all' as FilterType, label: '전체', count: stocks.length },
    { key: 'profit' as FilterType, label: '수익중', count: stocks.filter(s => s.profitRate && s.profitRate > 0).length },
    { key: 'loss' as FilterType, label: '손실중', count: stocks.filter(s => s.profitRate && s.profitRate < 0).length },
    { key: 'signals' as FilterType, label: '시그널있음', count: stocks.filter(s => s.badges.length > 0).length },
  ];

  const getFilteredStocks = () => {
    switch (activeFilter) {
      case 'profit':
        return stocks.filter(s => s.profitRate && s.profitRate > 0);
      case 'loss':
        return stocks.filter(s => s.profitRate && s.profitRate < 0);
      case 'signals':
        return stocks.filter(s => s.badges.length > 0);
      default:
        return stocks;
    }
  };

  const handleAddStock = (stockName: string) => {
    const newStock: WatchlistStock = {
      id: Date.now().toString(),
      name: stockName,
      code: '000000',
      currentPrice: 50000,
      changePercent: 0,
      buyPrice: null,
      profitRate: null,
      badges: [],
      alert: {
        message: '새로운 관심종목이 추가되었습니다',
        timeAgo: '방금'
      },
      memo: null
    };

    setStocks(prev => [...prev, newStock]);
  };

  const handleMemoClick = (stock: WatchlistStock) => {
    setSelectedStock(stock);
    setIsMemoModalOpen(true);
  };

  const handleMemoSave = (updates: { memo: string; buyPrice?: number; quantity?: number }) => {
    if (!selectedStock) return;

    setStocks(prev => prev.map(stock => {
      if (stock.id === selectedStock.id) {
        const updatedStock = { ...stock };
        updatedStock.memo = updates.memo || null;
        
        if (updates.buyPrice !== undefined) {
          updatedStock.buyPrice = updates.buyPrice;
          if (updates.buyPrice > 0) {
            updatedStock.profitRate = ((stock.currentPrice - updates.buyPrice) / updates.buyPrice) * 100;
          }
        }
        
        return updatedStock;
      }
      return stock;
    }));

    setSelectedStock(null);
  };

  const handleRemoveStock = (stockId: string) => {
    setStocks(prev => prev.filter(stock => stock.id !== stockId));
  };

  const handleAnalysisClick = (stockName: string) => {
    setSelectedStockName(stockName);
    setIsAnalysisPanelOpen(true);
  };

  const handleSetupClick = (stockName: string) => {
    const stock = stocks.find(s => s.name === stockName);
    if (stock) {
      setSelectedStock(stock);
      setIsTradeSetupModalOpen(true);
    }
  };

  const handleTradeSetupSave = (updates: { 
    memo?: string; 
    buyPrice?: number; 
    quantity?: number;
    stopLoss?: number;
    takeProfit1?: number;
    takeProfit2?: number;
  }) => {
    if (!selectedStock) return;

    setStocks(prev => prev.map(stock => {
      if (stock.id === selectedStock.id) {
        const updatedStock = { ...stock };
        
        if (updates.buyPrice !== undefined) {
          updatedStock.buyPrice = updates.buyPrice;
          if (updates.buyPrice > 0) {
            updatedStock.profitRate = ((stock.currentPrice - updates.buyPrice) / updates.buyPrice) * 100;
          }
        }
        
        return updatedStock;
      }
      return stock;
    }));

    setSelectedStock(null);
  };

  const filteredStocks = getFilteredStocks();

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-[#191f28]">⭐ 내 종목</h1>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#2171e5] transition-colors font-medium text-sm"
          >
            + 종목 추가
          </button>
        </div>
      </div>

      {/* 관심종목 칩 */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-3">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide">
          {stockChips.map((chip, index) => (
            <button
              key={index}
              onClick={() => setSelectedChip(chip.name)}
              className={`flex-shrink-0 px-3 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedChip === chip.name
                  ? 'bg-[#3182f6] text-white'
                  : 'bg-[#f8f9fa] text-[#191f28] hover:bg-[#e9ecef]'
              }`}
            >
              {chip.name}
              {chip.change && (
                <span className={`ml-1 ${chip.isPositive ? 'text-red-500' : 'text-blue-500'}`}>
                  {chip.change}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="bg-white border-b border-[#e8e8e8] px-4">
        <div className="flex gap-1">
          {filterTabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveFilter(tab.key)}
              className={`px-4 py-3 text-sm font-medium transition-colors relative ${
                activeFilter === tab.key
                  ? 'text-[#3182f6]'
                  : 'text-[#8b95a1] hover:text-[#191f28]'
              }`}
            >
              {tab.label} ({tab.count})
              {activeFilter === tab.key && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#3182f6]" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex gap-6 max-w-6xl mx-auto px-4 py-6">
        {/* Left Column - 관심종목 카드 */}
        <div className="flex-1 space-y-4">
          {filteredStocks.length > 0 ? (
            filteredStocks.map(stock => (
              <WatchlistCard
                key={stock.id}
                stock={stock}
                onMemoClick={handleMemoClick}
                onRemove={handleRemoveStock}
                onAnalysisClick={handleAnalysisClick}
                onSetupClick={handleSetupClick}
              />
            ))
          ) : (
            <div className="bg-white rounded-lg p-8 text-center">
              <div className="text-lg mb-2">📋</div>
              <div className="text-[#191f28] font-medium mb-1">관심종목이 없습니다</div>
              <div className="text-sm text-[#8b95a1]">종목을 추가해보세요</div>
            </div>
          )}
        </div>

        {/* Right Column - 실시간 타임라인 */}
        <div className="w-96">
          <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
            <div className="px-4 py-3 border-b border-[#e8e8e8]">
              <h2 className="font-bold text-[#191f28]">실시간 타임라인</h2>
              <p className="text-xs text-[#8b95a1] mt-1">내 종목 관련 소식</p>
            </div>
            <div className="divide-y divide-[#f0f0f0]">
              {timelinePosts.map((post) => (
                <div key={post.id} className="p-4">
                  <FeedPost post={post} compact />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <AddStockModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onAdd={handleAddStock}
      />

      <MemoEditModal
        isOpen={isMemoModalOpen}
        onClose={() => setIsMemoModalOpen(false)}
        onSave={handleMemoSave}
        stock={selectedStock}
      />

      <TradeSetupModal
        isOpen={isTradeSetupModalOpen}
        onClose={() => setIsTradeSetupModalOpen(false)}
        onSave={handleTradeSetupSave}
        stock={selectedStock}
      />

      <TradeAnalysisPanel
        isOpen={isAnalysisPanelOpen}
        onClose={() => setIsAnalysisPanelOpen(false)}
        stockName={selectedStockName}
      />
    </div>
  );
}