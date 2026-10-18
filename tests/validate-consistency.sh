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

assert_file_missing() {
  # assert_file_missing <path> <message>
  # 006-002 U3 (PD-9): a file withdrawn from the installable tree is asserted by
  # ABSENCE (assert_file_not_has on a missing file cannot distinguish).
  if [[ ! -f "$ROOT/$1" ]]; then
    pass "$2 ($1 does not exist)"
  else
    fail "$2 ($1 still exists)"
  fi
}

assert_tree_not_has() {
  # assert_tree_not_has <dir> <grep-pattern> <message>
  if ! grep -rEq -e "$2" "$ROOT/$1" 2>/dev/null; then
    pass "$3 ($1 is free of '$2')"
  else
    fail "$3 ($1 still contains '$2')"
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
  frontmatter "$1" | awk '/^[[:space:]]*bash:[[:space:]]*$/ {on=1; next} on && /^[[:space:]]{2}[A-Za-z_-]+:/ {exit} on'
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
  assert_file_has "$f" 'Abstenti' "F004: $f includes an Abstentions section"
done

# The "How to read the references" table is the specific section (it is not enough
# for the file to be mentioned elsewhere in the document).
load_table() { awk '/## How to read the references/{f=1} f{print} /^---$/{if(f)exit}' "$ROOT/skills/cdad-cycle/SKILL.md"; }
if load_table | grep -q 'verdict-tuple\.md'; then
  pass "F004: the 'How to read the references' table includes verdict-tuple.md"
else
  fail "F004: the 'How to read the references' table does NOT include verdict-tuple.md"
fi
# 006-002 U3 (PD-9): the two runtime references leave the installable skill, so
# the table must NOT index them any more — a row pointing to a removed file is
# the "dangling pointer" the unit forbids (reformulated, not deleted: the table
# itself is still required by the check above).
if load_table | grep -q 'opencode-delegation\.md'; then
  fail "F004 (006-002 PD-9): the 'How to read the references' table still includes opencode-delegation.md (withdrawn from the installable skill)"
else
  pass "F004 (006-002 PD-9): the 'How to read the references' table no longer includes opencode-delegation.md (withdrawn)"
fi
if load_table | grep -q 'claude-code-delegation\.md'; then
  fail "F004 (006-002 PD-9): the 'How to read the references' table still includes claude-code-delegation.md (withdrawn from the installable skill)"
else
  pass "F004 (006-002 PD-9): the 'How to read the references' table no longer includes claude-code-delegation.md (withdrawn)"
fi

echo
echo "# F009 — permissive bash policy (owner decision 2026-09-29)"
echo "############################################"

# Owner decision 2026-09-29 (spec docs/specs/permissive-bash-policy-2026-09-29/
# spec.yaml; reverses 002-009): NO operation filtering — every role agent's
# effective bash block is EXACTLY the catch-all allow. The retained barriers
# are PATH-based (edit/read/grep maps, CC path-guard) and contract-level.
# Declared, NOT a sandbox.

# All 10 role agents (generic + odoo): the effective bash rules (comments
# discarded) are exactly one rule — the catch-all allow.
for f in agents/cdad-architect.md agents/cdad-test-writer.md agents/cdad-implementer.md \
         agents/cdad-reviewer.md agents/cdad-scribe.md \
         agents/cdad-architect-odoo.md agents/cdad-test-writer-odoo.md \
         agents/cdad-implementer-odoo.md agents/cdad-reviewer-odoo.md \
         agents/cdad-scribe-odoo.md; do
  b="$(bash_section "$ROOT/$f" 2>/dev/null | grep -v '^[[:space:]]*#' | grep -v '^[[:space:]]*bash:' || true)"
  if [[ "$b" == $'    "*": allow' ]]; then
    pass "F009: $f: the bash block is EXACTLY the permissive catch-all allow"
  else
    fail "F009: $f: unexpected bash rules (owner decision 2026-09-29 wants exactly the catch-all allow) — got: $b"
  fi
done

# Path barriers are RETAINED (they are the systematic guard now) — verified
# SEMANTICALLY (004-001 T7a, PD-10/D7): the generated permission frontmatter
# is evaluated with findLast semantics by the shared checker
# tests/pd10_permission_semantics.py (reuses the evaluator from
# tests/test_opencode_read_map_and_steps.py). The old text-presence asserts
# here retired in the same commit as their passing replacements:
#   - readers edit deny            -> F009-readers-edit-deny
#   - tw '"tests/**": allow'       -> F009-tw-edit-tests-allow
#   - tw '"src/**": deny'          -> F009-tw-read-src-deny
#   - tw-odoo models deny          -> F009-tw-odoo-read-models-deny
#   - imp '"*": allow' (edit)      -> F009-imp-edit-catchall-allow
#   - imp '"tests/**": deny'       -> F009-imp-edit-tests-deny
#   - imp does-not-deny models     -> F009-imp-no-models-deny
#   - CC matcher Read|Grep|Glob    -> F009-cc-tw-read-guard
#   - CC matcher Edit|Write        -> F009-cc-imp-edit-guard
# Each mutation on a copy of the generated output that weakens a barrier is
# proven to fail its replacement (tests/test_004_001_t7_pd10.py, M1-M10).
echo "-- PD-10 semantic permission checks (F009 replacements) --"
PD10_OUT="$(python3 tests/pd10_permission_semantics.py --set consistency 2>&1)"
PD10_RC=$?
if [[ $PD10_RC -eq 0 ]]; then
  while IFS= read -r line; do
    [[ "$line" == PASS:* ]] && pass "${line#PASS: }"
  done <<< "$PD10_OUT"
  pass "PD-10: F009 semantic permission-map replacements all green (tests/pd10_permission_semantics.py --set consistency)"
else
  while IFS= read -r line; do
    [[ "$line" == FAIL:* ]] && fail "${line#FAIL: }"
  done <<< "$PD10_OUT"
  fail "PD-10: F009 semantic checker exited non-zero ($PD10_RC)"
fi

# Claude Code: NO Bash matcher anywhere (owner decision 2026-09-29 — the
# Bash content-guard hooks are retired); the path guards remain.
for f in agents/claude-code/cdad-*.md; do
  assert_string_not_has "$(cat "$f")" 'matcher:[[:space:]]*"?[A-Za-z|]*\bBash' \
    "F009: $f: no PreToolUse Bash matcher (permissive bash, owner decision 2026-09-29)"
done
# (the 'keeps the Read|Grep|Glob path guard' / 'keeps the Edit|Write path guard'
# text asserts retired -> replaced semantically above by
# F009-cc-tw-read-guard / F009-cc-imp-edit-guard)

# path-guard.sh: the Bash content-guard is retired; the fail-open
# documentation for external absolute paths stays.
assert_string_not_has "$(cat "$ROOT/scripts/claude-code-path-guard.sh")" 'BASH_CONTENT' \
  "F009: path-guard.sh no longer implements a Bash content-guard (owner decision 2026-09-29)"
assert_file_has "scripts/claude-code-path-guard.sh" 'outside.*PWD|outside the project' \
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
# 006-002 U3 (PD-9): the CC runtime delegation reference is withdrawn from the
# installable skill tree; the M6 concern is conserved on the INSTALLABLE tree
# (no installable skill text may carry the invented API or the misattributed
# citation) plus the withdrawal assert itself (reformulated, not deleted).
assert_file_missing "skills/cdad-cycle/references/claude-code-delegation.md" \
  "F010 (M6) + 006-002 PD-9: the Claude Code runtime delegation reference is withdrawn from the installable skill tree"
assert_tree_not_has "skills" 'from Agent import agent' \
  "F010 (M6): no installable skill text carries the invented Python API ('from Agent import agent')"
assert_tree_not_has "skills" '\(AP-7' \
  "F010 (M6): no installable skill text cites AP-7 for the isolation invariant (it is AP-1/AP-2)"

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
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'my arXiv pipeline' \
  "F010 (M8): verdict-tuple.md without a reference to 'my arXiv pipeline'"
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'fb-012' \
  "F010 (M8): verdict-tuple.md without a reference to 'fb-012'"
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'Approved by Pablo' \
  "F010 (M8): verdict-tuple.md without the owner's proper name"

echo
echo "############################################"
echo "# F001 — honest profiles note + §2 block drift (B7)"
echo "#   Reformulated by 006-002 PD-11 (U4): §2 of SKILL.md no longer fixes"
echo "#   models (no \"Model family\" column, no profiles paragraph)."
echo "#   RE-REFORMULATED by 006-003 PD-7b (U3, D7): the profiles vocabulary"
echo "#   itself is retired — §2 and the generated orchestrators must NOT"
echo "#   speak of profiles nor mention --basic."
echo "#   RE-REFORMULATED AGAIN by the owner's amendment A-5 (006-003 §9,"
echo "#   2026-10-18): the reviewer/implementer FAMILY requirement is RETIRED —"
echo "#   no installable text requires choosing, controlling, verifying or"
echo "#   declaring the reviewer's family/model relative to the implementer, and"
echo "#   the 'invariant not guaranteed' declaration tied to the family goes with"
echo "#   it (INV-5 replaced). The former presence asserts are INVERTED here, and"
echo "#   the I8 registration fields / 'model only from the configuration' rules"
echo "#   stay. Reformulated, never deleted (plan amendment A-1 + A-5)."
echo "############################################"

# 006-002 PD-11 (U4) + 006-003 PD-7b (U3) + 006-003 A-5: §2 of SKILL.md loses
# the "Model family" column, the profiles paragraph and every profile- or
# family-conditioned claim. What stands: the model of each role is the one
# CONFIGURED IN THE RUNTIME and the skill NAMES NO MODELS. What is GONE: the
# reviewer's family as a configuration verification / 'not verifiable' /
# 'declared' (A-5 replaced INV-5).
extract_skill_section2() {
  # Delimitation mirrors the focal oracle
  # (tests/test_006_002_u4_skill_without_models.py -> numbered_section_region):
  # the numbered heading starts the section whatever its level, and the section
  # ends at the next heading of the SAME or higher level; sub-headings (2.x)
  # stay inside. Awk cannot look ahead, so the "2." separator is required to be
  # followed by a non-digit to reject sub-numbers like "### 2.1".
  awk '
    function level(line,   n) { n = 0; while (substr(line, n + 1, 1) == "#") n++; return n }
    /^#+[ \t]/ {
      if (started) { if (level($0) <= target) exit; print; next }
      if ($0 ~ /^#+[ \t]*2([.)[:space:]:][^0-9]|$)/) {
        started = 1; target = level($0); print
      }
      next
    }
    started { print }
  ' "$ROOT/skills/cdad-cycle/SKILL.md"
}
SKILL_S2="$(extract_skill_section2)"
if [[ -z "$SKILL_S2" ]]; then
  fail "F001 (006-002 PD-11): SKILL.md §2 could not be extracted by its numbered heading"
