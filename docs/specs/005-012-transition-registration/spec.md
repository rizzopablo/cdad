> Spec **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR. Cuarta corrección del draft.** Texto del
> **architect** (`mofgw/deepseek-v4.1-flash`), como **enmienda del contrato aprobado** pedida por el
> **orquestador Claude**: el hallazgo **B3** (bloqueante **para el uso previsto**), sobre el **predicado de
> vigencia** del control de exclusión de **PD-14** frente a las aprobaciones **sin `transition_key`**
> (consecuencia del procedimiento anterior, registrada en la nota de la entrada `specification` del state).
> **Esta entrega REEMPLAZA la spec aprobada por el orquestador OpenCode** el **2026-10-14** (el draft-003,
> sha256 `56d0be4b…`, con su plan `fb270b70…`): esa aprobación queda **sustituida y no vigente** hasta que el
> orquestador (HITL delegada del epic-005) o el **dueño** re-aprueben esta versión **junto con el plan
> corregido** (una sola acción). El architect **no** aprueba su propia propuesta (anti-sesgo, ADR-003/ADR-011).
> Contrato vigente: `docs/epics/epic-005-real-operation/plan.md`, **fila 12** (`:45`) y las secciones que
> prevalecen sobre las filas («Ajuste de los ciclos pendientes», `:48-88`), sha256
> `63dda3b83561a8763a6b3ab9613f2b26029796921cdede4dfd65e7ab3ad059a6`. Insumo principal de esta corrección: el
> **hallazgo B3** y su evidencia en el state (la operación **no pudo** registrar la reaprobación anterior); los
> insumos de la corrección anterior —la **review formal única** de la etapa 4 (`review.md`, §1 B2 y §2.1/§2.2
> O1..O4)— quedan **conservados por referencia** (§0.2). Insumo de dirección: el informe de
> discovery `docs/specs/005-012-transition-registration/discovery.md` (§1-§19), **resuelto por referencia**:
> no se repite. Rige el **criterio de review vigente del 2026-10-12**
> (`docs/epics/epic-005-real-operation/execution.md:48-56`) y los insumos de la review de Codex (`:83-88`).
> **Sin rutas absolutas del dueño ni ids crudos de sesión** (`<home>`, `<repo>`, `<tmp>`, `<ses-…>`,
> `<exec-id>`); los fixtures que imitan otro proyecto son **sintéticos y anónimos**.

# Spec — 005-012-transition-registration

**Feature ID:** `005-012-transition-registration` · **Epic:** `epic-005-real-operation` ·
**Estado:** DRAFT (etapa 2, **cuarta corrección del draft**: B3; la aprobación del draft-003
—`56d0be4b…`— queda **sustituida y no vigente**). ADR-011 gobierna autoridad, capacidades y límites de rol.

---

## 0. Qué corrige esta versión (trazabilidad de la corrección)

### 0.1 Esta versión (draft-004): B3 — la vigencia que compite es la del pin que **nombra los bytes actuales**

Insumo principal: el **hallazgo B3** del orquestador, **bloqueante para el uso previsto**, con su evidencia en
el state (`docs/.cdad-state.json`, `stage_history`: la **nota** de la tercera entrada `specification` de esta
feature, 2026-10-14). Esta cuarta entrega corrige **un solo punto** —el **predicado de vigencia** del control
de exclusión de **PD-14**, y el texto de **D-8** para que la decisión quede coherente— y **no re-litiga** la
dirección aprobada (subcomando aparte de `prepare`, escritor único, recepción que no aprueba, idempotencia por
clave de contenido, vigencia estructural de la aprobación, cierre que comprueba antes de aplicar, disposición
del despacho sin recibo, digests derivados por el CLI). Todo lo demás del contrato **no cambia**; lo que cambia
se declara punto por punto:

| Punto | Qué pedía la corrección | Cómo lo resuelve esta spec |
|---|---|---|
| **B3** (bloqueante, uso previsto) | el control de exclusión de **PD-14** exige `--supersedes <transition-key>` ante una entrada `specification` **vigente** del mismo `(feature, contract_path)`, pero **`--supersedes` sólo puede citar entradas que tienen `transition_key`** y las aprobaciones **registradas a mano** —todas las de features en curso anteriores a esta operación y **las tres de esta misma feature**— son **keyless**. Consecuencia en uso previsto: **tras el despliegue, la primera reaprobación de cada feature en curso obligaría a editar el state a mano** —exactamente lo que esta unidad elimina—. La nota de esa entrada lo registra: el CLI responde `state incoherent` nombrando `transition_key None` y `--supersedes` con cualquier clave falla `does not name an existing specification approval`, así que **la operación sólo puede sustituir entradas que ella misma registró**; la reaprobación se registró a mano. | **PD-14 declara el predicado de vigencia:** una aprobación `specification` cuyo **pin (`contract_sha256`) ya no coincide con los bytes actuales** del contrato **no compite como «vigente»** en el control de exclusión. Es **el mismo criterio de vigencia que PD-8(b) ya usa** en el cierre —la entrada debe **nombrar** los bytes actuales— y **no hace falta inventar nada**: la entrada con el pin viejo **igual ya no habilita nada**, porque el lector exige que el pin coincida (`_contract_approval_for`, D3/PD-18). Quedan **tres consecuencias declaradas** en el propio PD-14: **(1)** la **reaprobación tras una enmienda** (los bytes del contrato cambiaron) **no necesita `--supersedes`**, tenga o no clave la entrada vieja: el control de exclusión no la ve como vigente y la aprobación nueva queda como la **única** que habilita; **(2)** `--supersedes` queda para reaprobar los **MISMOS bytes** (el caso raro: dos aprobaciones de bytes idénticos) y **funciona como hoy** (exigido sin el campo → rc=2 `state incoherent`; con el campo nombrando la entrada → rc=0); **(3)** el caso raro con la entrada **vigente SIN clave** (mismos bytes) **no tiene salida** y va a **deuda D-16** con su condición de cierre, **sin inventar un mecanismo** (ni un `--supersedes` por otra vía, ni migrar el state, ni recomputar claves históricas). **D-8** fija la **definición** de vigencia (el pin que nombra los bytes actuales): **un solo** criterio sirve al registro y al cierre. |
| **Coherencia** (sin cambio normativo) | — | **PD-15 queda sin cambios** (no decide vigencia: la vigencia es del **pin** y del campo estructural `supersedes`, nunca de una prosa) y **D-12 no se toca** (su consecuencia —el no-op de las entradas registradas con la fórmula anterior del payload— **no** depende del predicado de vigencia: el predicado nuevo **no lee** `transition_key` ni `transition_key_payload`). Se resuelven las referencias **colgantes a «§2.5»** (§2.1, §2.2, PD-8(b), PD-12, §3): **esa sección no existe**; la vigencia vive en **PD-14** (§2.3) y las referencias pasan a nombrarlo. **§6** suma el límite al alcance «fuera»; **§7** suma la fila de **deuda D-16**; **§5 D-10** y **§9** (duda 5) declaran el predicado único; **§8** declara que B3 **no** agrega una tercera extensión. |

**Evidencia del defecto (lectura del repo; sin escrituras).** En `docs/.cdad-state.json`, `stage_history`: las
**tres** entradas `specification` de `005-012` (2026-10-14) y **todas** las aprobaciones de las features en
curso están **sin `transition_key`**; la **nota** de la tercera documenta las dos respuestas del CLI y el
registro manual que quedó forzado. En la implementación:
`_approved_spec_entries` (`cdad_packet.py:1419-1438`) filtra por clave **sólo** lo marcado con `supersedes`
(una entrada sin clave **nunca** queda fuera por ahí y **sí** compite), el control de exclusión
(`:5343-5371`) decide qué compite comparando **sólo `contract_path`** —**no** el pin—, y `_registered_transition`
(`:4757-4767`) resuelve por **igualdad de `transition_key`**, de modo que una entrada **sin** clave **no puede
ser citada**. Con B3, la coincidencia del pin (`contract_sha256` **resuelto** de los bytes actuales, PD-20)
entra en ese predicado.

**Efecto buscado (criterio vigente 2026-10-12).** La corrección **quita** trabajo y **no** agrega controles:
elimina la única edición manual que el procedimiento actual obligaba (la reaprobación de un contrato cuya
aprobación previa es keyless), **no** introduce un mecanismo nuevo (usa el criterio de vigencia que el cierre ya
tenía) y **no** debilita ningún control: una entrada con el pin viejo **ya** era inoperante para el lector
(`_contract_approval_for`), así que no habilita nada ni antes ni después.

### 0.2 Corrección anterior (draft-003, aprobada y ahora sustituida): B2 y O1..O4 — registro conservado

Insumo principal: la **review formal única** de la etapa 4
(`docs/specs/005-012-transition-registration/review.md`). Esa entrega (la tercera) corrigió **un bloqueante del
contrato** —**B2**, la identidad de la transición— y **cuatro correcciones de texto** que la review confirmó
(**O1..O4**), **sin re-litigar** la dirección aprobada (subcomando aparte de `prepare`, escritor único,
recepción que no aprueba, idempotencia por clave de contenido, vigencia estructural de la aprobación, cierre
que comprueba antes de aplicar). El otro bloqueante —**B1**, la autoridad de PD-6 en `closure`— se corrige
**sólo en la implementación** (PD-6 ya cubre `closure`: la postcondición numerada gana sobre el resumen de la
ficha T3, y el arreglo es un RED en el focal de T3 más un GREEN que reusa el diagnóstico existente), así que
**no** entra en esta enmienda; **O5/O6/O7** van a **deuda** (§7, deuda D-13..D-15). Todo lo demás del contrato
**no cambia**; lo que cambia se declara punto por punto:

| Punto | Qué pedía la review | Cómo lo resuelve esta spec |
|---|---|---|
| **B2** (bloqueante, **del contrato**) | la identidad de PD-10 cubre la tupla `(execution_id, feature_id, transition, stage, substage, packet_id, receipt_sha256, resolution)` y PD-11 equipara «invocación idéntica» con «mismo `transition_key`», pero **hay insumos con efecto sobre el state fuera de la clave** (`--postcondition`/`--outcome`, `--current-stage`, `--artifact`): N `delivery` del mismo paquete con la misma etiqueta —el uso natural para registrar las postcondiciones de un GREEN— producen la **misma** clave y la 2ª..Nª devuelven rc=0 «no-op, no effects» **sin registrar y sin fallar**, contra lo que promete PD-12 | **PD-10 declara el payload canónico de la identidad**: la tupla **más los insumos con efecto** (la postcondición **resuelta** con su `outcome`, el `current_stage` declarado, los `artifacts` citados y los campos propios de cada clase: `replaced_by`, `approved_by`, `contract`/`plan`, `closure`), con su **normalización** y la **serialización canónica** ya usada; el payload se escribe en la entrada como clave nueva y aditiva `transition_key_payload` (§2.2), de modo que la identidad es **comprobable desde el state**. Dos invocaciones que difieren en un insumo con efecto → **claves distintas** → transición distinta (**nueva entrada**, PD-12), nunca un no-op silencioso. Un `--artifact` repetido con la **misma** ruta y digest es **no-op**, y el **orden** de varios `--artifact` **no** cambia la identidad (la entrada los guarda como *mapping*). La consecuencia sobre las entradas **ya registradas** con la fórmula anterior —no se invalidan; dejan de reconocerse como no-op candidato— queda **declarada** en PD-10 y como **deuda D-12** con su condición de cierre; **no** se migra el state. Aditividad: ninguna validación nueva exige campos a las entradas históricas (INV-3/PD-17). Se ajustan además §2.2, §2.4 (INV-6), PD-11 (la salida del no-op declara la anotación que no se escribe), §4 (AC-3 mide la identidad corregida) y D-7. |
| **O1** (texto, punto 2.1a) | el «caso 3» de AC-4 y su eco en la ficha T3 dicen que la «aprobación reemplazada **sin** `supersedes`» debe rechazar con `approval pending`; eso **no se sostiene** frente a PD-14/PD-15 (sin el campo estructural nada queda reemplazado: ambas entradas siguen habilitando) | el caso del cierre pasa a ser «aprobación **faltante** o pin que **ya no nombra** los bytes actuales» (§4 AC-4 y ficha T3 del plan); el caso «reemplazada **sin** `supersedes`» queda **sólo** en T5, donde ya estaba (PD-15). |
| **O2** (texto, punto 2.1b) | el paréntesis de `--stage` en §2.1 dice «obligatoria salvo `disposition`», cuando **dos** clases llevan etiqueta canónica (PD-13/PD-21) | §2.1 pasa a «obligatoria salvo `disposition` **y `late-delivery`**», y el bullet que las explica nombra las **dos**. |
| **O3** (texto, punto 2.1c) | PD-19 y la ficha T7 hablan de una «**tabla** de operaciones» en `project-execution.md` §5-§8 que **no existe** como tabla literal (son secciones en prosa); la entrega de T7 declaró la operación en una **sección nueva §9** contigua, que la review validó como cumplimiento de PD-19 | la operación se declara en una **sección nueva contigua a las secciones operativas §5-§8**; se retira la palabra «tabla» en **todas** sus apariciones en la spec y el plan (PD-19, §6, ficha T7 y el observable canónico de T7). No cambia el alcance ni la entrega. |
| **O4** (texto, punto 2.2) | el control de vigencia **por fecha** de la delegación es **propio de la operación** (`_validate_v2_vigency` no lee `expires_on`) y esa divergencia —que la review juzgó **correcta**— queda declarada en el código y en `t2-green.md`, no en el contrato | PD-6 suma una línea que declara el **mecanismo**: «vencida» se comprueba con el vocabulario ya declarado en **D4** (`expires_on` ISO en el pasado no es vigente; un `expires_on` no-ISO falla cerrado) y la forma canónica **por eventos** conserva su dueño. |

### 0.3 Corrección anterior (draft-002, aprobada y ahora sustituida) — registro conservado

Insumo principal: la review del orquestador Claude (`review-claude-spec-2026-10-14.md`). Se corrigen **un
bloqueo de uso previsto** (B1) y **dos precisiones obligatorias** (P1, P2), **sin re-litigar** la dirección
aprobada (subcomando aparte de `prepare`, escritor único, recepción que no aprueba, idempotencia por clave
de contenido, vigencia estructural de la aprobación, cierre que comprueba antes de aplicar). Todo lo demás
del contrato **no cambia**; lo que cambia se declara punto por punto:

