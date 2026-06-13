---
name: regime-classification
description: Apply this skill for Phase 4 market-regime research on ETH/USDT 5m USDT-M perpetual futures. It is the single source of truth for the canonical regime vocabulary and the repository-defined trend-strength framework, the five theory-grounded framework families to survey, the 7-criterion selection-matrix rubric and the no-mixing principle, the causal feature-timing and usable_from_timestamp rules, the causal/smoothed/posthoc label separation, the current-regime output JSON schema, the regime_labels.csv schema and forbidden columns, the Phase 3 trade-join algorithm, the Stage A / Stage B deliverables, the look-ahead-bias prevention checklist, the absolute prohibitions, and the MCP-down fallback. Used by the orchestrator, framework-scout, causal-auditor, data-agent, completeness-auditor, and prediction-researcher.
---

# Regime Classification Skill (Phase 4)

The durable contract for defining the CURRENT market regime of ETH/USDT 5m USDT-M perpetual
futures and a causal labeling pipeline whose only consumer is Phase 3. **Phase 4 is an
independent study: it reads no Phase 2/3 artifact, writes no DB row, and never lets the LLM
invent a regime.** The detailed framework-family descriptions, the candidate-record schema, and
the scoring weights live in `${CLAUDE_SKILL_DIR}/references/framework-families.md`.

## 0. Stage gate

Phase 4 has two layers. **Stage A (current-regime classification) is mandatory**; **Stage B
(future-regime prediction) is optional** and starts ONLY after Stage A is complete. Stage A
completion is the core objective — a skipped Stage B does not fail Phase 4, but a missing Stage A
deliverable does. Never start Stage B before Stage A is COMPLETE.

## 1. Isolation (non-negotiable)

- **No Phase 2 input:** result.json, trades.csv, portfolio.csv, signals.csv, and any
  per-strategy return / win-rate / profit-factor / MDD / Sharpe.
- **No Phase 3 input:** edge_fragment, strategy_evaluation, any after-the-fact "strategy X made
  money in period Y" information.
- **Read-only DB:** schema check, SPEC-vs-schema consistency, lifecycle_status read, and Phase 3
  query drafts only. No INSERT/UPDATE/DELETE/DDL; no writing strategy_profile / experiment /
  strategy_variant / edge_fragment / strategy_evaluation; no lifecycle transition; no hybrid
  materialization.
- **Allowed inputs:** ETH/USDT 5m OHLCV; optional funding_rate / open_interest /
  taker_buy_sell / liquidation / bid_ask_spread; public TA & regime theory; existing repository
  causal-regime code; the SPEC canonical vocabulary and the existing MarketRegime enum mapping.
- **Outputs are for Phase 3 only**, under `reports/phase4_market_regime/{YYYYMMDD_HHMM}/`. Never
  modify a Phase 2 artifact; never add a regime column to Phase 2 trades.csv/signals.csv.

## 2. Canonical regime vocabulary (do not alter)

`strong_up` · `strong_down` · `transition` · `volatile` · `range`. Plus `all`, which is NOT a
market state — it is the Phase 3 unconditional-aggregation bucket only. A framework more granular
than this must MAP onto these five; a framework that cannot map is not eligible as primary.
Extra ideas are recorded as `experimental_regime_candidate`, never as a silent replacement.

## 3. Repository-defined trend-strength framework (the SPEC default candidate)

This is ONE candidate (high SPEC alignment), not an automatic winner — it must still be justified
through the selection matrix:

- `strong_up`: ADX(14) >= 25 and EMA9 > EMA21 > EMA55
- `strong_down`: ADX(14) >= 25 and EMA9 < EMA21 < EMA55
- `transition`: ADX(14) >= 25 and EMA alignment is neither strong_up nor strong_down
- `volatile`: ADX(14) < 25 and the volatility feature is high
- `range`: ADX(14) < 25 and the volatility feature is not high

Combining ADX with EMA alignment here is **repository-defined**, not arbitrary mixing. Volatility
is used only to split volatile vs range.

