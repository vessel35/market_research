# Framework families, candidate-record schema, scoring, and feature catalog (Phase 4 reference)

Loaded on demand by the regime-classification skill. The SKILL.md holds the contract; this file
holds the survey detail.

## A. The five theory-grounded framework families

Survey ALL five and record a select/reject reason for each — even families you will not pick.

### A.1 Trend-strength
Theory: ADX / DMI trend-strength classification; moving-average alignment / slope for direction.
Idea: a trend exists when ADX (or a similar strength gauge) is high; direction comes from EMA/SMA
alignment or price-vs-MA position; low ADX means range / low-directional, not a trend. Repository
relevance: highest — the SPEC canonical regime is built on ADX(14) + EMA9/21/55, so this family
maps most directly. Causal: strong (all indicators computable on bars <= t with shift).

### A.2 Volatility regime
Theory: ATR percentile, realized-volatility percentile, Bollinger-band width, volatility
clustering, compression vs expansion. Idea: classify by volatility LEVEL rather than direction.
Caveat: volatility alone cannot define strong_up / strong_down (it has no direction); as a
primary it would need a direction theory bolted on, which risks mixing — so prefer it as the
auxiliary feature that splits volatile vs range, not as the primary.

### A.3 Price-action / market-structure
Theory: Dow theory, higher-high/higher-low, lower-high/lower-low, swing structure,
support/resistance break-and-retest. Idea: up-structure = HH/HL, down-structure = LH/LL, range =
inside a swing band. Caveat: pivots need confirmation delay; real-time you cannot know a swing is
final until later; ZigZag / hindsight pivots leak. Primary only with an explicit causal
pivot-confirmation rule.

### A.4 Statistical (latent-state)
Theory: Hidden Markov Model, Markov regime-switching, Gaussian mixture, return/volatility-state
clustering. Idea: estimate regimes as latent states or distributional clusters; transition
probabilities are modelable. Caveat: interpretability can be low; train/test split, scaler fit,
and clustering fit all leak if fit on whole data. Primary only with train-only fit, walk-forward
validation, and demonstrated label stability.

### A.5 Session / liquidity
Theory: time-of-day effect, session volatility, funding-time proximity, liquidity/spread proxy,
volume regime. Idea: crypto-perp state shifts with hour, liquidity, funding schedule, and volume.
Caveat: this describes the trading ENVIRONMENT more than the price regime; better as a no-trade
filter or a secondary annotation than as the primary market regime.

## B. Candidate-record schema (one per surveyed framework)

BEGIN_JSON
{
  "candidate_framework_id": "",
  "framework_name": "",
  "theoretical_basis": "",
  "source_type": "repository_spec | repository_code | technical_analysis_theory | academic_public | public_documentation | open_source",
  "source_reference": "",
  "core_market_assumption": "",
  "regime_definitions": [],
  "required_features": [],
  "required_data": [],
  "optional_data": [],
  "causal_implementation_possible": true,
  "lookahead_bias_risks": [],
  "real_time_availability": "",
  "mapping_to_spec_canonical_regimes": {},
  "strengths": [],
  "weaknesses": [],
  "fit_for_ethusdt_5m": "high | medium | low",
  "fit_for_phase3_analysis": "high | medium | low",
  "complexity": "low | medium | high",
  "interpretability": "high | medium | low",
  "selected_as_primary": false,
  "rejection_reason": "",
  "notes": ""
}
END_JSON

## C. Selection-matrix CSV columns

`candidate_framework_id`, `framework_name`, `theoretical_basis_strength`,
`repository_spec_alignment`, `causal_safety`, `interpretability`, `data_availability`,
`implementation_complexity`, `phase3_join_usability`, `weighted_score`, `selected_as_primary`,
`rejection_reason`.

Weights: theoretical_basis_strength 0.20, repository_spec_alignment 0.20, causal_safety 0.20,
interpretability 0.15, data_availability 0.10, implementation_complexity 0.10,
phase3_join_usability 0.05. Hard gates override the weighted score: low causal_safety, very low
repository_spec_alignment, or weak theoretical basis disqualify a candidate from being primary.

## D. regime_feature_catalog.csv columns

`feature_id`, `feature_name`, `category`, `formula`, `lookback`, `required_columns`,
`optional_columns`, `causal_safe`, `usable_from_rule`, `purpose`, `candidate_frameworks`,
`selected_framework_feature`, `regime_related`, `prediction_related`, `lookahead_risk`,
`implementation_status`, `priority`.

The final classifier includes ONLY features with `selected_framework_feature=true`. The catalog
is a survey list, not a license to feed every feature into one classifier.

## E. Feature categories (survey inventory)

- **trend:** EMA9/21/55, EMA alignment/slope/spread, ADX(14), +DI/-DI, MACD histogram, rolling
  return, trend persistence, HH/LL count, linear-regression slope.
- **volatility:** ATR(14), ATR percentile, realized vol, Bollinger width, high-low range
  percentile, expansion ratio, compression score, Parkinson, Garman-Klass.
- **momentum:** ROC, RSI, Stochastic RSI, MACD acceleration, candle momentum, consecutive-candle
  count.
- **mean-reversion:** Bollinger z-score, price-distance-from-EMA, return z-score, wick ratio,
  overextension, RSI-extreme.
- **volume:** volume z-score/percentile, expansion ratio, OBV slope, MFI, volume-price
  divergence.
- **microstructure proxy (optional data only):** OI change, funding rate, taker buy/sell
  imbalance, bid-ask spread, liquidation imbalance.
- **time:** hour-of-day, day-of-week, funding-interval proximity, session effect.

Every feature records `causal_safe` and `usable_from_rule`. A feature that is not causal-safe is
not eligible for the causal classifier.

## F. Stage B horizons, targets, models, validation (optional layer)

- Horizons: next_3 (15m), next_6 (30m), next_12 (1h), next_24 (2h), next_48 (4h) bars.
- Targets: future_regime, future_trend_regime, future_volatility_regime,
  future_breakout/range/transition/no_trade probability.
- Labels are training targets only, time-separated from features (a future label is never a
  current feature).
- Models, priority order: rule-based transition matrix → statistical (logistic / multinomial /
  Markov / HMM) → ML (RandomForest / GradientBoosting / XGBoost-or-LightGBM if available).
  LSTM / Transformer / RL are deprioritized (data hunger, overfitting, low interpretability,
  costly walk-forward).
- Validation: train/val/test time split, walk-forward, expanding-window, or rolling-window only.
  Forbidden: random/shuffle split, test-set threshold tuning, whole-data scaler or clustering
  fit, any Phase 2 result as label/feature.
- Metrics: accuracy, balanced accuracy, precision, recall, F1, macro-F1, confusion matrix,
  ROC-AUC (binary), PR-AUC (imbalanced), Brier score, calibration curve.

Unsupervised detection (K-means / GMM / HDBSCAN / HMM / PCA+clustering) is research-only: fit on
train only, transform/predict elsewhere, never replace the canonical regimes — record clusters as
`experimental_regime_candidate` in a separate file.
