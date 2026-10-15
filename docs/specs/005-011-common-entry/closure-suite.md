# 005-011 — Suite de cierre (orquestador Claude, 2026-10-13)

- **Versión:** worktree fijado a `d862056`, que incluye T1–T3 y la corrección de OP-1/OP-2, con `make staging` en el perfil por defecto.
- **Suite:** `python3 -m pytest tests`, 927 passed y 4 skipped, sin fallos (17 min).
- **`make validate`:** 155 PASS / 1 FAIL. El fallo es F011, que ya existía (D-6).
- **Validez para el cierre:** se corrió antes del despliegue. Si T4 solo agrega documentación, esta corrida es la suite de cierre. Cualquier cambio de producto posterior exige volver a correrla.

## Segunda corrida, después de T2b (2026-10-13)

- **Versión:** worktree fijado a `8ec574d`, que incluye T2b y el puntero al inicio del prompt del orquestador, con `make staging` en el perfil por defecto.
- **Suite:** 927 passed y 4 skipped, sin fallos (17 min).
- **`make validate`:** 155 PASS / 1 FAIL. El fallo es F011, que ya existía.
- **Validez:** reemplaza la corrida en `d862056` como suite de cierre, porque T2b cambió producto (la fuente del orquestador y los agentes generados).
- **Desviación declarada:** el puntero al inicio (`8ec574d`) lo agregó el orquestador Claude. Es una línea de texto que remite a la entrada de T2b sin repetir la regla. Guardas de texto y del generador: 83 passed.
