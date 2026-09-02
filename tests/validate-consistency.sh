#!/usr/bin/env bash
# =============================================================================
# validate-consistency.sh
#
# Oráculo de validación del epic docs/epics/epic-002-cdad-audit-fixes/plan.md.
# Cada bloque corresponde a una feature del epic (002-NNN-<slug>) y verifica
# la(s) postcondición(es) que esa feature cierra, contra el informe
# findings/audit-consistencia-2026-09-02.md. Bash puro (grep/sed/awk/diff),
# sin dependencias externas.
#
# Uso:
#   bash tests/validate-consistency.sh
#
# Salida: asserts PASS/FAIL explícitos + contador final. Exit 0 si todo pasa.
# =============================================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS_COUNT=0
FAIL_COUNT=0

pass() { PASS_COUNT=$((PASS_COUNT + 1)); printf 'PASS: %s\n' "$*"; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf 'FAIL: %s\n' "$*"; }

assert_file() {
  if [[ -f "$ROOT/$1" ]]; then pass "$2 ($1 existe)"; else fail "$2 ($1 NO existe)"; fi
}

assert_file_has() {
  if [[ -f "$ROOT/$1" ]] && grep -Eq -e "$2" "$ROOT/$1"; then
    pass "$3 ($1 contiene '$2')"
  else
    fail "$3 ($1 NO contiene '$2')"
  fi
}

assert_file_not_has() {
  if [[ -f "$ROOT/$1" ]] && ! grep -Eq -e "$2" "$ROOT/$1"; then
    pass "$3 ($1 NO contiene '$2')"
  else
    fail "$3 ($1 SÍ contiene '$2', no permitido)"
  fi
}

assert_files_identical() {
  # assert_files_identical <ruta1> <ruta2> <mensaje>
  if [[ -f "$ROOT/$1" && -f "$ROOT/$2" ]] && diff -q "$ROOT/$1" "$ROOT/$2" >/dev/null 2>&1; then
    pass "$3 ($1 == $2)"
  else
    fail "$3 ($1 != $2)"
  fi
}

assert_cmd_ok() {
  # assert_cmd_ok "<comando>" <mensaje>
  if eval "$1" >/dev/null 2>&1; then pass "$2"; else fail "$2"; fi
}

echo "############################################"
echo "# epic-002-cdad-audit-fixes — validate-consistency"
echo "############################################"
echo "(las secciones se completan feature por feature; ver plan.md)"
echo

echo "############################################"
echo "# F002 — single-source state schema (B9)"
echo "############################################"

# assets/state-template.json es la fuente única: debe llevar TODOS los campos
# (incluidos los de epic), no solo los de feature.
for key in stack active_epic epic_stage epic_features epic_history \
           audit_status postconditions_status stage_history active_feature \
           current_stage tdd_substage approver last_updated version; do
  assert_file_has "skills/cdad-cycle/assets/state-template.json" "\"$key\"" \
    "F002: state-template.json declara el campo '$key'"
done

assert_file_has "skills/cdad-cycle/references/state-detection.md" 'idle' \
  "F002: state-detection.md documenta el valor 'idle' de current_stage"

assert_file_has "skills/cdad-cycle/SKILL.md" \
  'assets/state-template\.json' \
  "F002: SKILL.md § State file referencia assets/state-template.json como schema completo"

assert_file_has "skills/cdad-cycle/references/bootstrap.md" \
  'assets/state-template\.json' \
  "F002: bootstrap.md Paso 4 referencia assets/state-template.json en vez de reproducir el schema"

assert_file_has "skills/cdad-epic/SKILL.md" \
  'cdad-cycle/assets/state-template\.json' \
  "F002: cdad-epic/SKILL.md referencia el schema base de cdad-cycle en vez de duplicarlo"

echo
echo "############################################"
echo "# F004 — verdict-tuple en los 4 agentes reviewer (B3) + tabla de carga (M5)"
echo "############################################"

for f in agents/cdad-reviewer.md agents/claude-code/cdad-reviewer.md \
         agents/cdad-reviewer-odoo.md agents/claude-code/cdad-reviewer-odoo.md; do
  assert_file_has "$f" 'Bucket' "F004: $f incluye campo Bucket en el formato de hallazgo"
  assert_file_has "$f" 'Abstenci' "F004: $f incluye sección Abstenciones"
done

# La tabla "Cómo leer las references" es la sección específica (no basta con
# que el archivo se mencione en otro lado del documento).
load_table() { awk '/## Cómo leer las references/{f=1} f{print} /^---$/{if(f)exit}' "$ROOT/skills/cdad-cycle/SKILL.md"; }
if load_table | grep -q 'verdict-tuple\.md'; then
  pass "F004: tabla 'Cómo leer las references' incluye verdict-tuple.md"
else
  fail "F004: tabla 'Cómo leer las references' NO incluye verdict-tuple.md"
fi
if load_table | grep -q 'claude-code-delegation\.md'; then
  pass "F004: tabla 'Cómo leer las references' incluye claude-code-delegation.md"
else
  fail "F004: tabla 'Cómo leer las references' NO incluye claude-code-delegation.md"
fi

echo "############################################"
echo "# RESULTADO"
echo "############################################"
echo "Assert PASS: $PASS_COUNT"
echo "Assert FAIL: $FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  echo "FAIL: $FAIL_COUNT assert(s) fallaron."
  exit 1
fi

echo "PASS: todas las aserciones del epic 002 verificadas."
exit 0
