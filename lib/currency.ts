// lib/currency.ts
export function isKoreanStock(ticker: string): boolean {
  return /^\d+$/.test(ticker);
}
export function getCurrencySymbol(ticker: string): string {
  return isKoreanStock(ticker) ? '원' : '$';
}
export function formatStockPrice(price: number, ticker: string): string {
  const isKR = isKoreanStock(ticker);
  if (isKR) return `${price.toLocaleString()}원`;
  return `$${price.toLocaleString()}`;
}
