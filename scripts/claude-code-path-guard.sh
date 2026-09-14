#!/bin/bash
# CDAD Claude Code Path Guard — rebuilds path-scoping via PreToolUse hook
#
# Usage: reads JSON from stdin (tool_name, tool_input.file_path or
# tool_input.command depending on the tool).
# Invoke: command: "~/.claude/cdad-scripts/path-guard.sh <role>"
#
# Roles based on file_path (Read/Grep/Glob/Edit/Write):
#   implementer         → blocks Edit/Write to test files (tests/** and co-located)
#   test-writer-read   → blocks Read/Grep/Glob to src/** and lib/** (except test files)
#   test-writer-write  → blocks Edit/Write to everything except test files
#   implementer-odoo   → alias of implementer
#   test-writer-odoo-read  → blocks Read/Grep/Glob to models/views/controllers/wizards
#   test-writer-odoo-write → same as test-writer-write (test allowlist)
#
# Roles based on command (Bash) — see findings/audit-consistencia-2026-09-02.md
# B1: the matcher above only covers Read/Grep/Glob/Edit/Write; Bash was left
# uncovered and was the real leak (cat src/x.py, sed -i tests/x.py, etc.). It
# does not try to parse which PATH the command touches (fragile, bash is
# Turing-complete); instead it blocks content read/write commands by name —
# the same design as the OpenCode agents' bash allowlist: Bash is for RUNNING
# things (tests, git, navigation), not for reading/writing content
# (for that there is Read/Edit, correctly scoped by the matcher above):
#   test-writer-bash | implementer-bash | test-writer-odoo-bash | implementer-odoo-bash
#     → blocks content-reading commands (cat/head/tail/sed/awk/grep/
#       rg/less/more/interpreters) and write-by-redirection (>, >>, tee,
#       sed -i). Does NOT block git/make/pytest/ls/find/wc/pwd — that is the
#       legitimate allowlist, calibrated so the agent is not forced to look
#       for workarounds.

set -e

ROL="${1:-unknown}"

# Reads the hook JSON from stdin
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

# ── Content guard via Bash (commands, not paths) ───────────────────────
BASH_CONTENT_GUARD_ROLES="test-writer-bash implementer-bash test-writer-odoo-bash implementer-odoo-bash"
if [[ "$TOOL_NAME" == "Bash" ]] && [[ " $BASH_CONTENT_GUARD_ROLES " == *" $ROL "* ]]; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
  if [[ -z "$COMMAND" ]]; then
    exit 0
  fi
  # First token of the command (binary name), ignoring leading whitespace.
  first_word() { printf '%s' "$1" | sed -E 's/^[[:space:]]+//' | awk '{print $1}'; }
  CMD_NAME="$(first_word "$COMMAND")"
  CMD_NAME="${CMD_NAME##*/}"  # no path (/usr/bin/cat -> cat)

  DENY_CONTENT_READ="cat head tail less more sed awk grep egrep fgrep rg ag python python3 node perl ruby php xxd od strings view vim vi nano emacs"
  for bad in $DENY_CONTENT_READ; do
    if [[ "$CMD_NAME" == "$bad" ]]; then
      exit 2  # Block: content-reading command
    fi
  done
  # Write via redirection or tee/sed-i, anywhere in the command
  # (includes pipelines: "foo | tee bar", "echo x >> tests/y").
  if [[ "$COMMAND" == *">"* ]] || [[ "$COMMAND" == *"tee "* ]] || [[ "$COMMAND" =~ sed[[:space:]]+-i ]]; then
    exit 2  # Block: content write via shell
  fi
  exit 0  # Everything else (make, pytest, git, ls, find, wc, pwd, ...) passes
