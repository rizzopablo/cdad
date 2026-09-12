#!/usr/bin/env bash
# =============================================================================
# run-checks.sh — cdad-010-opencode-permissions
#
# Capa estática de verificación de la feature (convención cdad-004):
# asserts grep/awk sobre los frontmatters de los 10 agentes OpenCode,
# el generador de allowlists, install.sh y la documentación P6.
#
# RED: este script se escribió ANTES de tocar implementación y DEBE fallar
# sobre el estado actual del repo (evidencia en VALIDATION.md).
#
# Uso: bash docs/specs/cdad-010-opencode-permissions/run-checks.sh
# Salida: asserts PASS/FAIL + contador. Exit 0 solo si todo pasa.
# =============================================================================
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
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

assert_string_not_has() {
  if [[ -n "$1" ]] && ! printf '%s' "$1" | grep -Eq -e "$2"; then
    pass "$3 (no contiene '$2')"
  else
    fail "$3 (contiene '$2', no permitido)"
  fi
}

frontmatter() {
  awk 'BEGIN{c=0} /^---/{c++; next} c==1 {print}' "$1"
}

# section <archivo> <clave> — imprime SOLO la sección <clave>: del frontmatter
# (líneas desde "  <clave>:" hasta la próxima clave al mismo nivel o "---")
section() {
  frontmatter "$1" | awk -v key="$2" '
    /^[[:space:]]{2}[a-z_]+:/ && !/^[[:space:]]{2}'"$key"':/ { if (on) exit }
    /^[[:space:]]{2}'"$key"':/ { on=1; print; next }
    on { print }
  '
}

# first_rule <contenido-sección> — primera línea de regla (no clave, no comentario)
first_rule() {
  printf '%s' "$1" | grep -v '^[[:space:]]*#' | grep -E '^[[:space:]]{4,}"' | head -1
}

AGENTS_BASE=(cdad-architect cdad-test-writer cdad-implementer cdad-reviewer cdad-scribe)
AGENTS_ALL=("${AGENTS_BASE[@]}" cdad-architect-odoo cdad-test-writer-odoo cdad-implementer-odoo cdad-reviewer-odoo cdad-scribe-odoo)

echo "############################################"
echo "# cdad-010 — run-checks (capa estática)"
echo "############################################"
echo

echo "## A1 — P1: write: ask (palanca de clasificación)"
for a in "${AGENTS_ALL[@]}"; do
  f="agents/$a.md"
  if [[ -f "$ROOT/$f" ]] && frontmatter "$ROOT/$f" | grep -Eq '^write:[[:space:]]*ask[[:space:]]*$'; then
    pass "A1: $f declara 'write: ask'"
  else
    fail "A1: $f NO declara 'write: ask' literal"
  fi
done
echo

echo "## A2 — P2/P3: catch-all primero + cero ask en claves de runtime"
for a in "${AGENTS_ALL[@]}"; do
  f="agents/$a.md"
  fm="$(frontmatter "$ROOT/$f" 2>/dev/null || true)"
  for key in bash edit read; do
    sec="$(printf '%s' "$fm" | awk -v key="$key" '
      /^[[:space:]]{2}[a-z_]+:/ && !/^[[:space:]]{2}'"$key"':/ { if (on) exit }
      /^[[:space:]]{2}'"$key"':/ { on=1; print; next }
      on { print }
    ')"
    # solo aplica si la clave es un bloque con reglas (no "deny"/"ask" simple)
    if printf '%s' "$sec" | grep -Eq '^[[:space:]]{4,}"'; then
      fr="$(printf '%s' "$sec" | grep -v '^[[:space:]]*#' | grep -E '^[[:space:]]{4,}"' | head -1)"
      if printf '%s' "$fr" | grep -Eq '"\*"[[:space:]]*:'; then
        pass "A2: $f/$key: catch-all es la primera regla"
      else
        fail "A2: $f/$key: la primera regla NO es catch-all (findLast invertido): '$fr'"
      fi
      if printf '%s' "$sec" | grep -Eq ':[[:space:]]*ask[[:space:]]*$'; then
        fail "A2: $f/$key: contiene acción 'ask' en runtime (prohibido, P3)"
      else
        pass "A2: $f/$key: sin 'ask' en runtime"
      fi
    fi
  done
done
echo

