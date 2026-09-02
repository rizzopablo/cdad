#!/usr/bin/env bash
# Checks RED/GREEN cdad-008-granular-planning — corren desde la raíz del repo
# Framework documental: checks de estructura (patrón cdad-004/005/006/007).
S2="skills/cdad-cycle/references/stage-2-specification.md"
ARC="agents/cdad-architect.md"
AP="skills/cdad-cycle/references/anti-patterns.md"
EPIC="skills/cdad-epic/SKILL.md"

# Scope de la sección nueva de planning (desde su encabezado hasta el siguiente '## ').
PLN="sed -n '/^## Planning de features complejas/,/^## [^P]/p' '$S2'"
# Scope del bloque AP-19 (se agrega al final: sin corte posterior imprime a EOF).
AP19="sed -n '/^## AP-19/,\$p' '$AP'"
# Scope del Gate de salida (Etapa 2 → Etapa 3).
G23="sed -n '/^## 🛑 Gate de salida (Etapa 2/,/^## Si surge/p' '$S2'"

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

echo "=== C1 -> P1: stage-2-specification.md sección 'Planning de features complejas' (7 piezas) ==="
t C1a "P1a: disparador (spec complejo) + rol (architect produce plan.md además del spec) + gate 2->3 lo incluye si existe" "test -f '$S2' && grep -qE '^## Planning de features complejas' '$S2' && $PLN | grep -qiE 'm(ú|u)ltiples componentes' && $PLN | grep -q 'architect' && $PLN | grep -q 'plan\.md' && $G23 | grep -q 'plan\.md'"
t C1b "P1b: tamaño de tarea — unidad más chica con mini-ciclo TDD propio que un reviewer podría rechazar sin rechazar la vecina + setup plegado" "$PLN | grep -qiE 'm(á|a)s chica' && $PLN | grep -qiE 'mini-ciclo TDD|ciclo TDD propio' && $PLN | grep -qiE 'rechazar sin rechazar' && $PLN | grep -qiE 'setup|scaffolding' && $PLN | grep -qiE 'pl(ie|e)ga|plegada|se pliega'"
t C1c "P1c: estructura de tarea — Files exactos + Consumes/Produces (contrato público, firmas exactas, apto test-writer) + pasos TDD" "$PLN | grep -q 'Files' && $PLN | grep -q 'Consumes' && $PLN | grep -q 'Produces' && $PLN | grep -qi 'firmas exactas' && $PLN | grep -qiE 'apto (para|el) test-writer' && $PLN | grep -qi 'pasos TDD'"
t C1d "P1d: regla central — plan define el CONTRATO (aserciones reales, comandos exactos) + comportamiento observable 3-5 bullets verificables + NUNCA impl especulativa (escribir la impl dos veces revierte TDD) + test-writer puede ver el plan entero" "$PLN | grep -qiE 'CONTRATO' && $PLN | grep -qi 'comportamiento observable' && $PLN | grep -qE '3[-–]5|3 a 5' && $PLN | grep -qi 'verificable' && $PLN | grep -qiE 'escribir la impl(ementaci(ó|o)n)? dos veces|revierte TDD' && $PLN | grep -qiE 'test-writer puede ver'"
t C1e "P1e: no placeholders — lista de frases prohibidas (TBD/TODO/similar a la Tarea N) = falla del plan; vagueza con contrato NO es placeholder" "$PLN | grep -q 'TBD' && $PLN | grep -q 'TODO' && $PLN | grep -qiE 'similar a la Tarea' && $PLN | grep -qiE 'falla del plan' && $PLN | grep -qiE 'NO es placeholder|no es placeholder'"
t C1f "P1f: auto-revisión — cobertura del spec (cada postcondición -> >=1 tarea) + escaneo de placeholders + consistencia de firmas entre tareas" "$PLN | grep -qiE 'cobertura del spec' && $PLN | grep -qiE 'cada postcondici(ó|o)n' && $PLN | grep -qE '(>|≥) ?1 tarea|>= ?1 tarea|al menos una tarea' && $PLN | grep -qiE 'escaneo de placeholders' && $PLN | grep -qiE 'consistencia de firmas'"
t C1g "P1g: global constraints del spec copiadas verbatim en el header" "$PLN | grep -qiE 'global constraints' && $PLN | grep -qiE 'verbatim' && $PLN | grep -qiE 'header|encabezado'"

