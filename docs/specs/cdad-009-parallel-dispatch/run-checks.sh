#!/usr/bin/env bash
# Checks RED/GREEN cdad-009-parallel-dispatch — corren desde la raíz del repo
# Framework documental: checks de estructura (patrón cdad-004..008).
S3="skills/cdad-cycle/references/stage-3-tdd.md"
SAS="skills/cdad-cycle/references/sub-agent-strategies.md"
SKILL="skills/cdad-cycle/SKILL.md"

# Scope de la sección nueva "Despacho paralelo" (de su encabezado hasta el
# siguiente '## ' — debe insertarse tras el packet ortogonal de Sub-fase 3.1
# y antes de '## Sub-fase 3.2 — GREEN').
PAR="awk '/^## Despacho paralelo/{f=1;next} f&&/^## /{f=0} f' '$S3'"
# Scope de la subsección aditiva en sub-agent-strategies.md (hasta el próximo '## ' o EOF).
SUBPAR="awk '/^### Sesiones paralelas del mismo rol/{f=1;next} f&&/^## /{f=0} f' '$SAS'"

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

echo "=== C1 -> P1: stage-3-tdd.md sección 'Despacho paralelo' (7 piezas) ==="
# Posición: después del packet ortogonal (Sub-fase 3.1) y antes de Sub-fase 3.2.
POS="test \$(grep -n '^## Despacho paralelo' '$S3' | cut -d: -f1) -gt \$(grep -n 'paths de c(ó|o)digo independiente' '$S3' | cut -d: -f1) && test \$(grep -n '^## Despacho paralelo' '$S3' | cut -d: -f1) -lt \$(grep -n '^## Sub-fase 3.2' '$S3' | cut -d: -f1)"
t C1a "P1a: encabezado '## Despacho paralelo' + ubicado tras el packet ortogonal (Sub-fase 3.1) y antes de Sub-fase 3.2 + árbol de decisión (2+ tareas genuinamente independientes -> paralelo)" "test -f '$S3' && grep -qE '^## Despacho paralelo' '$S3' && $POS && $PAR | grep -qiE 'genuinamente independiente' && $PAR | grep -qiE '2\+|dos o m(á|a)s'"

t C1b "P1b: árbol — comparten archivo/estado -> secuencial o wave dispatch; el packet ortogonal para UN test-writer sigue siendo el default" "$PAR | grep -qiE 'estado compartido|archivos en com(ú|u)n' && $PAR | grep -qi 'secuencial' && $PAR | grep -qiE 'wave dispatch' && $PAR | grep -qiE 'default' && $PAR | grep -qiE 'ortogonal'"

t C1c "P1c: precondición — paralelismo seguro requiere contrato de interfaz (Consumes/Produces del plan, ver stage-2 'Planning de features complejas'); sin él no hay despacho paralelo" "$PAR | grep -q 'Consumes' && $PAR | grep -q 'Produces' && $PAR | grep -qiE 'contrato de interfaz' && $PAR | grep -q 'Planning de features complejas' && $PAR | grep -qiE 'sin (él|el)|no hay despacho paralelo|no hay paralelismo'"

t C1d "P1d: reglas de despacho — prompt autocontenido por sesión (regla §6) con owned files + do-not-touch list; scope disjunto verificado (git diff --name-only); mismo rol, sesiones distintas, cada sesión no ve el trabajo de las otras" "$PAR | grep -qiE 'autocontenido' && $PAR | grep -q 'owned files' && $PAR | grep -qiE 'do-not-touch' && $PAR | grep -qF 'git diff --name-only' && $PAR | grep -qiE 'mismo rol' && $PAR | grep -qiE 'no ve (el trabajo|lo que)|sin ver el trabajo'"

t C1e "P1e: integración final SOLO del orquestador — revisar cada resumen -> overlap de archivos (git diff --name-only + comm) -> suite COMPLETA una vez al final; conflictos los resuelve el orquestador, nunca los subagentes" "$PAR | grep -qiE 'orquestador' && $PAR | grep -qiE 'resumen' && $PAR | grep -qF 'git diff --name-only' && $PAR | grep -q 'comm' && $PAR | grep -qiE 'suite COMPLETA|suite completa' && $PAR | grep -qiE 'nunca los subagentes'"

t C1f "P1f: state file — SOLO el orquestador lo escribe, siempre; las sesiones paralelas nunca lo tocan (regla explícita)" "$PAR | grep -qiE 'SOLO el orquestador|solo el orquestador' && $PAR | grep -qiE 'state file' && $PAR | grep -qiE 'nunca lo tocan|nunca lo toca|jam(á|a)s lo tocan'"

