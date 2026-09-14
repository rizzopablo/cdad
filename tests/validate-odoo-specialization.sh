#!/usr/bin/env bash
# =============================================================================
# validate-odoo-specialization.sh
#
# Validation oracle of the feature cdad-003 "Odoo specialization of CDAD".
# Verifies the postconditions P1..P6 of the approved spec
# (docs/specs/cdad-003-odoo/spec.md) as shell asserts (pure bash, no
# external dependencies: grep/sed/awk/test).
#
# Usage:
#   tests/validate-odoo-specialization.sh
#
# Output:
#   - explicit asserts with a clear message (PASS/FAIL)
#   - failure counter at the end
#   - exit 0 if everything passes ("PASS"); exit 1 if anything fails ("FAIL")
# =============================================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PASS_COUNT=0
FAIL_COUNT=0

# --- helpers ----------------------------------------------------------------
pass() { PASS_COUNT=$((PASS_COUNT + 1)); printf 'PASS: %s\n' "$*"; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf 'FAIL: %s\n' "$*"; }

assert_file() {
    # assert_file <relative-path> <message>
    if [[ -f "$ROOT/$1" ]]; then
        pass "$2 ($1 exists)"
    else
        fail "$2 ($1 does NOT exist)"
    fi
}

assert_file_has() {
    # assert_file_has <relative-path> <grep-pattern> <message>
    # NOTE: we use -e so patterns starting with dashes (--test-enable)
    # are not interpreted as grep options.
    if [[ -f "$ROOT/$1" ]] && grep -Eq -e "$2" "$ROOT/$1"; then
        pass "$3 ($1 contains '$2')"
    else
        fail "$3 ($1 does NOT contain '$2')"
    fi
}

assert_file_not_has() {
    # assert_file_not_has <relative-path> <grep-pattern> <message>
    if [[ -f "$ROOT/$1" ]] && ! grep -Eq -e "$2" "$ROOT/$1"; then
        pass "$3 ($1 does NOT contain '$2')"
    else
        fail "$3 ($1 DOES contain '$2', not allowed)"
    fi
}

frontmatter() {
    # frontmatter <file> — prints the ---...--- block (without the delimiters)
    awk 'BEGIN{c=0} /^---/{c++; next} c==1 {print}' "$1"
}
bash_section() {
    # bash_section <file> — prints ONLY the frontmatter 'bash:' section
    # (where the permission config lives). The section starts at the 'bash:' line.
    # Isolating it avoids false positives from legitimate mentions in the
    # body's prose ("python", "sed/awk", "code of").
    frontmatter "$1" | awk '/^[[:space:]]*bash:[[:space:]]*$/ {on=1; print; next} on'
}

assert_string_not_has() {
    # assert_string_not_has <content> <grep-pattern> <message>
    # Checks against a VARIABLE (in-memory content), not a path.
    if [[ -n "$1" ]] && ! printf '%s' "$1" | grep -Eq -e "$2"; then
        pass "$3 (does not contain '$2')"
    else
        fail "$3 (contains '$2', not allowed)"
    fi
}

echo "############################################"
echo "# P1 — Agent variants"
echo "############################################"

VARIANT_AGENTS=(architect test-writer implementer reviewer scribe)

# P1.1 — The 5 Odoo variant agent files exist + frontmatter + mode: subagent
for role in "${VARIANT_AGENTS[@]}"; do
    f="agents/cdad-$role-odoo.md"
    assert_file "$f" "P1: variant agent $role-odoo exists"
    assert_true_placeholder=1

    assert_file_has "$f" '^---' "P1 ($role-odoo): frontmatter delimiter (---)"
    assert_file_has "$f" '^mode:[[:space:]]*subagent' "P1 ($role-odoo): frontmatter declares mode: subagent"
done

# P1.test-writer — scopes **/models/**, **/views/**, **/controllers/**, **/wizards/**;
# allows **/tests/** and __manifest__.py
TW="agents/cdad-test-writer-odoo.md"
assert_file_has "$TW" 'models'      "P1 tw: scopes **/models/**"
assert_file_has "$TW" 'views'       "P1 tw: scopes **/views/**"
assert_file_has "$TW" 'controllers' "P1 tw: scopes **/controllers/**"
assert_file_has "$TW" 'wizards'     "P1 tw: scopes **/wizards/**"
assert_file_has "$TW" 'tests'       "P1 tw: allows **/tests/**"
assert_file_has "$TW" '__manifest__' "P1 tw: allows reading __manifest__.py"

