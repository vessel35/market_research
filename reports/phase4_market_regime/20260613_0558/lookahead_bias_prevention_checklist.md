# Look-ahead-Bias Prevention Checklist

**Run:** 20260613_0558 · **Framework:** `TREND_STRENGTH_ADX_EMA_SPEC` · **Mode:** data-present
acceptance run (2026-06-14). Independently reviewed by `causal-auditor` → **PASS** on both the
spec and the realized labels + implementation. `llm_discretion_used=false`.

**`passed` values:** `yes` = affirmatively satisfied (verified on the spec and/or the generated
labels); `n/a` = not applicable because that mechanism is genuinely unused (no scaler, no adaptive
train-only fit, no clustering in this rule-based classifier). **No row is `false`/`no`.** Per
prompt §34, only a `false` row blocks completion. Labels were generated on real OHLCV this run, so
the label-dependent rows are now verified on the actual file.

| check | passed | evidence | failure_action |
|---|---|---|---|
| feature uses bars <= t only | yes | classifier spec §6/§7/§8 — ADX/DM use bars t,t-1; EMA recursive on close[t]/EMA[t-1]; ATR percentile window ends at t. causal-auditor check 1 PASS | reject spec; recompute every feature on bars ≤ t |
| current-close feature usable only from next bar | yes | `usable_from_timestamp[t]=timestamp[t]+5min` on every branch (classifier §9/§11; pipeline §6; schema row 2) | shift label by one bar before any join |
| no future return in a current feature | yes | no future-return term in any selected feature; auditor check 2 PASS | remove the offending feature |
| no future high/low/min/max in a current feature | yes | ATR percentile uses a strictly trailing window (current+past); no future H/L/min/max anywhere (classifier §8; auditor check 2) | remove/replace with a trailing equivalent |
| label separated from feature | yes | labels derived from features and stored under distinct schema columns; features in catalog, labels in `regime_labels_schema.md` | separate label and feature storage |
| selected framework is theory-grounded | yes | Wilder ADX/DMI + standard multi-EMA alignment + Mandelbrot/Engle volatility clustering (research §3.1) | reject any LLM-invented regime |
| exactly one primary framework | yes | exactly one `selected_as_primary=true` in `regime_framework_selection_matrix.csv` (TREND_STRENGTH_ADX_EMA_SPEC) | choose exactly one primary |
| no arbitrary mixing | yes | only the framework's own ATR-percentile vol split (skill §3/§6); no other family's rules in the classifier; auditor check 4 PASS | remove any cross-family rule |
| rejected frameworks documented | yes | 16 rejected candidates with `rejection_reason` in the matrix + `regime_framework_research.md` §3–§4 | document every rejection with a reason |
| scaler fit train-only (if used) | n/a | no scaler used — rule-based classifier; no fit performed this run (no data) | if a scaler is ever added, fit on train split only |
| threshold fit train-only (if adaptive) | n/a | thresholds are fixed convention/SPEC values (ADX=25, P70), not theory-derived constants; the percentile is a causal trailing statistic, not a train-only model fit and not tuned to performance; no fit performed this run | if adaptive thresholds are introduced, fit on train split only, never on test/performance |
| clustering fit train-only (if used) | n/a | no clustering in the selected framework; statistical/clustering candidates rejected (hard gate) | if clustering is ever added, fit on train split only |
| no Phase 2 result used | yes | no Phase 2 artifact (result.json/trades.csv/portfolio.csv/signals.csv/per-strategy metrics) read; isolation stated | remove any Phase 2 input |
| no Phase 3 result used | yes | no Phase 3 artifact (edge_fragment/strategy_evaluation) read | remove any Phase 3 input |
| causal labels separated from smoothed/posthoc | yes | only causal labels produced (regime_labels.csv); no smoothed/posthoc files exist, so no mixing is possible; design mandates separate files (pipeline §11) | route smoothed/posthoc to their own files with usable_in_hybrid=false |
| Phase 2 artifacts not modified | yes | no Phase 2 artifact exists/was touched; outputs confined to the run dir | revert any Phase 2 modification |
| regime_labels.csv has no strategy-performance column | yes | generated regime_labels.csv verified: header is the 20 schema columns; 0 of the 14 forbidden columns (causal-auditor grep over the full file) | drop any forbidden column before writing the CSV |
| llm_discretion_used is false for all labels | yes | generated regime_labels.csv: llm_discretion_used=false on all 210,528 rows (verified; classifier is deterministic) | invalidate any label with llm_discretion_used=true |

**Result:** 15 rows `yes`, 3 rows `n/a` (no scaler / no adaptive-fit threshold / no clustering —
genuinely unused), **0 rows `false`** → look-ahead checklist passed (verified on real labels).
