# Price Audit Report - 2026-03-04

## Summary
- **Before cleanup**: 934 entries in signal_prices.json (784 UUID garbage)
- **After cleanup**: 152 valid entries
- **Zero price entries**: 0 ✅
- **Missing chart data**: 0 ✅

## Breakdown
- KR stocks: 62
- US stocks: 79
- Other (HK/Crypto/ETF/Index): 11

## Actions Taken
1. Removed 784 UUID garbage entries from signal_prices.json
2. Added 2 missing tickers from DB (IXIC, SQ/XYZ)
3. Fixed 4 failed tickers (284620.KQ, BRK-A, ^KS11, RIOT)
4. Refreshed all 152 prices via yfinance
5. Added 100 missing entries to stockPrices.json (3mo historical data)

## Previously Failed (Now Fixed)
- 284620 (아이덴): used .KQ suffix
- BRK.A (버크셔 해서웨이): used BRK-A symbol
- KS11 (코스피): used ^KS11 symbol
- RIOT (Riot Blockchain): fetched successfully on retry
- SQ (블록): ticker changed to XYZ
