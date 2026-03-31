// lib/currency.ts
export function isKoreanStock(ticker: string): boolean {
  return /^\d+$/.test(ticker);
}
export function getCurrencySymbol(ticker: string): string {
  return isKoreanStock(ticker) ? '원' : '$';
}
export function formatStockPrice(price: number, ticker: string): string {
  if (price == null || isNaN(price)) return '-';
  const isKR = isKoreanStock(ticker);
  if (isKR) return `${price.toLocaleString()}원`;

  // 극소수 가격 (크립토 등): 소수점 6~8자리, 반올림 없이 절삭
  if (price > 0 && price < 0.01) {
    const firstSig = Math.ceil(-Math.log10(price));
    const digits = Math.min(8, Math.max(6, firstSig + 3));
    const factor = 10 ** digits;
    const truncated = Math.floor(price * factor) / factor;
    return `$${truncated.toFixed(digits)}`;
  }
  if (price > 0 && price < 1) {
    return `$${price.toFixed(4)}`;
  }
  return `$${price.toLocaleString()}`;
}

export function formatPriceChange(change: number, ticker: string): string {
  if (change == null || isNaN(change)) return '-';
  const isKR = isKoreanStock(ticker);
  const sign = change >= 0 ? '+' : '';
  if (isKR) return `${sign}${change.toLocaleString()}원`;

  const abs = Math.abs(change);
  if (abs > 0 && abs < 0.01) {
    const firstSig = Math.ceil(-Math.log10(abs));
    const digits = Math.min(8, Math.max(6, firstSig + 3));
    const factor = 10 ** digits;
    const truncated = Math.floor(abs * factor) / factor;
    const val = change < 0 ? -truncated : truncated;
    return `${sign}$${val.toFixed(digits)}`;
  }
  if (abs > 0 && abs < 1) {
    return `${sign}$${change.toFixed(4)}`;
  }
  return `${sign}$${change.toLocaleString()}`;
}
