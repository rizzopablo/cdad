#!/usr/bin/env bash
# =============================================================================
# validate-consistency.sh
#
# Validation oracle of the epic docs/epics/epic-002-cdad-audit-fixes/plan.md.
# Each block corresponds to a feature of the epic (002-NNN-<slug>) and verifies
# the postcondition(s) that feature closes, against the report
# findings/audit-consistencia-2026-09-02.md. Pure bash (grep/sed/awk/diff),
# no external dependencies.
#
# Usage:
#   bash tests/validate-consistency.sh
#
# Output: explicit PASS/FAIL asserts + final counter. Exit 0 if everything passes.
# =============================================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS_COUNT=0
FAIL_COUNT=0

pass() { PASS_COUNT=$((PASS_COUNT + 1)); printf 'PASS: %s\n' "$*"; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf 'FAIL: %s\n' "$*"; }

assert_file() {
  if [[ -f "$ROOT/$1" ]]; then pass "$2 ($1 exists)"; else fail "$2 ($1 does NOT exist)"; fi
}

assert_file_has() {
  if [[ -f "$ROOT/$1" ]] && grep -Eq -e "$2" "$ROOT/$1"; then
    pass "$3 ($1 contains '$2')"
  else
    fail "$3 ($1 does NOT contain '$2')"
  fi
}

assert_file_not_has() {
  if [[ -f "$ROOT/$1" ]] && ! grep -Eq -e "$2" "$ROOT/$1"; then
    pass "$3 ($1 does NOT contain '$2')"
  else
    fail "$3 ($1 DOES contain '$2', not allowed)"
  fi
}

assert_files_identical() {
  # assert_files_identical <path1> <path2> <message>
  if [[ -f "$ROOT/$1" && -f "$ROOT/$2" ]] && diff -q "$ROOT/$1" "$ROOT/$2" >/dev/null 2>&1; then
    pass "$3 ($1 == $2)"
  else
    fail "$3 ($1 != $2)"
  fi
}

assert_cmd_ok() {
  # assert_cmd_ok "<command>" <message>
  if eval "$1" >/dev/null 2>&1; then pass "$2"; else fail "$2"; fi
}

frontmatter() {
  # frontmatter <file> — prints the ---...--- block (without the delimiters)
  awk 'BEGIN{c=0} /^---/{c++; next} c==1 {print}' "$1"
}

bash_section() {
  # bash_section <file> — prints ONLY the frontmatter 'bash:' section
  frontmatter "$1" | awk '/^[[:space:]]*bash:[[:space:]]*$/ {on=1; print; next} on'
}

assert_string_not_has() {
  # assert_string_not_has <content> <grep-pattern> <message>
  if [[ -n "$1" ]] && ! printf '%s' "$1" | grep -Eq -e "$2"; then
    pass "$3 (does not contain '$2')"
  else
    fail "$3 (contains '$2', not allowed)"
  fi
}

echo "############################################"
echo "# epic-002-cdad-audit-fixes — validate-consistency"
echo "############################################"
echo "(sections are filled in feature by feature; see plan.md)"
echo

echo "############################################"
echo "# F002 — single-source state schema (B9)"
echo "############################################"

# assets/state-template.json is the single source: it must carry ALL fields
# (including the epic ones), not only the feature ones.
for key in stack active_epic epic_stage epic_features epic_history \
           audit_status postconditions_status stage_history active_feature \
           current_stage tdd_substage approver last_updated version; do
  assert_file_has "skills/cdad-cycle/assets/state-template.json" "\"$key\"" \
    "F002: state-template.json declares the field '$key'"
done

assert_file_has "skills/cdad-cycle/references/state-detection.md" 'idle' \
  "F002: state-detection.md documents the current_stage value 'idle'"

assert_file_has "skills/cdad-cycle/SKILL.md" \
  'assets/state-template\.json' \
  "F002: SKILL.md § State file references assets/state-template.json as the full schema"

