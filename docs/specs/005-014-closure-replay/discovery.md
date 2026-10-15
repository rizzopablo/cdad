# Discovery — 005-014-closure-replay (etapa 1: mapeo técnico)

Read-only. No edité archivos. Unidad pequeña correctiva sobre la operación `register-transition` que entregó 005-012 (ya cerrada). No propongo contrato (eso es draft): acá mapeo superficie, orden de chequeos, límites, riesgos y la verificación proporcional.

---

## 0. Defecto confirmado, con evidencia exacta

Contrato de la fila 14: `docs/epics/epic-005-real-operation/plan.md:47`; historia de la fila: `plan.md:144-157`.

En `skills/cdad-cycle/scripts/cdad_packet.py`, `register_transition`:

- resuelve la feature desde `state.active_feature` en `:5055`, con **una sola** excepción (late-delivery) en `:5056-5061`;
- el **guard de feature nula** está en `:5062-5065` y su texto es literalmente el defecto: `"state incoherent: there is no active feature to register a transition for (state.active_feature is null); open the unit first (`open-unit`)"`;
- el **no-op de PD-11** (`_registered_transition`, `:4757-4767`) se consulta en `:5310-5324`, **después** del guard y después de todo el bloque de `closure`.

Consecuencia mecánica: tras un cierre real, el efecto de `closure` deja `active_feature: null` (`:5460-5462`), de modo que una repetición idéntica de la misma orden **muere en el guard `:5062-5065`** (rc=2) y el mensaje sugiere `open-unit`. Nunca se llega a `:5310`. La forma del arreglo la fija el análogo ya declarado: `late-delivery` resuelve la feature por `--feature` cuando no hay activa (`:5061`), y por eso hoy funciona.

**Por qué el defecto es exclusivo de `closure` (y de `late-delivery`).** La repetición legítima de `delivery`/`advance`/`gate`/`disposition` ocurre con la feature **abierta** (un orquestador interrumpido a mitad del ciclo): el guard no dispara y el no-op `:5310` opera. `closure` es la **única** clase cuyo postcondicionado (`active_feature: null`, `:5460`) hace que la *siguiente* invocación idéntica corra inevitablemente sin feature activa. `late-delivery` es la otra clase que opera sobre una feature cerrada y **ya tiene la vía declarada** (PD-13). Esto acota el arreglo a una clase.

---

## 1. Ruta exacta de la corrección

**Superficie declarada.** `§2.1` de la spec: `docs/specs/005-012-transition-registration/spec.md:183-204`; `--feature` ya existe en la superficie (`spec.md:189`) y su help en el CLI promete «default: state.active_feature; REQUIRED by `late-delivery`» (`cdad_packet.py:5978-5981`). Vocabulario cerrado de seis clases: `:4665-4666`.

**Puntos exactos que hay que tocar (mapeo, no parche):**

| Punto | Ubicación | Rol |
|---|---|---|
| resolución de feature por clase | `:5055-5065` | `late-delivery` en `:5061`; `closure` hoy **no** la usa |
| payload canónico | `_transition_identity_payload` `:4690-4738` | incluye `execution_id`, `feature_id`, `closure{path,sha256}`, `approved_by` |
| clave | `_transition_key` `:4741-4754` | `sha256(json canónico sort_keys)` |
| búsqueda idempotente | `_registered_transition` `:4757-4767` | barre **toda** `stage_history` por `transition_key` |
| no-op | `:5310-5324` | retorno temprano **sin** escritura |
| comprobaciones del cierre | PD-8(a) `:5195-5209`; PD-8(b) `:5210-5235`; cierre+autoridad `:5236-5259` | corren **antes** del no-op |
| exclusiones estructurales | `:5326-5383` | marcadores por condición |
| efecto del cierre | `:5446-5462` | reescribe `status`/`closed_at`/`closure_evidence` |
| coherencia de reposo | `_validate_idle_coherence` `:508-543` | tolera el remanente de `execution` (`:513`) |

**Qué cambia si `closure` resuelve la feature por `--feature` cuando `active_feature` es null.** La superficie ya tiene el argumento; hoy `args.feature` se lee **solo** en `:5061` (verificado: única aparición en `register_transition`). Con la extensión del `:5061` a `closure`, el guard `:5062` pasa, y el replay idéntico **alcanza** el no-op `:5310` porque:

- `_resolve_active_execution` (`:2243-2249`) lee `state.execution`; el cierre **no** lo limpia (efecto `:5446-5462` no toca `execution`), así que el replay resuelve **el mismo `execution_id`** y el payload coincide;
- PD-8(a) recorre la ejecución activa (mismos paquetes, ya con recibo) → verde;
- PD-8(b) encuentra la aprobación `specification` vigente (el pin sigue nombrando el contrato) → verde;
- el `--closure-path` se repite igual y el digest se re-deriva igual.

