// 주가 데이터 캐싱 시스템
interface CachedStockData {
  data: any[];
  timestamp: number;
  symbol: string;
  period: string;
}

interface StockCache {
  [key: string]: CachedStockData;
}

const CACHE_DURATION = 5 * 60 * 1000; // 5분 캐싱
const stockCache: StockCache = {};

export const getCachedStockData = (symbol: string, period: string): any[] | null => {
  const cacheKey = `${symbol}_${period}`;
  const cached = stockCache[cacheKey];
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    console.log(`캐시에서 데이터 로드: ${symbol} (${period})`);
    return cached.data;
  }
  
  return null;
};

export const setCachedStockData = (symbol: string, period: string, data: any[]): void => {
  const cacheKey = `${symbol}_${period}`;
  stockCache[cacheKey] = {
    data,
    timestamp: Date.now(),
    symbol,
    period
  };
  console.log(`데이터 캐시 저장: ${symbol} (${period}) - ${data.length}개 포인트`);
};

export const clearStockCache = (): void => {
  Object.keys(stockCache).forEach(key => delete stockCache[key]);
  console.log('주가 데이터 캐시 초기화');
};

export const getCacheStats = () => {
  const entries = Object.entries(stockCache);
  return {
    totalCached: entries.length,
    cacheEntries: entries.map(([key, value]) => ({
      key,
      symbol: value.symbol,
      period: value.period,
      dataPoints: value.data.length,
      age: Math.round((Date.now() - value.timestamp) / 1000),
      expired: Date.now() - value.timestamp > CACHE_DURATION
    }))
  };
};