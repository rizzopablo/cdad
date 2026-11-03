---
feature_id: 014-002-pd10-window-drift
approved_by: Pablo (HITL delegada, docs/epics/epic-014-suite-evidence-policy/execution.md)
approved_at: 2026-11-02
source: redactada por el orquestador por ser una corrección mínima de un oráculo (ADR-003); sin sesión de architect
---

# 014-002 — Ventana desfasada en el oráculo PD-10

## Contexto (evidencia)

La suite completa de cierre del epic 014 (`.cdad/local/epic014/gate-20261102T150101489105Z-2024645-560258da`,
commit `e9969d9e`) dio 1947 passed, 5 skipped, **1 failed**:
`tests/test_005_006_t1_start_procedure.py::test_pd10_installed_cli_paths_in_t1_wiring_points`.
Falla en `c4271693` y pasa en `0eab565c` (introducido en el epic 013 por corrimiento de líneas de `SKILL.md`; ese
epic cerró sin suite completa). El punto de cableado `|continuity.md| … <skill-dir>/scripts/cdad_continuity.py`
está hoy en `skills/cdad-cycle/SKILL.md:466-467`; el test lo busca en la ventana fija 444-464.

## Promesa

El oráculo PD-10 vuelve a verificar lo que promete —que los puntos de cableado de `SKILL.md` invocan al CLI con la
ruta derivada de `<skill-dir>`— sin depender de un número de línea que cualquier edición desplaza.

**PC-1.** El test ancla el punto de cableado de la tabla de carga por su contenido (la fila de `continuity.md` /
`project-execution.md` de la tabla «How to read the references») o, como mínimo, usa una ventana que lo contiene con
holgura; sigue exigiendo que haya al menos una invocación al CLI y que ninguna quede sin el marcador `<skill-dir>`.

**PC-2.** Sensibilidad: si en esa fila se quita el marcador `<skill-dir>` de una ruta `scripts/cdad_*.py`, el test
falla; si la fila desaparece de la ventana/ancla, el test falla.

## Invariantes

- Solo cambia `tests/test_005_006_t1_start_procedure.py` (test-writer). No se toca `SKILL.md` ni otros contratos
  cerrados (005-006).
- Sin cambios de comportamiento del producto.

## Aceptación

`pytest tests/test_005_006_t1_start_procedure.py` verde con el cambio; PC-2 comprobada por mutación local sobre una
copia; el cierre del epic repite la suite completa.
