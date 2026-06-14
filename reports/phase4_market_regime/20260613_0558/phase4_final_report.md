# Phase 4 Market Regime — Stage A Final Report

**Run:** 20260613_0558 · **Produced by:** completeness-auditor · **Date:** 2026-06-13
**Verdict:** Stage A COMPLETE — methodology/deliverable gates passed **and** the data-present
acceptance run passed (2026-06-14). `regime_labels.csv` was generated on real ETH/USDT 5m OHLCV
(210,528 bars); data-quality PASS; all unit + slice-invariance + warmup/boundary tests PASS;
`causal-auditor` PASS on the realized labels + implementation. See §35.14 for empirical results.
(Whether ADX=25 / P70 are *appropriate for trading* remains a Phase-3 question — Phase 4 only
profiles the distribution, never tuning to performance.)

---

## §35.1 Run Summary

| field | value |
|---|---|
| symbol | ETH/USDT |
| market | Binance USDT-M perpetual futures |
| timeframe | 5m |
| run_id | 20260613_0558 |
| run_mode | data-present acceptance run (methodology spec executed on real OHLCV, 2026-06-14) |
| data_period | 2024-01-01 00:00:00 → 2025-12-31 23:55:00 (210,528 bars; UTC) |
| stage_a_status | completed |
| stage_b_status | completed (research design; methodology-only) |
| selected_primary_framework | TREND_STRENGTH_ADX_EMA_SPEC |
| primary_labeling_method | causal |
| phase2_results_used | false |
| phase3_results_used | false |
| phase4_outputs_used_in_phase2 | false |
| intended_consumer | phase3_only |
| llm_discretion_used | false |
| regime_labels.csv | GENERATED — 210,528 rows (301 warmup, 210,227 labeled); causal; schema-conformant |
| data_quality_report.md | PRODUCED — PASS (0 dup/gap/OHLC violations; 21 zero-volume + 9 spike bars documented) |
| causal_classifier_version | phase4_specA_v1 |
| git_commit | 6a721f5 (labels generated against this commit) |
| research_db | not queried — file-based only (MCP-down fallback per skill §16) |

---

## §35.2 Framework Survey Summary

Five families were surveyed in parallel (17 candidates total). One primary selected; 16 rejected
with documented reasons.

| family | candidates surveyed | highest score in family | disposition of best |
|---|---:|---:|---|
| trend-strength | 3 | 4.850 (TREND_STRENGTH_ADX_EMA_SPEC) | PRIMARY |
| volatility | 4 | 3.925 (vol_04_ttm_squeeze_composite) | secondary / split impl. |
| price-action / market-structure | 3 | 4.050 (PA_MS_001_dow_structure) | next-best / future-research |
| statistical (HMM / regime-switching) | 4 | 2.625 (stat_hmrs_hamilton) | all HARD-GATED (causal_safety + no-data) |
| session / liquidity | 3 | 3.975 (SL_01_session_window) | all HARD-GATED (cannot map price regime) |

Sources: Wilder (1978), standard multi-EMA / MA-ribbon alignment (TA convention; 9/21/55 repo/SPEC-defined), Dow/Edwards-Magee (1948), Mandelbrot (1963), Engle (1982),
Hamilton (1989), Rabiner (1989), Admati-Pfleiderer (1988), Kyle (1985), Amihud (2002), Binance
funding-rate documentation.

---

## §35.3 Selection Matrix Summary

Full per-criterion scores: `regime_framework_selection_matrix.csv`. Criterion weights (sum 1.0)
and selected vs next-best comparison:

| criterion | weight | TREND_STRENGTH_ADX_EMA_SPEC (selected) | PA_MS_001_dow_structure (next-best) |
|---|---:|---:|---:|
| theoretical_basis_strength | 0.20 | 4.5 | 5.0 |
| repository_spec_alignment | 0.20 | 5.0 | 3.0 |
| causal_safety | 0.20 | 5.0 | 3.5 |
| interpretability | 0.15 | 5.0 | 5.0 |
| data_availability | 0.10 | 5.0 | 5.0 |
| implementation_complexity | 0.10 | 4.5 | 3.0 |
| phase3_join_usability | 0.05 | 5.0 | 4.0 |
| **weighted_score** | 1.00 | **4.850** | **4.050** |