assert_file_has "skills/cdad-cycle/references/bootstrap.md" \
  'assets/state-template\.json' \
  "F002: bootstrap.md Step 4 references assets/state-template.json instead of reproducing the schema"

assert_file_has "skills/cdad-epic/SKILL.md" \
  'cdad-cycle/assets/state-template\.json' \
  "F002: cdad-epic/SKILL.md references the cdad-cycle base schema instead of duplicating it"

echo
echo "############################################"
echo "# F004 — verdict-tuple in the 4 reviewer agents (B3) + load table (M5)"
echo "############################################"

for f in agents/cdad-reviewer.md agents/claude-code/cdad-reviewer.md \
         agents/cdad-reviewer-odoo.md agents/claude-code/cdad-reviewer-odoo.md; do
  assert_file_has "$f" 'Bucket' "F004: $f includes the Bucket field in the finding format"
  assert_file_has "$f" 'Abstenci' "F004: $f includes an Abstentions section"
done

# The "Cómo leer las references" table is the specific section (it is not enough
# for the file to be mentioned elsewhere in the document).
load_table() { awk '/## Cómo leer las references/{f=1} f{print} /^---$/{if(f)exit}' "$ROOT/skills/cdad-cycle/SKILL.md"; }
if load_table | grep -q 'verdict-tuple\.md'; then
  pass "F004: the 'Cómo leer las references' table includes verdict-tuple.md"
else
  fail "F004: the 'Cómo leer las references' table does NOT include verdict-tuple.md"
fi
if load_table | grep -q 'claude-code-delegation\.md'; then
  pass "F004: the 'Cómo leer las references' table includes claude-code-delegation.md"
else
  fail "F004: the 'Cómo leer las references' table does NOT include claude-code-delegation.md"
fi

echo
echo "############################################"
echo "# F009 — calibrated bash allowlist (B1, M3, M4)"
echo "############################################"

# test-writer/implementer (generic + odoo): no longer bash:{"*":allow}; yes to an
# allowlist with its own git commit (contract §5: "they write and commit their
# own artifact") and WITHOUT content-reading commands (cat/head/tail/rg)
# which are the real leak vector into src/** or tests/**.
for f in agents/cdad-test-writer.md agents/cdad-implementer.md \
         agents/cdad-test-writer-odoo.md agents/cdad-implementer-odoo.md; do
  # (line comments of the block are discarded: they may quote "*": allow
  # in prose explaining what was removed, without that being the effective value)
  b="$(bash_section "$ROOT/$f" 2>/dev/null | grep -v '^[[:space:]]*#' || true)"
  if [[ -n "$b" ]] && printf '%s' "$b" | grep -Eq -e '"\*":[[:space:]]*allow'; then
    fail "F009: $f: bash still has \"*\": allow (unclosed leak)"
  else
    pass "F009: $f: bash does NOT have \"*\": allow"
  fi
  assert_string_not_has "$b" '"cat \*":[[:space:]]*allow' \
    "F009: $f: bash does not allow 'cat *' (arbitrary content reading)"
  assert_string_not_has "$b" '"head \*":[[:space:]]*allow' \
    "F009: $f: bash does not allow 'head *'"
  assert_string_not_has "$b" '"tail \*":[[:space:]]*allow' \
    "F009: $f: bash does not allow 'tail *'"
  assert_file_has "$f" '"git commit\*?":[[:space:]]*allow|"git add' \
    "F009: $f: preserves git commit/add (contract §5, write-capable roles commit their artifact)"
done

# architect/reviewer/scribe — odoo variants: no longer "git *": allow (AP-17:
# a read-only role must not be able to commit/push/reset).
for f in agents/cdad-architect-odoo.md agents/cdad-reviewer-odoo.md agents/cdad-scribe-odoo.md; do
  assert_string_not_has "$(bash_section "$ROOT/$f" 2>/dev/null || true)" '"git \*":[[:space:]]*allow' \
    "F009: $f: bash has NO unscoped 'git *': allow (AP-17)"
  assert_file_has "$f" '"git diff\*?":[[:space:]]*allow' \
    "F009: $f: preserves git diff (non-mutating inspection)"
