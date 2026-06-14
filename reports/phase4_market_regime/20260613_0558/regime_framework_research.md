# Regime Framework Research — Phase 4 Stage A

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m
**Run:** reports/phase4_market_regime/20260613_0558/ · **Date:** 2026-06-13
**Mode:** SPEC-ONLY (no OHLCV/optional data loaded; `regime_labels.csv` waived). This document
defines the framework survey and selection; it uses public theory only — **no Phase 2/3 input**.

## 0. Method and isolation

Five theory-grounded framework families were surveyed in parallel by `framework-scout` agents
from free public sources (TA theory, quant-finance literature, public docs). Each returned
candidate-framework records in the skill's candidate schema. The orchestrator (this session)
then scored every candidate on the 7-criterion rubric and selected **exactly one** primary. No
Phase 2 result, Phase 3 result, or future-data signal was used. The regime definition comes from
the selected framework's published rules, never from LLM discretion (`llm_discretion_used=false`).

This is a **methodology-only** phase, so a separate `SPEC.md` is not required: the
`regime-classification` skill is the designated single source of truth for the canonical
vocabulary and the repository-defined trend-strength framework, and is treated as such.
`repository_spec_alignment` is therefore scored against that canonical framework. The
existing-classifier-vs-SPEC discrepancy check is not applicable (no existing classifier present
to reconcile).

## 1. Frameworks surveyed (17 candidates across 5 families)

| family | candidate_framework_id | framework | weighted_score | disposition |
|---|---|---|---:|---|
| trend-strength | TREND_STRENGTH_ADX_EMA_SPEC | ADX(14) + EMA9/21/55 alignment | 4.850 | **PRIMARY** |
| trend-strength | TREND_STRENGTH_ADX_DMI_DIR | ADX(14) + +DI/-DI direction | 4.175 | secondary |
| trend-strength | TREND_STRENGTH_EMA_ONLY_SLOPE | EMA stack + slope (no ADX) | 4.100 | rejected (dominated) |
| volatility | vol_04_ttm_squeeze_composite | TTM Squeeze (BB-in-Keltner) | 3.925 | secondary (split impl.) |
| volatility | vol_01_atr_percentile | ATR(14) percentile | 3.825 | secondary (split impl.) |
| volatility | vol_02_bbw_squeeze | Bollinger BandWidth | 3.825 | secondary |
| volatility | vol_03_realized_vol_percentile | Parkinson / Garman-Klass | 3.675 | future-research |
| price-action | PA_MS_001_dow_structure | Dow swing structure (HH/HL) | 4.050 | secondary (next-best) |
| price-action | PA_MS_002_bos_choch | BoS / ChoCH (ICT/SMC) | 3.475 | future-research |
| price-action | PA_MS_003_wyckoff | Wyckoff phases | 2.750 | future-research |
| statistical | stat_hmrs_hamilton | Hamilton MS-AR | 2.625 | rejected (hard gate) |
| statistical | stat_hmm_gaussian | Gaussian HMM | 2.525 | rejected (hard gate) |
| statistical | stat_gmm_regime | Gaussian Mixture Model | 2.400 | rejected (hard gate) |
| statistical | stat_vol_clustering | K-means vol-state clustering | 2.425 | rejected (hard gate) |
| session/liquidity | SL_01_session_window | Time-of-day / session | 3.975 | annotation (hard gate) |
| session/liquidity | SL_02_funding_proximity | Funding-interval proximity | 3.825 | annotation (hard gate) |
| session/liquidity | SL_03_volume_microstructure | Volume / microstructure | 3.000 | future-research |

Full per-criterion scores are in `regime_framework_selection_matrix.csv`.

## 2. Scoring rubric

Seven weighted criteria (weights sum to 1.0), each scored 0–5 (5 = best;
`implementation_complexity` scored as ease, 5 = simplest):

| criterion | weight |
|---|---:|
| theoretical_basis_strength | 0.20 |
| repository_spec_alignment | 0.20 |
| causal_safety | 0.20 |
| interpretability | 0.15 |
| data_availability | 0.10 |
| implementation_complexity | 0.10 |
| phase3_join_usability | 0.05 |

**Hard gates (override the score — never primary):** low `causal_safety`; very low
`repository_spec_alignment`; weak theoretical basis. Added this run: a framework that requires a
**train-only statistical fit** (HMM/GMM/clustering/scaler) cannot be validated with no data and
is therefore **ineligible as primary** this run.

## 3. Family analyses (items §14.1.2–§14.1.8)

### 3.1 Trend-strength (ADX/DMI + moving-average alignment)

