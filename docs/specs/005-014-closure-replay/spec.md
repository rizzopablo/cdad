# Spec — 005-014-closure-replay (v2, enmienda 001)

> Spec **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR — v2.** Texto del **architect** (`mofgw/deepseek-v4.1-flash`), entregado como **texto final** (el orquestador lo materializa). El architect **no** aprueba su propia propuesta (anti-sesgo, ADR-003/ADR-011): la aprobación la registra el orquestador bajo la **HITL delegada** del epic-005 (`docs/epics/epic-005-real-operation/execution.md:8-23`).
> **Contrato vigente:** `docs/epics/epic-005-real-operation/plan.md`, **fila 14** (`:47`) y las secciones que prevalecen sobre las filas (`:48-88`), sha256 `294e9bf5…` (el del `plan_sha256` del contrato de unidad). **Insumo principal:** el informe de discovery `docs/specs/005-014-closure-replay/discovery.md` (§0–§6), **resuelto por referencia**: no se repite. Rige el **criterio de review vigente del 2026-10-12** (`execution.md:48-56`).
> **Enmienda 001 (esta v2):** corrige una **contradicción interna** del v1 en el escenario central del dueño (detectada por el RED de T1). Declarada en «Enmienda 001» (abajo). Sólo toca PD-22 (tercera fuente de resolución), PD-24 (comparación contra la feature resuelta) y agrega PD-27 (aplicar un cierre exige feature activa). El resto se conserva **en sustancia**.
> **Forma decidida por el dueño:** spec **corta** y **sin plan aparte** (no hay `docs/specs/005-014-closure-replay/plan.md`). Se achica el volumen de documentos, no las garantías: gates registrados, roles separados y evidencia.
> **Sin rutas absolutas del dueño ni ids crudos de sesión** (`<ABS>`, `<tmp>`, `<feat>`, `<ses-…>`); rutas del repo relativas y `archivo:línea`.

**Feature ID:** `005-014-closure-replay` · **Epic:** `epic-005-real-operation` · **Depende de:** 005-012 (cerrada) · **Estado:** DRAFT (etapa 2, v2) — **sin aprobar**.

---

## 1. Descripción funcional

La operación `register-transition` de 005-012 (`docs/specs/005-012-transition-registration/spec.md`) resuelve la feature desde `state.active_feature` con **una sola** excepción (`late-delivery`), en `cdad_packet.py:5055-5061`, y su **guard de feature nula** (`:5062-5065`) rechaza con el texto `… there is no active feature … open the unit first (open-unit)`. El **no-op idempotente** de PD-11 (`_registered_transition`, `:4757-4767`, consultado en `:5310-5324`) corre **después** de ese guard.

El efecto de `closure` deja `active_feature: null` (`:5460-5462`) y **no** limpia `state.execution` (`new_state = dict(state)` en `:5429`; la rama `closure` de `:5446-5462` sólo reescribe `epic_features`/`active_feature`/`current_stage`/`active_packet`, nunca la clave `execution`). Por eso, **repetir la misma orden de cierre** muere hoy en el guard (`:5062-5065`, rc=2) con un mensaje que sugiere **abrir la unidad** — justo lo contrario de lo que corresponde cuando la feature **ya está cerrada**: un orquestador interrumpido después del cierre no puede reanudar con la misma orden.

Esta unidad **corrige sólo la clase `closure`**: (a) sin feature activa, resuelve la feature por `--feature`, y si no hay, por la **feature ligada a la ejecución activa** (`state.execution.feature_id`, que el cierre no limpia) — la forma que `late-delivery` ya usa para `--feature` (`:5061`); (b) si la clave de identidad (PD-10) ya está registrada en el historial de esa feature, la invocación es un **no-op exitoso** que lo dice y **no** escribe el state; (c) sin feature activa **nunca aplica** un cierre: o reconoce el ya registrado (no-op) o **rechaza cerrado** con un mensaje que **no** sugiere abrir la unidad, que **nombra** la feature y su estado y ofrece la salida legítima (PD-27). Con eso cubre **D-14** de 005-012 **acotada a `closure`**.

