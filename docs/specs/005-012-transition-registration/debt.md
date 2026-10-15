# Deuda de 005-012-transition-registration

Deuda consolidada al cierre, con **condición de cierre** por ítem. Criterio vigente (2026-10-12,
`docs/epics/epic-005-real-operation/execution.md:48-56`): se bloquea y se corrige ya lo que compromete el
resultado, la evidencia o el uso previsto; va a deuda lo que es una mejora o variante sin impacto material.
**Nada de esta lista bloquea el cierre de la feature**; cada ítem dice qué lo cierra. Los ítems **D-n** son
los de la spec §7 (su texto normativo vive ahí; acá se consolidan con su condición de cierre).

## 1. Deuda declarada por el contrato (spec §7)

| Id | Deuda | Condición de cierre |
|---|---|---|
| **D-1** | Generalizar el **veredicto** de `reconcile` (clasificación fina por paquete) a nivel de **ejecución**: esta unidad entrega la detección, el nombrado y el rechazo del cierre, no el veredicto fino (que vive en `cdad_continuity.py` y exige `--packet`). | La línea de continuidad (RD-a/RD-b, `execution.md:89-96`) o la próxima unidad que toque `cdad_continuity.py`. |
| **D-2** | **Campos derivados sin dueño:** `review_status` sigue apuntando a `docs/specs/005-013-unit-contract/review.md` con `active_feature` = 005-012 (y `audit_status` igual). La operación escribe **sólo** los campos de su clase y **no** barre derivados ajenos; en este ciclo `review_status` **no** se escribió a mano (el veredicto queda en `review.md` y en la entrada `review` del state). | Una decisión de alcance sobre el barrido de derivados en el cierre (¿el `closure` limpia `review_status`?) con su unidad. |
| **D-3** | Efecto del **tamaño del state** (la mayoría en `stage_history`; al cierre de esta feature el state pasa de 440 KB con 447 entradas) sobre la operación. La entrada que escribe es pequeña y no agrega copias. | **RD-b** (estado operativo compacto con historia durable). |
| **D-4** | **Despliegue**: la operación **no existe en la versión instalada** (compartida con 005-013). Ver §4. | El despliegue (reservado al dueño) + la comprobación de O3 en el activo instalado. |
| **D-5** | El rechazo de `prepare --new-execution` (PD-16) cubre el caso **acotado** del contexto v2 abierto y **sin uso** (el que crea `open-unit`). Un contexto creado por otra vía, o uno con paquetes, no se cubre. | Si se observa en un ciclo real: re-acotar y ampliar con evidencia. |
| **D-6** | El CLI verifica que la **delegación** esté vigente y resoluble, pero **no** puede verificar que **quien** aprueba sea la persona delegada (la delegación no nombra personas). | Una unidad de autoridad/HITL, si el dueño quiere una marca de identidad de quien aprueba. |
| **D-7** | D-3 de 005-013 (marca estructural de «restricción de aplicación inmediata»): no es esta unidad; acá sólo se la nombra. | La marca estructural declarada en los planes (decisión de 005-013). |
| **D-8** | El **staging del buzón** + descriptor `RESULT.json` sigue siendo del orquestador: la operación no lo automatiza (y en el cierre del Memory Bank se ejerció a mano: ver §3). | Deuda **D-10 de 005-004** («recepción de intervención cero»). |
| ~~**D-9**~~ | ~~Un despacho que el orquestador considere anulado también exige resolución.~~ **RETIRADA:** su salida es la **disposición** (PD-21/D-13), con la feature abierta, verificada por AC-4. | **Cumplida en esta entrega.** |
| **D-10** | **Autoridad sin delegación a nivel del estado:** P2 quita el bloqueo **de la operación**, pero la vigencia **del state** (`_validate_v2_vigency`, consumida por `validate-state`/`prepare`/`receive`) **sigue** exigiendo `hitl_delegation` con epic activo. | Una unidad de **autoridad/HITL** (005-001, dueño de la regla) que decida si el dueño sin delegación es una autoridad vigente a nivel de estado. |
| **D-11** | **Despachos sin recibo de ejecuciones cerradas:** el cierre mira **sólo** la ejecución activa y la disposición exige la feature **abierta**. | Si se observa un caso real: re-acotar y ampliar con evidencia (probablemente junto con D-1). |
| **D-12** | **Entradas registradas con la fórmula anterior de la clave:** conservan su `transition_key` y **no** se invalidan, pero repetir exactamente una de esas invocaciones **anexa una entrada nueva** en vez de reconocerse como no-op (no se migró el state: reconocerlas como no-op reabriría el fail-open que B2 cerró). En esta feature, 18 de las 26 entradas de la operación quedaron sin `transition_key_payload`. | Si la duplicación molesta en un ciclo real: una unidad que defina la compatibilidad (p. ej. reconocer ambas fórmulas como candidatas a no-op) **con** la guarda que B2 exige. |
| **D-13** | **O5 de la review:** la operación **no puede limpiar** `tdd_substage` (el vocabulario cerrado de `--substage` no admite `null`), así que el paso tdd→review del protocolo real deja un valor viejo (divergencia **informativa**: ningún validador lee el campo y `open-unit` lo limpia). | Unidad que dé un valor centinela o un `--clear-substage` declarado, o enmienda del texto del protocolo para tolerar el valor viejo; **con RED si cambia comportamiento**. |
| **D-14** | **O6 de la review:** PD-12(i) (cierre de una feature ya cerrada) sin guard ni test propio; la vía realista la atrapa la ausencia de `active_feature` (`state incoherent`). | Test del caso + guard temprano, o declarar que el guard anti-vía es el de `active_feature: null`. |
| **D-15** | **O7 de la review:** tres nits de cobertura declarada — (a) `--artifact` derivado **sin** aserción sin test directo; (b) el no-op «independiente de la cabeza» (D-7) **ya cubierto** por el RED de B2; (c) el conteo «despachos repetidos de un mismo paquete se cuentan una vez» (PD-8(a)) sin test explícito. | Tres focales chicos. |
| **D-16** | **Reaprobar los MISMOS bytes desde una aprobación vigente SIN clave** (keyless) no tiene salida por la operación: `--supersedes` no puede citarla y el control de exclusión la ve vigente. Es el **caso raro** (B3 lo acotó: la reaprobación tras una enmienda ya no lo necesita). | Unidad que defina la salida (no se inventó mecanismo); hasta entonces, la decisión del orquestador con registro manual declarado. |

