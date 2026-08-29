#!/usr/bin/env bash
# =============================================================================
# validate-odoo-specialization.sh
#
# Oráculo de validación de la feature cdad-003 "Especialización Odoo de CDAD".
# Verifica las postcondiciones P1..P6 del spec aprobado
# (docs/specs/cdad-003-odoo/spec.md) como asserts de shell (bash puro, sin
# dependencias externas: grep/sed/awk/test).
#
# Uso:
#   tests/validate-odoo-specialization.sh
#
# Salida:
#   - asserts explícitos con mensaje claro (PASS/FAIL)
#   - contador de fallos al final
#   - exit 0 si todo pasa ("PASS"); exit 1 si algo falla ("FAIL")
# =============================================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PASS_COUNT=0
FAIL_COUNT=0

# --- helpers ----------------------------------------------------------------
pass() { PASS_COUNT=$((PASS_COUNT + 1)); printf 'PASS: %s\n' "$*"; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf 'FAIL: %s\n' "$*"; }

assert_file() {
    # assert_file <ruta-relativa> <mensaje>
    if [[ -f "$ROOT/$1" ]]; then
        pass "$2 ($1 existe)"
    else
        fail "$2 ($1 NO existe)"
    fi
}

assert_file_has() {
    # assert_file_has <ruta-relativa> <patrón-grep> <mensaje>
    # NOTA: usamos -e para que patrones que empiezan con guiones (--test-enable)
    # no sean interpretados como opciones de grep.
    if [[ -f "$ROOT/$1" ]] && grep -Eq -e "$2" "$ROOT/$1"; then
        pass "$3 ($1 contiene '$2')"
    else
        fail "$3 ($1 NO contiene '$2')"
    fi
}

assert_file_not_has() {
    # assert_file_not_has <ruta-relativa> <patrón-grep> <mensaje>
    if [[ -f "$ROOT/$1" ]] && ! grep -Eq -e "$2" "$ROOT/$1"; then
        pass "$3 ($1 NO contiene '$2')"
    else
        fail "$3 ($1 SÍ contiene '$2', no permitido)"
    fi
}

frontmatter() {
    # frontmatter <archivo> — imprime el bloque ---...--- (sin los delimitadores)
    awk 'BEGIN{c=0} /^---/{c++; next} c==1 {print}' "$1"
}
bash_section() {
    # bash_section <archivo> — imprime SOLO la seccion 'bash:' del frontmatter
    # (donde vive la config de permisos). La seccion arranca en la linea 'bash:'.
    # Aislarla evita falsos positivos por menciones legitimas en la prosa del
    # cuerpo ("python", "sed/awk", "codigo de").
    frontmatter "$1" | awk '/^[[:space:]]*bash:[[:space:]]*$/ {on=1; print; next} on'
}

assert_string_not_has() {
    # assert_string_not_has <contenido> <patrón-grep> <mensaje>
    # Chequea sobre una VARIABLE (contenido en memoria), no sobre un path.
    if [[ -n "$1" ]] && ! printf '%s' "$1" | grep -Eq -e "$2"; then
        pass "$3 (no contiene '$2')"
    else
        fail "$3 (contiene '$2', no permitido)"
    fi
}

echo "############################################"
echo "# P1 — Variantes de agentes"
echo "############################################"

VARIANT_AGENTS=(architect test-writer implementer reviewer scribe)

# P1.1 — Existen los 5 archivos de agente variante Odoo + frontmatter + mode: subagent
for role in "${VARIANT_AGENTS[@]}"; do
    f="agents/cdad-$role-odoo.md"
    assert_file "$f" "P1: existe agente variante $role-odoo"
    assert_true_placeholder=1

    assert_file_has "$f" '^---' "P1 ($role-odoo): delimitador de frontmatter (---)"
    assert_file_has "$f" '^mode:[[:space:]]*subagent' "P1 ($role-odoo): frontmatter declara mode: subagent"
done

# P1.test-writer — acota **/models/**, **/views/**, **/controllers/**, **/wizards/**;
# permite **/tests/** y __manifest__.py
TW="agents/cdad-test-writer-odoo.md"
assert_file_has "$TW" 'models'      "P1 tw: acota **/models/**"
assert_file_has "$TW" 'views'       "P1 tw: acota **/views/**"
assert_file_has "$TW" 'controllers' "P1 tw: acota **/controllers/**"
assert_file_has "$TW" 'wizards'     "P1 tw: acota **/wizards/**"
assert_file_has "$TW" 'tests'       "P1 tw: permite **/tests/**"
assert_file_has "$TW" '__manifest__' "P1 tw: permite leer __manifest__.py"

# P1.implementer — niega edición/escritura de **/tests/**
assert_file_has "agents/cdad-implementer-odoo.md" 'tests' "P1 imp: acota **/tests/**"

# P1.reviewer — modelo distinto al del implementer
IMP_MODEL=""
REV_MODEL=""
if [[ -f "$ROOT/agents/cdad-implementer-odoo.md" ]]; then
    IMP_MODEL="$(frontmatter "$ROOT/agents/cdad-implementer-odoo.md" | sed -n -E 's/^model:[[:space:]]*["'"'"']*([^"'"'"'[:space:]]+).*/\1/p' | head -1)"
