# Stage B — Future Regime Prediction: Results (REAL DATA RUN)

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m. **Run:** 20260613_0558.
**Stage:** B (supplement). **Status:** EXECUTED on real data. Stage A remains COMPLETE and untouched.
**Source per-bar regime:** Stage A causal classifier `TREND_STRENGTH_ADX_EMA_SPEC` (`phase4_specA_v1`).
**Validation:** outer holdout TRAIN=2024 / TEST=2025; expanding walk-forward within 2024; embargo >= h bars at every seam; all fits TRAIN-only and frozen. **Seed:** 42.

> Stage B is AUXILIARY and PROBABILISTIC. It is NOT a Phase 3 current-regime label and is NOT proven to
> improve strategy performance (that is a post-Phase-3 question). Forecasts are never presented as a certain future.

## 0. Headline (per horizon, on the 2025 test set)

| h (bars) | minutes | best model (macro-F1) | best macro-F1 | T0 persistence macro-F1 | T1 transition macro-F1 | beats T0? | beats T1? |
|---|---|---|---|---|---|---|---|
| 3 | 15 | T3b XGBoost(cal) | 0.8135 | 0.7871 | 0.7871 | yes | yes |
| 6 | 30 | T3b XGBoost(cal) | 0.6862 | 0.6548 | 0.6015 | yes | yes |
| 12 | 60 | T3b XGBoost(cal) | 0.5338 | 0.5020 | 0.4859 | yes | yes |
| 24 | 120 | T0 persistence | 0.3536 | 0.3536 | 0.2727 | NO | yes |
| 48 | 240 | T0 persistence | 0.2507 | 0.2507 | 0.1217 | NO | yes |

Note: at h=3/6/12 the GBM (T3b XGBoost) wins on macro-F1, accuracy and Brier. At h=24/48 macro-F1 COLLAPSES
and **T0 persistence's macro-F1 beats every learned model** — the GBMs gain raw accuracy only by reverting to
the majority class `range`, which macro-F1 correctly penalizes. This long-horizon degradation is reported, not hidden.

## 1. Full metrics per horizon (2025 test, all models vs BOTH baselines)

### h = 3 bars (15 min) — test rows 105,117, train(after embargo) 105,093, embargoed 3

| model | accuracy | balanced acc | macro-F1 | Brier | transition recall | transition F1 | range recall |
|---|---|---|---|---|---|---|---|
| T0 persistence | 0.8561 | 0.7871 | 0.7871 | n/a | 0.5021 | 0.5021 | 0.8985 |
| T1 transition-matrix | 0.8561 | 0.7871 | 0.7871 | 0.2515 | 0.5021 | 0.5021 | 0.8985 |
| T2 logreg | 0.8545 | 0.8201 | 0.7922 | 0.2178 | 0.6709 | 0.5149 | 0.8866 |
| T3a LightGBM(cal) | 0.8729 | 0.7989 | 0.8079 | 0.1820 | 0.5239 | 0.5493 | 0.9439 |
| T3b XGBoost(cal) | 0.8752 | 0.8090 | 0.8135 | 0.1789 | 0.5596 | 0.5651 | 0.9394 |

### h = 6 bars (30 min) — test rows 105,114, train(after embargo) 105,090, embargoed 6

| model | accuracy | balanced acc | macro-F1 | Brier | transition recall | transition F1 | range recall |
|---|---|---|---|---|---|---|---|
| T0 persistence | 0.7535 | 0.6548 | 0.6548 | n/a | 0.2533 | 0.2533 | 0.8217 |
| T1 transition-matrix | 0.7548 | 0.6100 | 0.6015 | 0.3940 | 0.0000 | 0.0000 | 0.8511 |
| T2 logreg | 0.7465 | 0.7023 | 0.6724 | 0.3683 | 0.4996 | 0.3406 | 0.7999 |
| T3a LightGBM(cal) | 0.7796 | 0.6642 | 0.6787 | 0.3153 | 0.2421 | 0.2980 | 0.9041 |
| T3b XGBoost(cal) | 0.7838 | 0.6729 | 0.6862 | 0.3092 | 0.2535 | 0.3144 | 0.8995 |

