# Validation Results

## 1. Unit Tests (spec SS15)

| test | result | evidence |
|---|---|---|
| unit_strong_up | PASS | ADX=30 EMA9>EMA21>EMA55 -> regime='strong_up' (expected 'strong_up') alt='transition' |
| unit_strong_down | PASS | ADX=30 EMA9<EMA21<EMA55 -> regime='strong_down' (expected 'strong_down') alt='transition' |
| unit_transition | PASS | ADX=30 EMA9>EMA21 but EMA21<EMA55 -> regime='transition' (expected 'transition') alt='strong_up' |
| unit_volatile | PASS | ADX=18 vol_score=85 -> regime='volatile' (expected 'volatile') alt='range' |
| unit_range | PASS | ADX=18 vol_score=40 -> regime='range' (expected 'range') alt='volatile' |
| unit_boundary_adx_25_trend | PASS | ADX=25.0 (boundary) EMA up -> regime='strong_up' (must be 'strong_up'; >= inclusive) |
| unit_boundary_vol_70_volatile | PASS | ADX=18 vol_score=70.0 (boundary) -> regime='volatile' (must be 'volatile'; >= inclusive) |
| unit_confidence_strong_up_range | PASS | confidence=0.600000 for strong_up (must be in [0,1]) |
| unit_confidence_range_range | PASS | confidence=0.354286 for range (must be in [0,1]) |
| unit_confidence_volatile_range | PASS | confidence=0.390000 for volatile (must be in [0,1]) |
| unit_warmup_handled_in_pipeline | PASS | Warmup / NaN rows set to 'unknown_or_warmup' before classify_bar is called (verified separately by warmup_boundary test) |

## 2. Slice-Invariance Test — Causality Proof (spec SS16)

- Samples tested: 40
- Overall: **PASS**
- Failures: 0 — every truncated-series regime matches full-series

Proof of causality: for every sampled t, computing indicators on data[0:t+1] yields the identical regime as computing on the full series. No future bars are needed. The rolling ATR percentile uses pandas trailing rolling rank (causal). No centered window, no ZigZag, no whole-sample percentile is used.

## 3. usable_from_timestamp > timestamp (all rows)
**PASS** — rows with usable_from_timestamp <= timestamp: 0

## 4. Warmup / Boundary Check
**PASS** — first 288 rows all unknown_or_warmup: 288/288

Rows around warmup boundary (index 280-299):

| index | timestamp | regime |
|---|---|---|
| 280 | 2024-01-01 23:20:00+00:00 | unknown_or_warmup |
| 281 | 2024-01-01 23:25:00+00:00 | unknown_or_warmup |
| 282 | 2024-01-01 23:30:00+00:00 | unknown_or_warmup |
| 283 | 2024-01-01 23:35:00+00:00 | unknown_or_warmup |
| 284 | 2024-01-01 23:40:00+00:00 | unknown_or_warmup |
| 285 | 2024-01-01 23:45:00+00:00 | unknown_or_warmup |
| 286 | 2024-01-01 23:50:00+00:00 | unknown_or_warmup |
| 287 | 2024-01-01 23:55:00+00:00 | unknown_or_warmup |
| 288 | 2024-01-02 00:00:00+00:00 | unknown_or_warmup |
| 289 | 2024-01-02 00:05:00+00:00 | unknown_or_warmup |
| 290 | 2024-01-02 00:10:00+00:00 | unknown_or_warmup |
| 291 | 2024-01-02 00:15:00+00:00 | unknown_or_warmup |
| 292 | 2024-01-02 00:20:00+00:00 | unknown_or_warmup |
| 293 | 2024-01-02 00:25:00+00:00 | unknown_or_warmup |
| 294 | 2024-01-02 00:30:00+00:00 | unknown_or_warmup |
| 295 | 2024-01-02 00:35:00+00:00 | unknown_or_warmup |
| 296 | 2024-01-02 00:40:00+00:00 | unknown_or_warmup |
| 297 | 2024-01-02 00:45:00+00:00 | unknown_or_warmup |
| 298 | 2024-01-02 00:50:00+00:00 | unknown_or_warmup |
| 299 | 2024-01-02 00:55:00+00:00 | unknown_or_warmup |

## 5. No Forbidden Columns
**PASS** — forbidden columns found: none

## 6. llm_discretion_used = false (all rows)
**PASS** — rows with llm_discretion_used != false: 0

## 7. regime_labeling = 'causal' (all rows)
**PASS** — rows with regime_labeling != 'causal': 0

## Overall Verdict

**ALL ACCEPTANCE TESTS PASS**

- Unit tests: PASS
- Slice-invariance (causality): PASS
- usable_from > timestamp: PASS
- Warmup boundary (first 288 rows): PASS
- No forbidden columns: PASS
- llm_discretion_used=false: PASS
- regime_labeling=causal: PASS

---

## Extended tests (2026-06-14b)

All tests executed live against the OHLCV file and committed regime_labels.csv. Python 3.12.13, pandas 2.1.4, numpy 1.26.3.

### A. Indicator reference tests

**A1: EMA9/21/55 cross-check vs pandas ewm(adjust=False)**

Method: compare script's `compute_ema(close, N)` against `pd.Series(close).ewm(span=N, adjust=False).mean()` over bars 500..1000 (well past SMA-seed transient). SMA-seed transient decays as `(1 - 2/(N+1))^(500-N)`; for EMA55 that is approximately 5e-8, below the 1e-6 tolerance.

