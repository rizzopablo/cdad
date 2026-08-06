#!/usr/bin/env bash
# validate-subagents.sh — cdad-001: valida que la delegación vía sub-agentes
# nativos (subagent_type: cdad-<rol>) esté instalada y operativa end-to-end.
#
# Spec:   docs/specs/cdad-001-validate-subagents/spec.md
# Tests:  docs/specs/cdad-001-validate-subagents/tests/run_all.sh
# Uso:    bash scripts/validate-subagents.sh
#
# Qué verifica (en orden):
#   1. runtime  — los 5 agentes cdad-*.md existen en el dir de INSTALACIÓN
#      ($HOME/.config/opencode/agents), no en el repo. Si el dir runtime no
#      existe, fallback DOCUMENTADO: se compara contra el repo (agents/) con
#      WARN explícito y la etapa cuenta como FAIL (runtime no instalado).
#   2. repo     — cross-check contra la fuente de verdad reusando
#      `install.sh --check` (no se duplica lógica de comparación).
#   3. artefactos — enumera y verifica los 5 artefactos por etapa del ciclo
#      CDAD en docs/specs/cdad-001-validate-subagents/artifacts/.
#   4. modelos — cada agente cdad-* declara el modelo esperado (mapa
#      ADR-001/005) en su frontmatter; cdad-orchestrator NO declara model:
#      (el modelo lo elige el usuario).
#
# Exit: 0 si y solo si TODAS las verificaciones pasan; != 0 ante cualquier
# falla, imprimiendo qué falló. Read-only: idempotente por diseño.
# Convención del repo: set -euo pipefail (alineado con install.sh:12).
# El manejo de errores manual (FAIL + if-forms) es compatible con -e: las
# operaciones cuyo fallo es esperado se capturan en condiciones if, nunca
# como statements sueltos (reviewer cdad-001 finding #2).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SPEC_DIR="$REPO_ROOT/docs/specs/cdad-001-validate-subagents"
ART_DIR="$SPEC_DIR/artifacts"
RUNTIME_DIR="${HOME:-}/.config/opencode/agents"
INSTALL_SH="$REPO_ROOT/install.sh"
AGENTS=(cdad-architect cdad-implementer cdad-reviewer cdad-scribe cdad-test-writer)

FAIL=0
# Diagnósticos a stderr: no contaminan stdout verificable (reviewer finding #4).
fail() { echo "❌ $1" >&2; FAIL=1; }
ok()   { echo "✅ $1"; }

echo "== cdad-001 validate-subagents =="

# --- Etapa 1: agentes runtime (fuente: instalación, no repo) ----------------
echo "[runtime] agentes en $RUNTIME_DIR"
if [ ! -d "$RUNTIME_DIR" ]; then
  echo "⚠️  dir runtime no existe: $RUNTIME_DIR"
  echo "    Fallback documentado: comparando contra repo agents/ (fuente de verdad)."
  echo "    La etapa cuenta como FAIL: el runtime no está instalado."
  fail "runtime agents dir ausente: $RUNTIME_DIR"
  RUNTIME_DIR="$REPO_ROOT/agents"   # fallback: solo informativo
fi
for a in "${AGENTS[@]}"; do
  if [ ! -f "$RUNTIME_DIR/$a.md" ]; then
    fail "falta agente runtime: $a.md"
  elif ! grep -q '^description:' "$RUNTIME_DIR/$a.md"; then
    # Frontmatter mínimo: cubre la claim de §6 ("config estática (frontmatter
    # + byte-compare)") — el byte-compare lo hace install.sh --check (Etapa 2),
    # el frontmatter lo valida esta Etapa 1 (reviewer finding #5).
    fail "frontmatter sin description: $a.md"
  fi
done
if [ "$FAIL" -eq 0 ]; then ok "5/5 agentes runtime presentes (frontmatter OK)"; fi

# --- Etapa 2: cross-check contra repo (reusa install.sh --check) ------------
echo "[repo] cross-check: install.sh --check"
# La invocación se hace con `bash`, así que solo importa la existencia del
# archivo, no el bit +x (reviewer finding #3). Captura en if-form por set -e.
if [ ! -f "$INSTALL_SH" ]; then
  fail "install.sh no encontrado en $INSTALL_SH"
else
  if CHECK_OUT=$(bash "$INSTALL_SH" --check 2>&1); then
    CHECK_RC=0
  else
    CHECK_RC=$?
  fi
  echo "$CHECK_OUT" | tail -3
  if [ "$CHECK_RC" -ne 0 ]; then
    fail "install.sh --check falló (rc=$CHECK_RC)"
  else
    ok "install.sh --check PASS"
  fi
