#!/usr/bin/env bash
# validate-subagents.sh — cdad-001: validates that delegation via native
# sub-agents (subagent_type: cdad-<role>) is installed and operational end-to-end.
#
# Spec:   docs/specs/cdad-001-validate-subagents/spec.md
# Tests:  docs/specs/cdad-001-validate-subagents/tests/run_all.sh
# Usage:  bash scripts/validate-subagents.sh
#
# What it verifies (in order):
#   1. runtime  — the cdad-*.md agents exist in the INSTALLATION dir
#      ($HOME/.config/opencode/agents), not in the repo. If the runtime dir does
#      not exist, DOCUMENTED fallback: it compares against the repo (agents/)
#      with an explicit WARN and the stage counts as FAIL (runtime not installed).
#      Validated set: 5 base roles (architect/implementer/reviewer/scribe/
#      test-writer) + 5 Odoo variants (*-odoo with a fixed model per ADR-007).
#      The orchestrator (cdad-orchestrator) is validated separately (mode: all, no
#      model: — the user picks the model).
#   2. repo     — cross-check against the source of truth reusing
#      `install.sh --check` (comparison logic is not duplicated).
#   3. artifacts — enumerates and verifies the 5 artifacts per stage of the CDAD
#      cycle in docs/specs/cdad-001-validate-subagents/artifacts/.
#   4. models — each cdad-* agent declares the ACTIVE PROFILE's model in its
#      frontmatter (map scripts/cdad-models.sh; active profile = env
#      CDAD_MODEL_PROFILE > marker .cdad-models-profile > optimus); the
#      -odoo variants carry a FIXED model per role (ADR-007: the same in any
#      profile). cdad-orchestrator does NOT declare model: and is not part of this set.
#      Anti-bias guard in all 3 profiles: reviewer ≠ implementer (exact string
#      comparison) — covers misconfigured envs (CDAD_PREMIUM_MODEL_*).
#
# Exit: 0 if and only if ALL verifications pass; != 0 on any failure, printing
# what failed. Read-only: idempotent by design.
# Repo convention: set -euo pipefail (aligned with install.sh:12).
# Manual error handling (FAIL + if-forms) is compatible with -e: operations
# whose failure is expected are captured in if conditions, never as loose
# statements (reviewer cdad-001 finding #2).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$REPO_ROOT"
EXECUTION_CONTEXT=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --project-root)
      [ "$#" -ge 2 ] || { echo "ERROR: --project-root requires a value" >&2; exit 2; }
      PROJECT_ROOT="$2"; shift 2 ;;
    --execution-context)
      [ "$#" -ge 2 ] || { echo "ERROR: --execution-context requires a value" >&2; exit 2; }
      EXECUTION_CONTEXT="$2"; shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done
if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: --project-root must be an existing directory: $PROJECT_ROOT" >&2
  exit 2