## 4. The five framework families to survey

Survey ALL five, recording each candidate's select/reject reason (full detail in the references
file): (1) trend-strength (ADX/DMI + moving-average alignment), (2) volatility regime (ATR /
realized-vol percentile, Bollinger width, compression/expansion), (3) price-action /
market-structure (Dow theory, higher-high/lower-low, swing structure — needs causal pivot
confirmation), (4) statistical (Hidden Markov / regime-switching / Gaussian mixture — needs
train-only fit + walk-forward), (5) session / liquidity (time-of-day, funding proximity, volume —
usually a no-trade filter / secondary annotation, not a primary price regime).

## 5. Selection matrix — score, then pick ONE

Score each candidate on seven weighted criteria (weights sum to 1.0):

| criterion | weight |
|---|---|
| theoretical_basis_strength | 0.20 |
| repository_spec_alignment | 0.20 |
| causal_safety | 0.20 |
| interpretability | 0.15 |
| data_availability | 0.10 |
| implementation_complexity | 0.10 |
| phase3_join_usability | 0.05 |

**Hard gates (override the score):** low `causal_safety` → never primary; very low
`repository_spec_alignment` → never primary; weak theoretical basis → never primary. Among the
survivors, the highest weighted score becomes the primary. Write the scores to
`regime_framework_selection_matrix.csv` (columns in the references file) and the narrative to
`regime_framework_research.md` + `selected_primary_regime_framework.md`.

## 6. No-mixing principle

Allowed: one primary framework; other frameworks documented as comparison candidates,
secondary annotation, or future research; a mapping layer onto the canonical vocabulary;
auxiliary indicators that the chosen theory ALREADY uses together (e.g. ADX + EMA alignment, or
a volatility feature to split volatile/range). Forbidden: blending ADX rules + HMM states +
Bollinger squeeze + price-action pivots into one classifier; cherry-picking the best-looking
condition from each family; an unexplainable weighted-score ensemble as the primary label;
adjusting the mix by looking at Phase 2/3 results.

## 7. Current-regime definition method