Hard gates applied: low causal_safety (statistical family), very low repository_spec_alignment
(session/liquidity family), weak theory or no-data train-fit impossibility (HMM/GMM/clustering).
The selected framework cleared every hard gate and scored highest overall.

---

## §35.4 Selected Framework

**TREND_STRENGTH_ADX_EMA_SPEC** — repository-defined trend-strength framework.

**Why it fits ETH/USDT 5m:** Fully OHLCV-based, deterministic, reproducible. Operates 24/7
with no session assumption. ADX lag and the 20–25 gray-zone can cause label flicker at 5m
(documented limitation; mitigable with hysteresis), but this is the known trade-off for the
SPEC-defined canonical framework.

**Why it fits Phase 3:** Emits one canonical enum and a framework-internal confidence per bar
with a clean `usable_from_timestamp = bar_t + 5min`, making it trivially join-able to trade
entry/exit timestamps.

**Why it was not mixed:** The volatility feature (ATR percentile) used to split `volatile` vs
`range` is the framework's own internal auxiliary (explicitly sanctioned by skill §3/§6), not a
second co-primary family. No rule from any other family enters the classifier.

**Best-for-rubric, not proven-optimal:** it scored highest (4.850 vs Dow 4.050) under the
selection rubric and current constraints (causal, OHLCV-only, interpretable, Phase-3-join) — this
is **not** a claim of statistical optimality. Alternatives (Dow structure, HMM/Markov switching,
volatility-state models) remain open and should be compared empirically once data is available.
Grounding is **tiered**: ADX/DMI = strong (Wilder); multi-EMA *alignment* = standard practitioner;
the 9/21/55, ADX-25, and P70 values are repository/SPEC conventions, not academically-derived optima.

**Rejected alternatives summary:**

| candidate | rejection reason |
|---|---|
| TREND_STRENGTH_ADX_DMI_DIR | Lower SPEC alignment; `transition` requires arbitrary tolerance not in Wilder. Secondary. |
| TREND_STRENGTH_EMA_ONLY_SLOPE | Drops the ADX strength gate required by SPEC; false directional labels in ranges. |
| All 4 volatility candidates | Directional gap — cannot map strong_up/strong_down as standalone primaries. |
| PA_MS_001_dow_structure | Lower causal_safety (pivot-lag; ZigZag look-ahead trap); higher complexity. Future-research. |
| PA_MS_002_bos_choch | Practitioner-derived; reference impl is look-ahead biased. Future-research. |
| PA_MS_003_wyckoff | High complexity; subjective; designed for daily bars. Future-research. |
| stat_hmrs_hamilton | HARD GATE: low causal_safety; no data for train-only fit. Future-research. |
| stat_hmm_gaussian | HARD GATE: Viterbi is non-causal; no data for train fit. Future-research. |
| stat_gmm_regime | HARD GATE: whole-data fit trap; no data; no temporal structure. Exploratory only. |
| stat_vol_clustering | HARD GATE: centroid fit on full data; no data; atheoretic count. Exploratory only. |
| SL_01_session_window | HARD GATE: very low SPEC alignment — classifies environment, not price direction. |
| SL_02_funding_proximity | HARD GATE: cannot map canonical price regimes. Phase 3 annotation only. |
| SL_03_volume_microstructure | Cannot map directional regimes; data absent this run. Secondary. |

---

## §35.5 Regime Definition Summary

All five canonical regimes, defined by the selected framework's rules:

