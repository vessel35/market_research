# regime_labels.csv Schema

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m · **Run:** 20260613_0558
**Status:** `regime_labels.csv` **not produced this run** (SPEC-ONLY, no OHLCV). This document is
the authoritative schema + value-rule contract so the file can be generated identically when data
is present, and so Phase 3 knows the exact columns. `regime_labeling=causal`;
`llm_discretion_used=false`.

## Columns (20, in order)

| # | column | type | description |
|---|---|---|---|
| 1 | `timestamp` | datetime (UTC) | bar close timestamp t |
| 2 | `usable_from_timestamp` | datetime (UTC) | `timestamp + 5min`; strictly > `timestamp` |
| 3 | `symbol` | string | `ETH/USDT` |
| 4 | `timeframe` | string | `5m` |
| 5 | `regime` | enum | one of `strong_up`,`strong_down`,`transition`,`volatile`,`range` (or `unknown_or_warmup` for warmup rows) |
| 6 | `regime_alt` | enum/null | next-closest within-framework regime (e.g. `transition` near the ADX gate; `range` near P70) |
| 7 | `regime_labeling` | string | always `causal` in this file |
| 8 | `regime_confidence` | float [0,1] | framework-internal confidence (classifier spec §12) |
| 9 | `selected_primary_framework` | string | `TREND_STRENGTH_ADX_EMA_SPEC` |
| 10 | `trend_score` | float | `ADX14` value at t (trend strength) |
| 11 | `volatility_score` | float [0,100] | trailing ATR14 percentile rank at t |
| 12 | `momentum_score` | float/null | null — not used by this framework |
| 13 | `mean_reversion_score` | float/null | null — not used by this framework |
| 14 | `volume_score` | float/null | null this run (no volume data); reserved for a future confidence layer |
| 15 | `data_quality_score` | float/null | null this run (data-quality checks not run; no data) |
| 16 | `feature_snapshot_ref` | string/null | pointer to `feature_snapshot.parquet` row; null this run |
| 17 | `classifier_version` | string | `phase4_specA_v1` |
| 18 | `source_data_path` | string | OHLCV path; `none (spec-only)` this run |
| 19 | `git_commit` | string | `n/a (not a git repo)` this run |
| 20 | `llm_discretion_used` | bool | always `false`; a `true` value invalidates the row |

## Value rules

1. `regime` ∈ the five canonical values (plus `unknown_or_warmup` for warmup/NaN rows; never
   `all`).
2. `regime_labeling` is always `causal` in this file.
3. `usable_from_timestamp` is strictly later than `timestamp` (next 5m bar for close-based labels).
4. `llm_discretion_used` is always `false`.
5. One row per 5m bar from `warmup_end` (288) onward; warmup rows either omitted or written as
   `unknown_or_warmup` (confidence 0) — never as a canonical regime.
6. Smoothed/posthoc labels are NOT written here — they go to their own files with
   `usable_in_hybrid=false`.
7. No strategy-performance or future-looking column may be added (see forbidden list).
8. Deterministic: identical OHLCV → identical rows.

## Forbidden columns (14) — must NEVER appear in regime_labels.csv

`strategy_id`, `variant_id`, `trade_id`, `net_pnl`, `return_pct`, `future_return`,
`future_max_price`, `future_min_price`, `future_profit`, `phase2_result`, `edge_fragment_id`,
`usable_in_hybrid`, `polarity`, `strategy_evaluation_verdict`.

These couple labels to strategy results or use future data; their presence is a hard failure of
the look-ahead checklist. `usable_in_hybrid` is a Phase 3 concept, not a Phase 4 label column.

## Example row (illustrative — NOT generated data; no OHLCV this run)

BEGIN_JSON
{
  "timestamp": "2024-01-02T03:05:00Z",
  "usable_from_timestamp": "2024-01-02T03:10:00Z",
  "symbol": "ETH/USDT",
  "timeframe": "5m",
  "regime": "strong_up",
  "regime_alt": "transition",
  "regime_labeling": "causal",
  "regime_confidence": 0.72,
  "selected_primary_framework": "TREND_STRENGTH_ADX_EMA_SPEC",
  "trend_score": 31.4,
  "volatility_score": 58.0,
  "momentum_score": null,
  "mean_reversion_score": null,
  "volume_score": null,
  "data_quality_score": null,
  "feature_snapshot_ref": null,
  "classifier_version": "phase4_specA_v1",
  "source_data_path": "none (spec-only)",
  "git_commit": "n/a (not a git repo)",
  "llm_discretion_used": false
}
END_JSON

The example is illustrative only; values are not derived from any real or Phase 2/3 data.
