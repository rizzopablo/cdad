#!/usr/bin/env bash
# cdad-bash-allowlist.sh — standalone emitter for the per-role bash allowlists.
#
# 004-001 T4 review-fix (review-1 B2): the bash policy lives ONLY in the
# canonical role sources (sources/roles/architect.md — reader class,
# sources/roles/test-writer.md — writer class) and is derived by ONE
# implementation: scripts/cdad-generate.py (PD-1/PD-4: single source). This
# script is a thin adapter that builds the staging artifacts from those
# sources and prints the generated OpenCode bash block of the requested role —
# byte-identical to what the generator publishes in staging — replacing the
# former hand-written policy (which had drifted from the generator and
# silently discarded `du`, `rtk ls/pwd` and the declared pairs at install).
#
# Usage:
#   cdad-bash-allowlist.sh <role> [--stack odoo|auto]
#
#   role   architect | test-writer | implementer | reviewer | scribe
#          (an "-odoo" suffix is accepted and implies --stack odoo)
#   stack  odoo | auto (default). With "auto" the stack is detected on the
#          target machine (odoo toolchain present → odoo; otherwise generic,
#          honoring the declared state binding when one exists).
#
# Guarantees (owner decision 2026-09-29 — permissive operational policy, spec
# docs/specs/permissive-bash-policy-2026-09-29/spec.yaml; the cdad-010
# test-audit findings 3.1/3.2 remain preserved by composition — they live in
# the role sources and the runtime adapters, from which the generator derives
# the block):
#   - the emitted block is EXACTLY the catch-all `"*": allow` (PD-1/PD-3:
#     derived from the canonical sources; never silent, never hand-patched).
#   - NO operation filtering: the barriers are PATH-based (read/edit/grep
#     maps) and contract-level. Declared, NOT a sandbox.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
GENERATOR="$SCRIPT_DIR/cdad-generate.py"

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
usage: cdad-bash-allowlist.sh <role> [--stack odoo|auto]

role:  architect | test-writer | implementer | reviewer | scribe
       (an "-odoo" suffix is accepted and implies --stack odoo)

Prints the OpenCode YAML rule lines of the bash: section derived by
scripts/cdad-generate.py from the canonical sources (PD-4: both consumers —
generation and installation — compose the same policy; this adapter adds
no rules of its own).
EOF
}

rule() { printf '    "%s": %s\n' "$1" "$2"; }
pair() { rule "$1*" allow; rule "rtk $1*" allow; }

ROLE=""
STACK_FLAG=""

while [ $# -gt 0 ]; do
  case "$1" in
    --stack)
      [ $# -ge 2 ] || die "--stack requires a value (odoo|auto)"
      STACK_FLAG="$2"
      shift 2
      ;;
    --stack=*)
      STACK_FLAG="${1#--stack=}"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      die "unknown option: $1 (see --help)"
      ;;
    *)
      [ -z "$ROLE" ] || die "unexpected argument: $1 (see --help)"
      ROLE="$1"
      shift
      ;;
  esac
done

[ -n "$ROLE" ] || { usage >&2; exit 1; }

# Normalize the -odoo suffix: same role, odoo stack.
case "$ROLE" in
  *-odoo)
    if [ -n "$STACK_FLAG" ] && [ "$STACK_FLAG" != "odoo" ]; then
      die "--stack must be 'odoo' for role '$ROLE'"
    fi
    ROLE="${ROLE%-odoo}"
    STACK_FLAG="odoo"
    ;;
esac

case "$ROLE" in
  architect|test-writer|implementer|reviewer|scribe) ;;
  *) die "unknown role: $ROLE (expected one of: architect test-writer implementer reviewer scribe)" ;;
esac

STACK_ARG="auto"
if [ -n "$STACK_FLAG" ]; then
  case "$STACK_FLAG" in
    odoo|auto) ;;
    *) die "unknown stack: $STACK_FLAG (expected: odoo|auto)" ;;
  esac
  STACK_ARG="$STACK_FLAG"
fi
# "auto" = the stack detected on the TARGET machine (historical install.sh
# semantics, cdad-010 P5): odoo toolchain present → odoo; otherwise the
# generator resolves generic (--stack auto honors the declared state binding
# when one exists). Explicit --stack odoo is never downgraded by detection.
if [ "$STACK_ARG" = "auto" ] && has odoo; then
  STACK_ARG="odoo"
fi


# ---------------------------------------------------------------------------
# Derivation (single policy source: the generator, from the canonical sources)
# ---------------------------------------------------------------------------

STAGE_DIR="$(mktemp -d "${TMPDIR:-${HOME:-/tmp}}/.cdad-allowlist-XXXXXX")"
trap 'rm -rf "$STAGE_DIR"' EXIT

# --profile basic: the bash policy is profile-independent (the profile only
# pins the model: line), so the emitted block is the one every profile
# regenerates identically.
if ! python3 "$GENERATOR" --runtime opencode --stack "$STACK_ARG" \
      --profile basic --out "$STAGE_DIR" >/dev/null; then
  die "policy derivation failed: scripts/cdad-generate.py rejected the sources"
fi

# The stack RESOLVED by the generator (manifest["stack"]), read once and used
# both for variant selection and for the suite-emission gate below. With
# "auto" the generator may resolve odoo via the declared state binding; the
# manifest is the single truth for what was emitted.
STAGE_STACK="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["stack"])' "$STAGE_DIR/manifest.json")" \
  || die "cannot read the derived stack from the generator manifest"

# Review-2 R2-B1: select the artifact matching the RESOLVED stack — the
# specialized variant cdad-$ROLE-odoo.md when the generator resolved odoo,
# the base variant otherwise. Parity with the resolved variant comes from
# extraction, never from hand-patching rules onto the generic output
# (that would re-introduce the duplication PD-1 forbids).
case "$STAGE_STACK" in
  odoo)    agent_name="cdad-$ROLE-odoo.md" ;;
  generic) agent_name="cdad-$ROLE.md" ;;
  *) die "unexpected resolved stack in the generator manifest: $STAGE_STACK" ;;
esac
agent_file="$STAGE_DIR/agents/opencode/$agent_name"
[ -f "$agent_file" ] || die "no generated agent for role '$ROLE' (stack $STAGE_STACK)"

# The nested `permission.bash` block of the generated agent, without the
# 2-space `bash:` key (install.sh's apply_bash_block re-prints that key
# itself). Lines keep the generator's 4-space indentation — the substitution
# contract with install.sh is unchanged.
awk '
  /^---[[:space:]]*$/ { fm++; next }
  fm == 1 && /^[[:space:]]{2}bash:[[:space:]]*$/ { on = 1; next }
  fm == 1 && on {
    if ($0 ~ /^[[:space:]]{2}[A-Za-z_-]+:/) { exit }
    print
  }
' "$agent_file"

# Owner decision 2026-09-29: NO install-time toolchain tail — the permissive
# catch-all allow makes per-toolchain permits redundant. The emitted block is
# exactly what the generator derives (PD-2: single composition).