# P1.implementer — denies editing/writing **/tests/**
assert_file_has "agents/cdad-implementer-odoo.md" 'tests' "P1 imp: scopes **/tests/**"

# P1.reviewer — model different from the implementer's
IMP_MODEL=""
REV_MODEL=""
if [[ -f "$ROOT/agents/cdad-implementer-odoo.md" ]]; then
    IMP_MODEL="$(frontmatter "$ROOT/agents/cdad-implementer-odoo.md" | sed -n -E 's/^model:[[:space:]]*["'"'"']*([^"'"'"'[:space:]]+).*/\1/p' | head -1)"
fi
if [[ -f "$ROOT/agents/cdad-reviewer-odoo.md" ]]; then
    REV_MODEL="$(frontmatter "$ROOT/agents/cdad-reviewer-odoo.md" | sed -n -E 's/^model:[[:space:]]*["'"'"']*([^"'"'"'[:space:]]+).*/\1/p' | head -1)"
fi
if [[ -n "$IMP_MODEL" && -n "$REV_MODEL" && "$IMP_MODEL" != "$REV_MODEL" ]]; then
    pass "P1 rev: the reviewer's model ($REV_MODEL) differs from the implementer's ($IMP_MODEL)"
else
    fail "P1 rev: the reviewer's model differs from the implementer's (imp='$IMP_MODEL' rev='$REV_MODEL')"
fi

# P1 — bash allowlist for the 5 variants (review criterion, no longer reviewer-only):
# ONLY allowlist commands; NEVER an unrestricted wildcard ("*": allow) or
# Odoo/environment-specific commands.
#
# Amendment 2026-09-02 (epic-002-cdad-audit-fixes, 002-009, findings B1/M4):
# the original postcondition of this section required unscoped 'git *' for
# the 5 variants. A later audit detected that this was the real leak: a
# read-only role (architect/reviewer/scribe) with 'git *' can commit/
# push/reset (AP-17), and a write-capable role (test-writer/implementer)
# with 'git *' + 'cat *'/'head *'/'tail *'/'rg *' can read/write content
# outside its scope via bash, sidestepping the declarative permission.read/edit.
# The current postcondition: git SCOPED to non-mutating subcommands for the
# read-only roles (diff/log/show/blame/status); test-writer/implementer
# additionally get commit/add (SKILL contract §5: "they write and commit their
# own artifact") but lose cat/head/tail/rg (already covered by Read/Grep,
# correctly scoped). See findings/audit-consistencia-2026-09-02.md.
FORBIDDEN_BASH_ALL=('odoo-bin' 'psql' 'createdb' 'dropdb' 'go ' 'python' 'curl' 'wget' '"git \*"' '"git\*"')
FORBIDDEN_BASH_CONTENT=('"cat \*"' '"head \*"' '"tail \*"' '"rg \*"' 'sed' 'awk')
for role in "${VARIANT_AGENTS[@]}"; do
    af="agents/cdad-$role-odoo.md"
    assert_file_has "$af" 'pylint[[:space:]]*\*' "P1 ($role): allowlist includes 'pylint *'"
    BASH_RULES="$(bash_section "$ROOT/$af" | grep -v '^[[:space:]]*#')"
    if [[ -n "$BASH_RULES" ]]; then
        if printf '%s' "$BASH_RULES" | grep -Eq '^[[:space:]]*"\*"[[:space:]]*:[[:space:]]*allow'; then
            fail "P1 ($role): the bash section CONTAINS an unrestricted wildcard (\"*\": allow)"
        else
            pass "P1 ($role): the bash section has NO unrestricted wildcard (\"*\": allow)"
        fi
        if printf '%s' "$BASH_RULES" | grep -Eq -e '"git diff\*?":[[:space:]]*allow'; then
            pass "P1 ($role): allowlist includes git diff (non-mutating inspection)"
        else
            fail "P1 ($role): allowlist does NOT include git diff"
        fi
        for forb in "${FORBIDDEN_BASH_ALL[@]}"; do
            assert_string_not_has "$BASH_RULES" "$forb" "P1 ($role): allowlist does NOT include '$forb'"
        done
        case "$role" in
            test-writer|implementer)
                # write-capable: they commit their own artifact, but without
                # content-reading commands (already covered by Read/Grep).
                if printf '%s' "$BASH_RULES" | grep -Eq -e '"git (commit|add \*)\*?":[[:space:]]*allow'; then
                    pass "P1 ($role): allowlist includes git commit/add (contract §5)"
                else
                    fail "P1 ($role): allowlist does NOT include git commit/add"
                fi
                for forb in "${FORBIDDEN_BASH_CONTENT[@]}"; do
                    assert_string_not_has "$BASH_RULES" "$forb" "P1 ($role): allowlist does NOT include '$forb' (content reading — use Read/Grep)"
                done
                ;;
            *)
                # read-only: cat/head/tail/rg remain allowed (they are full-read
                # by design, with no scoped area to sidestep).
                assert_string_not_has "$BASH_RULES" 'sed' "P1 ($role): allowlist does NOT include 'sed'"
                assert_string_not_has "$BASH_RULES" 'awk' "P1 ($role): allowlist does NOT include 'awk'"
                ;;
        esac
    else
        fail "P1 ($role): no 'bash:' section detected in the frontmatter"
    fi
