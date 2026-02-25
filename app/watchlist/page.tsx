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

type FilterType = 'all' | 'profit' | 'loss' | 'signals' | 'review';

export default function WatchlistPage() {
  const [stocks, setStocks] = useState<WatchlistStock[]>(watchlistStocks);
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
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
    { key: 'review' as FilterType, label: '📋 매매 복기', count: tradeReviewData.length }
  ];

  const getFilteredStocks = () => {
    switch (activeFilter) {
      case 'profit':
        return stocks.filter(s => s.profitRate && s.profitRate > 0);
      case 'loss':
        return stocks.filter(s => s.profitRate && s.profitRate < 0);
      case 'signals':
        return stocks.filter(s => s.badges.length > 0);
      case 'review':
        return []; // Review tab doesn't show stocks, shows TradeReviewCards instead
      default:
        return stocks;
    }
  };

  const handleAddStock = (stockName: string) => {
    // Simple implementation - in a real app, you'd fetch stock data from an API
    const newStock: WatchlistStock = {
      id: Date.now().toString(),
      name: stockName,
      code: '000000', // Placeholder
      currentPrice: 50000, // Placeholder
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
          // Recalculate profit rate if we have a buy price
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
          // Recalculate profit rate if we have a buy price
          if (updates.buyPrice > 0) {
            updatedStock.profitRate = ((stock.currentPrice - updates.buyPrice) / updates.buyPrice) * 100;
          }
        }
        
        // Note: stopLoss, takeProfit1, takeProfit2 are stored in tradeData, not in stock object
        // In a real app, you'd save these to a backend or separate state
        
        return updatedStock;
      }
      return stock;
    }));

    setSelectedStock(null);
  };

  const filteredStocks = getFilteredStocks();

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">⭐️ 관심종목</h1>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 bg-[#00d4aa] text-white rounded-lg hover:bg-[#00c499] transition-colors font-medium"
          >
            + 종목 추가
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-1 mb-6 bg-gray-50 rounded-lg p-1">
          {filterTabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveFilter(tab.key)}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeFilter === tab.key
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="space-y-4">
          {activeFilter === 'review' ? (
            // Trade Review Cards
            tradeReviewData.length > 0 ? (
              tradeReviewData.map(trade => (
                <TradeReviewCard key={trade.id} trade={trade} />
              ))
            ) : (
              <div className="text-center py-12 text-gray-500">
                <div className="text-lg mb-2">📊</div>
                <div>매매 기록이 없습니다</div>
                <div className="text-sm">매매를 완료하면 여기에 나타납니다</div>
              </div>
            )
          ) : (
            // Stock Cards
            filteredStocks.length > 0 ? (
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
              <div className="text-center py-12 text-gray-500">
                <div className="text-lg mb-2">📋</div>
                <div>관심종목이 없습니다</div>
                <div className="text-sm">종목을 추가해보세요</div>
              </div>
            )
          )}
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
    </div>
  );
}