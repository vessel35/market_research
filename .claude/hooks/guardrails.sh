#!/usr/bin/env bash
# SessionStart hook. Re-injects the Phase 4 objective + guardrails into context every session
# so agents stay anchored to the goal (anti-drift). Warns if OBJECTIVE.md is still a placeholder.
# SessionStart cannot block (exit 2 has no effect here) — stderr is the only signal.
set -uo pipefail
root="${CLAUDE_PROJECT_DIR:-.}"

echo "=== HARNESS GUARDRAILS (Market Regime Research — Phase 4) ==="
echo "- Single driver = this session (Opus). Subagents stay in lane; out-of-lane work -> STOP and escalate."
echo "- Phase 4 is an INDEPENDENT study. It does NOT read Phase 2 results (result.json/trades.csv/portfolio.csv/signals.csv) or Phase 3 results (edge_fragment/strategy_evaluation)."
echo "- DB access is READ-ONLY (schema check, lifecycle_status read, Phase 3 query drafts). NO INSERT/UPDATE/DELETE/DDL anywhere."
echo "- Current market regime is defined ONLY by a theory-grounded framework chosen via the selection matrix — never by LLM discretion. llm_discretion_used must always be false."
echo "- Select exactly ONE primary framework. No arbitrary mixing. Rejected frameworks are documented as secondary/future-research."
echo "- All labels are CAUSAL (bars <= t only); usable_from_timestamp is always later than the bar. smoothed/posthoc labels live in SEPARATE files, never the causal label file."
echo "- Phase 4 outputs are consumed by Phase 3 ONLY. Outputs go under reports/phase4_market_regime/{YYYYMMDD_HHMM}/."
echo "- Stage A (current-regime classification) is mandatory; Stage B (future prediction) is optional and starts only AFTER Stage A completes."
echo "- Reports obey Markdown-stability rules: no nested code fences; use BEGIN_JSON/END_JSON and BEGIN_SQL/END_SQL markers; keep long JSON/SQL out of tables."
echo "- Do not ask the human mid-run. If uncertain, make a conservative assumption, record it and its impact, and continue."
echo ""

obj="$root/.claude/OBJECTIVE.md"
if [ ! -f "$obj" ]; then
  echo "[!] .claude/OBJECTIVE.md MISSING. Create one before dispatching any subagent." >&2
  exit 0
fi

if grep -Eq '<fill[- ]in>|TODO|XXX' "$obj"; then
  echo "[!] OBJECTIVE.md appears UNEDITED (placeholder markers detected: '<fill in>' / 'TODO' / 'XXX')." >&2
  echo "[!] Agents will anchor to placeholder text. Edit .claude/OBJECTIVE.md (esp. data path + turn budget) and restart." >&2
fi

echo "=== CURRENT OBJECTIVE (.claude/OBJECTIVE.md) ==="
cat "$obj"
exit 0