**Necesario pero NO suficiente.** Con ese único cambio, la cláusula «rechaza cerrado si es un cierre **distinto**» de la fila queda sin cubrir: un `closure` con **otro payload** (otra `--stage`, otro documento de cierre) pasaría el guard ya liberado, pasaría PD-8 (que **no** mira el estado de la feature) y **re-cerraría**, reescribiendo `status`/`closed_at`/`closure_evidence` en `:5450-5459` — exactamente el re-cierre de D-14. Verificado: `CLOSED_FEATURE_STATUSES` (`:114`) se consulta en `disposition` (`:5142`) y `late-delivery` (`:5161`), **nunca** en la rama `closure`.

---

## 2. Orden de chequeos por clase

Escenario (i): **feature cerrada y `active_feature` null** (el orquestador interrumpido justo después del cierre). Escenario (ii): **otra feature activa**.

| Clase | (i) feature cerrada, sin activa | (ii) otra feature activa | ¿Es el mismo arreglo? |
|---|---|---|---|
| `delivery` | guard `:5062` → rc=2 «open the unit». Replay post-cierre **no** es caso legítimo (la vía de lo cerrado es `late-delivery`). | `_packet_request_belongs_to_execution` (`:5091-5095`) contra la ejecución activa → `evidence missing` si el paquete es de otra ejecución. Rechaza, no desvía. | **No.** Su replay legítimo es con la feature abierta; ahí el no-op ya opera. Declarar en la spec. |
| `advance` | guard `:5062` → rc=2. | `--feature` ignorado; escribe los campos **globales** `current_stage`/`tdd_substage` (`:5480-5483`) e incluye `feature_id`=activa en la clave. No hay caso «cerrado». | **No.** Declarar. |
| `gate` | guard `:5062` → rc=2. | **`--feature` ignorado** (solo `:5061` lo usa): `gate --feature X` con B activa registra una entrada `feature: B` pinneando el `contract_path` de X (`:5265-5267`, `:5385-5413`) — **desvío silencioso**. Impacto acotado: una aprobación así atribuida a B con `contract_path` ajeno **nunca autoriza** (PD-8(b) exige `docs/specs/<feat>/spec.md`, `:5214-5227`), queda huérfana. → **deuda priorizada** (la fila lo manda: «si no es el mismo arreglo, va a deuda»). | **No** (arreglo distinto). |
| `closure` | guard `:5062` → rc=2 **antes** del no-op `:5310`. **El defecto.** | **`--feature` ignorado**: `closure --feature X` con B activa resolvería `feature_id = B` (`:5055`) y **cerraría B** si PD-8(B) está verde — desvío silencioso. | **Sí, es el arreglo de esta unidad.** |
| `late-delivery` | **ya resuelve por `--feature`** (`:5061`); guard pasa; status cerrado (`:5160-5167`); replay idéntico alcanza `:5310`. **Es el modelo.** | `args.feature` manda (`:5061`): apunta a X correcto. | **No aplica: ya tiene vía declarada** (PD-13). Sin cambio. |
| `disposition` | guard `:5062` → rc=2; y aunque se resolviera por `--feature`, la clase **exige feature abierta** (`:5141-5147`). No es un caso legítimo post-cierre. | `--feature` ignorado; requiere la feature abierta. | **No aplica** (PD-21 la restringe a la feature abierta; dentro de su dominio el no-op ya funciona). |

**Hallazgo transversal (ii):** el escenario «repetición después de un **cambio** de feature activa» **no** lo arregla esta unidad. La identidad incluye `execution_id` (`:4721`), y `open-unit` acuña una ejecución nueva (`_next_execution_id` `:1655-1660`); por lo tanto, aun con `--feature X`, el payload del replay lleva **otra** ejecución → **otra** clave → `_registered_transition` no encuentra nada. Reconocerlo exigiría comparar el payload **sin** `execution_id` o buscar la ejecución de la feature — un cambio de la identidad de PD-10, **fuera** de la fila → **deuda priorizada**.

---

## 3. Límites y riesgos del arreglo

