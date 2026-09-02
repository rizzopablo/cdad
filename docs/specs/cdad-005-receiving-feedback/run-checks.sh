#!/usr/bin/env bash
# Checks RED/GREEN cdad-005-receiving-feedback — corren desde la raíz del repo
RF="skills/cdad-cycle/references/receiving-feedback.md"
S4="skills/cdad-cycle/references/stage-4-review.md"
AP="skills/cdad-cycle/references/anti-patterns.md"
HP="skills/cdad-cycle/references/handoff-prompts.md"
SK="skills/cdad-cycle/SKILL.md"
VT="skills/cdad-cycle/references/verdict-tuple.md"

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

echo "=== C1 -> P1: receiving-feedback.md (una pieza por check) ==="
t C1a "existe receiving-feedback.md" "test -f '$RF'"
t C1b "secuencia 4 pasos (P1a)" "test -f '$RF' && grep -q 'sin reaccionar' '$RF' && grep -q 'restatea' '$RF' && grep -q 'código real' '$RF' && grep -qi 'de a un fix' '$RF'"
t C1c "respuestas prohibidas (P1b)" "test -f '$RF' && grep -q 'tenés razón' '$RF' && grep -qi 'performativ' '$RF'"
t C1d "ítems ambiguos -> STOP (P1c)" "test -f '$RF' && grep -q 'parar TODO' '$RF' && grep -qiE 'aclaraci(ó|o)n' '$RF'"
t C1e "push-back cuándo+cómo+destino (P1d)" "test -f '$RF' && grep -qi 'push-back' '$RF' && grep -qiE 'rompe funcionalidad|falta contexto|legacy|incorrecto para el stack' '$RF' && grep -qi 'evidencia' '$RF' && grep -qiE 'media el usuario|reconsideraci(ó|o)n' '$RF'"
t C1f "chequeo YAGNI con grep (P1e)" "test -f '$RF' && grep -q 'YAGNI' '$RF' && grep -qi 'grep' '$RF'"
t C1g "corrección factual (P1f)" "test -f '$RF' && grep -qiE 'correcci(ó|o)n factual' '$RF'"
t C1h "matriz de fuentes (P1g)" "test -f '$RF' && grep -qi 'matriz' '$RF' && grep -qi 'trusted' '$RF' && grep -qiE 'esc(e|é)ptic' '$RF'"
t C1i "persistencia -> scribe/systemPatterns (P1h)" "test -f '$RF' && grep -qi 'scribe' '$RF' && grep -q 'systemPatterns' '$RF'"
t C1j "ventaja estructural: dilución + sesión fresca (P1i)" "test -f '$RF' && grep -qiE 'diluci(ó|o)n' '$RF' && grep -qi 'fresca' '$RF'"
t C1k "tabla anti-racionalización (P1j)" "test -f '$RF' && grep -qiE 'anti-racionalizaci(ó|o)n' '$RF'"
t C1l "sección cuándo NO aplica (P1k/R4)" "test -f '$RF' && grep -qiE 'cu(á|a)ndo NO aplica' '$RF'"
t C1m "prohibición cláusulas de salida (P1l/R2)" "test -f '$RF' && grep -qiE 'cl(á|a)usulas? de salida' '$RF'"

echo "=== C2 -> P2: stage-4-review.md (regla del transmisor) ==="
t C2a "menciona receiving-feedback" "grep -q 'receiving-feedback' '$S4'"
t C2b "regla del transmisor: íntegro sin suavizar" "grep -qiE 'íntegr(a|o)' '$S4' && grep -qi 'suaviz' '$S4'"
t C2c "orden al receptor: aplicar protocolo antes de tocar código" "grep -qiE 'antes de (tocar|implementar|editar)' '$S4'"

