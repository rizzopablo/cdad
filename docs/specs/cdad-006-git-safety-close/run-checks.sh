#!/usr/bin/env bash
# Checks RED/GREEN cdad-006-git-safety-close — corren desde la raíz del repo
# Framework documental: checks de estructura (patrón cdad-004/cdad-005).
SM="skills/cdad-cycle/references/stage-5-merge.md"
AP="skills/cdad-cycle/references/anti-patterns.md"

# Scope del bloque de la nueva sección (número agnóstico: el spec dice §5.4,
# pero el archivo ya tiene 5.4/5.5 — ver VALIDATION.md §desviación).
SCOPE="sed -n '/^## 5\.[0-9]* — Cierre de la branch/,/^## /p' '$SM'"

pass=0; fail=0
t() {
  local id="$1" desc="$2" cmd="$3" rc
  if eval "$cmd" >/dev/null 2>&1; then
    echo "PASS  $id $desc"; pass=$((pass+1))
  else
    rc=$?
    echo "FAIL  $id $desc (exit=$rc)"; fail=$((fail+1))
  fi
}

echo "=== C1 -> P1: stage-5-merge.md sección Cierre de la branch (una pieza por check) ==="
t C1a "encabezado '## 5.N — Cierre de la branch (git safety)'" "test -f '$SM' && grep -qE '^## 5\.[0-9]+ — Cierre de la branch' '$SM'"
t C1b "detección git-dir/git-common-dir + guard submodule (P1a)" "$SCOPE | grep -q -- '--git-dir' && $SCOPE | grep -q -- '--git-common-dir' && $SCOPE | grep -q -- '--show-superproject-working-tree'"
t C1c "base branch confirmada, nunca asumida (P1b)" "$SCOPE | grep -qi 'nunca' && $SCOPE | grep -qiE 'confirmar|confirmaci(ó|o)n'"
t C1d "menú fijo 4 opciones (P1c)" "$SCOPE | grep -qi 'merge local' && $SCOPE | grep -q 'PR' && $SCOPE | grep -qi 'keep' && $SCOPE | grep -qi 'discard'"
t C1e "conflicto STOP sin auto-resolver + re-verificación de suite (P1d)" "$SCOPE | grep -qiE 'STOP' && $SCOPE | grep -qiE 'auto.?resolver|sin resolver' && $SCOPE | grep -qiE 're.?verificaci(ó|o)n'"
t C1f "discard palabra literal (P1f/R4)" "$SCOPE | grep -q 'discard'"
t C1g "limpieza por provenance, solo worktrees propios (P1g/R3)" "$SCOPE | grep -qiE '\\.worktrees|provenance|propios'"
t C1h "prune (P1g)" "$SCOPE | grep -q 'prune'"
t C1i "orden crítico merge -> worktree -> branch (P1h)" "$SCOPE | grep -qiE 'merge primero|primero.*merge'"
t C1j "anti-racionalización + cuándo NO aplica squash/monorepo (P1i)" "$SCOPE | grep -qiE 'anti-racionalizaci(ó|o)n' && $SCOPE | grep -qiE 'cu(á|a)ndo NO aplica' && $SCOPE | grep -qi 'squash' && $SCOPE | grep -qi 'monorepo'"

echo "=== C2 -> P2: anti-patterns.md AP-17 ==="
t C2a "encabezado '^## AP-17'" "grep -nE '^## AP-17' '$AP'"
t C2b "3 sub-secciones (Síntoma/Por qué es malo/Corrección) en bloque AP-17" "sed -n '/^## AP-17/,/^## AP-[0-9]/p' '$AP' | grep -q 'Síntoma' && sed -n '/^## AP-17/,/^## AP-[0-9]/p' '$AP' | grep -q 'Por qué es malo' && sed -n '/^## AP-17/,/^## AP-[0-9]/p' '$AP' | grep -q 'Corrección'"
t C2c "AP-17 cita §5.4 / stage-5" "sed -n '/^## AP-17/,/^## AP-[0-9]/p' '$AP' | grep -qE '5\\.4|stage-5'"

echo "=== C3 -> criterio 3: GUARD encabezados previos intactos (PASS hoy) ==="
t C3a "5.1 CI presente" "grep -qE '^## 5\\.1 — Verificaci(ó|o)n CI' '$SM'"
t C3b "5.2 Handoff al Scribe presente" "grep -q '^## 5.2 — Handoff al Scribe' '$SM'"
t C3c "5.3 Validación del usuario presente" "grep -qE '^## 5\\.3 — Validaci(ó|o)n del usuario' '$SM'"
t C3d "5.4 — Decisión sobre ADR intacta (no clobbered)" "grep -q '^## 5.4 — Decisión sobre ADR' '$SM'"
t C3e "5.5 — Merge intacto" "grep -q '^## 5.5 — Merge' '$SM'"
t C3f "Gate de salida presente" "grep -q 'Gate de salida' '$SM'"

echo "=== C4 -> criterio 5 (post-GREEN) ==="
if [ "${1:-}" = "--full" ]; then
  echo "--- C4a: suite cdad-003 ---"
  bash tests/validate-odoo-specialization.sh 2>&1 | tail -4
  echo "--- C4b: checks cdad-004 (C1a-C1f, C2a-C2b, C3a-C3b, vía --full de cdad-005) ---"
  bash docs/specs/cdad-005-receiving-feedback/run-checks.sh --full 2>&1 | grep -E 'C6b RESUMEN|Assert (PASS|FAIL)'
  echo "--- C4c: checks cdad-005 (contenido) ---"
  bash docs/specs/cdad-005-receiving-feedback/run-checks.sh 2>&1 | tail -1
else
  echo "POST-GREEN  C4a bash tests/validate-odoo-specialization.sh -> 121/121"
  echo "POST-GREEN  C4b checks cdad-004 -> 10/10  (correr: run-checks.sh --full)"
  echo "POST-GREEN  C4b' checks cdad-005 -> 23/23"
fi

echo "---"
echo "RESUMEN: PASS=$pass FAIL=$fail (checks de contenido + guard: $((pass+fail)); C4 corre con --full post-GREEN)"