| regime | rule | core features | expected behavior |
|---|---|---|---|
| strong_up | ADX(14) >= 25 AND EMA9 > EMA21 > EMA55 | ADX14, EMA9/21/55 | upward drift, HH/HL; trend-following longs |
| strong_down | ADX(14) >= 25 AND EMA9 < EMA21 < EMA55 | ADX14, EMA9/21/55 | downward drift, LH/LL; trend-following shorts |
| transition | ADX(14) >= 25 AND EMA alignment mixed | ADX14, EMA9/21/55 | whipsaw/reversal risk |
| volatile | ADX(14) < 25 AND ATR percentile >= P70 | ADX14, volatility_score | large directionless swings; breakout-fakeout risk |
| range | ADX(14) < 25 AND ATR percentile < P70 | ADX14, volatility_score | mean-reverting band; mean-reversion favored |

`all` is not a per-bar regime — it is the Phase 3 unconditional-aggregation bucket only and
never appears as a row value in `regime_labels.csv`.

Threshold policy: ADX gate = 25 (repository/SPEC value and common TA convention, not a Wilder-derived constant); P70 cutoff = fixed design convention
applied to a causal trailing ATR(14) percentile (window W=2016 bars, min 288). Neither threshold
was tuned to Phase 2/3 performance or a test set.

---

## §35.6 Feature Catalog Summary

Full catalog: `regime_feature_catalog.csv` (31 features; 32 lines incl. header).

**Selected-framework features** (`selected_framework_feature=true`, 7 features):

| feature_id | feature_name | category | lookback | causal_safe | purpose |
|---|---|---|---:|---|---|
| F001 | EMA9 | trend | 9 | true | direction (fast EMA) |
| F002 | EMA21 | trend | 21 | true | direction (mid EMA) |
| F003 | EMA55 | trend | 55 | true | direction (slow EMA) |
| F004 | ema_alignment_state | trend | 55 | true | direction classification |
| F005 | ADX14 | trend | 14 | true | trend-strength gate |
| F006 | ATR14 | volatility | 14 | true | basis for volatility_score |
| F007 | volatility_score | volatility | 2016 | true | volatile vs range split |

All 7 have `causal_safe=true` and `usable_from_rule=next_bar`. All other 24 catalog rows have
`selected_framework_feature=false` (survey / rejected / secondary candidates). No performance
column appears in the catalog; `lookahead_risk` for the 7 selected features is `low` or `medium`
(F007 medium due to the rolling window, which is documented as strictly trailing).

---

## §35.7 Labeling Pipeline Summary

| aspect | value |
|---|---|
| bar timestamp meaning | bar close time (UTC) |
| usable_from rule | `usable_from_timestamp = timestamp + 5min` (strictly later; next bar open) |
| warmup_end | bar 288 (max of ADX stable ~150, EMA55 ~55, vol window min 288) |
| causal label file | `regime_labels.csv` (GENERATED — 210,227 labeled bars; 301 warmup) |
| smoothed labels | none produced; if ever made go to `smoothed_regime_labels.csv` with `usable_in_hybrid=false` |
| posthoc labels | none produced; if ever made go to `posthoc_regime_labels.csv` with `usable_in_hybrid=false` |
| Phase 3 join key | latest causal label where `usable_from_timestamp <= trade.timestamp_entry` |
| llm_discretion_used | false for all labels; a true value invalidates a row |
| label separation | causal / smoothed / posthoc strictly in separate files; never mixed |
| reproducibility | deterministic (no randomness, no model fit, no LLM override); identical OHLCV → identical labels |

Phase 3 performs the join; Phase 4 only specifies it. Phase 3 writes
`regime_enriched_trades.csv` / `regime_enriched_trade_logs.jsonl`; it never overwrites Phase 2
`trades.csv`.

---

## §35.8 Prediction Research Summary (Stage B)

