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