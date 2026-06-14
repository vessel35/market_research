# Phase 3 Usage Contract

**Producer:** Phase 4 (this run, 20260613_0558) · **Sole consumer:** Phase 3.
Phase 4 outputs are for Phase 3 ONLY; they are never used in Phase 2 and never modify Phase 2
artifacts. `regime_labeling=causal`; `llm_discretion_used=false`.

**Readiness:** `regime_labels.csv` has been **generated and validated** on real ETH/USDT 5m OHLCV
(210,528 rows; data-quality PASS; acceptance tests PASS; causal-auditor PASS — see
`phase4_final_report.md` §35.13/§35.14). Phase 3 may consume it as the join source. Drawing
regime-conditional conclusions and hybrid/no-trade decisions is Phase 3's task (using these causal
labels); judging whether the thresholds are appropriate *for trading* is also Phase 3's.

## 1. Files Phase 3 reads

From `reports/phase4_market_regime/20260613_0558/`:
- `regime_labels.csv` — the causal per-bar labels (the join source). **Generated** (210,528 rows);
  follows `regime_labels_schema.md` exactly.
- `regime_labels_schema.md` — column + value contract (use until the CSV exists).
- `market_regime_definition.md` — canonical regime meanings + the value to use for
  `edge_fragment.regime`.
- `causal_regime_classifier_spec.md`, `regime_labeling_pipeline_spec.md` — join algorithms and
  causal-timing rules.
Phase 3 must NOT read Phase 2 result artifacts to "derive" regimes — it uses these labels only.

## 2. Canonical regimes Phase 3 uses

`strong_up`, `strong_down`, `transition`, `volatile`, `range` (per-bar), and `all` for
unconditional aggregation only. `unknown_or_warmup` rows are excluded from regime-conditional
analysis and from hybrid eligibility.

## 3. Trade-join rule

For each trade, attach the most recent causal label with
`usable_from_timestamp <= trade.timestamp_entry` (entry regime) and likewise for exit; the
holding-period path is all causal labels with `usable_from_timestamp` in `[entry, exit]` (see
`regime_labeling_pipeline_spec.md` §8). If no causal label is usable before entry, mark
`unknown_or_warmup` or exclude the trade. Period/daily joins use §9 of the pipeline spec.

## 4. Value for `edge_fragment.regime_labeling`

Always `causal` when sourced from `regime_labels.csv`. Phase 3 must not relabel a causal label as
smoothed/posthoc or vice versa.

## 5. Scope for smoothed/posthoc labels

Smoothed/posthoc labels (none produced this run) are analysis-only — visualization, market
narrative, toxic-zone scouting. They carry `usable_in_hybrid=false` and live in their own files.
Phase 3 may inspect them for research but must not treat them as current-regime truth.

## 6. Causal-only for `usable_in_hybrid`

Phase 3 computes `usable_in_hybrid` (a Phase 3 concept, never a Phase 4 column). Only
`regime_labeling=causal` labels may serve as the basis for hybrid eligibility. Smoothed/posthoc
labels are never a hybrid basis.

## 7. Condition to transition `strategy_profile.lifecycle_status = analyzed`

Phase 3 may set `analyzed` only after completing its regime-conditional performance analysis
(edge_fragment / strategy_evaluation) using these causal labels. Phase 4 does not perform this
transition and writes no DB row.

## 8. No retroactive modification of Phase 4 criteria

Phase 3 must not edit the regime definitions, thresholds, or framework selection after seeing its
own analysis results. The Phase 4 contract is frozen for the analysis cycle; changes go to a new
Phase 4 research cycle.

## 9. Revised regime candidates deferred

Any new regime idea Phase 3 surfaces is recorded as an `experimental_regime_candidate` for a
future Phase 4 cycle — not applied retroactively, not substituted for a canonical regime.

## 10. Do not overwrite Phase 2 artifacts

Phase 3 writes `regime_enriched_trades.csv` / `regime_enriched_trade_logs.jsonl` (new files). It
never adds a regime column to, or overwrites, Phase 2 `trades.csv` / `signals.csv` / `result.json`
/ `portfolio.csv`.

## 11. Causal-only hybrid candidacy when creating `edge_fragment`

When Phase 3 creates `edge_fragment`, only `regime_labeling=causal` fragments are hybrid
candidates; smoothed/posthoc-derived fragments are research annotations only.

## 12. Prediction output is not a current-regime label

A future-regime prediction study (Stage B) has been **designed** this run (design-only — no
models trained, no data). Regardless, Phase 3 must never use any Stage B prediction output as a
current `regime` label in `strategy_evaluation`; predictions are auxiliary/probabilistic only.
Current-regime labels come only from the causal classifier.
