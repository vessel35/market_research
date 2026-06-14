# Regime Prediction Label Spec (Stage B — Executed)

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m · **Run:** 20260613_0558
**Stage:** B. **Status:** EXECUTED on real labels (2026-06-14); labels built from Stage A
`regime_labels.csv` by `build_prediction_labels.py`. See `regime_prediction_results.md`.
**Source of the per-bar regime:** Stage A causal classifier `TREND_STRENGTH_ADX_EMA_SPEC`
(`phase4_specA_v1`). Stage A is NOT modified.

> THE FOUNDATIONAL RULE OF THIS DOCUMENT: every label below is a SUPERVISED TARGET ONLY. A label
> is derived from bars STRICTLY AFTER t. It is NEVER used as a current-regime feature, NEVER
> written into `regime_labels.csv`, and NEVER consumed by Phase 3 as a current regime. Features
> come from bars ≤ t (the Stage A causal features); labels come from bars > t. There is a clean
> boundary at t with an explicit gap (§5) so that no future information leaks into a predictor.

## 1. Time layout per training example

For a decision bar t and horizon h ∈ {3, 6, 12, 24, 48} bars:

- **Feature region:** bars ≤ t (predictors; the Stage A causal features and causal derivatives).
- **Label region:** bars in `(t, t+h]` (targets only).
- **Embargo gap (§5):** ensures the predictor's `usable_from_timestamp` never crosses into the
  label region.

