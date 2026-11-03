# Closure — 014-002-pd10-window-drift

**Epic:** `epic-014-suite-evidence-policy` — orden 2/2. **Cerrada:** 2026-11-02.
**Contrato:** `docs/specs/014-002-pd10-window-drift/spec.md` (aprobado por HITL delegada). No publicada ni desplegada.

## Resultado
`test_pd10_installed_cli_paths_in_t1_wiring_points` ancla el punto de cableado por contenido (filas `continuity.md` y
`project-execution.md` de la tabla de carga, una a una) en vez de una ventana por número de línea. Commit `acdab25d`
(solo `tests/test_005_006_t1_start_procedure.py`).

## Evidencia
- Antes: falla por AssertionError (razón correcta). Después: 15 passed en el archivo.
- Sensibilidad PC-2 (mutación en copia, informada por el test-writer): quitar `<skill-dir>` → falla; quitar cualquiera
  de las dos filas → falla. Un OR global enmascaraba la desaparición de una fila; por eso se verifica por fila.
- Sin revisión independiente de esta corrección (cambio de un oráculo, verificado por el orquestador): límite declarado.

## Deuda
- Sigue habiendo oráculos de ventana por número de línea en este y otros archivos de test (p. ej. ventanas 250-276 y
  277-443 del mismo test); cualquier edición de `SKILL.md` puede desplazarlos. Se detecta solo con suite completa.