| Punto | Qué pedía la review | Cómo lo resuelve esta spec |
|---|---|---|
| **B1** (bloqueante, uso previsto) | el cierre no tiene salida para un despacho que **nunca vuelve**, con la feature **abierta**: PD-8(a) exige recibo para todo despacho, y la única salida (`receive --late` + `late-delivery`, PD-13) está limitada a features **cerradas**; un despacho del que no habrá entrega deja el cierre sin salida y obliga a editar el state a mano | **clase nueva `disposition`** (PD-21, D-13): una **disposición explícita del orquestador** sobre un despacho **sin recibo**, con la feature **abierta** y el paquete `dispatched`, que registra la decisión (1) como **dato estructural** —`resolution: abandoned\|superseded`, `approval_effect: false`, **sin** `approved_by` y **sin** fabricar un `completed`—, (2) **satisface PD-8(a)** para ese paquete (PD-8(a) acepta recibo **o** disposición), (3) es **idempotente por `transition_key`** (PD-11), y (4) deja la **traza en `stage_history`**. El rechazo del cierre **ofrece** ahora las dos salidas legítimas (recibir, o disponer) y **deja de ofrecer** `late-delivery`, que es de feature cerrada. **AC-4 suma el caso** (rechazo que nombra → disposición → el cierre avanza). Y se declara, sin ampliarlo, que esta unidad **no** toca los despachos sin recibo de ejecuciones **cerradas** (el cierre mira **sólo** la ejecución activa). |
| **P1** (precisión obligatoria, resultado) | los digests (`--receipt`, `--artifact`, `--contract-sha256`, `--plan-sha256`) no deben exigirse por argumento: pasar un hash para que el CLI lo recalcule es trabajo y superficie de error sin protección | **PD-20**: los digests son **opcionales**; si **faltan**, el CLI los **calcula** sobre los bytes actuales, los **escribe** en la entrada y los **imprime** en la salida; si se **pasan**, los **verifica** y una diferencia **falla cerrado** (`evidence missing`). Pasarlos sirve para **un** caso declarado (citar **exactamente los bytes revisados**). Se ajustan §2.1, PD-2, PD-3, PD-5, PD-8, PD-9 y PD-13; **AC-1 se corre en la forma mínima, sin pasar ningún digest**. |
| **P2** (precisión obligatoria, uso previsto) | PD-6 exige una `hitl_delegation` vigente siempre que haya epic activo; el **dueño** es la autoridad original y un proyecto con epic y **sin** delegación no podría registrar sus gates | **PD-6** con **tres casos**: con delegación registrada → se verifica su **vigencia** (revocada o vencida sigue **fallando cerrado**); **sin** delegación → se **registra el aprobador declarado** (`--approve-by`) y la salida **dice que no hubo delegación que verificar** (misma forma que `active_epic: null`); con `active_epic: null` → sin autoridad que verificar. El CLI **no** verifica identidades (deuda D-6), así que **no** bloquea al dueño. |

**Datos no bloqueantes que la review deja asentados (aplicados).**

- **PD-17 (dato medido).** Los tests **no** deben asertar porcentajes ni conteos del state vivo (el state
  cambia con cada ciclo): PD-17 queda reescrita de modo que su oráculo sea **sólo** `validate-state rc=0
  antes y después` sobre el state del repo (sólo lectura), **sin cifras**. El dato **91,1 %** que citaba la
  versión aprobada se **retira**: el valor correcto con el método que el discovery declara
  (`len(json.dumps(stage_history, separators=(',',':')).encode())`) es **90,8 %** (y **90,7 %** antes del
  append del despacho, que es el valor que el discovery midió). Ningún PD, AC, tarea ni fixture depende de
  la cifra.
- **Tamaño/orden.** Se conserva el reparto en 8 tareas y el orden, con un ajuste pedido: **T1 deja usable la
  forma mínima (`delivery` **y** `advance`)** y las otras clases se agregan sobre esa base (D-2, plan §2).
- **La deuda del despacho anulado** (la fila **D-9** de §7, que la decisión **D-4** citaba como «deuda D-1»)
  **deja de ser deuda**: la salida existe (la disposición, PD-21/D-13). Se registra como **retirada** en §7 y
  se corrige la referencia interna de D-4.

**Efecto buscado sobre el costo operativo (criterio vigente 2026-10-12).** La corrección **reduce** trabajo y
**no** agrega controles frágiles: (i) la disposición reusa el escritor único, el vocabulario cerrado y la
clave de contenido que ya existían —no crea un segundo camino de registro ni una segunda máquina de
recibos—; (ii) los digests derivados **quitan** cuatro argumentos al operador (fila 12: reducir trabajo
operativo); (iii) la autoridad sin delegación **quita** un bloqueo que hoy obligaría a volver a la edición
manual; (iv) el único control nuevo sigue siendo la comprobación del cierre (PD-8), y la disposición es una
**salida**, no un control.

---

## 1. Descripción funcional

**Objetivo (fila 12, `plan.md:45`).** Hoy cada transición de un ciclo la escribe el orquestador con un
script propio que edita `docs/.cdad-state.json`: **10 de las 11** transiciones del ciclo se registran a
mano y **`open-unit`** es la única operación de transición del CLI (discovery §1, §9). Esta feature
incorpora al CLI **una operación que registra una decisión explícita del orquestador sobre una
transición** —recepción de una entrega, aprobación de un gate, avance de etapa, cierre de feature y, con
esta corrección, **disposición de un despacho sin recibo**—, **comprueba sus requisitos mecánicos** y **la
aplica de forma consistente**, sin edición manual del state, **sin duplicar efectos** si se repite tras una
interrupción y **conservando el juicio** del orquestador.

**Recorrido de uso (el caso real: registrar el GREEN de una tarea y cerrar la feature).**
Los pasos 1-4 del protocolo (despacho) ya son del CLI y no cambian: `prepare` → `validate-*` → `begin`
(continuidad) → `prepare --record-dispatch`. Los pasos 6-8 (staging del buzón, `receive`,
`materialize`) siguen siendo del camino legítimo existente. **El hueco es el paso 9**: hoy un script
propio de 49-63 líneas escribe a mano `stage_history`, `active_packet.status: "completed"` y
`postconditions_status`, y **no queda como evidencia durable** (discovery §13; `docs/specs/005-013-unit-contract/debt.md:65-69`).
Con esta feature, el paso 9 y el paso 5 del cierre (el script `…-register-closure.py`) pasan a ser
**una invocación** del CLI que (i) **exige la evidencia referenciada** (recibo durable o artefacto
materializado, con su digest —**derivado por el CLI**, PD-20—), (ii) en el **cierre** comprueba **las
entregas requeridas y la aprobación vigente antes de aplicar**, (iii) escribe el state en la **forma
existente** con el lock y la publicación atómica que ya existen, y (iv) **no duplica** si se repite.

**Lo que B2 fija sobre ese recorrido.** Registrar el GREEN de una tarea no es una invocación: son
**varias** —una `delivery` por resultado de postcondición, porque la superficie declara un
`--postcondition <n>` **singular** por invocación (§2.1)— y todas citan el **mismo** paquete, el **mismo**
recibo y (uso natural) la **misma** etiqueta `--stage`. La identidad de la transición (PD-10) tiene que
distinguirlas: si no, la 2ª..Nª se tragan como no-op y los resultados quedan sin escribir en
`postconditions_status` **afirmando** que no hubo efectos. Es lo que esta corrección cierra, y la razón de
que el payload de la clave incluya los insumos con efecto.

**El caso que esta corrección cierra (B1).** El cierre exige una entrega (recibo) para **todo** despacho de
la ejecución activa. Pero un run puede **no volver** (p. ej. «stream ended without finish_reason» del
proveedor): entonces el orquestador vuelve a despachar en un paquete nuevo y el primero queda `dispatched`
**sin recibo para siempre**. Con la regla aprobada, la feature **no se podía cerrar** con la operación nueva
y había que volver a editar el state a mano —justo lo que la unidad elimina—. La salida es una **disposición
explícita del orquestador** sobre ese despacho (`--transition disposition`), con la feature **abierta**:
registra la decisión como dato estructural, **no aprueba nada** y **no fabrica un `completed`**; a partir de
ahí el cierre **avanza** (PD-21, PD-8(a)).

**Qué NO cambia (frontera).** El CLI sigue sin decidir el **significado** de un texto, la **calidad**
de una entrega, si un bloqueante es bloqueante ni si una deuda se acepta (discovery §7; `re-entry.md:249-255`).
Y **no decide** si un despacho **debe** anularse: la disposición es la **decisión del orquestador**
transcrita a estructura; el CLI sólo comprueba la **coherencia mecánica** (que el paquete esté despachado,
que no tenga recibo, que la feature esté abierta) y la registra. El **juicio sigue siendo del orquestador**;
el CLI hace la **contabilidad**. `prepare` **no cambia de rol**: es el productor de paquetes y no se
convierte en registrador (dirección del encargo).

**Baseline declarado.** El CLI **instalado** es `7212ead` (sha256 `776d1168…`) y es el que **corre**; el
árbol del repo (HEAD) incluye además 005-013 y es la base sobre la que se diseña. La operación nueva
**no existe en la instalación hasta el despliegue** (deuda ya declarada por 005-013,
`docs/specs/005-013-unit-contract/debt.md:71-77`): es la deuda D-4 de §7, y por eso la aceptación corre
el CLI **del repo** (§4).

---

## 2. Contrato

### 2.1 Superficie CLI (subcomando nuevo, simétrico a `open-unit`)

```
cdad_packet.py register-transition --project-root R
    --transition <delivery|gate|advance|closure|late-delivery|disposition>  # la DECISIÓN (vocabulario cerrado de seis valores)
    [--stage <token>]                                     # la etiqueta de la transición (obligatoria salvo `disposition` y `late-delivery`)
    [--feature <feature-id>]                              # default: active_feature
    [--current-stage <stage>]                             # campo OPERATIVO current_stage
    [--substage <sub>]                                    # campo OPERATIVO tdd_substage
    [--packet <packet-id>]                                # el paquete citado (entrega / despacho a disponer)
    [--receipt <sha256>]                                  # ASERCIÓN opcional sobre el digest del recibo durable (PD-20)
    [--artifact <path>[=<sha256>]]                        # artefacto citado (repetible); el digest es opcional (PD-20)
    [--postcondition <n> --outcome <red|green>]           # decisión registrada (delivery)
    [--approve-by <texto>]                                # quién aprueba (gate/closure)
    [--contract-path <p>] [--contract-sha256 <hex>]       # gate de etapa 2 (spec) y closure; el digest es opcional (PD-20)
    [--plan-path <p>]     [--plan-sha256 <hex>]           # idem para el plan
    [--closure-path <p>]  [--closure-sha256 <hex>]        # closure: el cierre citado; el digest es opcional (PD-20)
    [--resolution <abandoned|superseded>]                 # disposition: la disposición (vocabulario cerrado)
    [--replaced-by <packet-id>]                           # disposition/`superseded`: el paquete que lo reemplaza
    [--supersedes <transition-key>]                       # vigencia estructural (PD-14, §2.3)
    [--note <texto>] [--by <rol>]
```

- **Qué identifica la transición:** `--transition` (la **decisión**, vocabulario **cerrado** de seis
  valores) junto con `--stage` (la **etiqueta** de la transición, token plano libre: el
  `stage_history[].stage` real tiene **184 valores distintos** y **no** admite un vocabulario cerrado sin
  invalidar la historia; ver D-1/D-2). `--stage` **no** se acepta para `disposition` **ni** para
  `late-delivery`: las **dos** clases con etiqueta canónica (`dispatch-disposition` y `late-delivery`) la
  fijan por sí mismas, porque su valor informativo está en `--resolution` (D-13) y porque una etiqueta libre
  haría depender la clave de identidad de un texto sin efecto (PD-13/PD-21).
- **Qué es la evidencia referenciada:** `--packet` identifica el **paquete** citado y el CLI resuelve su
  **recibo durable** bajo `.cdad/runtime/results/<exec>/<packet>/receipt.json`; el digest del recibo se
  **deriva** (PD-20) salvo que se afirme con `--receipt <sha256>`. Cuando la transición cita un artefacto
  materializado, `--artifact <path>` lo nombra y su digest se **deriva** salvo que se afirme con
  `=<sha256>`. Los digests se **verifican contra los bytes** antes de escribir; una aserción divergente o
  un archivo ausente **falla cerrado** (`evidence missing`).
- **Dos campos de etapa distintos, a propósito:** `--stage` es la etiqueta histórica
  (`stage_history[].stage`); `--current-stage`/`--substage` son los campos **operativos**
  (`state.current_stage` / `state.tdd_substage`), con el vocabulario cerrado de
  `state-detection.md:20-37` y `ROLE_SUBSTAGES` (`cdad_packet.py:47-66`). El CLI no los confunde.

### 2.2 Forma del registro (una entrada de `stage_history`, append-only, aditiva)

La operación escribe **una** entrada con las claves **ya usadas** por la historia (`stage`, `substage`,
`at`, `by`, `approved_by`, `contract_path`, `contract_sha256`, `plan_path`, `plan_sha256`, `packet_id`,
`receipt_ref`, `receipt_sha256`, `artifacts`, `closure_path`, `closure_sha256`, `note`) más **claves nuevas,
declaradas y aditivas**: `transition` (la clase), `transition_key` (§2.4), `transition_key_payload` (el
**payload canónico** sobre el que el digest se computa: la tupla más los insumos con efecto, PD-10),
`supersedes` (PD-14, §2.3),
`approval_effect: false`, y —**sólo en la clase `disposition`**— `resolution` (la disposición) y
`replaced_by` (el paquete que reemplaza, cuando la resolución es `superseded`). **Nunca** reescribe ni borra
una entrada existente. Los campos derivados que aplica cada clase son los que hoy escribe el script manual:

| `--transition` | Efecto sobre el state (además de la entrada) |
|---|---|
| `delivery` | `active_packet.status: "completed"` (si el paquete citado es el activo); `postconditions_status[<n>] = <outcome>` y `tdd_substage` si se declaran |
| `gate` | `approved_by` + `contract_path`/`contract_sha256` y `plan_path`/`plan_sha256` cuando se dan; `current_stage`/`tdd_substage` si se declaran |
| `advance` | `current_stage` y/o `tdd_substage` (vocabulario cerrado) |
| `closure` | `epic_features[<feat>].status: "done"` + `closed_at` + `closure_evidence{path,sha256}`; `active_feature: null`; `current_stage: "idle"`; `active_packet: null` (o terminal) |
| `late-delivery` | **ninguno** sobre la feature: sólo la entrada de traza (§2.6 / PD-13) |
| `disposition` | **ninguno** sobre la feature **ni** sobre el paquete: sólo la entrada de traza con `transition: "disposition"`, `resolution` y `replaced_by`; `active_packet` **no** cambia (no se fabrica un `completed`) (PD-21) |

