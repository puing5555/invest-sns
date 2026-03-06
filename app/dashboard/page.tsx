'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUserStocks, getPortfolioSummary, type PortfolioSummary, type UserStockWithPrice } from '@/lib/api/user-stocks';
import { getUserWatchlist } from '@/lib/api/user-watchlist';
import { getUnreadNotifications, getNotificationStats } from '@/lib/api/user-notifications';
import type { Database } from '@/types/supabase';

type UserStock = Database['public']['Tables']['user_stocks']['Row'];
type UserWatchlist = Database['public']['Tables']['user_watchlist']['Row'];
type UserNotification = Database['public']['Tables']['user_notifications']['Row'];

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [stocks, setStocks] = useState<UserStock[]>([]);
  const [watchlist, setWatchlist] = useState<UserWatchlist[]>([]);
  const [notifications, setNotifications] = useState<UserNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push('/login');
      return;
    }
    loadDashboard();
  }, [user, authLoading]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [summaryRes, stocksRes, watchlistRes, notifRes, statsRes] = await Promise.all([
        getPortfolioSummary(),
        getUserStocks(),
        getUserWatchlist(),
        getUnreadNotifications(),
        getNotificationStats(),
      ]);
      if (summaryRes.data) setSummary(summaryRes.data);
      if (stocksRes.data) setStocks(stocksRes.data);
      if (watchlistRes.data) setWatchlist(watchlistRes.data);
      if (notifRes.data) setNotifications(notifRes.data.slice(0, 5));
      if (statsRes.data) setUnreadCount(statsRes.data.unread);
    } catch (e) {
      console.error('Dashboard load error:', e);
    }
    setLoading(false);
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-3">📊</div>
          <div className="text-[#8b95a1]">대시보드 로딩 중...</div>
        </div>
      </div>
    );
  }

  const formatKRW = (n: number) => n.toLocaleString('ko-KR') + '원';
  const formatPercent = (n: number) => (n >= 0 ? '+' : '') + n.toFixed(2) + '%';

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-6 py-5">
        <h1 className="text-xl font-bold text-[#191f28]">📊 대시보드</h1>
        <p className="text-sm text-[#8b95a1] mt-1">
          {user?.email} 님의 포트폴리오
        </p>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        {/* 포트폴리오 요약 카드 */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <h2 className="text-sm font-medium text-[#8b95a1] mb-4">포트폴리오 요약</h2>
          {summary ? (
            <div>
              <div className="mb-4">
                <p className="text-sm text-[#8b95a1]">총 투자금</p>
                <p className="text-2xl font-bold text-[#191f28]">{formatKRW(summary.totalInvestment)}</p>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-[#8b95a1]">총 평가금</p>
                  <p className="text-lg font-bold text-[#191f28]">{formatKRW(summary.totalValue)}</p>
                </div>
                <div>
                  <p className="text-xs text-[#8b95a1]">수익률</p>
                  <p className={`text-lg font-bold ${summary.totalReturn >= 0 ? 'text-[#f04452]' : 'text-[#3182f6]'}`}>
                    {formatPercent(summary.totalReturnPercent)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-[#8b95a1]">보유 종목</p>
                  <p className="text-lg font-bold text-[#191f28]">{summary.totalStocks}개</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-[#8b95a1]">
              <p>아직 보유 종목이 없습니다</p>
              <Link href="/my-portfolio" className="text-[#3182f6] text-sm mt-2 inline-block">
                종목 추가하기 →
              </Link>
            </div>
          )}
        </div>

        {/* 보유 종목 */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-medium text-[#8b95a1]">보유 종목</h2>
            <Link href="/my-portfolio" className="text-xs text-[#3182f6]">전체보기 →</Link>
          </div>
          {stocks.length > 0 ? (
            <div className="space-y-3">
              {stocks.slice(0, 5).map((stock) => {
                const totalInvest = Number(stock.quantity) * Number(stock.avg_buy_price);
                return (
                  <div key={stock.id} className="flex justify-between items-center py-2 border-b border-[#f0f0f0] last:border-0">
                    <div>
                      <p className="font-medium text-[#191f28]">{stock.stock_name}</p>
                      <p className="text-xs text-[#8b95a1]">{stock.stock_code} · {stock.market}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-[#191f28]">{Number(stock.quantity)}주</p>
                      <p className="text-xs text-[#8b95a1]">{formatKRW(totalInvest)}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-center py-4 text-[#8b95a1] text-sm">보유 종목이 없습니다</p>
          )}
        </div>

        {/* 관심 종목 */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-medium text-[#8b95a1]">관심 종목</h2>
            <Link href="/my-watchlist" className="text-xs text-[#3182f6]">전체보기 →</Link>
          </div>
          {watchlist.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {watchlist.slice(0, 8).map((item) => (
                <span key={item.id} className="px-3 py-1.5 bg-[#f4f4f4] rounded-full text-sm text-[#191f28]">
                  {item.stock_name}
                  {item.alert_on_signals && <span className="ml-1 text-xs">🔔</span>}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-center py-4 text-[#8b95a1] text-sm">관심 종목이 없습니다</p>
          )}
        </div>

        {/* 최근 알림 */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-medium text-[#8b95a1]">
              최근 알림 {unreadCount > 0 && <span className="bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full ml-1">{unreadCount}</span>}
            </h2>
            <Link href="/notifications" className="text-xs text-[#3182f6]">전체보기 →</Link>
          </div>
          {notifications.length > 0 ? (
            <div className="space-y-3">
              {notifications.map((notif) => (
                <div key={notif.id} className={`py-2 border-b border-[#f0f0f0] last:border-0 ${!notif.is_read ? 'bg-blue-50 -mx-2 px-2 rounded-lg' : ''}`}>
                  <p className="text-sm font-medium text-[#191f28]">{notif.title}</p>
                  <p className="text-xs text-[#8b95a1] mt-0.5">{notif.message}</p>
                  <p className="text-xs text-[#b0b8c1] mt-1">{new Date(notif.created_at).toLocaleString('ko-KR')}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center py-4 text-[#8b95a1] text-sm">알림이 없습니다</p>
          )}
        </div>
      </div>
    </div>
  );
}