### h = 12 bars (60 min) — test rows 105,108, train(after embargo) 105,084, embargoed 12

| model | accuracy | balanced acc | macro-F1 | Brier | transition recall | transition F1 | range recall |
|---|---|---|---|---|---|---|---|
| T0 persistence | 0.6130 | 0.5020 | 0.5020 | n/a | 0.0822 | 0.0822 | 0.7101 |
| T1 transition-matrix | 0.6262 | 0.4933 | 0.4859 | 0.5493 | 0.0000 | 0.0000 | 0.7489 |
| T2 logreg | 0.5864 | 0.5427 | 0.5086 | 0.5659 | 0.3611 | 0.2230 | 0.6884 |
| T3a LightGBM(cal) | 0.6520 | 0.5083 | 0.5227 | 0.4927 | 0.0872 | 0.1273 | 0.8798 |
| T3b XGBoost(cal) | 0.6568 | 0.5194 | 0.5338 | 0.4855 | 0.1078 | 0.1498 | 0.8702 |

### h = 24 bars (120 min) — test rows 105,096, train(after embargo) 105,072, embargoed 24

| model | accuracy | balanced acc | macro-F1 | Brier | transition recall | transition F1 | range recall |
|---|---|---|---|---|---|---|---|
| T0 persistence | 0.4546 | 0.3536 | 0.3536 | n/a | 0.0374 | 0.0374 | 0.5800 |
| T1 transition-matrix | 0.4600 | 0.3063 | 0.2727 | 0.6661 | 0.0000 | 0.0000 | 0.7726 |
| T2 logreg | 0.4072 | 0.4027 | 0.3382 | 0.7228 | 0.4240 | 0.2149 | 0.5350 |
| T3a LightGBM(cal) | 0.5075 | 0.3284 | 0.3104 | 0.6455 | 0.0459 | 0.0774 | 0.9404 |
| T3b XGBoost(cal) | 0.5116 | 0.3378 | 0.3232 | 0.6409 | 0.0748 | 0.1149 | 0.9412 |

### h = 48 bars (240 min) — test rows 105,072, train(after embargo) 105,048, embargoed 48

| model | accuracy | balanced acc | macro-F1 | Brier | transition recall | transition F1 | range recall |
|---|---|---|---|---|---|---|---|
| T0 persistence | 0.3434 | 0.2507 | 0.2507 | n/a | 0.0334 | 0.0334 | 0.4913 |
| T1 transition-matrix | 0.4371 | 0.2000 | 0.1217 | 0.7070 | 0.0000 | 0.0000 | 1.0000 |
| T2 logreg | 0.3032 | 0.2931 | 0.2417 | 0.7819 | 0.2029 | 0.1089 | 0.3896 |
| T3a LightGBM(cal) | 0.4487 | 0.2294 | 0.1741 | 0.7042 | 0.0000 | 0.0000 | 0.9781 |
| T3b XGBoost(cal) | 0.4502 | 0.2357 | 0.1826 | 0.7022 | 0.0000 | 0.0000 | 0.9696 |

Per-class detail (precision/recall/F1/support for all five classes, every model and horizon) is in
`prediction_metrics.json` under `horizons[h].metrics[tier].per_class`.

## 2. Confusion matrices (representative)

Rows = true class, columns = predicted class, order = strong_up, strong_down, transition, volatile, range.

### T3b XGBoost(cal) @ h=3

| true \\ pred | strong_up | strong_down | transition | volatile | range |
|---|---|---|---|---|---|
| strong_up | 17467 | 493 | 610 | 486 | 1609 |
| strong_down | 262 | 18143 | 954 | 539 | 1385 |
| transition | 612 | 703 | 2695 | 220 | 586 |
| volatile | 192 | 336 | 158 | 10502 | 1191 |
| range | 776 | 878 | 305 | 828 | 43187 |

### T0 persistence @ h=48