### 2.3 Postcondiciones (numeradas y verificables)

**PD-1 (superficie y escritor único).** `register-transition` es un subcomando de
`skills/cdad-cycle/scripts/cdad_packet.py`, declarado en `build_parser` (`cdad_packet.py:4927-5010`) y
despachado en `main` (`:5134-5233`). Toda escritura del state pasa por `_ProjectLock`
(`:1257-1380`) y por la publicación atómica existente (`_publish_owned_atomically`, `:2243-2266`, o
`_publish_generation`, `:3981`), con la **única** serialización `_serialize_document` (`:2235-2240`).
No se agrega un segundo escritor ni una segunda serialización, y **`prepare` conserva su rol** de
productor de paquetes (no registra transiciones): un `prepare` posterior a una transición registrada
produce bytes idénticos a los que produciría sin ella (mismos insumos).

**PD-2 (recepción de una entrega: `delivery` aplicada).** Con una ejecución activa cuyo
`active_packet.id == <id>` está en `dispatched`, un recibo durable presente en
`.cdad/runtime/results/<exec>/<id>/receipt.json`, y `--transition delivery --stage <token> --packet <id>`
→ **rc=0**; se agrega **una** entrada de `stage_history` y `active_packet.status` pasa a `"completed"`;
`validate-state --project-root R` → rc=0 sobre el state resultante. El digest del recibo se **deriva** de
los bytes actuales del `receipt.json` y se escribe/imprime; **`--receipt <sha256>` es opcional** (PD-20): si
se pasa, se verifica contra esos bytes y una diferencia → rc=2 `evidence missing`.

**PD-3 (la entrega exige la evidencia referenciada).** Sin recibo durable para el paquete citado, o con un
`--packet` que no pertenece a la ejecución activa, o con `--receipt <sha256>` **afirmado** distinto del
digest de los bytes del `receipt.json`, o con un `--artifact` cuya ruta no existe o cuyo digest **afirmado**
no coincide → **rc=2**, marcador **`evidence missing`**, diagnóstico que **nombra el paquete y la evidencia
faltante** (`<packet_id>`, `receipt.json`, path/digest esperado y real) y **la acción legítima siguiente**;
el state y el árbol quedan **byte a byte idénticos** (INV-7).

**PD-4 (recibir una entrega NUNCA aprueba).** La entrada escrita por `--transition delivery` no lleva
`approved_by`, `contract_path`, `contract_sha256`, `plan_path`, `plan_sha256`, `verdict` ni `review_*`;
no habilita roles y no cierra gates. Control: con esa entrega registrada y **sin** entrada
`specification` pinneada, `prepare --role implementer --substage green` sigue fallando `approval pending`
(la autorización depende sólo de la entrada `specification`, `_contract_approval_for`,
`cdad_packet.py:1413-1486`). El `semantic_status` del recibo permanece `pending`: la operación no lo
reescribe (`cdad_result.py:575`).

**PD-5 (aprobación de un gate: `gate` registrada).** `--transition gate --stage <token> --approve-by
<texto>` → **rc=0**, con `approved_by` no vacío en la entrada. Para el **gate de etapa 2**
(`--stage specification` con `--contract-path`): antes de escribir, el CLI verifica que el archivo existe
y **deriva** su `sha256` de los bytes actuales (`--contract-sha256` es opcional, PD-20); con `--plan-path`,
el mismo control sobre el plan. Si se **afirma** un `--contract-sha256`/`--plan-sha256` y **difiere** del
digest de los bytes, o si el archivo está ausente → rc=2 `evidence missing`, sin efectos.

**PD-6 (el gate lo aprueba la autoridad vigente; el dueño no se bloquea sin delegación).** `gate` y
`closure` exigen `--approve-by` no vacío (quien aprueba). La comprobación de la autoridad tiene **tres
casos**:

- **Con un registro `hitl_delegation` presente en el state:** se verifica su **vigencia** —no revocada ni
  vencida, con `source` resoluble a un archivo existente— con el mismo control de `_validate_v2_vigency`
  (`cdad_packet.py:1558-1624`), **sin** re-declararlo (INV-4). Una delegación **revocada o vencida** →
  **rc=2**, marcador **`approval pending`**, nombrando el registro faltante; sin efectos. *(El fallo cerrado
  se conserva.)* **Mecanismo de «vencida» cuando la delegación es por fecha.** Se comprueba con el
  vocabulario ya declarado en **D4** (la vigencia de la delegación del dueño de continuidad,
  `cdad_continuity.py:279-320`): un `expires_on` **ISO en el pasado no es vigente**, y un `expires_on` que
  **no** es ISO **falla cerrado** (lo desconocido nunca se fabrica como vigente). El control es **propio de
  la operación** (`_gate_authority`, `cdad_packet.py:4907-4922`), porque el control consumido
  `_validate_v2_vigency` (`:1586-1653`) **no** lee `expires_on`; la forma canónica **por eventos** conserva
  su dueño (`REQUIRED_EXPIRY_EVENTS`, `:43` y `:590-592`) y sigue vigente sin cambio (O4).
- **Sin registro `hitl_delegation`:** el CLI **no** inventa una autoridad ni puede verificar **identidades**
  (deuda D-6), así que **no bloquea al dueño**, que es la autoridad **original**. Registra el **aprobador
  declarado** (`--approve-by`) y la salida **declara que no hubo delegación que verificar** (misma forma que
  el caso `active_epic: null`).
- **Con `active_epic: null`:** idéntico al anterior: no hay autoridad que verificar y se registra la
  decisión declarando que no hubo delegación.

**PD-7 (avance de etapa: `advance`).** `--transition advance --stage <token> [--current-stage <stage>]
[--substage <sub>]` → **rc=0**, fija `current_stage` y/o `tdd_substage`. Un `--current-stage` fuera de
`{discovery, specification, tdd, review, merge, idle}` o un `--substage` fuera de
`VALID_SUBSTAGES`/`ROLE_SUBSTAGES` (`cdad_packet.py:47-66`) → **rc=2**, marcador `state incoherent`,
nombrando los valores admitidos, sin efectos. El CLI **no** impone una tabla de progresión más allá del
vocabulario (el sentido del avance —incluido un retroceso legítimo de `review` a `tdd` por un
review-fix— es del orquestador; declarado en §3/INV-5).

**PD-8 (el cierre comprueba entregas y aprobación ANTES de aplicar).** `--transition closure` ejecuta,
**antes de cualquier escritura**, dos comprobaciones mecánicas sobre la ejecución y la feature activas:

- **(a) Entregas requeridas.** Para **cada** paquete de la ejecución activa que tiene **registro de
  despacho** (`.cdad/executions/<exec>/dispatches/*.json`; el registro nombra su `packet_id`, y los
  despachos repetidos de un mismo paquete se cuentan **una vez**), debe existir **o bien** un **recibo
  durable** (`.cdad/runtime/results/<exec>/<packet>/receipt.json`, mismo predicado que `_packet_has_receipt`,
  `:4698-4702`), **o bien** una **disposición registrada** (una entrada de `stage_history` con
  `transition: "disposition"` que **nombra** ese `packet_id`, PD-21). Si no existe ninguna de las dos →
  **rc=2**, marcador **`evidence missing`**, nombrando `<packet_id>` y el recibo faltante, y **ofreciendo
  las dos salidas legítimas**: (i) recibir la entrega por el camino normal (`receive` +
  `--transition delivery`) si la entrega existe o está en camino; (ii) `--transition disposition`, con la
  feature **abierta**, si el despacho **no va a volver**. *(El camino `receive --late` + `late-delivery` de
  PD-13 es sólo para una feature **cerrada** y por eso **no** es la salida de este rechazo; B1.)* El cierre
  mira **sólo la ejecución activa**; los despachos sin recibo de ejecuciones **cerradas** no los toca esta
  unidad (deuda D-11).
- **(b) Aprobación vigente.** Debe existir al menos una entrada `specification` de la feature activa
  cuyo pin **nombre** el contrato (la ruta y su digest derivado, PD-20) y que esté
  **vigente** según **PD-14** (el pin que **nombra los bytes actuales**: es **el mismo predicado de vigencia**
  que el control de exclusión del registro aplica, tras B3; **un solo** criterio, no dos). Si falta o está
  reemplazada → **rc=2**, marcador **`approval pending`**,
  nombrando la aprobación faltante.

Tras cualquiera de los dos rechazos el state y el árbol quedan **byte a byte idénticos** (INV-7). El
cierre **no** juzga si el **conjunto** de gates registrados es el correcto para las etapas de la
feature: eso es la decisión del orquestador, registrada por `gate` (§3, INV-5).

**PD-9 (cierre aplicado).** Con PD-8 verde, `--transition closure --stage <token> --approve-by <texto>
--closure-path <p>` → **rc=0** y el state queda: entrada `stage_history` con la traza de cierre
(y el `closure_sha256` **derivado** de los bytes del cierre, PD-20); `epic_features[<feat>].status: "done"`,
`closed_at`, `closure_evidence{path, sha256}`; `active_feature: null`; `current_stage: "idle"`;
`postconditions_status` no se vacía salvo que se declare; `active_packet: null` o terminal. El resultado
satisface `_validate_idle_coherence` (`:508-543`) y `validate-state` → rc=0.

**PD-10 (identidad de la transición: el payload canónico incluye los insumos con efecto).** La
operación computa `transition_key = sha256(canonical(payload))`, donde `payload` es el objeto JSON de la
identidad: la **tupla ya declarada** —`execution_id`, `feature_id`, `transition`, `stage`, `substage`,
`packet_id`, `receipt_sha256`, `resolution` (nulo salvo `disposition`)— **más los insumos con efecto** sobre
la entrada o sobre el state:

- `replaced_by` (la clase `disposition` con resolución `superseded`);
- `postcondition` (`{"n": <str>, "outcome": <red|green>}`, la postcondición **resuelta** con su resultado, o
  `null`): `n` se normaliza **como la clave del state** (`str(n)`, la forma con la que el efecto escribe
  `postconditions_status`), de modo que la aserción y el efecto comparten normalización;
- `current_stage` (el campo **operativo** declarado, o `null`);
- `artifacts` (los artefactos citados, o `[]`);
- `approved_by` (gate/closure, o `null`);
- `contract` y `plan` (`{"path": …, "sha256": …}` o `null`): el gate de etapa 2 que los cita;
- `closure` (`{"path": …, "sha256": …}` o `null`): el documento de cierre citado.

**Normalización (una sola, declarada).** El payload se serializa canónicamente con
`json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",",":"))` sobre bytes UTF-8, y su
`sha256` en hex es la clave (la serialización que la implementación ya usa; la del state no interviene). Un
campo ausente es `null` (nunca `""`), y sólo la clase que lo declara lo llena. Los digests del payload son los
**resueltos** por el CLI (derivados de los bytes o verificados contra ellos, PD-20): el payload lleva el valor
que la entrada escribe, no el que el operador afirmó. `artifacts` es una **lista de pares `[path, sha256]`
ordenada por `path`**, porque la entrada los guarda como *mapping*: el **orden** de varios `--artifact` no
tiene efecto y **no** cambia la identidad, y un `--artifact` repetido con la **misma** ruta y el **mismo**
digest resuelve al mismo par ⇒ la repetición idéntica es **no-op** (PD-11); con **otra** ruta o **otro**
digest el payload difiere ⇒ transición distinta (entrada nueva). **`note` y `by` no entran en el payload**:
son anotación de la invocación y prosa que el CLI no interpreta ni usa como control (PD-18/D-8); su
divergencia se **declara** en la salida del no-op (PD-11) y no se escribe. La clave distingue
**invocaciones**, no efectos: un insumo declarado que la clase no aplica (p. ej. `--current-stage` en
`delivery`) también entra en el payload, así que dos invocaciones que difieren sólo en él son dos
transiciones distintas aunque escriban el mismo efecto — declarado para que nadie lea la clave como una
huella del efecto.

**Lo que el payload garantiza (los dos sentidos).** Dos invocaciones con **los mismos insumos con efecto**
producen la **misma** clave (⇒ no-op, PD-11); dos invocaciones que difieren en **algún insumo con efecto**
producen **claves distintas** (⇒ entrada nueva, PD-12). Con eso «invocación idéntica» y «misma clave» vuelven
a ser equivalentes, que es lo que PD-12 promete y lo que la tupla anterior no cumplía (B2).

**Escritura y comprobabilidad.** El payload se escribe en la entrada como clave **nueva y aditiva**
`transition_key_payload` (§2.2), de modo que la identidad es **verificable desde el state** (el digest se
recomputa con la serialización declarada) y la **frontera de versión** es explícita: una entrada **sin**
`transition_key_payload` está registrada bajo la fórmula anterior.

**Entradas ya registradas con la fórmula anterior (consecuencia declarada; sin migración).** Ninguna entrada
histórica se invalida por no tener `transition_key` ni `transition_key_payload` (INV-3, PD-17) y **ninguna
validación nueva les exige campos** (aditividad): (i) su `transition_key` **no es comparable** con el nuevo,
así que **no** se reconoce como **no-op candidato** —reconocerla reabriría el defecto que esta corrección
cierra: el state **no registra** la postcondición ni el `current_stage` declarado de esas entradas, de modo
que un no-op «a la vieja» volvería a tragar invocaciones distintas—; (ii) repetir exactamente una de esas
invocaciones **no** es no-op: la operación pasa por las **exclusiones estructurales** (PD-12, que no cambian
por esto) y, si pasan (el paquete sigue con registro de despacho y su recibo durable existe), **anexa una
entrada nueva** con la clave nueva —traza duplicada, `rc=0`, state válido: ninguna entrada se reescribe ni se
borra—; (iii) **no** se migra el state (`transition_key`/`transition_key_payload` históricos no se
recomputan). Dato de **contexto** (no oráculo: el conteo sube con cada ciclo, PD-17): la review contó **14**
entradas con la fórmula anterior (13 `delivery` + 1 `gate`) y al escribir esta corrección el state de este
repo tiene **16** (14 `delivery` + 2 `gate`); ninguna de ellas queda invalidada. Las dos entradas
`specification` de esta feature **no** llevan `transition_key` (las registró el orquestador por su
procedimiento, no la operación), así que no son invocaciones repetibles y no entran en esta declaración. El
límite va a **deuda D-12** (§7) con su condición de cierre.

