# Cierre 008-003-lifecycle-decision-model

Fecha: 2026-10-27. Epic: `epic-008-suite-coherence`. Feature 3 de 6.

## Resultado

Packet, continuidad y recepción **deciden identidad, propietario, autoridad, replay y conflicto en un
núcleo compartido** (`skills/cdad-cycle/scripts/cdad_lifecycle.py`, nuevo, 408 líneas) y los consumidores
conservan sólo lectura, verificación física y publicación. Las **15 ramas decisorias locales** migradas
desaparecieron de los tres consumidores, incluidos los **bordes programáticos** (`plan_write`,
`close_durable_receipt`), que antes sólo pasaban por la guarda cuando se invocaban por CLI.

## Contrato

`docs/specs/008-003-lifecycle-decision-model/spec.md` — 6 PCs, plan de extracción y adopción. Decisiones
del orquestador: opción A del discovery (núcleo puro, **sin fachada**); la tabla `termination/delivery`
queda fuera (sus dueños no cambian).

## Cambios

- `cdad_lifecycle.py` (nuevo): `resolve_execution_identity`, `classify_authority`, `require_authority`,
  `require_epic_binding`, `scope_names_epic`, `resolve_owner`, `require_owner_operable`,
  `require_concordant`, `is_resumed_unit_checkpoint` y cuatro reglas de dominio —
  `decide_continuity_write`, `decide_continuity_close`, `decide_transition`, `decide_receipt`. Sin I/O,
  sin reloj (la fecha entra como parámetro) y sin importar consumidores.
- `cdad_continuity.py` (+401): guarda compartida en `plan_write`/`close_durable_receipt`; orden §4.4
  (identidad → replay → elegibilidad); `_accredited_unit`/`_owner_decision`/`_require_unit_identity`/
  `_require_owner_operable`.
- `cdad_packet.py` (+198): replay de cierre y de transición vía núcleo; el checkpoint de suspend/resume
  declara el estado proyectado.
- `cdad_result.py` (+65): replay durable **antes** de la suspensión; comparación de recibo vía núcleo.

## Evidencia

- RED `9d2d3c7` (5 tests; PC-01..04 rojos por causa medida, PC-05 guarda verde). GREEN `06ab12f`.
- Review con **3 bloqueantes estructurales**: guarda ausente en bordes programáticos; elegibilidad antes
  del replay (contradecía §4.4); y el núcleo recibía el replay **ya decidido** por el consumidor (fachada).
  Cerrados en `8b4f99b`; el inventario antes/después tiene 15 ramas con archivo:línea.
- Un defecto del **test** (fotografía de cuerpos tomada antes de un avance legítimo) corregido en
  `cb2dc98`; y un error del **orquestador** (declarar `close_durable_receipt` como compute-only cuando
  publica por diseño) corregido en `5266ed7`.
- Guardas de regresión agregadas: `d7a1d6d` (orden replay→elegibilidad tras revocación y suspensión, en
  escritura y recepción), `e162294` (bordes programáticos con control positivo), `5266ed7` (control de
  publicación).
- **9/9 tests** del módulo, verificado por el orquestador además del rol.
- Suite focal amplia (42 archivos de continuidad, recepción y transiciones): **440 passed**.
- **Gate de cierre:** ver «Gate».

## Gate

`python3 scripts/cdad-suite.py close --evidence-root .cdad/local/008-003/evidence --all`

| Dato | Valor |
|---|---|
| Intento | `attempt-20261027T225955301275Z-2686195-a6659aa6` |
| Resultado | **1783 passed, 5 skipped, 0 failed, 0 errors** |
| `rc` | **0** |
| `verified` | **true** |
| Canario | **delta 0** |
| Duración | 58:44 |

Los 5 skips son los opt-in reales de siempre (005-002 ×2, 005-009, 005-010 PD-8, 006-001 PD-6b).

## Deuda y límites

- **SUSP-IDENTITY:** el review dijo que la evidencia **no alcanzaba** con el primer GREEN (faltaba el borde
  programático y PC-06). Con `8b4f99b` + las guardas `e162294`/`5266ed7`, los tres bordes quedan cubiertos
  por test; el cierre efectivo de la deuda se declara **condicionado a esta evidencia**, no automático.
- **SUSP-GUARD:** cierre **parcial**: la guarda es única para evidencia disponible. Sigue abierto el límite
  de borrar contexto y registro para aparentar standalone; centralizar no recupera evidencia borrada.
- **SUSP-LOCK:** **no cierra** — falta coordinación de escritores; el decisor es puro y no elimina carreras.
- **SUSP-APPROVAL:** **no cierra** — decidir con evidencia existente no restaura aprobaciones borradas.
- `resume_unit` y la clasificación de retiro conservan ramas locales de vigencia, fuera de la superficie
  declarada: deuda explícita, no decisión migrada.
- La tabla `termination/delivery` de `cdad_dispatch`/`cdad_delegate` queda fuera de alcance por decisión.
- **Hallazgo de producto (media):** `begin` acepta como referencia un archivo que cae dentro del
  `write_scope` del propio paquete, y entonces el `record` siempre falla por P1. Ocurrió **cuatro veces**
  en este epic. Debe rechazarse en `begin` o advertirse; mientras tanto la regla operativa es no citar
  archivos que el rol edita.
