# Decisiones sobre el Discovery — 010-002-documentary-role-integration

**Fecha:** 2026-10-31. **Autoridad:** orquestador CDAD bajo el mandato HITL del
2026-10-30 (`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md`
§1 y §3). **Objeto:** las cinco preguntas abiertas de
`docs/specs/010-002-documentary-role-integration/discovery.md` §7, de las cuales
dos eran declaradas bloqueantes para Specification.

Documento del ámbito documental del orquestador. No es trabajo de rol: fija el
mandato que el borrador de Specification debe implementar, con el criterio del
uso real por el usuario final del sistema.

---

## D-1 — «Perfil documental» = especialización por contrato con los agentes existentes

**Decisión.** No se crean variantes de agente documentales, ni un campo nuevo del
estado, ni un selector paralelo. La especialización documental se expresa por el
**contrato del encargo** —objetivo, producto esperado, fuentes, alcance editable,
verificadores protegidos y evidencia— sobre los seis roles y los agentes que ya
existen, conservando `stack` como **dominio** (hoy `null`, o `odoo` cuando
corresponde).

**Por qué, con criterio de usuario final.**

1. **El usuario final de este sistema es quien encarga y quien recibe el
   producto.** Lo que necesita es que un encargo documental llegue al rol
   correcto, con su alcance y sus fuentes declaradas, y que el que produce no
   pueda ajustar su propio oráculo. Eso ya lo permite el transporte actual
   (`objective`, `inputs`, `write_scope`, `invariants`, `evidence_required`,
   `role`/`substage`).
2. **Un agente nuevo no agrega ninguna promesa que el contrato no dé.** El
   Discovery no encontró ningún comportamiento documental que exija una
   identidad de agente distinta; el conocimiento documental ya viaja por puntero
   en los agentes actuales, incluidas las variantes Odoo
   (`closure.md` de 010-001, §1-§2).
3. **El costo de las variantes es real y no proporcional.** Sondas del
   Discovery: `_derived_role` solo elimina el sufijo `-odoo`, de modo que un
   sufijo nuevo devuelve `None`; habría que tocar resolución, clasificación,
   generación, manifiestos, hooks, inventarios, staging e instalación, y
   multiplicar por dos runtimes. Eso es exactamente el «segundo mecanismo en
   paralelo» que el plan del epic prohíbe anticipar
   (`docs/epics/epic-010-documentary-specialization/plan.md`, Riesgos).
4. **`stack` sobrecargado rompería el dominio.** Está definido como dominio en
   `SKILL.md:130-137` y `sub-agent-strategies.md:144-165`; usarlo como tipo de
   producto reemplazaría la selección de dominio en vez de complementarla.

**Consecuencia para Specification.** La unidad debe entregar el **procedimiento
operativo** del encargo documental por los campos existentes y la verificación
estructural de que el producto documental no amplía permisos, no toca tests ni
oráculos y conserva el dominio del proyecto. No debe introducir agentes, campos
de estado ni selectores nuevos.

## D-2 — Aplicabilidad Odoo: las obligaciones de addon rigen cuando se toca un addon

**Decisión.** Las obligaciones de ejecución de las variantes Odoo que presuponen
modificar o verificar un addon (`make test` / `make test-clean` / lint / OCA /
`TransactionCase` / `@tagged` / inventario core-OCA como paso de verificación)
**rigen cuando el producto del encargo toca código, vistas, seguridad o datos del
addon**. Un encargo cuyo producto es **exclusivamente documental** conserva el
**conocimiento funcional de dominio** (por ejemplo, el mapeo proceso→módulo del
architect Odoo, que es conocimiento, no verificación) y **no** exige ejecutar la
batería de un addon que no modifica.

**Regla de mezcla.** Si el encargo toca código y documento, rigen las dos
familias: declararse «documental» **no** exime de las pruebas del código
modificado. La aplicabilidad se decide por el **producto declarado y su alcance
editable**, nunca por la etiqueta del encargo.

**Dónde se escribe.** En las fuentes competentes del dominio (las variantes Odoo
de rol y las fuentes de conocimiento Odoo afectadas), como cláusula de
aplicabilidad delimitada; el contrato general del rol no se debilita. Ningún
paquete puede usar esta cláusula para ignorar una instrucción superior: si un
encargo declara producto documental y su alcance editable incluye código, la
contradicción detiene esa parte y vuelve al orquestador.

**Por qué.** Sin esta delimitación, un encargo documental en un proyecto Odoo
queda formalmente bloqueado por una evidencia que su producto no puede producir —
y el rol, para cumplir, tendría que inventar una ejecución—. Con la delimitación,
el usuario final recibe el documento con su evidencia real y las pruebas siguen
obligatorias donde hay código.

## D-3 — El agente declarado debe corresponder al rol del encargo (fail-closed)

**Decisión.** El `agent` publicado en `REQUEST.json` debe ser el derivado de
`role` + `stack` del encargo, y una discordancia debe **fallar cerrado** antes del
despacho, no producir un render válido. Hoy el validador solo comprueba que sea
una cadena no vacía y el campo no entra en el render; una sonda del Discovery
confirmó que un `agent` de otro rol valida sin cambio de render.

