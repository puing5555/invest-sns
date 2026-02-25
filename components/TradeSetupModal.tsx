import { useState, useEffect } from 'react';
import { WatchlistStock } from '@/data/watchlistData';

interface TradeSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (updates: { 
    memo?: string; 
    buyPrice?: number; 
    quantity?: number;
    stopLoss?: number;
    takeProfit1?: number;
    takeProfit2?: number;
  }) => void;
  stock: WatchlistStock | null;
}

export default function TradeSetupModal({ isOpen, onClose, onSave, stock }: TradeSetupModalProps) {
  const [buyPrice, setBuyPrice] = useState<string>('');
  const [quantity, setQuantity] = useState<string>('');
  const [stopLoss, setStopLoss] = useState<string>('');
  const [takeProfit1, setTakeProfit1] = useState<string>('');
  const [takeProfit2, setTakeProfit2] = useState<string>('');

  useEffect(() => {
    if (stock) {
      setBuyPrice(stock.buyPrice?.toString() || '');
      setQuantity('');
      setStopLoss('');
      setTakeProfit1('');
      setTakeProfit2('');
    }
  }, [stock]);

  if (!isOpen || !stock) return null;

  const formatNumber = (value: string) => {
    const num = value.replace(/[^0-9]/g, '');
    return num.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  const handleNumberChange = (setter: React.Dispatch<React.SetStateAction<string>>) => 
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const formatted = formatNumber(e.target.value);
      setter(formatted);
    };

  const getAISuggestion = (type: 'stopLoss' | 'tp1' | 'tp2', basePrice: number) => {
    switch (type) {
      case 'stopLoss':
        return Math.round(basePrice * 0.93); // -7%
      case 'tp1':
        return Math.round(basePrice * 1.15); // +15%
      case 'tp2':
        return Math.round(basePrice * 1.25); // +25%
      default:
        return 0;
    }
  };

  const applySuggestion = (type: 'stopLoss' | 'tp1' | 'tp2') => {
    const basePrice = parseInt(buyPrice.replace(/,/g, '')) || stock.currentPrice;
    const suggestion = getAISuggestion(type, basePrice);
    const formatted = formatNumber(suggestion.toString());
    
    switch (type) {
      case 'stopLoss':
        setStopLoss(formatted);
        break;
      case 'tp1':
        setTakeProfit1(formatted);
        break;
      case 'tp2':
        setTakeProfit2(formatted);
        break;
    }
  };

  const handleAIAutoSetup = () => {
    const basePrice = parseInt(buyPrice.replace(/,/g, '')) || stock.currentPrice;
    setStopLoss(formatNumber(getAISuggestion('stopLoss', basePrice).toString()));
    setTakeProfit1(formatNumber(getAISuggestion('tp1', basePrice).toString()));
    setTakeProfit2(formatNumber(getAISuggestion('tp2', basePrice).toString()));
    if (!quantity) {
      setQuantity('100'); // Default quantity suggestion
    }
  };

  const handleSave = () => {
    const updates: { 
      buyPrice?: number; 
      quantity?: number;
      stopLoss?: number;
      takeProfit1?: number;
      takeProfit2?: number;
    } = {};

    if (buyPrice.trim()) {
      const price = parseInt(buyPrice.replace(/,/g, ''));
      if (!isNaN(price)) updates.buyPrice = price;
    }

    if (quantity.trim()) {
      const qty = parseInt(quantity.replace(/,/g, ''));
      if (!isNaN(qty)) updates.quantity = qty;
    }

    if (stopLoss.trim()) {
      const price = parseInt(stopLoss.replace(/,/g, ''));
      if (!isNaN(price)) updates.stopLoss = price;
    }

    if (takeProfit1.trim()) {
      const price = parseInt(takeProfit1.replace(/,/g, ''));
      if (!isNaN(price)) updates.takeProfit1 = price;
    }

    if (takeProfit2.trim()) {
      const price = parseInt(takeProfit2.replace(/,/g, ''));
      if (!isNaN(price)) updates.takeProfit2 = price;
    }

    onSave(updates);
    onClose();
  };

  const basePrice = parseInt(buyPrice.replace(/,/g, '')) || stock.currentPrice;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-bold">{stock.name} 매매 설정</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            ✕
          </button>
        </div>

        {/* Form */}
        <div className="space-y-4">
          {/* Buy Price */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              매수가 (원)
            </label>
            <input
              type="text"
              value={buyPrice}
              onChange={handleNumberChange(setBuyPrice)}
              placeholder={formatNumber(stock.currentPrice.toString())}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00d4aa]"
            />
          </div>

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              매수 수량 (주)
            </label>
            <input
              type="text"
              value={quantity}
              onChange={handleNumberChange(setQuantity)}
              placeholder="100"
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00d4aa]"
            />
          </div>

          {/* Stop Loss */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              손절가 (원)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={stopLoss}
                onChange={handleNumberChange(setStopLoss)}
                placeholder="0"
                className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00d4aa]"
              />
              <button
                onClick={() => applySuggestion('stopLoss')}
                className="px-3 py-2 text-xs border border-[#00d4aa] text-[#00d4aa] rounded-lg hover:bg-[#00d4aa] hover:text-white transition-colors whitespace-nowrap"
              >
                AI 제안: -7% ({formatNumber(getAISuggestion('stopLoss', basePrice).toString())}원)
              </button>
            </div>
          </div>

          {/* Take Profit 1 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              1차 익절가 (원)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={takeProfit1}
                onChange={handleNumberChange(setTakeProfit1)}
                placeholder="0"
                className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00d4aa]"
              />
              <button
                onClick={() => applySuggestion('tp1')}
                className="px-3 py-2 text-xs border border-[#00d4aa] text-[#00d4aa] rounded-lg hover:bg-[#00d4aa] hover:text-white transition-colors whitespace-nowrap"
              >
                AI 제안: +15% ({formatNumber(getAISuggestion('tp1', basePrice).toString())}원)
              </button>
            </div>
          </div>

          {/* Take Profit 2 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              2차 익절가 (원)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={takeProfit2}
                onChange={handleNumberChange(setTakeProfit2)}
                placeholder="0"
                className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00d4aa]"
              />
              <button
                onClick={() => applySuggestion('tp2')}
                className="px-3 py-2 text-xs border border-[#00d4aa] text-[#00d4aa] rounded-lg hover:bg-[#00d4aa] hover:text-white transition-colors whitespace-nowrap"
              >
                AI 제안: +25% ({formatNumber(getAISuggestion('tp2', basePrice).toString())}원)
              </button>
            </div>
          </div>

          {/* AI Auto Setup */}
          <button
            onClick={handleAIAutoSetup}
            className="w-full px-4 py-2 bg-[#00d4aa] text-white rounded-lg hover:bg-[#00c499] transition-colors font-medium"
          >
            🤖 AI 자동 설정
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
          >
            취소
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2 bg-[#00d4aa] text-white rounded-lg hover:bg-[#00c499] transition-colors"
          >
            저장
          </button>
        </div>
      </div>
    </div>
  );
}