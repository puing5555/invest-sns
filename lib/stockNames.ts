// 티커 → 한글 종목명 매핑 (DB에 한글 종목명이 없는 경우 사용)
const STOCK_NAME_MAP: Record<string, string> = {
  'CC': '캔톤네트워크',
  'BTC': '비트코인',
  'XRP': '리플',
  'NVDA': '엔비디아',
  'TSLA': '테슬라',
  'TSM': 'TSMC',
  'ASML': 'ASML',
  'MU': '마이크론',
  'SOXX': 'SOXX',
};

/**
 * 종목 표시명 반환: "한글명(티커)" 또는 stock이 이미 한글이면 "한글명(티커)"
 * stock과 ticker가 같으면 (CC/CC) 매핑 적용
 * stock이 이미 한글이면 ticker 있으면 "삼성전자(005930)", 없으면 "삼성전자"
 */
export function formatStockDisplay(stock?: string, ticker?: string): string {
  if (!stock) return ticker || '-';

  // DB에 "종목명 (TICKER)" 형태로 저장된 경우 strip
  let cleanStock = stock.replace(/\s*\([^)]+\)\s*$/, '').trim();

  const isKorean = /[가-힣]/.test(cleanStock);

  if (isKorean) {
    // 숫자로만 된 티커(005930 등)는 표시하지 않음
    if (!ticker || ticker === cleanStock || /^\d+$/.test(ticker)) return cleanStock;
    return `${cleanStock} (${ticker})`;
  }

  // 영문 티커만 있는 경우 → 매핑에서 한글명 찾기
  const korName = STOCK_NAME_MAP[cleanStock];
  if (korName) {
    return `${korName} (${cleanStock})`;
  }

  // 매핑 없으면 그대로
  return cleanStock;
}

/**
 * 관심 종목용: 한글명만 표시 (티커 제거). 한글명 없으면 원본 그대로.
 */
export function formatStockShort(stock?: string, ticker?: string): string {
  if (!stock) return ticker || '-';

  // DB에 "종목명 (TICKER)" 형태로 저장된 경우 strip
  let clean = stock.replace(/\s*\([^)]+\)\s*$/, '').trim();

  const isKorean = /[가-힣]/.test(clean);
  if (isKorean) return clean;

  const korName = STOCK_NAME_MAP[clean];
  return korName || clean;
}
