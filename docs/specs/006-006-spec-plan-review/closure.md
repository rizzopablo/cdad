# Cierre de 006-006-spec-plan-review

**Feature:** 006-006-spec-plan-review · **Epic:** `epic-006-opencode-concurrency` · **Cerrada:** 2026-10-20 · **Contrato:** `spec.md` sha256 `4d029a1178d4dbec6f589b69426402fb46ea7a49f324596837eba82bcd0ad298` y `plan.md`, aprobados el 2026-10-20, con la errata B-5 · **Aprobación:** orquestador Claude bajo la HITL delegada del epic-006, mantenida por el owner ese día. El owner autorizó los despliegues («cuando necesites hacer despliegue hazlo»).

## Qué entrega

- Revisión independiente de un borrador antes del RED. El borrador puede ser una spec sin plan, una spec con plan (identidad doble por digest) o el borrador de otra feature. El dictamen queda en la carpeta de la feature activa.
- Forma declarada del objeto (`--object-kind`, `--spec-path`, `--spec-version`) como extensión aditiva; por omisión la forma es `plan` y el comportamiento vigente no cambia.
- El dictamen nombra el objeto y su digest, y nunca aprueba.
- La exención entra en la identidad de la transición solo cuando se declara; las identidades históricas se conservan.
- Gate 2→3 supervisado, con `plan-review.md`; la política de compatibilidad entre revisiones queda declarada en `re-entry.md`.
- El rol reviewer declara la etapa 2; los agentes se generan desde la fuente.
- W-1: `--replace-packet` reemplaza un paquete de borrador preparado.

## Gates

| Etapa | Evidencia |
|---|---|
| U1–U5 | RED→GREEN por unidad (`u*-red.md`, `u*-green.md`, `u5-testfix.md`) |
| U6, recorrido real | `u6-acceptance.md`: E1–E7 cumplen. W-1 corregido (`w1-red.md`, `w1-green.md`) y verificado con el CLI desplegado: el paquete de reemplazo fija el digest de los bytes editados. W-2 es una observación |
| Review | `review.md`: apta para cierre, 0 B / 2 O. O-2 aplicado; O-1 queda como deuda |
| Suite de cierre | sobre `de629b8`+docs: **1404 passed, 5 skipped**, 0 fallas. En la corrida intermedia (U4) hubo 3 fallas de timing del waiter que pasan en aislado |
| `make validate` | 168 PASS / 1 FAIL F011: deriva `.pyc` (DT-8) y agentes personalizados del owner preservados |
| Despliegue | HOME en `86cb942` (código `de629b8`), con respaldo en `archive/`; `--check` muestra solo deriva `.pyc` |
| Memory Bank | borradores del scribe (`scribe.md`) aplicados, con una corrección de texto corrupto («suman») |

## Deuda declarada

- O-1: automatizar el selector de vigencia B/C de la errata B-5. Se verificó a mano y no tiene defecto.
- W-2: el adaptador termina con rc=0 aunque el resultado sea `blocked`.
- Deuda de la spec: nombres `draft-plan`/`plan-review`; exención como acto de autoridad; compatibilidad entre revisiones.
- Heredada de 006-005, sin cambios: U6-2, O-2, D-U65-4/5, O-2/O-3 de sus reviews, transporte del paquete nativo, DT-8, DT-9.
