# Mandato de orquestación — epic-010-documentary-specialization

## Fuente y aprobación

El usuario indicó «Listo, avanza como orquestador» y aprobó el plan presentado
con «Aprobado» el 2026-10-29 en esta sesión. El alcance aprobado está en
`docs/epics/epic-010-documentary-specialization/plan.md`.

## Alcance delegado

epic-010-documentary-specialization: registrar el plan aprobado y sus features,
preparar y delegar encargos por rol, verificar gates con evidencia, materializar
resultados de roles read-only y ejecutar git de documentación/estado. Incluye
Discovery de 010-001-documentary-contracts. No hereda mandatos de otras épicas.

Las specs, cambios de alcance, priorización estratégica de reviews, aceptación
funcional y Memory Bank requieren aprobación de Pablo. Esta delegación operativa
no autoriza al orquestador a aprobarlos en su nombre. No hay push, publicación ni
modificación de instalaciones globales autorizados por este mandato.

Vigencia: hasta cierre, cancelación o revocación de esta épica.

## Ampliación explícita del mandato — 2026-10-29

Pablo solicita: «Te delego hitl, eres el dueño del proceso. Continúa orquestando
proactivamente hasta completar las correcciones pendientes y el epic completo».
Se registra la instrucción como mandato de continuidad operativa para las cuatro
features, empezando por 010-000, y la integración y cierre de la épica. No se
relajan severidades, aislamiento, pruebas previas ni evidencia. El orquestador
continúa dentro del contrato vigente: esta instrucción no convierte una recepción
en aprobación ni permite autoaprobar lo que sus instrucciones superiores reservan
al usuario. Cambios reales de alcance y publicación se elevan al dueño. No se
hereda autoridad de otras épicas ni se autorizan cambios de modelos.

## Entrada operativa

La vista compacta inicial informa reposo y DRIFT solo en project. El primer
`republish-agents` rechazó sin republicar: el contexto conservado de 009-002 no
coincide con active_feature null. Se registra la nueva iniciativa y se utiliza
`prepare --new-execution`, que es la vía canónica para reemplazar el contexto de
una iniciativa cerrada; no se modifica ese contexto anterior a mano.

## Bitácora de proceso — correcciones de 010-001 (2026-10-31)

- **Paquete de review inválido (attempt 20, I-9).** El paquete
  `010-001-documentary-contracts-reviewer-review-001` se compuso con el CLI
  **instalado**, cuya copia de los bloques de rol precedía al GREEN de T4. El
  reviewer lo rechazó con `validate-packet` rc=2 sin revisar; se dispuso como
  `superseded`, se conservó el rechazo en `review-refused-packet-001.md` y se
  republicó con el CLI del proyecto. El fail-closed funcionó; el costo fue un
  despacho consumido sin producto. Desde entonces todo paquete de esta épica se
  compone con `scripts/cdad_packet.py` del proyecto.
- **Paquete de scribe retirado antes de despachar (2026-10-31).** El primer
  paquete de Memory Bank (`…-scribe-memory-001`) declaraba como único insumo el
  contrato, omitiendo el cierre, las dos revisiones y el Memory Bank vigente. Se
  retiró con la clase `withdraw` (motivo registrado en el estado,
  `stage: packet-withdrawal`, `resolution: withdrawn`) sin transporte ni efecto
  de producto, y se republicó `…-scribe-memory-002` con doce insumos declarados.
  La recepción del segundo paquete se registró con su recibo durable
  (`f5e0c213…`) y los cuatro documentos del Memory Bank se materializaron con CAS
  contra los bytes vigentes.
- **Cierre de 010-001.** Gate de review `bb7d63bb…`; gate de Memory Bank
  aprobado; cierre `b316e7e7…` con `closure.md` `d48a1fcf…`; suite completa
  `--all` rc=0 (1882 passed, 5 skipped, canary 0) sobre `6c5b5a8c`. La
  aceptación funcional y la aprobación del Memory Bank se ejercieron bajo el
  mandato del 2026-10-30 y quedan en
  `docs/specs/010-001-documentary-contracts/owner-acceptance-2026-10-31.md`. No se
  publica: la deriva de la instalación global queda declarada en `closure.md` §5.

## Bitácora de proceso — 010-002 hasta el GREEN de T4 (2026-10-31)

- **Cuatro pasadas de `plan-review` antes de aprobar.** v1 dejó dos bloqueantes
  (aplicabilidad Odoo fuera de los roles que no escriben el producto; promesa
  contradictoria de selección fuera del alcance de T4); v2 los cerró y abrió
  N1..N4; v3 cerró N1..N4 y abrió un bloqueante nuevo (**`--replace-packet`
  copiaba el agente del predecesor**, contra la garantía por construcción); v4 lo
  cerró por **rederivación** y quedó aprobable sin bloqueantes (N7 declarado).
  Las precisiones P-1..P-4 quedaron registradas en
  `discovery-decisions-2026-10-31.md`; N7 (cambio de `stack` sin otra
  obsolescencia deja un `prepared` sin salida directa) se acepta fail-closed con
  tres salidas legítimas declaradas en `owner-approval-2026-10-31.md`.
