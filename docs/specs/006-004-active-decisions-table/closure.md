# 006-004 — cierre de la feature

Status: cerrada el 2026-10-22 por el orquestador bajo la delegación HITL amplia del owner. **No está desplegada en HOME:** el owner lo pidió así porque hay una sesión activa en OpenCode, y el despliegue queda pendiente de su orden.

## Gates

| Gate | Resultado |
|---|---|
| Unidades U1–U5, U7 (RED/GREEN) y U6 (recorrido real) | hechas; informes en esta carpeta; `u6-acceptance.md` cumple E1–E7 y V-5 |
| Review de etapa 4 (`review.md`) | B-1 corregido (RED `4d71ccc`, GREEN `fc1179b`); B-2 resuelto por el orquestador (`execution.md`, `6aeeb48`); O-1..O-3 a deuda; W-U6-2 abstención |
| Focales `tests/test_006_004_*.py` | 56 passed |
| Suite completa | 1458 passed, 5 skipped, 2 failed. Los dos fallos son intermitentes y están en módulos que 006-004 no toca (`git diff 86cb942..HEAD` vacío sobre ellos y sobre el adaptador). `test_005_010_t2…::test_pd4_server_config_uses_server_without_standalone` pasa aislado. `test_006_001_t1b…::test_pd13_no_management_invocations_in_any_mode` pasa aislado y falla 1 de 3 veces al repetir el módulo |
| `make validate` / `validate-consistency.sh` | solo F011, la deriva ambiental conocida de la copia instalada |
| Memory Bank | `activeContext`, `progress` y `systemPatterns`, desde el borrador del scribe (`scribe.md`), aplicados sin cambios de contenido |

## Deuda que se lleva

- O-1..O-3 de la review: pertenencia a `docs/adr/` por prefijo; marcas de borrador residuales en ADR-034; el bloque U3 en el validador bash.
- W-U6-1: la fidelidad del scribe (cambia líneas no pedidas).
- W-U6-2: re-despacho de un paquete ya entregado, a reproducir.
- W-U6-3: el adaptador solo entrega `role-report` hacia el Memory Bank.
- `scope_validation: unknown` (U6-2 de 006-005).
- Flake nueva: `test_pd13_no_management_invocations_in_any_mode`, intermitente.
- Despliegue a HOME pendiente.