echo "## A3 — P4: política rtk global (denies + prohibiciones)"
for a in "${AGENTS_ALL[@]}"; do
  f="agents/$a.md"
  b="$(section "$ROOT/$f" bash | grep -v '^[[:space:]]*#' || true)"
  assert_string_not_has "$b" '"rtk \*":[[:space:]]*allow' \
    "A3: $f: bash NO tiene 'rtk *': allow (fuga total)"
  assert_string_not_has "$b" '"rtk git \*":[[:space:]]*allow' \
    "A3: $f: bash NO tiene 'rtk git *': allow (AP-17 vía proxy)"
  if printf '%s' "$b" | grep -Eq '"rtk err\*":[[:space:]]*deny'; then
    pass "A3: $f: 'rtk err*': deny presente"
  else
    fail "A3: $f: falta 'rtk err*': deny (ejecución arbitraria)"
  fi
  if printf '%s' "$b" | grep -Eq '"rtk summary\*":[[:space:]]*deny'; then
    pass "A3: $f: 'rtk summary*': deny presente"
  else
    fail "A3: $f: falta 'rtk summary*': deny (ejecución arbitraria)"
  fi
done
echo

echo "## A4 — P2/P4: test-writer (+odoo): scoping y pares rtk de lectura"
for a in cdad-test-writer cdad-test-writer-odoo; do
  f="agents/$a.md"
  b="$(section "$ROOT/$f" bash | grep -v '^[[:space:]]*#' || true)"
  e="$(section "$ROOT/$f" edit | grep -v '^[[:space:]]*#' || true)"
  r="$(section "$ROOT/$f" read | grep -v '^[[:space:]]*#' || true)"
  for forb in '"rtk read\*":[[:space:]]*allow' '"rtk grep\*":[[:space:]]*allow' '"rtk find\*":[[:space:]]*allow' '"rtk diff\*":[[:space:]]*allow;'; do :; done
  for pat in '"rtk read\*"' '"rtk grep\*"' '"rtk find\*"' '"rtk diff\*"'; do
    if printf '%s' "$b" | grep -Eq "$pat"; then
      val="$(printf '%s' "$b" | grep -E "$pat" | head -1 | sed -E 's/.*:[[:space:]]*//')"
      if [[ "$val" == "deny" ]]; then
        pass "A4: $f: $pat es deny"
      else
        fail "A4: $f: $pat NO es deny (fuga de lectura hacia src/**)"
      fi
    else
      fail "A4: $f: falta la regla $pat (debe ser deny)"
    fi
  done
  # globs de tests colocados EXPANDIDOS (sin braces — el matcher escapa {})
  if printf '%s' "$e" | grep -q '{'; then
    fail "A4: $f/edit: usa braces {} (el matcher los escapa — expandir variantes)"
  else
    pass "A4: $f/edit: sin braces {}"
  fi
  for glob in '\*\*/\*_test\.go' '\*\*/\*\.test\.js' '\*\*/\*\.test\.ts' '\*\*/\*\.test\.mjs' '\*\*/\*\.test\.cjs' '\*\*/\*\.spec\.ts' '\*\*/\*\.spec\.js' '\*\*/test_\*\.py'; do
    assert_file_has "$f" "\"$glob\"[[:space:]]*:[[:space:]]*allow" \
      "A4: $f/edit: glob de tests colocados '$glob' en allow"
  done
  assert_file_has "$f" '"tests/\*\*":[[:space:]]*allow' "A4: $f/edit: 'tests/**': allow"
  assert_file_has "$f" '"\*\*/tests/\*\*":[[:space:]]*allow' "A4: $f/edit: '**/tests/**': allow"
  # read: excepciones de lectura para tests colocados bajo src/lib
  assert_file_has "$f" '"src/\*\*/\*_test\.go"[[:space:]]*:[[:space:]]*allow|"src/\*\*/\*\*_test\.go"[[:space:]]*:[[:space:]]*allow' \
    "A4: $f/read: excepción de lectura para tests Go colocados"
done
echo

echo "## A5 — P2: implementer (+odoo): blocklist de tests"
for a in cdad-implementer cdad-implementer-odoo; do
  f="agents/$a.md"
  e="$(section "$ROOT/$f" edit | grep -v '^[[:space:]]*#' || true)"
  assert_file_has "$f" '"tests/\*\*":[[:space:]]*deny' "A5: $f/edit: 'tests/**': deny"
  assert_file_has "$f" '"\*\*/tests/\*\*":[[:space:]]*deny' "A5: $f/edit: '**/tests/**': deny"
  for glob in '\*\*/\*_test\.go' '\*\*/\*\.test\.js' '\*\*/\*\.test\.ts' '\*\*/test_\*\.py'; do
    assert_file_has "$f" "\"$glob\"[[:space:]]*:[[:space:]]*deny" \
      "A5: $f/edit: tests colocados '$glob' en deny"
  done
  if printf '%s' "$e" | grep -q '{'; then
    fail "A5: $f/edit: usa braces {} (expandir variantes)"
  else
    pass "A5: $f/edit: sin braces {}"
  fi
done
echo