**PD-11 (repetición idéntica = no-op sin duplicar efectos).** Repetir la **invocación idéntica** —los
**mismos insumos con efecto**, es decir el mismo `transition_key` de PD-10— → **rc=0**, **sin** agregar una
segunda entrada de `stage_history`, con el state **byte a byte idéntico** al de la primera invocación, y una
salida que **nombra la entrada existente** (la que ya registró la transición). El no-op es **independiente de
la cabeza**: no depende de que la entrada sea la última ni de la continuidad (contraste declarado en D-7).
**El no-op no puede tragar una invocación distinta:** si algún insumo **con efecto** difiere, la clave difiere
y la transición se registra como nueva (PD-10/PD-12). La única diferencia que el no-op admite es la
**anotación** (`--note`/`--by`, fuera del payload): la salida **nombra la entrada existente** y **declara** que
la anotación de esta invocación no se escribió, en vez de afirmar un no-op sin más (B2).

**PD-12 (transición distinta se registra como nueva; la exclusión estructural falla cerrado).** Un
`transition_key` distinto → **nueva entrada** (append), porque `stage_history` es append-only y un ciclo
legítimo repite etapas por tarea (184 etiquetas distintas). Una transición **estructuralmente
excluyente** → **rc=2**, marcador `state incoherent`, sin efectos: (i) `closure` de una feature cuya
`epic_features[].status` ya está en `CLOSED_FEATURE_STATUSES` (`:114`); (ii) `gate` de etapa 2 para un
`(feature, contract_path)` que ya tiene una entrada **vigente** sin dar `--supersedes` (PD-14, §2.3: compite
la entrada cuyo pin **nombra los bytes actuales**; una entrada con el pin viejo **no compite**); (iii)
`delivery` cuyo paquete citado **no está `dispatched`** (no puede tener recibo durable: esa condición
es estructural); (iv) `disposition` cuyo paquete citado **no pertenece** a la ejecución activa, **no está
`dispatched`**, **ya tiene recibo durable** (la evidencia contradice la disposición) o cuya feature **está
cerrada** (PD-21). **El reparto de marcadores es por condición, sin ambigüedad:** paquete no `dispatched`
→ `state incoherent`; paquete `dispatched` **sin** recibo, o con digest **afirmado** divergente →
`evidence missing` (PD-3).

**PD-13 (entrega tardía: salida explícita, sin reabrir ni aprobar).** Con la feature destino en
`CLOSED_FEATURE_STATUSES` y su ejecución ya cerrada:

1. `cdad_result.py receive --late …` (modo **declarado** que **reusa** la máquina de recibos de
   `cdad_result.py:493-591`: mismas validaciones de identidad, partes y digests, mismo esquema de
   `receipt.json`, `semantic_status: "pending"` **siempre**) persiste el recibo durable a partir de los
   bytes staged en el buzón `.cdad/inbox`, **reemplazando** la única precondición que hoy lo bloquea
   —«la feature activa no está cerrada» + «el paquete activo está `dispatched`»
   (`cdad_result.py:527-531`)— por la precondición **inversa** y declarada: la feature destino **está
   cerrada** y el paquete pertenece a su ejecución.
2. `register-transition --transition late-delivery --feature <closed-feature> --packet <id>` → **rc=0**
   (el digest del recibo se **deriva** y se escribe/imprime; `--receipt <sha256>` es opcional, PD-20) y
   deja: la feature **sin cambio de estado** (sigue `done`; no se toca `epic_features[].status`, ni
   `closed_at`, ni `active_feature`, ni `current_stage`); **ninguna aprobación nueva** (`approval_effect:
   false`, sin `approved_by`); y **traza durable**: el recibo bajo el root de resultados **más** una
   entrada de `stage_history` con `stage: "late-delivery"` y `transition: "late-delivery"`.

Con la feature **abierta** → rc=2 `state incoherent` (la salida tardía es sólo para lo cerrado; el
camino normal es `receive` + `delivery`, y para un despacho que no vuelve, `disposition`). Con la feature
cerrada pero **sin** recibo durable → rc=2 `evidence missing`.

**PD-14 (vigencia estructural de la aprobación).** Al registrar un `gate` de `--stage specification`
para un `(feature, contract_path)`, **compiten** sólo las entradas `specification` de esa feature **cuyo pin
nombra los bytes actuales** del contrato que el gate registra —la ruta `contract_path` y el
`contract_sha256` **resuelto** de esos bytes (PD-20)—: es **el mismo criterio de vigencia** que el cierre ya
usa en **PD-8(b)**, y **no** se agrega un tercero. Una entrada `specification` cuyo pin **ya no nombra** los
bytes actuales **no compite como vigente** (el contrato cambió y esa entrada, además, **ya no habilita nada**:
el lector exige que el pin coincida, `_contract_approval_for`, D3/PD-18). Si **compite** una entrada vigente:
sin `--supersedes` → **rc=2**, `state incoherent`, nombrando la entrada vigente y el campo `supersedes`; con
`--supersedes <transition-key>` que nombre una entrada **existente** de la misma feature y el mismo
`contract_path` → **rc=0** y, a partir de ahí, **la entrada nombrada deja de habilitar**: el lector
(`_approved_spec_entries` + `_contract_approval_for`, `:1398-1486`) la **ignora** y sólo la nueva
habilita. **Tres consecuencias, declaradas:**

1. **Reaprobación tras una enmienda (los bytes del contrato cambiaron): NO necesita `--supersedes`**, tenga o
   no clave la entrada vieja — el control de exclusión **no la ve como vigente** y la aprobación nueva queda
   como la **única** que habilita. Es el caso de uso que esta corrección fija: las aprobaciones registradas
   **a mano** (todas ellas **sin `transition_key`**) **dejan de competir en cuanto cambian los bytes**, sin
   migrar el state ni editar el state a mano.
2. **`--supersedes` queda para reaprobar los MISMOS bytes** (el caso raro: dos aprobaciones de bytes
   idénticos) y **funciona como hoy**: la **forma** del campo no cambia (nombra la clave de una entrada
   **existente** de la misma feature y el mismo `contract_path`, que siga o no nombrando los bytes actuales;
   no se agrega ningún control sobre ella); exigido sin el campo → **rc=2** `state incoherent`; con el campo
   nombrando la entrada → **rc=0**.
3. **El caso raro con la entrada vigente SIN clave** (mismos bytes, segunda aprobación, y la entrada que
   compite es **keyless**): no hay **clave que citar**, así que la operación **no puede** sustituirla. **No se
   inventa un mecanismo** para ese caso (ni un `--supersedes` por otra vía, ni migrar el state, ni recomputar
   claves históricas): va a **deuda D-16** (§7) con su condición de cierre.

**Aditivo y declarado sobre la regla existente** de 005-001 (D3/PD-18,
`docs/specs/005-001-idle-and-v7-bootstrap/spec.md:60-65,130`): la regla del pin **no se re-declara**; se
**extiende** con un segundo predicado —«entre las entradas cuyo pin nombra el contrato, sólo habilita la
**vigente**»—, y el predicado de **vigencia** queda **alineado** con el del cierre (**PD-8(b)**: el pin debe
**nombrar los bytes actuales**). Sin ninguna clave `supersedes` en el state, **el lector** selecciona
**igual que hoy** (INV-3/PD-17); el **control de exclusión** cambia exactamente en lo que esta corrección
declara: deja de ver como vigente una entrada cuyo pin ya no nombra los bytes actuales (y sólo eso).

**PD-15 (prohibido que la única traza de una sustitución sea prosa).** La sustitución registrada por
`register-transition` decide por el campo **estructural** `supersedes`; modificar el `note` de una
entrada sin `supersedes` **no** cambia qué entrada habilita. Control negativo: dos entradas con el pin
correcto y una nota en prosa «reemplaza a la anterior» pero sin `supersedes` → **ambas** siguen
habilitando (el comportamiento de hoy, declarado); con `supersedes` → sólo la nueva habilita.

**PD-16 (contexto de ejecución abierto y sin uso).** Con un contexto v2 **activo** de la feature activa
(el `state.execution` que creó `open-unit`) que esté **sin uso** —sin paquetes publicados con su
`execution_id` y sin registros de despacho—, `prepare --new-execution …` → **rc=2**, marcador
**`state incoherent`**, diagnóstico que **nombra el contexto ya abierto**
(`.cdad/executions/<exec-id>/execution.json`) y **cómo seguir** (usar el contexto abierto, o preparar
sin `--new-execution`), **sin acuñar** un segundo id. Sin contexto abierto previo, `prepare
--new-execution` sigue funcionando (control positivo: acuña un id nuevo y publica normalmente).

**PD-17 (aditividad sobre la historia real).** La operación y sus validaciones **no** exigen ningún
campo a las entradas existentes de `stage_history`. Sobre el state vigente del repo —cualquiera sea su
tamaño y su número de entradas, que **crece con cada ciclo**—, `validate-state --project-root <repo>` →
**rc=0 antes y después** de la feature (comprobación de **sólo lectura**; ver §4 y el plan, T8). El
oráculo de PD-17 es **`validate-state` rc=0 antes y después**, nunca un porcentaje ni un conteo del state
vivo: la cifra medible no es reproducible entre ciclos y no se usa como aserción (la revisión del
orquestador lo declara; el dato de contexto queda en §0).

**PD-18 (juicio intacto).** La operación **no** escribe `verdict`, `disposition`, `criterion`,
`review_path`/`review_sha256` ni ningún campo de juicio, **no** parsea prosa y **no** decide si un
bloqueante es bloqueante, si una deuda se acepta, si una entrega sirve ni **si un despacho debe
disponerse**. Su entrada no es una evaluación: es la **decisión del orquestador** transcrita a estructura.
*(La clave `resolution` de la clase `disposition` es la disposición declarada sobre el despacho, no el
campo `disposition` de una review.)*

**PD-19 (documentación por referencia).** `skills/cdad-cycle/references/re-entry.md` **paso 4**
(`:57-63`) pasa a **nombrar** la operación en vez de dejar la transición «al orquestador» sin
herramienta, y una **sección nueva de la operación** en `project-execution.md` —contigua a las secciones
operativas §5-§8, que son prosa con los comandos por operación: **no** existe una tabla literal en esa
zona— la **declara**; ninguna de las dos re-declara la regla del CLI ni copia texto de esta spec (INV-4). La operación
nueva también queda nombrada por las rutas que ya nombran operaciones
(`_next_route`/`_entry_selection`, `:4736-4778`), sin cambiar el mapa `entry` de 005-003.

**PD-20 (los digests los deriva el CLI; afirmarlos es una verificación opcional).** Todos los digests de
la superficie —`--receipt <sha256>`, `--artifact <path>=<sha256>`, `--contract-sha256`, `--plan-sha256` y
`--closure-sha256`— son **opcionales**. Si se **omiten**, el CLI los **calcula sobre los bytes actuales**
del archivo que la transición referencia (`receipt.json` del paquete citado; el path del artefacto; el
archivo de `--contract-path`/`--plan-path`/`--closure-path`), los **escribe** en la entrada y los
**imprime** en la salida. Si se **pasan**, los **verifica** contra los bytes actuales: una **diferencia**
o un archivo **ausente** → **rc=2**, marcador `evidence missing`, sin efectos (INV-7). Pasarlos sirve para
**un solo caso declarado**: aprobar o citar **exactamente los bytes que se revisaron** cuando el archivo
pudo **cambiar entre medio**. La salida **siempre** imprime los digests usados (derivados o verificados),
de modo que la entrada queda **auditable** sin recalcular nada. Para `--artifact`, la forma es
`<path>[=<sha256>]`: si el sufijo tras el **último** `=` es un sha256 de 64 hex, se **verifica**; si no, el
path es el argumento **completo** y el digest se **deriva**. **AC-1 se corre en la forma mínima, sin pasar
ningún digest.**

**PD-21 (disposición explícita de un despacho sin recibo, con la feature abierta).**
`--transition disposition --packet <id> --resolution <abandoned|superseded>` (con `--replaced-by
<packet-id>` **obligatorio** cuando la resolución es `superseded`) → **rc=0** y deja **una** entrada de
`stage_history` con `transition: "disposition"`, `stage: "dispatch-disposition"`, `resolution`,
`replaced_by` (si corresponde), `packet_id`, `approval_effect: false` y `transition_key`, **sin**
`approved_by` y **sin** fabricar un `completed` (**condición 1 de B1**). Comprobaciones mecánicas, **antes**
de escribir: la ejecución activa existe y el paquete citado **pertenece** a ella; el paquete tiene
**registro de despacho** (está `dispatched`); **no** existe **recibo durable** para él; la feature está
**abierta** (no en `CLOSED_FEATURE_STATUSES`) y por lo tanto hay ejecución activa. Cualquier incumplimiento
→ **rc=2**, marcador `state incoherent`, **nombrando** el hecho (el paquete ajeno, el paquete no
despachado, el recibo que la contradice, la feature cerrada), y state y árbol **byte a byte idénticos**
(INV-7, INV-9). La disposición **satisface PD-8(a)** para ese paquete: el cierre deja de rechazarlo
(**condición 2**). Es **idempotente por `transition_key`** (**condición 3**): repetir la invocación
idéntica → rc=0, sin segunda entrada, state byte-idéntico, salida que nombra la entrada existente (PD-11).
Deja la **traza en `stage_history`** (**condición 4**). **No** toca `active_packet` (su status queda como
está, **nunca** pasa a `completed` por esta clase), ni `epic_features[]`, ni `closed_at`, ni
`active_feature`, ni `current_stage`: registra la **decisión** (dato estructural), no un resultado ni una
aprobación. El CLI **no** juzga si la disposición es la correcta (INV-5/PD-18). Una segunda disposición con
**otra** resolución (p. ej. `abandoned` y luego `superseded`) es un `transition_key` distinto → **nueva
entrada** (append), consistente con PD-12; el cierre acepta el paquete si **alguna** entrada de disposición
lo nombra.

### 2.4 Invariantes (verificables)

- **INV-1.** Un solo escritor del state: `cdad_packet.py` bajo `_ProjectLock`; `register-transition` es
  la única superficie nueva de registro; `prepare` no registra transiciones.
- **INV-2.** `receive`/`validate-receipt`/`materialize` siguen **sin escribir el state** y **sin
  aprobar** (`semantic_status` siempre `pending`; `approval_effect` siempre `false`).
- **INV-3.** Append-only y aditividad: ninguna operación reescribe ni borra bytes de una entrada de
  `stage_history` ni de una entrada de `epic_history`; ninguna validación nueva se aplica a las
  entradas históricas.
