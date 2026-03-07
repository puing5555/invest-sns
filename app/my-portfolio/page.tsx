'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import {
  getUserStocks,
  addUserStock,
  updateUserStock,
  deleteUserStock,
  getPortfolioSummary,
  type PortfolioSummary,
} from '@/lib/api/user-stocks';
import {
  getUserWatchlist,
  addToWatchlist,
  removeFromWatchlistByCode,
} from '@/lib/api/user-watchlist';
import type { Database } from '@/types/supabase';

type UserStock = Database['public']['Tables']['user_stocks']['Row'];
type UserWatchlist = Database['public']['Tables']['user_watchlist']['Row'];

// 보유종목 추가/수정 모달
function StockModal({
  isOpen, onClose, onSubmit, editStock,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { stock_code: string; stock_name: string; market: string; quantity: number; avg_buy_price: number; notes?: string }) => void;
  editStock?: UserStock | null;
}) {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [market, setMarket] = useState('KOSPI');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (editStock) {
      setCode(editStock.stock_code);
      setName(editStock.stock_name);
      setMarket(editStock.market);
      setQuantity(String(editStock.quantity));
      setPrice(String(editStock.avg_buy_price));
      setNotes(editStock.notes || '');
    } else {
      setCode(''); setName(''); setMarket('KOSPI'); setQuantity(''); setPrice(''); setNotes('');
    }
  }, [editStock, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-lg font-bold text-[#191f28]">{editStock ? '종목 수정' : '보유종목 추가'}</h2>
          <button onClick={onClose} className="text-[#8b95a1] text-xl">✕</button>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목코드</label>
              <input value={code} onChange={e => setCode(e.target.value)} disabled={!!editStock}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] disabled:bg-gray-50"
                placeholder="005930" />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목명</label>
              <input value={name} onChange={e => setName(e.target.value)} disabled={!!editStock}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] disabled:bg-gray-50"
                placeholder="삼성전자" />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">시장</label>
            <select value={market} onChange={e => setMarket(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]">
              <option value="KOSPI">KOSPI</option>
              <option value="KOSDAQ">KOSDAQ</option>
              <option value="NASDAQ">NASDAQ</option>
              <option value="NYSE">NYSE</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">수량</label>
              <input type="number" value={quantity} onChange={e => setQuantity(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="10" />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">평균매수가</label>
              <input type="number" value={price} onChange={e => setPrice(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="70000" />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">메모 (선택)</label>
            <input value={notes} onChange={e => setNotes(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
              placeholder="메모를 입력하세요" />
          </div>
          <button
            onClick={() => {
              if (!code || !name || !quantity || !price) return;
              onSubmit({ stock_code: code, stock_name: name, market, quantity: Number(quantity), avg_buy_price: Number(price), notes: notes || undefined });
            }}
            className="w-full py-3 bg-[#3182f6] text-white rounded-xl font-medium hover:bg-[#1b64da] transition-colors">
            {editStock ? '수정하기' : '추가하기'}
          </button>
        </div>
      </div>
    </div>
  );
}

// 관심종목 추가 모달
function WatchlistModal({
  isOpen, onClose, onSubmit,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { stock_code: string; stock_name: string; market: string; notes?: string; alert_on_signals: boolean }) => void;
}) {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [market, setMarket] = useState('KOSPI');
  const [notes, setNotes] = useState('');
  const [alertSignals, setAlertSignals] = useState(true);

  useEffect(() => {
    if (!isOpen) { setCode(''); setName(''); setMarket('KOSPI'); setNotes(''); setAlertSignals(true); }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-lg font-bold text-[#191f28]">⭐️ 관심종목 추가</h2>
          <button onClick={onClose} className="text-[#8b95a1] text-xl">✕</button>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목코드</label>
              <input value={code} onChange={e => setCode(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#f5a623]"
                placeholder="005930" />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목명</label>
              <input value={name} onChange={e => setName(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#f5a623]"
                placeholder="삼성전자" />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">시장</label>
            <select value={market} onChange={e => setMarket(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#f5a623]">
              <option value="KOSPI">KOSPI</option>
              <option value="KOSDAQ">KOSDAQ</option>
              <option value="NASDAQ">NASDAQ</option>
              <option value="NYSE">NYSE</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">메모 (선택)</label>
            <input value={notes} onChange={e => setNotes(e.target.value)}
              className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#f5a623]"
              placeholder="관심 이유 등" />
          </div>
          <label className="flex items-center gap-3 cursor-pointer">
            <div
              onClick={() => setAlertSignals(!alertSignals)}
              className={`w-11 h-6 rounded-full transition-colors ${alertSignals ? 'bg-[#f5a623]' : 'bg-[#e8e8e8]'} relative`}>
              <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform shadow ${alertSignals ? 'translate-x-6' : 'translate-x-1'}`} />
            </div>
            <span className="text-sm text-[#191f28]">시그널 알림 받기</span>
          </label>
          <button
            onClick={() => {
              if (!code || !name) return;
              onSubmit({ stock_code: code, stock_name: name, market, notes: notes || undefined, alert_on_signals: alertSignals });
            }}
            className="w-full py-3 bg-[#f5a623] text-white rounded-xl font-medium hover:bg-[#e09400] transition-colors">
            관심 추가
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MyPortfolioPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  // 보유종목
  const [stocks, setStocks] = useState<UserStock[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editStock, setEditStock] = useState<UserStock | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  // 관심종목
  const [watchlist, setWatchlist] = useState<UserWatchlist[]>([]);
  const [watchModalOpen, setWatchModalOpen] = useState(false);
  const [watchDeleteConfirm, setWatchDeleteConfirm] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) { router.push('/login'); return; }
    loadData();
  }, [user, authLoading]);

  const loadData = async () => {
    setLoading(true);
    const [stocksRes, summaryRes, watchRes] = await Promise.all([
      getUserStocks(),
      getPortfolioSummary(),
      getUserWatchlist(),
    ]);
    if (stocksRes.data) setStocks(stocksRes.data);
    if (summaryRes.data) setSummary(summaryRes.data);
    if (watchRes.data) setWatchlist(watchRes.data);
    setLoading(false);
  };

  const handleAdd = async (data: any) => {
    const { error } = await addUserStock(data);
    if (error) { alert('추가 실패: ' + error.message); return; }
    setModalOpen(false);
    loadData();
  };

  const handleEdit = async (data: any) => {
    if (!editStock) return;
    const { error } = await updateUserStock(editStock.id, {
      quantity: data.quantity,
      avg_buy_price: data.avg_buy_price,
      notes: data.notes,
    });
    if (error) { alert('수정 실패: ' + error.message); return; }
    setEditStock(null);
    setModalOpen(false);
    loadData();
  };

  const handleDelete = async (id: string) => {
    const { error } = await deleteUserStock(id);
    if (error) { alert('삭제 실패: ' + error.message); return; }
    setDeleteConfirm(null);
    loadData();
  };

  const handleAddWatch = async (data: any) => {
    const { error } = await addToWatchlist(data);
    if (error) {
      if (error.message === 'Stock already in watchlist') { alert('이미 관심종목에 있습니다.'); }
      else { alert('추가 실패: ' + error.message); }
      return;
    }
    setWatchModalOpen(false);
    loadData();
  };

  const handleDeleteWatch = async (stockCode: string) => {
    const { error } = await removeFromWatchlistByCode(stockCode);
    if (error) { alert('삭제 실패: ' + error.message); return; }
    setWatchDeleteConfirm(null);
    loadData();
  };

  const formatKRW = (n: number) => n.toLocaleString('ko-KR') + '원';

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-[#8b95a1]">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* 헤더 */}
      <div className="bg-white border-b border-[#e8e8e8] px-6 py-5">
        <h1 className="text-xl font-bold text-[#191f28]">📊 포트폴리오</h1>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

        {/* ─── 보유종목 섹션 ─── */}
        <div>
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-base font-bold text-[#191f28]">🧳 보유종목</h2>
            <button onClick={() => { setEditStock(null); setModalOpen(true); }}
              className="px-3 py-1.5 bg-[#3182f6] text-white text-sm rounded-xl hover:bg-[#1b64da] transition-colors">
              + 종목 추가
            </button>
          </div>

          {/* 요약 카드 */}
          {summary && summary.totalStocks > 0 && (
            <div className="bg-white rounded-2xl p-5 shadow-sm mb-3">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-xs text-[#8b95a1]">총 투자금</p>
                  <p className="text-lg font-bold text-[#191f28]">{formatKRW(summary.totalInvestment)}</p>
                </div>
                <div>
                  <p className="text-xs text-[#8b95a1]">수익률</p>
                  <p className={`text-lg font-bold ${summary.totalReturn >= 0 ? 'text-[#f04452]' : 'text-[#3182f6]'}`}>
                    {(summary.totalReturn >= 0 ? '+' : '') + summary.totalReturnPercent.toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-[#8b95a1]">보유 종목</p>
                  <p className="text-lg font-bold text-[#191f28]">{summary.totalStocks}개</p>
                </div>
              </div>
            </div>
          )}

          {stocks.length === 0 ? (
            <div className="bg-white rounded-2xl p-10 text-center shadow-sm">
              <div className="text-4xl mb-3">🧳</div>
              <p className="text-[#8b95a1] mb-4">아직 보유 종목이 없습니다</p>
              <button onClick={() => { setEditStock(null); setModalOpen(true); }}
                className="px-6 py-2.5 bg-[#3182f6] text-white rounded-xl text-sm hover:bg-[#1b64da]">
                첫 종목 추가하기
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {stocks.map((stock) => {
                const totalInvest = Number(stock.quantity) * Number(stock.avg_buy_price);
                return (
                  <div key={stock.id} className="bg-white rounded-2xl p-5 shadow-sm">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-bold text-[#191f28]">{stock.stock_name}</p>
                        <p className="text-xs text-[#8b95a1] mt-0.5">{stock.stock_code} · {stock.market}</p>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={() => { setEditStock(stock); setModalOpen(true); }}
                          className="text-xs text-[#3182f6] border border-[#3182f6] px-3 py-1 rounded-lg hover:bg-blue-50">수정</button>
                        {deleteConfirm === stock.id ? (
                          <div className="flex gap-1">
                            <button onClick={() => handleDelete(stock.id)} className="text-xs text-white bg-red-500 px-3 py-1 rounded-lg">확인</button>
                            <button onClick={() => setDeleteConfirm(null)} className="text-xs text-[#8b95a1] border px-3 py-1 rounded-lg">취소</button>
                          </div>
                        ) : (
                          <button onClick={() => setDeleteConfirm(stock.id)}
                            className="text-xs text-red-500 border border-red-300 px-3 py-1 rounded-lg hover:bg-red-50">삭제</button>
                        )}
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-[#8b95a1]">수량</p>
                        <p className="font-medium text-[#191f28]">{Number(stock.quantity)}주</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#8b95a1]">평균매수가</p>
                        <p className="font-medium text-[#191f28]">{formatKRW(Number(stock.avg_buy_price))}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#8b95a1]">총투자금</p>
                        <p className="font-medium text-[#191f28]">{formatKRW(totalInvest)}</p>
                      </div>
                    </div>
                    {stock.notes && <p className="text-xs text-[#8b95a1] mt-3 bg-[#f8f9fa] p-2 rounded-lg">{stock.notes}</p>}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ─── 관심종목 섹션 ─── */}
        <div>
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-base font-bold text-[#191f28]">⭐️ 관심종목</h2>
            <button onClick={() => setWatchModalOpen(true)}
              className="px-3 py-1.5 bg-[#f5a623] text-white text-sm rounded-xl hover:bg-[#e09400] transition-colors">
              + 관심 추가
            </button>
          </div>

          {watchlist.length === 0 ? (
            <div className="bg-white rounded-2xl p-10 text-center shadow-sm">
              <div className="text-4xl mb-3">⭐️</div>
              <p className="text-[#8b95a1] mb-4">아직 관심종목이 없습니다</p>
              <button onClick={() => setWatchModalOpen(true)}
                className="px-6 py-2.5 bg-[#f5a623] text-white rounded-xl text-sm hover:bg-[#e09400]">
                관심종목 추가하기
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {watchlist.map((item) => (
                <div key={item.id} className="bg-white rounded-2xl p-5 shadow-sm">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-bold text-[#191f28]">{item.stock_name}</p>
                        {item.alert_on_signals && (
                          <span className="text-xs bg-[#fff8ee] text-[#f5a623] px-2 py-0.5 rounded-full border border-[#f5a623]/30">
                            🔔 알림
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[#8b95a1] mt-0.5">{item.stock_code} · {item.market}</p>
                    </div>
                    <div className="flex gap-2">
                      {watchDeleteConfirm === item.stock_code ? (
                        <div className="flex gap-1">
                          <button onClick={() => handleDeleteWatch(item.stock_code)} className="text-xs text-white bg-red-500 px-3 py-1 rounded-lg">확인</button>
                          <button onClick={() => setWatchDeleteConfirm(null)} className="text-xs text-[#8b95a1] border px-3 py-1 rounded-lg">취소</button>
                        </div>
                      ) : (
                        <button onClick={() => setWatchDeleteConfirm(item.stock_code)}
                          className="text-xs text-red-500 border border-red-300 px-3 py-1 rounded-lg hover:bg-red-50">삭제</button>
                      )}
                    </div>
                  </div>
                  {item.alert_price_target && (
                    <div className="mt-2 text-xs text-[#8b95a1]">
                      목표가: {Number(item.alert_price_target).toLocaleString()}원 ({item.alert_price_type === 'above' ? '이상' : '이하'})
                    </div>
                  )}
                  {item.notes && <p className="text-xs text-[#8b95a1] mt-2 bg-[#f8f9fa] p-2 rounded-lg">{item.notes}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 보유종목 모달 */}
      <StockModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditStock(null); }}
        onSubmit={editStock ? handleEdit : handleAdd}
        editStock={editStock}
      />

      {/* 관심종목 모달 */}
      <WatchlistModal
        isOpen={watchModalOpen}
        onClose={() => setWatchModalOpen(false)}
        onSubmit={handleAddWatch}
      />
    </div>
  );
}
