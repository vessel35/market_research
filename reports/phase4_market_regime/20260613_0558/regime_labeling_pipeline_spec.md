# Regime Labeling Pipeline Spec

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m · **Run:** 20260613_0558
**Classifier:** `phase4_trendstrength` `phase4_specA_v1` · **Primary labeling method:** causal.
**Mode:** SPEC-ONLY — pipeline fully specified; **not executed** (no OHLCV). `regime_labels.csv`
not produced this run.

## 1. Raw data input

ETH/USDT 5m OHLCV (`timestamp, open, high, low, close, volume`), Binance USDT-M perpetual,
UTC, 5-minute spacing. Optional data (funding/OI/taker) not required and absent this run.
`source_data_path` recorded in the manifest and label rows (`none (spec-only)` this run).

## 2. Data-quality validation (skill §8a / prompt §18) — run before any labeling

Checks: timestamps strictly ascending; zero duplicate timestamps; 5-minute gaps identified;
OHLC valid (high ≥ max(open,close), low ≤ min(open,close), high ≥ low); no negative price/volume;
zero-volume and extreme-spike bars flagged; data start/end confirmed; optional-data coverage
measured; timezone (UTC) confirmed; feature availability vs live timing checked. **Fatal** issues
(out-of-order/duplicate timestamps, broken OHLC) → NO labels produced. **Correctable** issues →
documented with method + impact in `data_quality_report.md`. **This run (methodology-only):** no data → these checks are out of scope (data-dependent), not a
deficiency; `data_quality_report.md` not produced and `data_quality_score` left null. Run them
when OHLCV is present.

## 3. Feature calculation (bars ≤ t)

Per `causal_regime_classifier_spec.md` §4/§6/§7/§8: TR/DM → Wilder ATR14, +DI/−DI, DX → ADX14;
EMA9/21/55 + `ema_alignment_state`; `volatility_score` = trailing ATR14 percentile (window
W=2016, min 288). All causal.

## 4. Selected primary framework application

Apply the repository-defined trend-strength rules (one framework, no mixing) from
`causal_regime_classifier_spec.md` §9. No other family's rules are applied.

## 5. Causal regime classification

For each bar t, emit `regime` ∈ {strong_up, strong_down, transition, volatile, range} (or
`unknown_or_warmup` for warmup/NaN), `regime_confidence` (§12 of the classifier spec), and
`regime_alt` (the next-closest within-framework regime, e.g. for `strong_up` near the ADX gate,
`transition`; for `volatile` near P70, `range`). `regime_labeling="causal"` for every row.

## 6. usable_from_timestamp assignment

`usable_from_timestamp[t] = timestamp[t] + 5min` (next 5m bar open), strictly later than
`timestamp[t]` — the label uses bar-t close and is usable for decisions/joins only from t+1.

## 7. regime_labels.csv output

Schema and value rules per `regime_labels_schema.md` (20 columns; `regime_labeling=causal`;
`llm_discretion_used=false`; no strategy-performance columns). Written under the run dir only.
**This run:** not produced (no data). When data is present, one row per 5m bar from `warmup_end`.

## 8. Phase 3 trade-join algorithm (Phase 3 performs; Phase 4 specifies)

BEGIN_PSEUDOCODE
for each trade:
    entry_time = trade.timestamp_entry
    exit_time  = trade.timestamp_exit
    regime_at_entry = latest label where regime_labeling="causal"
                      and usable_from_timestamp <= entry_time
    regime_at_exit  = latest label where regime_labeling="causal"
                      and usable_from_timestamp <= exit_time
    holding_period_regime_path = all causal labels with
        usable_from_timestamp >= entry_time and usable_from_timestamp <= exit_time
    if no causal label has usable_from_timestamp <= entry_time:
        regime_at_entry = "unknown_or_warmup"   # or exclude the trade from analysis
END_PSEUDOCODE

Phase 3 writes `regime_enriched_trades.csv` / `regime_enriched_trade_logs.jsonl`; it NEVER
overwrites Phase 2 `trades.csv`.

## 9. Phase 3 daily/period-join algorithm (Phase 3 performs; Phase 4 specifies)

BEGIN_PSEUDOCODE
for each period [period_start, period_end)  (e.g., a UTC day, or a portfolio/daily_returns row):
    labels_in_period = all causal labels with
        usable_from_timestamp >= period_start and usable_from_timestamp < period_end
    regime_time_share[r] = count(labels_in_period.regime == r) / count(labels_in_period)
                           for r in the five canonical regimes
    dominant_regime = argmax_r regime_time_share[r]   # ties -> mark "mixed"
    # attach regime_time_share (+ dominant_regime) to the period row for regime-conditional
    # aggregation; "all" = unconditional aggregation across every period
END_PSEUDOCODE

## 10. Error handling

- Fatal data-quality issue → abort labeling, emit `data_quality_report.md`, produce no labels.
- Warmup / NaN features (t < warmup_end=288) → `regime="unknown_or_warmup"`, confidence 0; such
  rows are excluded from Phase 3 hybrid eligibility.
- Zero-denominator in DX (when +DI+−DI=0) → DX=0.
- Gaps: a 5m gap does not invent bars; indicators continue from available bars; the gap is flagged
  in the data-quality report and the first post-gap bars may be lower-confidence.
- Insufficient history for the volatility window (< min 288) → warmup.

## 11. Non-causal label separation

Only causal labels are produced as the core output. If smoothed or posthoc labels are ever made,
they go to `smoothed_regime_labels.csv` / `posthoc_regime_labels.csv`, carry
`usable_in_hybrid=false`, and are NEVER written into `regime_labels.csv` or used as a
hybrid-eligibility basis. None are produced this run.

## 12. Reproducibility requirements

Deterministic: identical OHLCV input → identical labels (no randomness, no model fit, no LLM
discretion). Record `classifier_version` (`phase4_specA_v1`), `source_data_path`, `git_commit`,
the fixed thresholds (ADX 25, P70), and the window parameters (W=2016, min 288, warmup 288) so any
run is bit-reproducible. Live and backtest use the identical classification function. `git_commit`
is `n/a (not a git repo)` this run.