else
  if printf '%s' "$SKILL_S2" | grep -Eq 'configured in the runtime|configured in the environment|configured by the runtime|runtime configuration|configuration of the runtime|configurado en el runtime|configurado en el entorno|configuraci[oó]n del runtime'; then
    pass "F001 (006-002 PD-11): SKILL.md §2 declares the model of each role is the configured one"
  else
    fail "F001 (006-002 PD-11): SKILL.md §2 lacks the 'model of each role = the one configured in the runtime' sentence"
  fi
  if printf '%s' "$SKILL_S2" | grep -Eq 'names no model|does not name any model|does not name a model|name no model|no model is named|no model names|no nombra|sin nombrar|no se nombra'; then
    pass "F001 (006-002 PD-11): SKILL.md §2 declares the skill names no models"
  else
    fail "F001 (006-002 PD-11): SKILL.md §2 lacks the 'the skill names no models' declaration"
  fi
  # 006-003 PD-7b (U3) — ORACLE REPLACEMENT of the profiles-note assert: §2 must
  # be free of the profile vocabulary and of the retired --basic flag (the model
  # lives in the delegation configuration, PD-3; the profile is gone, PD-1).
  if printf '%s' "$SKILL_S2" | grep -Eqi 'perfil|profile|\-\-basic'; then
    fail "F001 (006-003 PD-7b): SKILL.md §2 still speaks of profiles / --basic (the model is chosen in the delegation configuration)"
  else
    pass "F001 (006-003 PD-7b): SKILL.md §2 is free of profile vocabulary and of --basic"
  fi
  # 006-003 A-5 (§9) — INVERTED (not deleted) version of the former family
  # presence asserts: §2 must NOT state the reviewer/implementer family
  # requirement, the 'configuration verification' form, the 'not verifiable'
  # case nor the 'invariant not guaranteed' declaration tied to the family.
  if printf '%s' "$SKILL_S2" | grep -Eqi 'model famil|family of the reviewer|reviewer .{0,40}famil|familia del (reviewer|revisor)|familia de(l)? (implementer|implementador)'; then
    fail "F001 (006-003 A-5): SKILL.md §2 still speaks of the reviewer's model family (the family requirement is retired)"
  else
    pass "F001 (006-003 A-5): SKILL.md §2 is free of the reviewer-family wording"
  fi
  if printf '%s' "$SKILL_S2" | grep -Eqi 'configuration check|check of the configuration|configuration verification|verification of the configuration|compar[ea]s? the (configured|effective) models|verificaci[oó]n de (la )?configuraci[oó]n|se verifica en la configuraci[oó]n'; then
    fail "F001 (006-003 A-5): SKILL.md §2 still declares the family as a configuration verification (retired by A-5)"
  else
    pass "F001 (006-003 A-5): SKILL.md §2 has no 'family = configuration verification' declaration"
  fi
  if printf '%s' "$SKILL_S2" | grep -Eqi 'invariant not guaranteed|invariante no garantizado'; then
    fail "F001 (006-003 A-5): SKILL.md §2 still declares the family invariant as not guaranteed (retired by A-5)"
  else
    pass "F001 (006-003 A-5): SKILL.md §2 has no 'invariant not guaranteed' family declaration"
  fi
