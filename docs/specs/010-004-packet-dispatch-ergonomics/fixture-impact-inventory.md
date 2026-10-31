# Inventario de impacto — convención de fixtures frente a PC-04 (010-004 T2)

**Fecha:** 2026-10-30
**Unidad:** `010-004-packet-dispatch-ergonomics`, T2 (GREEN entregado en `a273042e`, attempt19)
**Autoridad:** mandato HITL vigente (`docs/epics/epic-010-documentary-specialization/execution.md`) — decide y avanza, registra fundamento.
**Toolchain:** la del **repositorio** (`skills/cdad-cycle/scripts/cdad_packet.py --project-root .`). La copia instalada **no** se usó ni se modificó (drift D-1 declarado).
**Base medida:** `d1518e17` (docs: recepción de GREEN T2) sobre producto `a273042e`.

Este documento **mide**, no decide el gate. No cambia la spec, el plan ni el producto.

## 0. Resumen ejecutivo

| Clase | Qué es | Tests | Archivos |
|---|---|---|---|
| **C1 — fixture no canónica** | La fixture publica un contexto **v2 en ubicación no canónica** (`ROOT/EXECUTION.json`) y `prepare` la rechaza: es **exactamente lo que PC-04 exige** | **62** | 13 |
| **C2 — expectativa sustituida por §7** | Intake legacy implícito v1 (`PD-12`) que la spec **sustituye explícitamente** en §7 | **1** | 1 |
| **C3 — causa distinta (diagnóstico)** | El rechazo v1 del contexto **preempata** el diagnóstico de política inválida; `§4.5` exige informar los requisitos faltantes de `§4.1` (policy) en preparación nueva sobre legado | **1** | 1 |
| **Total fallos medidos** | | **64** | **15** |

Ninguno de los 62 fallos C1 es un defecto del producto: **PC-04 los exige**. C2 es una expectativa que la spec ya sustituyó con traza. **C3 es el único caso con causa distinta** y se reporta aparte: no entra en la migración de fixtures.

## 1. Universo medido y método

Un solo detector no alcanza: la convención inválida vive en **fixtures compartidas**, no en la mención textual de `execution.json`.

| Detector | Comando | Archivos |
|---|---|---|
| D1 — token literal del subcomando | `rg -l '["'"'"']prepare["'"'"']' tests/*.py` | 64 |
| D2 — grafo de la fixture compartida | `rg -l "test_packet_prepare\|run_prepare\|PrepareProject" tests/*.py` | 27 |
| D2 extra sobre D1 (consumidores que no citan el token) | `comm -13 <D1> <D2>` | 19 |
| D3 — invocadores del CLI que mencionan `prepare` y escaparon a D1∪D2 | `comm -13 <D1∪D2> <invocadores del CLI>` + `rg -l prepare` | 22 |
| **Universo medido** | unión D1 ∪ D2 ∪ D3 | **105 archivos** |

`<invocadores del CLI>` = `rg -l "PACKET_CLI|cdad_packet\.py" tests/*.py` (105 archivos).

### Corridas reales (todas con `-q --tb=line -rf -p no:cacheprovider`)

| Corte | Archivos | Comando | Resultado real |
|---|---|---|---|
| A — D1 con `--execution-context` explícito | 34 | `python3 -m pytest $(cat /tmp/opencode/prepare-callers-withectx.txt) …` | **`9 failed, 387 passed in 849.35s`** (rc 1) |
| B1 — D1 restante (mitad 1) | 15 | `… $(cat /tmp/opencode/chunkA.txt) …` | **`1 failed, 147 passed in 241.85s`** (rc 1) |
| B2 — D1 restante (mitad 2) | 15 | `… $(cat /tmp/opencode/chunkB.txt) …` | **`137 passed, 2 skipped in 274.27s`** (rc 0) |
| C — consumidores de `PrepareProject` no detectados por D1 | 19 | `… $(cat /tmp/opencode/extra19.txt) …` | **`54 failed, 68 passed in 69.22s`** (rc 1) |
| D — D3 | 22 | `… $(cat /tmp/opencode/unmeasured-prep.txt) …` | **`241 passed in 402.64s`** (rc 0) |
| **Total** | **105** | | **`64 failed, 980 passed, 2 skipped`** (1046 tests) |

