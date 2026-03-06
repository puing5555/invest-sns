/**
 * 사용자 관심 종목(워치리스트) 관리 API
 * 목적: 관심종목 CRUD 및 가격 알림 설정
 */

import { supabase } from '@/lib/supabase';
import type { Database } from '@/types/supabase';

type UserWatchlist = Database['public']['Tables']['user_watchlist']['Row'];
type UserWatchlistInsert = Database['public']['Tables']['user_watchlist']['Insert'];
type UserWatchlistUpdate = Database['public']['Tables']['user_watchlist']['Update'];

// 가격 알림 근접 확인용
export interface WatchlistWithAlert extends UserWatchlist {
  current_price?: number;
  alert_triggered?: boolean;
  price_distance_percent?: number;
}

/**
 * 사용자의 모든 관심 종목 조회
 */
export async function getUserWatchlist(): Promise<{
  data: UserWatchlist[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_watchlist')
    .select('*')
    .eq('user_id', user.id)
    .order('added_at', { ascending: false });

  return { data, error };
}

/**
 * 특정 종목이 관심목록에 있는지 확인
 */
export async function isInWatchlist(stockCode: string): Promise<{
  data: boolean;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: false, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_watchlist')
    .select('id')
    .eq('user_id', user.id)
    .eq('stock_code', stockCode)
    .single();

  return { data: !!data, error: error?.code === 'PGRST116' ? null : error };
}

/**
 * 관심 종목 추가
 */
export async function addToWatchlist(watchlistData: {
  stock_code: string;
  stock_name: string;
  market: string;
  alert_on_signals?: boolean;
  alert_price_target?: number;
  alert_price_type?: 'above' | 'below';
  notes?: string;
}): Promise<{
  data: UserWatchlist | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  // 중복 체크
  const { data: existing } = await isInWatchlist(watchlistData.stock_code);
  if (existing) {
    return { data: null, error: new Error('Stock already in watchlist') };
  }

  const insertData: UserWatchlistInsert = {
    user_id: user.id,
    stock_code: watchlistData.stock_code,
    stock_name: watchlistData.stock_name,
    market: watchlistData.market,
    alert_on_signals: watchlistData.alert_on_signals ?? true,
    alert_price_target: watchlistData.alert_price_target,
    alert_price_type: watchlistData.alert_price_type,
    notes: watchlistData.notes || null,
  };

  const { data, error } = await supabase
    .from('user_watchlist')
    .insert([insertData])
    .select()
    .single();

  return { data, error };
}

/**
 * 관심 종목 정보 수정
 */
export async function updateWatchlistItem(
  itemId: string,
  updates: {
    alert_on_signals?: boolean;
    alert_price_target?: number;
    alert_price_type?: 'above' | 'below' | null;
    notes?: string;
  }
): Promise<{
  data: UserWatchlist | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_watchlist')
    .update(updates)
    .eq('id', itemId)
    .eq('user_id', user.id) // 보안: 자신의 관심종목만 수정 가능
    .select()
    .single();

  return { data, error };
}

/**
 * 종목 코드로 관심 종목 정보 수정
 */
export async function updateWatchlistByCode(
  stockCode: string,
  updates: {
    alert_on_signals?: boolean;
    alert_price_target?: number;
    alert_price_type?: 'above' | 'below' | null;
    notes?: string;
  }
): Promise<{
  data: UserWatchlist | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_watchlist')
    .update(updates)
    .eq('stock_code', stockCode)
    .eq('user_id', user.id)
    .select()
    .single();

  return { data, error };
}

/**
 * 관심 종목 삭제 (ID로)
 */
export async function removeFromWatchlist(itemId: string): Promise<{
  data: null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { error } = await supabase
    .from('user_watchlist')
    .delete()
    .eq('id', itemId)
    .eq('user_id', user.id); // 보안: 자신의 관심종목만 삭제 가능

  return { data: null, error };
}

/**
 * 관심 종목 삭제 (종목 코드로)
 */
export async function removeFromWatchlistByCode(stockCode: string): Promise<{
  data: null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { error } = await supabase
    .from('user_watchlist')
    .delete()
    .eq('stock_code', stockCode)
    .eq('user_id', user.id);

  return { data: null, error };
}

/**
 * 가격 알림 설정이 있는 관심 종목만 조회
 */
export async function getWatchlistWithPriceAlerts(): Promise<{
  data: UserWatchlist[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_watchlist')
    .select('*')
    .eq('user_id', user.id)
    .not('alert_price_target', 'is', null)
    .not('alert_price_type', 'is', null)
    .order('added_at', { ascending: false });

  return { data, error };
}

/**
 * 시그널 알림이 활성화된 관심 종목만 조회
 */
export async function getWatchlistWithSignalAlerts(): Promise<{
  data: UserWatchlist[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_watchlist')
    .select('*')
    .eq('user_id', user.id)
    .eq('alert_on_signals', true)
    .order('added_at', { ascending: false });

  return { data, error };
}

/**
 * 현재가와 함께 관심 종목 조회 및 알림 체크
 */
export async function getWatchlistWithPrices(
  currentPrices: Record<string, number>,
  alertThreshold: number = 5 // 목표가 대비 몇% 이내면 알림으로 간주할지
): Promise<{
  data: WatchlistWithAlert[] | null;
  error: any;
}> {
  const { data: watchlist, error } = await getUserWatchlist();
  
  if (error || !watchlist) {
    return { data: null, error };
  }

  const watchlistWithAlerts: WatchlistWithAlert[] = watchlist.map(item => {
    const currentPrice = currentPrices[item.stock_code];
    let alert_triggered = false;
    let price_distance_percent;

    if (currentPrice && item.alert_price_target && item.alert_price_type) {
      const targetPrice = Number(item.alert_price_target);
      price_distance_percent = ((currentPrice - targetPrice) / targetPrice) * 100;

      if (item.alert_price_type === 'above' && currentPrice >= targetPrice) {
        alert_triggered = true;
      } else if (item.alert_price_type === 'below' && currentPrice <= targetPrice) {
        alert_triggered = true;
      } else if (Math.abs(price_distance_percent) <= alertThreshold) {
        alert_triggered = true; // 목표가 근접
      }
    }

    return {
      ...item,
      current_price: currentPrice,
      alert_triggered,
      price_distance_percent,
    };
  });

  return { data: watchlistWithAlerts, error: null };
}

/**
 * 관심 종목을 포트폴리오로 이동 (매수 완료)
 */
export async function moveToPortfolio(
  stockCode: string,
  purchaseData: {
    quantity: number;
    purchase_price: number;
    notes?: string;
  }
): Promise<{
  data: { removed_from_watchlist: boolean; added_to_portfolio: boolean };
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { 
      data: { removed_from_watchlist: false, added_to_portfolio: false }, 
      error: new Error('User not authenticated') 
    };
  }

  // 관심종목에서 해당 종목 정보 조회
  const { data: watchlistItem } = await supabase
    .from('user_watchlist')
    .select('*')
    .eq('user_id', user.id)
    .eq('stock_code', stockCode)
    .single();

  if (!watchlistItem) {
    return { 
      data: { removed_from_watchlist: false, added_to_portfolio: false },
      error: new Error('Stock not found in watchlist') 
    };
  }

  try {
    // 1. 포트폴리오에 추가
    const { addUserStock } = await import('./user-stocks');
    
    const { error: addError } = await addUserStock({
      stock_code: watchlistItem.stock_code,
      stock_name: watchlistItem.stock_name,
      market: watchlistItem.market,
      quantity: purchaseData.quantity,
      avg_buy_price: purchaseData.purchase_price,
      notes: purchaseData.notes || `관심종목에서 이동: ${watchlistItem.notes || ''}`,
    });

    if (addError) {
      return { 
        data: { removed_from_watchlist: false, added_to_portfolio: false },
        error: addError 
      };
    }

    // 2. 관심종목에서 제거
    const { error: removeError } = await removeFromWatchlistByCode(stockCode);

    return {
      data: { 
        removed_from_watchlist: !removeError, 
        added_to_portfolio: true 
      },
      error: removeError
    };

  } catch (error) {
    return { 
      data: { removed_from_watchlist: false, added_to_portfolio: false },
      error 
    };
  }
}

/**
 * 시장별 관심종목 통계
 */
export async function getWatchlistByMarket(): Promise<{
  data: Record<string, number> | null;
  error: any;
}> {
  const { data: watchlist, error } = await getUserWatchlist();
  
  if (error || !watchlist) {
    return { data: null, error };
  }

  const marketStats = watchlist.reduce((acc, item) => {
    acc[item.market] = (acc[item.market] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return { data: marketStats, error: null };
}

/**
 * 관심 종목 검색 (이름/코드로)
 */
export async function searchWatchlist(query: string): Promise<{
  data: UserWatchlist[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_watchlist')
    .select('*')
    .eq('user_id', user.id)
    .or(`stock_code.ilike.%${query}%,stock_name.ilike.%${query}%`)
    .order('added_at', { ascending: false });

  return { data, error };
}

/**
 * 관심 종목 일괄 추가 (CSV 파싱 등에 활용)
 */
export async function bulkAddToWatchlist(
  watchlistItems: Array<{
    stock_code: string;
    stock_name: string;
    market: string;
    notes?: string;
  }>
): Promise<{
  data: { success_count: number; error_count: number; errors: string[] };
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { 
      data: { success_count: 0, error_count: 0, errors: [] },
      error: new Error('User not authenticated') 
    };
  }

  const results = { success_count: 0, error_count: 0, errors: [] };

  for (const item of watchlistItems) {
    const { error } = await addToWatchlist(item);
    
    if (error) {
      results.error_count++;
      results.errors.push(`${item.stock_code}: ${error.message}`);
    } else {
      results.success_count++;
    }
  }

  return { data: results, error: null };
}