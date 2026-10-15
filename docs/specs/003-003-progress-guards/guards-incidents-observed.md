# Incidentes reales observados durante 003-003 (insumo para T5 / guards-ledger)

| Fecha | Caso | Situación | Evidencia | Recuperación aplicada |
|---|---|---|---|---|
| 2026-10-06 | C2 (artefacto de `opencode run`, ver guards-ledger) | El implementer lanzó la suite completa en segundo plano; murió al terminar la sesión | `dispatch-ledger.md` fila 6; salida del run `green-t1-003-003-a1` | Reanudación de la misma sesión con instrucción de correr en primer plano; 445 passed |
| 2026-10-06 | C1 (artefacto de `opencode run`) | El implementer cerró el turno «esperando ser retomado automáticamente» sin entrega final | ídem | Misma reanudación; entrega completa |
| 2026-10-06 | (orquestador) | El seguimiento del orquestador usaba `pgrep -f <título>`, que se encontraba a sí mismo: horas sin detectar fin real | conversación del orquestador | `launch.sh`/`watch.sh`: PID real + `.rc` + inactividad (DONE/GONE/STALLED) |
| 2026-10-06 | C2+C1 (repetido) | El implementer de T2 review-fix volvió a mandar la suite al fondo y cerró el turno esperando una notificación, pese a la instrucción explícita | ledger, fila 16 | Reanudación con «un solo comando bloqueante, timeout de la herramienta 1500000 ms»: 459 passed |
| 2026-10-06 | C2 (orquestador) | La reanudación lanzada por el orquestador murió al terminar su shell de espera (sin setsid) | ledger, fila 17 | `launch.sh` con setsid; el PID lo escribe el propio hijo |