Define the current regime ONLY by the selected framework's rules, on bars <= t, emitting
`regime` + `regime_confidence` (confidence uses only the framework's internal basis). The LLM
never overrides a label by "this looks like an uptrend". Output record:

BEGIN_JSON
{
  "timestamp": "",
  "usable_from_timestamp": "",
  "symbol": "ETH/USDT",
  "timeframe": "5m",
  "selected_primary_framework": "",
  "regime": "",
  "regime_confidence": 0,
  "feature_snapshot": {},
  "matched_framework_rules": [],
  "alternative_regimes_within_same_framework": [],
  "why_this_regime_by_framework_rule": "",
  "why_not_other_regimes_by_framework_rule": "",
  "llm_discretion_used": false,
  "notes": ""
}
END_JSON

`llm_discretion_used` must always be false; a true value makes the label invalid.

## 8. Causal feature timing + usable_from_timestamp

A feature computed from bar t's close is known only after bar t closes, so it is usable for a
decision or a Phase 3 trade-join only from the NEXT bar. Always record `usable_from_timestamp`,
and it must be strictly later than the bar timestamp. Rolling high/low must state whether the
current bar is included. Never treat a current bar's high/low as knowable at the bar's open.
For a Phase 3 trade, attach the most recent causal label whose `usable_from_timestamp <=
trade.timestamp_entry`.

## 8a. Data-quality checks (run before any labeling)

`data-agent` validates the OHLCV before any feature/label is computed: timestamps strictly
ascending; zero duplicate timestamps; 5-minute gaps identified; OHLC relationship valid
(high ≥ max(open, close), low ≤ min(open, close), high ≥ low); no negative price or volume;
zero-volume and extreme-spike bars flagged; data start/end dates confirmed; optional-data
(funding / open_interest / liquidation) coverage measured; timezone basis confirmed; feature
availability checked against live timing. A **fatal** issue (out-of-order or duplicate
timestamps, broken OHLC) means NO labels are produced. A **correctable** issue is documented
with the correction method and its impact. Results go to `data_quality_report.md`.

## 9. Three label kinds — keep them apart

- **causal:** bars <= t only; reproducible live; the ONLY primary label and the ONLY
  hybrid-eligibility basis in Phase 3.
- **smoothed:** may reference neighboring/future bars to de-noise; visualization / post-hoc aid
  only; `usable_in_hybrid=false`; never a hybrid basis.
- **posthoc:** labeled after seeing the whole segment; not live-reproducible; toxic-zone scouting
  / research only; `usable_in_hybrid=false`.

The core Stage A output is the causal pipeline. smoothed/posthoc may exist but live in SEPARATE
files — never mixed into the causal label file.

## 10. regime_labels.csv schema (causal file)

Columns: `timestamp`, `usable_from_timestamp`, `symbol`, `timeframe`, `regime`, `regime_alt`,
`regime_labeling` (="causal"), `regime_confidence`, `selected_primary_framework`, `trend_score`,
`volatility_score`, `momentum_score`, `mean_reversion_score`, `volume_score`,
`data_quality_score`, `feature_snapshot_ref`, `classifier_version`, `source_data_path`,
`git_commit`, `llm_discretion_used` (always false).

`regime` ∈ the five canonical values. `usable_from_timestamp` > `timestamp` (typically the next
5m bar for close-based labels). smoothed/posthoc labels go to their own files.

**Forbidden columns** (these would couple labels to strategy results): `strategy_id`,
`variant_id`, `trade_id`, `net_pnl`, `return_pct`, `future_return`, `future_max_price`,
`future_min_price`, `future_profit`, `phase2_result`, `edge_fragment_id`, `usable_in_hybrid`,
`polarity`, `strategy_evaluation_verdict`.

## 11. Phase 3 trade-join algorithm (Phase 3 performs this; Phase 4 only specifies it)

BEGIN_PSEUDOCODE
for each trade:
  entry_time = trade.timestamp_entry
  exit_time  = trade.timestamp_exit
  regime_at_entry = latest causal label where usable_from_timestamp <= entry_time
  regime_at_exit  = latest causal label where usable_from_timestamp <= exit_time
  holding_period_regime_path = all causal labels with
      usable_from_timestamp >= entry_time and usable_from_timestamp <= exit_time
END_PSEUDOCODE

This join runs in Phase 3 only. Phase 3 writes `regime_enriched_trades.csv` /
`regime_enriched_trade_logs.jsonl`; it never overwrites the Phase 2 trades.csv. If no causal
label is usable before entry, mark the trade `unknown_or_warmup` or exclude it from analysis.

## 12. Deliverables

**Stage A (mandatory)** under `reports/phase4_market_regime/{YYYYMMDD_HHMM}/`:
`phase4_manifest.json`, `regime_framework_research.md`, `regime_framework_selection_matrix.csv`,
`selected_primary_regime_framework.md`, `market_regime_definition.md`,
`causal_regime_classifier_spec.md`, `regime_feature_catalog.csv`,
`regime_labeling_pipeline_spec.md`, `regime_labels_schema.md`, `regime_labels.csv` (if data is
present), `lookahead_bias_prevention_checklist.md`, `phase3_usage_contract.md`,
`phase4_final_report.md`.

**Stage B (optional, after Stage A):** `regime_prediction_research.md`,
`regime_prediction_label_spec.md`, `regime_prediction_validation_plan.md`.

**Optional artifacts:** `smoothed_regime_labels.csv`, `posthoc_regime_labels.csv`,
`unsupervised_regime_candidates.csv`, `regime_transition_matrix.csv`,
`regime_duration_distribution.csv`, `feature_snapshot.parquet`, `data_quality_report.md`.

## 12a. Final report (phase4_final_report.md) — required contents

Run summary (symbol, timeframe, period, Stage A / Stage B status, selected primary framework,
primary labeling method, `phase2_results_used=false`, `phase3_results_used=false`, intended
consumer = Phase 3); framework-survey summary; selection-matrix summary (criterion → selected
vs next-best score); the selected framework (why it fits ETH/USDT 5m, why it fits Phase 3, why
it was not mixed, rejected alternatives); regime-definition summary; feature-catalog summary;
labeling-pipeline summary (timestamp meaning, `usable_from` rule, causal label file,
smoothed/posthoc separation, Phase 3 join key, `llm_discretion_used=false`); look-ahead
validation (each checklist row → passed + evidence); the Stage A completion table; the Phase 3
handoff (what Phase 3 reads / generates / must not modify / must use causal-only for hybrid
eligibility); and limitations + next research. Markdown-stable (no nested fences).

## 13. phase4_manifest.json (key fields)

BEGIN_JSON
{
  "phase": "phase4_market_regime",
  "primary_objective": "current_market_regime_classification",
  "secondary_objective": "future_regime_prediction_research_optional",
  "symbol": "ETH/USDT", "market": "Binance USDT-M perpetual futures", "timeframe": "5m",
  "canonical_regimes": ["strong_up", "strong_down", "transition", "volatile", "range", "all"],
  "primary_labeling_method": "causal",
  "selected_primary_framework": "",
  "stage_a_current_classification_status": "completed | failed | partial",
  "stage_b_prediction_research_status": "completed | skipped | partial",
  "stage_b_started_after_stage_a_completed": true,
  "phase_complete_condition": "stage_a_completed",
  "prediction_required_for_phase_completion": false,
  "phase2_results_used": false, "phase3_results_used": false,
  "phase4_outputs_used_in_phase2": false, "intended_consumer": "phase3_only",
  "lookahead_check_passed": true, "llm_discretion_used": false,
  "causal_classifier_version": "", "regime_labels_file": "", "git_commit": "", "notes": ""
}
END_JSON

## 14. Look-ahead-bias prevention checklist (every row must pass)

feature uses bars <= t only · current-close feature usable only from next bar · no future
return in a current feature · no future high/low/min/max in a current feature · label separated
from feature · selected framework is theory-grounded · exactly one primary framework · no
arbitrary mixing · rejected frameworks documented · scaler fit train-only (if used) · threshold
fit train-only (if adaptive) · clustering fit train-only (if used) · no Phase 2 result used · no
Phase 3 result used · causal labels separated from smoothed/posthoc · Phase 2 artifacts not
modified · regime_labels.csv has no strategy-performance column · llm_discretion_used is false
for all labels. **Any false → Stage A is not complete.** Record evidence + failure-action per row
in `lookahead_bias_prevention_checklist.md`.

## 15. Threshold policy

Priority: SPEC / existing-code thresholds → train-period percentile → walk-forward rolling
percentile → theory-based fixed threshold. Never tune a threshold to Phase 2 performance, Phase 3
results, the test set, or to make a strategy's edge look larger.

## 16. MCP / DB unavailable — fallback (do NOT claim a DB read happened)

If the research_db MCP is down, proceed with file-based work (the DB is only used read-only for
schema/lifecycle confirmation and Phase 3 query drafts). Record the unavailability in
`phase4_final_report.md` and mark any schema assumption as unverified rather than asserting it.

## 17. Markdown-stability rules (all reports)

No nested triple-backtick code fences. Use `BEGIN_JSON`/`END_JSON`, `BEGIN_SQL`/`END_SQL`,
`BEGIN_PSEUDOCODE`/`END_PSEUDOCODE` markers. Keep long JSON/SQL out of tables.

## Related skills

- `genius-thinking` — PR/MDA/IS for the framework selection (the matrix is an IS evaluation)
- `quant-backtest` — the canonical look-ahead bias rules (signal timing, shift)
- `statistical-validation` — train-only fit, walk-forward, no shuffle split (review + Stage B)
- `ml-strategy` — walk-forward training, label construction, model choice (Stage B)
- `crypto-derivatives` — funding / basis / OI inputs for the volatility & session/liquidity families
- `decimal-arithmetic-discipline` — numerically honest ADX/EMA/ATR threshold comparisons
