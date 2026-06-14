# Causal Regime Classifier Spec

**Symbol/market:** ETH/USDT, Binance USDT-M perpetual futures, 5m · **Run:** 20260613_0558
**Classifier version:** `phase4_specA_v1` · **Mode:** DATA-PRESENT (spec authored AND executed on
real OHLCV 2026-06-14; see §35.14 / `validation_results.md`). All features use bars ≤ t.
`llm_discretion_used=false`.

## 1. Selected primary framework

Repository-defined trend-strength: ADX(14) trend gate + EMA9/21/55 direction + ATR(14)-percentile
volatility split. One framework, no mixing.

## 2. Theoretical basis

Wilder (1978) ADX/DMI for trend strength; multi-EMA *alignment* for direction (a standard
trend-following technique; the 9/21/55 periods are repository/SPEC-defined); Mandelbrot
(1963)/Engle (1982) volatility clustering for the volatile/range split. See
`regime_framework_research.md` §3.1.

## 3. Input data

ETH/USDT 5m OHLCV: `timestamp`, `open`, `high`, `low`, `close`, `volume`. Timestamps strictly
ascending, UTC, 5-minute spacing, no duplicates, valid OHLC. (No data loaded this run; this is the
required input contract for a future data-present run.) No optional data required.

## 4. Feature calculation order (per bar t, bars ≤ t only)

1. True Range `TR[t]`, directional movement `+DM[t]`, `−DM[t]`.
2. Wilder-smoothed `ATR14[t]`, `+DM14[t]`, `−DM14[t]` → `+DI14[t]`, `−DI14[t]` → `DX[t]` →
   Wilder-smoothed `ADX14[t]`.
3. `EMA9[t]`, `EMA21[t]`, `EMA55[t]` (close).
4. `volatility_score[t]` = trailing percentile rank of `ATR14[t]` over the causal window.
5. Apply classification rules (§9); assign `usable_from_timestamp[t]` (§11) and
   `regime_confidence[t]` (§12).

## 5. Selected feature list (classifier inputs)

`EMA9`, `EMA21`, `EMA55`, `ema_alignment_state`, `ADX14`, `ATR14`, `volatility_score`
(ATR percentile). Exactly these are flagged `selected_framework_feature=true` in
`regime_feature_catalog.csv`. No other feature enters the classifier.

## 6. ADX(14) calculation (Wilder)

BEGIN_PSEUDOCODE
TR[t]      = max(high[t]-low[t], abs(high[t]-close[t-1]), abs(low[t]-close[t-1]))
upMove     = high[t] - high[t-1]
downMove   = low[t-1] - low[t]
plusDM[t]  = upMove   if (upMove > downMove and upMove > 0)   else 0
minusDM[t] = downMove if (downMove > upMove and downMove > 0) else 0

# Wilder smoothing (RMA), period P = 14:
#   seed S[P]   = sum(X[1..P])            (first available value at bar P)
#   recursion   = S[t] = S[t-1] - (S[t-1] / P) + X[t]
ATR14[t]   = WilderRMA(TR, 14)
sPlusDM[t] = WilderRMA(plusDM, 14)
sMinusDM[t]= WilderRMA(minusDM, 14)

plusDI14[t]  = 100 * sPlusDM[t]  / ATR14[t]     # ATR14 = WilderRMA(TR,14) == smoothed TR
minusDI14[t] = 100 * sMinusDM[t] / ATR14[t]
DX[t]        = 100 * abs(plusDI14[t]-minusDI14[t]) / (plusDI14[t]+minusDI14[t])    # 0 if denom=0
ADX14[t]     = WilderRMA(DX, 14)                 # first ADX = mean(DX over first 14 DX values)
END_PSEUDOCODE

All terms use bars ≤ t (TR and DM reference bar t and t−1; smoothing references prior smoothed
values). ADX first value appears ~bar 28; stabilizes ~bar 150.

## 7. EMA calculation

BEGIN_PSEUDOCODE
alpha_N    = 2 / (N + 1)
EMA_N[t]   = alpha_N * close[t] + (1 - alpha_N) * EMA_N[t-1]
seed: EMA_N[N] = SMA(close[1..N]); EMA undefined for t < N
END_PSEUDOCODE