A training row exists only if BOTH the feature region is past warmup (Stage A **effective warmup =
301 bars**; first labeled bar idx 301 = 2024-01-02 01:05:00 — the nominal `warmup_end=288` plus the
volatility_score's 288-bar min window) AND the full label region `(t, t+h]` exists in-sample for
that fold. Rows without a complete future window are dropped, never back-filled or padded.

## 2. Primary label — `label_future_regime_h`

BEGIN_PSEUDOCODE
# regime[] is the Stage A CAUSAL label series (phase4_specA_v1), bars <= each index.
# This reads regime AT INDEX t+h. It is a TARGET, never a feature.
label_future_regime_h[t] = regime[t + h]      # for h in {3,6,12,24,48}

# valid only if regime[t+h] is one of the five canonical values
# (strong_up, strong_down, transition, volatile, range);
# if regime[t+h] == "unknown_or_warmup"  -> example is DROPPED (no label), not coerced.
END_PSEUDOCODE

Notes:
- `regime[t+h]` itself was produced causally (it only used bars ≤ t+h when computed). Using it as
  a *label at decision time t* is correct supervised learning: we are predicting a future quantity.
  It becomes leakage ONLY if it (or any function of bars > t) is fed as a *predictor* at t — which
  is forbidden.
- `unknown_or_warmup` is never a target class. Rows whose future bar is warmup/NaN are excluded.

## 3. Trend collapse — `label_future_trend_regime_h`

BEGIN_PSEUDOCODE
r = regime[t + h]
if   r in {strong_up, strong_down, transition}: label_future_trend_regime_h[t] = "trending"
elif r in {volatile, range}:                    label_future_trend_regime_h[t] = "non_trending"
else:                                            label_future_trend_regime_h[t] = DROP   # warmup
END_PSEUDOCODE

A 2-class (trending / non_trending) coarse target; useful when 5-class is too sparse for a horizon.

## 4. Future realized-volatility label — `label_future_vol_regime_h`

A 3-class {high, normal, low} target built from realized volatility over the label window,
bucketed by TRAIN-ONLY percentiles (never whole-sample, never test).

BEGIN_PSEUDOCODE
# realized vol over the FUTURE window (t, t+h] -> this is a LABEL, never a feature.
log_ret[k] = ln(close[k] / close[k-1])
fut_rv_h[t] = stdev( log_ret[t+1 .. t+h] )        # realized vol of the next h bars

# Bucket thresholds are fit ON THE TRAIN FOLD ONLY:
#   p33_train, p67_train = 33rd/67th percentile of { fut_rv_h over TRAIN rows only }
# These same frozen thresholds are then APPLIED to validation/test rows (not refit).
if   fut_rv_h[t] >= p67_train: label_future_vol_regime_h[t] = "high"
elif fut_rv_h[t] <= p33_train: label_future_vol_regime_h[t] = "low"
else:                          label_future_vol_regime_h[t] = "normal"
END_PSEUDOCODE

Percentile thresholds are TRAIN-ONLY (skill §15 threshold policy + statistical-validation
train-only fit). They are frozen per fold and applied forward; refitting them on test data is
FORBIDDEN. `fut_rv_h` uses only bars > t, so it is a valid target and is never a predictor.

## 5. Embargo / gap rule (no boundary leakage)

The Stage A label for bar t becomes usable only at `t + 5min` (`usable_from_timestamp = t+1`).
Therefore:

- The newest predictor allowed for a decision at t is the Stage A label/feature of bar t, whose
  `usable_from_timestamp = t+1`. That is still ≤ the label region start (`t+1` onward) but it does
  NOT use any bar > t. To be safe and unambiguous, predictors are required to be fully determined
  by bars ≤ t.
- An **embargo of at least 1 bar** is placed between the feature region and the label region so
  that no feature window can touch the label window. For models with longer trailing feature
  windows, the embargo is documented and the same gap is applied identically in train/validation/
  test (no shrinking the gap on test).
- The label window `(t, t+h]` and the feature window `(…, t]` never overlap. This is asserted in
  the validation plan's leakage tests.

## 6. Future breakout label — `label_future_breakout_h`

A binary breakout event over the future window. Threshold is theory/convention or TRAIN-ONLY,
never tuned to Phase 2/3 outcomes.

BEGIN_PSEUDOCODE
# Reference level and band fixed at t from PAST bars only (this part is causal context, not the label):
ref_close = close[t]
atr_t     = ATR14[t]                              # Stage A causal ATR, bars <= t
k         = 1.5                                   # fixed convention (documented), not tuned to performance

# Future excursion over (t, t+h] -> LABEL region, bars > t:
up_move   = max(high[t+1 .. t+h]) - ref_close
down_move = ref_close - min(low[t+1 .. t+h])

label_future_breakout_h[t] = 1 if max(up_move, down_move) >= k * atr_t else 0
END_PSEUDOCODE

- The future `max(high)` / `min(low)` are used ONLY to build the label. They are NEVER features
  (using a future high/low as a current feature is explicitly forbidden by the look-ahead
  checklist). `atr_t` and `ref_close` are causal (bars ≤ t) and serve only to scale the threshold.
- `future_breakout_probability` is the model's P(label_future_breakout_h = 1).

## 7. Probability targets (binary, derived from the regime labels above)

BEGIN_PSEUDOCODE
label_future_range_h[t]      = 1 if regime[t+h] == "range"      else 0   # -> future_range_probability
label_future_transition_h[t] = 1 if regime[t+h] == "transition" else 0   # -> future_transition_probability
label_future_no_trade_h[t]   = 1 if regime[t+h] in {volatile, transition} else 0  # -> future_no_trade_probability
# rows where regime[t+h] == "unknown_or_warmup" are DROPPED, not labeled 0.
END_PSEUDOCODE

`future_no_trade_probability` is defined purely from regime SHAPE (which regimes are structurally
hostile to clean execution). It is NOT derived from any Phase 2/3 trade outcome, P&L, win rate,
profit factor, MDD, or Sharpe. It is an abstain/risk signal, not a performance label.

## 8. Label inventory and target columns

The per-(t, horizon) feature/label matrices (`prediction_matrix_h{h}.csv.gz`, regenerable via
`build_prediction_labels.py`) carry, per (t, horizon):

| column | type | source rule |
|---|---|---|
| `timestamp` | datetime UTC | decision bar t |
| `horizon_bars` | int | one of 3,6,12,24,48 |
| `label_future_regime` | enum(5) | §2 |
| `label_future_trend_regime` | enum(2) | §3 |
| `label_future_vol_regime` | enum(3) | §4 (train-only percentile) |
| `label_future_breakout` | bool | §6 |
| `label_future_range` | bool | §7 |
| `label_future_transition` | bool | §7 |
| `label_future_no_trade` | bool | §7 |
| `label_origin` | string | always `stage_b_supervised_target` |
| `llm_discretion_used` | bool | always `false` |

This file is a TARGET file for model training. It is physically and semantically separate from
`regime_labels.csv` and is never joined into it.

## 9. Hard separation guarantees (what makes this leak-free)

1. Predictors ⊆ {functions of bars ≤ t}. Targets ⊆ {functions of bars > t}. Disjoint by
   construction, with an embargo gap (§5).
2. No target column ever appears in the Stage A `regime_labels.csv` (its forbidden-column list
   already bans `future_return`, `future_max_price`, `future_min_price`, `future_profit`, etc.).
3. No future return/high/low/min/max is ever used as a CURRENT feature; such quantities appear
   only inside the label definitions above.
4. Volatility-bucket thresholds and any breakout threshold are TRAIN-ONLY or fixed convention —
   never test-set, never tuned to Phase 2/3 results.
5. `unknown_or_warmup` future bars produce DROPPED rows, never a coerced class.
6. No Phase 2 artifact and no Phase 3 artifact is used to define ANY label. `phase2_results_used
   =false`, `phase3_results_used=false`.
7. `llm_discretion_used=false` for every label: all targets are mechanical.

## 10. Scope reminder

These labels exist solely to TRAIN and EVALUATE Stage B forecast models under walk-forward
validation (see `regime_prediction_validation_plan.md`). They never become a current-regime
label, never feed the Stage A classifier, and never reach Phase 3 as a regime value. Phase 3
continues to use only the causal Stage A `regime` from `regime_labels.csv`.
