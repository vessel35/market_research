# Regime Prediction Validation Plan (Stage B — Design Only)

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m · **Run:** 20260613_0558
**Stage:** B. **Status:** DESIGN / METHODOLOGY-ONLY (NO OHLCV loaded; nothing trained or scored).
**Skills applied:** `statistical-validation` (time-ordered CV, train-only fit, no shuffle),
`ml-strategy` (walk-forward, label construction, calibration).

> No metric in this document is an empirical result. This is the validation PROTOCOL to be run
> when data is present. Any future reporting of these metrics must include class balance, the
> confusion matrix, calibration, and the per-fold spread — a single headline number is not a
> valid claim, and a forecast is never presented as a certain future.

## 1. Validation principle (strictly time-ordered)

Time is never broken. Every split preserves chronological order: training data strictly precedes
validation data, which strictly precedes test data. The model is always evaluated on bars that
occur AFTER everything it was fit on. This mirrors live deployment, where only the past is known.

## 2. Split scheme

### 2.1 Outer holdout (time split)

Partition the series chronologically into TRAIN / VALIDATION / TEST contiguous blocks (e.g.
60% / 20% / 20% by time). TEST is the most recent block and is touched exactly once, at the very
end, after all model and threshold decisions are frozen. No iterating on TEST.

### 2.2 Walk-forward (primary protocol)

Roll a train→test window forward through time, refitting at each step. Two variants, both
reported:

- **Expanding window:** train on `[start … e_k]`, evaluate on `(e_k … e_k + step]`, then extend
  `e_k`. Train set grows; uses all available history.
- **Rolling window:** train on a FIXED-LENGTH window `(e_k − L … e_k]`, evaluate on the next
  step, then slide both edges. Adapts to non-stationarity; discards stale history.

For each fold and each horizon h, the label region `(t, t+h]` for the LAST train row must end
before the first test row begins — i.e. an embargo of ≥ h bars (plus the §5 feature-side gap from
the label spec) is removed at the train/test seam so the future window of a train row cannot
overlap test inputs (purged + embargoed walk-forward). This embargo is applied identically across
all folds and is never shrunk to gain test rows.

### 2.3 Hyperparameter / threshold selection

All model selection, calibration fitting, and threshold setting (e.g. the future-vol-regime
train-only percentiles, breakout k, classification cutoffs) happen on TRAIN (and an inner
time-ordered VALIDATION split carved from TRAIN by the same chronological rule). The TEST block
never participates in any fitting or tuning.

## 3. FORBIDDEN validation practices (hard rules)

- Random train/test split or k-fold that ignores time order. FORBIDDEN.
- Shuffle split / any shuffling that mixes future bars into training. FORBIDDEN.
- Test-set threshold tuning or model selection on the test block. FORBIDDEN.
- Whole-data fit of ANY transform: scaler/standardizer, PCA, clustering, HMM emission/transition
  params, calibration map, or vol-bucket percentiles fit on the full sample (train+test).
  FORBIDDEN — all fit on TRAIN only, frozen, then applied forward.
- Using HMM SMOOTHED (full-sequence) state probabilities. FORBIDDEN — they peek at future bars.
  Only FILTERED (online, left-to-right) probabilities may be a feature or a prediction.
- Using any Phase 2 performance artifact (result.json, trades.csv, portfolio.csv, signals.csv,
  per-strategy return / win-rate / profit-factor / MDD / Sharpe) as a feature, label, weight, or
  selection criterion. FORBIDDEN.