fi
if [[ -f "$ROOT/agents/cdad-reviewer-odoo.md" ]]; then
    REV_MODEL="$(frontmatter "$ROOT/agents/cdad-reviewer-odoo.md" | sed -n -E 's/^model:[[:space:]]*["'"'"']*([^"'"'"'[:space:]]+).*/\1/p' | head -1)"
fi
if [[ -n "$IMP_MODEL" && -n "$REV_MODEL" && "$IMP_MODEL" != "$REV_MODEL" ]]; then
    pass "P1 rev: model del reviewer ($REV_MODEL) difiere del implementer ($IMP_MODEL)"
else
    fail "P1 rev: model del reviewer difiere del implementer (imp='$IMP_MODEL' rev='$REV_MODEL')"
fi

# P1 — bash allowlist para las 5 variantes (criterio review, ya no solo reviewer):
# SOLO comandos de la allowlist (make/pre-commit/pylint/git/ls/cat/find/rg/head/tail/wc/pwd);
# NUNCA comodín sin restricción ("*": allow) ni comandos de entorno Odoo/específicos.
FORBIDDEN_BASH=('odoo-bin' 'psql' 'createdb' 'dropdb' 'go ' 'python' 'sed' 'awk' 'curl' 'wget')
for role in "${VARIANT_AGENTS[@]}"; do
    af="agents/cdad-$role-odoo.md"
    assert_file_has "$af" 'pylint[[:space:]]*\*' "P1 ($role): allowlist incluye 'pylint *'"
    assert_file_has "$af" 'git[[:space:]]*\*'    "P1 ($role): allowlist incluye 'git *'"
    BASH_RULES="$(bash_section "$ROOT/$af")"
    if [[ -n "$BASH_RULES" ]]; then
        if printf '%s' "$BASH_RULES" | grep -Eq '^[[:space:]]*"\*"[[:space:]]*:[[:space:]]*allow'; then
            fail "P1 ($role): sección bash CONTIENE comodín sin restricción (\"*\": allow)"
        else
            pass "P1 ($role): sección bash SIN comodín sin restricción (\"*\": allow)"
        fi
        for forb in "${FORBIDDEN_BASH[@]}"; do
            assert_string_not_has "$BASH_RULES" "$forb" "P1 ($role): allowlist NO incluye '$forb'"
        done
    else
        fail "P1 ($role): no se detectó sección 'bash:' en el frontmatter"
    fi
done

echo "############################################"
echo "# P2 — Skills por rol"
echo "############################################"

assert_file "skills/odoo-architect/SKILL.md"   "P2: existe skill odoo-architect"
assert_file "skills/odoo-test-writer/SKILL.md" "P2: existe skill odoo-test-writer"
assert_file "skills/odoo-reviewer/SKILL.md"    "P2: existe skill odoo-reviewer"

# odoo-architect: modelo de fases GAP→Kick-Off→Implementation→Go-Live y roles PL/SPoC
assert_file_has "skills/odoo-architect/SKILL.md" 'GAP|Gap'        "P2 arch: menciona fase GAP/Gap"
assert_file_has "skills/odoo-architect/SKILL.md" 'Kick-Off'       "P2 arch: menciona fase Kick-Off"
assert_file_has "skills/odoo-architect/SKILL.md" 'Implementation' "P2 arch: menciona fase Implementation"
assert_file_has "skills/odoo-architect/SKILL.md" 'Go-Live'        "P2 arch: menciona fase Go-Live"
assert_file_has "skills/odoo-architect/SKILL.md" 'PL'             "P2 arch: menciona rol PL"
assert_file_has "skills/odoo-architect/SKILL.md" 'SPoC|SPOC'      "P2 arch: menciona rol SPoC/SPOC"

# odoo-test-writer: TransactionCase, tagged, Form (cada una como palabra real)
assert_file_has "skills/odoo-test-writer/SKILL.md" '\bTransactionCase\b' "P2 tw: menciona TransactionCase"
assert_file_has "skills/odoo-test-writer/SKILL.md" '\btagged\b'         "P2 tw: menciona tagged"
assert_file_has "skills/odoo-test-writer/SKILL.md" '\bForm\b'           "P2 tw: menciona Form"

# odoo-reviewer: pylint-odoo y split mandatory/advisory
assert_file_has "skills/odoo-reviewer/SKILL.md" 'pylint-odoo' "P2 rev: menciona pylint-odoo"
assert_file_has "skills/odoo-reviewer/SKILL.md" 'mandatory'   "P2 rev: menciona split mandatory"
assert_file_has "skills/odoo-reviewer/SKILL.md" 'advisory'    "P2 rev: menciona split advisory"

# implementer variante referencia carga de skills odoo-dev-methodology y odoo-expert
assert_file_has "agents/cdad-implementer-odoo.md" 'odoo-dev-methodology' "P2 imp: referencia skill odoo-dev-methodology"
assert_file_has "agents/cdad-implementer-odoo.md" 'odoo-expert'          "P2 imp: referencia skill odoo-expert"