## 2. Deuda y datos de la review formal (`review.md`)

- **Opciónales O1..O4:** **corregidos** en las enmiendas del contrato (draft-003 y draft-004) — texto de
  AC-4/ficha T3, paréntesis de `--stage`, la «tabla» de operaciones que no existía y el mecanismo del control
  de vigencia por fecha. **No son deuda.**
- **O5/O6/O7:** a deuda → **D-13/D-14/D-15** (§1).
- **Abstenciones (3):** (a) la evidencia de T8 — **resuelta** (corrida y repetida sobre el commit final);
  (b) la **suite completa** — **resuelta** en el cierre (1024 passed / 4 skipped, `closure-suite.md`);
  (c) la **auditoría recibo-por-recibo de las transiciones registradas** en el state durante el tramo —
  **material del audit del orquestador**, no de la review; el cierre deja constancia de que las 27 entregas de
  la ejecución tienen recibo durable (0 sin recibo) y de que el estado del gate de cierre comprueba esa
  condición antes de aplicar.

## 3. Deuda y datos de proceso (declarados durante el ciclo)

1. **El commit `da3612a`** (`state: sync .cdad-state.json checkpoint (HB 14 Oct)`, 4 líneas del state) fue
   emitido por un **proceso externo al ciclo** (heartbeat) y escribió el state **fuera del camino de la
   operación** (movió `active_packet` del RED de T1 al GREEN de T1 antes de que el orquestador registrara la
   transición). El state quedó válido y la transición se registró después. **Es evidencia de la clase de
   escritura que esta unidad reemplaza** (un escritor externo con acceso al state, sin transición registrada).
   *Cierre:* el `active_packet` pasa a tener un único camino de escritura por transición registrada — deuda
   de la unidad que gobierne a ese proceso.