- Using any Phase 3 artifact (edge_fragment, strategy_evaluation, "strategy X profited in period
  Y") as a feature, label, weight, or selection criterion. FORBIDDEN.
- Any DB write. FORBIDDEN (DB is read-only and optional).

## 4. Look-ahead rules specific to prediction

1. **Feature/label time separation.** Predictors are functions of bars ≤ t; targets are functions
   of bars > t; an embargo gap separates them (label spec §5). Asserted by test in §6.
2. **Train-only fitting.** Scaler, HMM params, clustering, calibration map, and all percentile
   thresholds are fit on TRAIN of the current fold only, frozen, then applied to validation/test.
3. **Online/filtered inference only.** Sequence models (Markov/HMM) produce predictions using only
   information available up to t; no smoothing over future bars; no re-estimation that uses test
   labels.
4. **Purge + embargo at the seam.** ≥ h-bar embargo at every train/test boundary so a training
   row's future window cannot overlap test inputs.
5. **No target back-fill.** Rows lacking a complete future window (or whose future bar is
   `unknown_or_warmup`) are dropped, never imputed.
6. **Causal predictors only.** The Stage A causal features (`phase4_specA_v1`) plus trailing-only
   derivatives; nothing from bars > t; no future return/high/low/min/max as a feature.

## 5. Metrics

### 5.1 Multiclass targets (`future_regime` 5-class, `future_trend_regime`, `future_vol_regime`)

| metric | why |
|---|---|
| accuracy | overall hit rate (interpret with caution under class imbalance) |
| balanced accuracy | corrects for imbalance across regimes |
| precision / recall / F1 (per class) | per-regime quality, esp. rare `transition` |
| macro-F1 | imbalance-robust headline for multiclass |
| confusion matrix | required alongside any accuracy figure; shows which regimes are confused |

### 5.2 Binary probability targets (`future_breakout`, `future_range`, `future_transition`, `future_no_trade`)

| metric | why |
|---|---|
| ROC-AUC | ranking quality of the probability |
| PR-AUC | preferred for imbalanced positives (rare breakouts/transitions) |
| precision / recall / F1 | at a documented, train-chosen operating threshold |
| Brier score | probability accuracy (lower is better) |
| calibration curve (reliability) | are predicted probabilities honest? required before any prob is reported as usable |

### 5.3 Per-fold reporting

Report each metric per walk-forward fold AND aggregated (mean ± dispersion across folds), so that
instability over time is visible. A model that only looks good on one fold is not accepted.

### 5.4 Baseline comparison (mandatory)

Every model is compared against (a) the persistence baseline `predict regime[t+h] = regime[t]`,
and (b) the Tier-1 rule-based transition matrix. A model that does not beat these out-of-sample
under walk-forward is reported as no-lift, not promoted.

## 6. Leakage / look-ahead test suite (must pass before any metric is trusted)

BEGIN_PSEUDOCODE
# T1 feature/label disjointness
assert max(index of any feature bar used at t) <= t
assert min(index of any label bar used at t)   >= t + 1
assert (feature window) and (label window) do not overlap, for every row and horizon

# T2 embargo at fold seam
for each walk-forward fold:
    assert last_train_label_end_index + embargo < first_test_input_index   # embargo >= h

# T3 train-only fitting
assert scaler / HMM params / clustering / calibration / vol-percentiles were fit on TRAIN only
assert these objects are FROZEN before touching validation/test

# T4 no shuffle / time order preserved
assert train timestamps < validation timestamps < test timestamps (strict)
assert no random/k-fold shuffling was applied

# T5 filtered-only inference
assert no HMM smoothed (full-sequence) posterior used as feature or prediction

# T6 isolation
assert no Phase 2 artifact used as feature/label/weight/selector
assert no Phase 3 artifact used as feature/label/weight/selector
assert no DB write occurred

# T7 slice invariance of predictors
# a predictor value at t computed on data[0:t+1] equals that computed on data[0:T+1] (T>t)
assert predictor[t] is independent of bars > t
END_PSEUDOCODE

Any failed assertion blocks reporting for that model.

## 7. Acceptance and reporting discipline

- A Stage B model is "useful" only if it beats both baselines out-of-sample, is well-calibrated
  (low Brier, near-diagonal reliability curve), and passes the §6 leakage suite — across folds,
  not on a single window.
- Predictions are PROBABILISTIC. Report probabilities with calibration; never state a
  deterministic future regime.
- Do NOT overstate accuracy: no headline metric without confusion matrix, class balance,
  calibration, and per-fold spread.
- Longer horizons (next_24, next_48) are expected to be weaker; report their degradation honestly
  rather than averaging it away.

## 8. Phase 3 usage scope and limits

- Stage B is auxiliary and supplementary; it does NOT establish that prediction improves strategy
  performance — that is a post-Phase-3 question, explicitly out of scope for Phase 4.
- Phase 3 MUST NOT use a Stage B prediction as a current-regime label or as a hybrid-eligibility
  basis. The causal Stage A `regime` from `regime_labels.csv` (joined by `usable_from_timestamp`)
  remains the sole such basis.
- Stage B never modifies the Stage A classifier, its features, or its labels.
- If Stage B is later run on data, its outputs are research artifacts under reports/ only, clearly
  marked as forecasts, with no DB write.

## 9. Isolation confirmation (Stage B)

`phase2_results_used=false`, `phase3_results_used=false`, no DB write. DB was not read this run;
schema/vocabulary were taken from the on-file Stage A deliverables (skill §16 file-based
fallback). `llm_discretion_used=false`. Stage A remains COMPLETE and untouched; Stage B is a
supplement, not a core Phase 4 result.