**Qué NO cambia.** El CLI sigue sin decidir el **significado** de un texto ni la **calidad** de una entrega (frontera del juicio, 005-012 §3/INV-5); la identidad de PD-10, las reglas del pin (PD-8(b)/PD-14), el efecto del cierre (PD-9) y las demás clases quedan intactos (§6 y «Enmienda 001»).

---

## 2. Contrato — postcondiciones (numeradas, observables)

Aditivas sobre PD-1..PD-21 de 005-012: **no** re-declaran ni modifican ninguna de esas reglas salvo el **orden** que PD-23 fija y la **resolución de feature** que PD-22 enmienda. Todas se observan sobre el **CLI real del repo** como subproceso (caja negra; sin mocks sobre el plumbing).

**PD-22 (resolución de la feature en `closure`; tres fuentes, en orden).** En `--transition closure`, la feature se resuelve en este **orden**:
(i) `--feature` si se da;
(ii) si no, `state.active_feature` si es un **string no vacío**;
(iii) si no, la feature ligada por la **ejecución activa** — `state.execution.feature_id` — si es un string no vacío.
Si **ninguna** de las tres existe → **rc=2**, marcador **`state incoherent`**, y el mensaje **nombra** que `state.active_feature` es nulo y que la repetición de un cierre ya aplicado nombra la feature con `--feature <feature-id>`; **no** contiene `open-unit` ni `open the unit`; el state queda **byte a byte idéntico** (INV-7/INV-11).

**Fundamento de la fuente (iii) — por qué no es un desvío silencioso.** La tercera fuente no es una búsqueda a ciegas en la historia: es **un único valor ligado por la ejecución activa**, el mismo que el CLI ya resuelve sin flag en `_resolve_active_execution` (`:2243-2249`, «Resolve the bound execution context from state.execution, without a flag»). `state.execution` es la proyección de la ejecución abierta sobre `V2_BINDING_FIELDS`, que incluye `feature_id` (`:77-80`), escrita en cada `prepare` (`:4482`) y cada `open-unit` (`:4631-4632`). El efecto del cierre **no** toca esa clave (`:5429`, `:5446-5462`), así que tras cerrar, la feature ligada por la ejecución sigue siendo exactamente la que el primer cierre resolvió desde `active_feature`: la repetición **verbatim** resuelve la **misma** feature cerrada y alcanza el no-op de PD-23. Es determinista y acotada a un valor, no una heurística. (El caso opuesto —replay tras un **cambio** de feature activa, donde habría que buscar la ejecución de la feature o comparar el payload **sin** `execution_id`— sí sería una búsqueda en la historia y **queda fuera** de esta unidad: **deuda E-2**.)

*Verificación (rama «ninguna de las tres»):* sobre un state con `active_feature: null`, sin `--feature` y sin feature ligada por la ejecución (`state.execution.feature_id` ausente o vacío):
```
python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \
  --project-root <ABS> --transition closure --stage feature-closure \
  --approve-by <texto> --closure-path docs/specs/<feat>/closure.md
```
→ rc=2; el texto trae `state incoherent` y **no** trae `open-unit`; ofrece `--feature <feature-id>`; `sha256` del state antes = después.

