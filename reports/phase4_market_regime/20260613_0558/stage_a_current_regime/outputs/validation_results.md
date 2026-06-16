# Validation Results

**OHLCV source:** `/home/vessel/workspace/trading-system/backtestdata/ETHUSDT_futures_5min.csv`
**Labels file:** `stage_a_current_regime/outputs/regime_labels.csv`
**Rows:** 210,528

## 1. Unit Branch Tests (5 regimes + warmup + boundaries + confidence)

| test | result | evidence |
|---|---|---|
| unit_strong_up | PASS | ADX=30 EMA9>EMA21>EMA55 -> regime='strong_up' (expected 'strong_up') alt='transition' |
| unit_strong_down | PASS | ADX=30 EMA9<EMA21<EMA55 -> regime='strong_down' (expected 'strong_down') alt='transition' |
| unit_transition | PASS | ADX=30 EMA9>EMA21 but EMA21<EMA55 -> regime='transition' (expected 'transition') alt='strong_up' |
| unit_volatile | PASS | ADX=18 vol_score=85 -> regime='volatile' (expected 'volatile') alt='range' |
| unit_range | PASS | ADX=18 vol_score=40 -> regime='range' (expected 'range') alt='volatile' |
| unit_warmup_handled_in_pipeline | PASS | Warmup / NaN rows set to 'unknown_or_warmup' before classify_bar is called; verified by effective_warmup_301 test |
| unit_boundary_adx_25_trend | PASS | ADX=25.0 (boundary) EMA up -> regime='strong_up' (must be 'strong_up'; >= inclusive) |
| unit_boundary_vol_70_volatile | PASS | ADX=18 vol_score=70.0 (boundary) -> regime='volatile' (must be 'volatile'; >= inclusive) |
| unit_confidence_strong_up_range | PASS | confidence=0.600000 for strong_up (must be in [0,1]) |
| unit_confidence_range_range | PASS | confidence=0.354286 for range (must be in [0,1]) |
| unit_confidence_volatile_range | PASS | confidence=0.390000 for volatile (must be in [0,1]) |

## 2. Schema Check (20 cols, 0 of 14 forbidden, causal, canonical regimes)

| test | result | evidence |
|---|---|---|
| schema_col_count | PASS | columns=20 (expected 20); cols=['timestamp', 'usable_from_timestamp', 'symbol', 'timeframe', 'regime', 'regime_alt', 'regime_labeling', 'regime_confidence', 'selected_primary_framework', 'trend_score', 'volatility_score', 'momentum_score', 'mean_reversion_score', 'volume_score', 'data_quality_score', 'feature_snapshot_ref', 'classifier_version', 'source_data_path', 'git_commit', 'llm_discretion_used'] |
| schema_required_cols_present | PASS | missing required columns: none |
| schema_no_forbidden_cols | PASS | forbidden columns found: none (0 of 14 forbidden cols present) |
| schema_regime_labeling_causal | PASS | rows with regime_labeling != 'causal': 0 |
| schema_llm_discretion_false | PASS | rows with llm_discretion_used != false: 0 |
| schema_regime_values_canonical | PASS | rows with regime not in canonical+warmup: 0; unexpected values: none |

## 3. usable_from_timestamp > timestamp (all rows)

| test | result | evidence |
|---|---|---|
| usable_from_gt_timestamp | PASS | rows with usable_from_timestamp <= timestamp: 0 (expected 0) |

## 4. Effective Warmup = 301 (rows 0..300 warmup, first labeled idx=301)

| test | result | evidence |
|---|---|---|
| effective_warmup_first_labeled_at_301 | PASS | rows 0..300 all unknown_or_warmup=True (301/301); first non-warmup index=301 (expected 301); row 301 regime='strong_up' @ 2024-01-02 01:05:00+00:00 |

## 5. EMA Indicator Reference vs pandas ewm(adjust=False)

| test | result | evidence |
|---|---|---|
| ema9_vs_pandas_ewm | PASS | max abs diff over bars 500..1000 = 0.000e+00 (threshold 1e-6) |
| ema21_vs_pandas_ewm | PASS | max abs diff over bars 500..1000 = 0.000e+00 (threshold 1e-6) |
| ema55_vs_pandas_ewm | PASS | max abs diff over bars 500..1000 = 3.825e-07 (threshold 1e-6) |

## 6. Wilder ATR(14)/+DI/-DI/DX Hand-Verify on Real Data

| test | result | evidence |
|---|---|---|
| wilder_atr14_hand_verify | PASS | seed=54.910000 script=54.910000; bar15=53.827857 script=53.827857; bar16=51.843010 script=51.843010; max abs diff=0.00e+00 |
| wilder_di14_hand_verify | PASS | +DI=33.636860 script=33.636860; -DI=10.872337 script=10.872337; max abs diff=0.00e+00 |
| wilder_dx14_hand_verify | PASS | DX at bar 14=51.145663 re-derived from script DI values=51.145663; abs diff=0.00e+00 |

## 7. Slice-Invariance: 40 random + ADX-boundary + vol_score-boundary (causal)

| test | result | evidence |
|---|---|---|
| slice_invariance_40_random | PASS | 40 random samples tested; failures=0 (expected 0) |
| boundary_adx_slice_invariance | PASS | 20 bars tested with ADX14 in [24,26] (found 14861 in band); failures=0 (expected 0) |
| boundary_volscore_slice_invariance | PASS | 20 bars tested with vol_score in [68,72] (found 8038 in band); failures=0 (expected 0) |

## Overall Verdict

**ALL TESTS PASS**

| section | result |
|---|---|
| Unit Branch Tests (5 regimes + warmup + boundaries + confidence) | PASS |
| Schema Check (20 cols, 0 of 14 forbidden, causal, canonical regimes) | PASS |
| usable_from_timestamp > timestamp (all rows) | PASS |
| Effective Warmup = 301 (rows 0..300 warmup, first labeled idx=301) | PASS |
| EMA Indicator Reference vs pandas ewm(adjust=False) | PASS |
| Wilder ATR(14)/+DI/-DI/DX Hand-Verify on Real Data | PASS |
| Slice-Invariance: 40 random + ADX-boundary + vol_score-boundary (causal) | PASS |