fi
# 006-003 A-5 (§9) — INVERTED (not deleted) version of the former F001 loop:
# the generated orchestrators must carry no profile wording (PD-1/PD-7) and no
# reviewer-family requirement (A-5: the family is not chosen, controlled,
# verified nor declared by the orchestrator).
for f in agents/cdad-orchestrator.md agents/claude-code/cdad-orchestrator.md; do
  assert_file_not_has "$f" '\-\-basic' \
    "F001 (006-003 PD-7b): $f no longer mentions the retired --basic profile"
  assert_file_not_has "$f" '[Pp]erfil|[Pp]rofile' \
    "F001 (006-003 PD-7b): $f no longer speaks of profiles"
  assert_file_not_has "$f" 'model famil|family of the reviewer|reviewer .{0,40}famil|familia del (reviewer|revisor)|familia de(l)? (implementer|implementador)' \
    "F001 (006-003 A-5): $f no longer requires the reviewer's model family"
  assert_file_not_has "$f" 'configuration check|check of the configuration|configuration verification|verification of the configuration|compar[ea]s? the (configured|effective) models|verificaci[oó]n de (la )?configuraci[oó]n' \
    "F001 (006-003 A-5): $f has no 'family = configuration verification' declaration"
  assert_file_not_has "$f" 'invariant not guaranteed|invariante no garantizado' \
    "F001 (006-003 A-5): $f has no 'invariant not guaranteed' family declaration"
