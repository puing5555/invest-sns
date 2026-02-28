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

  const isKorean = /[가-힣]/.test(stock);

  if (isKorean) {
    // 이미 한글 → "삼성전자(005930)" or "삼성전자"
    return ticker && ticker !== stock ? `${stock}(${ticker})` : stock;
  }

  // 영문 티커만 있는 경우 → 매핑에서 한글명 찾기
  const korName = STOCK_NAME_MAP[stock];
  if (korName) {
    return `${korName}(${stock})`;
  }

  // 매핑 없으면 그대로
  return stock;
}