- **INV-4.** Fuente única: esta spec **no** re-declara ninguna regla existente; cada extensión es
  **aditiva y declarada** (§8). La tabla de consecuencias por tipo de cambio de 005-013 **no** es esta
  operación.
- **INV-5.** Frontera del juicio (§3): estructura, digests, vocabulario de etapas, existencia de la
  autoridad vigente y de las entregas requeridas — **sí**; significado de un texto, calidad de una
  entrega, bloqueante, deuda y **si un despacho debe disponerse** — **no**.
- **INV-6.** Determinismo: los mismos insumos producen los mismos bytes de state (mismo pipeline
  transaccional), incluidos los digests **derivados** (PD-20): los mismos bytes de los archivos citados
  producen el mismo `receipt_sha256`/`artifacts`/`closure_sha256` escritos, y el mismo `transition_key` con su
  `transition_key_payload` escrito (PD-10): los mismos insumos con efecto producen la misma clave.
- **INV-7.** Fallo cerrado sin efectos: todo rechazo (rc≠0) deja el state y el árbol **byte a byte
  idénticos**.
- **INV-8.** Nada reservado al dueño se automatiza: alcance/criterios del epic, HOME, versiones
  instaladas, push y despliegue quedan fuera (fila 12 y `execution.md:19-23`).
- **INV-9.** La **clase `disposition`** registra una decisión y **no** un resultado: no escribe
  `approved_by`, **no** cambia `active_packet.status` (no fabrica un `completed`), **no** habilita roles y
  **no** toca ningún campo derivado de la feature; su única escritura es la entrada de `stage_history`
  (más `last_updated`).

---

## 3. Frontera del juicio (lo que el CLI comprueba y lo que no)

| El CLI **sí** comprueba (mecánico) | El CLI **no** decide (juicio del orquestador) |
|---|---|
| Que la evidencia citada **exista** y su **digest** (derivado o afirmado) **coincida** (recibo, artefacto, contrato, plan, cierre) | Si una entrega es **útil**, **correcta** o **suficiente** |
| Que la **autoridad vigente** exista, no esté revocada/vencida y sea resoluble (`_validate_v2_vigency`), **cuando hay delegación**; y que sin delegación **no** se invente autoridad | Si la aprobación **debía** ser del dueño o del delegado (reserva de alcance/autoridad y de identidad: D-6) |
| Que `current_stage`/`tdd_substage` estén en el **vocabulario cerrado**; que la etiqueta `--stage` sea un token plano | El **orden** semántico del ciclo más allá del vocabulario (un retroceso legítimo) |
| Que las **entregas requeridas** (paquetes despachados de la ejecución) tengan recibo durable **o** una disposición registrada | Si un despacho **debe** disponerse (`abandoned`/`superseded`) o si la entrega **va a llegar** |
| Que la **disposición** citada corresponda a un despacho **de la ejecución activa**, `dispatched`, **sin** recibo y con la feature **abierta** | **Cuál** vía de resolución es la correcta (recibir, disponer o reconciliar) |
| Cuál es la **aprobación vigente** cuando hay varias (PD-14: el pin que **nombra** los bytes actuales, marca estructural) | El **significado** de un texto; la **priorización** de una review |
| La **coherencia de reposo** al cerrar (`_validate_idle_coherence`) | Si el **conjunto** de gates registrados es el correcto para la feature |

---

## 4. Criterios de aceptación (medibles)

**Instrumento (común).** El **CLI real del repo** corrido como **subproceso**
(`python3 skills/cdad-cycle/scripts/cdad_packet.py …` y `…/cdad_result.py …`) sobre un **proyecto
descartable** creado en `<tmp>`, con el **`HOME` del subproceso en un tempdir vacío**. **Nunca este
repo, nunca HOME.** Patrón ya probado: `docs/specs/005-013-unit-contract/acceptance.md:7-14`,
`tests/test_004_002_t2_bootstrap.py:44-70`, `tests/test_005_007_t3_open_unit.py:20-41`,
`tests/product_staging.py`. Arnés **fuera de git**; la evidencia cruda vive en `.cdad/local/` (no
versionada). Fixture **sintético y anónimo**.

- **AC-1 — un ciclo representativo registrado SÓLO con la operación nueva, sin editar el state a
  mano.** *Insumo y productor:* el **orquestador** produce el proyecto descartable (política, plan del
  epic con `epic_features`, `hitl_delegation`, autoridad) y corre el recorrido: `open-unit` →
  `register-transition --transition advance` (discovery→specification) → `gate` de etapa 2 (spec+plan
  pinneados) → `delivery` del RED y del GREEN → `gate` de T4 → `delivery` del Memory Bank →
  `closure`. **Corre en la forma mínima: sin pasar ningún digest** (PD-20); los digests derivados se leen
  en **la salida** y en la entrada. Los paquetes/entregas del fixture son **reales** (`prepare` +
  `--record-dispatch` + `receive`). *Actor que evalúa:* el **orquestador** (HITL delegada). *Evidencia de
  cierre:* salida pegada de cada invocación con su `rc`; `sha256` del state antes/después; `git diff
  --name-only`/`find` del fixture con **sólo** lo que escribió el CLI; **cero** invocaciones de edición
  manual (se comprueba que el state es byte a byte el producido por el CLI); `validate-state` verde al
  final. *Límite duro declarado:* si alguna transición del ciclo quedara **fuera** del alcance de la
  operación, AC-1 no se alcanzaría sin trabajo manual; por eso `delivery`/`gate`/`advance`/`closure`
  cubren las cuatro clases (D-2) y **la única que queda con camino propio es el staging del buzón +
  `receive` + `materialize`**, que son el camino legítimo existente (no una edición del state).
- **AC-2 — entrega tardía sobre una feature cerrada.** *Insumo/productor:* el orquestador cierra el
  fixture con `closure` y luego entrega un texto final por el buzón
  (`receive --late` + `register-transition --transition late-delivery`). *Actor:* el orquestador.
  *Evidencia:* la feature **sigue `done`**; `semantic_status: "pending"`; **ninguna** aprobación nueva;
  **hay traza** (recibo durable + entrada `late-delivery`); `sha256` del state con
  `epic_features`/`active_feature`/`current_stage` **sin cambios** (sólo difiere el append de la traza).
- **AC-3 — repetición tras una interrupción.** *Insumo/productor:* el orquestador interrumpe entre la
  escritura y el commit, o repite la invocación idéntica. *Actor:* el orquestador. *Evidencia:* **conteo
  de entradas** de `stage_history` del fixture (una sola transición, no dos), state
  **byte-idéntico** al de la primera corrida (y también **después de appends posteriores**: la clave no
  depende de la cabeza), que una transición **distinta** sí se distingue (nueva entrada) —incluida una que
  difiere **sólo en un insumo con efecto**: otra `--postcondition` del mismo paquete con la misma `--stage`,
  u otro `--current-stage` (PD-10/B2)— y que una **estructuralmente excluyente** falla cerrado nombrando el
  conflicto. Aplica también a la **disposición** (repetirla es no-op, PD-21).
- **AC-4 — el cierre rechaza nombrando la entrega/la aprobación faltante, sin tocar el state; y la
  disposición lo destraba.** *Insumo/productor:* el orquestador reproduce en el fixture el **caso 1**
  (paquete despachado sin recibo) y el **caso 3** (aprobación **faltante** o pin que **ya no nombra** los
  bytes actuales). *Actor:* el
  orquestador. *Evidencia:* salida del rechazo con `rc=2`, el marcador (`evidence missing` / `approval
  pending` / `state incoherent`) y el **nombre** de la entrega o la aprobación faltante; `sha256` del
  state **byte-idéntico** tras el rechazo. **Caso B1 (nuevo):** con la feature **abierta** y un despacho
  **sin recibo**, el cierre rechaza **nombrándolo** (marcador `evidence missing`); se registra la
  **disposición** (`--transition disposition --packet <id> --resolution abandoned` —y el caso
  `superseded` con `--replaced-by`—) y repetirla es **no-op** (una sola entrada de `stage_history`, state
  byte-idéntico); y entonces el cierre **avanza** (`validate-state` verde y reposo coherente). El control
  positivo de PD-13 (feature cerrada) queda cubierto por AC-2.

**Meta de aceptación (fila 12 + discovery §17).** La feature cierra cuando AC-1..AC-4 tienen evidencia
**con el CLI del repo** y el cierre comprueba que el **trabajo manual del ciclo bajó** (los 6 scripts
de registro del último ciclo cerrado, `docs/specs/005-013-unit-contract/debt.md:65-69`, dejan de
necesitarse) **sin** compensarlo con más controles: el único control nuevo es la comprobación del
cierre (PD-8), y es el que **elimina** el «`completed` fabricado» del caso 1 y el que **tiene salida**
cuando el despacho no vuelve (PD-21). Los números son **orientación**, no umbral.

**Desconocidos declarados (no estimados).** (i) El **número de invocaciones** del recorrido completo de
AC-1; (ii) si la operación cubre **todas** las etapas con evidencia mecánica **homogénea** o si algunas
(review/priorización, Memory Bank) sólo **ganan traza** sin comprobación propia; (iii) si el fixture
mínimo necesita además un **plan del epic del producto con anclas** para el pin de unidad (hoy no hay
ciclo representativo del *path* de registro, sólo ciclos reales). (iv) La **magnitud** del ahorro
medido: se mide al cierre sobre el próximo ciclo real, no con una sonda sintética.

---

## 5. Decisiones (con fundamento y trade-off)

### D-1. Superficie: subcomando nuevo `register-transition`
**Decisión.** Un **subcomando nuevo**, simétrico a `open-unit` (`cdad_packet.py:4485-4551`), con el
**escritor único** (`_ProjectLock` + `_publish_owned_atomically`/`_publish_generation`). `prepare` **no**
cambia de rol. Nombre: `register-transition` — `register` nombra el acto de **contabilidad** que pide la
fila 12 («registra una decisión»), `transition` nombra el objeto; se descartaron `record-transition`
(`record` ya es el verbo de `--record-dispatch`, que registra **observaciones**, no decisiones) y
`advance` (demasiado estrecho: no cubre entrega ni cierre).
**Forma de la decisión explícita.** `--transition` (la clase, **vocabulario cerrado** de seis valores)
+ `--stage` (la etiqueta de la transición; canónica para `disposition`). **Evidencia referenciada:**
`--packet` (el CLI resuelve el recibo durable) y `--artifact <path>` para lo materializado; los digests se
**derivan** salvo que se afirmen (PD-20).
**Dos campos de etapa.** `--stage` = la etiqueta histórica (libre, token plano; canónica para
`disposition`); `--current-stage`/`--substage` = los campos operativos (vocabulario cerrado). No se
confunden porque en el state real son dos campos distintos.
**Trade-off.** Crece la interfaz (un subcomando más, y una clase más por B1) y hay que decidir qué
comprueba cada clase; a cambio, la superficie queda **descubrible por `--help`**, con su propio contrato y
sus tests, y no se mezcla el registro con el productor de paquetes (que es el invariante 1 de `prepare`).
**Alternativas descartadas.** (a) `prepare --record-transition`: mezcla el registro de transiciones con
el productor de paquetes y complica sus invariantes. (b) Extender sólo `receive`/`materialize`: ataca
el hueco más caro pero **no** cubre RED/GREEN/review/cierre, que son el resto del costo (discovery §8).

### D-2. Cobertura: las cuatro clases + la entrega tardía + la disposición, y el límite duro
**Decisión.** La operación cubre **las cuatro clases** de la fila —`delivery`, `gate`, `advance`,
`closure`— más `late-delivery` (la salida de PD-13) y `disposition` (la salida de B1/PD-21). Con eso
**AC-1 es alcanzable** (las cuatro transiciones que hoy escriben `stage_history` a mano se registran con
la operación) y **AC-4 también** (el despacho sin recibo tiene salida con la feature abierta). **Orden
declarado:** **T1** deja usable la **forma mínima (`delivery` **y** `advance`)** y las otras clases se
agregan sobre esa base (mismo criterio que la review del orquestador pide conservar).
**Aditividad obligatoria.** La validación es **aditiva**: no exige campos a las entradas históricas. El
`--stage` es un **token plano libre** (salvo `disposition`, canónico) precisamente porque
`stage_history[].stage` tiene **184 valores distintos** (medido sobre el state vigente) y un vocabulario
cerrado de etiquetas invalidaría la historia. Lo **cerrado** es la **decisión** (`--transition`), la
**disposición** (`--resolution`) y los campos **operativos**.
**Límite duro declarado.** Si alguna transición quedara fuera, AC-1 exigiría trabajo manual; por eso el
alcance **incluye** las cuatro clases y **no** hay hueco silencioso. Quedan **fuera** del registro
(declarado, no un hueco): el **staging del buzón** y la **escritura del descriptor** `RESULT.json` (paso 6
del protocolo), que el discovery §13 ya señala como deuda de **otra** unidad (D-10 de 005-004: «recepción
de intervención cero»).
**Trade-off.** Cubrir las clases hace la operación grande; acotarla dejaría AC-1 o AC-4 sin cumplir. La
mitigación frente al tamaño es el reparto por clase en tareas atómicas (plan §4), no la reducción del
alcance.

### D-3. Juicio intacto: la frontera
**Decisión.** Fijada en §3. El CLI comprueba **estructura, digests, vocabulario de etapas, existencia de
la autoridad vigente (cuando hay delegación) y de las entregas requeridas**; **no** decide el significado
de un texto, la calidad de una entrega, si un bloqueante es bloqueante, si una deuda se acepta ni la
priorización de una review, **ni si un despacho debe disponerse**. **Nada de rule-based sobre prosa**: no
se piden tests que decidan el sentido de un párrafo por listas de palabras (criterio del dueño,
`plan.md:26`; `re-entry.md:219-226`).
**Trade-off.** Renunciar a comprobaciones semánticas deja fuera «verificar que el cierre dice la
verdad»; a cambio, el CLI no se convierte en juez de prosa y el control no es frágil (el caso 3 muestra
que una nota en prosa **no** es un control).

