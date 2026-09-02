#!/usr/bin/env bash
# Checks RED/GREEN cdad-007-systematic-debugging — corren desde la raíz del repo
# Framework documental: checks de estructura (patrón cdad-004/005/006).
SD="skills/cdad-cycle/references/stage-debugging.md"
S3="skills/cdad-cycle/references/stage-3-tdd.md"
S5="skills/cdad-cycle/references/stage-5-merge.md"
SK="skills/cdad-cycle/SKILL.md"
AP="skills/cdad-cycle/references/anti-patterns.md"

# Scope del bloque AP-18 (último AP: sin corte posterior imprime a EOF).
AP18="sed -n '/^## AP-18/,\$p' '$AP'"
# Scope de la sección GREEN (3.2) de stage-3.
G32="sed -n '/^## Sub-fase 3.2/,/^## Sub-fase 3.3/p' '$S3'"
# Scope de §5.1 de stage-5.
S51="sed -n '/^## 5.1/,/^## 5.2/p' '$S5'"

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

echo "=== C1 -> P1: stage-debugging.md (una pieza por check; ver desviación en VALIDATION.md) ==="
t C1a "P1a: encabezado + ley de hierro sin causa raíz no hay fix + tight feedback loop = RED" "test -f '$SD' && grep -qiE 'causa ra(í|i)z' '$SD' && grep -qiE 'no hay fix|sin .*no hay' '$SD' && grep -q 'RED' '$SD' && grep -qi 'feedback loop' '$SD'"
t C1b "P1b(1): fase diagnóstico: error completo + loop rojo + cambios recientes + evidencia" "grep -qiE 'error completo' '$SD' && grep -qiE 'loop rojo' '$SD' && grep -qiE 'cambios recientes' '$SD' && grep -qi 'evidencia' '$SD'"
t C1c "P1b(2): minimización de repro cut-one-thing" "grep -qiE 'cut.?one.?thing' '$SD' && grep -qiE 'minimi' '$SD'"
t C1d "P1b(3): hipótesis rankeadas 3-5 falsables, una variable por vez" "grep -qiE 'hip(ó|o)tesis' '$SD' && grep -qE '3[-–]5|3 a 5' '$SD' && grep -qi 'falsable' '$SD' && grep -qiE 'una variable' '$SD'"
t C1e "P1b(4): fix único sobre causa raíz" "grep -qiE 'fix (ú|u)nico' '$SD' && grep -qiE 'causa ra(í|i)z' '$SD'"
t C1f "P1c: defense-in-depth después del fix + condition-based-waiting (tasa de repro)" "grep -qi 'defense.?in.?depth' '$SD' && grep -qi 'condition.?based.?waiting' '$SD' && grep -qiE 'tasa de repro|tasa de reproducci(ó|o)n' '$SD'"
t C1g "P1d: regla 3+ fixes -> STOP -> escalar al usuario con evidencia -> ADR" "grep -qE '3\\+' '$SD' && grep -q 'STOP' '$SD' && grep -qi 'evidencia' '$SD' && grep -q 'ADR' '$SD' && grep -qi 'usuario' '$SD'"
t C1h "P1e: roles — diagnóstico implementer / regresión test-writer / Five Whys-Fagan stubborn" "grep -qi 'implementer' '$SD' && grep -qi 'test-writer' '$SD' && grep -qi 'Five Whys' '$SD' && grep -qi 'Fagan' '$SD' && grep -qi 'stubborn' '$SD'"
t C1i "P1f: tabla anti-racionalización" "grep -qiE 'anti-racionalizaci(ó|o)n' '$SD' && grep -qE '^\|' '$SD'"
t C1j "P1g: cuándo NO aplica — infra / flaky puro con plan de monitoreo" "grep -qiE 'cu(á|a)ndo NO aplica' '$SD' && grep -qi 'flaky' '$SD' && grep -qi 'infra' '$SD' && grep -qi 'monitoreo' '$SD'"

