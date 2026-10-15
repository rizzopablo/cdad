# RED report — 005-004-claude-code-roles / T1 (test-writer, etapa 3)

- Paquete: `005-004-claude-code-roles-test-writer-red-001` (rol test-writer, subetapa `red`).
- Contrato: `docs/specs/005-004-claude-code-roles/spec.md` (sha256 `79d57e0a…`, PD-1 §3 / AC-1 §5) + `plan.md` (sha256 `f7c61a59…`, ficha T1).
- Commit de los tests: `34703b611e1ac14753cc11b25702c7fcd850a7a2` (`test: 005-004 T1 RED — …`).
- Write scope respetado: sólo `tests/`. No se editó implementación.

## 1. Archivos modificados

| Archivo | Tipo |
|---|---|
| `tests/test_005_004_t1_dispatch_tool_name.py` | nuevo (focal declarado por el paquete) — 347 líneas |
| `tests/validate-consistency.sh` | modificado: bloque nuevo `005-004 T1 … (PD-1/AC-1)` (+31 líneas, 0 borradas) |

`git diff --stat` acotado (el commit contiene exactamente esos dos paths):

```
 tests/test_005_004_t1_dispatch_tool_name.py | 347 ++++++++++++++++++++++++++++
 tests/validate-consistency.sh               |  31 +++
 2 files changed, 378 insertions(+)
```

No commiteado por mí (no es mío, pre-existente al despacho): `docs/.cdad-state.json` aparece `M` en `git status --short` porque el orquestador registró el despacho de este paquete (`active_packet` → `…-test-writer-red-001`, `status: dispatched`). Fuera de mi write scope: no lo toqué.

## 2. Mapa test → postcondición / criterio (un test por afirmación observable)

| Test (`tests/test_005_004_t1_dispatch_tool_name.py`) | PD / criterio | Estado hoy |
|---|---|---|
| `test_pd1_i_cc_orchestrator_declares_agent_dispatch_tool` | PD-1(i) / AC-1 | **ROJO** (AssertionError: el derivado CC del orchestrator no declara `Agent`; declara `Task`) |
| `test_pd1_ii_no_cc_agent_declares_task_as_dispatch_tool` | PD-1(ii) / AC-1 | **ROJO** (AssertionError: `cdad-orchestrator.md` declara `Task`) |
| `test_pd1_ii_opencode_side_keeps_its_tool_name` | PD-1 / AC-1 (control) | verde |
| `test_pd1_iii_adapter_owns_the_cc_dispatch_tool_name` | PD-1(iii) / AC-1 | **ROJO** (AssertionError: el adaptador CC declara `Task`) |
| `test_pd1_iii_reference_and_skill_name_the_same_tool` | PD-1(iii) / AC-1 | verde (conservación: ya nombran `Agent`) |
| `test_pd1_iv_generator_staging_is_idempotent` | PD-1(iv) / INV-2, INV-4 | verde |
| `test_pd1_iv_ten_cc_agents_keep_their_tools_lines` | PD-1(iv) / INV-4 (control) | verde |

Aserciones equivalentes en el validador del repo (superficie de tests, PD-1(ii)):

| Aserción en `tests/validate-consistency.sh` | PD / criterio | Estado hoy |
|---|---|---|
| `assert_cc_no_task_dispatch_tool` sobre las 11 salidas `agents/claude-code/cdad-*.md` | PD-1(ii) / AC-1 | **ROJO** sólo en `cdad-orchestrator.md` (10 PASS) |
| `the CC orchestrator declares the real dispatch tool 'Agent'` | PD-1(i) / AC-1 | **ROJO** (`tools:` del orchestrator sin `Agent`) |
| `the OpenCode side keeps its own dispatch tool name` | PD-1 / AC-1 (control) | verde |

Nota de método (anti-gaming): el oráculo se derivó del contrato (spec §2/§3 PD-1(i)-(iv) y §5 AC-1 + ficha T1 del plan), **no** de la implementación. No se leyeron `scripts/`, `sources/` ni `skills/` al escribir los tests. Sí se leen al ejecutarse los artefactos **generados** `agents/claude-code/**` (salida declarada del generador, `Makefile:1-6`; `invariante`: `agents/` no se edita a mano) y las superficies que PD-1(iii) nombra por ruta (`sources/agents/adapters/claude-code.md`, `references/claude-code-delegation.md`, `SKILL.md`, `references/opencode-delegation.md`). La tabla congelada «como hoy» de las líneas `tools:` de los diez agentes con/sin guard se **reusa por import** desde `tests/test_packet_prepare.py` (`EDIT_TOOLS`/`READ_ONLY_TOOLS`/`EXPECTED_GUARDS`), sin duplicarla (PD-9).