fi

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# If there is no file_path (e.g. Bash in a role without bash-content-guard, or a
# tool without a path), allow — the guard in this section is path-based, does not apply.
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Normalizes file_path to RELATIVE to the project (PWD) so that relative globs
# (tests/**, src/**, lib/**) match both relative and absolute paths.
# Fix B: without this, a sub-agent could pass an absolute path (/abs/.../tests/x)
# and evade the guard (the absolute path does not match the relative glob).
#
# Fix C (B1): an absolute path NOT under $PWD (a different root, symlink,
# etc.) was marked ABS_OUTSIDE_PWD=0 before and blindly relativized (it just
# stripped the leading "/") — "/home/otro/src/x.py" became
# "home/otro/src/x.py", which does NOT match the glob "src/**" and passed
# without being blocked. Now it is explicitly marked; matches_glob() also
# tries the glob with a "**/" prefix for that case, so "algo/.../src/x.py"
# keeps matching "src/**" no matter how many directories come before it.
ABS_OUTSIDE_PWD=0
# Computed HERE (main shell), not inside relativize(): that function is
# invoked via "$(...)" (subshell) below, so any variable assignment made
# inside is lost on return — it must be decided before.
EXPANDED_FILE_PATH="${FILE_PATH/#\~\//$HOME\/}"
if [[ "$EXPANDED_FILE_PATH" == /* && "$EXPANDED_FILE_PATH" != "$PWD"* ]]; then
  ABS_OUTSIDE_PWD=1
fi
relativize() {
  local p="$1"
  # expands ~/ if present
  p="${p/#\~\//$HOME\/}"
  # if absolute and under $PWD, relativizes it
  if [[ "$p" == "$PWD"* ]]; then
    p="${p#$PWD}"
    p="${p#/}"
  elif [[ "$p" == /* ]]; then
    # absolute and outside the project: there is no reliable way to know if it
    # is "the same folder with another root" — treated as potentially dangerous
    # (ABS_OUTSIDE_PWD is already set to 1, computed above in the parent shell).
    p="${p#/}"
  fi
  # strips ./, duplicate /, and trailing /
  p="${p#./}"
  p="${p//\/\//\/}"
  p="${p%/}"
  printf '%s' "$p"
}
FILE_PATH="$(relativize "$FILE_PATH")"

# Helper function: does a glob match?
matches_glob() {
  local path="$1"
  local glob="$2"

  # Exact base (tests, tests/) also matches tests/** — avoids bypass via an empty dir
  local base="${glob%/**}"
  if [[ "$path" == "$base" || "$path" == "$base/" ]]; then
    return 0
  fi

  # Substitutes ** with a regex pattern matching any depth
  local pattern="${glob//\*\*/.+}"
  pattern="${pattern//\*/[^/]*}"
  pattern="^${pattern}$"

  if [[ "$path" =~ $pattern ]]; then
    return 0
  fi

  # Fix C: if the original path was absolute and outside $PWD, also try the
  # glob with "**/" in front — covers "any root, then <glob>" instead of
  # requiring the glob to match from the relativized root.
  if [[ "$ABS_OUTSIDE_PWD" == "1" && "$glob" != "**/"* ]]; then
    local wide_pattern=".+/${pattern#^}"
    [[ "$path" =~ $wide_pattern ]] && return 0
  fi

  return 1
}

# Canonical list of "test file" patterns (single source of truth).
# Covers BOTH layouts: dedicated directory (tests/**) and tests CO-LOCATED
# next to the code by naming convention. Co-location is not a style choice: Go
# REQUIRES same package/directory to access non-exported identifiers
# (compiler requirement). Used by test-writer-*-write (allowlist) and
# implementer* (blocklist — the implementer must NOT be able to touch tests,
# co-located or not, or it breaks the anti-gaming gate).
TEST_FILE_GLOBS=(
  "tests/**"
  "**/tests/**"
  "**/*.test.js" "**/*.test.ts" "**/*.test.mjs" "**/*.test.cjs"
  "**/*.spec.ts" "**/*.spec.js"
  "**/*_test.go"
  "**/test_*.py"
)
is_test_file() {
  local path="$1" glob
  for glob in "${TEST_FILE_GLOBS[@]}"; do
    matches_glob "$path" "$glob" && return 0
  done
  return 1
}