| field | value |
|---|---|
| stage_b_status | completed (research design; methodology-only) |
| scope | Stage B initiated after Stage A COMPLETE (user request). Design-only — no data, so no model is trained/validated; auxiliary to Stage A and not a core Phase 4 completion requirement. |
| stage_b_started_after_stage_a | true |
| regime_prediction_research.md | produced — horizons (3/6/12/24/48 bars), 7 targets, model tiers (rule-based transition baseline → logistic/Markov/HMM → RF/GBM/XGBoost) |
| regime_prediction_label_spec.md | produced — future labels as supervised targets only; strict feature(≤t)/label(>t) separation + embargo gap |
| regime_prediction_validation_plan.md | produced — walk-forward/expanding/rolling time split; forbidden-split list; metrics; leakage test suite |

Stage B has been designed (the three files above). When executed on data it must: (a) keep the
current causal classifier unchanged, (b) never feed a future label as a current-regime feature,
(c) use walk-forward validation with train-only model fit, and (d) be treated as
auxiliary/probabilistic — never a current-regime label for Phase 3.

---

## §35.9 Look-ahead Validation Table

Evidence per checklist row. Source: `lookahead_bias_prevention_checklist.md`.

| check | result | evidence location |
|---|---|---|
| feature uses bars <= t only | yes | classifier spec §6/§7/§8; causal-auditor check 1 PASS |
| current-close feature usable only from next bar | yes | `usable_from_timestamp[t] = timestamp[t]+5min`; classifier §9/§11; pipeline §6; schema row 2 |
| no future return in a current feature | yes | no future-return term anywhere; causal-auditor check 2 PASS |
| no future high/low/min/max in a current feature | yes | ATR percentile strictly trailing; no future H/L/min/max; classifier §8; causal-auditor check 2 |
| label separated from feature | yes | labels in schema, features in catalog; distinct columns |
| selected framework is theory-grounded | yes | Wilder ADX/DMI + standard multi-EMA alignment + Mandelbrot/Engle vol clustering; research §3.1 |
| exactly one primary framework | yes | one `selected_as_primary=true` in matrix (TREND_STRENGTH_ADX_EMA_SPEC) |
| no arbitrary mixing | yes | only the framework's own ATR-percentile vol split; no other family rule; causal-auditor check 4 PASS |
| rejected frameworks documented | yes | 16 rejected rows with rejection_reason in matrix; research §3-4 |
| scaler fit train-only (if used) | n/a | no scaler used; rule-based; no fit performed |
| threshold fit train-only (if adaptive) | n/a | thresholds fixed convention/SPEC values (ADX=25, P70), not theory-derived; not tuned to performance |
| clustering fit train-only (if used) | n/a | no clustering in selected framework; statistical candidates rejected |
| no Phase 2 result used | yes | no Phase 2 artifact read; isolation stated in manifest and research |
| no Phase 3 result used | yes | no Phase 3 artifact read |
| causal labels separated from smoothed/posthoc | yes | only causal labels produced; no smoothed/posthoc files exist (pipeline §11) |
| Phase 2 artifacts not modified | yes | no Phase 2 artifact exists/was touched; outputs confined to run dir |
| regime_labels.csv has no strategy-performance column | yes | generated file verified: 20 schema columns, 0 of 14 forbidden (causal-auditor grep) |
| llm_discretion_used is false for all labels | yes | generated file: llm_discretion_used=false on all 210,528 rows (verified) |

Summary: 15 rows `yes`, 3 rows `n/a` (no scaler / no adaptive-fit threshold / no clustering —
genuinely unused), 0 rows `false`. Label-dependent rows now verified on the real generated labels.
Checklist PASSED.

---

## §35.10 Stage A Completion Table