1. **El no-op del cierre llega tarde.** PD-8(a)/(b), el requisito de `--closure-path` y la autoridad (`:5195-5259`) corren **antes** de `:5310`. Son solo-lectura → INV-7 se mantiene (todo rechazo deja el state idéntico). Riesgo declarable: un replay **legítimamente idéntico** podría ser rechazado por PD-8 si el mundo cambió (contrato editado, recibo borrado, cierre movido) aunque la transición ya esté registrada. El no-op se alcanza **solo si las precondiciones de PD-8 siguen verdes**. Opción de mitigación en draft: para `closure`, resolver la clave y consultar `_registered_transition` **antes** de PD-8 cuando la feature ya está cerrada.
2. **No-op sin escritura.** El retorno de `:5318-5324` ocurre antes de `_publish_owned_atomically` (`:5490`), así que no hay escritura del state. Salvedad de árbol: dentro del lock se corre `cleanup_stale_transactions(project_root)` (`:5049`) y el lock crea/borra su archivo — la mitad «árbol» de INV-7 ya está declarada como no asertada (`docs/specs/005-012-transition-registration/acceptance.md:49-51`); lo asertable es **bytes del state iguales**.
3. **Forma del rechazo de un cierre distinto.** No debe sugerir abrir la unidad. El texto vigente a evitar es `:5064` (`open the unit first (`open-unit`)`). El mensaje del caso «feature ya cerrada» debe nombrar la feature y su estado y ofrecer la salida legítima (la traza ya está; no hay nada que abrir). El marcador del rechazo lo decide el draft.
4. **`--feature` que nombra una feature NO cerrada con otra activa.** Con el arreglo acotado a «sin feature activa», `--feature` seguiría ignorado cuando hay una activa → cerraría la **activa** (desvío). Regla a fijar en el draft: para `closure`, `--feature` solo actúa cuando **no** hay feature activa; si se da y **difiere** de la activa → rechazo de coherencia (no desvío silencioso). Además, si `--feature` nombra una feature cuyo `execution_id` no es el de `state.execution`, hay incoherencia feature↔ejecución: `register_transition` **no** la chequea hoy (el chequeo `state.active_feature != execution.feature_id` existe en `validate-state`, `:567-570`, no acá) — el draft debería declararlo.
5. **Cierre de una feature ya cerrada (D-14).** Como el guard `active_feature: null` deja de proteger tras el arreglo, el «rechaza cerrado» de la fila **exige** un guard por estado de feature. Sin él, un cierre distinto re-cerraría.
6. **Observación menor (fuera de alcance, VERIFY).** La spec PD-8(a) dice «mismo predicado que `_packet_has_receipt`» (`spec.md:321-323`), pero el código `_packet_has_receipt` (`:5669-5673`) comprueba el **directorio** de resultados, mientras `_durable_receipt` (`:4793-4814`) comprueba el **archivo** `receipt.json`. Divergencia de predicado, no relacionada con esta unidad; se anota para no confundirla con el arreglo.

---

## 4. Relación con la deuda de 005-012 — ¿esta unidad cubre D-14?

- **D-13/PD-13** (`docs/specs/005-012-transition-registration/debt.md:25`, `spec.md:434-453`): «vías declaradas». Es **el modelo** que fija la forma: la feature cerrada se nombra por `--feature`. No es deuda a cubrir: es la referencia.
- **D-14** (`debt.md:26`, `spec.md:1003`): «PD-12(i) sin guard ni test propio; la vía realista la atrapa la ausencia de `active_feature`». **Confirmado en el código**: no hay guard por `CLOSED_FEATURE_STATUSES` en `closure` (usos: `:5142`, `:5161`) y **no existe** ningún test que repita un cierre ya aplicado (barrido de `tests/test_005_012_t3_closure_dispatch_resolution.py` sin coincidencias).
- **Lo que dejaron review y cierre** (`docs/specs/005-012-transition-registration/closure.md:63-64`; `debt.md:32-35`): O5/O6/O7 → D-13/D-14/D-15; el cierre no reabrió el caso.

**Decisión de alcance (recomendación, no contrato):** esta unidad **sí cubre D-14**, pero acotado a la clase `closure`, porque el arreglo **invalida el guard actual**: al dejar de bloquear el guard `active_feature: null`, el «rechaza cerrado si es un cierre distinto» de la fila **obliga** a un guard por estado. D-14 es de la clase `closure`, así que no amplía el alcance («cualquier otro cambio de `register-transition`» queda fuera). **No** se cubren D-12, D-13, D-16. El texto normativo (un PD nuevo o enmienda de PD-12/PD-11) pertenece al draft.

---

## 5. Verificación proporcional que exigirá la spec

**Regresión focal (pytest, caja negra).** El patrón existente corre el CLI real como subproceso y asierta postcondiciones observables, sin mocks sobre el cableado: `tests/test_005_012_t3_closure_dispatch_resolution.py:318-460` (fixture), `:624-739` (cierre aplicado + `validate-state` antes/después). Focal nueva propuesta `tests/test_005_014_closure_replay.py`:

- (a) cerrar por la operación, capturar `state_bytes()`, repetir la **misma** invocación → **rc=0**, salida con el no-op que **nombra** la entrada existente, **state byte a byte igual**, una sola entrada `closure`, `closed_at`/`closure_evidence` intactos;
- (b) repetir con **otro payload** (p. ej. otra `--stage`) → **rc=2**, marcador coherente con el draft, el mensaje **no** contiene `open-unit`/`open the unit`, state byte a byte igual;
- (c) `--feature` nombrando **otra** feature cerrada (o una feature abierta con otra activa) → rc=2 de coherencia, sin re-cierre y sin desvío, state igual.