t C1g "P1g: wave dispatch como default conservador + worktree-per-agent como opción documentada (cita §5.6 cleanup por provenance) + tabla anti-racionalización (4-6 filas)" "$PAR | grep -qiE 'default conservador' && $PAR | grep -qiE 'worktree' && $PAR | grep -qE '5\.6' && $PAR | grep -qiE 'provenance' && $PAR | grep -qiE 'anti-racionalizaci(ó|o)n' && $PAR | grep -qiE 'sesi(ó|o)n de fix' && $PAR | grep -qiE 'resumen del agente'"

echo "=== C2 -> P2: sub-agent-strategies.md subsección aditiva 'Sesiones paralelas del mismo rol' ==="
t C2a "P2a: subsección existe + aislamiento se mantiene (cada sesión sin ver trabajo ajeno) + el orquestador despacha y consolida" "test -f '$SAS' && grep -qE '^### Sesiones paralelas del mismo rol' '$SAS' && $SUBPAR | grep -qiE 'aislamiento' && $SUBPAR | grep -qiE 'orquestador' && $SUBPAR | grep -qiE 'consolida|despacha'"
t C2b "P2b: la subsección establece que el state file solo lo escribe el orquestador" "$SUBPAR | grep -qiE 'state file' && $SUBPAR | grep -qiE 'orquestador' && $SUBPAR | grep -qiE 'SOLO el orquestador|solo el orquestador|únic|unico|nunca lo tocan'"

echo "=== C3 -> P3: SKILL.md tabla de lectura (decisión del audit: la fila agrupada stage-1..stage-5 ya cubre stage-3-tdd.md; NO requiere fila nueva — P3 se valida por presencia de la sección en stage-3, chequeada en C1a) ==="
t C3a "P3: la tabla de lectura de SKILL.md cubre stage-3-tdd.md vía la fila agrupada (guard, PASS hoy)" "test -f '$SKILL' && grep -qE 'stage-1-discovery\.md.*\.\.\..*stage-5-merge\.md' '$SKILL'"
t C3b "P3 no-expansión: SKILL.md NO duplica la sección (sin encabezado propio de despacho paralelo)" "test -f '$SKILL' && ! grep -qE '^#+ .*Despacho paralelo' '$SKILL'"

echo "=== C4 -> GUARD: packet ortogonal + encabezados existentes + regla §6 intactos (PASS hoy) ==="
t C4a "stage-3: packet ortogonal intacto ('paths de código independientes que no se pisan', Sub-fase 3.1)" "grep -qE 'paths de c(ó|o)digo independiente(s)? que no se pisan' '$S3'"
t C4b "stage-3: encabezados '## Sub-fase 3.2 — GREEN' y '## 🛑 Gate de salida (Etapa 3 → Etapa 4)' intactos" "grep -qE '^## Sub-fase 3\.2 — GREEN' '$S3' && grep -q '## 🛑 Gate de salida (Etapa 3' '$S3'"
t C4c "sub-agent-strategies: 4 encabezados existentes intactos (Por qué importa / Estrategia por entorno / Permisos por rol — cheatsheet / Activación por stack)" "grep -qE '^## Por qu(é|e) importa' '$SAS' && grep -qE '^## Estrategia por entorno' '$SAS' && grep -qE '^## Permisos por rol — cheatsheet' '$SAS' && grep -qE '^## Activaci(ó|o)n por stack' '$SAS'"
t C4d "SKILL.md: regla §6 de state-passing intacta ('### 6. Regla de state-passing' + 'No asumas que recuerda nada')" "grep -qE '^### 6\. Regla de state-passing' '$SKILL' && grep -q 'No asumas que' '$SKILL'"

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
  echo "--- C5e: checks cdad-008 ---"
  bash docs/specs/cdad-008-granular-planning/run-checks.sh 2>&1 | tail -1
else
  echo "POST-GREEN  C5a bash tests/validate-odoo-specialization.sh -> 121/121"
  echo "POST-GREEN  C5b checks cdad-005 -> 23/23"
  echo "POST-GREEN  C5c checks cdad-006 -> 19/19"
  echo "POST-GREEN  C5d checks cdad-007 -> 23/23"
  echo "POST-GREEN  C5e checks cdad-008 -> 17/17  (correr: run-checks.sh --full)"
fi

echo "---"
echo "RESUMEN: PASS=$pass FAIL=$fail (checks de contenido + guard: $((pass+fail)); C5 corre con --full post-GREEN)"