fi
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"
if [ -n "${CDAD_INSTALL_ROOT+x}" ]; then
  case "$CDAD_INSTALL_ROOT" in
    /*) ;;
    *) echo "ERROR: CDAD_INSTALL_ROOT must be an absolute existing directory: $CDAD_INSTALL_ROOT" >&2; exit 2 ;;
  esac
  if [ ! -d "$CDAD_INSTALL_ROOT" ]; then
    echo "ERROR: CDAD_INSTALL_ROOT must be an absolute existing directory: $CDAD_INSTALL_ROOT" >&2
    exit 2
  fi
  INSTALL_ROOT="$CDAD_INSTALL_ROOT"
else
  INSTALL_ROOT="${HOME:-}"
fi
SPEC_DIR="$REPO_ROOT/docs/specs/cdad-001-validate-subagents"
ART_DIR="$SPEC_DIR/artifacts"
RUNTIME_DIR="$INSTALL_ROOT/.config/opencode/agents"
RUNTIME_INSTALL_DIR="$RUNTIME_DIR"
INSTALL_SH="$REPO_ROOT/install.sh"
PACKET_CLI="$REPO_ROOT/skills/cdad-cycle/scripts/cdad_packet.py"
SCOPED_MODEL_EXCEPTION=0
if [ -n "$EXECUTION_CONTEXT" ]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required to validate the execution context" >&2
    exit 2
  fi
  if [ ! -f "$PACKET_CLI" ]; then
    echo "ERROR: shared packet policy not found: $PACKET_CLI" >&2
    exit 2
  fi
  if ! POLICY_OUT=$(PYTHONDONTWRITEBYTECODE=1 python3 "$PACKET_CLI" validate-state \
      --project-root "$PROJECT_ROOT" --execution-context "$EXECUTION_CONTEXT" 2>&1); then
    echo "$POLICY_OUT" >&2
    exit 2
  fi
  echo "$POLICY_OUT"
  case "$POLICY_OUT" in
    *"model_policy=scoped-exception"*) SCOPED_MODEL_EXCEPTION=1 ;;
  esac
fi
# 5 base roles + 5 Odoo variants (fixed model per ADR-007, except the basic profile
# where agents inherit the runtime's model). The orchestrator is
# validated separately (not part of AGENTS): mode: all, no model:.
AGENTS=(cdad-architect cdad-implementer cdad-reviewer cdad-scribe cdad-test-writer \
        cdad-architect-odoo cdad-implementer-odoo cdad-reviewer-odoo cdad-scribe-odoo cdad-test-writer-odoo)

FAIL=0
# Diagnostics to stderr: does not pollute verifiable stdout (reviewer finding #4).
fail() { echo "❌ $1" >&2; FAIL=1; }
ok()   { echo "✅ $1"; }

echo "== cdad-001 validate-subagents =="

# --- Stage 1: runtime agents (source: installation, not repo) ----------------
echo "[runtime] agents in $RUNTIME_DIR"
if [ ! -d "$RUNTIME_DIR" ]; then
  echo "⚠️  runtime dir does not exist: $RUNTIME_DIR"
  echo "    Documented fallback: comparing against repo agents/ (source of truth)."
  echo "    The stage counts as FAIL: the runtime is not installed."
  fail "runtime agents dir missing: $RUNTIME_DIR"
  RUNTIME_DIR="$REPO_ROOT/agents"   # fallback: informational only
fi
for a in "${AGENTS[@]}"; do
  if [ ! -f "$RUNTIME_DIR/$a.md" ]; then
    fail "runtime agent missing: $a.md"
  elif ! grep -q '^description:' "$RUNTIME_DIR/$a.md"; then
    # Minimal frontmatter: covers the §6 claim ("static config (frontmatter
    # + byte-compare)") — install.sh --check does the byte-compare (Stage 2),
    # this Stage 1 validates the frontmatter (reviewer finding #5).
    fail "frontmatter without description: $a.md"
  fi
done
if [ "$FAIL" -eq 0 ]; then ok "10/10 runtime agents present (5 base + 5 Odoo variants; frontmatter OK)"; fi

# --- Stage 2: cross-check against repo (reuses install.sh --check) ------------
echo "[repo] cross-check: install.sh --check"
# The invocation is made with `bash`, so only the file's existence matters,
# not the +x bit (reviewer finding #3). Captured in if-form because of set -e.
if [ ! -f "$INSTALL_SH" ]; then
  fail "install.sh not found at $INSTALL_SH"
else
  if CHECK_OUT=$(bash "$INSTALL_SH" --check 2>&1); then
    CHECK_RC=0
  else
    CHECK_RC=$?
  fi
  echo "$CHECK_OUT" | tail -3
  if [ "$CHECK_RC" -ne 0 ]; then
    fail "install.sh --check failed (rc=$CHECK_RC)"
  else
    ok "install.sh --check PASS"
  fi
fi

# --- Stage 3: artifacts per stage (enumerate and verify format) -----------
echo "[artifacts] $ART_DIR"
stage() { # name path ok(0|1)
  if [ "$3" = "0" ]; then ok "$1 -> OK"; else fail "$1 -> FAIL ($2)"; fi
}
if [ -f "$ART_DIR/spec.md" ] && grep -q "^## 2\. Postcondición\|^## 2\. Postcondition" "$ART_DIR/spec.md"; then
  stage architect "spec.md" 0; else stage architect "spec.md" 1; fi
if [ -d "$ART_DIR/tests" ] && [ -n "$(ls -A "$ART_DIR/tests" 2>/dev/null)" ]; then
  stage test-writer "tests/" 0; else stage test-writer "tests/" 1; fi
# impl.diff: FORMAT verification (well-formed diff), not verification that it
# still applies against the current tree.
#
# Amendment 2026-09-02 (epic-002-cdad-audit-fixes, 002-011, finding B8): the
# previous version required "git apply --check[--reverse]" against the real
# tree — i.e., that the diff frozen on Aug 05 2026 still applied
# (or un-applied) over scripts/validate-subagents.sh, the same file
# this validator keeps editing. Any legitimate later change to the
# validator (cdad-003, ADR-007, this very epic) invalidates the diff without
# that being a real bug — it is a self-invalidating assertion: it can never
# go green again, and it stayed permanently red without
# docs/progress.md recording it as debt (hidden debt, against the skill's
# own Verification rule). The spike's evidentiary value is already
# captured in findings/validation-cdad-001.md; the remaining durable value is
# that the ARTIFACT be a well-formed diff (evidence that
# the spike produced a real diff, not free-form text) — that is stable.
if [ -f "$ART_DIR/impl.diff" ] && grep -q '^diff --git' "$ART_DIR/impl.diff" && grep -qE '^@@ .* @@' "$ART_DIR/impl.diff"; then
  stage implementer "impl.diff" 0; else stage implementer "impl.diff" 1; fi
if [ -f "$ART_DIR/review.md" ] && grep -q "^Reviewer model: " "$ART_DIR/review.md"; then
  stage reviewer "review.md" 0; else stage reviewer "review.md" 1; fi
if [ -f "$ART_DIR/memory-bank.md" ] && grep -qE "^##? .*2026|^[0-9]{4}-[0-9]{2}-[0-9]{2}" "$ART_DIR/memory-bank.md"; then
  stage scribe "memory-bank.md" 0; else stage scribe "memory-bank.md" 1; fi

# --- Stage 4: models per agent (profile-aware; single source of the map) ------
echo "[models] expected model per agent"
# The map lives in scripts/cdad-models.sh (single source: duplicates ADR-001/005 and
# the §2 table of the Roles Contract for the optimus profile). With the optimus
# profile (default/design) it yields EXACTLY the historical map — intentional
# validation guard: if the repo or the runtime drifts from the decision, this
# stage detects it. It runs last (after the artifacts) so as not to break the
# context of cdad-001's impl.diff, which only covers up to Stage 2.
MODELS_SH="$REPO_ROOT/scripts/cdad-models.sh"
MODELS_LOADED=0
if [ ! -f "$MODELS_SH" ]; then
  fail "scripts/cdad-models.sh not found (single source of the model map)"
else
  # shellcheck source=cdad-models.sh
  source "$MODELS_SH"
  MODELS_LOADED=1
fi

# Active profile: env CDAD_MODEL_PROFILE > runtime marker > optimus.
ACTIVE_PROFILE="${CDAD_MODEL_PROFILE:-}"
if [ -z "$ACTIVE_PROFILE" ] && [ -f "$RUNTIME_INSTALL_DIR/.cdad-models-profile" ]; then
  ACTIVE_PROFILE="$(cat "$RUNTIME_INSTALL_DIR/.cdad-models-profile")"
fi
ACTIVE_PROFILE="${ACTIVE_PROFILE:-optimus}"
if [ "$MODELS_LOADED" -eq 1 ] && ! cdad_valid_profile "$ACTIVE_PROFILE"; then
  fail "invalid model profile: '$ACTIVE_PROFILE' (expected: economical | optimus | premium | basic)"
  ACTIVE_PROFILE="optimus"
fi
echo "[models] active profile: $ACTIVE_PROFILE"
if [ "$ACTIVE_PROFILE" = "basic" ]; then
  echo "[models] basic profile: no fixed models — agents inherit the runtime's model; the reviewer≠implementer anti-bias is NOT verified in this profile (ADR-007)"
fi

declare -A MODEL_EXPECTED
if [ "$MODELS_LOADED" -eq 1 ]; then
  for a in "${AGENTS[@]}"; do
    MODEL_EXPECTED["$a"]="$(cdad_model "$ACTIVE_PROFILE" "${a#cdad-}")"
  done
fi
# cdad-orchestrator does NOT declare model: — the user picks the model when
# selecting it (ADR-001/005: the orchestrator stays without a fixed model).
for a in "${AGENTS[@]}"; do
  expected="${MODEL_EXPECTED[$a]:-}"
  [ -z "$expected" ] && continue
  actual="$(sed -n 's/^model:[[:space:]]*//p' "$RUNTIME_DIR/$a.md" 2>/dev/null | head -1)"
  if [ -z "$actual" ]; then
    fail "model missing in $a.md (expected: $expected)"
  elif [ "$actual" != "$expected" ]; then
    fail "wrong model in $a.md: '$actual' (expected: '$expected')"
  fi
