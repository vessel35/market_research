# Data Quality Report

**Source:** `/home/vessel/workspace/trading-system/backtestdata/ETHUSDT_futures_5min.csv`
**Run dir:** `/home/vessel/workspace/CoinTrading/market-regime/reports/phase4_market_regime/20260613_0558`

## 1. Timezone
Timestamps have no tz info in the file; localized to UTC per spec assumption. All downstream work uses UTC.

## 2. Coverage
- Data start: `2024-01-01 00:00:00+00:00`
- Data end:   `2025-12-31 23:55:00+00:00`
- Total rows: 210,528
- Expected (2024-01-01 to 2025-12-31 23:55 UTC, 5 m grid): 210,528
- Row delta:  +0

## 3. Timestamp order
PASS — all timestamps strictly ascending.

## 4. Duplicate timestamps
PASS — zero duplicate timestamps.

## 5. Five-minute gaps
- Gap count (consecutive bars with delta > 5 min): 0
PASS — no gaps found.

## 6. OHLC validity
- high < max(open,close): 0
- low > min(open,close):  0
- high < low:             0
- Total rows with any OHLC violation: 0
PASS — all OHLC relationships valid.

## 7. Negative / zero prices and volume
- open <= 0:   0
- high <= 0:   0
- low <= 0:    0
- close <= 0:  0
- volume <= 0: 21
WARNING (correctable): 21 zero-volume bar(s) flagged. Indicators computed; bars retained but noted.

## 8. Extreme-spike detection
- Method: |pct_change(close)| > max(5%, 10x median |pct_change|)
- Median |pct_change|: 0.000925
- Spike threshold used: 0.050000 (5.000%)
- Spike-flagged bars: 9
  First few (illustrative):
  - 2024-01-03 12:05:00+00:00 close=2087.87
  - 2024-04-13 20:05:00+00:00 close=2865.28
  - 2024-08-05 01:05:00+00:00 close=2340.95
  - 2024-12-09 21:00:00+00:00 close=3547.16
  - 2025-02-03 02:05:00+00:00 close=2334.44
Correctable: extreme-spike bars retained; data_quality_score is null this run. Impact: ATR/ADX one-bar transient around the spike.

## 9. Optional data (funding / OI / taker / liquidation)
Not present. Framework requires only OHLCV; optional features are null in labels. No impact on primary classification.

## 10. Summary
**VERDICT: PASS (no fatal issues). Correctable issues documented above. Proceeding to label generation.**