### D-4. Cierre: comprobar ANTES de aplicar, con salida para el despacho que no vuelve
**Decisión.** PD-8: dos comprobaciones —entregas requeridas (paquetes despachados de la ejecución con
recibo durable **o** disposición registrada) y la aprobación vigente pinneada— **antes** de escribir; si
falta algo, **falla cerrado nombrando** la entrega/la aprobación y **ofrece las dos salidas legítimas**
(recibir, o disponer). El conjunto de entregas requeridas es **derivado mecánicamente** (no declarado por
el orquestador): todo paquete con registro de despacho **debe** tener recibo **o** disposición, porque
`--replace-packet` sólo aplica a paquetes `prepared` (`project-execution.md:198-201`) y la resolución de
un `dispatched` es del orquestador.
**Trade-off.** El CLI **no** inventa una «anulación» (eso es juicio): la **disposición** es la decisión
del orquestador transcrita a estructura, y el CLI sólo registra su coherencia mecánica (B1/D-13). A
cambio, la regla deja de tener el límite que la versión aprobada declaraba (deuda D-9, hoy **retirada**):
con la feature abierta, un despacho que no vuelve ya tiene salida sin editar el state.
**Fundamento.** Es el requisito de la review de Codex (`execution.md:85-88`) y el único control nuevo
que **elimina** trabajo (deja de fabricarse a mano un `completed` que la evidencia no sostiene, caso 1) sin
bloquear el cierre cuando no hay entrega que recibir.

### D-5. Entrega tardía: el buzón como entrada, con marcador propio
**Decisión.** De las dos opciones del discovery §6, se elige la **primera**: el **buzón** `.cdad/inbox`
es la entrada y **una operación lo recibe** con un **marcador propio** (`--transition late-delivery`,
`stage: "late-delivery"`, `approval_effect: false`), reusando la **máquina de recibos** de
`cdad_result.py` mediante un modo declarado `receive --late` (misma identidad, mismas partes, mismos
digests, mismo esquema de recibo, `semantic_status: "pending"`), y **reemplazando** la única
precondición que hoy bloquea (`receive` llama a `validate_state`,
`cdad_result.py:513`→`cdad_packet.py:768`, y con la feature cerrada **falla cerrado**; `materialize`
igual, `cdad_result.py:841-842`) por la precondición **inversa**: la feature destino **está cerrada**.
**Las tres propiedades.** (1) **No** cambia el estado de la feature (sigue `done`); (2) **no** aprueba
nada (`approval_effect: false`, `semantic_status: pending`); (3) **deja traza durable** (recibo +
entrada de historia). Funciona **con la feature cerrada sin reabrirla** porque no toca
`active_feature`/`current_stage`/`epic_features[].status`.
**Frontera con la disposición (B1).** `late-delivery` **no** es la salida del cierre: es para una entrega
**que existe** pero llega **después del cierre**. El despacho que **nunca vuelve** se resuelve con
`disposition` y la feature **abierta** (PD-21). Ambas clases conviven sin ambigüedad: una registra una
entrega tardía, la otra una decisión sobre un despacho.
**Trade-off.** Un modo más en `receive` (superficie) frente a una **segunda máquina de recibos**
(prohibida: 005-004 PD-10 prohíbe duplicar el camino de recepción/registro, discovery §15 riesgo 1). Se
elige el modo declarado y se **documenta** que el modo `--late` es el único que invierte la
precondición de vigencia.

### D-6. Recibir no aprueba; y la autoridad no bloquea al dueño
**Decisión.** INV-2/PD-4: la recepción (normal y tardía) deja `semantic_status: "pending"`, **no**
habilita roles y **no** cierra gates. La autorización de un rol sigue dependiendo **exclusivamente** de la
entrada `specification` con pin (`_contract_approval_for`, `:1413-1486`), que sólo escribe `--transition
gate` con `--stage specification`, y sólo tras comprobar los bytes. En cuanto a **quién** aprueba un
`gate`/`closure` (P2), **PD-6** tiene tres casos: con delegación registrada se verifica su vigencia
(y revocada o vencida sigue fallando cerrado); **sin** delegación se registra el **aprobador declarado**
(`--approve-by`) y la salida declara que **no hubo delegación que verificar** —el CLI **no** verifica
identidades (deuda D-6) y **no** bloquea al dueño, que es la autoridad **original**—; con `active_epic:
null`, igual.
**Cómo se comprueba.** Contra-prueba en PD-4 (sin `specification`, `prepare --role implementer` sigue
`approval pending`) y comprobación de que la entrada `delivery` no lleva `approved_by`. Es el invariante
(b) de la fila 12.
**Límite declarado (deuda D-10).** La comprobación de autoridad **del state** (`_validate_v2_vigency`,
consumida por `validate-state`/`prepare`/`receive`) **sigue** exigiendo `hitl_delegation` cuando hay epic
activo. P2 quita el bloqueo **de la operación**, no esa condición del estado: un proyecto con epic activo
y **sin** delegación puede **registrar** sus gates y su cierre (el cierre produce un reposo que
`validate-state` acepta por la vía de reposo), pero los demás consumidores del estado siguen declarándolo
no vigente hasta que exista la delegación o una unidad de autoridad decida lo contrario (005-001; deuda
D-10).

### D-7. Repetición tras una interrupción: clave de identidad propia
**Decisión.** Clave de identidad **propia de la transición**: `transition_key` (§2.4/PD-10) sobre el
**payload canónico** —la tupla `(execution_id, feature_id, transition, stage, substage, packet_id,
receipt_sha256, resolution)` **más los insumos con efecto** (la postcondición resuelta con su `outcome`, el
`current_stage` declarado, los `artifacts` citados y los campos propios de cada clase: `replaced_by`,
`approved_by`, `contract`/`plan`, `closure`)—, almacenada **aditiva** y escrita también como
`transition_key_payload`. Repetición **idéntica** (mismos insumos con efecto) → **no-op** (rc=0, sin segunda
entrada, state byte-idéntico); transición **distinta** → **nueva entrada** (append); transición
**estructuralmente excluyente** → **falla cerrado** (PD-12). Incluir `resolution` en la clave es lo que hace a
la **disposición** idempotente **y** distinguible: dos resoluciones distintas del mismo despacho son dos
transiciones distintas (append), no un no-op espurio. Incluir los **insumos con efecto** es lo que hace a la
identidad distinguir transiciones distintas: sin ellos, la 2ª..Nª `delivery` del mismo paquete —el registro de
las postcondiciones de un GREEN— quedaba tragada como no-op «sin efectos» y los resultados no se escribían
(B2). El costo es resolver el payload **antes** de decidir el no-op; se paga una vez por invocación y evita el
fail-open.

**Fundamento de «nueva entrada» en vez de fallar cerrado.** `stage_history` es append-only y un ciclo
legítimo repite etapa por tarea (p. ej. `tdd-green-t1` y `tdd-green-t2`); fallar cerrado ante «misma
etapa, otra transición» rompería el ciclo real.
**Qué ofrece la continuidad y qué no (declarado).** `begin`/`checkpoint` tienen idempotencia por clave
`(execution_id, packet_id, attempt)` y la repetición idéntica es no-op **sólo mientras esa clave es la
cabeza**; tras el append de la siguiente, un `begin` idéntico **falla cerrado** (deuda T2-R1,
`continuity.md:48-56`). `reconcile` **exige `--packet`** (`cdad_continuity.py:1312-1316`): **no** hay
reconciliación a nivel de ejecución. Por eso la operación **no promete** la idempotencia de la
continuidad: ofrece una clave **content-addressed** (funciona independientemente de la cabeza) y se
declara su diferencia. `dispatched-unknown` (despacho sin recibo) **no** autoriza repetir
(`cdad_continuity.py:984-988`).
**La regla de dos intentos queda donde vive** (`re-entry.md:79-87`): un reintento responde a hipótesis o
información nueva; la repetición idéntica sin información nueva dispara revisión de estrategia. Esta
feature **no** la re-declara ni la usa como criterio.
**Trade-off.** Un `transition_key` (con su payload escrito) en la entrada es un campo más; a cambio, la
idempotencia **no** depende de la posición ni de la continuidad, y es verificable **desde el state**: por
conteo de entradas y recomputando el digest de `transition_key_payload`.

### D-8. Vigencia de la aprobación: marca estructural, aditiva sobre D3/PD-18
**Decisión.** **Una sola aprobación vigente** por `(feature, stage, contract_path)`, donde **vigente**
significa que su **pin** (`contract_path` + `contract_sha256`) **nombra los bytes actuales** del contrato: es
**un solo predicado de vigencia**, el que el cierre ya usaba (PD-8(b)), aplicado **también** al registrar
(PD-14), y una entrada cuyo pin ya no coincide con los bytes actuales **no compite** (y **ya no habilita**:
el lector exige el pin, D3/PD-18). La sustitución se marca con el campo **estructural** `supersedes` en la
entrada **nueva** (nombrando el `transition_key` de la reemplazada); el lector la **ignora** a partir de ahí.
El registro de una segunda entrada vigente para el mismo `(feature, stage, contract_path)` **exige**
`--supersedes` (si no, rc=2 `state incoherent`) **cuando la que compite nombra los bytes actuales**, es decir,
cuando se reaprueban los **mismos** bytes; tras una **enmienda** de los bytes, la aprobación vieja **no
compite** y la reaprobación **no** necesita el campo.
**Por qué en la entrada nueva y no en la vieja.** Reescribir la vieja rompería INV-3 (append-only) y la
byte-identidad de la historia. La vigencia se **deriva** de la declaración de la nueva.
**Aditividad declarada.** Es una **extensión** de la regla existente de 005-001 (D3/PD-18,
`docs/specs/005-001-idle-and-v7-bootstrap/spec.md:58-65,130`), que **no se re-declara**: se agrega el
predicado «vigente» a la selección de entradas y se **define** ese predicado (el pin que nombra los bytes
actuales, el mismo del cierre), sin tocar la regla del pin. Sin `supersedes` en ninguna entrada, **el lector**
selecciona **igual** que hoy (control de no-regresión); el **control de exclusión** cambia sólo en lo que
PD-14 declara.
**Límite declarado (B3).** El caso raro de reaprobar los **mismos** bytes desde una entrada vigente **sin
clave** no tiene salida por la operación —`--supersedes` sólo cita entradas con `transition_key`— y **no** se
le inventa un mecanismo: **deuda D-16** (§7), sin migrar el state. Este límite **no** alcanza al caso de la
**enmienda** (consecuencia 1 de PD-14), que es el que obligaba a editar el state a mano y el que esta
corrección elimina.
**Trade-off.** Dos campos nuevos en el state (`transition_key`, `supersedes`) frente a la alternativa
prohibida por el dueño: que la única traza de una sustitución sea **prosa** en un `note` (caso 3:
`docs/.cdad-state.json:4211-4231`) — exactamente la clase de control que el dueño prohíbe («no pidas
tests que decidan el significado de un párrafo por listas de palabras»).

### D-9. Deuda de 005-013 con condición de cierre en esta unidad
Tres ítems de `docs/specs/005-013-unit-contract/debt.md` (sección «Datos para 005-012», `:58-69`):

- **D-2 de 005-013 (`debt.md:41-43`), «reconciliación de un paquete `dispatched`» → condición de cierre
  005-012. Resuelto por (i): ENTRA dentro de (c).** Implementación mecánica: la comprobación de
  **entregas requeridas** de PD-8 es la **reconciliación a nivel de ejecución** que hoy no existe —
  clasifica cada paquete de la ejecución activa en *con recibo durable* (recibido), *con disposición*
  (dispuesto) o *sin resolver* (pendiente, **nombrado**)— y es la que impide tanto **duplicar efectos**
  (no se cierra ni se repite sobre un despacho sin resolver) como **fabricar** un `completed`. El
  veredicto fino por paquete sigue siendo de `reconcile` (`cdad_continuity.py`, que exige `--packet`), y
  **la decisión semántica** —si la entrega sirve, se adapta, quedó superado o el despacho se dispone— es
  del orquestador (fila 12(d)); el CLI **nombra**, no decide. Con esto la condición de cierre de D-2
  queda **cumplida por esta unidad** en su parte mecánica; el residuo (generalizar el **veredicto** de
  `reconcile` a nivel de ejecución) se declara como **D-1 de deuda** con condición de cierre explícita
  (§7).
- **Ejecución huérfana (`debt.md:60-64`) → ENTRA en el alcance** (tarea T6 del plan, con su focal):
  tras `open-unit`, `prepare --new-execution` debe **rechazarse** con un diagnóstico que **nombre el
  contexto ya abierto**, en vez de acuñar un segundo id (`_next_execution_id`, `:1627-1632`; hoy
  `_select_execution` sólo busca contexto previo si **no** se pasó `--new-execution`, `:1721-1723`, y
  `_bootstrap_v2_execution` acuña uno nuevo, `:1635-1660`). Precedente del diagnóstico accionable:
  `approval pending`/`packet obsolete`/`state incoherent`
  (`docs/specs/005-001-idle-and-v7-bootstrap/spec.md:69-73,99`, PD-12). **Un `prepare --new-execution`
  legítimo (sin contexto abierto previo) sigue funcionando** (control positivo en PD-16).
- **Registros con scripts del orquestador (`debt.md:65-69`) → es el NÚCLEO de esta feature**; su cierre
  **es** la operación nueva (§1-§2). El criterio de cierre es que los 6 scripts de registro del último
  ciclo (`…-register-tdd.py`, `…-register-review.py`, `…-register-reapproval.py`,
  `…-register-t4.py`, `…-register-memory.py`, `…-register-closure.py`) dejen de ser necesarios.

### D-10. Fuente única y aditividad
**Decisión.** Cada regla que se reusa tiene **dueño**, y esta spec la **referencia por ruta/sección**
(§8). Extensión **aditiva y declarada** en dos puntos, y sólo dos:
(1) el vocabulario de **tres** marcadores de `005-001` PD-12 se **extiende** con **`evidence missing`**
(nueva condición: «la evidencia referenciada por la transición no existe o no coincide con su
digest»); los tres existentes conservan su condición sin cambios y siguen siendo mutuamente
excluyentes por condición;
(2) la selección de entradas `specification` de `005-001` D3/PD-18 se **extiende** con el predicado
«vigente» (D-8), cuya **definición** fija B3 —el pin que **nombra los bytes actuales**, el mismo criterio
del cierre (PD-8(b))—, sin tocar la regla del pin.
**No se re-declara** nada: la regla del pin, el escritor único, el protocolo de materialización, la
idempotencia de la continuidad, la procedencia, la autoridad, la forma del state y la planificación por
unidad quedan en sus dueños. La clase `disposition` **no** agrega marcadores: reusa `state incoherent`
(disciplina estructural) y `evidence missing` (hecho de evidencia).
**Trade-off.** Un marcador nuevo es vocabulario que crece; la alternativa —reusar `approval pending`
para una evidencia faltante— mezclaría dos condiciones y volvería el diagnóstico menos accionable.

### D-11. Deuda con condición de cierre
**Decisión.** §7: todo lo que queda afuera va a deuda **con condición de cierre explícita**. Nada de
deuda oculta.