done

# architect/reviewer/scribe — generic ones: language-agnostic allowlist
# (M3: they were Go-only — go test/go vet/go build/gofmt — unusable in
# any non-Go project).
for f in agents/cdad-architect.md agents/cdad-reviewer.md agents/cdad-scribe.md; do
  assert_string_not_has "$(bash_section "$ROOT/$f" 2>/dev/null || true)" 'go test\*' \
    "F009: $f: the bash allowlist is no longer Go-only"
  assert_file_has "$f" '"make \*":[[:space:]]*allow' \
    "F009: $f: the agnostic allowlist includes 'make *' (the methodology's AGENTS.md convention)"
done

# Claude Code: Bash hook for test-writer/implementer (B1 — the current hook
# only matches Read|Grep|Glob and Edit|Write; Bash was left uncovered).
assert_file_has "agents/claude-code/cdad-test-writer.md" 'matcher:[[:space:]]*Bash' \
  "F009: cdad-test-writer (Claude Code) has a PreToolUse hook with a Bash matcher"
assert_file_has "agents/claude-code/cdad-implementer.md" 'matcher:[[:space:]]*Bash' \
  "F009: cdad-implementer (Claude Code) has a PreToolUse hook with a Bash matcher"

# path-guard.sh: new content-guard mode via bash + fix of the
# relativize() fail-open for absolute paths outside $PWD.
assert_file_has "scripts/claude-code-path-guard.sh" 'bash-content-guard|BASH_CONTENT' \
  "F009: path-guard.sh implements a guard mode for Bash"
assert_file_has "scripts/claude-code-path-guard.sh" 'HOME.*fuera del proyecto|fuera de \$PWD|outside.*PWD|no relativiza' \
  "F009: path-guard.sh documents or fixes the fail-open for external absolute paths"

echo
echo "############################################"
echo "# F010 — agent hygiene (M2, M6, M7, M8)"
echo "############################################"

# M2: the Claude Code scribe pointed to docs/memory-bank.md (it does not exist in
# the convention — the real Memory Bank is activeContext.md/progress.md/adr/).
assert_file_not_has "agents/claude-code/cdad-scribe.md" 'docs/memory-bank\.md' \
  "F010 (M2): cdad-scribe (Claude Code) no longer references docs/memory-bank.md"
assert_file_has "agents/claude-code/cdad-scribe.md" 'activeContext\.md' \
  "F010 (M2): cdad-scribe (Claude Code) references activeContext.md (the real Memory Bank)"

# M6: invented API (from Agent import agent) + AP-7 citation misattributed
# (AP-7 is "Memory Bank out of date"; the isolation invariant is
# AP-1/AP-2).
assert_file_not_has "skills/cdad-cycle/references/claude-code-delegation.md" \
  'from Agent import agent' \
  "F010 (M6): claude-code-delegation.md no longer has the invented Python API"
assert_file_not_has "skills/cdad-cycle/references/claude-code-delegation.md" \
  '\(AP-7' \
  "F010 (M6): claude-code-delegation.md no longer cites AP-7 for the isolation invariant (it is AP-1/AP-2)"

# M7: the 4 loose skills/*.md files remain as a one-line stub (or are deleted);
# in any case, they cannot remain a complete divergent copy.
for f in skills/handoff-prompts.md skills/re-entry.md skills/feature-handoff.md skills/epic-planning.md; do
  if [[ -f "$ROOT/$f" ]]; then
    lines="$(wc -l < "$ROOT/$f" | tr -d ' ')"
    if [[ "$lines" -le 10 ]]; then
      pass "F010 (M7): $f is a short stub (≤10 lines) or was removed"
    else
      fail "F010 (M7): $f is still a full copy ($lines lines) — reading trap"
    fi
  else
    pass "F010 (M7): $f was removed"
  fi
