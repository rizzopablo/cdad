# 005-004 — Suite de cierre (orquestador Claude, 2026-10-13)

**Corrida en un worktree fijado a `c8ab21f`, con `make staging PROFILE=basic`:** 915 passed, 2 failed, 4 skipped (17 min).

1. **`test_005_009_t3_spawn_reconciliation.py::test_inv8_no_unbacked_isolation_promise[claude-code-delegation]` — regresión real de T4.**
   - **Causa:** el texto reformateado de `claude-code-delegation.md` dejó «the guarantee is» en una línea y la negación («not **structural**») en la siguiente. El oráculo de INV-8 de 005-009 trabaja línea por línea.
   - **Por qué no se detectó antes:** las regresiones declaradas de T4 no incluían ese módulo.
   - **Corrección (`5d6f667`):** se reformatea el texto para que la negación quede en la misma línea, sin tocar el test. La hizo el orquestador como desviación declarada: es un cambio de una línea de documentación, y el oráculo es el test existente.
2. **`test_install_review5_regressions.py::…::test_review5_b4_basic_request_vs_staging_profile_labels_coherent` — error del lanzador, no del producto.**
   - **Causa:** el test exige que el staging esté construido con el perfil por defecto, y yo lo construí con `PROFILE=basic`.

**Verificación en `5d6f667`, en un worktree nuevo con `make staging` (perfil por defecto):**
- **Módulos corridos:** los cuatro focales de 005-004, `test_005_009_t3_spawn_reconciliation.py` y `test_install_review5_regressions.py`. Resultado: 55 passed.
- **`make validate`:** 155 PASS / 1 FAIL. El fallo es F011, que ya existía (deuda D-6).
- **Equivalencia:** el resto de la suite se toma como equivalente por referencia (`re-entry.md`, *Equivalence of a registered run*), porque entre `c8ab21f` y `5d6f667` solo cambia esa línea de documentación.

**Deuda de proceso:**
- las regresiones de una tarea que edita un reference deben incluir los oráculos de texto que lo cubren (aquí, INV-8 de 005-009);
- el procedimiento de la suite de cierre debe fijar el perfil de staging.

## Precisiones posteriores (revisión de Codex, 2026-10-13)

- **El fallo 1 no es una regresión del producto.**
  - El texto ya negaba que la garantía fuera estructural; solo repartía la frase en dos líneas, y el oráculo de INV-8 de 005-009 la leyó mal.
  - Unir la línea fue una salida práctica para cerrar.
  - Deuda: el oráculo debe ser menos frágil, por ejemplo evaluando la frase completa y no línea por línea.
  - Lo mismo vale para las comprobaciones de los focales nuevos de 005-004 que juzgan el significado de un párrafo con listas de palabras.
    - Las comprobaciones mecánicas de herramientas, modelos, instalación y hooks se mantienen.
    - La corrección semántica de las explicaciones es materia de review: la búsqueda de frases ayuda, pero no es garantía.
- **La equivalencia abarcó dos cambios, no uno.** Entre la corrida y la verificación cambiaron la línea y el perfil del staging (de `basic` al perfil por defecto).
  - Con el perfil por defecto se corrieron los focales de 005-004 y los dos módulos que fallaron (55 passed).
  - El resto de la suite pasó con `basic`. No se identificó qué otros tests dependen del perfil, así que la equivalencia para el perfil por defecto es parcial y se declara así.
- **`git stash`:** el riesgo concreto es retirar cambios ajenos de un árbol compartido. No se agrega una barrera por comando; los encargos dan el procedimiento de trabajo aislado (un worktree) y el gate comprueba que se cumpla.
