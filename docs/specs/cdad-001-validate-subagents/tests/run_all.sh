#!/usr/bin/env bash
# run_all.sh — tests de la spec cdad-001-validate-subagents
# Ejecutar desde docs/specs/cdad-001-validate-subagents/
# Uso: bash tests/run_all.sh [--setup-only]
set -u

SPEC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SPEC_DIR/../../.." && pwd)"          # repo root
SCRIPT="$REPO_ROOT/scripts/validate-subagents.sh"
ART_DIR="$SPEC_DIR/artifacts"
RUNTIME_DIR="${HOME}/.config/opencode/agents"
TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

PASS=0; FAIL=0
report() { # name ok detail
  if [ "$2" = "0" ]; then PASS=$((PASS+1)); echo "✅ T${1}: PASS — ${3}";
  else FAIL=$((FAIL+1)); echo "❌ T${1}: FAIL — ${3}"; fi
}

# ---- Precondiciones del entorno de test ----
if [ ! -f "$SCRIPT" ]; then
  echo "⚠️  validate-subagents.sh no existe aún (spec-first: tests antes del build)."
  echo "    Tests corridos en modo 'pre-build': solo precondiciones + formato de artefactos."
fi

# ---- T1: exit 0 con entorno válido ----
if [ -f "$SCRIPT" ]; then
  bash "$SCRIPT" >/dev/null 2>&1
  T1_RC=$?
  report 1 "$([ $T1_RC -eq 0 ] && echo 0 || echo 1)" "exit=$T1_RC (esperado 0)"
else
  report 1 1 "script ausente (pre-build)"
fi

# ---- T2: exit != 0 si falta un agente runtime ----
if [ -f "$SCRIPT" ] && [ -d "$RUNTIME_DIR" ] && [ -f "$RUNTIME_DIR/cdad-reviewer.md" ]; then
  mv "$RUNTIME_DIR/cdad-reviewer.md" "$TMPDIR_TEST/cdad-reviewer.md"
  OUT=$(bash "$SCRIPT" 2>&1); T2_RC=$?
  mv "$TMPDIR_TEST/cdad-reviewer.md" "$RUNTIME_DIR/cdad-reviewer.md"
  if [ $T2_RC -ne 0 ] && echo "$OUT" | grep -q "cdad-reviewer"; then
    report 2 0 "exit=$T2_RC + menciona cdad-reviewer"
  else
    report 2 1 "exit=$T2_RC, mención reviewer=$(echo "$OUT" | grep -c cdad-reviewer)"
  fi
elif [ ! -f "$SCRIPT" ]; then
  report 2 1 "script ausente (pre-build)"
else
  report 2 1 "precondición runtime no disponible"
fi

# ---- T3: cross-check contra repo (reusa install.sh --check) ----
if [ -f "$SCRIPT" ]; then
  OUT=$(bash "$SCRIPT" 2>&1)
  if echo "$OUT" | grep -qE "install\.sh --check|PASS \(11/11\)|in sync"; then
    report 3 0 "output incluye cross-check install.sh"
  else
    report 3 1 "output sin rastro de install.sh --check"
  fi
else
  report 3 1 "script ausente (pre-build)"
fi

# ---- T4: artefactos por etapa con formato mínimo ----
T4_OK=0
if [ -f "$ART_DIR/spec.md" ] && grep -q "^## 2\. Postcondición" "$ART_DIR/spec.md"; then T4_OK=$((T4_OK+1)); fi
if [ -d "$ART_DIR/tests" ] && [ -n "$(ls -A "$ART_DIR/tests" 2>/dev/null)" ]; then T4_OK=$((T4_OK+1)); fi
if [ -f "$ART_DIR/impl.diff" ] && { \
    (cd "$REPO_ROOT" && git apply --check --reverse "$ART_DIR/impl.diff" >/dev/null 2>&1) || \
    (cd "$REPO_ROOT" && git apply --check "$ART_DIR/impl.diff" >/dev/null 2>&1); }; then T4_OK=$((T4_OK+1)); fi
if [ -f "$ART_DIR/review.md" ] && grep -q "^Reviewer model: " "$ART_DIR/review.md"; then T4_OK=$((T4_OK+1)); fi
if [ -f "$ART_DIR/memory-bank.md" ] && grep -qE "^##? .*2026|^[0-9]{4}-[0-9]{2}-[0-9]{2}" "$ART_DIR/memory-bank.md"; then T4_OK=$((T4_OK+1)); fi
report 4 "$([ $T4_OK -eq 5 ] && echo 0 || echo 1)" "artefactos OK=$T4_OK/5"

# ---- T5: idempotencia (2 corridas seguidas, sin error de "ya existe") ----
if [ -f "$SCRIPT" ]; then
  R1=$(bash "$SCRIPT" >/dev/null 2>&1; echo $?)
  R2=$(bash "$SCRIPT" >/dev/null 2>&1; echo $?)
  if [ "$R1" = "0" ] && [ "$R2" = "0" ]; then
    report 5 0 "exit=$R1/$R2"
  else
    report 5 1 "exit=$R1/$R2 (esperado 0/0)"
  fi
else
  report 5 1 "script ausente (pre-build)"
fi

echo ""
echo "═══ RESULTADO: $PASS/5 PASS, $FAIL/5 FAIL ═══"
[ $FAIL -eq 0 ] && exit 0 || exit 1