done

# M8: private context (arXiv pipeline, fb-012, guard-event-log, owner's
# name) outside a distributable skill.
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'mi pipeline arXiv' \
  "F010 (M8): verdict-tuple.md without a reference to 'mi pipeline arXiv'"
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'fb-012' \
  "F010 (M8): verdict-tuple.md without a reference to 'fb-012'"
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'aprobación de Pablo' \
  "F010 (M8): verdict-tuple.md without the owner's proper name"

echo
echo "############################################"
echo "# F001 — honest profiles note + §2 block drift (B7)"
echo "############################################"

# The profiles note mentions the 4 real profiles (--basic was missing) and
# caveats the anti-bias invariant for the profile that suspends it.
for f in skills/cdad-cycle/SKILL.md agents/cdad-orchestrator.md agents/claude-code/cdad-orchestrator.md; do
  assert_file_has "$f" '\-\-basic' "F001: $f mentions the --basic profile in the switch"
  assert_file_has "$f" 'basic.*[Nn][Oo] est[aá] garantizado|basic.*suspendid|salvo.*basic|excepto.*basic' \
    "F001: $f caveats the anti-bias invariant for the basic profile"
done

# The §2 block (Roles Contract + profiles note) remains INTENTIONALLY identical
# across the 3 files (ADR-007: "The identity of the §2 block (SKILL ↔ orchestrator)
# with the profiles note was verified byte-identical" — verified by hand at the
# time, never automated). This assert is the missing automation: it extracts from
# "### 2. Contrato de cada rol" up to and including the "Switch:" line, and compares.
extract_role_contract() {
  awk '/^### 2\. Contrato de cada rol/{f=1} f{print; if ($0 ~ /^Modelos del diseño/) exit}' "$ROOT/$1"
}
extract_role_contract "skills/cdad-cycle/SKILL.md" > /tmp/rc_skill.$$ 2>/dev/null
extract_role_contract "agents/cdad-orchestrator.md" > /tmp/rc_oc.$$ 2>/dev/null
extract_role_contract "agents/claude-code/cdad-orchestrator.md" > /tmp/rc_cc.$$ 2>/dev/null
if diff -q /tmp/rc_skill.$$ /tmp/rc_oc.$$ >/dev/null 2>&1 && diff -q /tmp/rc_skill.$$ /tmp/rc_cc.$$ >/dev/null 2>&1; then
  pass "F001: §2 block (Roles Contract + profiles note) identical in SKILL.md and the 2 orchestrators"
else
  fail "F001: §2 block DIVERGES between SKILL.md and the orchestrators (see diff)"
fi
rm -f /tmp/rc_skill.$$ /tmp/rc_oc.$$ /tmp/rc_cc.$$

echo
echo "############################################"
echo "# F003 — SKILL.md ↔ stage-N gates synchronized + B11"
echo "############################################"

# Gate 2→3: SKILL.md includes the plan.md item that previously only stage-2 had.
assert_file_has "skills/cdad-cycle/SKILL.md" 'plan\.md.*existe.*auto-revisión|Si el spec es complejo' \
  "F003: SKILL.md's Gate 2→3 includes the plan.md item (previously only in stage-2)"

# Gate 3→4: stage-3-tdd.md includes the 2 items previously only in SKILL.md.
assert_file_has "skills/cdad-cycle/references/stage-3-tdd.md" 'Test Audit completado y aprobado' \
  "F003: Gate 3→4 of stage-3-tdd.md includes 'Test Audit completado y aprobado' (previously only in SKILL.md)"
assert_file_has "skills/cdad-cycle/references/stage-3-tdd.md" 'justificación explícita en spec\.md' \
  "F003: Gate 3→4 of stage-3-tdd.md includes 'justificación explícita en spec.md' (previously only in SKILL.md)"