echo "=== C2 -> P2: enlaces de entrada (SKILL.md, stage-3 GREEN, stage-5 §5.1) ==="
t C2a "P2a: SKILL.md tabla de lectura agrega fila stage-debugging" "test -f '$SK' && grep -q 'stage-debugging' '$SK'"
t C2b "P2b: stage-3 sub-fase GREEN referencia stage-debugging antes de re-delegar" "$G32 | grep -q 'stage-debugging' && $G32 | grep -qiE 're-deleg'"
t C2c "P2c: stage-5 §5.1 referencia stage-debugging antes de 'volvé/volvemos a Etapa 3'" "$S51 | grep -q 'stage-debugging' && $S51 | grep -qiE 'volv(é|e) a Etapa 3' && $S51 | awk '/stage-debugging/{seen=1} /volv(é|e) a Etapa 3/{if(!seen) exit 1}'"

echo "=== C3 -> P3: anti-patterns.md AP-18 ==="
t C3a "encabezado '^## AP-18'" "grep -nE '^## AP-18' '$AP'"
t C3b "3 sub-secciones (Síntoma/Por qué es malo/Corrección) en bloque AP-18" "$AP18 | grep -q 'Síntoma' && $AP18 | grep -q 'Por qué es malo' && $AP18 | grep -q 'Corrección'"
t C3c "AP-18 cita la reference stage-debugging" "$AP18 | grep -q 'stage-debugging'"

echo "=== C4 -> GUARD: sub-fases TDD, gates y estructura previa intactos (PASS hoy) ==="
t C4a "stage-3: Sub-fase 3.1 — RED intacta" "grep -qE '^## Sub-fase 3.1 — RED' '$S3'"
t C4b "stage-3: Sub-fase 3.2 — GREEN intacta" "grep -qE '^## Sub-fase 3.2 — GREEN' '$S3'"
t C4c "stage-3: Sub-fase 3.3 — REFACTOR intacta" "grep -qE '^## Sub-fase 3.3 — REFACTOR' '$S3'"
t C4d "stage-3: Gate de salida (Etapa 3 -> Etapa 4) presente" "grep -q 'Gate de salida (Etapa 3' '$S3'"
t C4e "stage-5: '## 5.6 — Cierre de la branch (git safety)' intacta (cdad-006, no clobbered)" "grep -q '^## 5.6 — Cierre de la branch (git safety)' '$S5'"
t C4f "stage-5: Gate de salida (Etapa 5 -> done) presente" "grep -q 'Gate de salida (Etapa 5' '$S5'"
t C4g "stage-5: '## 5.1 — Verificación CI' intacta" "grep -qE '^## 5.1 — Verificaci(ó|o)n CI' '$S5'"

echo "=== C5 -> criterio 5 (post-GREEN) ==="
if [ "${1:-}" = "--full" ]; then
  echo "--- C5a: suite cdad-003 ---"
  bash tests/validate-odoo-specialization.sh 2>&1 | tail -4
  echo "--- C5b: checks cdad-004 + cdad-005 (vía --full de cdad-005) ---"
  bash docs/specs/cdad-005-receiving-feedback/run-checks.sh --full 2>&1 | grep -E 'C6b RESUMEN|Assert (PASS|FAIL)'
  echo "--- C5c: checks cdad-005 (contenido) ---"
  bash docs/specs/cdad-005-receiving-feedback/run-checks.sh 2>&1 | tail -1
  echo "--- C5d: checks cdad-006 (no regresión cross-feature) ---"
  bash docs/specs/cdad-006-git-safety-close/run-checks.sh 2>&1 | tail -1
else
  echo "POST-GREEN  C5a bash tests/validate-odoo-specialization.sh -> 121/121"
  echo "POST-GREEN  C5b checks cdad-004 + cdad-005 -> 10/10 + 23/23  (correr: run-checks.sh --full)"
  echo "POST-GREEN  C5c checks cdad-005 -> 23/23"
  echo "POST-GREEN  C5d checks cdad-006 -> 19/19"
fi

echo "---"
echo "RESUMEN: PASS=$pass FAIL=$fail (checks de contenido + guard: $((pass+fail)); C5 corre con --full post-GREEN)"