**PD-23 (repetición idéntica = no-op sin escritura, decidido por la identidad).** En `closure`, si el **`transition_key`** de la invocación (PD-10, `:4741-4754`; su payload incluye `feature_id` y `execution_id`, `:4721-4722`) **ya está registrado** en `stage_history` (`_registered_transition`, `:4757-4767`) → **rc=0**, la salida **nombra** la entrada existente (su `transition_key`), el state queda **byte a byte idéntico** (sin escritura) y existe **una sola** entrada `transition: "closure"` de esa feature.
**Orden (decisión de diseño 2).** Para `closure` con la feature **ya cerrada** (`_feature_status` ∈ `CLOSED_FEATURE_STATUSES`), la resolución del documento de cierre (PD-9/PD-20) y la búsqueda de identidad **preceden** a PD-8(a), PD-8(b) y el control de autoridad (PD-6). **Fundamento:** la fila 14 promete «repetir un cierre ya aplicado **no falla**» sin condicionarlo; hoy PD-8(a)/(b), el requisito de `--closure-path` y la autoridad (`:5195-5259`) corren **antes** del no-op (`:5310`), así que un replay legítimo podría ser rechazado por un mundo cambiado. **Consecuencia de la opción elegida:** la repetición legítima es no-op **aunque el mundo haya cambiado** después del cierre (contrato editado, recibo borrado, delegación revocada); y, en la rama de feature cerrada, el requisito de `--closure-path` se evalúa antes de PD-8. **Opción descartada (A):** mantener PD-8 antes del no-op → un replay legítimo podría ser rechazado por PD-8(b) (pin que ya no nombra los bytes), PD-8(a) (recibo ausente) o PD-6 (delegación revocada) **aunque la transición ya esté registrada**, contra la promesa de la fila. **Requisitos de argumento (declarado):** los chequeos de nivel de argumento de la clase (`--approve-by` no vacío, PD-6; `--stage` token plano, §2.1) siguen en la cabeza de la operación (`:5018-5046`) porque son insumos de la identidad; el no-op precede a **PD-8(a)/(b), al requisito de `--closure-path` y a la autoridad**, no a esos dos. **Límite declarado:** la identidad de PD-10 lleva el digest **resuelto** del cierre (PD-20), así que el documento citado debe seguir existiendo para recomputar la clave; si falta, la resolución falla cerrado con `evidence missing` (PD-20, sin cambio).
*Verificación:* cerrar y repetir la **misma** orden:
```
python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \
  --project-root <ABS> --transition closure --stage feature-closure \
  --approve-by <texto> --closure-path docs/specs/<feat>/closure.md
```
→ 1ª vez rc=0 (aplica el cierre); 2ª vez rc=0 con `transition already registered` + el `transition_key`; `sha256` del state antes = después; `len([e for e in stage_history if e["transition"]=="closure"]) == 1`. (Con la enmienda, la 2ª invocación resuelve la feature cerrada por la fuente (iii) de PD-22.)

**PD-24 (coherencia `--feature` ↔ feature resuelta; nunca desvío silencioso).** En `closure`: (a) si **existe** una feature resuelta por las fuentes (ii)/(iii) —esto es, `state.active_feature` es un string no vacío, o, si no, `state.execution.feature_id` lo es— y `--feature` se da y **difiere** de esa feature resuelta → **rc=2**, marcador `state incoherent`, nombrando **las dos** features; sin efectos. (b) si `--feature` se da y **no** nombra una entrada de `epic_features` → **rc=2**, marcador `state incoherent`, nombrando la feature desconocida; sin efectos. (c) `--feature` **igual** a la feature resuelta → se acepta (idéntico al default). (d) `--feature` ausente → la feature resuelta (activa si está; si no, la ligada por la ejecución; comportamiento nuevo de PD-22).
*Verificación:* con B activa, `closure --feature <A>` (A≠B) → rc=2, `state incoherent`, y el state **byte a byte idéntico** (no se cierra B ni A). Cubierto por `tests/test_005_014_closure_replay.py::test_pd24_closure_with_feature_differing_from_active_feature_fails_closed`.

**PD-25 (guard por estado: cierre de una feature ya cerrada; cubre D-14 acotada a `closure`).** En `closure`, si el `transition_key` **no** está registrado (PD-23 no disparó) y `epic_features[<feature>].status` ∈ `CLOSED_FEATURE_STATUSES` (`:114`) —donde `<feature>` es la **feature resuelta** por PD-22— → **rc=2**, marcador **`state incoherent`** (el marcador que 005-012 PD-12(i) **ya declara** para esta condición — no se inventa uno nuevo), y el mensaje: (a) **nombra** la feature y su estado; (b) **no** contiene `open-unit` ni `open the unit`; (c) ofrece la **salida legítima** — repetir la **misma** orden de cierre es un no-op (su identidad ya está registrada, PD-23) y una entrega que llegó **después** del cierre usa la vía declarada (`receive --late` + `--transition late-delivery`, PD-13); **no** ofrece una vía de re-cierre. Sin efectos (INV-7). Este guard corre **antes** de PD-8 (no hay nada que comprobar de un cierre ya aplicado) y es lo que impide el re-cierre de D-14 sin depender del guard `active_feature: null`.
*Verificación:* tras un cierre, una orden de cierre **distinta** (otro `--stage` u otro `--closure-path`) → rc=2, `state incoherent`, nombra la feature + `done`, **no** contiene `open-unit`; state byte a byte idéntico. Cubierto por `tests/test_005_014_closure_replay.py::test_pd25_distinct_closure_after_closure_rejects_closed_naming_feature_and_done`.

