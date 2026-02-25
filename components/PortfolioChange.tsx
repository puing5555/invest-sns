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
      {/* ?àÎ°ú ??Í≤?*/}
      {newBuys.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-lg font-semibold text-[#191f28] mb-3">
            <span className="text-green-500">?ü¢</span>
            ?àÎ°ú ??Í≤?          </h4>
          <div className="grid gap-3">
            {newBuys.map((stock, index) => (
              <div key={index} className="bg-green-50 border border-green-200 rounded-2xl p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-bold text-[#191f28]">
                      {stock.name} <span className="text-[#8b95a1] font-normal">({stock.ticker})</span>
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

      {/* ????Í≤?*/}
      {increased.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-lg font-semibold text-[#191f28] mb-3">
            <span className="text-blue-500">?îº</span>
            ????Í≤?          </h4>
          <div className="space-y-2">
            {increased.map((stock, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <div className="font-bold text-[#191f28]">
                  {stock.name} <span className="text-[#8b95a1] font-normal">({stock.ticker})</span>
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

      {/* Ï§ÑÏù∏ Í≤?*/}
      {decreased.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-lg font-semibold text-[#191f28] mb-3">
            <span className="text-orange-500">?îΩ</span>
            Ï§ÑÏù∏ Í≤?          </h4>
          <div className="space-y-2">
            {decreased.map((stock, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <div className="font-bold text-[#191f28]">
                  {stock.name} <span className="text-[#8b95a1] font-normal">({stock.ticker})</span>
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

      {/* ????Í≤?*/}
      {soldAll.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-lg font-semibold text-[#191f28] mb-3">
            <span className="text-red-500">?î¥</span>
            ????Í≤?          </h4>
          <div className="flex flex-wrap gap-2">
            {soldAll.map((stock, index) => (
              <div key={index} className="bg-red-50 border border-red-200 rounded-2xl px-3 py-2 flex items-center gap-2">
                <span className="font-bold text-[#191f28]">
                  {stock.name} <span className="text-[#8b95a1] font-normal">({stock.ticker})</span>
                </span>
                <span className="text-red-500">??/span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}