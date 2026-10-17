I'm on the RED substage for U1 of 006-002-delegation-by-layer. Let me start by reading the approved contract and plan.
Now let me study the existing test patterns referenced by the plan:
Let me look at the staging helper and the generator test:
Now let me examine the coupled test modules and the adapter sources (readable as consumer):
Confirmed: no `delegation` section in the adapters yet. Let me check the coupled module #4 and validate-consistency.sh, plus generate staging to see current orchestrator state:
Let me check the Makefile staging target and generate staging `PROFILE=basic` in a throwaway copy to see the current orchestrator state:
Let me see how existing adapter sections get composed into the generated orchestrator (to design the composition oracle without over-fitting):
The generator composes adapter-section *content* by concept (not verbatim copy) — good to know for the oracle design. Let me verify the current RED-expected state of the generated orchestrators:
The CC orchestrator already names `Agent` + `subagent_type` today (line 270). Let me check that F011 failure and see the CC orchestrator context, plus check where the CC line 270 lives:
F011's failure is pre-existing host-install drift (a `.pyc` in the user's installed skills) — unrelated to U1's surface. Let me check the remaining concepts in the current orchestrators to predict RED failures precisely:
Now the critical analysis: what does the generator's hardcoded block (`:812-828`) currently contribute to the generated orchestrator, and does coupled test #4 depend on it? Let me compare the role source against the generated orchestrator:
Sources/roles/orchestrator.md owns anti-recursion/boundary. Let me find which generated lines are NOT in any source (i.e., the generator-hardcoded block):
The anti-recursion content exists twice in the generated orchestrator (role-source bullet + hardcoded block) — #4's conservación survives GREEN's hardcoded-block removal. Let me verify no test pins the hardcoded section's exact content:
No test pins the hardcoded block content. The coupled-module analysis is complete: none needs changing for U1 (I'll justify per-PD in the report). Now I'll write the RED test file:
Now run the focal test and capture the RED evidence:
9 RED failures + 1 passing control (CC native mechanism, as predicted). Let me capture the precise failure reason of each test (all must be contract AssertionError):
All 9 RED failures are contract AssertionErrors. Now run the U1 regressions (plan: `test_cdad_generate.py`, #1, #4, validate-consistency.sh):
All regressions green. Now commit only `tests/`:
# Reporte test-writer — RED U1 `006-002-delegation-by-layer` (packet `…-test-writer-red-001`)

## Archivos modificados
- **`tests/test_006_002_u1_delegation_section.py`** (nuevo, +497 líneas) — único archivo, dentro del write_scope `tests/`.

## Mapa test → postcondición
| Test | PD |
|---|---|
| `TestPd2aExactlyOneDelegationSection::test_pd2a_{opencode,claude_code}_adapter_has_exactly_one_delegation_section` | PD-2(a) |
| `TestPd2bSourceOwnsDelegationContent::test_pd2b_{opencode,claude_code}_source_block_owns_the_delegation_concepts` | PD-2(a)/(b) + D-1 (el contenido vive en la fuente) |
| `TestPd2cOcOrchestratorNativeMechanism::test_pd2c_opencode_…` | PD-2(c) (OpenCode: `` `task` `` + `subagent_type: cdad-<role>`) |
| `TestPd2cCcOrchestratorNativeMechanism::test_pd2c_claude_code_…` | PD-2(c) (Claude Code: `` `Agent` `` + `subagent_type`) — control, pasa hoy |
| `TestPd4IntraRuntimeAdapterProhibition::test_pd4_ii_…` | PD-4(ii)/D-1 (prohibición explícita co-ubicada, ambos runtimes) |
| `TestPd4BasicFamilyDeclaration::test_pd4_basic_family_declaration_in_{opencode,claude_code}_…` | PD-4(iii)+(iv) / D-3 (`basic` no garantizada + registro `model_configured`/`model_reported` + nunca elige/inventa + modelo solo de la config del entorno) |
| `TestPd2dPacketPassAndReceiptLink::test_pd2d_…` | PD-2(d) + PD-5(b) (pase byte-idéntico + enlace «Orchestrator materialization protocol») |

Oráculos por concepto con alternativas (`require_any` de `tests/test_005_010_t3_references.py`); formularios de herramienta (code-spans, `subagent_type`), nunca la palabra suelta *task*. Sin dependencia del orden interno (ningún assert fija posición). Staging `PROFILE=basic` en copia temporal propia (patrón `tests/product_staging.py`), nunca escrito en el repo; sin valores de host; sin `/tmp` como canal.

## Comandos y resultados
1. `python3 -m pytest tests/test_006_002_u1_delegation_section.py -v` → **9 failed, 1 passed**. Todos los fallos son **AssertionError de contrato**, ninguno import/sintaxis/fixture:
   - PD-2(a): «debe llevar EXACTAMENTE un bloque `cdad-section:delegation` (encontrados 0)» ×2
   - PD-2(b)/D-1: «no tiene bloque … el contenido no vive en la fuente» ×2
   - PD-2(c) OC: «no declara el concepto clave 'mecanismo nativo `task`'»
   - PD-4(ii): «no co-ubica [prohibición + intra-runtime] alrededor del ancla [adaptador CLI]»
   - PD-4(iii): «no declara 'campos de registro model_configured/model_reported'» ×2
   - PD-2(d)/PD-5(b): «no enlaza al «orchestrator materialization protocol»»
   - Único PASO hoy (predicho): control CC `` `Agent` ``+`subagent_type` (ya existe vía tool-loading del adaptador CC).
2. Regresiones ficha U1 — todas verdes: `test_cdad_generate.py` **10 passed**; #1 `test_005_004_t1_dispatch_tool_name.py` **7 passed**; #4 `test_005_009_t3_spawn_reconciliation.py` **21 passed**.
3. `bash tests/validate-consistency.sh` → **155 PASS / 1 FAIL**: el fallo es **F011 preexistente y ambiental** — `scripts/validate-subagents.sh` falla en `install.sh --check` por drift del host (`DRIFT: <home>/.claude/skills/cdad-cycle/scripts/__pycache__/cdad_packet.cpython-313.pyc`), ajeno a la superficie U1 (adaptadores/orquestadores). Preexistente antes de este RED; declarado, no lo trabajo (fuera de write_scope).

## Módulos acoplados (lista del plan): ninguno cambió — justificación
- **#1 `test_005_004_t1_dispatch_tool_name.py`**: fija frontmatter `tools:` CC (Agent≠Task), dueño del nombre en el adaptador CC y paridad staging↔repo. U1 GREEN agrega una sección `delegation` sin tocar frontmatter ni esas afirmaciones; el bloque nuevo nombrará `Agent` (coherente con `test_pd1_iii_*`). Sin cambio.
- **#4 `test_005_009_t3_spawn_reconciliation.py`**: sus asserts de conservación en generados se satisfacen desde `sources/roles/orchestrator.md` (anti-recursión :77-79, distinción :97-99). La remoción del bloque hardcodeado `:812-828` elimina un DUPLICADO del spawn guard en el generado (el bullet de la fuente permanece compuesto), no la única ocurrencia. Verificado en staging: las marcas están en las líneas 71/93 (fuente) además de la 179 (hardcodeada). Sin cambio.
- **`tests/validate-consistency.sh`** (F001/F004/F010): F001 exige `--basic` + caveat basic en los orquestadores — vive en el párrafo «Models of the design» compuesto, que U1 no toca (su reforma es U4/PD-11); F004/F010 son superficie U3/U5. Sin cambio.

## Límites y aislamiento (declaración honesta)
- No leí implementación nueva: ni `scripts/`, ni `skills/`, ni `agents/` editados. Leí, como consumidor (autorizado por el paquete): `sources/agents/adapters/*.md` y `sources/roles/orchestrator.md` (fuentes de consumidor) y la salida generada en staging. Escrituras solo en `tests/`; staging en directorios temporales del propio test.

## Commit
- `a2db8f8` — `test: 006-002 U1 RED delegation sections (PD-2/PD-4 text; D-1/D-3)` (solo `tests/test_006_002_u1_delegation_section.py`; sin `--no-verify`, sin stash, sin push).

**Estado:** RED de U1 completo — 9 fallos por el motivo correcto, control CC verde, regresiones verdes. Listo para GREEN (implementador): secciones `delegation` en ambos adaptadores + composición por el generador, sin tocar `tests/`.