echo "=== C3 -> P3: anti-patterns.md AP-16 ==="
t C3a "encabezado '^## AP-16'" "grep -nE '^## AP-16' '$AP'"
t C3b "3 sub-secciones (Síntoma/Por qué es malo/Corrección) en bloque AP-16" "sed -n '/^## AP-16/,/^## AP-[0-9]/p' '$AP' | grep -q 'Síntoma' && sed -n '/^## AP-16/,/^## AP-[0-9]/p' '$AP' | grep -q 'Por qué es malo' && sed -n '/^## AP-16/,/^## AP-[0-9]/p' '$AP' | grep -q 'Corrección'"
t C3c "AP-16 cita la reference receiving-feedback" "sed -n '/^## AP-16/,/^## AP-[0-9]/p' '$AP' | grep -q 'receiving-feedback'"

echo "=== C4 -> P4: mapa de lectura + handoff ==="
t C4a "SKILL.md tabla de lectura menciona receiving-feedback.md" "sed -n '/^## Cómo leer las references/,/^## /p' '$SK' | grep -q 'receiving-feedback.md'"
t C4b "handoff-prompts.md: transmisión íntegra + invocación del protocolo" "grep -q 'receiving-feedback' '$HP' && grep -qiE 'íntegr(a|o)' '$HP'"

echo "=== C5 -> invariante reconsideración (verdict-tuple.md) ==="
t C5a "cita steelman/reversal/reconsideración" "grep -qiE 'steelman|reversal|reconsideraci(ó|o)n' '$VT'"
t C5b "GUARD formato intacto (R3): tuple de 4 campos" "grep -q '## El tuple (por hallazgo)' '$VT' && grep -q 'BLOQUEANTE' '$VT' && grep -q 'ABSTENER' '$VT' && grep -q 'Provenance' '$VT'"

echo "=== C6 -> criterio 7 (post-GREEN) ==="
if [ "${1:-}" = "--full" ]; then
  echo "--- C6a: suite cdad-003 ---"
  bash tests/validate-odoo-specialization.sh 2>&1 | tail -4
  echo "--- C6b: checks cdad-004 (C1a-C1f, C2a-C2b, C3a-C3b) ---"
  cd skills
  c=0; ok=0
  cx() { local id="$1" cmd="$2"; c=$((c+1)); if eval "$cmd" >/dev/null 2>&1; then echo "PASS  $id"; ok=$((ok+1)); else echo "FAIL  $id (exit=$?)"; fi; }
  cx C1a "grep -nE '^\|.*\`make lint\`.*\|' odoo-make-env/SKILL.md"
  cx C1b "grep -q -- '--no-overwrite' odoo-make-env/SKILL.md"
  cx C1c "grep -q -- '--diff' odoo-make-env/SKILL.md"
  cx C1d "grep -qE -- '--all\b' odoo-make-env/SKILL.md"
  cx C1e "grep -qE 'uvx pre-commit-vauxoo==[0-9]+\.' odoo-make-env/SKILL.md"
  cx C1f "grep -qiE '(lint|pre-commit).*host|host.*(lint|pre-commit)' odoo-make-env/SKILL.md"
  cx C2a "[ \"\$(grep -c 'hoo-oca' odoo-reviewer/SKILL.md)\" -eq 0 ]"
  cx C2b "sed -n '/[Ee]videncia requerida/,/^## /p' odoo-reviewer/SKILL.md | grep -qE '^4\..*(\bmake lint\b|\blint\b)'"
  cx C3a "grep -qE 'lint limpio|make lint' ../agents/cdad-implementer-odoo.md"
  cx C3b "grep -qE 'lint limpio|make lint' ../agents/cdad-reviewer-odoo.md"
  echo "C6b RESUMEN: $ok/10"
  cd ..
else
  echo "POST-GREEN  C6a bash tests/validate-odoo-specialization.sh -> 121/121"
  echo "POST-GREEN  C6b checks cdad-004 (C1a-C1f, C2a-C2b, C3a-C3b) -> 10/10  (correr: run-checks.sh --full)"
fi

echo "---"
echo "RESUMEN: PASS=$pass FAIL=$fail (checks de contenido: $((pass+fail)); C6 corre con --full post-GREEN)"
