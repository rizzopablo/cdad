# Mandato HITL del dueño — 2026-10-30

Registro durable del mandato explícito del dueño del proceso para esta unidad y el
resto de `epic-010-documentary-specialization`. Autoridad superior: el plan del
epic `docs/epics/epic-010-documentary-specialization/plan.md` (aprobado por Pablo,
2026-10-29) y su mandato de orquestación
`docs/epics/epic-010-documentary-specialization/execution.md` (2026-10-29).
Este documento **no** reemplaza esos contratos: registra la delegación HITL que el
dueño acaba de ampliar por instrucción literal.

- **Otorga:** Pablo, dueño del proceso y aprobador del epic-010.
- **Registra:** orquestador CDAD (sesión subagente autorizada por el orquestador
  supervisor del epic).
- **Fecha de registro:** 2026-10-30 (UTC `2026-10-30T16:03:59Z`, reloj del
  entorno verificado antes de escribir).
- **Feature activa al registrar:** `010-004-packet-dispatch-ergonomics`
  (ejecución `exec-010-004-packet-dispatch-ergonomics-001`), etapa `tdd`,
  subfase `audit`.

## Cita literal de la instrucción

«Te delego hitl, eres el dueño del proceso, toma decisiones con criterio amplio
pensando en el uso real del sistema por el usuario final. Continúa orquestando
proactivamente hasta completar las correcciones pendientes y el epic completo.»

## Qué autoriza

1. **Aprobar en nombre de Pablo los gates operativos del ciclo** de esta unidad
   (`010-004-packet-dispatch-ergonomics`), empezando por el AUDIT T1 y siguiendo
   con los que el plan aprobado exija: POST-AUDIT, RED, GREEN, refactor,
   properties, E2E, revisión y cierre. Cada aprobación se registra con su
   fundamento, la evidencia verificada y la referencia a este mandato y a la
   recomendación técnica que la sostiene; nunca en silencio.
2. **Resolver las ambigüedades funcionales que el AUDIT escala**, eligiendo la
   opción trazable al contrato y a la recomendación técnica, y registrando la
   decisión (ver `audit-approval-2026-10-30.md`, resoluciones A1 y A2).
3. **Continuar el epic-010 completo** —`010-001-documentary-contracts`,
   `010-002-documentary-role-integration`, `010-003-documentary-pilot`,
   integración y cierre— sin volver a detener el ciclo pidiendo aprobaciones
   rutinarias de gate, incluidas las aprobaciones que el plan del epic exige
   para specs y planes de esas features **en tanto implementen la descomposición
   y el alcance ya aprobados** en `plan.md` (§Descomposición, §Alcance,
   §Criterios de aceptación).
4. **Operar con criterio amplio orientado al uso real del sistema**: elegir la
   solución más simple que sostenga el contrato, evitar mecanismos nuevos sin
   necesidad demostrada, y no dejar deuda silenciosa (toda falta de cobertura o
   limitación se declara con su motivo).

## Qué NO autoriza

- **No cambia contratos ya aprobados**: `spec.md` de 010-004 conserva su pin
  `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64` y
  `plan.md` su pin `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685`.
  Ninguno de los dos se edita para aprobar un gate.
- **No cambia el alcance ni la descomposición del epic-010**: features, orden,
  dependencias, criterios de aceptación y exclusiones de `plan.md` quedan como
  están. Un cambio real de alcance, una feature nueva o un criterio nuevo vuelven
  al dueño.
- **No relaja evidencias ni gates**: no convierte una recepción en aprobación, no
  autoriza saltar AUDIT/POST-AUDIT/RED, no acepta un RED que falle por
  `ImportError`, no reduce severidades de bloqueantes y no permite que un rol
  audite o apruebe su propio trabajo. El aislamiento de roles (test-writer sin
  implementación, reviewer read-only en sesión distinta) se mantiene igual.
- **No autoriza publicación, push, deploy ni actualización de la instalación
  global.** Esa instrucción sigue siendo del dueño; si existiera una instrucción
  previa vigente de squash al cierre, este mandato no la amplía.
- **No se hereda** a otras épicas ni transfiere autoridad sobre proyectos
  consumidores, y no autoriza cambios de modelos ni de configuración del runtime.
- **No permite reescribir historia**: recibos, paquetes emitidos, state,
  `stage_history` y specs históricas (`004-002`) se conservan; las correcciones
  se hacen en la fuente y se publican por el cauce normal.

## Vigencia y revocación

- **Cubre** la unidad `010-004-packet-dispatch-ergonomics` completa y el resto del
  `epic-010-documentary-specialization` hasta su cierre (incluida la integración
  entre features y el cierre del epic).
- **Vence** al cerrar o cancelar el epic-010.
- **El dueño puede revocarlo en cualquier momento**, sin causa y sin efecto
  retroactivo sobre lo ya registrado: la revocación se anota aquí con fecha y se
  refleja en `state.hitl_delegation` (`revoked_at`), que es el control que hace
  fallar cerrado los gates siguientes con `approval pending`. Desde ese momento el
  orquestador vuelve a detenerse en cada gate que exija aprobación del dueño.

## Trazabilidad y efectos registrados

- `state.hitl_delegation.mandate_ref` apunta a este documento, con la cita literal
  en `mandate_quote` y el alcance en `mandate_scope`. `source` y `epic_mandate`
  conservan `docs/epics/epic-010-documentary-specialization/execution.md` como
  referencia de autoridad que el CLI verifica contra `execution.authority_ref`.
  Ambas fuentes coexisten: `execution.md` describe el alcance de orquestación,
  este documento amplía la dimensión HITL. Hay además una entrada activa en
  `state.delegation_history` con este documento como fuente.
- Aplicaciones de este mandato, en orden:
  1. Aprobación del AUDIT T1 de 010-004 —
     `docs/specs/010-004-packet-dispatch-ergonomics/audit-approval-2026-10-30.md`
     (incluye las resoluciones A1 y A2 con su fundamento).
  2. Paso habilitante V2-1 (plantilla POST-AUDIT mono-subfase) preparado como
     paquete `implementer/green` de esta unidad, bajo la decisión owner
     `owner-decision-plan-v2-1.md`.
- Este registro no acredita por sí mismo ningún trabajo de rol: los resultados se
  reciben por el mecanismo de re-entrada, con su recibo, y las aprobaciones
  quedan en `stage_history` con el aprobador declarado.
