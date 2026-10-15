# ADR-023 — La delegación externa entre CLI es una interfaz común con un adaptador por destino que reutiliza el mecanismo existente; rol, CLI y modelo son decisiones independientes, la entrega no aprueba el gate y la delegación no amplía autoridad

* Estado: **Aceptado** (2026-10-11; orquestador bajo delegación HITL de epic-005)
* Fecha: 2026-10-11
* Decisores: orquestador bajo delegación HITL de epic-005 (aprobación del dueño, `execution.md`)
* Confianza: **Media-Alta**

## Contexto y enunciado del problema

005-009 busca que un agente autorizado (coordinador) pueda **encargar un paquete CDAD ya
preparado a una sesión de rol en OTRO CLI** y recibir su entrega por el flujo CDAD existente, con
proyecto, rol, configuración, entrega y re-entry verificables. El recorrido es `agente autorizado
→ encargo canónico → adaptador del CLI destino → sesión de rol → resultado durable → re-entry del
responsable`.

Tres hechos del discovery definen el problema arquitectónico:

1. **El mecanismo ya existe y debe reutilizarse.** `prepare` (paquetes canónicos), el registro de
   despacho I8 (`--record-dispatch`), el ledger `.cdad/executions/<id>/dispatches/`, los recibos
   (`cdad_result.py receive`) y la reconciliación (`cdad_continuity.py reconcile`/`resume`); el
   state del ciclo tiene un **único escritor** (el orquestador). Lo que **falta** es el
   **transporte**: no existe un dispatcher/adaptador previo como script en el producto; el
   despacho real se hizo a mano.
2. **El modo de carga del rol en OpenCode es el punto más delicado.** Los roles se generan
   `mode: subagent` y el orquestador `mode: all`; hay evidencia local (2026-09-29) de que una
   entry `mode: subagent` **cuelga en silencio** y de que existen agentes **no-Cdad** en el mismo
   namespace (riesgo de fallback silencioso a un agente genérico).
3. **La configuración efectiva de una sesión no tiene lector de producto:** solo se infiere del
   registro I8.

La pregunta arquitectónica es **cómo agregar el transporte de la delegación externa sin duplicar
el mecanismo, sin crear otro state/ledger y sin ampliar autoridad**, y **cómo hacerlo extensible a
otros destinos sin un script por pareja de herramientas**.

## Decisión

1. **Una interfaz común de delegación, agnóstica del destino, con un adaptador por destino
   (PD-1/INV-2).** El producto expone `cdad_delegate.py` (interfaz) que resuelve el adaptador por
   **convención de módulo** (`cdad_delegate_<id>.py` en el mismo directorio). Invocada con
   (proyecto, paquete canónico, destino, configuración de ejecución) devuelve
   `{attempt, session, termination, delivery_ref, diagnosis}`. **Agregar un destino no edita la
   interfaz** (no hay un script por pareja).
2. **La interfaz reutiliza el mecanismo existente y no crea otro state ni otro ledger
   (PD-2/INV-1/INV-3).** Reutiliza `prepare`, el registro I8, el ledger, `receive` y `reconcile`;
   **transporta el `PACKET.md` íntegro y byte-idéntico** (sin re-render ni plantilla paralela);
   toma `execution_id`/`packet_id`/`role`/`substage` **del paquete publicado**, nunca del
   documento de observación; **nunca** escribe `docs/.cdad-state.json`.
3. **El proyecto es explícito e independiente del directorio del coordinador (PD-3).** Se resuelve
   con `--project-root`; correr desde un cwd no relacionado con el proyecto resuelve el paquete de
   ESE proyecto. El producto no resuelve recursos desde el cwd del coordinador.
4. **El modo de carga soportado se verifica y falla cerrado, sin fallback genérico (PD-4/D5).** El
   adaptador verifica la entry no-interactiva contra los agentes derivados publicados; una entry
   no soportada (p. ej. `mode: subagent` como principal) **falla cerrado** con diagnóstico que
   nombra agente y modo, **no despacha sesión** y **jamás** cae a un agente no-Cdad.