done

# 004-001 T3 / D7 / PD-14: byte-equality of the §2 block is NO LONGER a
# requirement (the generator composes the orchestrator's §2 as a COMPOSED
# artifact per runtime), so the old 3-copy byte-identity assert is REPLACED
# by per-runtime semantic coherence asserts below.
extract_role_contract() {
  awk '/^### 2\. Contract of each role/{f=1} f{print; if ($0 ~ /^Models of the design|^Design models/) exit}' "$ROOT/$1"
}
# F001 §2 semantic coherence (004-001 T3; D7 + PD-14 — replaces byte-identity):
# (i) no model outside the runtime's own map; (ii) §2 marked as composed.
CC_RC="$(extract_role_contract "agents/claude-code/cdad-orchestrator.md")"
OC_RC="$(extract_role_contract "agents/cdad-orchestrator.md")"
if [[ -z "$CC_RC" ]]; then
  fail "F001: CC orchestrator §2 could not be extracted (agents/claude-code/cdad-orchestrator.md)"
fi
if [[ -z "$OC_RC" ]]; then
  fail "F001: OC orchestrator §2 could not be extracted (agents/cdad-orchestrator.md)"
fi
if printf '%s' "$CC_RC" | grep -Eq 'deepseek-v4-(pro|flash)|glm-5\.2|qwen3\.7-(plus|max)|minimax-m3'; then
  fail "F001: CC orchestrator §2 mentions OpenCode design models that cdad_model_claude does not produce (PD-14/D7)"
