# AUDIT — 007-001-unambiguous-entry (test-writer, 2026-10-23)

Materializado desde el texto final del test-writer (sesión `ses_e94ca5f2…`), substage AUDIT.
Contrato: spec `c88bab66…` + enmienda menor post-audit (aclaraciones del architect).

## Cobertura test ↔ postcondición

| PC | Cobertura existente | Estado |
|---|---|---|
| PC-01 | `tests/test_005_003_t1_compact_view.py:337-409`, `test_005_003_f2_idle_history.py:209-307` (sólo `entry`) | parcial |
| PC-02 | `test_005_003_t1_compact_view.py:337-366` | parcial |
| PC-03 | `test_005_003_f2_idle_history.py:209-307` (mitad `entry`/`next`) | parcial |
| PC-04 | — | sin cobertura (8 variaciones) |
| PC-05 | — | sin cobertura |
| PC-06/07/09/10 | — (semántica previa en `test_005_012_t5_approval_vigency.py`, sin proyección) | sin cobertura |
| PC-08 | superficie `draft-plan` en `test_004_003_t1_draft_contract.py:119-160`, sin proyección | parcial |
| PC-11 | **regresión nombrada**: `test_005_011_t3_view_action.py:452-525` | cubierta |
| PC-12 | `test_005_003_t1_compact_view.py:250-266` | parcial |
| PC-13 | `test_005_003_t1_compact_view.py:272-331` | parcial |
| PC-14 | — | sin cobertura |

**Ningún test existente queda obsoleto ni requiere ajuste**: no hay aserciones de conjunto o longitud exacta de las claves de la proyección (verificado con `rg`).

## Riesgos que el implementer debe respetar

1. `next.route` es prosa congelada por los dos tests PD-5; la acción estructurada va en `next.operation`.
2. `entry` no se toca (`continuity-reconcile` para preparado y despachado).
3. Límite de 16.384 B con fixture rico.
4. `big_doc == small_doc`: `record.pointer` apunta al **primer** registro aplicable y no se agregan contadores derivados del historial.
5. En reposo, `next.operation.source` no puede ser `docs/.cdad-state.json:execution` (test F2).

## Fixtures

Reutilizables: `test_004_002_t2_bootstrap.py:62-268`, `test_005_003_f2_idle_history.py:92-119` (`_packet_dir`), `test_005_013_t1_unit_projection.py:266-352` (`epic_history`), `test_004_003_t1_draft_contract.py:103-116`, `test_005_012_t5_approval_vigency.py:260-315`.

Matriz: PC-04 con 8 variaciones (execution_id ajeno, identidad, feature, rol/substage, request ilegible, sin `active_packet` con uno y con varios pendientes, explícito válido + pendientes); S1-S6 con las combinaciones bytes cambiados + sin registros y bytes cambiados + todos sustituidos; A1-A4; C1-C3; D1.

## Plan de RED (`tests/test_007_001_unambiguous_entry.py`, 14 tests)

Nombres exactos en spec §4. Caja negra por subproceso (`status --project-root <ABS>`), `HOME` en tempdir, helpers heredados, fallo RED siempre de aserción.

## Dudas resueltas por el orquestador (consulta al architect)

1. **Estado ilegible → `situation=diagnosis`**; `at-rest` exige estado legible (enmienda aplicada).
2. **S3 es alcanzable** con el selector vigente (`_superseded_transition_keys` recoge `supersedes` de cualquier entrada); el fixture describe el estado observado, no una secuencia válida del protocolo (enmienda aplicada).
3. **`observed_sha256=null` explícito** si se emite `contract` sin comprobar bytes (enmienda aplicada).
4. `next.operation.source` en `pending-work-unresolved` es **cadena exacta**: `docs/.cdad-state.json:active_packet / .cdad/packets`. Sin enmienda.
5. `unknowns`/`reason` nuevos se prueban por **concepto**; los diagnósticos anteriores, por comparación estricta. Sin enmienda.

## Evidencia

HEAD `1f2366f`, árbol limpio. Ningún archivo modificado por el rol. No hay `tests/test_007_001_unambiguous_entry.py` todavía.
