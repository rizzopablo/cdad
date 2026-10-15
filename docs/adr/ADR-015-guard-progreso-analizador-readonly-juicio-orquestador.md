# ADR-015 — El guard de progreso es un analizador read-only; el juicio es del orquestador

## Estado
Aceptado (dueño, 2026-10-07).

## Contexto
El desarrollo real sufre interrupciones y repeticiones improductivas (2.073 reintentos
idénticos en un caso, ~20 h). Un supervisor que consuma más que el trabajo que evita, o
que decida semánticamente, agrava el problema. La spec de 003-003 resolvió D1–D11 y el
dueño enmendó la frontera del preflight (2026-10-06): un rechazo no es mala conducta y
salir de la raíz del proyecto se habilita por defecto.

## Decisión
`skills/cdad-cycle/scripts/cdad_guard.py` es un **analizador determinista read-only**
sobre señales ya existentes (DB de sesiones, artefactos 001/002):
1. `classify` detecta repetición sin progreso y polling legítimo sobre trazas grabadas
   (`trace-v1`), con dedup por token de relevancia.
2. `preflight` es **consultivo**: solo `deny` con regla explícita; fuera de la raíz ⇒
   `allow`; sin destino resoluble ⇒ `unknown`.
3. `record`/`budget` persisten eventos/presupuesto **durables** bajo
   `.cdad/executions/<id>/guards/**`, keyed por `execution_id+packet_id+attempt`; el
   guard **nunca** escribe `docs/.cdad-state.json` ni repite efectos.
4. El canal de escalado usa una **tabla cerrada evento→acción** (solo acciones
   reversibles); la ambigüedad vuelve al orquestador.
El guard nunca cambia spec, autoridad ni prioridad, y no concede/endurece permisos.

## Alternativas consideradas
- **Controlador/supervisor LLM permanente:** descartado (consume más de lo que ahorra;
  prohibido por el epic y el handoff del architect).
- **Techo mecánico nuevo / auto-bloqueo duro:** descartado; `steps:300` sigue siendo el
  único techo y su enforcement no está probado en vivo (V5).
- **Hash del output completo para equivalencia:** descartado por frágil; la huella es
  `tool + args canonicalizados + clase de resultado`, evidencia por referencia.

## Consecuencias
- (+) Supervisor barato y auditable; juicio humano/de orquestador preservado; interfaces
  durables keyed por `execution_id` no obstaculizan 003-004.
- (−) Su utilidad depende de que el orquestador consuma el canal; el lector en vivo
  (grabador) es deuda (G1) y en el primer uso real el guard no detectó los incidentes
  reales C1/C2; el digest de progreso por rutas es de grano grueso (deuda media).
- (−) El mapa de capacidades por rol del preflight (D6) queda parcial (conjunto genérico
  `WRITE_TOOLS`, O-D declarada).

## Confianza
**Media.** La separación analizador/orquestador y el presupuesto durable están
verificados por tests y por uso (consistente con ADR-003/ADR-011/ADR-014); la **utilidad
medida** del guard es baja en su primer uso real honesto y la calibración de severidad
(contenido vs rutas, preflight) queda como deuda con uso real.