Los logs completos de las cinco corridas quedan en `/tmp/opencode/{consumer-suite,chunkA,chunkB,extra19,last22}.log` (evidencia de la sesión; los conteos de arriba son la línea resumen real de cada uno).

### Verificación de causa única (no por lectura del reporte del rol)

Se contó, por cada línea de fallo (`--tb=line` emite una por test), cuántas contienen el diagnóstico de PC-04:

```
slice A: FAILED=9  tb_lines=9  tb_with_canonical=7     (2 de causa distinta: ver §3)
slice C: FAILED=54 tb_lines=54 tb_with_canonical=54    (una sola causa)
slice B: FAILED=1  tb_lines=1  tb_with_canonical=0     (C2)
slice D: FAILED=0
```

Diagnóstico literal de la causa C1:

> `ERROR: a new preparation requires the execution context at its canonical location (.cdad/executions/<execution_id>/execution.json), but the selected context is <ROOT>/EXECUTION.json — a copy in another location is not an admitted locator and is never copied, converted or relocated to make it pass. Pass the canonical context, or start the new v2 execution with prepare --new-execution (010-004 §4.1/PC-04)`

## 2. Inventario por archivo

| Archivo | Tests | Fallos | Causa | Clase | Acción |
|---|---:|---:|---|---|---|
| `tests/test_packet_prepare.py` | 19 | 8 | C1 (7 directos + 1 carrera inalcanzable) | (ii) | migrar fixture |
| `tests/test_006_006_u1_draft_object_form.py` | 21 | 16 | C1 | (ii) | migrar fixture |
| `tests/test_004_003_t4_validation_fields.py` | 11 | 8 | C1 | (ii) | migrar fixture |
| `tests/test_005_007_t2_progressive_plan_validator.py` | 6 | 6 | C1 | (ii) | migrar fixture |
| `tests/test_004_003_t3_plan_checks.py` | 5 | 5 | C1 | (ii) | migrar fixture |
| `tests/test_004_003_t2_plan_review.py` | 5 | 5 | C1 | (ii) | migrar fixture |
| `tests/test_006_005_u1c_packet_agent.py` | 5 | 4 | C1 | (ii) | migrar fixture |
| `tests/test_006_006_u3_review_route_and_gate.py` | 12 | 2 | C1 | (ii) | migrar fixture |
| `tests/test_004_003_t2_reviewfix.py` | 2 | 2 | C1 | (ii) | migrar fixture |
| `tests/test_004_003_t1_reviewfix.py` | 2 | 2 | C1 | (ii) | migrar fixture |
| `tests/test_004_003_t1_draft_contract.py` | 2 | 2 | C1 | (ii) | migrar fixture |
| `tests/test_005_007_t6_templates.py` | 4 | 1 | C1 | (ii) | migrar fixture |
| `tests/test_005_007_reviewfix_blockings.py` | 2 | 1 | C1 | (ii) | migrar fixture |
| `tests/test_004_002_t7_acceptance.py` | 3 | 1 | C2 | (i) | actualizar expectativa con traza |
| `tests/test_004_002_t2_reviewfix.py` | 18 | 1 | C3 | (iii) | **NO migrar** — reportar |
| **Total** | **117** | **64** | | | |

Detalle de los dos fallos que no son C1 directo:

- `tests/test_packet_prepare.py::TestPrepareFailureHasNoEffects::test_p4_packet_id_directory_appearing_before_mkdir_is_not_touched` — la fixture `PrepareProject` hace fallar `prepare` **antes** del punto de carrera (`sitecustomize` crea el directorio ajeno en `mkdir`); el hook nunca dispara y el test reporta `foreign packet directory was deleted`. **Misma causa raíz C1** (el rechazo de PC-04 precede a la publicación). Promesa intacta: la carrera se vuelve a ejercitar en cuanto la fixture use el contexto canónico.
- `tests/test_004_002_t2_reviewfix.py::TestF6NoLegacyFallbackOnInvalidPolicyLocation::test_f6_policy_directory_with_v1_context_no_legacy_fallback` — **causa distinta (C3)**, ver §3.

## 3. Clases (i)/(ii)/(iii)

### (i) Expectativas que la spec sustituye — actualizar con traza (1 test)

- `tests/test_004_002_t7_acceptance.py::TestT7LayoutsConsumersMatrix::test_criterio2_full_matrix_single_walk_from_install`, celda `_cell_legacy` (`:430-473`): hoy exige `prepare` rc=0 y paquete publicado sobre un consumidor legacy **sin política** con documento v1 en `.cdad/execution.json`. La spec §7 sustituye **explícitamente** esa garantía de `004-002/spec.md:112-115` (PD-12, «conserva su intake») en cuanto permitía preparar implícitamente un encargo v1 sin policy. Traza de la actualización: expectativa anterior (`test_004_002_t7_acceptance.py:430-473` + docstring) → `docs/specs/004-002-project-execution-bootstrap/spec.md:112-115` (PD-12) → `owner-decision-v2-new-assignments.md:3-13` → `010-004/spec.md` §7 + PC-04 + INV-11. Las demás celdas y aserciones de la matriz **no** cambian.

### (ii) Tests ajenos con convención de fixture ahora inválida — migrar sin tocar la promesa (62 tests / 13 archivos)

Todos fallan por C1. La convención anterior está centralizada en tres puntos:

1. `tests/test_role_packets.py::StateFixture` (`:247`) — escribe el documento v2 en `ROOT/EXECUTION.json`.
2. `tests/test_packet_prepare.py::PrepareProject.execution_path` (`:152-153`) y `PrepareProject.args()` (`:155-164`) — pasan `--execution-context ROOT/EXECUTION.json` a `prepare`.
3. `tests/test_role_packet_render.py::PacketFixture.invoke` (`:200`) — pasa `ROOT/EXECUTION.json`; **sólo** afecta a `render`/`validate-*`, donde la vía histórica explícita (§4.1, fila 3 de la matriz) **sigue admitida**: no se toca.

La migración correcta es de **convención**, no de aserción: el mismo documento v2 se escribe/lee en `.cdad/executions/<execution_id>/execution.json` para la **preparación nueva**; ninguna promesa verificada cambia.

### (iii) Causa distinta — regresión/incumplimiento a corregir por el implementer (1 test)

- `tests/test_004_002_t2_reviewfix.py::TestF6NoLegacyFallbackOnInvalidPolicyLocation::test_f6_policy_directory_with_v1_context_no_legacy_fallback` (`:462-501`).
  - **Qué verifica:** con `docs/cdad-policy.json` existente pero **directorio** y un contexto v1 presente, `prepare` debe fallar (rc≠0, sin paquete, v1 intacto, árbol sin cambios) **y el diagnóstico debe nombrar la política** (`:487-489`, regex `policy|pol[íi]tica`).
  - **Qué ocurre ahora:** rc≠0, sin paquete, v1 intacto y árbol sin cambios **se cumplen**; el diagnóstico es el de v1: `an existing v1 execution context is present at .cdad/execution.json: a new preparation uses execution v2 only…` — **no nombra la política**.
  - **Por qué es incumplimiento y no sustitución:** `010-004/spec.md` §4.5 exige que «La preparación nueva sobre legado informa los requisitos faltantes de §4.1: **policy**, autoridad/aprobación/pin o coherencia de estado». El plan, además, declara `N-4/N-5/N-6` como «no se introduce **precedencia diagnóstica** ni interpretación legacy nueva» (`plan.md`, «Incertidumbres y deferred-hardening»). El rechazo v1 introdujo una precedencia que deja el diagnóstico de política inalcanzable en ese escenario.
  - **Acción:** **no** se toca el test en la unidad de migración. Se reporta al implementer (o al owner, si prefiere decidir la precedencia). Un test que se "arregla" aflojando la regex destruiría la única verificación de que la ruta de política se evalúa.

