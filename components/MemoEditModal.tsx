import { useState, useEffect } from 'react';
import { WatchlistStock } from '@/data/watchlistData';

interface MemoEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (updates: { memo: string; buyPrice?: number; quantity?: number }) => void;
  stock: WatchlistStock | null;
}

export default function MemoEditModal({ isOpen, onClose, onSave, stock }: MemoEditModalProps) {
  const [memo, setMemo] = useState('');
  const [buyPrice, setBuyPrice] = useState<string>('');
  const [quantity, setQuantity] = useState<string>('');

  // Initialize form when stock changes
  useEffect(() => {
    if (stock) {
      setMemo(stock.memo || '');
      setBuyPrice(stock.buyPrice?.toString() || '');
      setQuantity(''); // We don't have quantity in our data structure, but keeping it for the UI
    }
  }, [stock]);

  if (!isOpen || !stock) return null;

  const handleSave = () => {
    const updates: { memo: string; buyPrice?: number; quantity?: number } = {
      memo: memo.trim()
    };

    if (buyPrice.trim()) {
      const price = parseInt(buyPrice.replace(/,/g, ''));
      if (!isNaN(price)) {
        updates.buyPrice = price;
      }
    }

    if (quantity.trim()) {
      const qty = parseInt(quantity.replace(/,/g, ''));
      if (!isNaN(qty)) {
        updates.quantity = qty;
      }
    }

    onSave(updates);
    onClose();
  };

  const formatNumber = (value: string) => {
    const num = value.replace(/[^0-9]/g, '');
    return num.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  const handleBuyPriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatNumber(e.target.value);
    setBuyPrice(formatted);
  };

  const handleQuantityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatNumber(e.target.value);
    setQuantity(formatted);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-lg mx-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-bold">{stock.name} 메모 ?�집</h2>
          <button 
            onClick={onClose}
            className="text-[#8b95a1] hover:text-gray-600 text-xl"
          >
            ??
          </button>
        </div>

        {/* Form */}
        <div className="space-y-4">
          {/* Memo Textarea */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              메모
            </label>
            <textarea
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="?�자 메모�??�력?�세??.."
              rows={3}
              className="w-full px-4 py-2 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#3182f6] resize-none"
            />
          </div>

          {/* Buy Price Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              매수가 (??
            </label>
            <input
              type="text"
              value={buyPrice}
              onChange={handleBuyPriceChange}
              placeholder="0"
              className="w-full px-4 py-2 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
            />
          </div>

          {/* Quantity Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              매수 ?�량 (�?
            </label>
            <input
              type="text"
              value={quantity}
              onChange={handleQuantityChange}
              placeholder="0"
              className="w-full px-4 py-2 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-200 rounded-2xl text-gray-600 hover:bg-[#f2f4f6] transition-colors"
          >
            취소
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2 bg-[#3182f6] text-white rounded-2xl hover:bg-[#00c499] transition-colors"
          >
            ?�??
          </button>
        </div>
      </div>
    </div>
  );
}