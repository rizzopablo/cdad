Route C intake validated before working (request/packet `rc=0`, `render --route C` byte-identical to the dispatch identification, `execution.json` `schema_version: 2`, contract sha256 `0d630c49…81abc` matches). No cycle skills loaded. Work done, suite green, committed. FINAL TEXT report:

# Informe del implementer — 010-002 T8, subfase REVIEW-FIX (intento 2)

## Intake (ruta C) — validado antes de trabajar

| Comprobación | Resultado |
|---|---|
| Bloque de identificación único, sin paquete inline ni mezcla A+C | OK |
| `packet_id`, `contract.sha256`, `execution_id` contra `REQUEST.json` y `PACKET.md` | Coinciden |
| `execution.json` | `schema_version: 2` (v2, ruta C admisible) |
| `cdad_packet.py validate-request` / `validate-packet` | `rc=0` / `rc=0` |
| `cdad_packet.py render --route C` vs identificación del despacho | idéntico (incluido `project_root`, `packet`, `request`) |
| SHA-256 del contrato `spec.md` | `0d630c49…81abc` — coincide |
| `tests/` intactos al cierre | `git diff HEAD -- tests/` vacío |

## Archivos modificados (3 fuentes + 2 generados; `agents/` solo vía `make agents`)

### REGLA 1 — `skills/cdad-cycle/SKILL.md` §3.1 (compactación, −9 líneas netas)

**Antes** (15 líneas de cuerpo, 132–146; el +9 neto de T4 había llevado la fila del CLI de la 464 a la 473, fuera de la ventana `(444, 464)`):
> `The \`stack\` field … selects role variants by / domain. With …` (15 líneas con la doctrina completa)

**Después** (6 líneas de cuerpo, mismo párrafo, mismas oraciones, solo reenvuelto):
> `The \`stack\` field of \`docs/.cdad-state.json\` selects role variants by domain. With \`stack: odoo\`, the orchestrator delegates each role to its specialized \`cdad-{architect,test-writer,implementer,reviewer,scribe}-odoo\` variant` / `(permission profiles, models and Odoo skills per role). Mechanism detail, triggers and mapping table in \`references/sub-agent-strategies.md\` (not duplicated here). The derivation is the one the canonical producer applies` / `and consumers do not re-implement: a \`stack\` that is absent, \`null\` or empty derives the generic \`cdad-<role>\`; any non-empty stack derives \`cdad-<role>-<stack>\`, a suffix by domain. «Any other value» never means the` / `generic agent. The dispatch uses the \`agent\` of the validated request, and a required variant that is not published stops the dispatch: it is a procedural duty of the orchestrator (verify publication and stop) and it is` / `never substituted silently. The mechanical rejection before launching the role work belongs to the external adapter; no new mechanical guard is claimed for the` / `native path.`

**Por qué satisface PD-10 sin debilitar nada:** la fila `project-execution.md` vuelve a la línea 464 (borde inclusivo de la ventana) y `continuity.md` a la 465; la ventana `(250, 276)` conserva su punto (261→252) y la región de flujo `(277, 443)` conserva el suyo (296→287). La doctrina PC-09 queda íntegra en el mismo párrafo: derivación por sufijo (`suffix` + `cdad-<role>-<stack>`), genérico solo para ausente/null/vacío, «any other value» negado + con sufijo en ventana (doble absolución del detector), variante no publicada como deber procedimental (`stop` + `procedural duty`), sustitución silenciosa negada, y rechazo mecánico atribuido solo al adaptador externo con negación de guarda nueva en la vía nativa (`claims_new_mechanical_guard` → `[]`, verificado por los 29 tests del módulo que siguen verdes). No se agregó ninguna línea por encima de la tabla.

### REGLA 2 — `sources/agents/adapters/opencode.md` y `claude-code.md` (bloque `delegation`, re-unión en una línea)

**Antes** (asociación partida por el rewrap de T4):
> `then dispatch with the \`task\`/\`Agent\` tool and \`subagent_type\` = the \`agent\` of the` / `validated request (role→subagent mapping: \`cdad-architect\`,` …