| true \\ pred | strong_up | strong_down | transition | volatile | range |
|---|---|---|---|---|---|
| strong_up | 5188 | 3351 | 902 | 2513 | 8711 |
| strong_down | 3234 | 5387 | 945 | 1976 | 9741 |
| transition | 1212 | 1135 | 161 | 433 | 1875 |
| volatile | 2410 | 3357 | 780 | 2778 | 3054 |
| range | 8608 | 8053 | 2025 | 4678 | 22565 |

### T3b XGBoost(cal) @ h=48

| true \\ pred | strong_up | strong_down | transition | volatile | range |
|---|---|---|---|---|---|
| strong_up | 78 | 105 | 0 | 1231 | 19251 |
| strong_down | 3 | 364 | 0 | 1013 | 19903 |
| transition | 18 | 117 | 0 | 212 | 4469 |
| volatile | 14 | 304 | 0 | 2329 | 9732 |
| range | 14 | 189 | 0 | 1193 | 44533 |

At h=48 both the best GBM and persistence dump most mass into `range`/the two trend classes and essentially
stop predicting `transition` (recall ~0) — long-horizon 5-class prediction is not reliable.

## 3. Calibration summary (multiclass Brier; isotonic on a train-internal chronological holdout)

| h | T3a LightGBM Brier (uncal -> cal) | T3b XGBoost Brier (uncal -> cal) |
|---|---|---|
| 3 | 0.1940 -> 0.1820 | 0.2021 -> 0.1789 |
| 6 | 0.3413 -> 0.3153 | 0.3508 -> 0.3092 |
| 12 | 0.5403 -> 0.4927 | 0.5475 -> 0.4855 |
| 24 | 0.7067 -> 0.6455 | 0.7108 -> 0.6409 |
| 48 | 0.7785 -> 0.7042 | 0.7803 -> 0.7022 |

Isotonic calibration LOWERS Brier at every horizon (probabilities are more honest after calibration).
Calibration map was fit ONLY on a chronological tail (15%) of the 2024 train block, never on 2025 test.
Absolute Brier rises steeply with horizon: the further out, the less trustworthy any probability.

## 4. Walk-forward stability inside 2024 (model selection; expanding, 4 folds)

Mean +/- pop-stdev of macro-F1 across folds (LightGBM tracked uncalibrated in WF for speed; calibration is a
holdout-only step). Stability across folds confirms the 2025 holdout is not a single lucky window.

| h | T0 persistence | T1 transition | T2 logreg | T3a LightGBM |
|---|---|---|---|---|
| 3 | 0.788 +/- 0.001 | 0.788 +/- 0.001 | 0.795 +/- 0.003 | 0.796 +/- 0.003 |
| 6 | 0.653 +/- 0.004 | 0.599 +/- 0.002 | 0.672 +/- 0.006 | 0.671 +/- 0.011 |
| 12 | 0.492 +/- 0.005 | 0.477 +/- 0.003 | 0.509 +/- 0.009 | 0.508 +/- 0.013 |
| 24 | 0.346 +/- 0.017 | 0.290 +/- 0.025 | 0.336 +/- 0.008 | 0.340 +/- 0.007 |
| 48 | 0.255 +/- 0.019 | 0.126 +/- 0.001 | 0.235 +/- 0.006 | 0.238 +/- 0.004 |

## 5. Tier-1 empirical transition matrix (estimated on the 2024 TRAIN fold ONLY, h=3)

This is NOT the Stage A whole-data descriptive matrix (that would leak the 2025 test year). It is re-estimated
on train rows only and frozen. P(regime[t+3] = col | regime[t] = row):

| from \\ to | strong_up | strong_down | transition | volatile | range |
|---|---|---|---|---|---|
| strong_up | 0.856 | 0.001 | 0.042 | 0.028 | 0.073 |
| strong_down | 0.001 | 0.864 | 0.053 | 0.025 | 0.058 |
| transition | 0.081 | 0.104 | 0.518 | 0.097 | 0.201 |
| volatile | 0.046 | 0.053 | 0.010 | 0.800 | 0.090 |
| range | 0.036 | 0.036 | 0.005 | 0.020 | 0.903 |

