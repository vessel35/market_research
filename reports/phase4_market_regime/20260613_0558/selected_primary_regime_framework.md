# Selected Primary Regime Framework

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m · **Run:** 20260613_0558
**Mode:** SPEC-ONLY (no data; labels waived). Theory-grounded; `llm_discretion_used=false`.

## 1. Selected framework

**Repository-defined trend-strength framework** — candidate id
`TREND_STRENGTH_ADX_EMA_SPEC`: ADX(14) as the trend-strength gate, EMA9/21/55 alignment as the
direction signal, and a causal ATR(14) percentile as the volatility split for the no-trend
bucket. Weighted selection score **4.850** (highest of 17 candidates).

## 2. Selection reason

Highest weighted score and clears every hard gate. It is the only surveyed framework that is
simultaneously (a) directional (can express `strong_up`/`strong_down`, unlike the volatility and
session families), (b) fully causal with no model fit (unlike the statistical family, which is
also un-trainable in this no-data run), and (c) a 1:1 match to the SPEC canonical vocabulary
(unlike price-action, which needs an auxiliary volatility feature and carries pivot-lag
look-ahead traps). Next-best was Dow swing structure (4.050), kept as future research. This is the
best fit **for the selection rubric and current constraints** (causal, OHLCV-only, interpretable,
Phase-3-join) — **not a proven statistical optimum**; alternatives (Dow structure, HMM/Markov
switching, volatility-state models) should be compared empirically once data is available.

## 3. Theoretical basis

- **Trend strength — ADX/DMI (Wilder 1978):** directional movement (+DM, −DM) smoothed against
  True Range yields +DI/−DI; their normalized divergence (DX), Wilder-smoothed over 14, is ADX.
  ADX rises in any persistent trend and falls in directionless markets. The ADX≥25 "strong
  trend" cutoff is a common TA convention and the repository/SPEC value — Wilder grounds the ADX
  trend-strength *concept*, but the specific 25 is convention, not a Wilder-derived constant.
- **Direction — multi-EMA alignment:** EMA9>EMA21>EMA55 = uniformly bullish multi-horizon
  structure; the reverse = bearish. Moving-average *alignment* is a standard trend-following
  technique; the specific 9/21/55 periods are repository/SPEC-defined, not from a named author's
  system.
- **Volatility split — volatility clustering (Mandelbrot 1963; Engle 1982 ARCH):** within the
  no-trend bucket, ATR percentile separates a high-volatility (choppy) state from a quiet range.
  Mandelbrot grounds non-normality/fat-tails (large changes tend to follow large changes); Engle
  ARCH grounds conditional (past-dependent) volatility. Neither *derives* the P70 cutoff — P70 is
  a design convention.

**Grounding-strength tiers (be precise):** ADX/DMI trend strength = **strong** (Wilder, an
established method); multi-EMA *alignment* for direction = **standard practitioner** technique;
the volatility-split *concept* is theory-grounded, but its **P70 cutoff and the 9/21/55 and
ADX-25 parameters are repository/SPEC conventions**, not academically-derived optima. The
selection `theoretical_basis_strength` score reflects the *methods'* grounding; the specific
parameter values remain conventions to be profiled against data (never tuned to performance).

Combining a strength gate with a direction signal is the **repository-defined** design (skill §3),
not arbitrary mixing.

## 4. Why it fits this project

- **ETH/USDT 5m:** OHLCV-only, deterministic, reproducible; robust 24/7 (no session assumption).
- **Phase 3:** emits one canonical enum + a confidence per bar with a clean `usable_from_timestamp`,
  trivially join-able to trade entry/exit timestamps.
- **SPEC:** it *is* the canonical framework; maximal alignment and zero translation loss.

## 5. SPEC canonical mapping (1:1)

| canonical regime | framework rule |
|---|---|
| strong_up | ADX(14) ≥ 25 AND EMA9 > EMA21 > EMA55 |
| strong_down | ADX(14) ≥ 25 AND EMA9 < EMA21 < EMA55 |
| transition | ADX(14) ≥ 25 AND EMA alignment is neither strictly up nor strictly down |
| volatile | ADX(14) < 25 AND volatility_score is high (ATR percentile ≥ P70) |
| range | ADX(14) < 25 AND volatility_score is not high (ATR percentile < P70) |

`all` is not produced — it is the Phase 3 unconditional-aggregation bucket only.

## 6. Features used (classifier inputs; all bars ≤ t)