`ema_alignment_state[t]` ∈ {up, down, mixed}: up if EMA9>EMA21>EMA55; down if EMA9<EMA21<EMA55;
else mixed. Uses bars ≤ t.

## 8. Volatility score calculation

BEGIN_PSEUDOCODE
# Causal trailing percentile rank of ATR14 (bars <= t, includes bar t; NEVER future bars)
W_full = 2016          # ~7 days of 5m bars
W_min  = 288           # ~1 day; minimum history before the score is trusted
window = ATR14[max(warmup_atr, t-W_full+1) .. t]
volatility_score[t] = 100 * (count(window <= ATR14[t]) - 1) / (len(window) - 1)   # 0..100
# high iff volatility_score[t] >= 70 (P70)
END_PSEUDOCODE

Strictly trailing — no centered window, no whole-sample percentile. Before `W_min` bars of ATR
history exist, the bar is treated as warmup (§9). The P70 cutoff is a fixed convention, not a
train-only fit and not tuned to performance.

**Implementation note (data-present run, 2026-06-14):** the percentile is computed with pandas
`rolling(2016, min_periods=288).rank(pct=True)` (= count(window ≤ x)/len, average ties). **For
classifier_version `phase4_specA_v1` this pandas convention is the canonical/authoritative
definition**; the `(count−1)/(len−1)` line above is an equivalent illustration (they differ by
<0.04% at W=2016). Both are strictly trailing (bars ≤ t) and causal. Effective warmup is **301 bars** (ATR(14) first valid ~bar 14, and
`volatility_score` then needs `min_periods=288` further ATR values), slightly beyond the nominal
`warmup_end=288`; the NaN-gate in §9 handles this correctly (those rows → `unknown_or_warmup`).

## 9. Classifier pseudocode

BEGIN_PSEUDOCODE
warmup_end = 288    # max(ADX stable ~150, EMA55 ~55, volatility W_min 288)
for each bar t:
    if t < warmup_end or any(EMA9,EMA21,EMA55,ADX14,ATR14,volatility_score) is NaN:
        regime[t] = "unknown_or_warmup"; regime_confidence[t] = 0.0
        usable_from_timestamp[t] = timestamp[t] + 5min
        continue
    if ADX14[t] >= 25 and EMA9[t] > EMA21[t] > EMA55[t]:
        regime[t] = "strong_up"
    elif ADX14[t] >= 25 and EMA9[t] < EMA21[t] < EMA55[t]:
        regime[t] = "strong_down"
    elif ADX14[t] >= 25:
        regime[t] = "transition"
    elif volatility_score[t] >= 70:
        regime[t] = "volatile"
    else:
        regime[t] = "range"
    usable_from_timestamp[t] = timestamp[t] + 5min      # label uses bar-t close -> next bar
END_PSEUDOCODE

`unknown_or_warmup` is a label-availability state, NOT a canonical regime; such rows are excluded
from Phase 3 hybrid eligibility (the Phase 3 join already treats "no usable label" as
`unknown_or_warmup`). They are not written as one of the five canonical values.

## 10. Threshold source

ADX gate `25` = repository/SPEC value and common TA convention (Wilder grounds the ADX concept; 25
is convention, not a derived constant); volatility-high cutoff `P70` = documented design convention applied
to a causal trailing ATR percentile. Priority chain (skill §15): SPEC/code (absent) → train-period
percentile (no data) → walk-forward percentile (no data) → **fixed convention/SPEC value** (used; to be profiled against the data distribution later). Never tuned to
Phase 2/3 performance or a test set.

## 11. usable_from_timestamp rules

Every feature is computed from bar-t close, so the regime for bar t is known only after bar t
closes; therefore `usable_from_timestamp[t] = timestamp[t] + 5min` (next 5m bar open), strictly
later than `timestamp[t]`. Rolling/percentile windows include the current bar and only past bars.
No current-bar high/low is treated as known at bar open.

## 12. regime_confidence formula (framework-internal only, 0..1)

BEGIN_PSEUDOCODE
trend_gate_margin = clip(abs(ADX14[t] - 25) / 25, 0, 1)
atr_den = max(0.5 * ATR14[t], 1e-12)        # flat-market divide-by-zero guard (ATR14==0)
if regime == "strong_up":
    spec_margin = clip(min(EMA9-EMA21, EMA21-EMA55) / (atr_den), 0, 1)