**Después** (misma información, asociación en una misma línea a 4 caracteres de distancia):
> `… — then dispatch with the \`task\`/\`Agent\` tool` / `(\`subagent_type\` = \`cdad-<role>\`, role→subagent mapping) using the \`agent\` of the validated` / `request (\`cdad-architect\`, \`cdad-test-writer\`, \`cdad-implementer\`, \`cdad-reviewer\`, \`cdad-scribe\`). A` … (resto del bloque B1 byte-idéntico)

**Por qué satisface PD-2(b) sin debilitar nada:** la regex `subagent_type[^\n]{0,80}cdad-(?:<role>|…)` vuelve a matchear en la misma línea; se conservan el formulario de herramienta (`` `task` ``/`` `Agent` ``), el token `subagent_type`, la lista concreta de los cinco mapeos, y todo el bloque B1 (deber procedimental, sin sustitución silenciosa, guarda mecánica solo externa) que miden los tests de 010-002 con radio. La región `native_mechanism_region` sigue terminando en el bullet siguiente (las continuaciones no empiezan con `- `).

### REGLA 3 — frase literal `resolve the stack` (2 adaptadores + 2 orquestadores generados)

**Antes:** `First derive the recipient from the \`stack\`` (el rewrap había eliminado la frase que F007 exige).
**Después:** `First resolve the stack, then derive the recipient from the` (+ resto idéntico), en ambos adaptadores; los dos `agents/*/cdad-orchestrator.md` la reciben por composición vía `make agents` (verificado con `grep -c`: 1 ocurrencia en cada una de las 4 superficies).

**Por qué satisface F007 sin debilitar nada:** el validador consolidado (`assert_file_has … 'resolve the stack'`, paridad OpenCode/Claude Code sobre el sufijo resuelto antes de delegar) vuelve a pasar; la frase añadida no toca ningún detector de 010-002 (`resolve` no pertenece a ninguna familia de tokens) y la derivación canónica que sigue nombra el mismo origen (`docs/.cdad-state.json.stack`).

### Lo que no se perdió (B1/B2 intactos)
Módulo 29/29 + propiedades 7/7 verdes; generador, `010-001`, techo estático y `pd8b` verdes (tabla). `sources/roles/` no se tocó (fuera de `write_scope`); `skills/cdad-cycle/packets/**` intacto (I-10); `tests/` intacto.

## Tabla de comandos (salida y rc)

| Comando | rc | Salida |
|---|---|---|
| `python3 -B -m pytest -q tests/test_006_002_u1_delegation_section.py` | 0 | `10 passed in 3.83s` (antes: `2 failed, 8 passed`) |
| `python3 -B -m pytest -q tests/test_005_006_t1_start_procedure.py` | 0 | `15 passed in 0.13s` (antes: `1 failed, 14 passed`) |
| `python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py` | 0 | `29 passed in 44.10s` |
| `python3 -B -m pytest -q tests/test_010_002_documentary_role_properties.py` | 0 | `7 passed in 189.82s` |
| `python3 -B -m pytest -q tests/test_cdad_generate.py tests/test_010_001_documentary_contracts.py tests/test_static_block_ceiling.py` | 0 | `23 passed in 17.13s` |
| `python3 -B -m pytest -q tests/test_006_003_u8_acceptance.py -k pd8b` | 0 | `1 passed, 4 deselected in 36.06s` (validador sobre instalación aislada; F007 verde) |
| `make agents` ×2 + hash de `agents/` y `build/staging` | 0 | `agents/ 7f9c2d65…`, `staging 9b914e8f…` — idénticos entre generaciones (regeneración reproducible) |

Suite completa: no ejecutada — política del paquete (la corre quien cierra).

## Commit
- **`cc6dad54`** — `fix(010-002): review-fix de 4 regresiones de cierre (PD-10, PD-2b x2, F007)` — 5 archivos, +29/−42 (3 fuentes + 2 agentes regenerados). `docs/.cdad-state.json` sucio preexistente y `discovery.md` untracked de `010-000` quedaron fuera del commit, como en el review-fix anterior.

## Límites honestos
- La corrección es de instrucciones y localizadores: los controles acreditan presencia/posición, no conducta de modelos (PC-13).
- La fragilidad de los localizadores (ventana fija PD-10, regex por línea PD-2b) sigue registrada en el backlog del epic: cualquier edición legítima por encima de la tabla la vuelve a romper; la verificación futura de unidades que toquen `SKILL.md`/adaptadores debe incluir estos tres oráculos.
