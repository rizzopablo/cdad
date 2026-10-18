Implementer GREEN de **U2 de `006-002-delegation-by-layer`** completado. Reporte:

## Archivos modificados (file:line)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/SKILL.md` | `:43` preámbulo de §2 (`task/delegate routing` → `per-runtime dispatch routing`); `:134-167` §4 reescrito neutral (principio, SPAWN GUARD abstracto, orden nativo→handoff→inline, regla de adaptadores = dueño del ciclo de vida, invariantes de rol, recibo, paquete/re-entry independientes del transporte); `:237` recomendación del modo B; `:264` paso 4 (pase de bytes por el mecanismo nativo declarado); `:269` paso 4 (orden); `:457` fila `progress-guards.md`; `:459-460` filas de las dos referencias por runtime; `:495` sección multi-entorno (a1/a2 → (a) con mecanismo declarado por el orquestador del runtime) |
| `skills/cdad-cycle/references/handoff-prompts.md` | `:36` encabezado (sin «in OpenCode»); `:38-42` invocación por el mecanismo nativo declarado; `:92` alternativa con sub-agentes |
| `skills/cdad-cycle/references/progress-guards.md` | `:27` despacho fuera del runtime (sin `opencode run`); `:39` nota del modo de despacho |
| `skills/cdad-cycle/references/sub-agent-strategies.md` | `:42` invocación OpenCode; `:53` invocación Claude Code (sin `Agent`/`task`/`delegate`) |

No se tocó `tests/`, §2 «Model family» ni el párrafo de perfiles (U4), las dos referencias por runtime ni `cli-delegation.md` (U3), `re-entry.md` (U5), `install.sh`/`cdad-models.sh`/ADR-007.

## Tabla test → resultado

| Test | PD | Resultado |
|---|---|---|
| `test_006_002_u2_neutral_skill.py::TestPd1SkillWithoutRuntimeTools::test_pd1_no_dispatch_tool_form_in_installable_skill_text` | PD-1/INV-1 | **PASS** (24 offenders → 0) |
| `...::test_pd1_no_concrete_model_in_delegation_context` | PD-1/INV-2 | **PASS** (guard pre-satisfecho, mantenido) |
| `...::TestPd3Section4NeutralCore::test_pd3_section4_keeps_the_seven_points_in_abstract_form` | PD-3 | **PASS** (los 7 puntos, 10 sub-conceptos) |
| `...::test_pd3_section4_names_no_runtime_tool_form` | PD-3/INV-1 | **PASS** (6 offenders → 0) |
| `test_005_004_t1_dispatch_tool_name.py::test_pd1_iii_reference_and_owners_name_the_same_tool` (acoplado) | PD-1(iii)/AC-1 + 006-002 PD-1/PD-3 | **PASS** |
| `test_005_009_t3_spawn_reconciliation.py::test_pd9_spawn_guard_conserved_in_skillmd` (acoplado) | PD-9 + 006-002 PD-1 | **PASS** (aserción marcada, prohibición, sub-subagentes, anti-bucle+negación, handoff conservados; sin `sessions_spawn`) |
| `test_005_010_t3_references.py` (regresión ficha U2) | 005-010 PD-10/INV-7 | **PASS** 5/5 |
| `test_006_002_u1_delegation_section.py` (regresión ficha U2) | 006-002 PD-2/PD-4 | **PASS** |
| `test_005_004_t4_cc_guard_decisions.py`, `test_005_005_t3_provenance.py`, `test_005_005_t2_docs_policy.py`, `test_packet_prepare.py`, `test_role_packet_consumers.py`, `test_role_packet_review_regressions.py`, `test_004_003_t5_reentry_equivalence.py`, `test_003_006_t1_wiring.py`, `test_003_006_t2_activation.py`, `test_005_006_t1_start_procedure.py`, `test_005_006_t2_intake.py` (regresión proporcional de las superficies tocadas) | varias | **PASS** (154 passed en total) |
| `test_005_006_t6_owner_reviewfix.py::test_hallazgo_a2_cli_invocations_derived_from_skill_dir` | — | **FAIL pre-existente** (ver abajo) |
| `test_003_006_t3_receive_wiring.py::T3AgentRegenerationCoherence::test_p1_regenerated_agents_reflect_source` | — | **FAIL pre-existente** (ver abajo) |

## Comandos con salida