**PD-26 (el resto del cierre no cambia).** Cuando la feature **no** está cerrada y **hay feature activa** (primera aplicación del cierre), el camino vigente corre **sin cambios y en su orden actual**: PD-8(a) (`:5195-5209`), PD-8(b) (`:5210-5235`), el requisito de `--closure-path` (PD-9, `:5239-5250`), la autoridad (PD-6, `:5258`) y la aplicación (PD-9, `:5446-5462`). Ninguna de esas reglas se re-declara ni se modifica.
*Verificación:* los focales de 005-012 que tocan la operación siguen verdes:
```
python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py \
  tests/test_005_012_t1_register_transition_base.py \
  tests/test_005_012_t4_late_delivery.py \
  tests/test_005_012_t5_approval_vigency.py -q -p no:cacheprovider
```

**PD-27 (nueva — aplicar un cierre exige feature activa; el techo de la enmienda).** En `closure`, **sin** feature activa (`state.active_feature` nulo o vacío) la operación **NUNCA aplica** un cierre: sólo puede **reconocer** el ya registrado o **rechazar cerrado**. Concretamente, con `state.active_feature` nulo/vacío y la feature resuelta por PD-22:
(a) si el `transition_key` **ya está registrado** → **no-op** rc=0 sin escritura (PD-23);
(b) si **no** está registrado y la feature resuelta **ya está cerrada** (`CLOSED_FEATURE_STATUSES`) → **rc=2** (PD-25, con su marcador y su mensaje);
(c) si **no** está registrado y la feature resuelta **NO está cerrada** → **rc=2**, marcador **`state incoherent`**, y el mensaje **nombra la situación** (no hay feature activa que aplicar; el cierre citado no está registrado), **ofrece** `--feature <feature-id>` para repetir un cierre **ya aplicado**, y **no** contiene `open-unit` ni `open the unit`. Sin efectos (INV-7/INV-11).
**Relación con PD-26.** PD-26 conserva **intacto** el camino de la **primera** aplicación (feature abierta **y** activa). PD-27 es la regla que **impide que la enmienda ensanche el comportamiento**: la fuente (iii) de PD-22 sólo sirve para **resolver** la feature de un cierre ya aplicado (para el no-op o el rechazo), jamás para **aplicar** un cierre nuevo; la aplicación sigue exigiendo `active_feature`, exactamente como antes. Sin feature activa no se cierra nada.
*Verificación (caso (c)):* con `active_feature: null`, la ejecución ligada a una feature **abierta** y sin cierre registrado, `closure` sin `--feature` → rc=2, `state incoherent`, sin `open-unit`, con `--feature` en la salida; state byte a byte idéntico. Cubierto por `tests/test_005_014_closure_replay.py::test_pd22_closure_without_feature_and_without_active_feature_rejects_without_open_unit`.

### 2.1 Decisiones de diseño que esta spec fija