else
  pass "F001: CC orchestrator §2 free of OpenCode design models (PD-14/D7)"
fi
# 006-003 U1 (PD-1c/PD-7a/INV-3) — ORACLE REPLACEMENT of the three per-runtime
# model-value asserts above (PD-14/D7): they required each §2 to CARRY the model
# values of its own runtime map. The map is retired (PD-1c) and no installable
# text fixes or names a model (INV-3), so the asserts are INVERTED here instead
# of deleted: §2 of BOTH orchestrators must be free of every model name.
MODEL_NAME_RE='deepseek|glm-|qwen|minimax|sonnet|haiku|opus|fable|mofgw/'
for s2_entry in "agents/claude-code/cdad-orchestrator.md|$CC_RC" "agents/cdad-orchestrator.md|$OC_RC"; do
  section_file="${s2_entry%%|*}"
  section_block="${s2_entry#*|}"
  if printf '%s' "$section_block" | grep -Eq "$MODEL_NAME_RE|(^|[|])[[:space:]]*model:"; then
    fail "F001: $section_file §2 names a model (006-003 PD-7a/INV-3: no installable text fixes or names a model)"
  else
    pass "F001: $section_file §2 free of model names (006-003 PD-7a/INV-3, replaces PD-14 model cells)"
  fi
done
unset s2_entry section_file section_block
if printf '%s' "$OC_RC" | grep -Eq 'Roles-contract §2 table — composed|composed from all'; then
  pass "F001: OC orchestrator §2 is marked as composed (PD-4/D7)"
else
  fail "F001: OC orchestrator §2 lacks the composed marker — §2 is a composed artifact of the generator (PD-4/D7)"
fi
if printf '%s' "$CC_RC" | grep -Eq 'Roles-contract §2 table — composed|composed from all'; then
  pass "F001: CC orchestrator §2 is marked as composed (PD-4/D7)"
else
  fail "F001: CC orchestrator §2 lacks the composed marker — §2 is a composed artifact of the generator (PD-4/D7)"
fi

echo
echo "############################################"
echo "# F003 — SKILL.md ↔ stage-N gates synchronized + B11"
echo "############################################"

# Gate 2→3: SKILL.md includes the plan.md item that previously only stage-2 had.
assert_file_has "skills/cdad-cycle/SKILL.md" 'plan\.md.*exists.*self-review|If the spec is complex' \
  "F003: SKILL.md's Gate 2→3 includes the plan.md item (previously only in stage-2)"

# Gate 3→4: stage-3-tdd.md includes the 2 items previously only in SKILL.md.
assert_file_has "skills/cdad-cycle/references/stage-3-tdd.md" 'Test Audit completed and approved' \
  "F003: Gate 3→4 of stage-3-tdd.md includes 'Test Audit completed and approved' (previously only in SKILL.md)"
assert_file_has "skills/cdad-cycle/references/stage-3-tdd.md" 'explicit justification in spec\.md' \
  "F003: Gate 3→4 of stage-3-tdd.md includes 'explicit justification in spec.md' (previously only in SKILL.md)"

# Gate 5→done: CI carve-out in stage-5-merge.md + "Feature merged" in SKILL.md.
assert_file_has "skills/cdad-cycle/references/stage-5-merge.md" 'If NO CI is configured' \
  "F003: Gate 5→done of stage-5-merge.md includes the CI carve-out (previously only in SKILL.md)"