# Gate 5→done: CI carve-out in stage-5-merge.md + "Feature mergeada" in SKILL.md.
assert_file_has "skills/cdad-cycle/references/stage-5-merge.md" 'Si NO hay CI configurado' \
  "F003: Gate 5→done of stage-5-merge.md includes the CI carve-out (previously only in SKILL.md)"
assert_file_has "skills/cdad-cycle/SKILL.md" 'Feature mergeada' \
  "F003: Gate 5→done of SKILL.md includes 'Feature mergeada' (previously only in stage-5-merge.md)"

# B11: the 4→5 gate no longer contradicts the explicit-delegation exception that
# the file itself documents (Layer 2 / §2.3).
for f in skills/cdad-cycle/SKILL.md skills/cdad-cycle/references/stage-4-review.md; do
  assert_file_not_has "$f" '\[ \] Usuario aprobó priorización \(no delegado al LLM\)\.' \
    "F003 (B11): $f no longer has the absolute wording of the 4→5 gate"
  assert_file_has "$f" 'agente-delegada con pedido explícito' \
    "F003 (B11): $f mentions the explicit-delegation exception in the gate"
done
assert_file_not_has "skills/cdad-cycle/references/stage-2-specification.md" \
  '\*\*AP-10\*\*: delegar la aprobación al LLM\. Indelegable\.' \
  "F003 (B11): the short AP-10 in stage-2 is no longer absolute without the exception"

echo
echo "############################################"
echo "# F007 — Claude Code orchestrator repaired (B6)"
echo "############################################"

CCO="agents/claude-code/cdad-orchestrator.md"
assert_file_has "$CCO" 'con la herramienta' \
  "F007: $CCO instructs delegating via a tool (not task/delegate)"
assert_file_has "$CCO" 'Agent.{0,10}subagent_type' \
  "F007: $CCO mentions the Agent tool with subagent_type"
assert_file_not_has "$CCO" 'vía\s*\n?\s*`delegate`; roles write-capable' \
  "F007: $CCO no longer instructs 'delegate' as the per-role invocation mechanism"
assert_file_has "$CCO" 'resolvé el sufijo de' \
  "F007: $CCO resolves the stack suffix before delegating (parity with OpenCode)"
assert_file_has "$CCO" 'cdad-<rol>-<stack>' \
  "F007: $CCO mentions the cdad-<rol>-<stack> pattern for specialized variants"

echo
echo "############################################"
echo "# F008 — anti-bias guard also for cdad_model_claude (B2)"
echo "############################################"

# shellcheck source=scripts/cdad-models.sh
source "$ROOT/scripts/cdad-models.sh"
for p in economical optimus premium; do
  r="$(cdad_model_claude "$p" reviewer)"
  i="$(cdad_model_claude "$p" implementer)"
  if [[ -n "$r" && -n "$i" && "$r" != "$i" ]]; then
    pass "F008: cdad_model_claude profile '$p' — reviewer ($r) != implementer ($i)"
  else
    fail "F008: cdad_model_claude profile '$p' — reviewer ($r) == implementer ($i), violates anti-bias"
  fi
done

assert_file_has "scripts/validate-subagents.sh" 'cdad_model_claude' \
  "F008: validate-subagents.sh evaluates cdad_model_claude (previously only OpenCode's cdad_model)"

echo
echo "############################################"
echo "# F005 — reviewer taxonomy unified (B4)"
echo "############################################"

CCR="agents/claude-code/cdad-reviewer.md"
assert_file_not_has "$CCR" '\*\*CRITICAL\*\*|\*\*MAJOR\*\*|\*\*MINOR\*\*|\*\*TRIVIAL\*\*' \
  "F005: $CCR no longer uses the CRITICAL/MAJOR/MINOR/TRIVIAL taxonomy"
assert_file_has "$CCR" 'Critical:.*Bloquea merge' \
  "F005: $CCR uses the addyosmani taxonomy (Critical/Required/Nit/Optional/FYI)"