| gate | deliverable / check | result | evidence |
|---|---|---|---|
| G1-a | regime_framework_research.md present | PASS | file present; 17 candidates, 5 families, selection documented |
| G1-b | regime_framework_selection_matrix.csv present | PASS | file present; 17 rows; 1 primary; 16 rejected with reasons |
| G1-c | selected_primary_regime_framework.md present | PASS | file present; named TREND_STRENGTH_ADX_EMA_SPEC |
| G1-d | market_regime_definition.md present | PASS | file present; 5 canonical regimes defined |
| G1-e | causal_regime_classifier_spec.md present | PASS | file present; 18 sections; all features causal |
| G1-f | regime_feature_catalog.csv present | PASS | file present; 31 features; 7 selected-framework features |
| G1-g | regime_labeling_pipeline_spec.md present | PASS | file present; full pipeline specified |
| G1-h | regime_labels_schema.md present | PASS | file present; 20 columns; 14 forbidden columns enumerated |
| G1-i | phase3_usage_contract.md present | PASS | file present; 12 sections |
| G1-j | lookahead_bias_prevention_checklist.md present | PASS | file present; 18 rows; 0 false |
| G1-k | phase4_manifest.json present | PASS | file present; all required fields verified |
| G1-l | regime_labels.csv | PRESENT | generated; 210,528 rows; causal; 0 forbidden columns |
| G1-m | data_quality_report.md | PRESENT | data-quality PASS (0 dup/gap/OHLC violations) |
| G2 | look-ahead checklist all passed | PASS | 15 yes + 3 n/a + 0 false |
| G3 | exactly one selected_as_primary=true in matrix | PASS | TREND_STRENGTH_ADX_EMA_SPEC only; 16 rejected |
| G3-x | internal consistency (matrix / framework doc / definition / manifest) | PASS | all four name TREND_STRENGTH_ADX_EMA_SPEC |
| G4 | causal-auditor PASS | PASS | stated in checklist header and manifest notes; deliverables consistent |
| G5 | 14 forbidden columns absent from schema; llm_discretion_used fixed false | PASS | all 14 enumerated and absent from 20-column schema |
| G6 | manifest isolation flags | PASS | phase2_results_used=false, phase3_results_used=false, phase4_outputs_used_in_phase2=false, intended_consumer=phase3_only, llm_discretion_used=false, lookahead_check_passed=true, stage_a=completed, stage_b=completed |

All gates: PASS.

---

## §35.11 Phase 3 Handoff

**What Phase 3 reads** (from `reports/phase4_market_regime/20260613_0558/`):
- `regime_labels.csv` — causal per-bar labels (the join source; GENERATED — 210,528 rows, 2024-01-01..2025-12-31, causal)
- `regime_labels_schema.md` — column and value contract (20 columns, 14 forbidden columns enumerated)
- `market_regime_definition.md` — canonical regime meanings and the value for `edge_fragment.regime`
- `causal_regime_classifier_spec.md`, `regime_labeling_pipeline_spec.md` — join algorithms
  and causal-timing rules
- `phase3_usage_contract.md` — full handoff contract

**What Phase 3 generates** (new files, never overwriting Phase 2 artifacts):
- `regime_enriched_trades.csv` / `regime_enriched_trade_logs.jsonl`

**What Phase 3 must not do:**
- Modify Phase 2 `trades.csv` / `signals.csv` / `result.json` / `portfolio.csv`
- Use smoothed or posthoc labels as the basis for hybrid eligibility
- Retroactively edit regime definitions, thresholds, or framework selection
- Treat Stage B prediction output (if any) as a current-regime label

**Hybrid eligibility rule:**
Only `regime_labeling=causal` labels may serve as the basis for `usable_in_hybrid` in Phase 3.
`usable_in_hybrid` is a Phase 3 concept and never appears as a column in `regime_labels.csv`.

**Join algorithm** (Phase 3 performs; Phase 4 specifies):

BEGIN_PSEUDOCODE
for each trade:
    entry_time = trade.timestamp_entry
    exit_time  = trade.timestamp_exit
    regime_at_entry = latest causal label where usable_from_timestamp <= entry_time
    regime_at_exit  = latest causal label where usable_from_timestamp <= exit_time
    holding_period_regime_path = all causal labels with
        usable_from_timestamp >= entry_time and usable_from_timestamp <= exit_time
    if no causal label has usable_from_timestamp <= entry_time:
        regime_at_entry = "unknown_or_warmup"
