'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import {
  getUserWatchlist,
  addToWatchlist,
  updateWatchlistItem,
  removeFromWatchlist,
} from '@/lib/api/user-watchlist';
import type { Database } from '@/types/supabase';

type UserWatchlist = Database['public']['Tables']['user_watchlist']['Row'];

function AddWatchlistModal({
  isOpen,
  onClose,
  onSubmit,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { stock_code: string; stock_name: string; market: string; alert_on_signals?: boolean; alert_price_target?: number; alert_price_type?: 'above' | 'below'; notes?: string }) => void;
}) {
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [market, setMarket] = useState('KOSPI');
  const [alertSignals, setAlertSignals] = useState(true);
  const [targetPrice, setTargetPrice] = useState('');
  const [priceType, setPriceType] = useState<'above' | 'below'>('above');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (isOpen) { setCode(''); setName(''); setMarket('KOSPI'); setAlertSignals(true); setTargetPrice(''); setPriceType('above'); setNotes(''); }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-lg font-bold text-[#191f28]">관심종목 추가</h2>
          <button onClick={onClose} className="text-[#8b95a1] text-xl">✕</button>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목코드</label>
              <input value={code} onChange={e => setCode(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="005930" />
            </div>
            <div>
              <label className="text-xs text-[#8b95a1] mb-1 block">종목명</label>
              <input value={name} onChange={e => setName(e.target.value)}
                className="w-full px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
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
          <div className="flex items-center justify-between">
            <label className="text-sm text-[#191f28]">시그널 알림 받기</label>
            <button onClick={() => setAlertSignals(!alertSignals)}
              className={`w-12 h-6 rounded-full transition-colors ${alertSignals ? 'bg-[#3182f6]' : 'bg-[#e8e8e8]'}`}>
              <div className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${alertSignals ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>
          <div>
            <label className="text-xs text-[#8b95a1] mb-1 block">목표가 (선택)</label>
            <div className="flex gap-2">
              <input type="number" value={targetPrice} onChange={e => setTargetPrice(e.target.value)}
                className="flex-1 px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6]"
                placeholder="목표가 입력" />
              <select value={priceType} onChange={e => setPriceType(e.target.value as 'above' | 'below')}
                className="px-3 py-2.5 border border-[#e8e8e8] rounded-xl text-sm">
                <option value="above">이상</option>
                <option value="below">이하</option>
              </select>
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
              if (!code || !name) return;
              onSubmit({
                stock_code: code, stock_name: name, market,
                alert_on_signals: alertSignals,
                alert_price_target: targetPrice ? Number(targetPrice) : undefined,
                alert_price_type: targetPrice ? priceType : undefined,
                notes: notes || undefined,
              });
            }}
            className="w-full py-3 bg-[#3182f6] text-white rounded-xl font-medium hover:bg-[#1b64da] transition-colors">
            추가하기
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MyWatchlistPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [watchlist, setWatchlist] = useState<UserWatchlist[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user) { router.push('/login'); return; }
    loadData();
  }, [user, authLoading]);

  const loadData = async () => {
    setLoading(true);
    const { data } = await getUserWatchlist();
    if (data) setWatchlist(data);
    setLoading(false);
  };

  const handleAdd = async (data: any) => {
    const { error } = await addToWatchlist(data);
    if (error) { alert('추가 실패: ' + error.message); return; }
    setModalOpen(false);
    loadData();
  };

  const handleToggleAlert = async (item: UserWatchlist) => {
    await updateWatchlistItem(item.id, { alert_on_signals: !item.alert_on_signals });
    loadData();
  };

  const handleDelete = async (id: string) => {
    const { error } = await removeFromWatchlist(id);
    if (error) { alert('삭제 실패: ' + error.message); return; }
    setDeleteConfirm(null);
    loadData();
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-[#8b95a1]">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      <div className="bg-white border-b border-[#e8e8e8] px-6 py-5">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold text-[#191f28]">👀 관심 종목</h1>
          <button onClick={() => setModalOpen(true)}
            className="px-4 py-2 bg-[#3182f6] text-white text-sm rounded-xl hover:bg-[#1b64da] transition-colors">
            + 종목 추가
          </button>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        {watchlist.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 text-center shadow-sm">
            <div className="text-4xl mb-3">👀</div>
            <p className="text-[#8b95a1] mb-4">관심 종목이 없습니다</p>
            <button onClick={() => setModalOpen(true)}
              className="px-6 py-2.5 bg-[#3182f6] text-white rounded-xl text-sm hover:bg-[#1b64da]">
              관심종목 추가하기
            </button>
          </div>
        ) : (
          watchlist.map((item) => (
            <div key={item.id} className="bg-white rounded-2xl p-5 shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-bold text-[#191f28]">{item.stock_name}</p>
                  <p className="text-xs text-[#8b95a1] mt-0.5">{item.stock_code} · {item.market}</p>
                </div>
                <div className="flex items-center gap-3">
                  {/* 시그널 알림 토글 */}
                  <button onClick={() => handleToggleAlert(item)}
                    className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs transition-colors ${item.alert_on_signals ? 'bg-blue-50 text-[#3182f6]' : 'bg-gray-100 text-[#8b95a1]'}`}>
                    {item.alert_on_signals ? '🔔 알림 ON' : '🔕 알림 OFF'}
                  </button>
                  {deleteConfirm === item.id ? (
                    <div className="flex gap-1">
                      <button onClick={() => handleDelete(item.id)} className="text-xs text-white bg-red-500 px-3 py-1 rounded-lg">확인</button>
                      <button onClick={() => setDeleteConfirm(null)} className="text-xs text-[#8b95a1] border px-3 py-1 rounded-lg">취소</button>
                    </div>
                  ) : (
                    <button onClick={() => setDeleteConfirm(item.id)}
                      className="text-xs text-red-500 border border-red-300 px-3 py-1 rounded-lg hover:bg-red-50">삭제</button>
                  )}
                </div>
              </div>
              {/* 목표가 & 메모 */}
              {(item.alert_price_target || item.notes) && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.alert_price_target && (
                    <span className="text-xs bg-amber-50 text-amber-700 px-2 py-1 rounded-lg">
                      🎯 목표가 {Number(item.alert_price_target).toLocaleString()}원 {item.alert_price_type === 'above' ? '이상' : '이하'}
                    </span>
                  )}
                  {item.notes && (
                    <span className="text-xs bg-[#f8f9fa] text-[#8b95a1] px-2 py-1 rounded-lg">{item.notes}</span>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <AddWatchlistModal isOpen={modalOpen} onClose={() => setModalOpen(false)} onSubmit={handleAdd} />
    </div>
  );
}
