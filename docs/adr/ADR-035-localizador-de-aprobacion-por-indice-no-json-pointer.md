# ADR-035: El localizador del registro de aprobación se emite por índice 0-based con historial determinado por el objeto, no como JSON Pointer

- **Status**: Accepted (2026-10-23; aprobado por el orquestador bajo HITL delegada del dueño, epic-007).
- **Date**: 2026-10-23
- **Deciders**: orquestador del epic-007 (autoridad delegada); autor de la spec y test-writer (evidencia). El scribe no aprueba.
- **Confidence**: Alta. La alternativa elegida está verificada por los tests de la feature (49 casos incluyen `record.index` 0-based y la ausencia del token del historial); la rechazada está reproducida contra una garantía aprobada con test propio (`tests/test_005_003_t1_compact_view.py:228,325`). Queda Media en un punto: el consumidor deriva el historial de `object`, y todavía no lo ejerce ningún consumidor externo.
- **Contrato**: `docs/specs/007-001-unambiguous-entry/spec.md` §2.3 y §6; verificación `tests/test_007_001_unambiguous_entry.py`, `review-003` APTO.

## Contexto y problema

La vista compacta (`cdad_packet.py status`) debía mostrar la referencia verificable al registro de aprobación aplicable al rol y objeto del request. «Verificable» exige un localizador: algo que permita ir del registro proyectado al registro real en `docs/.cdad-state.json`.

El borrador pedía un JSON Pointer al registro del historial. Un pointer nombra su contenedor, y el contenedor se llama `stage_history`. La garantía PD-1 —vigente y de otra autoridad— prohíbe ese token en la salida, porque su objetivo es que el historial no se proyecte:

- `tests/test_005_003_t1_compact_view.py:228` — `assert "stage_history" not in proc.stdout`
- `tests/test_005_003_t1_compact_view.py:325` — ídem con historial grande

No era un detalle de formato: era una contradicción entre dos contratos aprobados.

## Opciones

**A. Índice 0-based con historial determinado por `object` (adoptada).** `record.index` es el índice del registro seleccionado en el historial que determina `object` (`stage_history` para `feature-spec`, `epic_history` para `epic-plan`). No se emite el nombre del historial ni el historial; `transition_key` puede ser `null`; para `desconocida`, `record` sólo conserva un registro si su selección se comprobó independientemente, y nunca se fabrica un localizador. Ventajas: localiza igual, no emite el token, no toca PD-1 ni sus tests, conserva INV-6. Coste: no es autosuficiente — el consumidor deriva el historial de `object`.

**B. JSON Pointer (rechazada).** Autosuficiente y estándar, pero viola PD-1; arreglarlo exigía enmendar dos tests aprobados, es decir relajar una garantía vigente para acomodar una feature nueva. Ese orden de prioridades es el que el proyecto no acepta.

**C. Registro sin localizador (rechazada).** Cero riesgo, pero contradice el requisito que originó la feature (AC-7.2): un `status` sin localizador es una afirmación, no una referencia verificable.

**D. Pointer con alias del historial (rechazada).** Evita el token inventando un vocabulario de alias y convierte el localizador en un dato que no existe en el estado: deja de ser verificable.

## Decisión

Se adopta **A**, con dos partes que conviene no confundir:

1. **Forma:** `record.index` entero 0-based, historial determinado por `object`. Interfaz estable para 007-002..004, que podrán alimentarla pero no cambiar nombres, tipos ni significados.
2. **Precedencia entre garantías:** una feature nueva no relaja una garantía aprobada para caber en ella; se busca la forma de cumplir ambas. Aquí el índice cumple la verificabilidad sin emitir el token y sin enmendar ningún test aprobado.

## Consecuencias

- **Positivas:** PD-1 intacta y verificada; referencia verificable sin volcar historial; límite de 16.384 B conservado; semántica del índice fijada por `object`, no por el nombre del historial.
- **Negativas / coste asumido:** localizador no autosuficiente; el mismo índice en historiales distintos es un localizador distinto y sólo `object` desambigua; registros sin `transition_key` dejan ese campo en `null`.
- **Neutral:** `desconocida` puede quedar con `record=null`; no se fabrica un localizador para completar la vista.

## Cumplimiento

- `skills/cdad-cycle/scripts/cdad_packet.py` — proyección de `authority.approval_reference` y `record.index`.
- `tests/test_007_001_unambiguous_entry.py` — índice 0-based por objeto y ausencia del token; `tests/test_005_003_t1_compact_view.py` permanece sin modificar.
- `docs/specs/007-001-unambiguous-entry/spec.md` §2.3 y §6.
