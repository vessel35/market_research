# Current Objective — Phase 4: Market Regime Research (Stage A)

> Edit this each run. `guardrails.sh` injects it at SessionStart.
> After editing, register the Done-when block as a `/goal` so each turn auto-evaluates.

**Goal:** For ETH/USDT 5m USDT-M perpetual futures, survey theory-grounded market-regime
frameworks, select exactly ONE primary framework via a scored matrix, and author a causal
(look-ahead-free) current-regime classifier + labeling pipeline + Phase 3 usage contract.
Stage A (current-regime classification) is the required objective; Stage B (future prediction)
is optional.

**Data path:** /home/vessel/workspace/trading-system/backtestdata/ETHUSDT_futures_5min.csv (ETH/USDT 5m OHLCV; 2024-01-01 ~ 2025-12-31; 210,528 bars) — supplied 2026-06-14; data-present acceptance run
**Optional data:** none
**Period:** 2024-01-01 ~ 2025-12-31 (full coverage in data)
**Run dir:** reports/phase4_market_regime/20260613_0558/ (data-present execution added on top of the methodology spec)
**Compute:** /home/vessel/workspace/trading-system/.venv/bin/python (pandas 2.1.4, numpy 1.26.3, scipy; no TA-Lib)

**In scope:**
- Theory-based framework survey across the 5 families (trend-strength, volatility,
  price-action / market-structure, statistical / HMM, session / liquidity).
- A scored selection matrix and ONE primary framework, with documented rejections (no mixing).
- A causal classifier spec, feature catalog, labeling pipeline, and `regime_labels.csv` (if
  data is present) mapped to the canonical vocabulary (strong_up / strong_down / transition /
  volatile / range).
- A Phase 3 usage contract and a passed look-ahead-bias prevention checklist.

**Out of scope (escalate / do NOT do):**
- Reading any Phase 2 artifact (result.json / trades.csv / portfolio.csv / signals.csv /
  per-strategy performance) or Phase 3 artifact (edge_fragment / strategy_evaluation).
- Any DB write (INSERT/UPDATE/DELETE/DDL), lifecycle transition, or hybrid materialization.
- LLM-invented regimes, mixing frameworks, tuning thresholds to performance, future data as a
  current feature, smoothed/posthoc labels used as causal.
- Starting Stage B before Stage A is COMPLETE.

**Done when (Stage A — deliverable-present + checklist-passed + isolation-verifiable):**
- All 13 Stage A deliverables exist under reports/phase4_market_regime/{YYYYMMDD_HHMM}/:
  regime_framework_research.md, regime_framework_selection_matrix.csv,
  selected_primary_regime_framework.md, market_regime_definition.md,
  causal_regime_classifier_spec.md, regime_feature_catalog.csv,
  regime_labeling_pipeline_spec.md, regime_labels_schema.md, phase3_usage_contract.md,
  lookahead_bias_prevention_checklist.md, phase4_manifest.json, phase4_final_report.md
  (regime_labels.csv only if data is present).
- Exactly ONE primary framework selected; rejected frameworks documented; no arbitrary mixing.
- `causal-auditor` returned PASS on the classifier spec + pipeline in this transcript.
- The look-ahead-bias prevention checklist has every row passed (no false).
- `llm_discretion_used` is false for all labels; causal labels are separated from
  smoothed/posthoc.
- `completeness-auditor` ran in this transcript and returned COMPLETE.
- No Phase 2/3 artifact was read; no DB write occurred (DB used read-only only).
- Reports are Markdown-stable (no nested code fences; BEGIN_JSON/BEGIN_SQL markers).
- Turn budget: ≤ 15 orchestrator turns. If exceeded → STOP and escalate; do not
  auto-extend.

**Register with /goal (example):**

Stage A is complete only when completeness-auditor returns COMPLETE in this transcript, all 13
Stage A deliverables exist, exactly one primary framework was selected with documented
rejections, causal-auditor returned PASS, the look-ahead checklist has zero false rows, and no
Phase 2/3 artifact was read and no DB write occurred. Until then, continue the named gaps. Do
not declare completion from a feeling of "enough". Stage B is optional and starts only after
Stage A is COMPLETE.