elif regime == "strong_down":
    spec_margin = clip(min(EMA21-EMA9, EMA55-EMA21) / (atr_den), 0, 1)
elif regime == "transition":
    up_al   = clip(min(EMA9-EMA21, EMA21-EMA55) / (atr_den), 0, 1)
    down_al = clip(min(EMA21-EMA9, EMA55-EMA21) / (atr_den), 0, 1)
    spec_margin = 1 - max(up_al, down_al)          # high when far from any alignment
elif regime == "volatile":
    spec_margin = clip((volatility_score[t] - 70) / 30, 0, 1)
else:  # range
    spec_margin = clip((70 - volatility_score[t]) / 70, 0, 1)
regime_confidence[t] = clip(0.5 * trend_gate_margin + 0.5 * spec_margin, 0, 1)
END_PSEUDOCODE

Weights (0.5/0.5) and scales (0.5·ATR, 30, 70) are fixed conventions, documented here, derived
from the framework's own geometry — never from strategy performance. This `regime_confidence` is
distinct from `edge_fragment.confidence` (Phase 3 computes the latter).

## 13. MarketRegime mapping

strong_up→`STRONG_UP`, strong_down→`STRONG_DOWN`, transition→`TRANSITION`, volatile→`VOLATILE`,
range→`RANGE`, all→`ALL` (aggregation only). This methodology-only phase defines the canonical
enum names directly; if a backtest service later exposes its own MarketRegime enum, Phase 3
reconciles names at integration time (not required here).

## 14. Look-ahead prevention rules

(1) All features use bars ≤ t. (2) No future return/high/low/min/max anywhere. (3) ATR percentile
uses a strictly trailing window (current + past), never centered or whole-sample. (4) Label for
bar t usable only from t+1. (5) No centered rolling windows, no ZigZag/hindsight pivots. (6) No
scaler/clustering/model fit (rule-based; no train fit). (7) Warmup bars flagged, never
back-filled. (8) Smoothed/posthoc labels (if ever made) stay in separate files.

## 15. Unit-test plan (per skill §33.2) — EXECUTED 2026-06-14, all PASS (`validation_results.md`)

1. strong_up: ADX=30, EMA9>EMA21>EMA55 → `strong_up`.
2. strong_down: ADX=30, EMA9<EMA21<EMA55 → `strong_down`.
3. transition: ADX=30, EMA9>EMA21<EMA55 (mixed) → `transition`.
4. volatile: ADX=18, volatility_score=85 → `volatile`.
5. range: ADX=18, volatility_score=40 → `range`.
6. NaN warmup: t<288 or NaN feature → `unknown_or_warmup`, confidence 0.
7. boundary: ADX exactly 25 → trend branch (>= 25); volatility_score exactly 70 → `volatile`
   (>= 70). Document and freeze the inclusive-boundary convention.

## 16. Slice-invariance test plan (per skill §33.3) — EXECUTED 2026-06-14, 40/40 PASS (`validation_results.md`)

1. For any t ≤ T: `regime[t]` computed on `data[0:t+1]` equals `regime[t]` computed on
   `data[0:T+1]` (appending future bars must not change a past label).
2. `usable_from_timestamp[t] > timestamp[t]` for every row.
3. Any centered-window feature → test fails (must not be present).
4. Smoothed/posthoc labels must not appear in the causal label file.
5. Any row with `llm_discretion_used=true` → test fails.

## 17. Phase 3 application

Phase 3 attaches, for each trade, the most recent causal label with
`usable_from_timestamp <= trade.timestamp_entry` (and similarly for exit), and the holding-period
path between them. Phase 3 performs the join; Phase 4 only specifies it. Full algorithm in
`regime_labeling_pipeline_spec.md` and `phase3_usage_contract.md`.

## 18. LLM-discretion confirmation

Every label is produced solely by the deterministic rules in §9. No LLM judgment, narrative, or
"looks like an uptrend" override is used at any point. `llm_discretion_used=false` for all labels;
a `true` value would render the label invalid.