echo "############################################"
echo "# P3 — Contrato make"
echo "############################################"

MF="skills/odoo-make-env/assets/Makefile.template"
assert_file "$MF" "P3: existe Makefile.template"
assert_file_has "$MF" '^test:'            "P3: Makefile.template tiene target 'test:'"
assert_file_has "$MF" '^test-one:'        "P3: Makefile.template tiene target 'test-one:'"
assert_file_has "$MF" '^test-clean:'      "P3: Makefile.template tiene target 'test-clean:'"
assert_file_has "$MF" '--test-enable'  "P3: Makefile.template usa --test-enable"
assert_file_has "$MF" '--stop-after-init' "P3: Makefile.template usa --stop-after-init"

CF="skills/odoo-make-env/assets/odoo-test.conf.template"
assert_file "$CF" "P3: existe odoo-test.conf.template"
assert_file_has "$CF" 'workers[[:space:]]*=[[:space:]]*0' "P3: odoo-test.conf.template tiene workers = 0"
assert_file_has "$CF" 'db_maxconn'                        "P3: odoo-test.conf.template tiene db_maxconn"

echo "############################################"
echo "# P4 — Activación por stack"
echo "############################################"

# P4 (criterio review): el mecanismo de activación por stack=odoo debe estar
# documentado en el SKILL.md PRINCIPAL de skills/cdad-cycle/ (no solo references/).
assert_file_has "skills/cdad-cycle/SKILL.md" 'stack' "P4: SKILL.md principal de cdad-cycle contiene 'stack'"
assert_file_has "skills/cdad-cycle/SKILL.md" 'odoo'  "P4: SKILL.md principal de cdad-cycle contiene 'odoo'"

echo "############################################"
echo "# P5 — Instalación (install.sh)"
echo "############################################"

assert_file "install.sh" "P5: existe install.sh en raíz"
assert_file_has "install.sh" 'cdad-.*-odoo' "P5: install.sh maneja los agentes variante odoo (grep 'cdad-.*-odoo')"

echo "############################################"
echo "# P6 — Lecciones empíricas incorporadas"
echo "############################################"

# P6 (criterio review, más estricto): en skills/odoo-make-env/ deben aparecer
# LITERALMENTE la trampa "res.groups.privilege" (no solo "privilege") y el
# marcador "<list>" o "<list " (no solo la palabra "list") — las trampas Odoo 19.
if grep -rEq -R 'res\.groups\.privilege' "$ROOT/skills/odoo-make-env" 2>/dev/null \
   && grep -rEq -R '<list>|<list[[:space:]]' "$ROOT/skills/odoo-make-env" 2>/dev/null; then
    pass "P6: skills/odoo-make-env documenta literalmente 'res.groups.privilege' y '<list>'/<list '"
else
    fail "P6: skills/odoo-make-env NO documenta literalmente 'res.groups.privilege' y '<list>' (trampas Odoo 19)"
fi

if grep -rEq -R 'drift' "$ROOT/skills/odoo-make-env" 2>/dev/null; then
    pass "P6: skills/odoo-make-env documenta drift de schema"
else
    fail "P6: skills/odoo-make-env NO documenta drift de schema"
fi

echo "############################################"
echo "# A3 — Sanitización (criterio I2/A3)"
echo "############################################"

# A3 (criterio review, nuevo/crítico): ningún patrón sensible puede aparecer en
# TODO el repo publicable (docs/, skills/, drafts/, agents/, tests/, examples/,
# README.md). Si aparece cualquiera de estos patrones → FAIL.
# El propio oráculo se excluye del escaneo (es quien verifica, no un artefacto).
SENS_PATTERN='OPO|\.opo|saas\.ar|opodev|oc05396|rizzopablodrgit'
SENS_DIRS=(docs skills drafts agents tests examples)
SENS_HITS=""
for d in "${SENS_DIRS[@]}"; do
    [[ -d "$ROOT/$d" ]] || continue
    SENS_HITS+="$(grep -rEl --exclude="$(basename "$0")" -e "$SENS_PATTERN" "$ROOT/$d" 2>/dev/null)"
done
if [[ -f "$ROOT/README.md" ]] && grep -Eq -e "$SENS_PATTERN" "$ROOT/README.md"; then
    SENS_HITS+=" README.md"
fi
if [[ -n "$SENS_HITS" ]]; then
    fail "A3: patrones sensibles encontrados en lo publicable: $(echo "$SENS_HITS" | tr '\n' ' ')"
else
    pass "A3: sin patrones sensibles en lo publicable (docs/skills/drafts/agents/tests/examples/README)"
fi

echo
echo "############################################"
echo "# RESULTADO"
echo "############################################"
echo "Assert PASS: $PASS_COUNT"
echo "Assert FAIL: $FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
    echo "FAIL: $FAIL_COUNT assert(s) fallaron — feature incompleta (estado RED esperado)."
    exit 1
fi

echo "PASS: todas las postcondiciones P1..P6 y el criterio A3 verificados."
exit 0