1. **Resolución de la feature de `closure` (PD-22 enmendada):** orden `--feature` → `active_feature` → feature ligada por la ejecución (`state.execution.feature_id`). Sin ninguna de las tres: rc=2 `state incoherent`, mensaje que nombra la situación y pide `--feature <feature-id>`; **sin** `open-unit`.
2. **Replay idéntico:** no-op rc=0 sin escritura, **antes** de PD-8 y de la autoridad cuando la feature está cerrada; opción descartada y consecuencias declaradas en PD-23.
3. **Rechazo del cierre distinto:** rc=2, **`state incoherent`** (marcador ya declarado por PD-12(i)), sin efectos, mensaje sin `open-unit` que nombra feature+estado y ofrece la salida legítima (PD-25). **No** se crea una vía de registro nueva.
4. **Guard por estado + techo de la enmienda:** PD-25 (feature cerrada) **y** PD-27 (sin feature activa no se aplica). Cubren **D-14** de 005-012 **acotada a `closure`**. **No** cubren D-12, D-13, D-16 (005-012).
5. **`--feature` que difiere de la feature resuelta:** rechazo de coherencia, nunca desvío silencioso (PD-24). La feature resuelta es la activa si está; si no, la ligada por la ejecución. El chequeo feature↔ejecución de `validate-state` (`:567-570`, rama single-model; la rama v2 `_validate_v2_state:656` **no** lo hace) **no** se replica acá: la identidad (el payload lleva `feature_id` **y** `execution_id`) + PD-24/PD-25/PD-27 ya hacen de un `--feature` desalineado un rechazo cerrado; replicarlo ampliaría el alcance → **deuda E-3** (§6).
6. **Las demás clases (punto (b) de la fila):** `late-delivery` es el **modelo ya declarado** (sin cambio, `:5061`); `delivery`/`advance`/`gate`/`disposition` **no** comparten el mismo arreglo (su replay legítimo ocurre con la feature **abierta**, donde el no-op ya opera y el guard no dispara) → **no se tocan acá**. El `--feature` silenciosamente ignorado en `gate` y el replay tras un **cambio** de feature activa (identidad con `execution_id`, PD-10) van a **deuda priorizada** (E-1/E-2, §6). Es una decisión de alcance, con su motivo: la fila manda corregir «sólo si es el mismo arreglo».
7. **Fuera de alcance, explícito:** cualquier otro cambio de `register-transition`; la identidad de PD-10; las reglas del pin (PD-8(b)/PD-14); el efecto del cierre (PD-9); y el predicado `_packet_has_receipt` directorio-vs-archivo (`:5669-5673` vs `_durable_receipt` `:4793-4814`, anotado por el discovery §3.6) → **deuda E-5** (§6).

---

## 3. Invariantes (verificables)

- **INV-10.** Una repetición idéntica **no** escribe el state: los bytes quedan iguales (005-012 INV-7/PD-11). *Verificación:* `sha256` de `docs/.cdad-state.json` antes = después del replay.
- **INV-11.** Toda validación y todo rechazo ocurren **antes** de cualquier escritura (005-012 INV-7). *Verificación:* en cada caso de rechazo de PD-22/PD-24/PD-25/PD-27, state byte a byte idéntico.
- **INV-12.** `stage_history` es **append-only**: ninguna entrada se reescribe (005-012 INV-3). *Verificación:* la entrada de cierre original queda intacta (mismo `transition_key`, `closed_at`, `closure_evidence`) tras el replay.
- **INV-13.** La identidad de PD-10 **no** cambia: el payload canónico conserva sus campos y su serialización (no se agrega ni se quita ninguno). *Verificación:* los focales de identidad de 005-012 (T1/T2/T5) siguen verdes.

---

## 4. Criterios de aceptación (medibles)

De **esta unidad** (distintos de los AC-1..AC-4 de 005-012). **Instrumento común:** el **CLI real del repo** como subproceso, sobre un **proyecto descartable** en `<tmp>`, con el **`HOME` del subproceso en un tempdir vacío**; **nunca** este repo ni HOME; arnés **fuera de git**; fixtures **sintéticos y anónimos** (patrón de `docs/specs/005-012-transition-registration/acceptance.md:3-8,57-59`).

- **AC-1 (regresión focal).** Cerrar una feature por la operación y repetir la **MISMA** orden → **rc=0**, no-op que lo dice y **nombra** la entrada existente, **state byte a byte igual** (`sha256` antes = después) y **una sola** entrada `closure`. *Evidencia:* `rc` y salida de las dos invocaciones; `sha256` del state antes/después; conteo de entradas `transition: "closure"`.
- **AC-2 (repetición con OTRO payload).** Repetir con otro payload (p. ej. otra `--stage` u otro `--closure-path`) → **rc=2**, sin efectos (state byte a byte igual) y el mensaje **no** contiene `open-unit`. *Evidencia:* `rc`, marcador `state incoherent`, ausencia de `open-unit`, `sha256` igual.
- **AC-3 (reanudación con el CLI real).** Escenario sobre un proyecto descartable: cierre aplicado → «interrupción» (re-ejecutar la **misma** orden) → **no-op** (rc=0, bytes iguales). Mismo instrumento que T8 de 005-012; arnés fuera de git `.cdad/local/005-014-replay-acceptance.py`. La orden repetida, exacta:
```
python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \
  --project-root <ABS> --transition closure --stage feature-closure \
  --approve-by <texto> --closure-path docs/specs/<feat>/closure.md
```
  *Evidencia:* salida de las dos corridas, `sha256` del state antes/después, `validate-state` rc=0.
