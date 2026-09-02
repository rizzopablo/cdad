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

frontmatter() {
  # frontmatter <archivo> — imprime el bloque ---...--- (sin los delimitadores)
  awk 'BEGIN{c=0} /^---/{c++; next} c==1 {print}' "$1"
}

bash_section() {
  # bash_section <archivo> — imprime SOLO la sección 'bash:' del frontmatter
  frontmatter "$1" | awk '/^[[:space:]]*bash:[[:space:]]*$/ {on=1; print; next} on'
}

assert_string_not_has() {
  # assert_string_not_has <contenido> <patrón-grep> <mensaje>
  if [[ -n "$1" ]] && ! printf '%s' "$1" | grep -Eq -e "$2"; then
    pass "$3 (no contiene '$2')"
  else
    fail "$3 (contiene '$2', no permitido)"
  fi
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

echo
echo "############################################"
echo "# F009 — bash allowlist calibrada (B1, M3, M4)"
echo "############################################"

# test-writer/implementer (genérico + odoo): ya NO bash:{"*":allow}; sí
# allowlist con git commit propio (contrato §5: "escriben y commitean su
# propio artefacto") y SIN comandos de lectura de contenido (cat/head/tail/rg)
# que son el vector real de fuga hacia src/** o tests/**.
for f in agents/cdad-test-writer.md agents/cdad-implementer.md \
         agents/cdad-test-writer-odoo.md agents/cdad-implementer-odoo.md; do
  # (comentarios de línea del bloque se descartan: pueden citar "*": allow
  # en prosa explicando qué se removió, sin que eso sea el valor efectivo)
  b="$(bash_section "$ROOT/$f" 2>/dev/null | grep -v '^[[:space:]]*#' || true)"
  if [[ -n "$b" ]] && printf '%s' "$b" | grep -Eq -e '"\*":[[:space:]]*allow'; then
    fail "F009: $f: bash sigue en \"*\": allow (fuga sin cerrar)"
  else
    pass "F009: $f: bash NO tiene \"*\": allow"
  fi
  assert_string_not_has "$b" '"cat \*":[[:space:]]*allow' \
    "F009: $f: bash no permite 'cat *' (lectura de contenido arbitraria)"
  assert_string_not_has "$b" '"head \*":[[:space:]]*allow' \
    "F009: $f: bash no permite 'head *'"
  assert_string_not_has "$b" '"tail \*":[[:space:]]*allow' \
    "F009: $f: bash no permite 'tail *'"
  assert_file_has "$f" '"git commit\*?":[[:space:]]*allow|"git add' \
    "F009: $f: preserva git commit/add (contrato §5, roles write-capable comitean su artefacto)"
done

# architect/reviewer/scribe — variantes odoo: ya NO "git *": allow (AP-17:
# un rol read-only no debe poder commitear/pushear/resetear).
for f in agents/cdad-architect-odoo.md agents/cdad-reviewer-odoo.md agents/cdad-scribe-odoo.md; do
  assert_string_not_has "$(bash_section "$ROOT/$f" 2>/dev/null || true)" '"git \*":[[:space:]]*allow' \
    "F009: $f: bash NO tiene 'git *': allow sin acotar (AP-17)"
  assert_file_has "$f" '"git diff\*?":[[:space:]]*allow' \
    "F009: $f: preserva git diff (inspección no-mutante)"
done

# architect/reviewer/scribe — genéricos: allowlist agnóstica de lenguaje
# (M3: eran Go-only — go test/go vet/go build/gofmt — inutilizable en
# cualquier proyecto no-Go).
for f in agents/cdad-architect.md agents/cdad-reviewer.md agents/cdad-scribe.md; do
  assert_string_not_has "$(bash_section "$ROOT/$f" 2>/dev/null || true)" 'go test\*' \
    "F009: $f: allowlist de bash ya no es Go-only"
  assert_file_has "$f" '"make \*":[[:space:]]*allow' \
    "F009: $f: allowlist agnóstica incluye 'make *' (convención AGENTS.md de la metodología)"
done

# Claude Code: hook Bash para test-writer/implementer (B1 — el hook actual
# solo matchea Read|Grep|Glob y Edit|Write; Bash queda sin cubrir).
assert_file_has "agents/claude-code/cdad-test-writer.md" 'matcher:[[:space:]]*Bash' \
  "F009: cdad-test-writer (Claude Code) tiene hook PreToolUse con matcher Bash"
assert_file_has "agents/claude-code/cdad-implementer.md" 'matcher:[[:space:]]*Bash' \
  "F009: cdad-implementer (Claude Code) tiene hook PreToolUse con matcher Bash"

# path-guard.sh: nuevo modo de guarda de contenido vía bash + fix del
# fail-open de relativize() para rutas absolutas fuera de $PWD.
assert_file_has "scripts/claude-code-path-guard.sh" 'bash-content-guard|BASH_CONTENT' \
  "F009: path-guard.sh implementa un modo de guarda para Bash"
assert_file_has "scripts/claude-code-path-guard.sh" 'HOME.*fuera del proyecto|fuera de \$PWD|outside.*PWD|no relativiza' \
  "F009: path-guard.sh documenta o corrige el fail-open de rutas absolutas externas"

echo
echo "############################################"
echo "# F010 — higiene de agentes (M2, M6, M7, M8)"
echo "############################################"

# M2: el scribe de Claude Code apuntaba a docs/memory-bank.md (no existe en
# la convención — el Memory Bank real es activeContext.md/progress.md/adr/).
assert_file_not_has "agents/claude-code/cdad-scribe.md" 'docs/memory-bank\.md' \
  "F010 (M2): cdad-scribe (Claude Code) ya no referencia docs/memory-bank.md"
assert_file_has "agents/claude-code/cdad-scribe.md" 'activeContext\.md' \
  "F010 (M2): cdad-scribe (Claude Code) referencia activeContext.md (Memory Bank real)"

# M6: API inventada (from Agent import agent) + cita de AP-7 mal apuntada
# (AP-7 es "Memory Bank desactualizado"; el invariante de aislamiento es
# AP-1/AP-2).
assert_file_not_has "skills/cdad-cycle/references/claude-code-delegation.md" \
  'from Agent import agent' \
  "F010 (M6): claude-code-delegation.md ya no tiene la API Python inventada"
assert_file_not_has "skills/cdad-cycle/references/claude-code-delegation.md" \
  '\(AP-7' \
  "F010 (M6): claude-code-delegation.md ya no cita AP-7 para el invariante de aislamiento (es AP-1/AP-2)"

# M7: los 4 skills/*.md sueltos quedan como stub de una línea (o se borran);
# en cualquier caso, no pueden seguir siendo una copia divergente completa.
for f in skills/handoff-prompts.md skills/re-entry.md skills/feature-handoff.md skills/epic-planning.md; do
  if [[ -f "$ROOT/$f" ]]; then
    lines="$(wc -l < "$ROOT/$f" | tr -d ' ')"
    if [[ "$lines" -le 10 ]]; then
      pass "F010 (M7): $f es un stub corto (≤10 líneas) o fue removido"
    else
      fail "F010 (M7): $f sigue siendo una copia completa ($lines líneas) — trampa de lectura"
    fi
  else
    pass "F010 (M7): $f fue removido"
  fi
done

# M8: contexto privado (pipeline arXiv, fb-012, guard-event-log, nombre del
# dueño) fuera de un skill distribuible.
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'mi pipeline arXiv' \
  "F010 (M8): verdict-tuple.md sin referencia a 'mi pipeline arXiv'"
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'fb-012' \
  "F010 (M8): verdict-tuple.md sin referencia a 'fb-012'"
assert_file_not_has "skills/cdad-cycle/references/verdict-tuple.md" 'aprobación de Pablo' \
  "F010 (M8): verdict-tuple.md sin nombre propio del dueño"

echo
echo "############################################"
echo "# F001 — nota de perfiles honesta + drift del bloque §2 (B7)"
echo "############################################"

# La nota de perfiles menciona los 4 perfiles reales (faltaba --basic) y
# caveatea el invariante anti-bias para el perfil que lo suspende.
for f in skills/cdad-cycle/SKILL.md agents/cdad-orchestrator.md agents/claude-code/cdad-orchestrator.md; do
  assert_file_has "$f" '\-\-basic' "F001: $f menciona el perfil --basic en el switch"
  assert_file_has "$f" 'basic.*[Nn][Oo] est[aá] garantizado|basic.*suspendid|salvo.*basic|excepto.*basic' \
    "F001: $f caveatea el invariante anti-bias para el perfil basic"
done

# El bloque §2 (Contrato de roles + nota de perfiles) sigue siendo
# INTENCIONALMENTE idéntico entre los 3 archivos (ADR-007: "La identidad del
# bloque §2 (SKILL ↔ orquestador) con la nota de perfiles se verificó
# byte-idéntica" — verificado a mano en su momento, nunca automatizado). Este
# assert es la automatización que faltaba: extrae desde "### 2. Contrato de
# cada rol" hasta la línea de "Switch:" inclusive, y compara.
extract_role_contract() {
  awk '/^### 2\. Contrato de cada rol/{f=1} f{print; if ($0 ~ /^Modelos del diseño/) exit}' "$ROOT/$1"
}
extract_role_contract "skills/cdad-cycle/SKILL.md" > /tmp/rc_skill.$$ 2>/dev/null
extract_role_contract "agents/cdad-orchestrator.md" > /tmp/rc_oc.$$ 2>/dev/null
extract_role_contract "agents/claude-code/cdad-orchestrator.md" > /tmp/rc_cc.$$ 2>/dev/null
if diff -q /tmp/rc_skill.$$ /tmp/rc_oc.$$ >/dev/null 2>&1 && diff -q /tmp/rc_skill.$$ /tmp/rc_cc.$$ >/dev/null 2>&1; then
  pass "F001: bloque §2 (Contrato de roles + nota de perfiles) idéntico en SKILL.md y los 2 orquestadores"
else
  fail "F001: bloque §2 DIVERGE entre SKILL.md y los orquestadores (ver diff)"
fi
rm -f /tmp/rc_skill.$$ /tmp/rc_oc.$$ /tmp/rc_cc.$$

echo
echo "############################################"
echo "# F003 — gates SKILL.md ↔ stage-N sincronizados + B11"
echo "############################################"

# Gate 2→3: SKILL.md incluye el ítem de plan.md que antes solo tenía stage-2.
assert_file_has "skills/cdad-cycle/SKILL.md" 'plan\.md.*existe.*auto-revisión|Si el spec es complejo' \
  "F003: Gate 2→3 de SKILL.md incluye el ítem de plan.md (antes solo en stage-2)"

# Gate 3→4: stage-3-tdd.md incluye los 2 ítems que antes solo tenía SKILL.md.
assert_file_has "skills/cdad-cycle/references/stage-3-tdd.md" 'Test Audit completado y aprobado' \
  "F003: Gate 3→4 de stage-3-tdd.md incluye 'Test Audit completado y aprobado' (antes solo en SKILL.md)"
assert_file_has "skills/cdad-cycle/references/stage-3-tdd.md" 'justificación explícita en spec\.md' \
  "F003: Gate 3→4 de stage-3-tdd.md incluye 'justificación explícita en spec.md' (antes solo en SKILL.md)"

# Gate 5→done: carve-out de CI en stage-5-merge.md + "Feature mergeada" en SKILL.md.
assert_file_has "skills/cdad-cycle/references/stage-5-merge.md" 'Si NO hay CI configurado' \
  "F003: Gate 5→done de stage-5-merge.md incluye el carve-out de CI (antes solo en SKILL.md)"
assert_file_has "skills/cdad-cycle/SKILL.md" 'Feature mergeada' \
  "F003: Gate 5→done de SKILL.md incluye 'Feature mergeada' (antes solo en stage-5-merge.md)"

# B11: el gate 4→5 ya no contradice la excepción de delegación explícita que
# el propio archivo documenta (Capa 2 / §2.3).
for f in skills/cdad-cycle/SKILL.md skills/cdad-cycle/references/stage-4-review.md; do
  assert_file_not_has "$f" '\[ \] Usuario aprobó priorización \(no delegado al LLM\)\.' \
    "F003 (B11): $f ya no tiene la redacción absoluta del gate 4→5"
  assert_file_has "$f" 'agente-delegada con pedido explícito' \
    "F003 (B11): $f menciona la excepción de delegación explícita en el gate"
done
assert_file_not_has "skills/cdad-cycle/references/stage-2-specification.md" \
  '\*\*AP-10\*\*: delegar la aprobación al LLM\. Indelegable\.' \
  "F003 (B11): AP-10 corto en stage-2 ya no es absoluto sin la excepción"

echo
echo "############################################"
echo "# F007 — orquestador Claude Code reparado (B6)"
echo "############################################"

CCO="agents/claude-code/cdad-orchestrator.md"
assert_file_has "$CCO" 'con la herramienta' \
  "F007: $CCO instruye delegar vía herramienta (no task/delegate)"
assert_file_has "$CCO" 'Agent.{0,10}subagent_type' \
  "F007: $CCO menciona la herramienta Agent con subagent_type"
assert_file_not_has "$CCO" 'vía\s*\n?\s*`delegate`; roles write-capable' \
  "F007: $CCO ya no instruye 'delegate' como mecanismo de invocación por rol"
assert_file_has "$CCO" 'resolvé el sufijo de' \
  "F007: $CCO resuelve el sufijo de stack antes de delegar (paridad con OpenCode)"
assert_file_has "$CCO" 'cdad-<rol>-<stack>' \
  "F007: $CCO menciona el patrón cdad-<rol>-<stack> para variantes especializadas"

echo
echo "############################################"
echo "# F008 — guard anti-bias también para cdad_model_claude (B2)"
echo "############################################"

# shellcheck source=scripts/cdad-models.sh
source "$ROOT/scripts/cdad-models.sh"
for p in economical optimus premium; do
  r="$(cdad_model_claude "$p" reviewer)"
  i="$(cdad_model_claude "$p" implementer)"
  if [[ -n "$r" && -n "$i" && "$r" != "$i" ]]; then
    pass "F008: cdad_model_claude perfil '$p' — reviewer ($r) != implementer ($i)"
  else
    fail "F008: cdad_model_claude perfil '$p' — reviewer ($r) == implementer ($i), viola anti-bias"
  fi
done

assert_file_has "scripts/validate-subagents.sh" 'cdad_model_claude' \
  "F008: validate-subagents.sh evalúa cdad_model_claude (antes solo cdad_model de OpenCode)"

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