# Per-role logic
case "$ROL" in
  implementer)
    # Blocks Edit/Write to tests: dedicated directory AND co-located (any of
    # the TEST_FILE_GLOBS conventions). Without the co-located ones, in Go/JS
    # repos with tests next to the code the implementer could edit the tests
    # that validate it — breaks the anti-gaming gate.
    if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
      if is_test_file "$FILE_PATH"; then
        exit 2  # Block
      fi
    fi
    exit 0  # Allow everything else
    ;;

  implementer-odoo)
    # Alias of implementer, Odoo variant: same rule (dedicated and co-located tests).
    if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
      if is_test_file "$FILE_PATH"; then
        exit 2  # Block
      fi
    fi
    exit 0  # Allow everything else
    ;;

  test-writer-read)
    # Blocks Read/Grep/Glob to src/** and lib/**, WITH the EXCEPTION of co-located
    # test files (2026-09-04, same reason as test-writer-write below: a repo
    # with a Go backend — like any Go repo — has its tests next to the code,
    # under src/**, not in a separate tests/**). Without this, the
    # test-writer cannot read/audit the existing suite it has a mandate to
    # edit (AUDIT + authorized spec edits), even though it CAN write it —
    # asymmetric block discovered in a review of the guard. The real
    # implementation (serializer.js, resolver.js, tools.go, etc.) stays
    # blocked: none of those match the test globs.
    if [[ "$TOOL_NAME" =~ ^(Read|Grep|Glob)$ ]]; then
      if (matches_glob "$FILE_PATH" "src/**" || matches_glob "$FILE_PATH" "lib/**") \
        && ! is_test_file "$FILE_PATH"; then
        exit 2  # Block
      fi
    fi
    exit 0  # Allow everything else
    ;;

  test-writer-odoo-read)
    # Blocks Read/Grep/Glob to the Odoo implementation (models/views/controllers/wizards).
    if [[ "$TOOL_NAME" =~ ^(Read|Grep|Glob)$ ]]; then
      if matches_glob "$FILE_PATH" "**/models/**" \
        || matches_glob "$FILE_PATH" "**/views/**" \
        || matches_glob "$FILE_PATH" "**/controllers/**" \
        || matches_glob "$FILE_PATH" "**/wizards/**"; then
        exit 2  # Block
      fi
    fi
    exit 0  # Allow everything else
    ;;

  test-writer-write)
    # Blocks Edit/Write to everything EXCEPT test files (allowlist = TEST_FILE_GLOBS).
    # Two supported layouts (2026-09-04, fix detected in a client project
    # with a Go backend + JS extension): dedicated directory `tests/**`, and tests
    # CO-LOCATED next to the code, identified by naming convention.
    # Co-location is not a stylistic whim: Go REQUIRES same package (same
    # directory) for a test to access non-exported identifiers —
    # moving them to tests/ would break access to internals in much of a
    # typical Go suite. Without this glob, a repo that co-locates its tests (e.g.
    # src/extension/*.test.js, src/server/**/*_test.go) leaves the
    # test-writer role with NO writable path. The guard's intent does
    # not change: the test-writer still writes test files only.
    if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
      if ! is_test_file "$FILE_PATH"; then
        exit 2  # Block
      fi
    fi
    exit 0  # Allow everything else
    ;;

  test-writer-odoo-write)
    # Odoo variant: same allowlist (tests/** is the Odoo layout; the co-located
    # patterns are harmless — an addon has no *_test.go).
    if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
      if ! is_test_file "$FILE_PATH"; then
        exit 2  # Block
      fi
    fi
    exit 0  # Allow everything else
    ;;

  *)
    # Unknown role → allow (fail-open)
    exit 0
    ;;
esac