2. **El `artifact_kind` inválido en la recepción del discovery** (un kind fuera de la tabla cerrada por
   rol/subetapa): el recibo inválido **no aprobó nada** (quedó en `pending`), se preservó en `.cdad/local/` y se
   rehízo la recepción con el descriptor correcto **sobre los mismos bytes**. El error fue del descriptor que
   armó el orquestador, no del rol. *Cierre:* una guía de construcción del descriptor en la operación (o la
   recepción de intervención cero, D-8/D-10 de 005-004).
3. **El ADR no tiene `artifact_kind` en la tabla cerrada del producto** (los kinds del scribe son
   projectbrief/systemPatterns/activeContext/progress): la entrega del Memory Bank se recibió por partes para
   los dos documentos admitidos, y el ADR se materializó **aparte**. *Cierre:* agregar el kind (y su raíz
   permitida) a la política de artefactos, o declarar que los ADR siguen el camino de materialización directa
   del orquestador (misma situación que declaró la review de 005-013).
4. **Un `active_packet` único obliga a serializar los RED del review-fix:** los dos RED (B2 y B1) no pudieron
   despacharse en paralelo — un `prepare` nuevo es rechazado mientras el paquete activo esté `dispatched` —.
   No es un defecto (es la exclusión declarada de paralelismo en la fila 12), pero **cuesta una ronda de
   serialización** por cada review-fix de más de un caso. *Cierre:* la unidad de paralelismo (fuera del
   alcance de esta feature).

## 4. Despliegue pendiente (del dueño) — necesario para el uso previsto

La operación **no existe en la versión instalada**: el próximo despliegue lleva **005-013 y 005-012 juntas**
(comparten el mismo bloque de cambios del CLI). Hasta entonces, en cualquier proyecto que use el CLI instalado
el registro de transiciones **sigue siendo manual** y la reaprobación de un contrato tras una enmienda obliga
al registro a mano (el defecto B3 **corregido en el repo**, pero **no desplegado**). **Bloqueo declarado con
responsable (dueño)**; no se declara verde por proximidad. *Cierre:* el despliegue (reservado al dueño) y la
comprobación posterior en el activo instalado (O3 de 005-013).

## 5. Los dos digests escritos mal a mano y corregidos — evidencia de por qué existe esta unidad

Dos veces en este ciclo el orquestador **transcribió un digest a mano** al registrar una aprobación y se
equivocó; las dos veces lo detectó en la misma sesión y **corrigió la entrada antes de commitear** (no quedó
ningún digest inexacto en el estado versionado — las entradas corregidas son las únicas que existen en git):

1. **Aprobación de la enmienda del contract por B2** (reaprobación del draft-003): la entrada se registró
   primero con el `receipt_sha256` del **paquete del draft-002** (el recibo anterior) y se corrigió al del
   paquete del draft-003 (`66f56dee…`).
2. **Aprobación de la enmienda del contrato por B3** (reaprobación del draft-004): la entrada se registró
   primero con un `receipt_sha256` **inexacto** y se corrigió al real (`45c2098d…`).

En los dos casos la corrección consistió en **retirar la entrada y volver a registrarla** (append-only
respetado: sólo se anexó la correcta) con un script propio en `.cdad/local/`. **Lo que esto evidencia:** el
registro manual obliga a calcular y transcribir digests que el CLI puede **derivar** (PD-20) y una
transcripción manual se equivoca; el precio de esa transcripción —y de un state editado a mano sin
comprobación previa— es exactamente lo que estas dos unidades (registro de transiciones y contrato por unidad)
eliminan. La traza durable de los dos casos está en los scripts locales corregidos
(`.cdad/local/005-012-register-reapproval-00{3,4}.py`) y en los informes del tramo; **no** hay un recibo ni un
commit que la conserve (los intentos incorrectos **nunca** se commitearon). *Cierre:* ninguno propio —es
evidencia del problema, no deuda—; se conserva como dato declarado, y su causa (transcripción manual de
digests) queda cerrada por PD-20.