5. **La espera es sobre una señal durable, no sobre el `rc` del cliente (PD-5/INV-6).** Acotada,
   sin sondeo sin límite y sin callback inventado; un cliente que retorna **antes** de que el rol
   termine **no** produce `completed`. El adaptador responde **dentro de la cota que recibe**.
6. **Vocabulario de terminación con entrega ≠ gate (PD-6/D4/INV-5).** `completed`, `blocked`,
   `transport-error`, `timeout`, `cancelled` (y `unknown`), derivados de **hechos materiales**.
   `rc=0` **no** aprueba un gate: el recibo queda `semantic_status:"pending"` y el gate lo decide
   el responsable en el re-entry. Un `timeout` **no** prueba ausencia de cambios; tras una
   interrupción los efectos se **reconcilian** antes de repetir, y `_classify` distingue
   `dispatched-unknown` (no fallo) de éxito.
7. **Configuración portable: configurado/observado/`unknown`, sin valores del host (PD-8/INV-7).**
   Modelo, binario/versión, logs, servidores y tiempos viven en la config de ejecución (local,
   git-ignorada) o flags; **ningún** valor de este VPS aparece en el producto ni en contratos
   públicos.
8. **La prohibición heredada de spawn se conserva y se distingue de la delegación externa
   (PD-9).** La anti-recursión se conserva donde el runtime no soporta el spawn nativo; la
   delegación externa autorizada (coordinador→worker **entre CLIs**) se distingue de la recursión
   de subagentes **dentro del mismo runtime**. Primer aterrizaje: coordinador→worker, devolución
   al coordinador, **sin** recursión automática. Una delegación **no** amplía autoridad ni permite
   al worker escribir el state.
9. **El recorrido real es el gate de integración, no un test (PD-10).** El primer recorrido real
   Claude → OpenCode → recepción CDAD, desde la instalación elegida, con re-entry, lo corre el
   orquestador con el dueño y se registra como evidencia.
10. **Frontera explícita (INV-9).** No scheduler, no instalación automática de CLI, no sandbox; no
    se implementan todos los destinos (solo OpenCode); la dirección inversa y otros CLI son
    incrementos posteriores.

## Consecuencias

* **Positivas.** El transporte de la delegación se agrega **sin duplicar** el mecanismo (paquetes,
  I8, ledger, recibos, reconciliación, single-writer del state) ni la autoridad; agregar un destino
  es **aditivo** (un módulo, sin editar la interfaz); el modo de carga no soportado **no** produce
  un falso éxito; la entrega y el gate quedan separados; la configuración no filtra el host; y la
  distinción delegación-externa/recursión **no** debilita el SPAWN GUARD.
* **Negativas / costos.** La resolución por **convención de módulo** acopla el nombre del archivo
  al id del destino (un id mal nombrado → adaptador no resoluble, fail-closed). El adaptador hereda
  dependencias del destino concreto (la **superficie de señal durable** y el **modo de carga
  soportado** de la versión vigente), que hay que confirmar por versión (VERIFY-3). El transporte
  byte-idéntico obliga a que la interfaz **no** interprete el paquete. Los opcionales de la review
  (cota de espera ausente → invocación sin cota; `--packet-id` sin validar en el adaptador) son
  costos abiertos del diseño actual.
* **Riesgo aceptado.** La **mediación en vivo** de un proceso de runtime real y el **recorrido
  real** (PD-10) **no** se demuestran por los tests (que verifican la interfaz y el adaptador con
  un binario falso y un destino de prueba); el gate de integración es del dueño. Límites honestos:
  una sesión/proceso separado **no** es un sandbox y cambiar de CLI **no** garantiza otra familia
  de modelo (INV-8).