END_PSEUDOCODE

**Lifecycle transition:** Phase 3 may set `strategy_profile.lifecycle_status = analyzed` only
after completing regime-conditional performance analysis. Phase 4 writes no DB row and performs
no lifecycle transition.

---

## §35.12 Limitations and Next Research

### Limitations of this run

| limitation | impact | mitigation / next step |
|---|---|---|
| (Resolved 2026-06-14) Data-present run completed | `regime_labels.csv` generated + validated on 210,528 bars; data-quality PASS; acceptance tests PASS | None — see §35.14. Re-profile only if a different period/dataset is used |
| SPEC.md / existing regime code not present | None — SPEC.md is not required for a methodology-only phase; the `regime-classification` skill is the canonical-vocabulary + repository-defined-framework source of truth by design, and `repository_spec_alignment` is correctly scored against it; the existing-classifier-vs-SPEC discrepancy check is not applicable (no existing classifier to reconcile) | None required. If a backtest service with its own MarketRegime enum later exists, reconcile enum names at integration time |
| research_db not queried | Schema and canonical-mapping confirmation from the DB is unverified | Restore DB connectivity; run a SELECT-only schema check (read-only role); record any discrepancy |
| Not a git repo | `git_commit = n/a`; reproducibility relies solely on the spec file contents | Initialize a git repo or confirm version tracking; record commit hash in future runs |
| ADX 20-25 gray-zone at 5m | Label flicker at the ADX boundary; labels may oscillate between `transition` and `strong_up`/`strong_down` near the gate | Consider a hysteresis rule (confirmed only after N bars above/below threshold); document as a spec amendment and confirm against train data |
| Short-intraday horizon only | EMA9/21/55 ≈ 45/105/275 min (EMA55 ≈ 4.6h); classifier sees only short-intraday regime, not higher-timeframe context | Optional future multi-timeframe extension: anchor 5m labels within causal 1h/4h structure |
| ATR percentile cold-start (< 288 bars) | First ~288 bars are `unknown_or_warmup`; low-confidence until W_min reached | Expected; warmup rows excluded from Phase 3 hybrid eligibility |
| Threshold *trading-appropriateness* still open | ADX=25 / P70 are fixed convention/SPEC values; the ETH/USDT 5m distribution is now profiled (§35.14) and the splits are sane, but whether they are optimal *for trading* is a Phase-3 question | Phase 3 evaluates regime-conditional performance; do NOT tune thresholds to performance |
| Stage B is design-only (no data) | Prediction models not trained/validated (methodology-only) | Execute Stage B (train + walk-forward validate) when OHLCV is present, per regime_prediction_validation_plan.md |

### Next research priorities

1. (COMPLETED 2026-06-14) Data-present run executed on real ETH/USDT 5m OHLCV (210,528 bars);
   `regime_labels.csv` and `data_quality_report.md` produced and validated.
2. (Integration-time only, optional) If a backtest service with a `MarketRegime` enum later
   exists, reconcile enum names — not required for this methodology-only phase.
3. DB schema check: restore research_db connectivity; verify canonical-regime enum mapping.
4. Hysteresis design: evaluate an ADX hysteresis rule on the train period to reduce 5m label
   flicker; document as a spec amendment.
5. Stage B execution: the prediction research design is complete (3 files); train and
   walk-forward-validate the models when OHLCV is present, starting from the rule-based
   transition-matrix baseline.
6. Secondary annotations for Phase 3: session-window and funding-proximity no-trade filters
   (SL_01, SL_02) are ready-to-implement; volume/microstructure confidence layer (F070-F071)
   pending data.

---

## §35.13 Usage readiness & acceptance criteria

**Status (2026-06-14):** methodology/deliverable complete **and** the data-present acceptance run
PASSED on real ETH/USDT 5m OHLCV. Validated as a **causal current-regime classifier on this
dataset**. (Whether the thresholds are *appropriate for trading* is a Phase-3 question — Phase 4
only profiled the distribution; it did not tune to performance.)

