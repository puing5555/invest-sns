/**
 * stockUtils.ts -- 종목 코드 정규화 유틸
 *
 * DB 시그널 ticker와 static URL 경로 불일치 방지:
 *   ETH-USD → ETH
 *   BTC-USD → BTC
 *   000660.KS → 000660  (이미 별도 페이지 존재하는 경우 유지)
 */

/**
 * ticker를 URL 경로용으로 정규화.
 * - 크립토: ETH-USD → ETH, BTC-USD → BTC
 * - 한국주식: 000660.KS는 그대로 (out/stock/000660.KS 존재)
 * - 기타: 변경 없음
 */
export function normalizeTickerForUrl(ticker: string): string {
  if (!ticker) return ticker;

  // 크립토 USD 페어 정규화: XXX-USD → XXX
  if (ticker.endsWith('-USD')) {
    return ticker.replace('-USD', '');
  }

  return ticker;
}

/**
 * stock 상세 페이지 URL 생성 헬퍼.
 * tab 파라미터는 선택적.
 */
export function stockDetailUrl(ticker: string, tab?: string): string {
  const code = normalizeTickerForUrl(ticker);
  const base = `/stock/${code}`;
  return tab ? `${base}?tab=${tab}` : base;
}