## 4. Desviación del proceso — el AUDIT T1 subestimó este universo

**Hecho.** El AUDIT T1 (`test-audit.md` §1.1) declaró **2** expectativas sustituidas y §1.2 listó 3 tests «vigentes que comparten fixtures» (5 en total, evidencia mayormente `[L]` = lectura). La medición real da **64** tests en **15** archivos, con 62 fallos de causa única.

**Causa.** El AUDIT construyó el universo leyendo el árbol de tests y contando menciones a `execution.json` (6 menciones en 2 archivos), en lugar de **ejecutar la suite de consumidores**. La convención inválida vive en una **fixture compartida importada** (`PrepareProject`/`StateFixture`), que un conteo de menciones textuales no revela: **18 de los 19** archivos del corte C la consumen sin citar jamás `execution.json` ni el token `prepare` (el 19.º es el RED nuevo de T2, que sí manipula `EXECUTION.json` a propósito). La spec §7 ya lo había advertido —«Los dos tests nombrados no constituyen una lista exhaustiva ni evidencia de ejecución»— y el plan T1 exigía inventariar «las pruebas afectadas, distinguiendo expectativas vigentes de las sustituidas». El AUDIT no cumplió ese punto del encargo.

**Consecuencia.** Una **unidad adicional** de migración de fixtures (test-writer, sólo `tests/**`), previa al gate GREEN de T2. **No** hay cambio de contrato, de alcance del producto ni de la spec: PC-04 se implementó como está especificado y los 62 fallos C1 son su efecto exigido. El único cambio de contrato potencial —la precedencia diagnóstica de C3— se escala por separado y no se resuelve aquí.

**Medida correctiva.** El gate GREEN de T2 no se declara cerrado hasta que la unidad de migración deje el universo medido en verde (salvo C3, que requiere decisión). El inventario de este documento reemplaza al §1.1/§1.2 del AUDIT como lista de trabajo ejecutada.

**Corrección de alcance (POST-AUDIT `-004`, posterior).** El encargo correctivo que ejecutó este inventario acotó por error los cambios de aserción a la celda C2 del §3(iii) y dejó fuera tres oráculos legítimos de `tests/test_packet_prepare.py`; el resultado medido es 63 → 3 fallos con los tres residuales en ese archivo. La desviación de proceso, su fundamento por oráculo y la unidad correctiva de cierre se registran en `scope-correction-residual-oracles.md`.

## 5. Límites de esta medición (honestidad)

- Se midió el **universo de consumidores de `prepare`** (105 archivos), no la suite completa.
- Los 62 fallos C1 se clasifican por su **primer** diagnóstico observable: tras migrar la fixture, cada test ejercita sus aserciones reales y podría aparecer un fallo distinto, preexistente o nuevo. La unidad de migración debe reportarlo, no absorberlo: si aparece una causa distinta, se detiene esa parte y se devuelve como regresión.
- `tests/test_packet_prepare.py::TestPreparedInstalled::test_p5_installed_cli_prepare_matches_repo_prepare` compara el CLI **instalado** con el del repo. Con el drift D-1 declarado (instalado atrasado) y sin instalación global autorizada, es un candidato a fallar por **deriva de toolchain**, no por la fixture: la unidad debe reportarlo con evidencia en vez de debilitar el aserto o reinstalar.