assert_file_has "skills/cdad-cycle/SKILL.md" 'Feature merged' \
  "F003: Gate 5→done of SKILL.md includes 'Feature merged' (previously only in stage-5-merge.md)"

# B11: the 4→5 gate no longer contradicts the explicit-delegation exception that
# the file itself documents (Layer 2 / §2.3).
for f in skills/cdad-cycle/SKILL.md skills/cdad-cycle/references/stage-4-review.md; do
  assert_file_not_has "$f" '\[ \] User approved prioritization \(not delegated to the LLM\)\.' \
    "F003 (B11): $f no longer has the absolute wording of the 4→5 gate"
  assert_file_has "$f" 'agent-delegated with an explicit request' \
    "F003 (B11): $f mentions the explicit-delegation exception in the gate"
done
assert_file_not_has "skills/cdad-cycle/references/stage-2-specification.md" \
  '\*\*AP-10\*\*: delegating approval to the LLM\. Non-delegable\.' \
  "F003 (B11): the short AP-10 in stage-2 is no longer absolute without the exception"

echo
echo "############################################"
echo "# F007 — Claude Code orchestrator repaired (B6)"
echo "############################################"

CCO="agents/claude-code/cdad-orchestrator.md"
assert_file_has "$CCO" '`Agent` tool' \
  "F007: $CCO instructs delegating via a tool (not task/delegate)"
assert_file_has "$CCO" 'Agent.{0,10}subagent_type' \
  "F007: $CCO mentions the Agent tool with subagent_type"
assert_file_not_has "$CCO" 'via `delegate`; roles write-capable' \
  "F007: $CCO no longer instructs 'delegate' as the per-role invocation mechanism"
assert_file_has "$CCO" 'resolve the stack' \
  "F007: $CCO resolves the stack suffix before delegating (parity with OpenCode)"
assert_file_has "$CCO" 'cdad-<role>-<stack>' \
  "F007: $CCO mentions the cdad-<role>-<stack> pattern for specialized variants"

echo
echo "############################################"
echo "# F008 — no model map and no model in the agents"
echo "############################################"

# 006-003 U1 (PD-1c/PD-1e/INV-3) — ORACLE REPLACEMENT of the former F008 block.
# F008 used to `source scripts/cdad-models.sh` and assert that
# `cdad_model_claude <profile> reviewer` differed from `<profile> implementer`
# for every profile (anti-bias map check, B2). The model map is RETIRED (PD-1c)
# and no installable text fixes a model (PD-1e/INV-3), so there is no profile
# matrix left to compare. The block is replaced — not deleted — by the three
# absence asserts that carry the same anti-bias intent at the tree level: no
# map, no `model:` in any agent, no remaining map consumer in the product.

assert_file_missing "scripts/cdad-models.sh" \
  "F008 (006-003 PD-1c): the model map is retired (was scripts/cdad-models.sh)"