fi

# --- Etapa 3: artefactos por etapa (enumerar y verificar formato) -----------
echo "[artefactos] $ART_DIR"
stage() { # nombre path ok(0|1)
  if [ "$3" = "0" ]; then ok "$1 -> OK"; else fail "$1 -> FAIL ($2)"; fi
}
if [ -f "$ART_DIR/spec.md" ] && grep -q "^## 2\. Postcondición" "$ART_DIR/spec.md"; then
  stage architect "spec.md" 0; else stage architect "spec.md" 1; fi
if [ -d "$ART_DIR/tests" ] && [ -n "$(ls -A "$ART_DIR/tests" 2>/dev/null)" ]; then
  stage test-writer "tests/" 0; else stage test-writer "tests/" 1; fi
# impl.diff: bien formado Y representando el estado actual (git apply --check
# --reverse = ya aplicado; fallback forward = aún aplicable). `patch --dry-run`
# falla con diffs de creación ya aplicados (archivo existe) — ver review.md.
if [ -f "$ART_DIR/impl.diff" ] && { \
    (cd "$REPO_ROOT" && git apply --check --reverse "$ART_DIR/impl.diff" >/dev/null 2>&1) || \
    (cd "$REPO_ROOT" && git apply --check "$ART_DIR/impl.diff" >/dev/null 2>&1); }; then
  stage implementer "impl.diff" 0; else stage implementer "impl.diff" 1; fi
if [ -f "$ART_DIR/review.md" ] && grep -q "^Reviewer model: " "$ART_DIR/review.md"; then
  stage reviewer "review.md" 0; else stage reviewer "review.md" 1; fi
if [ -f "$ART_DIR/memory-bank.md" ] && grep -qE "^##? .*2026|^[0-9]{4}-[0-9]{2}-[0-9]{2}" "$ART_DIR/memory-bank.md"; then
  stage scribe "memory-bank.md" 0; else stage scribe "memory-bank.md" 1; fi

# --- Etapa 4: modelos por agente (mapa ADR-001/005) ---------------------------
echo "[modelos] modelo esperado por agente"
# El mapa duplica la tabla "Familia modelo" del Contrato de roles (ADR-001) y
# la decisión de provider de ADR-005 — guard de validación intencional: si el
# repo o el runtime drift de la decisión, esta etapa lo detecta. Se corre al
# final (después de los artefactos) para no romper el contexto del impl.diff
# de cdad-001, que cubre solo hasta la Etapa 2.
declare -A MODEL_EXPECTED=(
  [cdad-architect]=mofgw/deepseek-v4-pro
  [cdad-test-writer]=mofgw/glm-5.2
  [cdad-implementer]=mofgw/deepseek-v4-flash
  [cdad-reviewer]=mofgw/qwen3.7-plus
  [cdad-scribe]=mofgw/deepseek-v4-pro
)
# cdad-orchestrator NO declara model: — el modelo lo elige el usuario al
# seleccionarlo (ADR-001/005: el orquestador sigue sin modelo fijo).
for a in "${AGENTS[@]}"; do
  expected="${MODEL_EXPECTED[$a]:-}"
  [ -z "$expected" ] && continue
  actual="$(sed -n 's/^model:[[:space:]]*//p' "$RUNTIME_DIR/$a.md" 2>/dev/null | head -1)"
  if [ -z "$actual" ]; then
    fail "modelo ausente en $a.md (esperado: $expected)"
  elif [ "$actual" != "$expected" ]; then
    fail "modelo incorrecto en $a.md: '$actual' (esperado: '$expected')"
  fi
done
if [ -f "$RUNTIME_DIR/cdad-orchestrator.md" ] && grep -q '^model:' "$RUNTIME_DIR/cdad-orchestrator.md"; then
  fail "cdad-orchestrator.md no debe declarar model: (el modelo lo elige el usuario)"
fi
if [ "$FAIL" -eq 0 ]; then ok "modelos OK (5/5 según ADR-001/005; orquestador sin model:)"; fi

# --- Veredicto -----------------------------------------------------------------
if [ "$FAIL" -eq 0 ]; then
  echo "== RESULTADO: PASS (todas las verificaciones OK) =="
  exit 0
else
  echo "== RESULTADO: FAIL (ver mensajes ❌ arriba) =="
  exit 1
fi