- **AC-4 (no-regresión, si corresponde).** Los focales de 005-012 que tocan la operación siguen verdes (comando de PD-26). *Evidencia:* salida de `pytest` con el conteo.

**Prueba decisiva (fila 14):** cerrar una feature y repetir la misma orden de cierre (rc=0, no-op, state byte a byte igual); una repetición con otro payload rechaza; y el escenario de reanudación de AC-3 con el CLI real sobre un proyecto descartable.

**Gates de tests.** El **implementer** corre los focales y los **módulos tocados** (los cuatro de PD-26). La **suite completa** (`python3 -m pytest tests -q -p no:cacheprovider`) la corre **quien cierra, una vez, en un worktree aparte** (política de la parte común). `make validate` puede dar **F011** (`scripts/validate-subagents.sh`, drift de copia instalada): **preexistente y declarado**, no una regresión de esta unidad.

---

## Enmienda 001 (v2) — motivo, qué cambió y qué no

**Motivo (defecto del contrato v1, detectado por el RED de T1).** El v1 era **internamente contradictorio** en el escenario central del dueño: PD-22 resolvía la feature de `closure` como «`--feature` si se da, y si no `state.active_feature`», mientras PD-23 y PD-25 (y sus comandos de verificación, y AC-1/AC-3) prometían que **repetir la MISMA orden de cierre** de una feature ya cerrada es un **no-op**. Tras el cierre, `state.active_feature` es `null` (`:5460`), así que la orden repetida **verbatim** no resolvía ninguna feature y moría en el guard de PD-22 (`:5062-5065`, rc=2): el no-op era **inalcanzable**. El focal `tests/test_005_014_closure_replay.py` (escrito por un test-writer aislado a partir de este contrato) lo reproduce en `test_pd23_*` y `test_pd25_*` con la orden literal. El dueño pidió expresamente que un orquestador interrumpido justo después del cierre **pueda reanudar con la misma orden**.

**Qué cambió (exactamente tres puntos).**
1. **PD-22 — tercera fuente de resolución.** Se agrega (iii): la feature ligada por la ejecución activa (`state.execution.feature_id`), que el efecto del cierre **no** limpia (`:5429`, `:5446-5462`). Con eso, la orden de cierre repetida resuelve la feature cerrada y alcanza el no-op de PD-23. Se justifica por qué (iii) **no** es un desvío silencioso (un único valor ligado por la ejecución, `:2243-2249`, no una búsqueda en la historia).
2. **PD-27 (nueva) — aplicar un cierre exige feature activa.** Sin `active_feature` la operación **nunca aplica** un cierre: sólo reconoce el ya registrado (PD-23) o rechaza cerrado (PD-25 si la feature resuelta ya está cerrada; PD-27(c) si no lo está y la clave no está registrada). Es el **techo** que impide que la enmienda ensanche el comportamiento. Relación con PD-26 declarada (PD-26 conserva intacto el camino de la primera aplicación).
3. **PD-24 — comparación contra la feature resuelta.** El rechazo por incoherencia compara `--feature` con la feature **resuelta** (la activa si está; si no, la ligada por la ejecución): si difiere → rc=2 nombrando las dos. Se conserva el resto (entrada desconocida → rc=2; igual a la resuelta → se acepta; ausente → la resuelta).

**Qué NO cambió (por qué el resto sigue intacto).** La enmienda es **aditiva**: no altera el payload de identidad de PD-10 (`:4690-4738`, `:4741-4754`), ni el no-op (PD-23/PD-11, `:5310-5324`), ni el **orden** que PD-23 fija (el no-op precede a PD-8 y a la autoridad en la rama cerrada), ni el efecto del cierre (PD-9, `:5446-5462`), ni el camino de la primera aplicación (PD-26), ni el guard por estado (PD-25), ni las reglas del pin (PD-8(b)/PD-14), ni los invariantes (INV-10..INV-13), ni los criterios AC-1..AC-4, ni la deuda E-1..E-5, ni las reglas de anonimización. La única superficie tocada es **cómo se resuelve la feature** de `closure` y **la prohibición de aplicar sin feature activa**; todo lo demás se conserva **en sustancia y en su texto**.