Persistence dominates the diagonal (e.g. range->range 0.903, strong_up->strong_up 0.856), which is exactly why
the trivial persistence baseline is so hard to beat and why argmax of this matrix degenerates to persistence at
short h and to `range` at long h (transition recall -> 0).

## 6. Leakage / look-ahead test suite (T1-T7) — results

| test | meaning | result |
|---|---|---|
| T1 feature/label disjointness | label not in features; no future-named feature col; label=regime[t+h] aligned (asserted in build) | PASS (True / True) |
| T2 embargo at seam | >= h bars removed at 2024/2025 seam and every WF fold (asserted in code) | PASS (True) |
| T3 train-only fitting | scaler, transition matrix, calibration all fit on TRAIN slices, frozen forward | PASS (True) |
| T4 time order preserved | train ts < test ts (asserted); no shuffle/k-fold | PASS (True) |
| T5 filtered-only inference | no HMM smoothed/full-sequence posterior used (no HMM in this run) | PASS (True) |
| T6 isolation | no Phase 2 / Phase 3 artifact; no DB write | PASS (p2=False, p3=False, dbwrite=False) |
| T7 predictor slice-invariance | rolling feature at t equals prefix recompute (independent of bars > t) | PASS (True) |

All assertions are in `build_prediction_labels.py` (T1 alignment, T7 slice-invariance) and
`train_predict_regime.py` (T2 seam embargo, T4 time order, T3 train-only fits). The run completed without an
assertion failure, so every metric above is admissible. Embargoed train-row counts per horizon (3/6/12/24/48 rows)
appear in section 1 and in `prediction_metrics.json`.

## 7. Honest longer-horizon degradation

- Median regime durations (Stage A): strong_up ~14, strong_down ~15, volatile ~6, transition ~4, range ~18 bars.
- A 5-class prediction at h=24 (120 min) or h=48 (240 min) reaches well past the median life of trend/volatile/
  transition regimes, so the conditional distribution flattens toward the unconditional one.
- Result: at h>=24, learned models lose to trivial persistence on macro-F1, and `transition` becomes nearly
  unpredictable (recall ~0 for persistence/transition-matrix/GBM; only the balanced logreg keeps non-trivial but
  low-precision recall). We DO NOT average this away or promote the higher raw accuracy of the GBM at long h.
- Usable signal exists at h=3 and h=6 (15-30 min): T3b XGBoost beats both baselines on macro-F1 and Brier with
  stable walk-forward folds. h=12 is marginal-positive. h=24/48 are reported as no-lift / negative-lift.

## 8. Limitations

- The label is itself a Stage A causal classifier output, not ground-truth market state; Stage B predicts the
  FUTURE VALUE of that classifier, inheriting its definition and any of its noise.
- Single outer holdout (one 2025 test year). Walk-forward inside 2024 is the stability evidence; a single test
  regime epoch could still differ from future epochs. Predictions are probabilistic, not deterministic.
- Features are intentionally lean (Stage A causal regime + scores + short causal lags/deltas/rolls). Richer causal
  OHLCV/derivatives features were not added; the gain over persistence at short h is modest.
- Brier rises sharply with horizon; long-horizon probabilities are weakly calibrated in absolute terms.
- No hyperparameter search was tuned to the test set; defaults documented in `train_predict_regime.py`.

## 9. Phase 3 usage scope and limits

- Stage B outputs are RESEARCH artifacts under reports/ only, clearly marked as forecasts. No DB write.
- Phase 3 MUST NOT use any Stage B prediction as a current-regime label or as a hybrid-eligibility basis. The
  sole current-regime basis remains the causal Stage A `regime` in `regime_labels.csv` joined by
  `usable_from_timestamp`.
- A Stage B forecast (e.g. `future_regime_probability` at h=3/6) may be consumed only as an AUXILIARY,
  probabilistic risk/abstain signal, and only with its calibration and the baseline comparison shown above.
- Stage B is a SUPPLEMENT; Stage A completion is the core Phase 4 result. Stage B does not establish that
  prediction improves strategy performance — that is explicitly post-Phase-3 and out of scope here.