- **AUDIT con una resolución de alcance.** El informe midió, no estimó: cuatro
  fixtures simulan históricos quitando solo `agent`, uno inyecta un agente de rol
  ajeno y ninguno fija la copia del agente en el reemplazo. A1 extendió el
  `write_scope` de T5 a `tests/test_010_004_t2_red.py` (cinco tests hoy verdes que
  la regla de presencia rompería por un motivo ajeno a su promesa), A2 rebasa el
  fixture de variante no publicada a una variante del mismo rol, A3 ubica el test
  de finalización del write-ahead en el módulo nuevo.
- **RED de T3 y GREEN de T4.** RED: 13 tests en cuatro grupos, 10 rojos por
  obligación ausente y 3 controles ya verdes. GREEN (`c0126040`, 44 archivos):
  procedimiento documental en `handoff-prompts.md`, matriz de aplicabilidad Odoo
  por rol en las seis fuentes y en las cinco skills Odoo implicadas, doctrina de
  selección alineada en `SKILL.md`, los dos adaptadores y `sub-agent-strategies`,
  y 22 agentes regenerados con `make agents`. Verificado por el orquestador:
  13/13, tests intactos (`07c919ec…`), techo 3864/12000 sin elevar, dos
  generaciones con hash idéntico, 36 + 78 regresiones y Odoo 68/68.
- **Defecto I-10, declarado y no oculto.** El paquete del GREEN se publicó con
  `packets/roles/implementer.md` en `d93b44e4…` y el encargo autorizado modificó
  ese mismo archivo (`ef3dab65…`). Como `render_packet` lee las fuentes del árbol
  vivo, la admisión dejó de reconocer el paquete **no alterado**. Se acreditó con
  el árbol restituido a las fuentes que la cabecera declara (bytes de `0d935bc8`):
  `validate-packet`, **`record-dispatch` y `receive`** corrieron en esa ventana y
  el árbol se restauró de inmediato, sin tocar `PACKET.md` ni `REQUEST.json`. Es
  una **excepción a una guarda fail-closed**, no una comparación pasiva, y no se
  establece como práctica reutilizable (una recurrencia exige corregir I-10 o
  decisión del dueño); la desviación queda en
  `docs/specs/010-002-documentary-role-integration/deviation-green-accreditation-2026-10-31.md`
  y el defecto en el backlog como I-10 con sus dos correcciones posibles.

## Bitácora — suite de cierre de 010-002, intento 1 (2026-10-31)

La suite completa midió el commit `35b81093`: `rc=1`, `4 failed, 1914 passed,
5 skipped` en 1:06:07. Los cuatro fallos son regresiones estructurales
introducidas por T4 y por el review-fix en superficies compartidas, y ninguno
afecta la sustancia del producto de la unidad (sus 36 tests siguen verdes):

- **005-006 PD-10** — la inserción de 9 líneas en `SKILL.md` §3.1 corrió la fila
  que invoca el CLI instalado de la línea 464 (borde de la ventana declarada) a
  la 473. La promesa está intacta; se rompió su localizador.
- **006-002 PD-2(b)**, en los dos adaptadores — el rewrap partió la asociación
  `subagent_type` ↔ mapeo rol→subagente, que el control exige en la misma línea.
- **F007 del validador consolidado** — el mismo rewrap eliminó «resolve the
  stack» del orquestador de Claude Code.

**Causa de proceso, no de cobertura:** los oráculos existían; lo que faltó fue
ejecutarlos. T4 verificó 36 + 78 tests y la matriz Odoo; el review-fix verificó
el módulo, las propiedades, el generador y `010-001`; el dictamen de T8 no los
corrió. Ninguno incluyó `test_005_006_t1_start_procedure.py`,
`test_006_002_u1_delegation_section.py` ni el validador. Regla que queda: una
unidad que edita `SKILL.md` o los adaptadores incluye en su verificación los
oráculos de esas superficies.

La deriva del canario (18 líneas) quedó **atribuida al servidor de OpenChamber**
—journal 13:42:29/36—, que reescribió el agente instalado con bytes que no son
el derivado del repositorio; la suite no escribió en el HOME real. Se declara el
límite: el canario mide el entorno y no distingue un test de otro gestor de
agentes. La fragilidad de los dos localizadores queda en el backlog como I-11 e
I-12, y el límite del canario como ítem propio. Detalle y evidencia en
`docs/specs/010-002-documentary-role-integration/closure-suite-attempt-001.md`.