## 3. Comandos exactos y salida

### 3.1 Focal (RED)

```
python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py -q
```

```
FF.F...                                                                  [100%]
=================================== FAILURES ===================================
…/tests/test_005_004_t1_dispatch_tool_name.py:174: AssertionError: PD-1(i)/AC-1: el derivado de Claude Code del orchestrator no declara 'Agent' como herramienta de despacho (declara: ['Bash', 'Edit', 'Glob', 'Grep', 'Read', 'Skill', 'Task', 'Write'])
…/tests/test_005_004_t1_dispatch_tool_name.py:210: AssertionError: PD-1(ii)/AC-1: agentes de Claude Code que declaran 'Task' como herramienta de despacho: ['cdad-orchestrator.md'] (la real observada es 'Agent')
…/tests/test_005_004_t1_dispatch_tool_name.py:241: AssertionError: PD-1(iii)/AC-1: el adaptador fuente (sources/agents/adapters/claude-code.md) declara 'Task' como herramienta de despacho de Claude Code; la herramienta real es 'Agent'

=========================== short test summary info ============================
FAILED tests/test_005_004_t1_dispatch_tool_name.py::test_pd1_i_cc_orchestrator_declares_agent_dispatch_tool
FAILED tests/test_005_004_t1_dispatch_tool_name.py::test_pd1_ii_no_cc_agent_declares_task_as_dispatch_tool
FAILED tests/test_005_004_t1_dispatch_tool_name.py::test_pd1_iii_adapter_owns_the_cc_dispatch_tool_name
3 failed, 4 passed in 1.01s
```

**Motivo de cada RED (todos AssertionError de comportamiento; ningún ImportError/SyntaxError/NameError):**

1. PD-1(i): el frontmatter generado del orchestrator CC declara la herramienta de despacho como `Task` (`['Bash','Edit','Glob','Grep','Read','Skill','Task','Write']`); falta `Agent` — exactamente el outlier que el contrato declara (§3 PD-1(i): «Hoy el derivado declara `Task`: `agents/claude-code/cdad-orchestrator.md:4`»). La asociación `Agent`↔`subagent_type` del cuerpo ya es cierta.
2. PD-1(ii): de las 11 salidas CC, sólo `cdad-orchestrator.md` declara `Task`; las otras 10 ya están correctas.
3. PD-1(iii): el adaptador fuente (dueño del enunciado) declara `Task` como herramienta de despacho de Claude Code (`Agent` sí aparece, pero la declaración de la herramienta es la vieja) ⇒ la aserción de contenido declarado falla hoy.

### 3.2 Validador del repo (regresión declarada, RED por la aserción nueva)

```
bash tests/validate-consistency.sh
```

Bloque nuevo + resumen:

```
# 005-004 T1 — Claude Code declares the real dispatch tool (PD-1/AC-1)
PASS: 005-004 PD-1: agents/claude-code/cdad-architect.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-architect-odoo.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-implementer.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-implementer-odoo.md does not declare 'Task' as a dispatch tool
FAIL: 005-004 PD-1: agents/claude-code/cdad-orchestrator.md declares 'Task' as a dispatch tool (the real one is 'Agent')
PASS: 005-004 PD-1: agents/claude-code/cdad-reviewer.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-reviewer-odoo.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-scribe.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-scribe-odoo.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-test-writer.md does not declare 'Task' as a dispatch tool
PASS: 005-004 PD-1: agents/claude-code/cdad-test-writer-odoo.md does not declare 'Task' as a dispatch tool
FAIL: 005-004 PD-1: the CC orchestrator declares the real dispatch tool 'Agent' (agents/claude-code/cdad-orchestrator.md does NOT contain '^tools:.*\bAgent\b')
PASS: 005-004 PD-1 (control): the OpenCode side keeps its own dispatch tool name (skills/cdad-cycle/references/opencode-delegation.md contains '\bTask\b')
Assert PASS: 152
Assert FAIL: 4
FAIL: 4 assert(s) failed.
```

De los 4 FAIL: **2 son la aserción nueva** (transición RED→GREEN esperada de T1: se pondrán verdes con el `cc_tools`/adaptador corregidos y `make agents`) y **2 son pre-existentes** (ver §5).

