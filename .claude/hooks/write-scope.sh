#!/usr/bin/env bash
# PreToolUse on Write|Edit|MultiEdit. Blocks edits to protected zones (config/CI/infra/secrets).
# Env *templates* (.env.example/.sample/.template/.dist) are allowed; real env files are blocked.
# NOTE: Phase 4 writes belong under reports/phase4_market_regime/ — that location is policy
# (OBJECTIVE.md + agent lanes), not enforced here, to avoid false-positive stoppages on
# legitimate scratch notes/branches. This hook only hard-blocks genuinely protected zones.
set -uo pipefail
input="$(cat)"

# JSON extraction via jq (~10ms startup) instead of python3 — a pyenv shim adds ~300ms
# per python3 call, which lands on EVERY Write/Edit. python3 stays as a fallback.
if command -v jq >/dev/null 2>&1; then
  path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""' 2>/dev/null)"
else
  path="$(INPUT="$input" python3 -c '
import os, json, sys
try:
    d = json.loads(os.environ.get("INPUT","") or "{}")
except Exception:
    print(""); sys.exit(0)
print((d.get("tool_input",{}) or {}).get("file_path",""))
')"
fi

[ -z "$path" ] && exit 0

# Allow env *templates* (no secrets by definition).
base="$(basename "$path")"
case "$base" in
  .env.example|.env.sample|.env.template|.env.dist|env.example|env.sample|env.template) exit 0 ;;
esac

protected=(
  '\.env($|\.)'
  '\.mcp\.json$'
  '\.claude/settings\.json$'
  '\.claude/hooks/'
  '(^|/)\.github/'
  '(^|/)(terraform|k8s|helm)/'
  '\.(pem|key|p12|keystore|tfvars|tfstate)$'
  '(^|/)secrets?/'
  '(^|/)credentials?/'
  '(^|/)(secrets?|credentials?)\.(ya?ml|json|env|toml)$'
  '\.codex/config\.toml$'
  '\.claude\.json$'
)
for p in "${protected[@]}"; do
  if printf '%s' "$path" | grep -E -qi -e "$p"; then
    echo "BLOCKED by write-scope: '$path' is a protected zone (/$p/). Outside any agent's lane. Stop and ask the human to make this change." >&2
    exit 2
  fi
done
exit 0
