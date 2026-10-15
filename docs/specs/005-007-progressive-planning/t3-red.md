# Informe RED — 005-007 T3: `open-unit` (PD-7) + dependencias declaradas (obs 2)

**Role:** test-writer · **Substage:** red · **Packet:** `005-007-progressive-planning-test-writer-red-004` · **Execution:** `exec-005-007-progressive-planning-001`
**Contrato:** `docs/specs/005-007-progressive-planning/spec.md` (PD-7, PD-12; AC-2) + `plan.md` ficha T3 + `review-claude-spec-2026-10-13.md` obs 2.
**Commit RED:** `47cd7cc` (rama `codex/epic-005-real-operation`) — solo `tests/test_005_007_t3_open_unit.py` (597 líneas; `git show --stat HEAD`: 1 file changed, 597 insertions).

## 1. Modified files

- `tests/test_005_007_t3_open_unit.py` — **nuevo** (focal declarado de T3). Único archivo tocado; write scope respetado (`tests/**`). Nota: `git status` mostró además `docs/.cdad-state.json` modificado por el runtime del ciclo (historia T2) — **no** lo toqué ni lo commiteé (fuera del write scope del packet).

## 2. Diseño del oráculo (caja negra, sin leer implementación)

Superficie: `subprocess` sobre `skills/cdad-cycle/scripts/cdad_packet.py` (`open-unit`, `validate-state`, `status`) — el módulo nunca se importa y la implementación nunca se lee. Fixture autocontenido (tempdir, HOME aislado): patrón existente reutilizado de `tests/test_005_003_t1_compact_view.py` / `tests/test_005_003_f2_idle_history.py` / `tests/test_005_001_t3_idle.py` (helpers de `tests/test_004_002_t2_bootstrap.py`: `build_project`, `prepare_args`, `read_state`, `write_state`, `tree_snapshot`) + `prepare` real (rc=0, más la sonda lo confirmó) + mutación declarada a **reposo legítimo con cola `queued`** (`active_feature: null` + `current_stage: "idle"`, features cerradas `done`, contratos pineados para las unidades `queued`). No depende del estado real del repo.

Preparación (sondas desechables en `/tmp/opencode/probe_t3_fixture*.py`, hoy):
- reposo con cola → `validate-state` rc=0 «VALID: idle»; `status` rc=0, `entry: next-unit`; entrada con `depends_on` extra aceptada (rc=0);
- `open-unit` → rc=2 «invalid choice: 'open-unit'» (subcomando inexistente).

## 3. RED: 6 tests, uno por postcondición/caso exigido

Comando exacto: `python3 -m pytest tests/test_005_007_t3_open_unit.py -q` → **6 failed in 4.49s** (resumen abajo, §5).

| # | Test | Postcondición / obs | Falla HOY en (aserción propia, no fixture) |
|---|---|---|---|
| 1 | `test_pd7_open_unit_opens_first_queued_unit` | PD-7 APERTURA: una invocación abre la **primera `queued`** del orden del plan: `active_feature`, entrada `in-progress`+`opened_at`, `current_stage="discovery"`, `epic_stage` sin cambios, resto `queued`, y `validate-state` verde | `PD-7 violada (APERTURA): UNA invocación de \`open-unit\` debe abrir la primera unidad \`queued\` (rc=0); hoy rc=2 (subcomando inexistente)` |
| 2 | `test_pd7_second_invocation_with_open_unit_rejected_without_writes` | PD-7 IDEMPOTENCIA/REPOSO: segunda invocación con unidad ya abierta → rc≠0, diagnóstico accionable que nombra la unidad, **sin escribir state ni árbol** | `PD-7 (IDEMPOTENCIA/REPOSO): el rechazo es un error de uso del CLI ('invalid choice'), no el comportamiento del contrato PD-7` |
| 3 | `test_pd7_feature_target_rejects_non_queued_or_unknown_unit` | PD-7 selección: `--feature` sobre entrada no `queued` (done) o inexistente → rc≠0 + diagnóstico que nombra la unidad y `queued`, sin escribir | ídem (rechazo de dominio ausente; hoy error de uso) |
| 4 | `test_pd7_no_shortcuts_authority_blocks_byte_identical` | PD-7 conservar autoridad: `stage_history`, `approver`, `hitl_delegation`, `version` idénticos tras abrir; `docs/cdad-policy.json` byte-idéntico | `PD-7 violada (NO-ATAJOS): la apertura debe ocurrir (rc=0)...; hoy rc=2` (primera aserción, luego evalúa identidad de bloques) |
| 5 | `test_obs2_declared_dependencies_verified_or_declared` | obs 2: (a) `depends_on` declarado con dependencia no `done` → RECHAZA nombrándola, sin abrir ni escribir; (b) sin `depends_on` → abre y **declara explícitamente** que no verifica dependencias (el orden del plan es la autoridad) | `obs 2 (a): el rechazo es un error de uso del CLI ('invalid choice')...` (y en (b) faltaría la declaración explícita) |
| 6 | `test_pd7_discovery_status_next_route_names_open_unit_and_project_start_documents_it` | PD-7 DESCUBRIMIENTO: la ruta `next-unit` de `status` **nombra** `open-unit` y `skills/cdad-cycle/references/project-start.md` la documenta por referencia (una sección que la nombre) | `PD-7 violada (DESCUBRIMIENTO): la ruta \`next-unit\` de \`status\` debe NOMBRAR la operación (\`open-unit\`)` — hoy emite `{"route": "next unit (project-start.md §6-§7)", "source": "docs/.cdad-state.json:current_stage"}`, sin `open-unit` |

