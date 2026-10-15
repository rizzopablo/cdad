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
# v2 (I10/C2 — 004-002 T5): when the project has docs/cdad-policy.json, the
# guard classifies each path with the installed `cdad_packet.py
# validate-policy --classify` (CDAD_PACKET_CLI, or
# $HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py) — a single
# classifier — and applies the role boundary to the resulting class:
#   · implementer edits everything EXCEPT test / colocated-test;
#   · test-writer reads/searches everything EXCEPT implementation, and edits
#     only test / colocated-test;
#   · a test-writer Grep/Glob with no `path` is blocked, asking to narrow the
#     search to tests/docs.
# An invalid policy or an unfindable classifier blocks with a diagnostic: no
# silent fallback to the global globs. Without a policy the legacy glob behavior
# below is preserved byte for byte.
#
# Owner decision 2026-09-29 (reverses 002-009): NO operation filtering — the
# Bash content-guard modes (test-writer-bash / implementer-bash and odoo
# variants) are RETIRED; no generated agent carries a Bash hook anymore and
# this script no longer inspects Bash commands. Bash is permissive by design
# (declared, NOT a sandbox): the systematic barriers are the path guards above
# plus the role contracts.

set -e

ROL="${1:-unknown}"

# Reads the hook JSON from stdin
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

# ---------------------------------------------------------------------------
# v2 dynamic guard (I10/C2): a project policy makes the guard classify paths
# with the installed cdad_packet.py instead of the global hardcoded globs.
# ---------------------------------------------------------------------------
# B5 (I10/PD-8): Claude Code exports CLAUDE_PROJECT_DIR to its hooks; use it as
# the project root so the guard still applies the policy when the cwd is not the
# root (a subdirectory). Without the variable pwd is kept (legacy behavior).
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
POLICY_FILE="$PROJECT_ROOT/docs/cdad-policy.json"