**Correspondencia con el focal de T1 (declarada, para no confundir cobertura con contrato).**
- `test_pd23_*` y `test_pd25_*` (la orden literal, sin `--feature`) pasan **por la fuente (iii)**: tras el cierre, `state.execution.feature_id` sigue ligado a la feature cerrada, que así se resuelve (PD-23 no-op / PD-25 rechazo cerrado).
- `test_pd22_*` — `active_feature` puesto a `null` pero `state.execution.feature_id` aún ligado (la ejecución del fixture) — resuelve por (iii) la feature **abierta** y cae en **PD-27(c)** (sin feature activa no se aplica nada; no cerrada; clave no registrada): rc=2, `state incoherent`, sin `open-unit`, con `--feature` en la salida. Coincide con los observables que el focal asevera.
- `test_pd24_*` cubre PD-24(a) con la feature activa.
- La rama «ninguna de las tres» de PD-22 (todas las fuentes ausentes) es un **fallback defensivo** y **no** tiene caso propio en el focal (ver **E-6**, §6).

---

## 5. Tareas de la etapa 3 (dentro de esta spec; no hay plan aparte)

- **T1 — RED focal + GREEN de la clase `closure` sin feature activa.** Focal `tests/test_005_014_closure_replay.py` (caja negra: subprocess sobre el CLI real, reutilizando el patrón y los helpers de `tests/test_005_012_t3_closure_dispatch_resolution.py`). Casos, cada uno apuntando a una postcondición:
  - replay **idéntico** tras un cierre → PD-23 (+ INV-10/INV-12): rc=0, salida que nombra la entrada, state byte a byte igual, **una** entrada `closure`;
  - **cierre distinto** (otro `--stage`/`--closure-path`) → PD-25 (+ INV-11): rc=2, `state incoherent`, nombra feature+`done`, **sin** `open-unit`, state igual;
  - `--feature` que **difiere** de la activa → PD-24: rc=2, `state incoherent`, state igual;
  - `--feature` **faltante** sin feature activa → PD-22/PD-27(c): rc=2, `state incoherent`, sin `open-unit`, con `--feature`, state igual.
  El **GREEN** implementa PD-22..PD-25 y PD-27 en `register_transition`: extender la resolución de feature de `:5061` a `closure` con las **tres fuentes** (`--feature` → `active_feature` → `state.execution.feature_id`); agregar el guard por `CLOSED_FEATURE_STATUSES`; **impedir la aplicación sin feature activa** (PD-27) y **reordenar** el no-op en la rama de feature cerrada (PD-23). No se toca la identidad (PD-10) ni el efecto del cierre (PD-9).
- **T2 — escenario de reanudación de AC-3** con el CLI real sobre un proyecto descartable (arnés `.cdad/local/005-014-replay-acceptance.py`, fuera de git).

---

## 6. Deuda declarada

