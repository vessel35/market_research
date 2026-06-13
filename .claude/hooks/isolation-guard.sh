#!/usr/bin/env bash
# PreToolUse on Bash. Keeps DB mutation OFF the shell — DB access in Phase 4 is READ-ONLY
# (schema check / lifecycle read / Phase 3 query draft); the hard boundary is the read-only DB
# role grant, and this hook backstops the shell path. Blocks non-SELECT SQL only when there is
# REAL SQL context: a DB client is invoked (psql/mysql/...) with a non-SELECT keyword, or
# genuine DML/DDL *syntax* is present. Bare keywords (git merge, rg UPDATE) do NOT trigger.
#
# NOTE: Phase 2/3 artifact READ-blocking was intentionally REMOVED from this hook (regime-research
# only). Phase 4's "no Phase 2/3 input" invariant is now enforced by the agent lanes (each agent's
# forbidden list) + OBJECTIVE, not by a mechanical read gate. This drops the hook off the hot Read
# path entirely and removes the per-read grep loop. Only exit 2 blocks.
set -uo pipefail
input="$(cat)"

# JSON extraction via jq (~10ms startup); python3 fallback for hosts without jq.
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // ""' 2>/dev/null)"
else
  cmd="$(INPUT="$input" python3 -c '
import os, json, sys
try: d = json.loads(os.environ.get("INPUT","") or "{}")
except Exception: print(""); sys.exit(0)
print((d.get("tool_input",{}) or {}).get("command",""))
')"
fi

[ -z "${cmd:-}" ] && exit 0

block(){ echo "BLOCKED by isolation-guard: $1 Phase 4 keeps DB mutations off the shell — DB access is read-only. Stop and escalate." >&2; exit 2; }

# DB mutation from the shell — syntax-anchored DML/DDL, or any non-SELECT via a DB client.
dml_syntax=(
  '\bDELETE[[:space:]]+FROM\b'
  '\bINSERT[[:space:]]+INTO\b'
  '\bUPDATE\b[^;|]+\bSET\b[^;|]*='
  '\bDROP[[:space:]]+(TABLE|DATABASE|INDEX|VIEW|SCHEMA|SEQUENCE|MATERIALIZED|ROLE|USER)\b'
  '\bALTER[[:space:]]+(TABLE|DATABASE|INDEX|VIEW|SCHEMA|SEQUENCE|TYPE|ROLE|USER)\b'
  '\bTRUNCATE[[:space:]]+(TABLE|ONLY)\b'
  '\bGRANT\b[^;|]*[[:space:]]+ON\b'
  '\bMERGE[[:space:]]+INTO\b'
)
sql_keywords=( '\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|GRANT|MERGE|UPSERT)\b' )
db_client='\b(psql|mysql|mariadb|sqlite3|clickhouse-client|clickhouse|duckdb|cockroach|pgcli|mycli|usql|pg_dump|pg_restore)\b'

if printf '%s' "$cmd" | grep -E -qi -e "$db_client"; then
  for p in "${sql_keywords[@]}"; do
    printf '%s' "$cmd" | grep -E -qi -e "$p" && block "non-SELECT SQL via a shell DB client (/$p/)."
  done
else
  for p in "${dml_syntax[@]}"; do
    printf '%s' "$cmd" | grep -E -qi -e "$p" && block "non-SELECT SQL syntax in a shell command (/$p/)."
  done
fi
exit 0
