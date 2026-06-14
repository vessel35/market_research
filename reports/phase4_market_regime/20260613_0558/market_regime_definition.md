# Market Regime Definition

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m · **Run:** 20260613_0558
**Primary framework:** repository-defined trend-strength (ADX(14) + EMA9/21/55 + ATR-percentile
volatility split). `llm_discretion_used=false`.

## 1. Selected primary framework

`TREND_STRENGTH_ADX_EMA_SPEC` (see `selected_primary_regime_framework.md`). It defines the current
market regime for every 5m bar from data confirmed up to that bar.

## 2. Canonical regime vocabulary

`strong_up` · `strong_down` · `transition` · `volatile` · `range`. Plus `all` (NOT a market
state). This vocabulary is fixed by the SPEC and is not altered.

## 3–4. Regime definitions and expected behavior

- **strong_up** — confirmed uptrend: ADX≥25 with EMA9>EMA21>EMA55. Expect directional upward
  drift, higher-highs; trend-following longs favored.
- **strong_down** — confirmed downtrend: ADX≥25 with EMA9<EMA21<EMA55. Expect directional
  downward drift, lower-lows; trend-following shorts favored.
- **transition** — trend present (ADX≥25) but EMA alignment conflicted (crossover/flux). Expect
  unstable direction; elevated reversal/whipsaw risk.
- **volatile** — no trend (ADX<25) but elevated volatility (ATR percentile ≥ P70). Expect
  large, directionless swings; high noise; breakout-fakeout risk.
- **range** — no trend (ADX<25) and subdued volatility (ATR percentile < P70). Expect
  mean-reverting oscillation within a band; mean-reversion favored.

## 5. MarketRegime enum mapping

This phase maps to the canonical enum names directly; if a backtest service
later exposes a concrete `MarketRegime` enum, Phase 3 reconciles names at integration time (not
required here):

| canonical regime | MarketRegime enum (proposed) |
|---|---|
| strong_up | `MarketRegime.STRONG_UP` |
| strong_down | `MarketRegime.STRONG_DOWN` |
| transition | `MarketRegime.TRANSITION` |
| volatile | `MarketRegime.VOLATILE` |
| range | `MarketRegime.RANGE` |
| all | `MarketRegime.ALL` (aggregation only; never a per-bar label) |

## 6. Meaning of `all`

`all` is the Phase 3 unconditional-aggregation bucket ("across all regimes"); it is never emitted
as a per-bar regime and never appears in `regime` of `regime_labels.csv`.

## 7. causal / smoothed / posthoc distinction

This deliverable defines **causal** labels only (bars ≤ t, live-reproducible). Smoothed (uses
neighbouring/future bars to de-noise) and posthoc (whole-segment hindsight) labels are NOT
produced in this run; if ever produced they live in `smoothed_regime_labels.csv` /
`posthoc_regime_labels.csv`, are flagged `usable_in_hybrid=false`, and are never mixed into the
causal label file or used as a hybrid-eligibility basis.

## 8. Threshold policy

ADX gate = 25 (repository/SPEC value and common TA convention, not a Wilder-derived constant); volatility-high cutoff = P70 (design convention) of a causal trailing ATR(14)
percentile. Fixed convention/theory thresholds — never tuned to Phase 2/3 performance or a test
set (see `selected_primary_regime_framework.md` §8 and `causal_regime_classifier_spec.md` §10).

## 9. Volatility high/low criterion

`volatility_score` = trailing rolling percentile rank of ATR(14) over a causal window (default
W=2016 bars ≈ 7 days; expanding from data start until W is reached). **High** iff percentile ≥
70; otherwise **not high**. Strictly trailing (never centered/whole-sample). Before sufficient
history exists, the bar is treated as warmup (low confidence), not forced into `volatile`.

## 10. Procedure to add revised/experimental candidate regimes

Canonical regimes stay fixed. A new idea (e.g. `low_volatility_compression`, `funding_extreme`)
is recorded as an `experimental_regime_candidate` in a separate file, validated in a later
research cycle, never applied retroactively to Phase 3 results, and never adjusted to flatter
backtest performance. It does not replace any canonical regime.

## 11. Value Phase 3 uses for `edge_fragment.regime`

Phase 3 uses the **canonical** `regime` value (one of the five) from the causal
`regime_labels.csv`, joined by `usable_from_timestamp` (see `phase3_usage_contract.md`). Only
`regime_labeling=causal` labels are hybrid-eligible.

## 12. Definition table

| regime | definition | primary framework rule | core features | expected behavior | allowed_in_edge_fragment | notes |
|---|---|---|---|---|---|---|
| strong_up | confirmed uptrend | ADX(14) ≥ 25 AND EMA9 > EMA21 > EMA55 | ADX(14), EMA9, EMA21, EMA55 | upward drift, HH/HL | yes | directional; trend-following longs |
| strong_down | confirmed downtrend | ADX(14) ≥ 25 AND EMA9 < EMA21 < EMA55 | ADX(14), EMA9, EMA21, EMA55 | downward drift, LH/LL | yes | directional; trend-following shorts |
| transition | trend present, direction unresolved | ADX(14) ≥ 25 AND EMA alignment mixed | ADX(14), EMA9, EMA21, EMA55 | whipsaw/reversal risk | yes | unstable; crossover/flux |
| volatile | no trend, high volatility | ADX(14) < 25 AND ATR percentile ≥ P70 | ADX(14), volatility_score (ATR pct) | large directionless swings | yes | breakout-fakeout risk |
| range | no trend, low volatility | ADX(14) < 25 AND ATR percentile < P70 | ADX(14), volatility_score (ATR pct) | mean-reverting band | yes | mean-reversion favored |
| all | aggregation bucket (not a state) | n/a | n/a | n/a | no (aggregation only) | Phase 3 unconditional bucket |
