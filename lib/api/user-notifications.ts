/**
 * 사용자 알림 시스템 관리 API
 * 목적: 알림 생성, 조회, 설정 관리
 */

import { supabase } from '@/lib/supabase';
import type { Database } from '@/types/supabase';

type UserNotification = Database['public']['Tables']['user_notifications']['Row'];
type UserNotificationInsert = Database['public']['Tables']['user_notifications']['Insert'];
type UserNotificationSettings = Database['public']['Tables']['user_notification_settings']['Row'];
type UserNotificationSettingsUpdate = Database['public']['Tables']['user_notification_settings']['Update'];

// 알림 생성용 타입
export interface CreateNotificationData {
  type: 'signal' | 'price_target' | 'analyst_report' | 'market_summary' | 'ai_insight' | 'portfolio_alert';
  title: string;
  message: string;
  stock_code?: string;
  metadata?: Record<string, any>;
}

// 알림 통계
export interface NotificationStats {
  total: number;
  unread: number;
  today: number;
  by_type: Record<string, number>;
}

/**
 * 사용자의 모든 알림 조회
 */
export async function getUserNotifications(
  limit: number = 50,
  offset: number = 0
): Promise<{
  data: UserNotification[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notifications')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1);

  return { data, error };
}

/**
 * 읽지 않은 알림만 조회
 */
export async function getUnreadNotifications(): Promise<{
  data: UserNotification[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notifications')
    .select('*')
    .eq('user_id', user.id)
    .eq('is_read', false)
    .order('created_at', { ascending: false });

  return { data, error };
}

/**
 * 특정 종목 관련 알림 조회
 */
export async function getNotificationsByStock(
  stockCode: string,
  limit: number = 20
): Promise<{
  data: UserNotification[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notifications')
    .select('*')
    .eq('user_id', user.id)
    .eq('stock_code', stockCode)
    .order('created_at', { ascending: false })
    .limit(limit);

  return { data, error };
}

/**
 * 특정 타입의 알림만 조회
 */
export async function getNotificationsByType(
  type: string,
  limit: number = 20
): Promise<{
  data: UserNotification[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notifications')
    .select('*')
    .eq('user_id', user.id)
    .eq('type', type)
    .order('created_at', { ascending: false })
    .limit(limit);

  return { data, error };
}

/**
 * 새 알림 생성
 */
export async function createNotification(
  notificationData: CreateNotificationData
): Promise<{
  data: UserNotification | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  // 사용자 알림 설정 확인
  const { data: settings } = await getUserNotificationSettings();
  if (settings && !settings.enabled) {
    return { data: null, error: new Error('Notifications disabled for user') };
  }

  // 타입별 설정 확인
  if (settings && !isNotificationTypeEnabled(settings, notificationData.type)) {
    return { data: null, error: new Error(`${notificationData.type} notifications disabled`) };
  }

  const insertData: UserNotificationInsert = {
    user_id: user.id,
    type: notificationData.type,
    title: notificationData.title,
    message: notificationData.message,
    stock_code: notificationData.stock_code || null,
    metadata: notificationData.metadata ? JSON.parse(JSON.stringify(notificationData.metadata)) : {},
  };

  const { data, error } = await supabase
    .from('user_notifications')
    .insert([insertData])
    .select()
    .single();

  return { data, error };
}

/**
 * 알림을 읽음으로 표시
 */
export async function markNotificationAsRead(notificationId: string): Promise<{
  data: UserNotification | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notifications')
    .update({ 
      is_read: true, 
      read_at: new Date().toISOString() 
    })
    .eq('id', notificationId)
    .eq('user_id', user.id) // 보안: 자신의 알림만 수정
    .select()
    .single();

  return { data, error };
}

/**
 * 여러 알림을 읽음으로 표시
 */
export async function markMultipleAsRead(notificationIds: string[]): Promise<{
  data: UserNotification[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notifications')
    .update({ 
      is_read: true, 
      read_at: new Date().toISOString() 
    })
    .in('id', notificationIds)
    .eq('user_id', user.id)
    .select();

  return { data, error };
}

/**
 * 모든 알림을 읽음으로 표시
 */
export async function markAllAsRead(): Promise<{
  data: UserNotification[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notifications')
    .update({ 
      is_read: true, 
      read_at: new Date().toISOString() 
    })
    .eq('user_id', user.id)
    .eq('is_read', false)
    .select();

  return { data, error };
}

/**
 * 알림 삭제
 */
export async function deleteNotification(notificationId: string): Promise<{
  data: null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { error } = await supabase
    .from('user_notifications')
    .delete()
    .eq('id', notificationId)
    .eq('user_id', user.id); // 보안: 자신의 알림만 삭제

  return { data: null, error };
}

/**
 * 읽은 알림 일괄 삭제 (정리용)
 */
export async function deleteReadNotifications(): Promise<{
  data: null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { error } = await supabase
    .from('user_notifications')
    .delete()
    .eq('user_id', user.id)
    .eq('is_read', true);

  return { data: null, error };
}

/**
 * 알림 통계 조회
 */
export async function getNotificationStats(): Promise<{
  data: NotificationStats | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  // 전체 알림 수 조회
  const { count: total, error: totalError } = await supabase
    .from('user_notifications')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.id);

  if (totalError) {
    return { data: null, error: totalError };
  }

  // 읽지 않은 알림 수 조회
  const { count: unread, error: unreadError } = await supabase
    .from('user_notifications')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.id)
    .eq('is_read', false);

  if (unreadError) {
    return { data: null, error: unreadError };
  }

  // 오늘 알림 수 조회
  const today = new Date().toISOString().split('T')[0];
  const { count: todayCount, error: todayError } = await supabase
    .from('user_notifications')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.id)
    .gte('created_at', `${today}T00:00:00.000Z`);

  if (todayError) {
    return { data: null, error: todayError };
  }

  // 타입별 알림 수 조회
  const { data: typeData, error: typeError } = await supabase
    .from('user_notifications')
    .select('type')
    .eq('user_id', user.id);

  if (typeError) {
    return { data: null, error: typeError };
  }

  const by_type = (typeData || []).reduce((acc, item) => {
    acc[item.type] = (acc[item.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return {
    data: {
      total: total || 0,
      unread: unread || 0,
      today: todayCount || 0,
      by_type
    },
    error: null
  };
}

/**
 * 사용자 알림 설정 조회
 */
export async function getUserNotificationSettings(): Promise<{
  data: UserNotificationSettings | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notification_settings')
    .select('*')
    .eq('user_id', user.id)
    .single();

  return { data, error };
}

/**
 * 사용자 알림 설정 업데이트
 */
export async function updateNotificationSettings(
  updates: UserNotificationSettingsUpdate
): Promise<{
  data: UserNotificationSettings | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_notification_settings')
    .update(updates)
    .eq('user_id', user.id)
    .select()
    .single();

  return { data, error };
}

/**
 * 특정 알림 타입 활성화/비활성화
 */
export async function toggleNotificationType(
  type: keyof Omit<UserNotificationSettings, 'user_id' | 'enabled' | 'email_enabled' | 'push_enabled' | 'updated_at'>,
  enabled: boolean
): Promise<{
  data: UserNotificationSettings | null;
  error: any;
}> {
  return await updateNotificationSettings({ [type]: enabled });
}

/**
 * 실시간 알림 구독 (Supabase Realtime 사용)
 */
export function subscribeToNotifications(
  callback: (payload: { new: UserNotification; old?: UserNotification; eventType: 'INSERT' | 'UPDATE' | 'DELETE' }) => void
) {
  return supabase
    .channel('user-notifications')
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'user_notifications'
    }, (payload) => {
      callback({ new: payload.new as UserNotification, eventType: 'INSERT' });
    })
    .on('postgres_changes', {
      event: 'UPDATE',
      schema: 'public',
      table: 'user_notifications'
    }, (payload) => {
      callback({ 
        new: payload.new as UserNotification, 
        old: payload.old as UserNotification,
        eventType: 'UPDATE' 
      });
    })
    .subscribe();
}

// 헬퍼 함수들

/**
 * 알림 타입이 사용자 설정에서 활성화되어 있는지 확인
 */
function isNotificationTypeEnabled(
  settings: UserNotificationSettings,
  type: string
): boolean {
  switch (type) {
    case 'signal':
      return settings.portfolio_alerts || settings.watchlist_alerts;
    case 'price_target':
      return settings.price_alerts;
    case 'analyst_report':
      return settings.analyst_reports;
    case 'market_summary':
      return settings.market_summary;
    case 'ai_insight':
      return settings.ai_insights;
    default:
      return true; // 새로운 타입은 기본적으로 허용
  }
}

/**
 * 시그널 기반 알림 생성 (개인화된 시그널 감지 시 사용)
 */
export async function createSignalNotification(
  stockCode: string,
  stockName: string,
  signalData: {
    signal_type: string;
    confidence: number;
    influencer_name: string;
    key_quote?: string;
    video_title?: string;
    signal_id?: string;
  }
): Promise<{
  data: UserNotification | null;
  error: any;
}> {
  const title = `${stockName} ${signalData.signal_type} 시그널`;
  const message = signalData.key_quote || 
    `${signalData.influencer_name}님이 ${stockName}에 대해 ${signalData.signal_type} 의견을 제시했습니다. (신뢰도: ${signalData.confidence}%)`;

  return await createNotification({
    type: 'signal',
    title,
    message,
    stock_code: stockCode,
    metadata: {
      signal_id: signalData.signal_id,
      confidence: signalData.confidence,
      influencer_name: signalData.influencer_name,
      video_title: signalData.video_title,
    }
  });
}

/**
 * 가격 알림 생성
 */
export async function createPriceAlert(
  stockCode: string,
  stockName: string,
  currentPrice: number,
  targetPrice: number,
  alertType: 'above' | 'below'
): Promise<{
  data: UserNotification | null;
  error: any;
}> {
  const direction = alertType === 'above' ? '상승' : '하락';
  const title = `${stockName} 목표가 도달!`;
  const message = `${stockName}이 설정한 목표가 ${targetPrice.toLocaleString()}원에 도달했습니다. (현재가: ${currentPrice.toLocaleString()}원)`;

  return await createNotification({
    type: 'price_target',
    title,
    message,
    stock_code: stockCode,
    metadata: {
      current_price: currentPrice,
      target_price: targetPrice,
      alert_type: alertType,
      price_change_percent: ((currentPrice - targetPrice) / targetPrice) * 100
    }
  });
}