- **Theory:** Wilder's ADX/DMI (1978) measures trend *strength* from smoothed directional
  movement; ADX≥25 = strong trend, ADX<25 = no trend (ADX≥25 is a common TA convention and the
  repository/SPEC value, not a Wilder-derived constant). Direction comes from EMA9/21/55 alignment
  — moving-average *alignment* is a standard trend-following technique; the 9/21/55 periods are
  repository/SPEC-defined. The ADX+EMA combination is the **repository-defined** framework
  (skill §3) — combining strength + direction is sanctioned, not arbitrary mixing.
- **Features/data:** EMA9/21/55, ADX(14) (needs True Range, +DM, -DM), and a volatility feature
  (ATR(14)) for the volatile/range split. OHLCV only.
- **Causal feasibility:** Fully causal — all are trailing close-based indicators on bars ≤ t;
  label known at bar-t close, `usable_from_timestamp` = next bar. No model fit. Volatility split
  uses a causal trailing percentile with a fixed convention cutoff (P70).
- **Look-ahead risks:** Only ADX warmup (~150 bars) instability and the need for a *trailing*
  (never centered/whole-sample) volatility percentile. No future-data reference.
- **5m fit:** Medium — ADX lag and the 20–25 gray-zone can cause label flicker at 5m (mitigable
  with hysteresis); otherwise robust. **SPEC mapping:** 1:1 onto all five canonical regimes.
- **Variants:** +DI/-DI direction (DMI original) — lower SPEC alignment, ambiguous `transition`;
  EMA-only — drops the ADX strength gate, producing false directional labels in ranges.

### 3.2 Volatility regime (ATR / BBW / realized-vol / TTM squeeze)

- **Theory:** Volatility clustering (Mandelbrot 1963; Engle 1982 ARCH). Classifies by risk
  level: compression vs expansion. **Structurally directionless.**
- **Features/data:** ATR(14) percentile, Bollinger BandWidth, Parkinson/Garman-Klass RV, or
  TTM Squeeze (BB inside Keltner). OHLCV only.
- **Causal feasibility:** Causal if percentiles use a trailing window; TTM Squeeze is best (a
  structural BB-in-KC rule needing **no** percentile fit — ideal for a no-data spec).
- **Look-ahead risks:** Whole-sample percentile (must be trailing); off-the-shelf indicators
  fine otherwise. **5m fit:** Medium (Parkinson/GK degrade at 5m due to microstructure noise).
- **SPEC mapping:** Maps only `volatile`/`range` — **cannot** produce `strong_up`/`strong_down`.
  Therefore unfit as a standalone primary, but it is exactly the auxiliary the SPEC framework
  uses to split `volatile` vs `range` (skill §6, allowed).

### 3.3 Price-action / market-structure (Dow, BoS/ChoCH, Wyckoff)

- **Theory:** Dow Theory (1900s; Edwards & Magee 1948) — uptrend = HH+HL, downtrend = LH+LL;
  structural break ends the trend. BoS/ChoCH is the ICT/SMC operationalization. Wyckoff adds
  volume-phase analysis.
- **Features/data:** Causally-confirmed swing highs/lows; structural-break flags; (Wyckoff also
  volume). OHLCV (high/low).
- **Causal feasibility:** Causal **only** with a right-sided pivot-confirmation rule (confirm a
  swing after k bars), which imposes a deterministic k·5-min lag. **Look-ahead risk is high in
  practice:** every off-the-shelf ZigZag / centered-pivot / hindsight-pivot definition is
  look-ahead biased; the popular SMC reference library uses future candles and must be rewritten.
- **5m fit:** Medium — many noisy micro-pivots at 5m. **SPEC mapping:** Maps `strong_up`,
  `strong_down`, `transition`, `range` natively; needs an auxiliary volatility feature for
  `volatile`. Dow (PA_MS_001) is the strongest theory in this family and the overall next-best.

### 3.4 Statistical / latent-state (Hamilton MS, HMM, GMM, K-means)

- **Theory:** Hamilton (1989) regime-switching; HMM (Baum-Welch/forward/Viterbi); GMM mixtures;
  K-means vol clustering. Strong academic grounding.
- **Features/data:** log-returns + realized vol; **requires a train-only EM/clustering fit** plus
  walk-forward validation and a latent-state→canonical mapping layer.
- **Causal feasibility / look-ahead risks:** Only the *filtered* (forward) probability is causal;
  the **default outputs are non-causal** (Kim-smoothed probabilities, Viterbi over the whole
  sequence) and whole-data EM/scaler/clustering fits are classic leaks. Latent states permute
  across refits.