if [[ -f "$POLICY_FILE" ]]; then
  case "$ROL" in
    implementer|implementer-odoo)
      GUARD_BASE="implementer"; GUARD_MODE="write" ;;
    test-writer-read|test-writer-odoo-read)
      GUARD_BASE="test-writer"; GUARD_MODE="read" ;;
    test-writer-write|test-writer-odoo-write)
      GUARD_BASE="test-writer"; GUARD_MODE="write" ;;
    *)
      GUARD_BASE=""; GUARD_MODE="" ;;
  esac

  if [[ -n "$GUARD_BASE" ]]; then
    # R6: MultiEdit/NotebookEdit join the v2 mediation (the legacy block below
    # is untouched). NotebookEdit carries its target in `notebook_path`.
    case "$TOOL_NAME" in
      Read|Edit|Write|MultiEdit)
        RAW_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty') ;;
      NotebookEdit)
        RAW_PATH=$(echo "$INPUT" | jq -r '.tool_input.notebook_path // empty') ;;
      Grep|Glob)
        RAW_PATH=$(echo "$INPUT" | jq -r '.tool_input.path // empty') ;;
      *)
        exit 0 ;;
    esac
    IS_EDIT_TOOL=0
    case "$TOOL_NAME" in
      Edit|Write|MultiEdit|NotebookEdit) IS_EDIT_TOOL=1 ;;
    esac

    # B2 (I10/C2): a project-wide Grep/Glob is not scoped — `path` empty, ".",
    # "./", or the project root (absolute) all search the whole project. The
    # test-writer must narrow it to tests/docs instead.
    if [[ "$GUARD_BASE" == "test-writer" && ( "$TOOL_NAME" == "Grep" || "$TOOL_NAME" == "Glob" ) ]]; then
      if [[ -z "$RAW_PATH" || "$RAW_PATH" == "." || "$RAW_PATH" == "./" \
            || "$RAW_PATH" == "$PROJECT_ROOT" || "$RAW_PATH" == "$PROJECT_ROOT/" ]]; then
        echo "CDAD path-guard: $TOOL_NAME without a bounded path searches the whole project; narrow the search to tests/ or docs/ (acotá la búsqueda a tests/docs) or pass an explicit path" >&2
        exit 2
      fi
    fi

    # A tool that carries no path (no file input) is not mediated here.
    if [[ -z "$RAW_PATH" ]]; then
      exit 0
    fi

    # B6 (PD-2/PD-8): `~` and `~/…` are absolute paths in disguise — the path
    # surface accepts them (the legacy branch expands them), but bash does not,
    # so they used to reach textual classification and pass. Expand them with
    # $HOME and let the outside-the-project rule (R1) below decide; every other
    # `~usuario…` form cannot be resolved reliably and is blocked. This covers
    # file_path, notebook_path and the Grep/Glob `path`.
    if [[ "$RAW_PATH" == "~" ]]; then
      RAW_PATH="$HOME"
    elif [[ "$RAW_PATH" == "~/"* ]]; then
      RAW_PATH="$HOME/${RAW_PATH#\~/}"
    elif [[ "$RAW_PATH" == "~"* ]]; then
      echo "CDAD path-guard: a '~user' path is outside the project and cannot be resolved ($RAW_PATH); blocking" >&2
      exit 2
    fi

    # R1 (PD-2/I10): an absolute path is inside the project only when the
    # remainder starts with '/'. A sibling whose name collides with the project
    # prefix (<root>x/...) is NOT under the root and must not be relativized
    # into a phantom in-project path.
    REL_PATH="$RAW_PATH"
    if [[ "$RAW_PATH" == /* ]]; then
      if [[ "$RAW_PATH" == "$PROJECT_ROOT" ]]; then
        REL_PATH="."
      elif [[ "$RAW_PATH" == "$PROJECT_ROOT"/* ]]; then
        REL_PATH="${RAW_PATH#"$PROJECT_ROOT"/}"
      else
        echo "CDAD path-guard: path outside the project root is not classifiable ($RAW_PATH); blocking" >&2
        exit 2
      fi
    fi
    REL_PATH="${REL_PATH#./}"

    CLI="${CDAD_PACKET_CLI:-$HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py}"
    if [[ ! -f "$CLI" ]]; then
      echo "CDAD path-guard: policy present but the classifier was not found; set CDAD_PACKET_CLI or install \$HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py — blocking without fallback" >&2
      exit 2
    fi

    # B4 (I10/C2): a Glob is mediated by `pattern` too. A pattern escaping with
    # '..' or absolute, or whose literal prefix (up to the first wildcard) is an
    # implementation path, leaves the bounded scope. The prefix is classified
    # both project-relative and resolved against `path` (supplementary probes).
    PROBES=("$REL_PATH")
    if [[ "$GUARD_BASE" == "test-writer" && "$TOOL_NAME" == "Glob" ]]; then
      PATTERN=$(echo "$INPUT" | jq -r '.tool_input.pattern // empty')
      if [[ "$PATTERN" == *".."* || "$PATTERN" == /* || "$PATTERN" == "~"* ]]; then
        echo "CDAD path-guard: Glob pattern escapes the bounded scope ('..', absolute or '~'); blocking" >&2
        exit 2
      fi
      PREFIX="${PATTERN%%[*?]*}"
      PREFIX="${PREFIX%/}"
      if [[ -n "$PREFIX" ]]; then
        PROBES+=("$PREFIX")
        if [[ -n "$REL_PATH" && "$REL_PATH" != "." ]]; then
          PROBES+=("${REL_PATH%/}/$PREFIX")
        fi
      fi
    fi

    PYTHON="${CDAD_PYTHON:-python3}"
    CLASSIFY_ARGS=()
    for probe in "${PROBES[@]}"; do
      CLASSIFY_ARGS+=(--classify "$probe")
    done
    if ! OUTPUT=$("$PYTHON" "$CLI" validate-policy --project-root "$PROJECT_ROOT" "${CLASSIFY_ARGS[@]}" 2>&1); then
      echo "CDAD path-guard: cannot classify '$REL_PATH' under the project policy (invalid policy or classifier failure); blocking without fallback" >&2
      echo "$OUTPUT" >&2
      exit 2
    fi
    CLASS=$(printf '%s\n' "$OUTPUT" | head -n1 | cut -f2)

    # B1 (inv. 3, PD-7): no role edits the single policy or the published
    # derived agents (derivatives and manifest) — the exclusion of the policy
    # prevails over any class-based permission.
    if [[ "$IS_EDIT_TOOL" == "1" ]]; then
      if [[ "$CLASS" == "policy" || "$REL_PATH" == ".opencode/agents/"* ]]; then
        echo "CDAD path-guard: no role edits the policy or the published derived agents ($REL_PATH); blocking (PD-7)" >&2
        exit 2
      fi
    fi

    # P-1 (004-002, owner decision 2026-10-02): a path declared in
    # path_policy.private_paths is denied to EVERY mediated role and tool. It is
    # the single deliberately obvious barrier, for files no role needs.
    if [[ "$CLASS" == "private" ]]; then
      echo "CDAD path-guard: private project path is denied to every role ($REL_PATH); blocking" >&2
      exit 2
    fi

    # B4: any supplementary pattern probe resolving implementation escapes.
    # R2ii (P-1 004-002): a Glob pattern may also point into a private path
    # from a bounded (parent) `path`; that escapes the private barrier just as
    # an implementation-reaching pattern escapes the role's scope.
    if (( ${#PROBES[@]} > 1 )) \
      && printf '%s\n' "$OUTPUT" | tail -n +2 | cut -f2 | grep -qxE 'implementation|private'; then
      echo "CDAD path-guard: Glob pattern reaches implementation or a private path from a bounded path; narrow the pattern to tests/docs" >&2
      exit 2
    fi

    case "$GUARD_BASE:$GUARD_MODE" in
      implementer:write)
        if [[ "$IS_EDIT_TOOL" == "1" ]]; then
          case "$CLASS" in
            test|colocated-test)
              echo "CDAD path-guard: implementer may not edit tests ($REL_PATH is $CLASS)" >&2
              exit 2 ;;
          esac
        fi
        exit 0 ;;
      test-writer:read)
        case "$CLASS" in
          implementation)
            echo "CDAD path-guard: test-writer may not read implementation ($REL_PATH)" >&2
            exit 2 ;;
        esac
        exit 0 ;;
      test-writer:write)
        case "$CLASS" in
          test|colocated-test)
            exit 0 ;;
          *)
            echo "CDAD path-guard: test-writer may only edit tests ($REL_PATH is $CLASS)" >&2
            exit 2 ;;
        esac ;;
    esac
    exit 0
  fi
fi

# ---------------------------------------------------------------------------
# Legacy behavior (no project policy): global hardcoded globs.
# ---------------------------------------------------------------------------

# Owner decision 2026-09-29: no Bash command filtering — the former
# content-guard block was retired with the Bash hooks (see header). Bash
# passes unfiltered; the path guard below applies to file_path tools only.

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