**Escenario de reanudación con el CLI real sobre proyecto descartable.** Mismo instrumento que T8: `acceptance.md:3-8,57-59` — CLI **del repo** como subproceso, proyecto en `<tmp>`, `HOME` del subproceso en un tempdir vacío, **nunca** este repo ni HOME. Arnés fuera de git `.cdad/local/005-014-replay-acceptance.py` (no versionado). La orden repetida, exacta:

```
python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \
  --project-root <ABS> --transition closure --stage feature-closure \
  --approve-by <texto> --closure-path docs/specs/<feat>/closure.md
```

(correrla dos veces: ciclo completo con la operación → cierre → «interrupción» = re-ejecutar la misma orden → no-op rc=0, bytes iguales).

**Comandos de verificación.**

```
# focal
python3 -m pytest tests/test_005_014_closure_replay.py -q -p no:cacheprovider

# regresión de los módulos tocados (identidad + clases)
python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py \
                 tests/test_005_012_t1_register_transition_base.py \
                 tests/test_005_012_t4_late_delivery.py \
                 tests/test_005_012_t5_approval_vigency.py -q -p no:cacheprovider

# escenario real sobre proyecto descartable
python3 .cdad/local/005-014-replay-acceptance.py

# suite completa y validadores: al cierre, por quien cierra (política de la parte común)
python3 -m pytest tests -q -p no:cacheprovider
make validate
```

**Evidencia que hace falta:** rc y salida de cada invocación (el no-op debe **nombrar** la entrada), `sha256` del `docs/.cdad-state.json` antes/después del replay (iguales), conteo de entradas `transition: "closure"` (1), y el mensaje del rechazo (sin `open-unit`) con su marcador.

**Convención aplicable.** Postcondiciones numeradas y observables antes del RED; tests de caja negra sobre el CLI real (sin mocks sobre el plumbing, como T1/T3); sin cobertura por cobertura. Las propiedades (invariantes) y el E2E son subetapas declaradas de la etapa 3, no de este discovery.

---

## 6. Ítems abiertos (VERIFY) y recomendación

**VERIFY (no inventar):**
- Marcador exacto del rechazo «cierre de una feature ya cerrada» (¿reusa `state incoherent` de PD-12(i) o el draft define otro?). **Depende del draft.**
- Texto exacto del mensaje que reemplaza al `:5064`, y si el draft lo declara como obligación de salida.
- Convivencia con `--closure-sha256` afirmado en el replay (payload lleva el valor resuelto, `:5295`, `:5306-5307`); confirmar con el draft que el replay idéntico también aplica a la forma que **afirma** el digest.
- Predicado `_packet_has_receipt` directorio vs archivo (§3.6): anotado, fuera de alcance.

**Recomendación al draft (sin redactar el contrato):**
1. Corregir en `closure` **solo**: (a) resolver la feature por `--feature` cuando no hay feature activa (extender el patrón de `:5061`), y (b) guard de feature cerrada que, con la clave ya registrada, devuelva no-op rc=0 sin escritura; si la clave **no** existe, rechace cerrado con un mensaje que no sugiera abrir la unidad. Esto **cubre D-14** en la clase `closure`.
2. Declarar explícitamente, en la spec, que `delivery`/`advance`/`gate`/`disposition` **no** requieren el mismo arreglo (su replay legítimo ocurre con la feature abierta) y que `late-delivery` es el modelo ya declarado.
3. Mandar a **deuda priorizada**: (i) el `--feature` silenciosamente ignorado en `gate` (y el desvío de `closure` con otra feature activa, según cómo lo cierre el draft), y (ii) el replay tras un **cambio** de feature activa (`execution_id` nuevo ⇒ clave distinta), que es una cuestión de identidad (PD-10), no de orden.
4. Mantener intactos: no-op sin escritura (INV-7/PD-11), `stage_history` append-only (INV-3), y el efecto de cierre (`:5446-5462`).

**Evidencia citada:** CLI `skills/cdad-cycle/scripts/cdad_packet.py:2243-2249,4665-4666,4690-4754,4757-4767,4793-4814,5055-5065,5080-5259,5289-5383,5446-5462,5669-5673,5978-5981`; spec `docs/specs/005-012-transition-registration/spec.md:183-204,316-453,528-562,583,1003`; deuda `…/debt.md:24-28`; cierre `…/closure.md:63-64`; aceptación `…/acceptance.md:3-8,49-51,57-59`; épica `docs/epics/epic-005-real-operation/plan.md:47,144-157`, `execution.md:48-56,83-88`; tests `tests/test_005_012_t3_closure_dispatch_resolution.py:318-460,624-739`, `tests/test_005_012_t1_register_transition_base.py:837+`.