* **Sin cambios de forma.** `prepare`, el esquema cerrado de I8, `cdad_result.py`,
  `cdad_continuity.py`, el clasificador, el guard de Claude Code y la publicación atómica **no**
  cambian; solo se agrega el transporte y se reconcilia la prosa del SPAWN GUARD.

## Alternativas consideradas

* **Un script por pareja de herramientas (coordinador×destino).** Rechazada (D1/INV-2): multiplica
  el mantenimiento y contradice «un adaptador por destino».
* **Un runner genérico de jobs / scheduler / sandbox.** Rechazada (INV-9): fuera de alcance.
* **Crear un state/ledger propio de la delegación.** Rechazada (D2/INV-1/INV-3): el state tiene
  único escritor y el mecanismo (I8/ledger/recibos) ya existe.
* **Esperar sobre el `rc` del cliente de invocación.** Rechazada (D6/INV-6): el cliente puede
  volver antes de que el rol termine; se espera sobre la señal durable.
* **Tomar `rc=0` como aprobación de gate.** Rechazada (D4/INV-5): la entrega y el gate son hechos
  distintos; el recibo queda `pending`.
* **Fallback a un agente genérico si la entry no es soportada.** Rechazada (D5/PD-4): silenciaría
  el modo de carga no soportado; se falla cerrado con diagnóstico nombrado.
* **Reutilizar `run-python-unittest` como adaptador.** Rechazada (D2/VERIFY-5): es un runner
  **especializado** a `python3 -m unittest`; sirve de **patrón**, no de adaptador listo.

## Referencias

* Contrato: `docs/specs/005-009-cli-delegation/spec.md` (PD-1..PD-10, INV-1..INV-10; D1–D10) y
  `plan.md` (T1–T4).
* Insumo: `docs/specs/005-009-cli-delegation/discovery.md`.
* Revisión: `docs/specs/005-009-cli-delegation/review.md` (OK, 0 bloqueantes); cierre:
  `docs/specs/005-009-cli-delegation/closure.md`.
* Referencia operativa: `skills/cdad-cycle/references/cli-delegation.md` (dueño del contrato de la
  interfaz y del adaptador).
* Fronteras: ADR-003, ADR-008, ADR-019 y ADR-020.

## Enmienda (2026-10-11) — señal durable real, identidad desde la fila, `mode` soportado y directorio del proyecto (005-010)

* Confianza: **Media-Alta** (decisiones respaldadas por sondas del runtime instalado + una corrida
  de aceptación real; el esquema del store **no** es contrato público y su estabilidad entre
  versiones queda como riesgo mitigado por fallo cerrado).

**Contexto.** ADR-023 se aprobó con la superficie de 005-009. La aceptación real de 005-010, contra
el runtime instalado, corrigió premisas materiales de los puntos 4 y 5 y confirmó el alcance real
del punto 3. Los demás puntos de ADR-023 (interfaz común, reutilización sin otro state/ledger,
entrega ≠ gate, sin fallback genérico, configuración portable, frontera) **se conservan**.

**1. La señal durable la produce el runtime, no el fixture (corrige el punto 5).** El punto 5 decía
«se espera sobre una señal durable, no sobre el `rc`», pero no fijaba cuál. La señal durable real de
OpenCode es su **base de sesiones SQLite** (`session_v2` + `session_message`), abierta **en solo
lectura** (`mode=ro`) en la ruta que declara la configuración de ejecución (`sessions_db`, ruta
configurable, nunca hardcodeada). El JSON `{status, session, final_text}` de 005-009 **no existe** en
el runtime real: lo escribía solo el binario falso del fixture (por eso el contrato se validaba
**contra sí mismo**). Un store ausente/ilegible/no-SQLite/con esquema incompleto **falla cerrado**
con diagnóstico que nombra el esquema/columna (`blocked`), sin entrega ni recibo; el
`UnicodeDecodeError` (leer la base como JSON) deja de ser una excepción no capturada. Como el esquema
**no es contrato público**, se valida por columnas requeridas, no por marcador de versión; no se usa
`immutable=1` con el servicio vivo; **nunca** se escribe el store.