| Id | Deuda | Motivo / condición de cierre |
|---|---|---|
| **Cobertura de D-14** (005-012) | **Cubierta, acotada a `closure`:** PD-25 (guard por `CLOSED_FEATURE_STATUSES` antes de re-cerrar) + PD-27 (sin feature activa no se aplica) + el RED de T1. | El arreglo **invalida** el guard `active_feature: null`, así que el «rechaza cerrado» de la fila **obliga** a un guard por estado; D-14 es de la clase `closure` y no amplía el alcance. **No** se cubren D-12, D-13, D-16 (005-012). |
| **E-1** (priorizada) | `gate` **ignora** `--feature` en silencio: `gate --feature X` con B activa registra una entrada `feature: B` pinneando el `contract_path` de X (`:5265-5267`) — desvío silencioso; la entrada queda huérfana (nunca autoriza, PD-8(b) exige `docs/specs/<feat>/spec.md`). | **Arreglo distinto** al de esta unidad (la fila manda a deuda lo que no es el mismo arreglo). Una unidad que haga actuar/validar `--feature` en todas las clases. |
| **E-2** (priorizada) | Replay tras un **cambio** de feature activa: la identidad incluye `execution_id` (`:4721`) y `open-unit` acuña una ejecución nueva (`_next_execution_id`), así que aun con `--feature X` el payload lleva **otra** ejecución → **otra** clave → no hay no-op. | Es una cuestión de **identidad (PD-10)**, no de orden → fuera de la fila. Una unidad que decida comparar el payload sin `execution_id` o buscar la ejecución de la feature, con RED. **La enmienda 001 no la toca**: la fuente (iii) lee **un** valor ligado por la ejecución, no busca en la historia. |
| **E-3** | El chequeo feature↔ejecución de `validate-state` (`:567-570`, rama single-model) **no** se replica en `register_transition`: con `active_feature` presente, PD-22 resuelve por (ii) y **no** compara contra `state.execution.feature_id`; la incoherencia activa↔ejecución no se chequea. | El payload (PD-10) lleva `feature_id` **y** `execution_id`, y PD-24/PD-25/PD-27 hacen de un `--feature` desalineado un rechazo cerrado; replicar el chequeo ampliaría el alcance. Se cierra si un caso real lo exige. |
| **E-4** (límite declarado; consecuencia de D-12) | Una entrada `closure` registrada con la **fórmula anterior** de la clave (sin `transition_key_payload`) **no** se reconoce como no-op; como la feature está cerrada, PD-25 la rechaza. | D-12 (005-012) **no** se cubre; no se migra el state ni se recomputan claves históricas. |
| **E-5** (anotada, fuera de alcance) | Predicado `_packet_has_receipt` **directorio** (`:5669-5673`) vs `_durable_receipt` **archivo** (`:4793-4814`). | Divergencia de predicado **no** relacionada con esta unidad (discovery §3.6); se anota para no confundirla con el arreglo. |
| **E-6** (nueva, cobertura declarada) | La rama «ninguna de las tres» de PD-22 (sin `--feature`, `active_feature` nulo y `state.execution.feature_id` ausente/vacío) **no** tiene caso propio en el focal. | Es un **fallback defensivo**: en un state v2 bien formado la clave `execution` se escribe con `feature_id` (`:77-80`, `:4482`, `:4631-4632`), así que la rama sólo se alcanza con un binding malformado. Se declara para no presentarla como cubierta; se cierra si un caso real la exige. |

---

## 7. Anonimización

Este documento usa **rutas relativas del repo** y referencias `archivo:línea`; los lugares que en la ejecución son absolutos o efímeros se escriben como `<ABS>`, `<tmp>`, `<feat>`, `<ses-…>`. **No** contiene rutas absolutas del dueño ni ids crudos de sesión; **no** nombra proyectos de otros clientes. Los fixtures de T1/T2 son **sintéticos y anónimos** (mismo patrón que los focales de 005-012). La enmienda 001 **no** cambia estas reglas: agrega referencias `cdad_packet.py:77-80,2243-2249,5429,5446-5462` (todas relativas al repo), sin datos del dueño.

---

## 8. Estado del documento

**Estado: DRAFT — SIN APROBAR (v2, enmienda 001).** El architect entrega este texto como propuesta y **no** lo aprueba (anti-sesgo, ADR-003/ADR-011). La **aprobación** (y la autorización de la etapa 3) la registra el **orquestador** bajo la HITL delegada del epic-005, con el gate de etapa 2 correspondiente. **No** se crea `plan.md` (forma liviana decidida por el dueño). Sin marca de aprobación en esta entrega.

---

**Resumen para el orquestador (fuera del contrato):** spec corta **v2** entregada como texto final; la **enmienda 001** aplica tres cambios —PD-22 con la tercera fuente de resolución (`state.execution.feature_id`, justificada), PD-27 nueva (sin feature activa no se aplica ningún cierre) y PD-24 comparando contra la feature resuelta— y conserva el resto en sustancia (PD-23/PD-25/PD-26, invariantes INV-10..INV-13, AC-1..AC-4, deuda E-1..E-5, anonimización). Agrega E-6 (cobertura declarada del fallback de PD-22). Queda **sin aprobar** para tu decisión bajo HITL delegada.