done

echo "############################################"
echo "# P2 — Skills per role"
echo "############################################"

assert_file "skills/odoo-architect/SKILL.md"   "P2: skill odoo-architect exists"
assert_file "skills/odoo-test-writer/SKILL.md" "P2: skill odoo-test-writer exists"
assert_file "skills/odoo-reviewer/SKILL.md"    "P2: skill odoo-reviewer exists"

# odoo-architect: GAP→Kick-Off→Implementation→Go-Live phase model and PL/SPoC roles
assert_file_has "skills/odoo-architect/SKILL.md" 'GAP|Gap'        "P2 arch: mentions the GAP/Gap phase"
assert_file_has "skills/odoo-architect/SKILL.md" 'Kick-Off'       "P2 arch: mentions the Kick-Off phase"
assert_file_has "skills/odoo-architect/SKILL.md" 'Implementation' "P2 arch: mentions the Implementation phase"
assert_file_has "skills/odoo-architect/SKILL.md" 'Go-Live'        "P2 arch: mentions the Go-Live phase"
assert_file_has "skills/odoo-architect/SKILL.md" 'PL'             "P2 arch: mentions the PL role"
assert_file_has "skills/odoo-architect/SKILL.md" 'SPoC|SPOC'      "P2 arch: mentions the SPoC/SPOC role"

# odoo-test-writer: TransactionCase, tagged, Form (each as a real word)
assert_file_has "skills/odoo-test-writer/SKILL.md" '\bTransactionCase\b' "P2 tw: mentions TransactionCase"
assert_file_has "skills/odoo-test-writer/SKILL.md" '\btagged\b'         "P2 tw: mentions tagged"
assert_file_has "skills/odoo-test-writer/SKILL.md" '\bForm\b'           "P2 tw: mentions Form"

# odoo-reviewer: pylint-odoo and mandatory/advisory split
assert_file_has "skills/odoo-reviewer/SKILL.md" 'pylint-odoo' "P2 rev: mentions pylint-odoo"
assert_file_has "skills/odoo-reviewer/SKILL.md" 'mandatory'   "P2 rev: mentions the mandatory split"
assert_file_has "skills/odoo-reviewer/SKILL.md" 'advisory'    "P2 rev: mentions the advisory split"

# the implementer variant references the current skill odoo-expert (odoo-dev-methodology retired in d9dc599)
assert_file_not_has "agents/cdad-implementer-odoo.md" 'odoo-dev-methodology' "P2 imp: does NOT reference the retired skill odoo-dev-methodology"
assert_file_has "agents/cdad-implementer-odoo.md" 'odoo-expert'          "P2 imp: references the odoo-expert skill"

echo "############################################"
echo "# P3 — Make contract"
echo "############################################"

MF="skills/odoo-make-env/assets/Makefile.template"
assert_file "$MF" "P3: Makefile.template exists"
assert_file_has "$MF" '^test:'            "P3: Makefile.template has the 'test:' target"
assert_file_has "$MF" '^test-one:'        "P3: Makefile.template has the 'test-one:' target"
assert_file_has "$MF" '^test-clean:'      "P3: Makefile.template has the 'test-clean:' target"
assert_file_has "$MF" '--test-enable'  "P3: Makefile.template uses --test-enable"
assert_file_has "$MF" '--stop-after-init' "P3: Makefile.template uses --stop-after-init"

CF="skills/odoo-make-env/assets/odoo-test.conf.template"
assert_file "$CF" "P3: odoo-test.conf.template exists"
assert_file_has "$CF" 'workers[[:space:]]*=[[:space:]]*0' "P3: odoo-test.conf.template has workers = 0"
assert_file_has "$CF" 'db_maxconn'                        "P3: odoo-test.conf.template has db_maxconn"

echo "############################################"
echo "# P4 — Activation by stack"
echo "############################################"