**2. Correlación inequívoca por `--session <id>` (concreta el punto 5).** El adaptador **elige** el
id de sesión y lo pasa en `--session <id>`; la fila durable lleva **ese** `id`, `agent` y
`idle_outcome`, así que la correlación es material e inequívoca. Se toma el texto final del **último**
mensaje `session_message` de tipo `assistant` (`data.content[].text`). La terminación se clasifica
desde `idle_outcome` —`succeeded→completed` (con texto; si falta, `blocked`), `failed→blocked`,
`interrupted→cancelled`, y sin idle dentro de la espera acotada → `timeout`—, **nunca** desde el `rc`
del cliente. La espera es acotada por `wait.timeout_seconds`; su ausencia **falla cerrado antes del
despacho** (no hay invocación desacotada).

**3. `mode: subagent` es entrada no interactiva en la versión instalada (corrige el punto 4).** El
punto 4 hacía del `mode: all` la barrera. La evidencia del runtime instalado muestra que
`opencode run --agent <mode:subagent>` **sí** es una entrada no interactiva (la observación «cuelga»
provenía del binario **legacy** en PATH). Por eso el adaptador **deja de exigir `mode: all`**: exige
que el derivado `cdad-<rol>` esté publicado y **verifica la identidad desde la fila durable**
(`session_v2.agent == "cdad-<rol>"`), **sin fallback** a un agente no-Cdad (INV-6 se conserva). La
brecha «entry no soportada → falla cerrado» se mantiene, pero su **hecho material** pasa de `mode` a
la identidad durable. `scripts/cdad-generate.py`, la fuente canónica de agentes y el `mode` de los
roles **no** cambian.

**4. OpenCode toma el directorio del proyecto de `PWD`, no del cwd (confirma el punto 3).** El punto
3 exigía que el proyecto fuese explícito e independiente del directorio del coordinador. La
aceptación real demostró que `opencode run` resuelve el directorio del proyecto desde la **variable
de entorno `PWD`**, no desde el `cwd` del proceso: con `PWD` heredado del coordinador, el rol corría
en el proyecto equivocado. El adaptador fija `PWD` = raíz del proyecto explícito (`--project-root`)
en la invocación. El proyecto explícito, por lo tanto, **se hace cumplir en ese nivel** (transporte +
`PWD`), no solo en el encargo.

**Consecuencias.** Los puntos 4 y 5 quedan **superados en su afirmación específica** (el `mode` como
barrera; la señal sin identificar); el resto de ADR-023 sigue vigente. Positivo: la barrera es un
**hecho material** (la fila durable) y la señal es una superficie que el runtime realmente produce.
Costo/riesgo: el **esquema del store no es contrato público** (riesgo del epic) → mitigado con fallo
cerrado por columnas y con la prueba de integración opcional por versión; la corrida real usa el
**store y la credencial del runtime** (la credencial vive en la base, un store vacío no autentica),
de modo que **lo aislado es CDAD** (instalación + proyecto), no el runtime.

**Alternativas consideradas.** (a) salida `--format json` del cliente como única señal → rechazada
(es superficie del cliente y puede volver antes de que el rol termine); (b) `session export` →
rechazada (requiere servidor; superficie de cliente); (c) señal escrita por el worker → rechazada
(señal inventada; si el worker falla, no hay señal). (d) Publicar variantes `mode: all` → rechazada
(duplica agentes y toca la generación).

**Referencias.** Contrato: `docs/specs/005-010-real-opencode-delegation/spec.md` (PD-1..PD-10,
INV-1..INV-10; D1–D10) y `plan.md` (T1–T4). Insumo: `.../discovery.md`. Aceptación real:
`.../evidence/pd10-acceptance.md`. Revisión: `.../review.md` (1 bloqueante R1 corregido; R5–R7 a
deuda). Referencias operativas: `skills/cdad-cycle/references/{cli-delegation,opencode-delegation}.md`.