```
$ python3 -m pytest tests/test_006_002_u2_neutral_skill.py -q
4 passed in 0.13s

$ python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py \
    "tests/test_005_009_t3_spawn_reconciliation.py::test_pd9_spawn_guard_conserved_in_skillmd" -q
8 passed in 1.07s

$ python3 -m pytest tests/test_006_002_u2_neutral_skill.py tests/test_005_004_t1_dispatch_tool_name.py \
    tests/test_005_009_t3_spawn_reconciliation.py tests/test_005_010_t3_references.py \
    tests/test_006_002_u1_delegation_section.py tests/test_005_004_t4_cc_guard_decisions.py \
    tests/test_005_005_t3_provenance.py tests/test_005_005_t2_docs_policy.py -q
62 passed in 6.46s

$ python3 -m pytest <superficies tocadas: 11 módulos> -q   # packet_prepare, consumers, review_regressions, 004_003_t5
102 passed in 103.55s
$ python3 -m pytest tests/test_006_002_u2_neutral_skill.py tests/test_003_006_t1_wiring.py \
    tests/test_005_006_t1_start_procedure.py tests/test_005_006_t2_intake.py \
    tests/test_003_006_t2_activation.py -q
52 passed in 5.17s

$ make validate
Assert PASS: 155 / Assert FAIL: 1        # único FAIL: F011 (DT-8 ambiental)

$ bash scripts/validate-subagents.sh
[runtime] agents in <home>/.config/opencode/agents — ✅ 10/10 runtime agents present
DRIFT: differs .../.claude/skills/cdad-cycle/SKILL.md
❌ install.sh --check failed (rc=1)      # drift de las copias INSTALADAS en HOME (DT-8), no del repo
== RESULT: FAIL (see the ❌ messages above) ==

$ bash tests/validate-odoo-specialization.sh
Assert PASS: 67 / Assert FAIL: 0
```

## Declaraciones honestas (límites y hallazgos)

1. **`F011` de `make validate` = DT-8 ambiental** (ya reportado en el RED): el validador compara contra los agentes/skills **instalados en HOME** (`.claude/agents`, `.config/opencode/agents`, `.claude/skills`), que quedaron stale respecto del repo; ajeno a `tests/` y a la superficie de U2. Nada más falla (F001/F004/F010 y el control 005-004 PD-1 pasan).
2. **Dos oráculos NO de la ficha U2 fallan por el GREEN de U1** (no por este diff): `test_005_006_t6::test_hallazgo_a2_cli_invocations_derived_from_skill_dir` y `test_003_006_t3::test_p1_regenerated_agents_reflect_source`. Los offenders están en `agents/cdad-orchestrator.md:183`, `agents/claude-code/cdad-orchestrator.md:188` y la sección `delegation` insertada por U1 en los agentes derivados (`git show HEAD:agents/...` los reproduce; `git diff --name-only` de este commit no incluye `agents/` ni `sources/`). **No los toqué ni edité tests**: quedan reportados al orquestador (son superficie de U1/U7, no de U2).
3. **Ventana de líneas congelada de `test_005_006_t1_start_procedure.py` (no es oráculo de la ficha U2).** Su ventana `SKILL.md:444-464` exige una invocación CLI; mi primera versión de §4 (+23 líneas netas) corrió la fila `project-execution.md` fuera de la ventana y lo rompió. Lo **resolví preservando la aserción**: compacté §4 de modo que el desplazamiento neto cae dentro de la tolerancia de la ventana (fila en `:454`; el bloque §4 quedó en 34 líneas, vs. 40 antes). Eso obligó a redactar los últimos cuatro puntos como párrafos de una línea; el costo de legibilidad es consecuencia del contrato de la ventana, no una preferencia de estilo. No edité el test.
4. **Trazabilidad §2 (U4)**: `model_scan_text` neutraliza §2 para el oráculo de modelos; no toqué la columna «Model family» ni el párrafo de perfiles, así que la deuda real de PD-11 sigue intacta y no la reclamo como verde.
5. No usé la suite completa (política del packet: la cierra el closer).

## git diff --stat

```
 skills/cdad-cycle/SKILL.md                         | 77 ++++++++++------------
 skills/cdad-cycle/references/handoff-prompts.md    | 17 +++---
 skills/cdad-cycle/references/progress-guards.md    | 11 ++--
 .../cdad-cycle/references/sub-agent-strategies.md  |  4 +--
 4 files changed, 52 insertions(+), 57 deletions(-)
```

## Commit

```
git add skills/cdad-cycle/SKILL.md skills/cdad-cycle/references/handoff-prompts.md \
        skills/cdad-cycle/references/progress-guards.md skills/cdad-cycle/references/sub-agent-strategies.md
git commit -m "feat: 006-002 U2 GREEN — §4 neutral y skill sin herramientas de runtime"
→ 8cf2d75  (4 archivos, todos bajo skills/; sin --no-verify, sin stash, sin push)
```

Verificación final: `test_pd1_no_dispatch_tool_form_in_installable_skill_text` → 0 offenders sobre `skills/cdad-cycle/**` y `skills/cdad-epic/**` (exclusiones declaradas: `context-meter.md`, las dos referencias de runtime — U3, `cli-delegation.md` — U3, §2 de `SKILL.md` — U4).