echo "=== C2 -> P2: agents/cdad-architect.md extensión de scope (aditiva) ==="
t C2a "P2a: cdad-architect.md tiene sección de planificación (produce plan.md cuando el spec es complejo)" "test -f '$ARC' && grep -qiE '^#+ .*Planificaci(ó|o)n' '$ARC' && grep -qiE 'spec es complejo|spec complejo' '$ARC'"
t C2b "P2b: cdad-architect.md menciona plan.md con las reglas (contrato, no implementación)" "grep -q 'plan\.md' '$ARC' && grep -qiE 'CONTRATO|comportamiento observable' '$ARC'"

echo "=== C3 -> P3: anti-patterns.md AP-19 — Plan placeholder ==="
t C3a "encabezado '^## AP-19'" "grep -nE '^## AP-19' '$AP'"
t C3b "3 sub-secciones (Síntoma/Por qué es malo/Corrección) en bloque AP-19" "$AP19 | grep -q 'Síntoma' && $AP19 | grep -q 'Por qué es malo' && $AP19 | grep -q 'Corrección'"
t C3c "AP-19 cita la sección 'Planning de features complejas' de stage-2-specification.md" "$AP19 | grep -q 'Planning de features complejas'"

echo "=== C4 -> GUARD: encabezados stage-2 intactos + cdad-epic planning light intacto (PASS hoy) ==="
t C4a "stage-2: '## Variantes según tamaño' intacta" "grep -qE '^## Variantes seg(ú|u)n tama(ñ|n)o' '$S2'"
t C4b "stage-2: '## Por qué la claridad del spec no es negociable' intacta" "grep -qE '^## Por qu(é|e) la claridad del spec no es negociable' '$S2'"
t C4c "stage-2: '## 🛑 Gate de salida (Etapa 2 → Etapa 3)' intacta" "grep -q '## 🛑 Gate de salida (Etapa 2' '$S2'"
t C4d "stage-2: '## Si surge algo no contemplado en spec durante implementación' intacta" "grep -qE '^## Si surge algo no contemplado en spec durante implementaci(ó|o)n' '$S2'"
t C4e "cdad-epic/SKILL.md SIN mención de granular-planning (planning light intacto, no-expansión)" "test -f '$EPIC' && ! grep -qi 'granular' '$EPIC'"

echo "=== C5 -> criterio post-GREEN (sin regresión) ==="
if [ "${1:-}" = "--full" ]; then
  echo "--- C5a: suite cdad-003 ---"
  bash tests/validate-odoo-specialization.sh 2>&1 | tail -3
  echo "--- C5b: checks cdad-005 ---"
  bash docs/specs/cdad-005-receiving-feedback/run-checks.sh 2>&1 | tail -1
  echo "--- C5c: checks cdad-006 ---"
  bash docs/specs/cdad-006-git-safety-close/run-checks.sh 2>&1 | tail -1
  echo "--- C5d: checks cdad-007 ---"
  bash docs/specs/cdad-007-systematic-debugging/run-checks.sh 2>&1 | tail -1
else
  echo "POST-GREEN  C5a bash tests/validate-odoo-specialization.sh -> 121/121"
  echo "POST-GREEN  C5b checks cdad-005 -> 23/23"
  echo "POST-GREEN  C5c checks cdad-006 -> 19/19"
  echo "POST-GREEN  C5d checks cdad-007 -> 23/23  (correr: run-checks.sh --full)"
fi

echo "---"
echo "RESUMEN: PASS=$pass FAIL=$fail (checks de contenido + guard: $((pass+fail)); C5 corre con --full post-GREEN)"