EMA9, EMA21, EMA55 (close); ADX(14) (from +DM/−DM/TR with Wilder smoothing); ATR(14);
`volatility_score` = trailing rolling percentile rank of ATR(14) over a causal window. These are
the only features flagged `selected_framework_feature=true` in `regime_feature_catalog.csv`.

## 7. Features deliberately NOT used

+DI/−DI as the direction signal (SPEC uses EMA alignment); Bollinger/Keltner, Parkinson/GK,
realized-vol (alternative volatility estimators — ATR percentile is sufficient and SPEC-aligned);
RSI/MACD/Stochastic momentum; mean-reversion z-scores; volume/OBV/MFI; HMM/GMM/cluster states;
session/funding/microstructure features. These are catalogued (`selected_framework_feature=false`)
for the survey but **excluded from the classifier** to honor the no-mixing principle.

## 8. Threshold policy

Priority per skill §15 / prompt §21.4: SPEC/existing-code → train-period percentile →
walk-forward rolling percentile → fixed convention/theory. This is a methodology-only phase (no
separate SPEC.md/code is required) and no data is loaded, so we fall to **fixed convention/SPEC
values** (to be profiled against the data distribution later, never tuned to performance):

- **ADX trend gate = 25** — repository/SPEC value and a common TA convention for a strong trend
  (Wilder grounds the ADX trend-strength concept; 25 is convention, not a derived constant). To be
  profiled against the ETH/USDT 5m ADX distribution when data is present (never tuned to performance).
- **Volatility-high cutoff = 70th percentile (P70)** — documented convention; applied to a
  **causal trailing percentile** of ATR(14) (a rolling online statistic over bars ≤ t, window
  default W=2016 bars ≈ 7 days; expanding from data start until W is reached).
- The P70 cutoff is a fixed convention, **not** a train-only model fit and **not** tuned to any
  performance. No threshold is derived from Phase 2/3 results or a test set. When data becomes
  available, the P70 percentile may be re-confirmed against the train period only (never the test
  set); the cutoff value itself is not changed to improve any strategy's edge.

## 9. Causal implementation rule

For each bar t, compute EMA/ADX/ATR and `volatility_score` from bars ≤ t only; apply the §5
rules; set `usable_from_timestamp[t] = timestamp[t] + 5min` (next bar open) because the label
uses bar-t close. Live and backtest use the identical function. Full detail in
`causal_regime_classifier_spec.md`.

## 10. Look-ahead prevention rules

No future return/high/low/min/max in any feature; no centered windows; ATR percentile uses a
**trailing** window only (never whole-sample); the label for bar t is usable only from bar t+1;
warmup bars (until ADX/EMA stabilize) are flagged, not back-filled; smoothed/posthoc labels (if
ever produced) live in separate files. Independently reviewed by `causal-auditor`.

## 11. Limitations

- ADX lag and 20–25 gray-zone can flicker labels at 5m (a documented hysteresis option exists but
  is not in the SPEC; not added to avoid altering the canonical rule).
- **Short-intraday horizon only:** at 5m, EMA9/21/55 ≈ 45 / 105 / 275 min (EMA55 ≈ 4.6h) and the
  volatility window W=2016 ≈ 7 days. The classifier captures the short-intraday regime; it does
  not see higher-timeframe market context (a future multi-timeframe extension could anchor 5m
  labels within causal 1h/4h structure).
- The volatility split needs a trailing percentile that requires accumulated history to be
  meaningful; cold-start bars are low-confidence/warmup.
- **Methodology-only phase:** `regime_labels.csv` and data-quality checks are out of scope
  (data-dependent artifacts), not deficiencies; thresholds are fixed convention/SPEC values and would
  be confirmed against train data (never tuned to performance) in a later data-present run.
  SPEC.md is not required — the `regime-classification` skill is the canonical source by design;
  the existing-classifier-vs-SPEC discrepancy check is not applicable (no existing classifier).

## 12. Rejected alternatives held for future research

- **Dow swing structure (PA_MS_001)** — leading next-best; revisit with a causal pivot-confirmation
  rule and multi-timeframe anchoring.
- **TTM Squeeze / ATR-percentile** — preferred alternative *implementations* of the volatility
  split if ATR percentile proves noisy.
- **Hamilton MS / HMM** — only with data, a train-only forward-filter fit, walk-forward validation,
  and a stable latent→canonical mapping (record as `experimental_regime_candidate`).
- **Session / funding-proximity** — Phase 3 secondary annotation / no-trade filter (not a regime).
