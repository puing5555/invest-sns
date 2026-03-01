'use client';

import { NewBuy, Increase, Decrease, SoldStock } from '../data/guruData';

interface PortfolioChangeProps {
  newBuys: NewBuy[];
  increased: Increase[];
  decreased: Decrease[];
  soldAll: SoldStock[];
}

export default function PortfolioChange({ newBuys, increased, decreased, soldAll }: PortfolioChangeProps) {
  return (
    <div className="space-y-6">
      {/* 새로 산 것 */}
      {newBuys.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-3">
            <span className="text-green-500">🟢</span>
            새로 산 것
          </h4>
          <div className="grid gap-3">
            {newBuys.map((stock, index) => (
              <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-bold text-gray-900">
                      {stock.name} {stock.ticker && !/^\d+$/.test(stock.ticker) && <span className="text-gray-500 font-normal">({stock.ticker})</span>}
                    </div>
                  </div>
                  <div className="text-green-600 font-semibold">
                    {stock.amount}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 더 산 것 */}
      {increased.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-3">
            <span className="text-blue-500">🔼</span>
            더 산 것
          </h4>
          <div className="space-y-2">
            {increased.map((stock, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <div className="font-bold text-gray-900">
                  {stock.name} {stock.ticker && !/^\d+$/.test(stock.ticker) && <span className="text-gray-500 font-normal">({stock.ticker})</span>}
                </div>
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 rounded-full px-3 py-1">
                    <span className="text-blue-600 font-semibold text-sm">+{stock.percentage}%</span>
                  </div>
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${Math.min(stock.percentage * 5, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 줄인 것 */}
      {decreased.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-3">
            <span className="text-orange-500">🔽</span>
            줄인 것
          </h4>
          <div className="space-y-2">
            {decreased.map((stock, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <div className="font-bold text-gray-900">
                  {stock.name} {stock.ticker && !/^\d+$/.test(stock.ticker) && <span className="text-gray-500 font-normal">({stock.ticker})</span>}
                </div>
                <div className="flex items-center gap-3">
                  <div className="bg-orange-100 rounded-full px-3 py-1">
                    <span className="text-orange-600 font-semibold text-sm">-{stock.percentage}%</span>
                  </div>
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-orange-500 h-2 rounded-full"
                      style={{ width: `${Math.min(stock.percentage * 5, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 다 판 것 */}
      {soldAll.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-3">
            <span className="text-red-500">🔴</span>
            다 판 것
          </h4>
          <div className="flex flex-wrap gap-2">
            {soldAll.map((stock, index) => (
              <div key={index} className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 flex items-center gap-2">
                <span className="font-bold text-gray-900">
                  {stock.name} {stock.ticker && !/^\d+$/.test(stock.ticker) && <span className="text-gray-500 font-normal">({stock.ticker})</span>}
                </span>
                <span className="text-red-500">✕</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