### D-12. Aceptación
**Decisión.** §4 y plan §6: CLI **real del repo** como subproceso sobre proyecto **descartable** en
`<tmp>` con `HOME` en tempdir vacío; los cuatro casos; productor, actor que evalúa y evidencia de cierre
por caso; los **desconocidos** declarados (§4). **La ejecuta el orquestador** bajo la HITL delegada
(`execution.md:10-12`); la **review formal** juzga el contrato y el sentido de los textos, no los tests.
**Trade-off.** Correr el CLI del repo (y no el instalado) es inevitable: la operación no existe en la
instalación (§1, D-4 de deuda) y el drift de instalación ya está declarado por 005-013.

### D-13. Disposición de un despacho sin recibo: clase propia, no una reutilización de `delivery`
**Decisión (mecanismo elegido para B1).** Una **clase propia** del vocabulario cerrado,
`--transition disposition`, con `--resolution <abandoned|superseded>` (vocabulario cerrado) y
`--replaced-by <packet-id>` obligatorio cuando la resolución es `superseded`. Escribe **sólo** una
entrada de traza (§2.2, PD-21): `resolution`, `replaced_by`, `approval_effect: false`; **no** aprueba,
**no** toca `active_packet` (no fabrica un `completed`), **no** habilita roles ni gates, y su
`transition_key` incluye `resolution` (idempotente y distinguible).
**Fundamento.** La review deja el mecanismo abierto («`--transition delivery` con una disposición
`abandoned`/`superseded`, o una clase propia»). Se elige la **clase propia** porque: (i) `delivery`
significa **recepción** (PD-2/PD-4: «recibir nunca aprueba»), y una «entrega abandonada» es un
oxímoron; (ii) reutilizar `delivery` con un `--resolution` no-`received` obligaría a **relajar** PD-3
(entrega sin recibo → `evidence missing`) y PD-12(iii) (paquete no `dispatched` → `state incoherent`),
que son los controles más fuertes de la unidad, para un caso que **no es una recepción**; (iii) la clase
propia mantiene la frontera (el CLI **registra** la decisión y **no** juzga si procede), y deja el
vocabulario de marcadores intacto (reusa `state incoherent`/`evidence missing`).
**Cumple las cuatro condiciones de B1:** (1) dato estructural, sin aprobar y sin fabricar `completed`
(PD-21/INV-9); (2) satisface PD-8(a) para ese paquete (PD-8(a)/PD-21); (3) idempotente por
`transition_key` (PD-10/PD-11); (4) traza en `stage_history` (PD-21).
**Trade-off.** El vocabulario de decisiones pasa de cinco a seis valores y aparece una clave más
(`resolution`, `replaced_by` sólo en esa clase). A cambio, no se debilita ningún control existente, el
cierre gana su salida con la feature abierta, y la decisión queda como **dato estructural** auditable en
lugar de editar el state a mano.
**Frontera declarada.** La disposición cubre el caso de la **ejecución activa**; los despachos sin recibo
de ejecuciones **cerradas** quedan fuera (deuda D-11), y el CLI **no** reconoce «anulaciones» que no se
declaren por esta clase: sigue sin inventar una anulación.

### D-14. Digests derivados por el CLI: la aserción es opcional, el cálculo es del CLI
**Decisión (mecanismo y fundamento de P1).** Los digests son **opcionales** (PD-20): el CLI los **deriva**
sobre los bytes actuales, los **escribe** y los **imprime**; si se afirman, los **verifica** y una
diferencia **falla cerrado**. El **único** caso declarado para afirmarlos es **citar exactamente los bytes
revisados** cuando el archivo pudo cambiar entre medio.
**Fundamento.** Fila 12 pide **reducir trabajo operativo**: calcular un hash para que el CLI lo recalcule
es trabajo y superficie de error sin protección adicional (review P1). La derivación **no** debilita la
verificación: el CLI compara **siempre** contra los bytes, y la salida registra el digest usado, así que
la entrada queda auditable sin que el operador calcule nada.
**Trade-off.** Se pierde la posibilidad de **detectar** que un archivo cambió entre la revisión y el
registro **sin** afirmar el digest; por eso se conserva la afirmación opcional para ese caso, y por eso
**AC-1 corre en la forma mínima** (sin digests) y su evidencia incluye los digests impresos.

---

## 6. Alcance y fuera de alcance

**Dentro.**
- La operación `register-transition` con sus **seis clases** (`delivery`, `gate`, `advance`, `closure`,
  `late-delivery`, `disposition`), la forma aditiva del registro, la **clave de identidad con su payload
  canónico** (PD-10), la vigencia
  estructural (con **un solo** predicado de vigencia: la entrada cuyo pin **nombra** los bytes actuales,
  PD-14/PD-8(b) — B3), la comprobación del cierre, la entrega tardía y la disposición del despacho sin recibo
  (D-1..D-9, D-13); y los **digests derivados** por el CLI (D-14/PD-20).
- La autoridad del gate con **tres casos** (delegación vigente / sin delegación / sin epic) sin bloquear
  al dueño (D-6/PD-6).
- El rechazo de `prepare --new-execution` con contexto abierto y sin uso (D-9, `debt.md:60-64`).
- La documentación **por referencia** (`re-entry.md` paso 4; **sección nueva de la operación** en
  `project-execution.md`, contigua a las operativas §5-§8).
- La aceptación AC-1..AC-4 con el CLI del repo.

**Fuera.**
- Las candidatas de `execution.md:89-96`: **adopción de versión entre ciclos** (RD-a) y **estado
  operativo compacto con historia durable** (RD-b). Sin unidad ni prioridad (decisión del dueño,
  2026-10-13); RD-b explica el tamaño del state y **no** se resuelve acá.
- Los **despachos sin recibo de ejecuciones cerradas**: el cierre mira **sólo** la ejecución activa y la
  disposición exige la feature **abierta**; no se amplía eso (deuda D-11).
- La **reaprobación de los MISMOS bytes** desde una aprobación vigente **sin clave** (B3): `--supersedes`
  **no puede** citarla y la operación **no** inventa un mecanismo; queda declarada como **deuda D-16**.
- La **tabla de consecuencias por tipo de cambio** de 005-013 (PD-6..PD-11,
  `docs/specs/005-013-unit-contract/spec.md`): es de 005-013; acá sólo se la **nombra** en la frontera.
- El **staging del buzón** y el descriptor `RESULT.json` (paso 6 del protocolo): deuda de 005-004
  (D-10, «recepción de intervención cero»).
- CI, sandbox, plataforma de jobs, **paralelismo** (`active_packet` único ya lo excluye), tocar **HOME**,
  push y **despliegue**. Los contratos de 003-*/005-* **no se reabren**.
- Tests que decidan el significado de un texto por listas de palabras; tests de cobertura no derivados
  de un PD; tests que aserten **porcentajes o conteos del state vivo** (PD-17).

---

## 7. Deuda con condición de cierre

| Id | Deuda | Condición de cierre |
|---|---|---|
| **D-1** | Generalizar el **veredicto** de `reconcile` (clasificación fina por paquete: `not-started`/`dispatched-unknown`/…) a nivel de **ejecución**. Esta unidad entrega la detección + el nombrado + el rechazo del cierre (decisión **D-9 de §5**, el ítem de 005-013), **no** el veredicto fino, que vive en `cdad_continuity.py` y exige `--packet` (`:1312-1316`). | La **línea de continuidad** (RD-b/RD-a, `execution.md:89-96`) o la próxima unidad que toque `cdad_continuity.py`; se cierra cuando exista una reconciliación de ejecución que clasifique sin `--packet`. |
| **D-2** | Inventario y limpieza de **campos derivados sin dueño** (`review_status` sigue apuntando a 005-013 con `active_feature` 005-012, `docs/.cdad-state.json:9-12` vs `:6-7`; `audit_status`). La operación escribe **sólo** los campos de su clase; **no** barre derivados ajenos. | Una decisión de alcance sobre el barrido en el cierre (¿el cierre limpia `review_status`?) con su unidad; hoy **declarado**: el desvío es **detectable** (el cierre dejó de fabricar `completed`) pero **no** se corrige solo. |
| **D-3** | Efecto del **tamaño del state** (la mayoría en `stage_history`) sobre la operación nueva. La entrada que escribe es **pequeña** y no agrega copias, pero el state sigue creciendo. | **RD-b** (estado operativo compacto con historia durable). |
| **D-4** | **Despliegue**: la operación **no existe en la instalación** hasta que el dueño despliegue (compartida con 005-013 O3, `debt.md:71-77`). | El despliegue (reservado al dueño) + la comprobación de O3 en el activo instalado. |
| **D-5** | El rechazo de `prepare --new-execution` (PD-16) cubre el caso **acotado** del contexto v2 abierto y **sin uso** (el que crea `open-unit`). Un segundo contexto creado por otra vía, o uno con paquetes, **no** se cubre. | Si se observa en un ciclo real: re-acotar y ampliar con evidencia; hoy declarado como límite. |
| **D-6** | El CLI verifica que la **delegación** esté vigente y resoluble, pero **no** puede verificar que **quien** aprueba sea la persona delegada (la delegación no nombra personas). | Si el dueño quiere una marca de identidad de quien aprueba: una unidad de autoridad/HITL; hoy **declarado** como frontera (§3). |
| **D-7** | D-3 de 005-013 («juicio de *restricción de aplicación inmediata*» / marca estructural, `005-013/debt.md:44-47`): **no** es esta unidad; acá sólo se la nombra. | La marca estructural declarada en los planes (decisión de 005-013). |
| **D-8** | El **staging del buzón** + descriptor `RESULT.json` (paso 6 del protocolo) sigue siendo del orquestador: la operación nueva **no** lo automatiza. | Deuda **D-10 de 005-004** («recepción de intervención cero»). |
| ~~**D-9**~~ | ~~Un despacho que el orquestador considere **anulado** también exige resolución: el CLI no reconoce una «anulación».~~ **RETIRADA: ya no es deuda.** La salida es la **disposición** (PD-21/D-13), con la feature **abierta**: el orquestador declara `abandoned`/`superseded` y el cierre avanza sin editar el state. | **Cumplida en esta entrega** (B1). Se conserva el id para trazabilidad; la decisión **D-4** corregía su referencia (decía «deuda D-1»). |
| **D-10** | **Autoridad sin delegación**: P2 quita el bloqueo **de la operación** (PD-6), pero la vigencia **del state** (`_validate_v2_vigency`, consumida por `validate-state`/`prepare`/`receive`) **sigue** exigiendo `hitl_delegation` cuando hay epic activo. Un proyecto con epic y sin delegación puede **registrar** gates/cierre, pero los demás consumidores lo declaran no vigente. | Una unidad de **autoridad/HITL** (005-001, dueño de la regla) que decida si el dueño sin delegación es una autoridad vigente a nivel de estado; hasta entonces, la operación no bloquea y el límite queda declarado. |
| **D-11** | **Despachos sin recibo de ejecuciones cerradas**: esta unidad (y la disposición) cubren **sólo la ejecución activa** con la feature abierta; el cierre mira sólo la ejecución activa. | Si se observa un caso real: re-acotar y ampliar con evidencia (probablemente junto con D-1); hoy declarado como límite explícito (B1, dato no bloqueante de la review). |
| **D-12** | **No-op de las entradas registradas con la fórmula anterior de la clave** (consecuencia declarada de **B2**): al no llevar `transition_key_payload`, su `transition_key` no es comparable con el nuevo y no se reconoce como no-op candidato; repetir una de esas invocaciones **anexa** una entrada nueva (traza duplicada, state válido) en vez de ser no-op. Reconocerlas reabriría el fail-open que B2 cierra (el state no registra la postcondición ni el `current_stage` declarado de esas entradas); **no** se migra el state ni se reescribe ninguna entrada. | Si se quiere un no-op también para ellas: una unidad que decida **cómo se recupera la información que el state no guardó** (registro del payload hacia adelante en las entradas nuevas —ya es el caso— o una marca de versión explícita), con RED primero; hoy **declarado como límite**. |
| **D-13** | **`tdd_substage` no se puede limpiar (O5)**: el paso tdd→review del protocolo real (`stage-3-tdd.md:251`) escribe `tdd_substage: null`, y la operación no puede reproducir esa vuelta a `null` (`VALID_SUBSTAGES` no la admite y sólo asigna cuando se declara): queda un valor viejo. Además el vocabulario de contrato (`VALID_SUBSTAGES`) no contiene los valores que el protocolo nombra para esa transición (`integration`/`review-pending`, `re-entry.md:201,213`). Ningún validador lee `tdd_substage`, así que es **divergencia informativa**, no un fallo mecánico, y **no** obliga a editar el state a mano. | Una unidad que dé un valor centinela o un `--clear-substage` declarado, **o** la enmienda del texto del protocolo para tolerar el valor viejo en esa transición; con RED si cambia comportamiento. |
| **D-14** | **PD-12(i) sin guard ni test propio (O6)**: el cierre de una feature cuyo `epic_features[].status` ya está cerrado. La vía realista la atrapa la ausencia de `active_feature` (marcador `state incoherent`, `cdad_packet.py:5005-5010`), pero un state `done` **con** `active_feature` (ya incoherente) re-cerraría, sobreescribiendo `closed_at`/`closure_evidence` con una entrada nueva (`:5347-5364`). | Test del caso **+** guard temprano del cierre (o la declaración explícita de que el guard anti-vía **es** `active_feature: null`), con RED si cambia comportamiento. |
| **D-15** | **Nits de cobertura declarada (O7)**: (a) `--artifact` **derivado sin aserción** sin test directo (sólo el divergente y el ausente); (b) el conteo «despachos repetidos de un mismo paquete se cuentan una vez» de PD-8(a) sin test explícito. (El tercer nit de O7 —el no-op **independiente de la cabeza**— **lo cubre el RED de B2** declarado en PD-11/AC-3.) | Dos focales chicos, en la unidad de hardening que toque el área. |
| **D-16** | **Reaprobación de los MISMOS bytes desde una aprobación vigente SIN clave (B3).** La entrada compite (su pin nombra los bytes actuales) y `--supersedes` **no puede citarla** —sólo cita entradas con `transition_key`—, así que la segunda aprobación de bytes idénticos **no tiene salida** por la operación; las aprobaciones registradas **a mano** (todas keyless) son las afectadas. **No alcanza** al caso de la **enmienda** (bytes cambiados), que sí tiene salida sin `--supersedes` (PD-14, consecuencia 1). **No** se inventa un mecanismo: ni un `--supersedes` por otra vía, ni migrar el state, ni recomputar claves históricas. | Una unidad que decida **cómo se cita** (o cómo se reconoce la vigencia de) una entrada **sin `transition_key`** —una marca de versión explícita, un criterio de nombrado que no dependa de la clave, o el registro de esa aprobación por la operación—, con **RED** primero si cambia comportamiento. Hoy **declarado como límite explícito** (B3, consecuencia 3 de PD-14). |

