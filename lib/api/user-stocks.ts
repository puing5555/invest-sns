/**
 * 사용자 보유 종목 관리 API
 * 목적: 포트폴리오 CRUD 및 손익 계산
 */

import { supabase } from '@/lib/supabase';
import type { Database } from '@/types/supabase';

type UserStock = Database['public']['Tables']['user_stocks']['Row'];
type UserStockInsert = Database['public']['Tables']['user_stocks']['Insert'];
type UserStockUpdate = Database['public']['Tables']['user_stocks']['Update'];

// 포트폴리오 요약 타입
export interface PortfolioSummary {
  totalInvestment: number;
  totalValue: number;
  totalReturn: number;
  totalReturnPercent: number;
  totalStocks: number;
}

// 확장된 종목 정보 (현재가 포함)
export interface UserStockWithPrice extends UserStock {
  current_price?: number;
  current_value?: number;
  profit_loss?: number;
  profit_loss_percent?: number;
}

/**
 * 사용자의 모든 보유 종목 조회
 */
export async function getUserStocks(): Promise<{
  data: UserStock[] | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_stocks')
    .select('*')
    .eq('user_id', user.id)
    .order('total_investment', { ascending: false });

  return { data, error };
}

/**
 * 특정 종목의 보유 정보 조회
 */
export async function getUserStock(stockCode: string): Promise<{
  data: UserStock | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { data, error } = await supabase
    .from('user_stocks')
    .select('*')
    .eq('user_id', user.id)
    .eq('stock_code', stockCode)
    .single();

  return { data, error };
}

/**
 * 새 종목을 포트폴리오에 추가
 */
export async function addUserStock(stockData: {
  stock_code: string;
  stock_name: string;
  market: string;
  quantity: number;
  avg_buy_price: number;
  notes?: string;
}): Promise<{
  data: UserStock | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const insertData: UserStockInsert = {
    user_id: user.id,
    stock_code: stockData.stock_code,
    stock_name: stockData.stock_name,
    market: stockData.market,
    quantity: stockData.quantity,
    avg_buy_price: stockData.avg_buy_price,
    notes: stockData.notes || null,
  };

  const { data, error } = await supabase
    .from('user_stocks')
    .insert([insertData])
    .select()
    .single();

  return { data, error };
}

/**
 * 기존 보유 종목 정보 수정
 */
export async function updateUserStock(
  stockId: string,
  updates: {
    quantity?: number;
    avg_buy_price?: number;
    notes?: string;
  }
): Promise<{
  data: UserStock | null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const updateData: UserStockUpdate = {
    ...updates,
    last_updated_at: new Date().toISOString(),
  };

  const { data, error } = await supabase
    .from('user_stocks')
    .update(updateData)
    .eq('id', stockId)
    .eq('user_id', user.id) // 보안: 자신의 종목만 수정 가능
    .select()
    .single();

  return { data, error };
}

/**
 * 수량 및 평균매수가 업데이트 (추가 매수/매도)
 */
export async function updateStockPosition(
  stockCode: string,
  transaction: {
    type: 'buy' | 'sell';
    quantity: number;
    price: number;
    notes?: string;
  }
): Promise<{
  data: UserStock | null;
  error: any;
}> {
  const { data: currentStock, error: fetchError } = await getUserStock(stockCode);
  
  if (fetchError || !currentStock) {
    return { data: null, error: fetchError || new Error('Stock not found') };
  }

  let newQuantity: number;
  let newAvgBuyPrice: number;

  if (transaction.type === 'buy') {
    // 추가 매수: 가중평균 계산
    const currentValue = Number(currentStock.quantity) * Number(currentStock.avg_buy_price);
    const additionalValue = transaction.quantity * transaction.price;
    newQuantity = Number(currentStock.quantity) + transaction.quantity;
    newAvgBuyPrice = (currentValue + additionalValue) / newQuantity;
  } else {
    // 매도: 수량만 감소
    newQuantity = Number(currentStock.quantity) - transaction.quantity;
    newAvgBuyPrice = Number(currentStock.avg_buy_price);
    
    if (newQuantity < 0) {
      return { data: null, error: new Error('Cannot sell more than owned quantity') };
    }
    
    // 전량 매도시 종목 삭제
    if (newQuantity === 0) {
      return await deleteUserStock(currentStock.id);
    }
  }

  const notes = transaction.notes 
    ? `${currentStock.notes || ''}\n${new Date().toISOString()}: ${transaction.type} ${transaction.quantity}주 @${transaction.price} - ${transaction.notes}`.trim()
    : currentStock.notes;

  return await updateUserStock(currentStock.id, {
    quantity: newQuantity,
    avg_buy_price: newAvgBuyPrice,
    notes,
  });
}