- **5m fit:** Low — near-zero per-bar mean returns make directional discrimination poor; K=2
  cannot cover five regimes, K≥4 is EM-unstable. **SPEC mapping:** weak (post-hoc, no native
  `transition`). **Disposition:** HARD-GATED out this run — low causal_safety **and** a train fit
  is impossible with no data. Recorded as future-research (and unsupervised candidates only).

### 3.5 Session / liquidity (time-of-day, funding proximity, volume/microstructure)

- **Theory:** Intraday/session periodicity (Admati-Pfleiderer 1988; crypto studies); funding
  settles every 8h (00/08/16 UTC) creating pre/post-settlement micro-distortions; microstructure
  liquidity (Kyle 1985, Amihud 2002).
- **Features/data:** hour-of-day, day-of-week, minutes-to/from-funding (timestamp-only, trivially
  causal); volume z-score/percentile, OI, taker imbalance (need optional data — **absent**).
- **Causal feasibility:** Timestamp features fully causal; volume/microstructure blocked this run.
- **5m fit / SPEC mapping:** Describes the trading **environment**, not price direction —
  **cannot map any canonical price regime**. **Disposition:** HARD-GATED out as primary; valuable
  as Phase 3 secondary annotation / no-trade filter (session, funding-proximity) and a
  `volume_score` confidence column when data is present.

## 4. Selection (item §14.1.8)

**Selected primary: `TREND_STRENGTH_ADX_EMA_SPEC`** — the repository-defined trend-strength
framework (ADX(14)≥25 + EMA9/21/55 alignment, with a causal ATR(14)-percentile volatile/range
split). Weighted score **4.850**, the highest, and it clears every hard gate: strong theory
(Wilder ADX + standard multi-EMA alignment), highest `repository_spec_alignment` (it *is* the canonical framework, 1:1
mapping), top `causal_safety` (pure trailing formula, no fit), top interpretability, OHLCV-only.

**Next-best:** `PA_MS_001_dow_structure` (4.050) — the strongest theory among directional
alternatives, but gated below the primary by lower causal_safety (pivot-lag + ZigZag look-ahead
trap), higher implementation complexity, and its need for an auxiliary volatility feature. Kept
as the leading **secondary / future-research** framework.

**Notable hard-gate cases:** `SL_01_session_window` scored 3.975 on raw criteria yet is
**rejected** — its `repository_spec_alignment` is 1.0 (it cannot express a price regime). This is
exactly why hard gates exist: a high environment-state score must not promote a non-price-regime
framework to primary. The statistical family (2.4–2.6) is rejected for low causal_safety plus the
no-data train-fit impossibility.

Rejected/secondary frameworks and reasons are recorded per-row in
`regime_framework_selection_matrix.csv` and carried into `selected_primary_regime_framework.md`.

## 5. Why no mixing (item §14.1.9)

Exactly **one** primary framework is adopted. No rules from other families are blended into the
classifier. Specifically:

- The **volatility feature** used to split `volatile` vs `range` is **not** a second framework —
  the SPEC framework (skill §3, §6) *defines* the low-ADX bucket as split by a volatility feature.
  Using ATR(14) percentile for that split is the framework's own auxiliary, explicitly allowed;
  it is not the volatility-regime *family* acting as a co-primary.
- Price-action, statistical, and session/liquidity frameworks are **documented only** as
  secondary references / future research / Phase 3 annotations — none contributes a rule to the
  primary classifier.
- No "best-looking condition from each family" cherry-pick, no weighted-score ensemble, and no
  adjustment of any rule by looking at Phase 2/3 results. Thresholds follow SPEC/theory only.

## 6. Sources (representative)

- Wilder, J.W. (1978) *New Concepts in Technical Trading Systems* — ADX/DMI.
- StockCharts ChartSchool: ADX, Bollinger BandWidth, TTM Squeeze.
- Multiple moving-average *alignment* (MA-ribbon) — standard trend-following TA convention; the
  EMA9/21/55 periods are repository/SPEC-defined, not from a named author's system.
- Edwards & Magee (1948) *Technical Analysis of Stock Trends* — Dow theory.
- Mandelbrot (1963); Engle (1982, ARCH) — volatility clustering.
- Parkinson (1980); Garman & Klass (1980) — range-based volatility estimators.
- Hamilton (1989) *Econometrica*; Rabiner (1989) HMM tutorial; Kim (1994) smoother.
- Admati & Pfleiderer (1988); Corbet et al. (2019) — intraday periodicity.
- Kyle (1985); Amihud (2002) — market-microstructure liquidity.
- Binance funding-rate documentation (8h settlement; 2025 adaptive intervals).

Full URLs are recorded in the framework-scout transcript for this run.