## 9b. Forecast artifact (the Phase-3-consumable per-row output)

The study now emits an actual per-row forecast, not just aggregate metrics. For each horizon
h in {3, 6, 12, 24, 48} the final **2024-trained, isotonic-calibrated XGBoost** predicts the
**2025 out-of-sample test set** and writes `regime_forecast_h{h}.csv.gz` (gzip; same byte-
reproducible writer as the matrices). No in-sample 2024 forecasts are emitted (they would be
overfit). Scope is 2025 OOS only.

Columns: `timestamp` (bar t), `prediction_usable_from_timestamp`, `horizon_bars`,
`target_timestamp` (= t + h*5min), the five CALIBRATED class probabilities
`p_strong_up, p_strong_down, p_transition, p_volatile, p_range` (rounded to 6 dp),
`predicted_regime` (argmax), `realized_regime` (= regime[t+h] from `regime_labels.csv`, reference
only — this is historical 2025 data), `model_version` (`phase4_specB_xgb_isotonic_v1`),
`source_classifier_version` (`phase4_specA_v1`).

**One-bar usability rule.** `prediction_usable_from_timestamp` = `timestamp` + 5min, i.e. the
forecast for bar t is usable only AFTER bar t closes — the SAME one-bar rule as the Stage A
causal label. This is enforced in code (assert) and verified: `prediction_usable_from_timestamp`
is strictly greater than `timestamp` on every row of every horizon. It prevents a one-bar-
lookahead misread (treating a forecast keyed at bar t as if it were known at or before t).

**Consistency.** The probabilities are EXACTLY the calibrated T3b probabilities used in
`prediction_metrics.json`; verified by recomputing argmax accuracy from the forecast file and
matching it bit-for-bit to the metrics `T3b_xgboost.accuracy` at every horizon.

Per-file size and sha256 are recorded in `prediction_provenance.json` under
`forecast_artifact.files` (committed=true, regenerable=true). These files **are committed** (~13MB).

**Usage scope (re-emphasized).** This forecast is AUXILIARY and PROBABILISTIC. It is NEVER a
Phase 3 current-regime label and NEVER a hybrid-eligibility basis; the sole current-regime basis
remains the causal Stage A `regime`. A forecast may be consumed only as a probabilistic
risk/abstain signal, with its calibration and baseline comparison (sections 0-3) in view, and at
long horizons (h>=24) it carries no lift over trivial persistence on macro-F1.

## 10. Reproduction

BEGIN_JSON
{
  "build": "python build_prediction_labels.py --labels regime_labels.csv --outdir . --horizons 3,6,12,24,48",
  "train": "python train_predict_regime.py --features . --outdir . --seed 42 --horizons 3,6,12,24,48",
  "seed": 42,
  "python": "/home/vessel/workspace/trading-system/.venv/bin/python",
  "metrics_file": "prediction_metrics.json",
  "provenance_file": "prediction_provenance.json",
  "forecast_files": "regime_forecast_h{3,6,12,24,48}.csv.gz",
  "matrices_byte_reproducible": "yes (gzip mtime=0, empty FNAME; two regenerations produce identical sha256)",
  "forecasts_cross_platform_bit_identical": "no (XGBoost output; byte-identical same-arch only; cross-platform metrics match ~3 decimals, not bit-exact)"
}
END_JSON

Note: the gzip CONTAINER is byte-reproducible (mtime=0 + empty FNAME). The
`prediction_matrix_*.csv.gz` (rule-based, derived only from `regime_labels.csv`) regenerate
byte-identically — verified vs the provenance sha256, including by an external reviewer on a
different machine — and are **gitignored** (~72MB, regenerable). The `regime_forecast_*.csv.gz`
are **committed** (~13MB) but are XGBoost output: byte-identical only on the same OS/architecture;
cross-platform the T3b numbers can differ ~1e-3 (see REPRODUCE.md "Determinism notes"). The
reproducibility anchors are the input/label sha256 + metrics-to-tolerance, not the forecast bytes
across machines.