/**
 * 보유 종목 삭제
 */
export async function deleteUserStock(stockId: string): Promise<{
  data: null;
  error: any;
}> {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { data: null, error: new Error('User not authenticated') };
  }

  const { error } = await supabase
    .from('user_stocks')
    .delete()
    .eq('id', stockId)
    .eq('user_id', user.id); // 보안: 자신의 종목만 삭제 가능

  return { data: null, error };
}

/**
 * 포트폴리오 요약 정보 계산
 */
export async function getPortfolioSummary(
  currentPrices?: Record<string, number>
): Promise<{
  data: PortfolioSummary | null;
  error: any;
}> {
  const { data: stocks, error } = await getUserStocks();
  
  if (error || !stocks) {
    return { data: null, error };
  }

  if (stocks.length === 0) {
    return {
      data: {
        totalInvestment: 0,
        totalValue: 0,
        totalReturn: 0,
        totalReturnPercent: 0,
        totalStocks: 0,
      },
      error: null
    };
  }

  const totalInvestment = stocks.reduce((sum, stock) => 
    sum + (Number(stock.quantity) * Number(stock.avg_buy_price)), 0
  );

  let totalValue = totalInvestment; // 기본값: 매수가 기준

  // 현재가가 제공된 경우 실시간 가치 계산
  if (currentPrices) {
    totalValue = stocks.reduce((sum, stock) => {
      const currentPrice = currentPrices[stock.stock_code] || Number(stock.avg_buy_price);
      return sum + (Number(stock.quantity) * currentPrice);
    }, 0);
  }

  const totalReturn = totalValue - totalInvestment;
  const totalReturnPercent = totalInvestment > 0 ? (totalReturn / totalInvestment) * 100 : 0;

  return {
    data: {
      totalInvestment,
      totalValue,
      totalReturn,
      totalReturnPercent,
      totalStocks: stocks.length,
    },
    error: null
  };
}

/**
 * 현재가와 함께 보유 종목 조회 (외부 가격 데이터 연동용)
 */
export async function getUserStocksWithPrices(
  currentPrices: Record<string, number>
): Promise<{
  data: UserStockWithPrice[] | null;
  error: any;
}> {
  const { data: stocks, error } = await getUserStocks();
  
  if (error || !stocks) {
    return { data: null, error };
  }

  const stocksWithPrices: UserStockWithPrice[] = stocks.map(stock => {
    const currentPrice = currentPrices[stock.stock_code];
    const quantity = Number(stock.quantity);
    const avgBuyPrice = Number(stock.avg_buy_price);
    
    let current_value, profit_loss, profit_loss_percent;
    
    if (currentPrice) {
      current_value = quantity * currentPrice;
      profit_loss = current_value - (quantity * avgBuyPrice);
      profit_loss_percent = ((currentPrice - avgBuyPrice) / avgBuyPrice) * 100;
    }

    return {
      ...stock,
      current_price: currentPrice,
      current_value,
      profit_loss,
      profit_loss_percent,
    };
  });

  return { data: stocksWithPrices, error: null };
}

/**
 * 시장별 보유 종목 통계
 */
export async function getPortfolioByMarket(): Promise<{
  data: Record<string, { count: number; investment: number; percentage: number }> | null;
  error: any;
}> {
  const { data: stocks, error } = await getUserStocks();
  
  if (error || !stocks) {
    return { data: null, error };
  }

  const totalInvestment = stocks.reduce((sum, stock) => 
    sum + (Number(stock.quantity) * Number(stock.avg_buy_price)), 0
  );

  const marketStats = stocks.reduce((acc, stock) => {
    const investment = Number(stock.quantity) * Number(stock.avg_buy_price);
    
    if (!acc[stock.market]) {
      acc[stock.market] = { count: 0, investment: 0, percentage: 0 };
    }
    
    acc[stock.market].count += 1;
    acc[stock.market].investment += investment;
    
    return acc;
  }, {} as Record<string, { count: number; investment: number; percentage: number }>);

  // 퍼센트 계산
  Object.keys(marketStats).forEach(market => {
    marketStats[market].percentage = totalInvestment > 0 
      ? (marketStats[market].investment / totalInvestment) * 100 
      : 0;
  });

  return { data: marketStats, error: null };
}