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
