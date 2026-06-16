# Regime Prediction Research (Stage B — Executed)

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m · **Run:** 20260613_0558
**Stage:** B (optional future-regime prediction). **Status:** EXECUTED on real ETH/USDT 5m labels
(2026-06-14) — empirical results in `regime_prediction_results.md`.
**Built on top of:** Stage A current-regime classifier `TREND_STRENGTH_ADX_EMA_SPEC`
(classifier version `phase4_specA_v1`), which is COMPLETE and is NOT modified by this stage.

> EXECUTED on real data: future-regime labels were built from the Stage A `regime_labels.csv`
> (210,227 labeled bars, 2024–2025) and models were trained + walk-forward validated
> (train 2024 / test 2025). Empirical metrics are in `regime_prediction_results.md`. All forecasts
> are probabilistic and auxiliary — never a Phase 3 current-regime label. No Phase 2/3 result used.

**Executed scope (this run):** only the primary target `label_future_regime` (5-class) was trained
and evaluated. The other designed targets below — `future_trend_regime`, `future_volatility_regime`,
`future_breakout`, `future_range/transition/no_trade_probability` — remain **designed-but-not-executed**
(future work). They are kept in this document as the design, not as executed results.

## 1. What Stage B is (and is not)

Stage A answers "what regime is it NOW?" using only bars ≤ t (causal). Stage B is a separate,
*supplementary* research layer that asks "what is the probability of each regime over the next
h bars?". It is auxiliary and probabilistic. It:

- NEVER replaces the Stage A causal classifier; the causal label remains the only Phase 3
  hybrid-eligibility basis.
- NEVER feeds a predicted/future value back into the current-regime features.
- Is NOT a core Phase 4 deliverable — Phase 4's core objective (Stage A) is already met. Stage B
  is a supplement; its presence or accuracy does not change Stage A completion status.
- Does NOT conclude that prediction improves strategy performance. Whether a regime forecast
  helps a strategy is a post-Phase-3 question and is out of scope here.

## 2. Strict separation: features vs. labels (the central rule)

Time `t` is the decision bar. There are two disjoint time regions:

- **Features (predictors):** computed ONLY from bars ≤ t. These are exactly the Stage A causal
  features — `EMA9`, `EMA21`, `EMA55`, `ema_alignment_state`, `ADX14`, `ATR14`,
  `volatility_score` (ATR percentile) — plus, optionally, the current Stage A `regime[t]` and
  `regime_confidence[t]` (themselves causal, bars ≤ t), and causal derived features (recent
  regime dwell time, recent transition counts, ATR-percentile trend, Bollinger/Keltner width as
  trailing values). All predictors satisfy `usable_from_timestamp ≤ t+1`.
- **Labels (targets):** derived ONLY from bars > t (specifically the Stage A causal label at
  `t+h` and realized statistics over `(t, t+h]`). Labels are SUPERVISED TARGETS ONLY. They are
  never read back as a current feature, never written into `regime_labels.csv`, and never used as
  a Phase 3 current-regime label.

A future regime/return/high/low/min/max is ALWAYS a label, NEVER a feature. There is a clean
boundary at t: predictors stop at t, targets start after t. See
`regime_prediction_label_spec.md` for exact construction and the warmup/embargo gap.

## 3. Prediction horizons

5m bars. Horizons are forward-looking target offsets only (they define the label, never a
feature window):

| horizon id | bars ahead (h) | wall-clock | rationale |
|---|---|---|---|
| next_3 | 3 | 15m | very-short-term persistence / immediate continuation |
| next_6 | 6 | 30m | short-term regime stability |
| next_12 | 12 | 1h | intraday regime turnover |
| next_24 | 24 | 2h | session-scale regime shift |
| next_48 | 48 | 4h | multi-hour regime outlook (highest noise / lowest reliability) |

Each horizon is a separate prediction task with its own labels and its own model fit. Longer
horizons are expected (a priori, not measured) to be harder and must not be presented as
reliable; report calibration, not just accuracy.

## 4. Prediction targets

All targets are defined formally in `regime_prediction_label_spec.md`. Summary:

| target | type | meaning (over horizon h) |
|---|---|---|
| `future_regime` | multiclass (5) | Stage A causal regime at t+h |
| `future_trend_regime` | multiclass (3) | trend collapse of regime at t+h: {trending(strong_up/strong_down/transition), non_trending(volatile/range), —} |
| `future_volatility_regime` | multiclass (3) | realized-vol bucket over (t,t+h]: {high, normal, low} by TRAIN-ONLY percentile |
| `future_breakout_probability` | binary prob | P(a breakout event occurs within (t,t+h]) |
| `future_range_probability` | binary prob | P(regime at t+h is `range`) / P(ranging persists) |
| `future_transition_probability` | binary prob | P(regime at t+h is `transition`) |
| `future_no_trade_probability` | binary prob | P(t+h regime ∈ no-trade set {volatile, transition}) — a *risk/abstain* signal, NOT a strategy-performance label |

`future_no_trade_probability` is defined purely from the regime vocabulary (which regimes are
structurally hostile to clean execution), NOT from any Phase 2/3 outcome. It is a regime-shape
signal, never "strategy X lost money."

## 5. Model candidates (ranked, with rationale)

Ranked from most-recommended baseline to deprioritized. ALL are walk-forward only (see
`regime_prediction_validation_plan.md`); none is fit on the whole dataset.

### 5.1 Tier 1 — Rule-based transition model (RECOMMENDED FIRST BASELINE)

The first thing to build, because it is fully interpretable, leak-resistant by construction, and
sets the bar every later model must beat. It is a small set of theory-grounded rules over the
*current* Stage A state:

- **First-order regime transition matrix.** Estimate, on TRAIN data only, the empirical
  `P(regime[t+h] = j | regime[t] = i)` for each horizon h. Prediction at t = the row of the
  matrix for the current regime. This is a Markov persistence baseline.
- **Trend-persistence rule.** If `regime[t]` ∈ {strong_up, strong_down} with high
  `regime_confidence` and rising/stable ADX, assign elevated probability that the same trend
  regime persists at t+h (trends auto-correlate at short horizons). Persistence probability
  decays with h.
- **Compression → expansion rule.** If current `volatility_score` is low and falling (range with
  tightening ATR percentile), raise `future_breakout_probability` / `future_volatility_regime=high`
  for the horizon (volatility-clustering / squeeze theory). Causal: uses only trailing ATR
  percentile.
- **Overextension → reversal/transition rule.** If a strong trend has run for a long causal dwell
  with ADX rolling over (ADX falling from a high level while EMA spread narrows), raise
  `future_transition_probability`. Uses only bars ≤ t.

Each rule emits a probability, not a hard class. Rules are combined by a fixed, documented scheme
(e.g. transition matrix as the prior, the three structural rules as bounded adjustments), never
by a weight tuned to Phase 2/3 outcomes.

#### Transition-matrix baseline (real, train-fold estimated)

The Tier-1 baseline is the empirical transition matrix P(regime[t+h] | regime[t]). For
VALIDATION it is estimated on the TRAIN window only (per fold), never on the test window or the
whole sample. The Stage A whole-data descriptive matrix is `regime_transition_matrix.csv`
(empirical persistence ≈ 0.95 on the diagonal for trend/range regimes, ≈ 0.80 for `transition`);
that file is descriptive only and is NOT used as the validated baseline (using it would leak the
2025 test year). Executed results vs this baseline (and vs Tier-0 persistence) are in
`regime_prediction_results.md`.

### 5.2 Tier 2 — Classical statistical models

- **Multinomial logistic regression** for `future_regime` (5-class); **binary logistic** for the
  probability targets. Interpretable coefficients, naturally calibrated, cheap to refit each fold.
- **Markov / higher-order Markov transition model.** Generalizes the Tier-1 matrix; can condition
  on (regime, volatility bucket) joint states.
- **Hidden Markov Model (HMM) / regime-switching.** Fit EMISSION + TRANSITION params on TRAIN
  only; at inference use FILTERED (online, left-to-right) state probabilities — never the
  smoothed (full-sequence) posterior, which peeks at future bars. The smoothed posterior is
  look-ahead and is FORBIDDEN as a feature or label. HMM here predicts the *latent* state forward;
  its states must be mapped to the canonical vocabulary, not invented.

### 5.3 Tier 3 — Tree-ensemble ML

