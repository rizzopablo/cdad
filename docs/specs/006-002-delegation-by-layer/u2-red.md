Ahora escribo el módulo RED de U2.
Ahora ajusto el test de modelos y la sección PD-3 para usar el locator general.
Ahora actualizo el docstring/mapa de ese módulo:
Ahora la reformulación de #4 (spawn guard en SKILL.md):
RED de U2 completo. Reporte:

## Archivos (solo `tests/`)

| Archivo | Cambio |
|---|---|
| `tests/test_006_002_u2_neutral_skill.py` | **NUEVO** (405 líneas) — RED de PD-1 + PD-3 |
| `tests/test_005_004_t1_dispatch_tool_name.py` | acoplado **reformulado** (`test_pd1_iii_reference_and_owners_name_the_same_tool` + mapa del docstring) |
| `tests/test_005_009_t3_spawn_reconciliation.py` | acoplado **reformulado** (`test_pd9_spawn_guard_conserved_in_skillmd` + nota RED) |

## Mapa test → PD

| Test | PD | Estado en RED |
|---|---|---|
| `TestPd1SkillWithoutRuntimeTools::test_pd1_no_dispatch_tool_form_in_installable_skill_text` | PD-1 / INV-1 | **FAIL** (AssertionError): 24 formas de herramienta en la superficie U2 |
| `...::test_pd1_no_concrete_model_in_delegation_context` | PD-1 / INV-2 | PASS hoy → **GUARD pre-satisfecho** declarado (el árbol no fija modelos fuera de §2, superficie de PD-11/U4) |
| `TestPd3Section4NeutralCore::test_pd3_section4_keeps_the_seven_points_in_abstract_form` | PD-3 | **FAIL**: §4 (134-174) sin 6 de los 10 sub-conceptos (principio, nativo, dueño del ciclo de vida, invariantes, recibo, transporte) |
| `...::test_pd3_section4_names_no_runtime_tool_form` | PD-3 / INV-1 | **FAIL**: §4 con `task`/`delegate`/`Agent`/`subagent_type`/`sessions_spawn` |

Oráculo de ausencia con las **exclusiones declaradas y con dueño**: `context-meter.md` (lector/medición, INV-8), las dos referencias de runtime (**TEMPORAL, comentario «U3»**, PD-9), `cli-delegation.md` (contrato del adaptador, PD-10) y §2 de `SKILL.md` (PD-11/U4, neutralizada manteniendo la numeración de líneas). Regexes de modelo/proveedor **reusados por import** desde `tests/test_005_010_t3_references.py`. Los 24 offenders caen **exactamente** en las líneas que el spec §1 declara para U2 (`SKILL.md:145-160, 243, 275, 463-466, 501-502`; `handoff-prompts.md:39-40`; `progress-guards.md:27,38`; `sub-agent-strategies.md:53`) — el oráculo ni más amplio ni más estrecho que la unidad.

## Comandos y salida

```
python3 -m pytest tests/test_006_002_u2_neutral_skill.py -q
→ 3 failed, 1 passed in 0.17s   (los 3 fallos: AssertionError; grep ImportError|SyntaxError = 0)

python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py tests/test_005_009_t3_spawn_reconciliation.py tests/test_005_010_t3_references.py -q
→ 2 failed, 31 passed in 1.57s
  FAIL test_pd1_iii_reference_and_owners_name_the_same_tool  (SKILL.md aún nombra `Agent`)
  FAIL test_pd9_spawn_guard_conserved_in_skillmd             (SKILL.md aún nombra sessions_spawn)

bash tests/validate-consistency.sh → Assert PASS: 155 / FAIL: 1
  el único FAIL es preexistente y ambiental: F011 validate-subagents.sh → drift de los agentes INSTALADOS en HOME
  (.claude/agents, .config/opencode/agents), ajeno a tests/ y a la superficie de U2.
  F004/F010/F001 y el control 005-004 PD-1 (que U2 podría tocar) pasan.

bash tests/validate-odoo-specialization.sh → PASS 67 / FAIL 0
```

## Acoplados: qué cambió y por qué (plan A-1; U7 plegada)

- **#1** `test_pd1_iii_reference_and_skill_name_the_same_tool` → el dueño del nombre deja de ser `SKILL.md`: ahora exigen `Agent` el reference, el **adaptador fuente** y el **orquestador derivado**, y exigen que `SKILL.md` **no** lo nombre como herramienta (forma de herramienta, no la palabra suelta). Cobertura conservada + punto de falla contra el árbol viejo. Justificado por **006-002 PD-1/PD-3**.
- **#4** `test_pd9_spawn_guard_conserved_in_skillmd`: la mitad «nombra el mutador concreto» se **invierte** (el guard de la skill queda abstracto; el nombre de la herramienta pertenece al orquestador del runtime). Prohibición, sub-subagentes, anti-bucle y handoff siguen exigidos. Justificado por **PD-1/PD-3 + INV-1**.
- **#5** `test_005_010_t3_references.py`: **sin cambio** — su superficie es `cli-delegation.md`/`opencode-delegation.md` (PD-10/U3), disjunta de la de U2; corre como regresión y pasa (5/5).
- **`tests/validate-consistency.sh`**: **sin cambio** — F004/F010 leen las dos referencias (U3), F001 lee §2/perfiles (U4); ninguno afirma texto de la superficie de U2.

## Commit

```
git add tests/test_006_002_u2_neutral_skill.py tests/test_005_004_t1_dispatch_tool_name.py tests/test_005_009_t3_spawn_reconciliation.py
git commit -m "test: 006-002 U2 RED — §4 neutral de cdad-cycle y skill sin herramientas de runtime"
→ 4e17dcc  (sin --no-verify, sin stash, sin push; diff 3 archivos, todos bajo tests/)
```

## Declaraciones honestas

- No abrí ningún archivo de `skills/`, `sources/`, `scripts/` ni `agents/` para derivar aserciones: el oráculo sale del spec/plan. Sí vi fragmentos de `SKILL.md` en los **mensajes de falla de los propios tests** (el diagnóstico del guard de 005-009 imprime su ventana, y la línea 156 de mi propio mensaje). Declarado como límite del guard (el test lee el producto por diseño).
- La localización de §4/§2 es por **encabezado numerado** (el contrato las llama «§4»/«§2»), con guarda de drift si no se delimitan.
- El test de modelos en este subfase es un guard pre-satisfecho; su deuda real vive en §2 y pertenece al RED de **U4 (PD-11)** — no la reclamo como verde contractual.
- La corrida no usó la suite completa (política del packet): la cierra el closer.
