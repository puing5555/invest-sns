import { useState } from 'react';
import { searchResults } from '@/data/watchlistData';

interface AddStockModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (stockName: string) => void;
}

export default function AddStockModal({ isOpen, onClose, onAdd }: AddStockModalProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredResults = searchResults.filter(stock =>
    stock.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  const handleAdd = (stockName: string) => {
    onAdd(stockName);
    onClose();
    setSearchTerm('');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">종목 추�?</h2>
          <button 
            onClick={onClose}
            className="text-[#8b95a1] hover:text-gray-600 text-xl"
          >
            ??
          </button>
        </div>

        {/* Search Input */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="종목�??�는 코드 검??
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
            autoFocus
          />
        </div>

        {/* Results List */}
        <div className="max-h-64 overflow-y-auto">
          {filteredResults.length > 0 ? (
            <div className="space-y-1">
              {filteredResults.map((stock, index) => (
                <button
                  key={index}
                  onClick={() => handleAdd(stock)}
                  className="w-full text-left px-4 py-3 hover:bg-[#f2f4f6] rounded-2xl transition-colors"
                >
                  {stock}
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-[#8b95a1]">
              검??결과가 ?�습?�다
            </div>
          )}
        </div>
      </div>
    </div>
  );
}