if grep -Eq '^model:' agents/cdad-*.md agents/claude-code/*.md 2>/dev/null; then
  fail "F008 (006-003 PD-1e/INV-3): some agent artifact still fixes a model (grep -E '^model:' agents/)"
else
  pass "F008 (006-003 PD-1e/INV-3): no agent artifact fixes a model"
fi

if grep -rEq 'cdad_model(_claude)?[[:space:]]' install.sh scripts/ 2>/dev/null; then
  fail "F008 (006-003 PD-1c): install.sh/scripts/ still consume the retired model map"
else
  pass "F008 (006-003 PD-1c): install.sh/scripts/ consume no model map"
fi

echo
echo "############################################"
echo "# F005 — reviewer taxonomy unified (B4)"
echo "############################################"

CCR="agents/claude-code/cdad-reviewer.md"
assert_file_not_has "$CCR" '\*\*CRITICAL\*\*|\*\*MAJOR\*\*|\*\*MINOR\*\*|\*\*TRIVIAL\*\*' \
  "F005: $CCR no longer uses the CRITICAL/MAJOR/MINOR/TRIVIAL taxonomy"
assert_file_has "$CCR" 'Critical:.*Blocks merge' \
  "F005: $CCR uses the addyosmani taxonomy (Critical/Required/Nit/Optional/FYI)"
assert_file_has "$CCR" 'Axis 4: Security' \
  "F005: $CCR includes the Security axis (previously absent — the only one of the 4 reviewers without it)"

# The 4 reviewers now share the same severity taxonomy.
for f in agents/cdad-reviewer.md agents/cdad-reviewer-odoo.md agents/claude-code/cdad-reviewer-odoo.md; do
  assert_file_has "$f" 'Critical:.*Blocks merge' \
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
  assert_file_not_has "$f" 'Exhaustive coverage, property tests, load' \
    "F006: $f no longer groups property tests inside the cycle's exclusion phrase"
  assert_file_has "$f" 'Property tests are NOT the same question|Property tests derived from invariants' \
    "F006: $f clarifies that property tests derived from the spec's invariants do belong to the cycle"
  assert_file_has "$f" 'RED verifies the requirement, it does not maximize coverage' \
    "F006: $f declares the RED-verifies-the-requirement rule"
done

# The rule also reaches the system prompt of the 4 test-writers (not just the
# reference, which may not get loaded).
for f in agents/cdad-test-writer.md agents/claude-code/cdad-test-writer.md \
         agents/cdad-test-writer-odoo.md agents/claude-code/cdad-test-writer-odoo.md; do
  assert_file_has "$f" 'verifies the requirement, it does not maximize coverage' \
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
assert_file_has "docs/epics/epic-001-superpowers-gaps/closure.md" 'Cerrado|Closed' \
  "F012 (M9): closure.md has a closure date"
assert_file_has "skills/cdad-epic/SKILL.md" 'Why there is no .cdad-epic-.* sub-agent' \
  "F012 (M10): documented decision about the absence of a cdad-epic-* sub-agent"

echo
echo "############################################"
echo "# 005-004 T1 — Claude Code declares the real dispatch tool (PD-1/AC-1)"
echo "############################################"

# PD-1(ii)/AC-1: NO Claude Code agent declares `Task` as its dispatch tool —
# the tool observed in real runs is `Agent` with `subagent_type: cdad-<role>`.
# The declaration lives once in the generator and the derived agents carry it;
# the orchestrator's `tools:` line is the one not frozen by
# tests/test_packet_prepare.py (which pins the other ten agents).
assert_cc_no_task_dispatch_tool() {
  local f="$1" line
  line="$(frontmatter "$ROOT/$f" 2>/dev/null | grep -E '^tools:' | head -n1)"
  if printf '%s\n' "$line" | grep -Eq '[[:space:],:]Task\b'; then
    fail "005-004 PD-1: $f declares 'Task' as a dispatch tool (the real one is 'Agent')"
  else
    pass "005-004 PD-1: $f does not declare 'Task' as a dispatch tool"
  fi
}
for f in agents/claude-code/cdad-*.md; do
  assert_cc_no_task_dispatch_tool "$f"
done

# PD-1(i)/AC-1: the orchestrator derived for Claude Code declares `Agent`.
assert_file_has "agents/claude-code/cdad-orchestrator.md" '^tools:.*\bAgent\b' \
  "005-004 PD-1: the CC orchestrator declares the real dispatch tool 'Agent'"

# Control de no-regresión (PD-1/AC-1), repuntado por 006-002 U3 (PD-9): el lado
# OpenCode CONSERVA su nombre de herramienta — y lo declara en su CAPA DE AGENTE
# (el adaptador fuente y el orquestador generado, dueños del mecanismo según
# D-1), no en la referencia por runtime que sale del árbol instalable.
assert_file_missing "skills/cdad-cycle/references/opencode-delegation.md" \
  "006-002 PD-9: the OpenCode runtime delegation reference is withdrawn from the installable skill tree"
assert_file_has "sources/agents/adapters/opencode.md" '`task`' \
  "005-004 PD-1 (control): the OpenCode agent layer (source adapter) keeps its own dispatch tool name"
assert_file_has "agents/cdad-orchestrator.md" '`task`' \
  "005-004 PD-1 (control): the generated OpenCode orchestrator declares its own dispatch tool name"

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
