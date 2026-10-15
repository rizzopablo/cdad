# Suite de cierre — 005-012-transition-registration

La corrió una sola vez el orquestador Claude, que coordina el cierre, el 2026-10-14.

- **Versión:** worktree fijado en `6fd515d`, que incluye T1–T7, los review-fix B1, B2 y B3 y la evidencia
  de T8. Se armó con `make staging` en el perfil por defecto.
- **Suite:** `python3 -m pytest tests -q -p no:cacheprovider` → **1024 passed y 4 skipped, sin fallos**
  (20 min).
- **`make validate`:** 155 PASS y 1 FAIL. El fallo es **F011**, que ya existía antes (D-6 de 005-011).
- **T8 se repitió sobre `6fd515d`**, después de B3, con el mismo arnés del orquestador copiado dentro del
  worktree: AC-1..AC-4 dan los mismos resultados que la corrida registrada en `acceptance.md`. AC-1 hizo
  8 invocaciones, todas con rc=0, y registró 7 entradas, todas de la operación, sin edición manual.
  Con esto la aceptación queda en el mismo commit que el cierre. La primera repetición, con el arnés
  copiado fuera del repo, no vale como evidencia: el arnés ubica el CLI a partir de su propia ruta.
- **Equivalencia:** el código no cambió entre `6fd515d` y este registro. Después solo se agrega la
  documentación del cierre.
