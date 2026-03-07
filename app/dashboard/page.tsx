'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getUserStocks } from '@/lib/api/user-stocks';
import { getUserWatchlist } from '@/lib/api/user-watchlist';
import { getUnreadNotifications, getNotificationStats } from '@/lib/api/user-notifications';
import type { Database } from '@/types/supabase';

type UserStock = Database['public']['Tables']['user_stocks']['Row'];
type UserWatchlist = Database['public']['Tables']['user_watchlist']['Row'];
type UserNotification = Database['public']['Tables']['user_notifications']['Row'];

// Mock 시황 데이터 (추후 API 연동)
const MARKET_DATA = [
  { flag: '🇺🇸', items: ['S&P 5,234 +0.3%', '나스닥 16,832 +0.5%', '다우 39,420 +0.1%'] },
  { flag: '🇰🇷', items: ['코스피 2,578 -0.2%', '코스닥 752 +0.4%'] },
  { flag: '₿', items: ['BTC $85,420 +1.2%', '금 $2,914 +0.3%', '원달러 1,455 +0.1%'] },
];

type TabKey = '지금' | '뉴스' | 'LIVE' | '시장';

interface VideoCard {
  id: string;
  channel_name: string;
  title: string;
  upload_date: string;
  long_summary: string | null;
  youtube_url: string;
  mentioned_stocks: string[] | null;
  channel_id: string;
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabKey>('지금');
  const [stocks, setStocks] = useState<UserStock[]>([]);
  const [watchlist, setWatchlist] = useState<UserWatchlist[]>([]);
  const [notifications, setNotifications] = useState<UserNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [videos, setVideos] = useState<VideoCard[]>([]);
  const [videoFilter, setVideoFilter] = useState<string>('내 종목');
  const [channelFilter, setChannelFilter] = useState<string[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string>('전체');
  const [videoPage, setVideoPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [newsFilter, setNewsFilter] = useState<'전체' | '공시' | '내종목'>('전체');

  useEffect(() => {
    if (authLoading) return;
    if (!user) { router.push('/login'); return; }
    loadDashboard();
  }, [user, authLoading]);

  useEffect(() => {
    if (activeTab !== 'LIVE') return;
    const handleScroll = () => {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 300) {
        loadMoreVideos();
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [activeTab, videoPage, hasMore, loadingMore]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [stocksRes, watchlistRes, notifRes, statsRes] = await Promise.all([
        getUserStocks(),
        getUserWatchlist(),
        getUnreadNotifications(),
        getNotificationStats(),
      ]);
      if (stocksRes.data) setStocks(stocksRes.data);
      if (watchlistRes.data) setWatchlist(watchlistRes.data);
      if (notifRes.data) setNotifications(notifRes.data.slice(0, 5));
      if (statsRes.data) setUnreadCount(statsRes.data.unread);
      // videos 테이블 조회 (없으면 빈 배열)
      await loadVideos();
    } catch (e) {
      console.error('Dashboard load error:', e);
    }
    setLoading(false);
  };

  const loadVideos = async (page = 1, append = false) => {
    try {
      const limit = 20;
      const offset = (page - 1) * limit;
      const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/videos?select=*&order=upload_date.desc&limit=${limit}&offset=${offset}`;
      const res = await fetch(url, {
        headers: {
          apikey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          if (append) {
            setVideos(prev => [...prev, ...data]);
          } else {
            setVideos(data);
          }
          setHasMore(data.length === limit);
        }
      }
    } catch (e) {
      // 테이블 없으면 무시
    }
  };

  const loadMoreVideos = async () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    const nextPage = videoPage + 1;
    await loadVideos(nextPage, true);
    setVideoPage(nextPage);
    setLoadingMore(false);
  };

  const toggleExpand = (id: string) => {
    setExpandedCards(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const formatKRW = (n: number) => n.toLocaleString('ko-KR') + '원';
  const formatPercent = (n: number) => (n >= 0 ? '+' : '') + n.toFixed(2) + '%';
  const formatTime = (iso: string) => {
    try {
      const d = new Date(iso);
      return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
    } catch { return iso; }
  };

  const CATEGORY_LABELS: Record<string, string> = {
    'stock_analysis': '종목분석',
    'market_overview': '시황',
    'education': '교육',
    'macro': '매크로',
    'general': '일반',
  };

  const userStockNames = stocks.map(s => s.stock_name);
  const userWatchlistNames = watchlist.map(w => w.stock_name);
  const userStocks = new Set([...userStockNames, ...userWatchlistNames]);

  const filteredVideos = videos.filter(video => {
    // 내 종목 필터
    if (videoFilter === '내 종목') {
      if (!video.mentioned_stocks || video.mentioned_stocks.length === 0) return false;
      const hasMyStock = video.mentioned_stocks.some(s => userStocks.has(s));
      if (!hasMyStock) return false;
    }
    // 채널 필터
    if (channelFilter.length > 0 && !channelFilter.includes(video.channel_name)) return false;
    // 카테고리 필터
    if (categoryFilter !== '전체') {
      const catMap: Record<string, string> = {
        '종목분석': 'stock_analysis',
        '시황': 'market_overview',
        '교육': 'education',
        '매크로': 'macro',
      };
      if ((video as any).category !== catMap[categoryFilter]) return false;
    }
    return true;
  });

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

  const TABS: TabKey[] = ['지금', '뉴스', 'LIVE', '시장'];

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-6 py-5">
        <h1 className="text-xl font-bold text-[#191f28]">📊 대시보드</h1>
        <p className="text-sm text-[#8b95a1] mt-1">{user?.email} 님의 포트폴리오</p>
      </div>

      {/* 탭 네비게이션 */}
      <div className="bg-white border-b border-[#e8e8e8] sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4">
          <div className="flex">
            {TABS.map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-5 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-[#3182f6] text-[#3182f6]'
                    : 'border-transparent text-[#8b95a1] hover:text-[#191f28]'
                }`}
              >
                {tab === 'LIVE' ? '🔴 LIVE' : tab}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

        {/* ===== 탭1: 지금 ===== */}
        {activeTab === '지금' && (
          <>
            {/* ① 보유종목 */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-sm font-medium text-[#8b95a1]">보유종목</h2>
                <Link href="/my-portfolio" className="text-xs text-[#3182f6]">전체보기 →</Link>
              </div>
              {stocks.length > 0 ? (
                <div className="space-y-3">
                  {stocks.slice(0, 4).map((stock) => {
                    const returnPct = (stock as any).return_pct ?? 0;
                    const returnAmt = (stock as any).return_amount ?? 0;
                    return (
                      <div key={stock.id} className="flex justify-between items-center py-2 border-b border-[#f0f0f0] last:border-0">
                        <div>
                          <p className="font-medium text-[#191f28]">{stock.stock_name}</p>
                          <p className="text-xs text-[#8b95a1]">{stock.stock_code} · {stock.market}</p>
                        </div>
                        <div className="text-right">
                          <p className={`font-semibold ${returnPct >= 0 ? 'text-[#f04452]' : 'text-[#3182f6]'}`}>
                            {formatPercent(returnPct)}
                          </p>
                          <p className={`text-xs ${returnAmt >= 0 ? 'text-[#f04452]' : 'text-[#3182f6]'}`}>
                            {returnAmt >= 0 ? '+' : ''}{formatKRW(returnAmt)}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-[#8b95a1]">
                  <p>보유 종목이 없습니다</p>
                  <Link href="/my-portfolio" className="text-[#3182f6] text-sm mt-2 inline-block">종목 추가하기 →</Link>
                </div>
              )}
            </div>

            {/* ② 관심종목 */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-sm font-medium text-[#8b95a1]">관심종목</h2>
                <Link href="/my-watchlist" className="text-xs text-[#3182f6]">전체보기 →</Link>
              </div>
              {watchlist.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {watchlist.slice(0, 5).map((item) => (
                    <span key={item.id} className="px-3 py-1.5 bg-[#f4f4f4] rounded-full text-sm text-[#191f28]">
                      {item.stock_name}
                      {item.alert_on_signals && <span className="ml-1 text-xs">🔔</span>}
                    </span>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4 text-[#8b95a1] text-sm">
                  <p>관심종목이 없습니다</p>
                  <Link href="/my-watchlist" className="text-[#3182f6] text-sm mt-2 inline-block">관심종목 추가 →</Link>
                </div>
              )}
            </div>

            {/* ③ 시황 3줄 */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h2 className="text-sm font-medium text-[#8b95a1] mb-4">시황</h2>
              <div className="space-y-3">
                {MARKET_DATA.map((group) => (
                  <div key={group.flag} className="flex items-start gap-3">
                    <span className="text-lg">{group.flag}</span>
                    <div className="flex flex-wrap gap-x-4 gap-y-1">
                      {group.items.map((item) => {
                        const isPositive = item.includes('+');
                        const isNegative = item.includes('-') && !item.includes('원달러');
                        return (
                          <span key={item} className={`text-sm ${isPositive ? 'text-[#f04452]' : isNegative ? 'text-[#3182f6]' : 'text-[#191f28]'}`}>
                            {item}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-xs text-[#b0b8c1] mt-3">※ 시황 데이터 추후 API 연동 예정</p>
            </div>

            {/* ④ 오늘 알림 */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-sm font-medium text-[#8b95a1]">
                  오늘 알림 {unreadCount > 0 && (
                    <span className="bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full ml-1">{unreadCount}</span>
                  )}
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
          </>
        )}

        {/* ===== 탭2: 뉴스 ===== */}
        {activeTab === '뉴스' && (
          <>
            {/* 서브 필터 */}
            <div className="flex gap-2">
              {(['전체', '공시', '내종목'] as const).map(f => (
                <button
                  key={f}
                  onClick={() => setNewsFilter(f)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    newsFilter === f ? 'bg-[#3182f6] text-white' : 'bg-white text-[#8b95a1] border border-[#e8e8e8]'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>

            {/* 공시 AI분석 카드 placeholder */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h2 className="text-sm font-medium text-[#8b95a1] mb-4">공시 AI 분석</h2>
              <div className="text-center py-8 text-[#8b95a1]">
                <div className="text-3xl mb-2">📋</div>
                <p className="text-sm">공시 데이터 로딩 중...</p>
                <Link href="/explore" className="text-[#3182f6] text-sm mt-2 inline-block">공시 탭에서 보기 →</Link>
              </div>
            </div>

            {/* 뉴스 헤드라인 placeholder */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h2 className="text-sm font-medium text-[#8b95a1] mb-4">뉴스 헤드라인</h2>
              <div className="text-center py-8 text-[#8b95a1]">
                <div className="text-3xl mb-2">📰</div>
                <p className="text-sm">뉴스 API 연동 예정</p>
              </div>
            </div>
          </>
        )}

        {/* ===== 탭3: LIVE ===== */}
        {activeTab === 'LIVE' && (
          <>
            {/* 필터 바 */}
            <div className="space-y-2">
              {/* 1행: 주요 필터 */}
              <div className="flex gap-2 overflow-x-auto pb-1">
                {['내 종목', '전체'].map(f => (
                  <button
                    key={f}
                    onClick={() => {
                      setVideoFilter(f);
                      setCategoryFilter('전체');
                      setChannelFilter([]);
                    }}
                    className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                      videoFilter === f
                        ? 'bg-[#3182f6] text-white'
                        : 'bg-white text-[#8b95a1] border border-[#e8e8e8]'
                    }`}
                  >
                    {f === '내 종목' ? '⭐ 내 종목' : f}
                  </button>
                ))}

                {/* 채널별 드롭다운 */}
                <div className="relative flex-shrink-0">
                  <select
                    value={channelFilter[0] || ''}
                    onChange={e => {
                      const val = e.target.value;
                      setChannelFilter(val ? [val] : []);
                      setVideoFilter('전체');
                    }}
                    className={`px-4 py-2 rounded-full text-sm font-medium border transition-colors appearance-none cursor-pointer ${
                      channelFilter.length > 0
                        ? 'bg-[#3182f6] text-white border-[#3182f6]'
                        : 'bg-white text-[#8b95a1] border-[#e8e8e8]'
                    }`}
                  >
                    <option value="">채널별 ▼</option>
                    {Array.from(new Set(videos.map(v => v.channel_name))).map(ch => (
                      <option key={ch} value={ch}>{ch}</option>
                    ))}
                  </select>
                </div>

                {/* 카테고리 드롭다운 */}
                <div className="relative flex-shrink-0">
                  <select
                    value={categoryFilter}
                    onChange={e => {
                      setCategoryFilter(e.target.value);
                      if (e.target.value !== '전체') setVideoFilter('전체');
                    }}
                    className={`px-4 py-2 rounded-full text-sm font-medium border transition-colors appearance-none cursor-pointer ${
                      categoryFilter !== '전체'
                        ? 'bg-[#3182f6] text-white border-[#3182f6]'
                        : 'bg-white text-[#8b95a1] border-[#e8e8e8]'
                    }`}
                  >
                    <option value="전체">카테고리 ▼</option>
                    <option value="종목분석">종목분석</option>
                    <option value="시황">시황</option>
                    <option value="교육">교육</option>
                    <option value="매크로">매크로</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 영상 카드 목록 */}
            {filteredVideos.length > 0 ? (
              <div className="space-y-4">
                {filteredVideos.map(video => {
                  const isExpanded = expandedCards.has(video.id);
                  const summary = video.long_summary || '';
                  const SHORT_LIMIT = 120;
                  const needsToggle = summary.length > SHORT_LIMIT;
                  const category = (video as any).category;
                  return (
                    <div key={video.id} className="bg-white rounded-2xl p-6 shadow-sm">
                      {/* 채널명 + 시간 + 카테고리 */}
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-[#f4f4f4] rounded-full flex items-center justify-center text-sm font-bold text-[#3182f6]">
                            {video.channel_name[0]}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-[#191f28]">{video.channel_name}</p>
                            <p className="text-xs text-[#b0b8c1]">{formatTime(video.upload_date)}</p>
                          </div>
                        </div>
                        {category && category !== 'general' && (
                          <span className="px-2 py-0.5 bg-[#f4f4f4] rounded text-xs text-[#8b95a1]">
                            {CATEGORY_LABELS[category] || category}
                          </span>
                        )}
                      </div>
                      {/* 제목 */}
                      <h3 className="font-bold text-[#191f28] mb-2 leading-snug">{video.title}</h3>
                      {/* 요약 */}
                      {summary && (
                        <div className="mb-3">
                          <p className="text-sm text-[#4e5968] leading-relaxed">
                            {isExpanded || !needsToggle ? summary : summary.slice(0, SHORT_LIMIT) + '...'}
                          </p>
                          {needsToggle && (
                            <button onClick={() => toggleExpand(video.id)} className="text-xs text-[#3182f6] mt-1">
                              {isExpanded ? '접기' : '더보기'}
                            </button>
                          )}
                        </div>
                      )}
                      {/* 언급 종목 */}
                      {video.mentioned_stocks && video.mentioned_stocks.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mb-3">
                          <span className="text-xs text-[#8b95a1]">📌 언급:</span>
                          {video.mentioned_stocks.slice(0, 5).map(s => (
                            <span
                              key={s}
                              className={`px-2 py-0.5 rounded text-xs ${
                                userStocks.has(s) ? 'bg-[#fff3cd] text-[#856404] font-medium' : 'bg-[#f4f4f4] text-[#191f28]'
                              }`}
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      )}
                      {/* 영상 보기 */}
                      <a href={video.youtube_url} target="_blank" rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-[#3182f6] font-medium">
                        🎬 영상 보기 →
                      </a>
                    </div>
                  );
                })}

                {/* 무한 스크롤 로딩 */}
                {loadingMore && (
                  <div className="text-center py-4 text-[#8b95a1] text-sm">
                    <div className="inline-block animate-spin mr-2">⟳</div>로딩 중...
                  </div>
                )}
                {!hasMore && filteredVideos.length > 0 && (
                  <p className="text-center py-4 text-[#b0b8c1] text-xs">모든 영상을 불러왔습니다</p>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-2xl p-12 shadow-sm text-center">
                <div className="text-4xl mb-3">🎬</div>
                {videoFilter === '내 종목' && userStocks.size === 0 ? (
                  <>
                    <p className="text-[#8b95a1] font-medium">보유/관심 종목을 추가하면</p>
                    <p className="text-[#8b95a1] font-medium">관련 영상이 표시됩니다</p>
                    <Link href="/my-portfolio" className="text-[#3182f6] text-sm mt-3 inline-block">종목 추가하기 →</Link>
                  </>
                ) : (
                  <>
                    <p className="text-[#8b95a1] font-medium">영상 데이터 준비 중</p>
                    <p className="text-xs text-[#b0b8c1] mt-2">추적 채널의 영상이 수집되면 여기에 표시됩니다</p>
                  </>
                )}
              </div>
            )}
          </>
        )}

        {/* ===== 탭4: 시장 ===== */}
        {activeTab === '시장' && (
          <div className="bg-white rounded-2xl p-12 shadow-sm text-center">
            <div className="text-4xl mb-3">📈</div>
            <p className="text-[#191f28] font-medium">준비 중입니다</p>
            <p className="text-xs text-[#b0b8c1] mt-2">Fear & Greed 게이지, 섹터별 등락, 외국인/기관 수급, 유튜버 전체 컨센서스</p>
          </div>
        )}

      </div>
    </div>
  );
}