# P4 (review criterion): the stack=odoo activation mechanism must be
# documented in the MAIN SKILL.md of skills/cdad-cycle/ (not only references/).
assert_file_has "skills/cdad-cycle/SKILL.md" 'stack' "P4: cdad-cycle's main SKILL.md contains 'stack'"
assert_file_has "skills/cdad-cycle/SKILL.md" 'odoo'  "P4: cdad-cycle's main SKILL.md contains 'odoo'"

echo "############################################"
echo "# P5 — Installation (install.sh)"
echo "############################################"

assert_file "install.sh" "P5: install.sh exists at the root"
assert_file_has "install.sh" 'cdad-.*-odoo' "P5: install.sh handles the odoo variant agents (grep 'cdad-.*-odoo')"

echo "############################################"
echo "# P6 — Empirical lessons incorporated"
echo "############################################"

# P6 (review criterion, stricter): skills/odoo-make-env/ must contain
# LITERALLY the "res.groups.privilege" trap (not just "privilege") and the
# "<list>" marker or "<list " (not just the word "list") — the Odoo 19 traps.
if grep -rEq -R 'res\.groups\.privilege' "$ROOT/skills/odoo-make-env" 2>/dev/null \
   && grep -rEq -R '<list>|<list[[:space:]]' "$ROOT/skills/odoo-make-env" 2>/dev/null; then
    pass "P6: skills/odoo-make-env literally documents 'res.groups.privilege' and '<list>'/<list '"
else
    fail "P6: skills/odoo-make-env does NOT literally document 'res.groups.privilege' and '<list>' (Odoo 19 traps)"
fi

if grep -rEq -R 'drift' "$ROOT/skills/odoo-make-env" 2>/dev/null; then
    pass "P6: skills/odoo-make-env documents schema drift"
else
    fail "P6: skills/odoo-make-env does NOT document schema drift"
fi

echo "############################################"
echo "# A3 — Sanitization (I2/A3 criterion)"
echo "############################################"

# A3 (review criterion, new/critical): no sensitive pattern may appear in
# ALL of the publishable repo (docs/, skills/, drafts/, agents/, tests/, examples/,
# README.md). If any of these patterns appears → FAIL.
# The oracle itself is excluded from the scan (it is the one verifying, not an artifact).
#
# The patterns are NOT hardcoded here (this test is public: hardcoding the
# private names would publish them). Sources, in order:
#   1. env CDAD_SENSITIVE_PATTERNS (ERE regexes separated by |)
#   2. tests/.sensitive-patterns.local (gitignored, one regex per line)
#   3. generic fallback: private IPs (always runs, cumulative with 1/2)
SENS_PATTERN='\b(10|172\.(1[6-9]|2[0-9]|3[01])|192\.168)\.[0-9]+\.[0-9]+\.[0-9]+\b'
if [ -n "${CDAD_SENSITIVE_PATTERNS:-}" ]; then
    SENS_PATTERN="$SENS_PATTERN|${CDAD_SENSITIVE_PATTERNS}"
elif [ -f "$ROOT/tests/.sensitive-patterns.local" ]; then
    LOCAL_PAT="$(grep -v '^[[:space:]]*$' "$ROOT/tests/.sensitive-patterns.local" | tr '\n' '|' | sed 's/|$//')"
    SENS_PATTERN="$SENS_PATTERN|${LOCAL_PAT}"
fi
SENS_DIRS=(docs skills drafts agents tests examples)
SENS_HITS=""
for d in "${SENS_DIRS[@]}"; do
    [[ -d "$ROOT/$d" ]] || continue
    SENS_HITS+="$(grep -rEl --exclude="$(basename "$0")" --exclude=".sensitive-patterns.local" -e "$SENS_PATTERN" "$ROOT/$d" 2>/dev/null)"
done
if [[ -f "$ROOT/README.md" ]] && grep -Eq -e "$SENS_PATTERN" "$ROOT/README.md"; then
    SENS_HITS+=" README.md"
fi
if [[ -n "$SENS_HITS" ]]; then
    fail "A3: sensitive patterns found in the publishable content: $(echo "$SENS_HITS" | tr '\n' ' ')"
else
    pass "A3: no sensitive patterns in the publishable content (docs/skills/drafts/agents/tests/examples/README)"
fi

echo
echo "############################################"
echo "# RESULT"
echo "############################################"
echo "Assert PASS: $PASS_COUNT"
echo "Assert FAIL: $FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
    echo "FAIL: $FAIL_COUNT assert(s) failed — incomplete feature (expected RED state)."
    exit 1
fi

echo "PASS: all postconditions P1..P6 and the A3 criterion verified."
exit 0