**Usable now:**
- The causal classifier spec + the deterministic `build_regime_labels.py`.
- The generated causal `regime_labels.csv` (210,227 labeled bars) for Phase 3 trade/period joins.
- The Phase 3 trade/period-join contract.

**Still Phase 3's responsibility (not done here):**
- Regime-conditional strategy conclusions and hybrid / no-trade eligibility (Phase 3 does this
  *using* these causal labels; Phase 4 does not).
- Judging whether ADX=25 / P70 are appropriate *for trading* (distribution profiled in §35.14;
  threshold *tuning* is out of scope by rule).

**Minimum acceptance criteria — ALL PASSED (see §35.14, `validation_results.md`):**
1. OHLCV data-quality checks (skill §8a) — ✅ PASS.
2. Generate causal `regime_labels.csv` — ✅ 210,528 rows.
3. Profile distribution / durations / transitions (sanity, not tuning) — ✅ done.
4. Unit tests (§33.2) + slice-invariance (§33.3) — ✅ PASS (40/40 slice samples).
5. Warmup + inclusive-boundary (ADX=25, P70) validation — ✅ PASS.

All five pass → a validated current-regime classifier on the supplied dataset (a research
classifier; production trading use remains subject to Phase 3 analysis).

---

## §35.14 Data-present execution results (2026-06-14)

**Source:** `/home/vessel/workspace/trading-system/backtestdata/ETHUSDT_futures_5min.csv` —
ETH/USDT 5m OHLCV, 210,528 bars, 2024-01-01 00:00:00 → 2025-12-31 23:55:00 (UTC). Compute:
`trading-system/.venv` (pandas 2.1.4). Generator: `build_regime_labels.py` (deterministic).

**Data quality (`data_quality_report.md`): PASS** — strictly ascending timestamps, 0 duplicates,
0 five-minute gaps, 0 OHLC-relationship violations, no negative prices. Documented non-fatal:
21 zero-volume bars, 9 extreme-spike (>5% close-to-close) bars; both retained.

**Labels (`regime_labels.csv`):** 210,528 rows; 301 `unknown_or_warmup`; 210,227 labeled. Causal;
`regime_labeling=causal`; `llm_discretion_used=false`; schema-conformant (0 forbidden columns).

| regime | count | % of labeled |
|---|---:|---:|
| range | 93,834 | 44.63% |
| strong_down | 42,541 | 20.24% |
| strong_up | 39,456 | 18.77% |
| volatile | 24,866 | 11.83% |
| transition | 9,530 | 4.53% |

Context: ADX≥25 on 43.5% of labeled bars; vol_score≥70 on 30.4% of no-trend bars. The transition
matrix is strongly diagonal (regimes persist); median run length ~14–18 bars for trend regimes,
~4 for transition (`regime_transition_matrix.csv`, `regime_duration_distribution.csv`).

**Acceptance tests (`validation_results.md`): ALL PASS** — unit tests (five regimes + warmup +
inclusive boundaries ADX=25→trend, vol=70→volatile + confidence); slice-invariance (40 sampled
bars recomputed on `data[0:t+1]` == full-series label, 0 failures); `usable_from_timestamp >
timestamp` on all rows; first 288 rows `unknown_or_warmup`.

**Independent review:** `causal-auditor` PASS on the realized labels + `build_regime_labels.py`
(no `.shift(-k)`, no `center=True`, no whole-sample percentile; trailing `rolling(2016).rank`
confirmed; indicators bars ≤ t only; isolation held).

**Convention note:** the implemented ATR percentile uses pandas
`rolling(2016,min_periods=288).rank(pct=True)` (count/len) — a <0.04% tie-convention difference
from the spec's `(count−1)/(len−1)`; both strictly trailing and causal (classifier spec §8). The
effective warmup is 301 bars (vol_score needs 288 ATR values).