done
# Anti-bias guard (all profiles): reviewer and implementer must run on
# DIFFERENT models. Exact string comparison — detects misconfigured envs
# (e.g. CDAD_PREMIUM_MODEL_REVIEWER == CDAD_PREMIUM_MODEL_IMPLEMENTER)
# without needing to infer model family.
REVIEWER_MODEL="${MODEL_EXPECTED[cdad-reviewer]:-}"
IMPLEMENTER_MODEL="${MODEL_EXPECTED[cdad-implementer]:-}"
if [ "$SCOPED_MODEL_EXCEPTION" -eq 0 ] && [ -n "$REVIEWER_MODEL" ] && [ -n "$IMPLEMENTER_MODEL" ] && [ "$REVIEWER_MODEL" = "$IMPLEMENTER_MODEL" ]; then
  fail "reviewer and implementer share a model ($REVIEWER_MODEL) — violates the anti-bias invariant; check CDAD_PREMIUM_MODEL_REVIEWER/IMPLEMENTER"
fi

# Anti-bias guard — Claude Code (findings B1/B2, 2026-09-02): the guard
# above only evaluates cdad_model (OpenCode/mofgw map). cdad_model_claude
# (haiku/sonnet/opus) was never checked, and the premium profile gave "opus"
# for reviewer AND implementer — silent violation of the same invariant,
# in the same profile, with no guard detecting it. In Claude Code there
# are no cross-model families (everything is Anthropic-native): "different" here
# means a different string, same as the guard above but against the
# correct map. basic is exempt (same trade-off documented in ADR-007).
if [ "$SCOPED_MODEL_EXCEPTION" -eq 0 ] && [ "$MODELS_LOADED" -eq 1 ] && [ "$ACTIVE_PROFILE" != "basic" ]; then
  CC_REVIEWER_MODEL="$(cdad_model_claude "$ACTIVE_PROFILE" reviewer)"
  CC_IMPLEMENTER_MODEL="$(cdad_model_claude "$ACTIVE_PROFILE" implementer)"
  if [ -n "$CC_REVIEWER_MODEL" ] && [ -n "$CC_IMPLEMENTER_MODEL" ] && [ "$CC_REVIEWER_MODEL" = "$CC_IMPLEMENTER_MODEL" ]; then
    fail "Claude Code: reviewer and implementer share a model ($CC_REVIEWER_MODEL) in profile '$ACTIVE_PROFILE' — violates the anti-bias invariant (cdad_model_claude)"
  fi
fi

if [ -f "$RUNTIME_DIR/cdad-orchestrator.md" ] && grep -q '^model:' "$RUNTIME_DIR/cdad-orchestrator.md"; then
  fail "cdad-orchestrator.md must not declare model: (the user picks the model)"
fi
if [ "$FAIL" -eq 0 ]; then ok "models OK (10/10: 5 base + 5 Odoo variants, per profile $ACTIVE_PROFILE; orchestrator without model:)"; fi

# --- Verdict -----------------------------------------------------------------
if [ "$FAIL" -eq 0 ]; then
  echo "== RESULT: PASS (all verifications OK) =="
  exit 0
else
  echo "== RESULT: FAIL (see the ❌ messages above) =="
  exit 1
fi