| test | result | evidence |
|---|---|---|
| ema9_vs_pandas_ewm | PASS | max abs diff over bars 500..1000 = 0.000e+00 (threshold 1e-6) |
| ema21_vs_pandas_ewm | PASS | max abs diff over bars 500..1000 = 0.000e+00 (threshold 1e-6) |
| ema55_vs_pandas_ewm | PASS | max abs diff over bars 500..1000 = 3.825e-07 (threshold 1e-6) |

The non-zero EMA55 residual (3.8e-7) reflects the expected SMA-seed vs pure-exponential difference that has not fully decayed at bar 500. It is well below 1e-6.

**A2: Hand-verify Wilder ATR(14) and ADX(14)/+DI/-DI on first real-data bars**

Using the actual first 17 OHLCV bars (2024-01-01 00:00..01:20 UTC). Hand-computed expected values using the sum-seeded Wilder recursion and compared to script output.

First 17 bars (H/L/C from data):

```
[0]  H=2289.92 L=2282.97 C=2289.92
[1]  H=2294.00 L=2288.77 C=2292.56
[2]  H=2299.16 L=2292.61 C=2298.49
[3]  H=2298.93 L=2294.06 C=2294.06
[4]  H=2297.99 L=2294.06 C=2296.59
[5]  H=2298.13 L=2290.82 C=2292.83
[6]  H=2292.83 L=2290.08 C=2291.72
[7]  H=2296.20 L=2291.00 C=2296.20
[8]  H=2296.59 L=2292.90 C=2295.19
[9]  H=2296.00 L=2294.13 C=2294.45
[10] H=2297.35 L=2294.44 C=2297.34
[11] H=2299.00 L=2296.76 C=2297.41
[12] H=2297.63 L=2294.77 C=2295.72
[13] H=2297.02 L=2295.38 C=2296.56
[14] H=2299.49 L=2295.68 C=2298.53
[15] H=2301.37 L=2298.53 C=2300.66
[16] H=2301.41 L=2299.55 C=2299.67
```

Hand-computed expected values at bar 14 (first Wilder seed position):

- ATR14 seed = sum(TR[1..14]) = **54.910000**
- ATR14 at bar 15 (one recursion) = 54.910000 - 54.910000/14 + TR[15] = **53.827857**
- ATR14 at bar 16 = **51.843010**
- +DI14 = 100 * sum(+DM[1..14]) / ATR14_seed = **33.636860**
- -DI14 = 100 * sum(-DM[1..14]) / ATR14_seed = **10.872337**
- DX14 = 100 * |+DI14 - -DI14| / (+DI14 + -DI14) = **51.145663**

| test | result | evidence |
|---|---|---|
| wilder_atr14_hand_verify | PASS | seed=54.910000 matches script; bar15=53.827857 matches; bar16=51.843010 matches; max abs diff=0.00e+00 |
| wilder_di14_hand_verify | PASS | +DI=33.636860 matches script; -DI=10.872337 matches script; max abs diff=0.00e+00 |
| wilder_dx14_hand_verify | PASS | DX at bar 14=51.145663 matches re-derived from script DI values; abs diff=0.00e+00 |

### B. Effective-warmup direct assert

Assertion: rows 0..300 (inclusive, 301 rows) are ALL `unknown_or_warmup`; row index 301 is the FIRST non-warmup labeled row.

| test | result | evidence |
|---|---|---|
| effective_warmup_first_labeled_at_301 | PASS | rows 0..300 all unknown_or_warmup=True (301/301); first non-warmup index=301; row 301 regime='strong_up' |

Explanation: `WARMUP_END=288` forces indices 0..287 to warmup by the index check. Indices 288+ also require `vol_score` to be non-NaN, which needs `min_periods=288` non-NaN ATR values. ATR first becomes non-NaN at index 14 (bar 15 of data, using TR[1:] slice). Indices 14..301 span exactly 288 values, so `vol_score` first becomes non-NaN at index 301. This makes the effective warmup end 301, not 288, even though the spec constant is 288.

First non-warmup labeled row: **index 301** (2024-01-02 01:15:00 UTC), regime = `strong_up`.

### C. Boundary-stratified slice-invariance

Near-threshold bars carry the highest risk of look-ahead in any edge- or future-dependent window. Slice-invariance is recomputed for each selected bar t by running the full indicator pipeline on data[0:t+1] and comparing regime[t] to the full-series value.

**ADX14 in [24, 26] — near trend-gate boundary:**

Found 14,882 bars in this band. Tested 20 (first 20 in index order).

| test | result | evidence |
|---|---|---|
| boundary_adx_slice_invariance | PASS | 20 bars tested with ADX14 in [24,26]; failures=0 (expected 0) |

**vol_score in [68, 72] — near volatility-gate boundary:**

Found 8,038 bars in this band. Tested 20 (first 20 in index order).

| test | result | evidence |
|---|---|---|
| boundary_volscore_slice_invariance | PASS | 20 bars tested with vol_score in [68,72]; failures=0 (expected 0) |

### Extended tests overall verdict

**ALL 9 EXTENDED TESTS PASS**

| category | tests | result |
|---|---|---|
| EMA cross-check (A1) | 3 (EMA9/21/55) | PASS |
| Wilder ATR/DI/DX hand-verify (A2) | 3 (ATR14, +/-DI, DX) | PASS |
| Effective warmup direct assert (B) | 1 | PASS |
| Boundary ADX slice-invariance (C) | 1 (20 bars) | PASS |
| Boundary vol_score slice-invariance (C) | 1 (20 bars) | PASS |
