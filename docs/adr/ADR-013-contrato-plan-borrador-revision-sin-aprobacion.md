# ADR-013 — El contrato de plan borrador (`draft-plan`) separa revisión de aprobación

## Estado
Aceptado (2026-10-05) — origen: feature `004-003-planning-procedures` (epic
`epic-004-single-source-planning`). Aprobado por el dueño (HITL delegada al
orquestador). Borrador del scribe materializado por el orquestador (ADR-003).

## Contexto
El renderer de paquetes soportaba dos contract-kinds: `approved-feature-spec` para
`reviewer/review` (y el resto de los roles) y `approved-epic-plan` para el
architect. Revisar un **plan borrador antes de aprobación** no cabía honestamente
en ese contrato (`docs/epics/epic-004-single-source-planning/plan.md:284-289`):
falsificar `approved` o reutilizar un tipo incompatible para pasar el guard estaba
prohibido.

Esa brecha (D8) bloqueaba al architect (`prepare` rc=2 por el requisito I2 de
`stage_history`) y no permitía revisar un plan sin aprobarlo. Fue la causa del
"handoff legacy identificado" con que arrancó 004-003.

## Opciones consideradas

### Opción A: `draft-plan` como contract-kind nativo, sin marca de aprobación
- **Pros:** revisión de primera clase con versión y `authority_ref`; separa el
  artefacto revisado del estado de aprobación; el guard detecta la forja
  (`approved-*` + `plan_version`); habilita el primer paquete v2 del architect.
- **Contras:** superficie nueva (flags + enum + esquema) que reconciliar en los
  consumidores; riesgo de misroute entre subfases y kinds.

### Opción B: handoff legacy mientras se migra
- **Pros:** cero cambios de contrato.
- **Contras:** no revisa un borrador como contrato de primera clase; mantiene la
  brecha D8 y el trabajo sin paquete.

### Opción C: reutilizar `approved-*` con una bandera de "borrador"
- **Pros:** sin enum nuevo.
- **Contras:** falsifica la aprobación; contradice la regla del epic y el
  invariante "revisión ≠ aprobación". **Descartada.**

## Decisión
`draft-plan` es un contract-kind de primera clase que **no aprueba**: la emisión
lleva el sha/versión del borrador y un `purpose` no aprobatorio
(`draft plan for review`); la forja `approved-*` + `plan_version` se rechaza
(rc≠0, sin publicación). El objeto borrador solo es admisible en la subfase
`plan-review` del rol `reviewer`, con pairing bidireccional enforce en
`validate_request` (punto único). La revisión de plan corre sobre el rol reviewer
existente — no un planner ni un sub-agente nuevo.

## Razones
1. Separa artefacto revisado, referencia de autorización y estado de aprobación
   (PD-1/PD-3).
2. Cierra la brecha D8 sin falsificar `approved`.
3. El guard de forja es estructural y localizado (<10 líneas + esquema).

## Consecuencias
- **(+)** Plan borrador revisable desde el producto instalado, en sesión
  independiente del autor; primer paquete v2 del architect habilitado.
- **(+)** `prepare` sigue siendo el único productor; sin productor paralelo.
- **(−)** Superficie nueva que reconciliar en `VALID_CONTRACT_KINDS`, el esquema,
  `ROLE_SUBSTAGES` y las fuentes de rol (hecho en 004-003).
- **(−)** `--contract-path` de `draft-plan` acepta hoy cualquier archivo del
  proyecto (deuda O-C de la segunda mirada).
- **Neutral:** la regla de equivalencia/re-entry (PD-5/PD-6) es disciplina del
  orquestador, sin enforcement ejecutable (límite declarado).

## Confianza
Media-Alta — verificado en vivo por T1/T2/T7: el par válido
(`reviewer`, `plan-review`) + `draft-plan` renderiza rc=0 y el borrador no se
aprueba; los negativos de forja y de misroute fallan rc≠0 sin publicación; el
recorrido real (T7) preparó el paquete `plan-review` sobre el replan de 003-002
(rc=0) y el plan siguió `draft`. El enforcement del pairing se verificó
estructuralmente en un punto único (`cdad_packet.py:729-739`). No hay barrera
mecánica sobre `--contract-path`.