Cada docstring traza su postcondición y el fallo RED esperado; ninguna aserción de fixture puede fallar (las precondiciones de fixture — `prepare` rc=0, reposo coherenteHoy, `entry=next-unit` — son comportamiento existente verde, verificado por sonda y por las regresiones).

## 4. Exact commands and outputs

```
$ python3 -m pytest tests/test_005_007_t3_open_unit.py -q
=========================== short test summary info ============================
FAILED tests/test_005_007_t3_open_unit.py::test_pd7_open_unit_opens_first_queued_unit
FAILED tests/test_005_007_t3_open_unit.py::test_pd7_second_invocation_with_open_unit_rejected_without_writes
FAILED tests/test_005_007_t3_open_unit.py::test_pd7_feature_target_rejects_non_queued_or_unknown_unit
FAILED tests/test_005_007_t3_open_unit.py::test_pd7_no_shortcuts_authority_blocks_byte_identical
FAILED tests/test_005_007_t3_open_unit.py::test_obs2_declared_dependencies_verified_or_declared
FAILED tests/test_005_007_t3_open_unit.py::test_pd7_discovery_status_next_route_names_open_unit_and_project_start_documents_it
6 failed in 4.49s
```

Cada fallo es `AssertionError` de comportamiento (mensajes §3); ninguno es `ImportError`, `SyntaxError` ni `JSONDecodeError` (el único `JSONDecodeError` está capturado y convertido en `AssertionError` de precondición, que hoy pasa).

Regresiones declaradas del plan (motivo concreto: el test importa helpers compartidos de solo lectura; verificación focal, no suite completa):

```
$ python3 -m pytest tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py tests/test_005_003_f2_idle_history.py tests/test_005_001_t3_idle.py -q
............................                                             [100%]
28 passed in 16.86s
```

Línea base previa (mismos archivos + focales bosque de 005-001/005-003): 18 passed.

## 5. Commit

```
$ git add tests/test_005_007_t3_open_unit.py
$ git commit -m "test: 005-007 T3 RED — open-unit abre la primera queued del plan sin editar el state (PD-7) + dependencias declaradas de la obs 2 (6 failed, fallo por asercion de contrato)"
[codex/epic-005-real-operation 47cd7cc] ... 1 file changed, 597 insertions(+)
$ git show --stat HEAD | tail -4
 tests/test_005_007_t3_open_unit.py | 597 +++++++++++++++++++++++++++++++++++++
 1 file changed, 597 insertions(+)
```

## 6. Notas honestas (límites)

- La aserción `"dependenc" in out2.lower()` de obs 2 (b) es deliberadamente **mínima y no copia prosa del contrato**: exige que la salida mencione dependencias; el GREEN decide su formulación exacta de la declaración («no verifica dependencias; el orden del plan es la autoridad»).
- Caso 2 y obs 2 (a): la aserción `rc≠0` pasa HOY (por el error de uso), por eso la aserción de rechazo de dominio (`_no_usage_error` + diagnóstico que nombra la unidad/dependencia) es la que falla y define el RED de ese caso.
- El fixture usa `depends_on` como campo extra de la entrada `epic_features`: la sonda confirmó que el validador vigente lo tolera en reposo (rc=0); si el GREEN decidiera otra representación, la obs 2 se re-discute con el contrato (no con el test).
- `docs/.cdad-state.json` quedó modificado en el árbol por el runtime del ciclo (historia T2); es ajeno a esta sesión y queda sin commitear (alcance del packet respetado).

Status: RED registrado — 6/6 tests fallan por aserción de contrato del PD-7/obs 2, listo para GREEN en sesión aislada de implementer.