echo "## A6 — P2/P4: read-onlys (+odoo): edit deny simple + rtk de lectura"
for a in cdad-architect cdad-reviewer cdad-scribe cdad-architect-odoo cdad-reviewer-odoo cdad-scribe-odoo; do
  f="agents/$a.md"
  b="$(section "$ROOT/$f" bash | grep -v '^[[:space:]]*#' || true)"
  if frontmatter "$ROOT/$f" | grep -Eq '^edit:[[:space:]]*deny[[:space:]]*$'; then
    pass "A6: $f: 'edit: deny' simple"
  else
    fail "A6: $f: 'edit:' NO es deny simple"
  fi
  assert_string_not_has "$b" 'sed[[:space:]]*-i|"sed[[:space:]]*\*":[[:space:]]*allow|"tee' \
    "A6: $f/bash: sin escritura de contenido vía shell (sed -i/tee)"
  for pat in '"rtk read\*"' '"rtk grep\*"' '"rtk find\*"'; do
    assert_file_has "$f" "$pat[[:space:]]*:[[:space:]]*allow" \
      "A6: $f/bash: $pat en allow (rol lector)"
  done
done
echo

echo "## A7 — P5: generador de allowlists + integración install.sh"
assert_file "scripts/cdad-bash-allowlist.sh" "A7: generador existe"
if [[ -f "$ROOT/scripts/cdad-bash-allowlist.sh" && -x "$ROOT/scripts/cdad-bash-allowlist.sh" ]]; then
  pass "A7: generador es ejecutable"
else
  fail "A7: generador NO es ejecutable (chmod +x)"
fi
assert_file_has "install.sh" 'cdad-bash-allowlist\.sh' "A7: install.sh invoca el generador"
assert_file_has "scripts/cdad-bash-allowlist.sh" 'pylint' "A7: generador conserva 'pylint *' para stack odoo"
assert_file_not_has "scripts/cdad-bash-allowlist.sh" '"go[[:space:]]+\*"|go test\*' \
  "A7: generador NO emite go* para stack odoo (FORBIDDEN_BASH_ALL, audit 3.2)"
echo

echo "## A8 — P6: documentación actualizada"
assert_file_has "skills/cdad-cycle/references/opencode-delegation.md" 'write:[[:space:]]*ask' \
  "A8: opencode-delegation.md documenta la palanca write: ask"
assert_file_has "skills/cdad-cycle/references/opencode-delegation.md" 'delegate.*no-viable|canal.*muerto|dead' \
  "A8: opencode-delegation.md documenta delegate como no-viable en este deploy"
assert_file_has "skills/cdad-cycle/SKILL.md" 'task-ables? vía .write: ask|write: ask' \
  "A8: SKILL.md §4 corregido (task-able vía write: ask)"
assert_file_has "agents/cdad-orchestrator.md" 'write: ask|task-able' \
  "A8: cdad-orchestrator.md actualizado (o cita)"
assert_file_has "docs/projectbrief.md" 'task-able|write: ask' \
  "A8: projectbrief.md: restricción de delegación corregida"
assert_file_has "docs/systemPatterns.md" 'write: ask' "A8: systemPatterns.md documenta la palanca"
assert_file_has "docs/systemPatterns.md" 'vigilancia' "A8: systemPatterns.md incluye regla de vigilancia"
echo

echo "## A9 — criterio 6: cero diff en agents/claude-code/"
if git diff --name-only HEAD -- agents/claude-code/ 2>/dev/null | grep -q .; then
  fail "A9: hay cambios sin commitear en agents/claude-code/"
else
  if git log --oneline -20 --format='%h %s' -- agents/claude-code/ | head -1 | grep -qE 'cdad-010'; then
    fail "A9: cdad-010 tocó agents/claude-code/ (prohibido salvo justificación AUDIT)"
  else
    pass "A9: agents/claude-code/ sin cambios de esta feature"
  fi
fi
echo

echo "## A10 — regresión: validadores existentes en PASS"
# NOTA RED: validate-subagents.sh y validate-consistency.sh F011 están en FAIL
# PREEXISTENTE (drift de copias instaladas vs repo — enmiendas 02-09/09-08
# hechas a mano en ~/.config). El GREEN de cdad-010 debe dejarlos en PASS
# (install --check contra expectativa derivada). Registrado en VALIDATION.md.
for v in scripts/validate-subagents.sh tests/validate-odoo-specialization.sh tests/validate-consistency.sh; do
  if bash "$v" >/dev/null 2>&1; then
    pass "A10: $v PASS"
  else
    fail "A10: $v FALLA (preexistente por drift, o regresión de cdad-010)"
  fi
done
echo

echo "############################################"
echo "RESULTADO: $PASS_COUNT PASS, $FAIL_COUNT FAIL"
echo "############################################"
[[ $FAIL_COUNT -eq 0 ]] && exit 0 || exit 1