**Por qué está en el alcance de esta unidad.** La promesa de 010-002 es que el
encargo llegue **al rol correspondiente** por el flujo canónico. Un campo que
puede declarar otro rol sin objeción contradice esa promesa en el punto exacto
donde se resuelve el destinatario. Es además la clase de defecto que se paga
caro: un reviewer encargado a un implementer no se detecta hasta que el producto
llega mal.

**Alcance mínimo.** Validar coherencia rol ↔ agente en `prepare`/validación del
request y en el registro del despacho; conservar el comportamiento actual para
`stack` vacío y `odoo`; el mensaje de rechazo debe nombrar el rol, el stack y el
agente esperado.

## D-4 — Variantes inexistentes: la promesa se alinea con el mecanismo

**Decisión.** Se alinea la redacción de las instrucciones de despacho con lo que
el mecanismo hace: el agente se **deriva** del rol y del dominio, y si la variante
derivada no está publicada el despacho **falla cerrado** (el adaptador externo ya
lo hace). No se promete un fallback silencioso al agente genérico que `prepare`
no implementa.

**Por qué.** Una instrucción que promete un fallback inexistente produce dos
conductas distintas según la superficie: el adaptador externo rechaza y una
sesión nativa podría improvisar. Alinear la frase es más honesto y más barato que
agregar detección de existencia en tres lugares.

## D-5 — Divergencia del esquema publicado: se corrige el asset, no se inventa campo

**Decisión.** `skills/cdad-cycle/assets/packet-request.schema.json` declara
`additionalProperties: false` sin enumerar `agent` ni `execution_context`, que el
validador Python sí admite. Se corrige el **asset** para que describa el request
real. No se agrega ningún campo nuevo por esta vía.

**Por qué.** Un esquema publicado que rechaza un request válido es un oráculo
falso: quien valide con el asset obtiene un veredicto distinto del CLI. Es
corrección de coherencia, no ampliación.

---

## Lo que estas decisiones NO autorizan

- No autorizan publicar, hacer push ni actualizar la instalación global: la
  deriva de 010-001 §5 sigue abierta y publicar es decisión del dueño.
- No autorizan ampliar permisos por defecto de ningún rol ni tocar el default de
  alcance del implementer.
- No autorizan cerrar el epic: `010-003` sigue pendiente y es donde se acredita
  la detección de defectos semánticos.
- No convierten el Discovery en contrato: el borrador de Specification debe
  declarar postcondiciones verificables y pasar su propia revisión.

---

## Precisiones del 2026-10-31 (tras `plan-review-002` y `plan-review-003`)

Estas precisiones **no reabren** D-1..D-5: acotan su alcance donde la revisión
independiente encontró una diferencia literal o una vía pública sin contrato.

**P-1 — D-3, contraste estático de rol (N3 de `plan-review-002`).** Además del
contraste contextual contra el `stack` vigente en publicación y despacho nuevos,
la validación compartida del request contrasta **estáticamente** que un `agent`
presente pertenezca al rol declarado (nombre genérico exacto o prefijo completo
con sufijo no vacío), sin consultar el `stack`. Un agente de otro rol no valida
ni produce render válido. Su diagnóstico nombra **rol, agente recibido y familia
esperada** y declara que no evalúa `stack`: la diferencia con el diagnóstico
contextual de D-3 está justificada porque esa comprobación no tiene stack que
nombrar.

**P-2 — D-3, intento nuevo frente a continuidad del registro (N2).** El
contraste contra el `stack` vigente rige para **intentos nuevos** de despacho; no
se reaplica a la repetición idempotente de un registro idéntico ni a la
finalización válida del write-ahead del mismo intento ya iniciado. La excepción
no relaja identidad, integridad, idempotencia, transacciones ni precondiciones
existentes, y no habilita un intento nuevo encubierto bajo un identificador
reutilizado.

**P-3 — D-3, request histórico sin `agent` (N6 de `plan-review-003`).** Un
request histórico admitido sin `execution_context` ni `agent` puede registrar un
**intento nuevo**: no hay agente que contrastar, así que no se aplica el
contraste contextual y **no** se deriva ni se sustituye un agente en silencio. El
paquete conserva la autoridad de su propio destinatario declarado.

**P-4 — Publicación por reemplazo (B1 de `plan-review-003`).** `prepare
--replace-packet` es una vía pública de publicación y su sucesor es una
publicación nueva. El sucesor **rederiva** el `agent` del rol y del `stack`
vigente, igual que una preparación ordinaria; **no** copia el agente del
predecesor. Motivo: copiarlo mantenía la contradicción con la garantía por
construcción y, con la regla de presencia, rompía reemplazos legítimos de
requests históricos sin `agent`. Con la rederivación, la garantía por
construcción cubre las dos vías públicas de publicación (preparación y
reemplazo), y `tests/test_007_002_dispatch_recovery.py` entra en la verificación
del RED y en las regresiones del GREEN.

**Límite.** Ninguna de estas precisiones autoriza publicar, ampliar permisos ni
agregar agentes, campos, etapas o selectores; el alcance de la unidad no cambia.