**Registro de B3 (corregido en esta versión; no es deuda).** **B3** —hallazgo del orquestador al re-aprobar la
enmienda anterior, aceptado como **bloqueante para el uso previsto** y documentado en la nota de esa entrada
del state—: el control de exclusión de **PD-14** exigía `--supersedes` ante una entrada `specification`
**vigente** del mismo `(feature, contract_path)`, pero `--supersedes` **sólo cita entradas con
`transition_key`** y las aprobaciones registradas **a mano** (todas las anteriores a esta operación y las tres
de esta misma feature) son **keyless**: la primera reaprobación de cada feature en curso obligaba a **editar el
state a mano**. Se corrige en **PD-14** (el pin que **ya no nombra** los bytes actuales **no compite** como
vigente: el mismo criterio de PD-8(b)) y en **D-8**; el caso no bloqueante (los **mismos** bytes con una
entrada vigente **sin clave**) queda como **deuda D-16**, sin inventar mecanismo. **PD-15 no cambia** (no
decide vigencia: la vigencia es del pin y del campo estructural `supersedes`, nunca de una prosa) y **D-12 no
se toca** (la consecuencia declarada de la fórmula anterior del payload **no** depende del predicado de
vigencia: el predicado nuevo **no lee** `transition_key`/`transition_key_payload`). Las referencias colgantes a
«**§2.5**» —esa sección **no existe**: la vigencia vive en **PD-14** (§2.3)— pasan a nombrar **PD-14**. Detalle
punto por punto en **§0.1**.

**Registro de O1..O4 (corregidos en la versión anterior; no son deuda).** **O1** (el caso del cierre es «aprobación
faltante o pin que ya no nombra los bytes actuales»; el caso «sin `supersedes`» queda en T5) se corrigió en
§4 de esta spec y en la ficha T3 del plan; **O2** («obligatoria salvo `disposition` y `late-delivery`») en
§2.1; **O3** (la operación se declara en una **sección nueva contigua a las operativas §5-§8**, no en una
«tabla») en PD-19, §6 y la ficha T7 del plan; **O4** (el mecanismo del control de fecha, con el vocabulario
de D4 y su dueño) en PD-6. Detalle punto por punto en §0.2. Los ids de esta tabla son ids de **deuda** (§7),
distintos del espacio de **decisiones** de §5 (convención ya vigente: la decisión D-4 cita la deuda D-9).

---

## 8. Fuente única, referencias y aditividad

**Contrato y autoridad.**
- `docs/epics/epic-005-real-operation/plan.md:45` (fila 12), `:48-88` (secciones que prevalecen);
  sha256 `63dda3b8…59a6`.
- `docs/epics/epic-005-real-operation/execution.md:8-23` (HITL delegada), `:48-56` (criterio de review
  vigente), `:83-88` (insumos de la review de Codex), `:89-96` (candidatas y medición).
- Informe de discovery: `docs/specs/005-012-transition-registration/discovery.md` §1-§19 (entrada del
  draft, **por referencia**; sha256 `d0b15b03…`).
- Review del orquestador Claude de las versiones aprobadas:
  `docs/specs/005-012-transition-registration/review-claude-spec-2026-10-14.md` (insumo de esta
  corrección: B1, P1, P2 y los datos no bloqueantes).

- Review formal única de la etapa 4 (insumo de esta corrección: B2 y O1..O4):
  `docs/specs/005-012-transition-registration/review.md`.

**Reglas reusadas (dueño → referencia; ninguna se re-declara).**
- **Vista compacta y selección de entrada** → `docs/specs/005-003-orientation-reduction/spec.md:109-120`;
  implementación `_entry_selection`/`_next_route` (`cdad_packet.py:4736-4778`).
- **Protocolo de materialización y transición (paso 4)** → `re-entry.md:14-63`; esta feature **cambia el
  paso 4** (pasa a nombrar la operación), **no** lo duplica.
- **Idempotencia y reconciliación** → `continuity.md:17-21,48-60` (y su deuda T2-R1 declarada).
- **Procedencia** → `docs/specs/005-005-adoption-coherence/spec.md` (por referencia; versión/activación).
- **Autoridad** → `execution.md` (HITL) y `_validate_v2_vigency` (`cdad_packet.py:1558-1624`); la
  autoridad **original** del dueño es el fundamento del caso «sin delegación» (PD-6/P2).
- **Forma del state y vocabulario de etapas** → `state-detection.md:20-37` + `assets/state-template.json`.
- **Aprobación pinneada por rol (D3/PD-18)** → `docs/specs/005-001-idle-and-v7-bootstrap/spec.md:58-65,130`
  (**extendida** por D-8, no re-declarada).
- **Marcadores de diagnóstico (PD-12)** → `docs/specs/005-001-idle-and-v7-bootstrap/spec.md:69-73,99`
  (**extendida** con `evidence missing`, D-10).
- **Reemplazo de paquetes / obsolescencia** → `project-execution.md:186-254` (`--replace-packet` sólo
  `prepared`).
- **Planificación por unidad y simetría con `open-unit`** → `docs/specs/005-007-progressive-planning/spec.md`
  y `.../plan.md` (D-3/`005-007/debt.md:11`); precedente `open_unit` (`cdad_packet.py:4485-4551`).
- **Recepción / recibo durable / materialización** → `docs/specs/003-002-artifact-tools/spec.md` §2-§9 y
  `cdad_result.py:493-591` (`receive`), `:802-842` (`materialize`).
- **Frontera con 005-013** → `project-execution.md:83-84` y `docs/specs/005-013-unit-contract/debt.md:41-43`
  (nombrada, **no** implementada acá).
- **Patrón de aceptación** → `docs/specs/005-013-unit-contract/acceptance.md:7-20`;
  `tests/test_004_002_t2_bootstrap.py:44-70`, `tests/test_005_007_t3_open_unit.py:20-41`,
  `tests/product_staging.py`.

**Aditividad declarada (las únicas dos extensiones).** (1) El vocabulario de marcadores de 005-001 PD-12
suma **`evidence missing`**. (2) La selección de entradas `specification` de 005-001 D3/PD-18 suma el
predicado **vigente** (`supersedes`). Ambas son **aditivas** y se declaran aquí y en el plan. La corrección
**B2** no extiende ninguna regla ajena: agrega una clave **propia de esta unidad** a la forma del registro
(`transition_key_payload`, §2.2/PD-10), dentro del mismo escritor único. La clase
`disposition` (PD-21) y los digests derivados (PD-20) **no** agregan extensiones: reusan el vocabulario de
marcadores existente y el escritor único. La corrección **B3** tampoco agrega una tercera extensión:
**define** el predicado «vigente» que la extensión (2) ya había declarado, con el **mismo** criterio que el
cierre ya usaba (PD-8(b)), y **no** toca la regla del pin de su dueño (D3/PD-18).

---

## 9. Dudas del discovery §19 — resueltas o declaradas

| # | Duda | Resolución |
|---|---|---|
| 1 | Superficie | **Subcomando nuevo** `register-transition` (D-1). |
| 2 | Alcance por etapa | **Las cuatro clases + entrega tardía + disposición** (D-2/D-13); que alguna etapa sólo **gane traza** sin comprobación propia queda como **desconocido declarado** (§4). |
| 3 | Entrega tardía | El **buzón como entrada** con operación y **marcador propio** (D-5); la disposición es una salida **distinta** para el despacho sin recibo (D-13). |
| 4 | Comprobación de entregas | **En el cierre, antes de aplicar** (D-4); no en el registro (para no volver el registro un control frágil por etapa). |
| 5 | Vigencia de aprobaciones | **Campo estructural `supersedes`** en la entrada nueva + predicado **vigente** en el lector (D-8); aditivo sobre D3/PD-18. **Vigente** = el pin **nombra** los bytes actuales (**un solo** criterio, el mismo del cierre; B3), así que la reaprobación tras una enmienda **no** necesita `--supersedes` y el caso raro keyless va a deuda **D-16**. |
| 6 | Repetición | Clave **content-addressed** `transition_key` sobre el payload canónico (incluye `resolution` **y los insumos con efecto**: postcondición resuelta, `current_stage`, `artifacts`, y los campos de cada clase); idéntica = no-op; distinta (en cualquier insumo con efecto) = nueva entrada; excluyente = fail closed (D-7/PD-10..PD-12). |
| 7 | Reconciliación a nivel de ejecución | **Entra** como la comprobación de entregas requeridas (D-9, decisión (i)); el **veredicto fino** queda como deuda **D-1** con condición de cierre. |
| 8 | Frontera de 005-013 | Se la **nombra** (§8) y se resuelve D-2 por (i); **no** se implementa la tabla de consecuencias (§6). |
| 9 | Despacho que no vuelve (B1) | **Clase `disposition`** (D-13/PD-21), con la feature abierta; el cierre la acepta y la ofrece. Los despachos de ejecuciones cerradas quedan fuera (D-11). |
| 10 | Digests por argumento (P1) | **Opcionales y derivados por el CLI** (D-14/PD-20); afirmarlos sólo para citar los bytes revisados. |
| 11 | Autoridad sin delegación (P2) | **Tres casos** (D-6/PD-6); el límite del estado se declara (D-10). |

---

## 10. Anonimización

Este documento y el plan no contienen rutas absolutas del dueño ni ids crudos de sesión: usan
`<home>`, `<repo>`, `<tmp>`, `<ses-…>` y `<exec-id>`. No nombran proyectos de otros clientes; el
consumidor con tests anidados se cita por su unidad (**005-008**). Los fixtures que imitan otro proyecto
son **sintéticos y anónimos** (patrón de `docs/specs/005-013-unit-contract/acceptance.md:16-20`).

---

## 11. Estado del documento
**Estado: APROBADA.** El **architect** no aprueba su propia propuesta (anti-sesgo, ADR-003/ADR-011: entregó este texto como DRAFT; su cabecera DRAFT se conserva como registro de la entrega). La **aprobó el orquestador OpenCode** el **2026-10-14** bajo la **HITL delegada del epic-005** (`docs/epics/epic-005-real-operation/execution.md:8-23`), **junto con el `plan.md` corregido y en una sola acción**. **Esta aprobación REEMPLAZA la del draft-003** (spec `56d0be4bd74d8dc0e68112d018850e6f18d26c7f16a9ce994879772bb0feedd5`, plan `fb270b70bc9841e1e027f1ec1561b204e95f3634ca275a991821c829f34885d0`), que queda **sustituida y no vigente** (y ya era inoperante por el pin); las del draft-002 (`6504e655…`) y draft-001 (`89ba8ea1…`) quedaron sustituidas del mismo modo.

**Motivo de la cuarta corrección (B3).** El orquestador Claude revisó el tramo anterior y declaró **bloqueante para el uso previsto** el hallazgo del orquestador OpenCode: el control de exclusión de PD-14 exigía `--supersedes <transition-key>`, y `--supersedes` **solo puede citar entradas con `transition_key`**, mientras que las aprobaciones registradas a mano (todas las de las features en curso de cualquier proyecto) son **keyless** — de modo que **tras el despliegue la primera reaprobación de cada feature en curso habría obligado a editar el state a mano**, que es exactamente lo que esta unidad elimina. **La enmienda:** una aprobación `specification` cuyo **pin (`contract_sha256`) ya no coincide con los bytes actuales** del contrato **no compite como «vigente»** en el control de exclusión — es **el mismo criterio** que PD-8(b) ya usa en el cierre, y esa entrada **igual ya no habilitaba nada** porque el lector exige que el pin coincida (D3/PD-18 de 005-001). Consecuencias declaradas: la reaprobación tras una enmienda **no necesita `--supersedes`**; `--supersedes` queda para reaprobar **los mismos bytes** (funciona como hoy); y el caso raro de los mismos bytes con una entrada vigente **sin clave** va a **deuda D-16** con condición de cierre, sin inventar mecanismo.

**Gate 2→3 revalidado con verificación propia del orquestador** (no por aceptación de la prosa):

- los cuatro bloques mínimos presentes; **PD-1..PD-21** continuas, **INV-1..INV-9**, **AC-1..AC-4** medibles, **D-1..D-16** (D-9 retirada, D-16 nueva);
- **sin** marca de aprobación ni frontmatter `approved_by` en la entrega del rol (grep: 0 coincidencias en los dos documentos entregados);
- anonimización limpia (0 rutas absolutas del dueño, 0 ids crudos de sesión, 0 nombres de otros proyectos);
- bloque canónico `plan-tasks` **byte-idéntico** al aprobado y **revalidado por el orquestador** con las funciones del propio CLI: **OK**, T1..T8, `validation_strategy` idéntica (1017 caracteres);
- **B3 aplicada** donde correspondía: PD-14 (el predicado que compite es «el pin nombra los bytes actuales», un solo criterio con PD-8(b)), D-8 (definición de *vigente* y límite declarado), la **resolución de las referencias colgantes a «§2.5»** (esa sección no existía: la vigencia vive en PD-14/§2.3), la fila de deuda **D-16** y la trazabilidad en §0.1; y **PD-15 y D-12 declarados sin cambios** (D-12 no se toca porque el predicado nuevo **no lee** `transition_key`).

**El defecto se midió, no se supuso.** El registro de la reaprobación del draft-003 (entrada `specification` del state, con su nota) transcribe las **dos** respuestas del CLI: `state incoherent: … already has a vigente specification approval … (transition_key None); registering a second vigente one requires --supersedes <transition-key> … (PD-14)` y `state incoherent: --supersedes … does not name an existing specification approval …`. Con la enmienda, ese registro manual deja de ser necesario.

**Registro manual declarado (última vez).** La aproximación de esta aprobación se registró **a mano** con un script en `.cdad/local/`, porque **el arreglo todavía no está implementado**: el control de exclusión sigue comportándose como antes hasta el GREEN de B3, así que la operación **seguiría** rechazando esta misma reaprobación. Es la **última transición manual por esta causa** y queda declarada como tal en la nota de la entrada. El arreglo va **RED primero** en el focal de **T5** y después el GREEN; ésas sí se registran con la operación.

La **firma y los hashes** están registrados en `docs/.cdad-state.json` (`stage_history`, `stage: specification`). El contrato **no arranca TDD**: sigue el **review-fix** de **B3**.

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-14