### 3.3 Regresiones declaradas (verdes)

```
python3 -m pytest tests/test_packet_prepare.py tests/test_cdad_generate.py tests/test_003_006_t3_receive_wiring.py tests/test_003_007_t4_atomic_unit_rule.py -q
```

```
......................................................                   [100%]
54 passed in 22.79s
```

## 4. Qué verifica cada control verde (no-regresión)

- **OpenCode conserva su nombre:** `references/opencode-delegation.md` sigue nombrando `Task` (el cambio de T1 es sólo del lado CC) — verde hoy y en el validador.
- **Idempotencia + paridad (PD-1(iv), INV-2/INV-4):** el generador corrido dos veces sobre el mismo staging no cambia bytes (`set(first) == set(second)` y hashes iguales) y los derivados del repo son byte-idénticos a la salida del generador (`agents/claude-code/**`, 11 archivos). Comando interno del test: `python3 scripts/cdad-generate.py --runtime claude-code --stack odoo --profile optimus --out <tmp>` (dos corridas). Se usó el **generador de staging** — opción que el encargo admite expresamente («`make agents` (o el generador de staging)»): `make agents` escribiría en `agents/`, fuera de mi write scope.
- **Diez agentes con/sin guard (PD-1(iv)):** las líneas `tools:` de `cdad-{architect,architect-odoo,reviewer,reviewer-odoo,scribe,scribe-odoo,implementer,implementer-odoo,test-writer,test-writer-odoo}.md` siguen exactamente `Read, Grep, Glob, Bash, Skill` / `Read, Grep, Glob, Bash, Edit, Write, Skill` (tabla congelada del repo, reusada por import).

## 5. Bloqueos / límites honestos (declarados, no silenciosos)

1. **FAILs pre-existentes del validador (no atribuibles a T1).** `F011: scripts/validate-subagents.sh → FAIL` y `F011: tests/validate-odoo-specialization.sh → FAIL` (A3 sanitización: encuentra patrones sensibles en docs pre-existentes y en `tests/__pycache__`). Verificado **pre-existente**: extraje `HEAD` con `git archive HEAD` a `/tmp/opencode/cdad-head-005004`, copié `tests/.sensitive-patterns.local` (copiado, **nunca leído**) y `bash tests/validate-consistency.sh` ahí da los mismos dos FAIL, ajenos a mis archivos. Mi bloque nuevo corre después de F011 y no los afecta.
2. **`docs/.cdad-state.json` modificado, no por mí** (registro de despacho del orquestador). No lo toqué ni lo commiteé.
3. **`make agents` no se ejecutó** en el repo (habría escrito `agents/`, fuera de `tests/`): la idempotencia/paridad se evidenció con el generador declarado (§4).
4. **Exposición incidental (declarada):** en la **primera** corrida del focal, la introspección de pytest sobre una aserción imprimió un fragmento (~200 caracteres) del bloque de comentario inicial de `sources/agents/adapters/claude-code.md` junto al fallo. No fue una lectura deliberada (el archivo nunca se leyó al escribir el test; el oráculo vino de la spec/plan), no informó ninguna aserción y se corrigió la forma de la aserción (`is False`) para que el log no vuelque contenido de la fuente. No se leyó `scripts/` ni `skills/` en ningún caso.
5. **La suite completa no se corrió** (política del paquete: la corre una vez quien cierra). Sólo focal + regresiones declaradas + validador.
6. **No hay comparación contra la implementación futura:** estos tests verifican comportamiento observable del contrato (nombre declarado de la herramienta, idempotencia/paridad de los derivados, aserción del validador), no plumbing interno; si el GREEN resuelve la declaración de otra forma válida pero introduce una mención nueva de `Task` en el adaptador CC, la aserción PD-1(iii) lo bloqueará y deberá resolverse en el contrato (no se relaja el oráculo desde el rol).

## 6. Evidencia de commit

```
34703b611e1ac14753cc11b25702c7fcd850a7a2
test: 005-004 T1 RED — el derivado de Claude Code del orchestrator declara Agent (PD-1/AC-1)
 tests/test_005_004_t1_dispatch_tool_name.py | 347 ++++++++++++++++++++++++++++
 tests/validate-consistency.sh               |  31 +++
 2 files changed, 378 insertions(+)
```

Sin `--no-verify`, sin push, sin desplegar, sin tocar HOME, sin leer `tests/.sensitive-patterns.local`.