assert_file_has "$CCR" 'Eje 4: Security' \
  "F005: $CCR includes the Security axis (previously absent — the only one of the 4 reviewers without it)"

# The 4 reviewers now share the same severity taxonomy.
for f in agents/cdad-reviewer.md agents/cdad-reviewer-odoo.md agents/claude-code/cdad-reviewer-odoo.md; do
  assert_file_has "$f" 'Critical:.*Bloquea merge' \
    "F005: $f already used the addyosmani taxonomy (no changes, parity verification)"
done

echo
echo "############################################"
echo "# F006 — property tests contradiction + RED discipline (B5 + decision 3)"
echo "############################################"

# The exclusion phrase no longer includes "property tests" wholesale — it separates
# exhaustive coverage/load-perf/non-derived edge cases (outside the cycle)
# from property tests derived from invariants marked by the spec (inside,
# sub-phase 3.4).
for f in skills/cdad-cycle/SKILL.md skills/cdad-cycle/references/stage-3-tdd.md; do
  assert_file_not_has "$f" 'cobertura exhaustiva, property tests, load' \
    "F006: $f no longer groups property tests inside the cycle's exclusion phrase"
  assert_file_has "$f" 'Property tests.*[Nn][Oo]? son la misma pregunta|Property tests derivados de invariantes' \
    "F006: $f clarifies that property tests derived from the spec's invariants do belong to the cycle"
  assert_file_has "$f" 'RED verifica el requerimiento, no maximiza cobertura' \
    "F006: $f declares the RED-verifies-the-requirement rule"
done

# The rule also reaches the system prompt of the 4 test-writers (not just the
# reference, which may not get loaded).
for f in agents/cdad-test-writer.md agents/claude-code/cdad-test-writer.md \
         agents/cdad-test-writer-odoo.md agents/claude-code/cdad-test-writer-odoo.md; do
  assert_file_has "$f" 'verifica el requerimiento, no maximiza cobertura' \
    "F006: $f — the RED Procedure includes the no-over-specification rule"
done

echo
echo "############################################"
echo "# F011 — consolidated validator (B8)"
echo "############################################"

assert_file_not_has "scripts/validate-subagents.sh" 'git apply --check --reverse' \
  "F011 (B8): validate-subagents.sh no longer requires impl.diff to still apply against the tree (self-invalidating assertion retired)"
assert_file_has "scripts/validate-subagents.sh" "diff --git" \
  "F011 (B8): validate-subagents.sh still verifies impl.diff's format (well-formed diff)"

if bash "$ROOT/scripts/validate-subagents.sh" >/dev/null 2>&1; then
  pass "F011: scripts/validate-subagents.sh (active profile) → PASS"
else
  fail "F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details"
fi

if bash "$ROOT/tests/validate-odoo-specialization.sh" >/dev/null 2>&1; then
  pass "F011: tests/validate-odoo-specialization.sh → PASS (zero regression over cdad-003/004)"
else
  fail "F011: tests/validate-odoo-specialization.sh → FAIL"
fi

echo
echo "############################################"
echo "# F012 — epic dogfood (M9 fixed, M10)"
echo "############################################"

assert_file "docs/epics/epic-001-superpowers-gaps/closure.md" \
  "F012 (M9): retrospective closure.md of epic-001-superpowers-gaps exists"
assert_file_has "docs/epics/epic-001-superpowers-gaps/closure.md" 'Cerrado' \
  "F012 (M9): closure.md has a closure date"
assert_file_has "skills/cdad-epic/SKILL.md" 'Por qué no hay un sub-agente' \
  "F012 (M10): documented decision about the absence of a cdad-epic-* sub-agent"

echo "############################################"
echo "# RESULT"
echo "############################################"
echo "Assert PASS: $PASS_COUNT"
echo "Assert FAIL: $FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  echo "FAIL: $FAIL_COUNT assert(s) failed."
  exit 1
fi

echo "PASS: all of epic 002's assertions verified."
exit 0
