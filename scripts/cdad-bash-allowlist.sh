#!/usr/bin/env bash
# cdad-bash-allowlist.sh — single source for the per-role bash allowlists
# (cdad-010 P5; rtk policy in ADR-009: every legit command gets an X* / rtk X*
# pair, because models wrap commands in the rtk workspace wrapper).
#
# install.sh injects this output into the INSTALLED copies of the OpenCode
# agents only (same pattern as the model: line). The repo keeps a handwritten
# agnostic default: the repo is the source of truth, copies derive, and
# installed copies are never edited by hand.
#
# Usage:
#   cdad-bash-allowlist.sh <role> [--stack odoo|auto]
#
#   role   architect | test-writer | implementer | reviewer | scribe
#          (an "-odoo" suffix is accepted and implies --stack odoo)
#   stack  odoo | auto (default). With "auto" the toolchains present on this
#          machine are detected via command -v.
#
# Guarantees (test-audit cdad-010 findings 3.1/3.2):
#   - catch-all deny first, specific rules after (findLast semantics).
#   - every role gets the global rtk denies: rtk err*, rtk summary*,
#     rtk git * — and NEVER "rtk *": allow (that is a total leak).
#   - write-capable roles deny the reading proxies (rtk read/grep/find/diff)
#     BEFORE any allow, so findLast cannot resurrect them.
#   - --stack odoo never emits raw go/python commands (FORBIDDEN_BASH_ALL)
#     and always emits the pylint/pre-commit pairs (odoo validator P1).
#   - no detected stack = agnostic base only (make + git + navigation),
#     exactly what F009 requires as the repo default.
#   - read-only roles never get suite commands (they do not run suites).

set -euo pipefail

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
usage: cdad-bash-allowlist.sh <role> [--stack odoo|auto]

role:  architect | test-writer | implementer | reviewer | scribe
       (an "-odoo" suffix is accepted and implies --stack odoo)

Prints the YAML rule lines for the bash: section of that agent. install.sh
injects the output into installed copies only; the repo never changes.
EOF
}

# rule <pattern> <action> — prints one indented YAML rule line.
rule() { printf '    "%s": %s\n' "$1" "$2"; }
comment() { printf '    # %s\n' "$*"; }

# pair <prefix> — emits the X* / rtk X* allow pair for a command prefix
# (ADR-009). The prefix must include the trailing space when the wildcard
# replaces an argument (e.g. "make " -> "make *", "git add " -> "git add *").
pair() {
  rule "$1*" allow
  rule "rtk $1*" allow
}

has() { command -v "$1" >/dev/null 2>&1; }

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
STACK_FLAG=""
ROLE=""

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

case "${STACK_FLAG:-auto}" in
  odoo|auto) ;;
  *) die "unknown stack: $STACK_FLAG (expected: odoo|auto)" ;;
esac

is_writer() { [ "$ROLE" = "test-writer" ] || [ "$ROLE" = "implementer" ]; }
is_odoo() {
  [ "${STACK_FLAG:-}" = "odoo" ] || { [ -z "${STACK_FLAG:-}" ] && has odoo; }
}

# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------

emit_deny_block() {
  comment "Catch-all first, specific rules after (findLast semantics)."
  rule "*" deny
  comment "Global rtk denies, defense-in-depth; AP-17 via proxy (test-audit cdad-010 3.1)."
  comment "Never emit a bare \"rtk *\" allow: that is a total leak."
  rule "rtk err*" deny
  rule "rtk summary*" deny
  rule "rtk git *" deny
}

emit_writer_reading_denies() {
  comment "Reading via proxy is denied (B1 leak): content reading goes through Read/Grep."
  rule "rtk read*" deny
  rule "rtk grep*" deny
  rule "rtk find*" deny
  rule "rtk diff*" deny
}

emit_base_allow() {
  comment "Agnostic base (F009): make + navigation + non-mutating git inspection."
  pair "make "
  # cd * is safe: compound commands are evaluated per segment (tree-sitter
  # command nodes), so the command after `cd X &&` is still checked on its
  # own. Without this, the workdir prefix `cd <path> &&` matches only the
  # catch-all deny and locks out every workdir-scoped call (GREEN-1 finding).
  rule "cd *" allow
  rule "ls *" allow
  rule "wc *" allow
  rule "pwd" allow
  pair "git diff"
  pair "git log"
  pair "git status"
}

emit_suite_allow() {
  comment "Suite commands for the toolchains detected on this machine (pairs per ADR-009)."
  if has go; then
    pair "go test"
    pair "go vet"
    pair "go build"
    pair "gofmt "
  fi
  if has pytest || has python3; then
    pair "pytest"
  fi
  if has npm; then
    pair "npm test"
    pair "npm run"
  fi
  if has deno; then
    pair "deno test"
  fi
  if has cargo; then
    pair "cargo test"
  fi
  # ruby is detected by design (spec P5) but has no safe test-only entry to
  # allowlist; suites there run via make.
}

emit_reader_allow() {
  comment "Read-only role: content-reading commands (full-read by design)."
  pair "cat "
  pair "head "
  pair "tail "
  pair "rg "
  rule "rtk read*" allow
  rule "rtk grep*" allow
  rule "rtk find*" allow
  pair "git show"
  pair "git blame"
}

emit_odoo_allow() {
  comment "Odoo stack (test-audit cdad-010 3.2): suites run via make (odoo-make-env);"
  comment "raw go/python commands are never emitted (FORBIDDEN_BASH_ALL)."
  pair "pylint "
  pair "pre-commit "
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
comment "Generated by scripts/cdad-bash-allowlist.sh (cdad-010 P5) — do not edit by hand:"
comment "install.sh derives this block from the stack detected on the target machine."

emit_deny_block
if is_writer; then
  emit_writer_reading_denies
fi
emit_base_allow
if is_odoo; then
  emit_odoo_allow
fi
if is_writer && ! is_odoo; then
  emit_suite_allow
fi
if ! is_writer; then
  emit_reader_allow
fi