- **Random forest**, **gradient boosting**, **XGBoost / LightGBM** on the causal feature set for
  the multiclass and binary targets.
- **Calibrated classifier.** Wrap any ML model in isotonic / Platt calibration FIT ON A TRAIN-ONLY
  calibration fold (never the test set), because downstream use needs honest probabilities, not
  just argmax labels. Report Brier score and calibration curves.
- Class imbalance (rare regimes such as transition) handled by class weights / focal loss /
  PR-AUC-oriented evaluation — never by resampling that crosses the train/test time boundary.

### 5.4 Deprioritized — sequence/deep/RL models

| model | deprioritized because |
|---|---|
| LSTM / GRU | data-hungry; high overfit risk on a single 5m series; expensive to refit per walk-forward fold; low interpretability vs. the rule baseline; marginal benefit unlikely to be demonstrable without large data |
| Transformer | even more data-hungry and compute-heavy; attention offers little over engineered causal features at this horizon; opaque; walk-forward refit cost is high |
| Reinforcement learning | conflates prediction with policy/reward — couples to performance, which violates isolation (reward would implicitly encode Phase 2/3-style outcomes); not a clean supervised forecast; very hard to validate without leakage |

These are recorded as future research, contingent on (a) far more data, (b) a demonstrated lift
of Tier 1–3 over the rule baseline, and (c) a leakage-proof reward/label that does not use Phase
2/3 results. They are NOT to be built first.

## 6. Recommended build order

1. Rule-based transition matrix + structural rules (Tier 1) — establish the interpretable
   baseline and the persistence floor.
2. Multinomial / binary logistic (Tier 2) — first statistical lift, calibrated by construction.
3. Markov / HMM (filtered only) — sequence-aware baseline.
4. Tree ensembles + calibration (Tier 3) — only if they beat Tier 1–2 out-of-sample under
   walk-forward, with honest calibration.
5. Deep/RL — only if §5.4 preconditions are met.

Every step is judged by walk-forward out-of-sample metrics AND calibration, and every step must
clear the rule baseline before it is taken seriously.

## 7. Feature engineering constraints (causal-only)

- Permitted predictors: Stage A causal features (bars ≤ t); current Stage A `regime[t]` /
  `regime_confidence[t]`; trailing-only derived features (regime dwell length so far, count of
  transitions in the last N bars, ATR-percentile slope, trailing Bollinger/Keltner width,
  trailing return/vol stats over bars ≤ t). Optional causal derivatives (funding, OI,
  taker-imbalance) only as trailing values with a correct `usable_from_timestamp`.
- Forbidden predictors: ANY value computed from bars > t; the future label itself; future return /
  future high / low / min / max; the HMM smoothed (full-sequence) posterior; any centered/rolling
  window that includes future bars; any Phase 2 artifact (result.json, trades.csv, portfolio.csv,
  signals.csv, per-strategy return/PF/MDD/Sharpe); any Phase 3 artifact (edge_fragment,
  strategy_evaluation).

## 8. Outputs and Phase 3 usage scope

- Stage B outputs are research artifacts under reports/ only: `regime_prediction_results.md` +
  `prediction_metrics.json` (executed metrics), the per-(t,horizon) feature/label matrices
  (`prediction_matrix_h{h}.csv.gz`, regenerable/gitignored), the per-row calibrated forecast
  artifact (2025 OOS), and this trio of design docs. All clearly marked as forecasts.
- Phase 3 MUST NOT use a Stage B prediction as a current-regime label, nor as a
  hybrid-eligibility basis. The causal Stage A label is the only such basis.
- Predictions are PROBABILISTIC and must be reported with calibration; they are never presented
  as a certain future. No deterministic "the next regime WILL be X" statements.
- Do NOT overstate accuracy. Any headline number without its confusion matrix, class balance,
  calibration curve, and walk-forward fold spread is not a valid claim.

## 9. Isolation confirmation (Stage B)

`phase2_results_used=false`, `phase3_results_used=false`. No DB write occurred or is implied
(DB is read-only and optional; this run made no DB read — schema is taken from the Stage A
deliverables on file, per skill §16 file-based fallback). The Stage A classifier and its labels
are untouched. `llm_discretion_used=false`: every label/target is mechanically defined, with no
LLM "this looks like" judgment.
