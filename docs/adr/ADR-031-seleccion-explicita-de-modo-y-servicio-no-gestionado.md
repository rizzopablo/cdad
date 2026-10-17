# ADR-031: El modo de ejecución de la delegación externa es explícito y el servicio de fondo no se gestiona; con el servicio corriendo, un fallo termina en `blocked`

- **Status**: Accepted
- **Date**: 2026-10-17
- **Deciders**: Pablo (dueño: aprobó el **cambio de alcance** del modo `service` el 2026-10-16 y la dirección
  del epic; delegó la HITL del epic-006 a Claude) + orquestador Claude (HITL delegada: ratificó **D-11 (A)** y
  **D-9**, y condujo los recorridos reales y la suite de cierre) + architect (spec v2 y plan v2)
- **Confidence**: Media
- **Aprobación**: aprobado por Pablo el 2026-10-17 (Memory Bank de 006-001), a partir del borrador del scribe (patrón
  Scribe; ADR-003/ADR-011). **Evidencia disponible:** contrato **spec v2** `dac418b9…` y **plan v2**
  `2726744…` aprobados juntos el 2026-10-16; RED→GREEN por unidad (T1 `91f7e98` → `4bc8934`+`a96c2d8`; T1b
  `7ccedb4` → `b949849`; T2 `8447443` → `ddba831`; T3 `5e5828a` → `d0a7963`); **review formal 3 bloqueantes /
  5 opcionales / 3 abstenciones** con los tres bloqueantes **corregidos** (`17a7ca1` → `161c9ff`) y **re-review
  5 de 5 cerrados, 0 bloqueantes, 1 opcional nuevo**; **suite de cierre 1 failed / 1079 passed / 5 skipped**
  (la falla, instancia de DT-9); recorridos reales de PD-6 (gate de versión real; fallback declarado
  `completed` 33,9 s; `require` `blocked` 1,1 s). **La confianza es Media** porque: (i) la **concurrencia real
  en las dos topologías elegidas no está demostrada** (PD-6 = BLOQUEO declarado: falta la credencial del dueño
  para `mode: server`, y un servicio en la versión del cliente) y **AC-7 está pendiente del dueño**; (ii) el
  gate de versión depende de un **archivo de registro no público** (DT-6); (iii) hay una **ventana de carrera
  declarada** que el runtime no permite cerrar (D-13); (iv) **B1 y B2 fueron huecos reales** —una banda
  aritmética de cota y un fail-open en el intento previo— que sólo aparecieron en la review, no en el GREEN;
  (v) quedan **O3–O5** y **O5-RF** a deuda. No es Baja porque los bloqueantes se cerraron con RED→GREEN
  verificado por una re-review independiente, la suite de cierre tiene una sola falla, instancia de DT-9 y verde en aislado y el fail-closed se observó en un
  recorrido real (2.0.22 vs 2.0.27 → `blocked`, sin fallback y sin tokens).

## Contexto y problema

Dos despachos reales del implementer a OpenCode terminaron `failed` por **contención en la base de sesiones
compartida** (`LockTimeoutError` / `database is locked`, ≈89 s y ≈487 s). La investigación
(`docs/specs/006-001-opencode-concurrency-reliability/discovery.md`) mostró que el adaptador del repo elegía el
modo por la **mera presencia** de `server` en la config, **no** comprobaba la versión del servidor, **perdía la
correlación** en un `timeout`, mataba **sólo al hijo directo** y **no miraba intentos previos**; y que las
configs examinadas omitían `server`, así que **cada despacho abría un servidor privado más** sobre el mismo
store. En paralelo, el dueño fijó la dirección del ciclo (cambio de alcance aprobado el 2026-10-16): el runtime
está diseñado para que el cliente **sin flags** use el **servicio de fondo** que es dueño del store.

La pregunta de arquitectura: **¿cómo elige CDAD una topología de ejecución para una delegación, sin
convertirse en administrador de un servicio compartido y sin que un fallo lo empuje a un fallback que agrave la
contención que la feature existe para mitigar?**

## Opciones consideradas

### Opción A: modo explícito con `service` como camino normal, servicio no gestionado y fallo cerrado (ADOPTADA)

- Pros: la selección queda **explícita y verificable** (`server` | `service` | `standalone`, sin fallback
  silencioso); el camino normal **deja de agregar un escritor** por despacho; con el servicio corriendo
  cualquier incompatibilidad termina `blocked` en vez de abrir un `standalone` al lado; el fallback existe sólo
  donde es legítimo (`stopped`) y es **contable** en la procedencia.
- Contras: una invocación extra (`service status`) y dos resultados posibles en ese camino; CDAD depende de un
  detalle del runtime (el formato de una línea de `service status`) y, para el gate de versión, de un archivo
  **no público** (DT-6); la topología real con servicio **no se puede demostrar** en este ciclo (PD-6).

### Opción B: que el default de `mode` pase a `service`

- Contras: un cambio de topología hacia un servidor **compartido** es decisión del **consumidor**, no un
  default silencioso (la feature existe para que la elección sea explícita) y cambiaría el comportamiento de
  todas las configs que hoy no declaran nada. **Descartada** → **D-9** (costo declarado: hasta que el consumidor
  declare `mode: "service"`, sigue abriendo un servidor privado por despacho; acción de la recepción, AC-7).

### Opción C: gate de versión por `GET <url>/api/info` con la credencial del servicio

- Contras: exige **leer la contraseña** del servicio **y** usar la URL para el mismo hecho que la proyección
  local obtiene sin red ni secreto. **Descartada** (más exposición, mismo resultado).

### Opción D: modo servicio sin gate de versión (sólo liveness), observando la versión después en la fila durable

- Contras: el cliente resuelve el servicio con `mismatch = "ignore"` (hecho verificado), así que CDAD
  despacharía contra un servicio **incompatible**; contradice la precisión del dueño («versión distinta con el
  servicio corriendo → `blocked`»). **Descartada**; sólo sería admisible aceptando el conflicto de forma
  explícita y derivando el gate a `mode: server`.

### Opción E: que CDAD arranque, reinicie o recargue el servicio para alinear versiones

- Contras: reservado al **dueño/operador**; un ciclo de desarrollo no reconfigura ni reinicia servicios
  compartidos, y la recarga puede dejar el store con más escritores. **Descartada** → **INV-2**
  («nunca arrancar ni gestionar el servicio»).

### Opción F: fallback a `standalone` ante **cualquier** fallo del modo servicio

- Contras: con el servicio **corriendo** eso es exactamente el «escritor de más» que la feature busca evitar
  (el store ya tiene N≥3 escritores de larga vida). **Descartada** → **INV-10**: con el servicio vivo, todo
  fallo termina `blocked`.

### Opción G: recuperación fail-open en el chequeo del intento previo (para no bloquear de más)

- Contras: es la conducta que la review encontró (B2) y que **reconstruye el problema**: con el worker previo
  vivo sosteniendo el lock, el chequeo no puede afirmar el estado y despacharía un **segundo worker del mismo
  paquete**. **Descartada** → el chequeo es **innegociable**, con la única distinción declarada del store
  **inexistente** (§2.7).

## Decision

1. **Selección explícita.** `mode` ∈ {`server`, `service`, `standalone`} con validación **antes** del despacho
   (`blocked` con diagnóstico que nombra la clave). Con `mode` **sin declarar** rige la **compatibilidad v1**
   (D-9). Sin fallback silencioso: la **única** transición admisible es el fallback declarado y contable
   `service` → `standalone` cuando `service status` informa que el servicio **no corre**.
2. **Preflight de servicio de solo lectura.** `service status` se invoca **exactamente una vez** (nunca
   `serve`, nunca `service start|stop|restart|get|set|unset`, nunca `reload`), dentro de la cota y del
   presupuesto restante, con **interpretación cerrada**: URL `http(s)` con host y sin userinfo → corre;
   literal `stopped` → no corre; cualquier otra respuesta (rc≠0, vacío, varias líneas, no reconocible,
   timeout) → **`blocked`** («no se puede afirmar que el servicio no corre»), **nunca** standalone. La URL que
   imprime **no se usa, no se guarda y no entra en ninguna salida**.
3. **Gate de compatibilidad por proyección de una sola clave (D-11, alternativa A).** Con el servicio
   corriendo, la versión del servicio se obtiene **proyectando únicamente** `version` del registro del
   servicio: sin red, sin contraseña, sin URL, sin abrir conexiones. Igual a la del cliente → despacho **sin
   flags**; distinta o **no verificable** → `blocked` nombrando las dos versiones (o «no verificable») y la
   acción siguiente, **nunca** standalone.
4. **La variante estricta es una clave propia.** `service.require` (booleano, default `false`): con `true`, el
   servicio que no corre termina `blocked`; sólo tiene efecto en modo servicio y se registra como no aplicable
   en los demás (D-10).
5. **Procedencia por intento sin tocar el esquema I8.** El adaptador registra su intento en **toda** terminación
   posterior a la carga de `REQUEST.json` y agrega, **al final** del texto libre de `provenance.runtime`, los
   pares `mode_requested=`, `mode_effective=`, `client_version=`, `server_version=`, `dispatch_flags=`,
   `service_status=` y `fallback=`. Lo no observado es `unknown`, nunca `0` ni vacío (INV-9). El fallback queda
   así **auditable y contable** por intento.
6. **CDAD no gestiona el servicio ni servidores (INV-2 reescrita).** Ninguna argv del binario lleva `serve`,
   `service <start|stop|restart|get|set|unset>` ni `reload`; el despacho **sin flags** ocurre **sólo** después
   de comprobar que el servicio corre y es compatible; la terminación ordenada alcanza **sólo** al grupo propio
   del cliente del adaptador.
7. **Un servicio vivo no admite otro escritor por esta vía (INV-10 nueva).** Ningún camino de selección,
   fallback o recuperación abre un `standalone` mientras el servicio corre, ni re-despacha solo, ni arranca el
   servicio o abre otro servidor; las relecturas ante lock son `mode=ro`, acotadas, con backoff y **sin**
   presión de escritura.
8. **El chequeo del intento previo es innegociable.** Un registro previo del mismo paquete con `session` no
   nulo cuya fila **no puede afirmarse** (store ocupado o ilegible) → `blocked` **antes de cualquier
   invocación**; la fila previa **idle** o **ausente** no bloquea, y un store **inexistente** es un hecho
   determinante distinto (§2.7). Sin reintentos automáticos.

## Reasons

1. **El camino normal deja de agregar escritores.** El runtime está diseñado para que el cliente sin flags use
   el servicio de fondo: adoptarlo **configurado** (y no por default silencioso) ataca la causa medida —un
   servidor privado por despacho sobre el mismo store— sin serializar el desarrollo ni restringir el contexto
   de los agentes.
2. **El invariante manda sobre la conveniencia.** Con el servicio corriendo, la respuesta correcta a una
   incompatibilidad es **`blocked` con acción siguiente**, no un standalone que agrave la contención: la
   recuperación **no reconstruye el problema** (es la lectura textual de la precisión del dueño y el motivo de
   INV-10).
3. **El gate de versión se hace sin exponer el secreto.** La proyección de **una sola clave** obtiene el hecho
   (versión) sin red, sin contraseña y sin URL; el acoplamiento al archivo queda declarado como deuda (DT-6) en
   vez de convertirse en una dependencia silenciosa.
4. **Hacer visible el fallback es parte del arreglo.** Registrar `mode_requested`/`mode_effective`/`fallback`/
   `service_status` en el texto libre del esquema cerrado permite **contar** cuántos despachos caen al fallback
   (DT-7) y correlacionar la ventana de carrera (D-13) sin cambiar la interfaz ni el esquema I8.
5. **Lo no observado no se afirma.** El mismo criterio que exige `blocked` cuando `service status` responde
   algo inesperado se aplica al intento previo: no se puede afirmar que el worker anterior terminó ⇒ no se
   despacha otro.

## Consequences

- **Positivas.** El modo solicitado, el efectivo, la causa del fallback y el modo de despacho quedan
  **verificables por intento**; el adaptador **nunca** gestiona el servicio ni abre un `standalone` junto a un
  servicio vivo; el `timeout` conserva la sesión elegida y bloquea el re-despacho; los secretos siguen fuera de
  argv, diagnóstico, registros y recibo (se descarta la salida de `service status` salvo el discriminante); la
  interfaz común, `OUTPUT_KEYS`, el vocabulario de terminación, el esquema I8 y la identidad durable quedan
  **intactos**.
- **Negativas / límites declarados.** (a) **La contención del store no se elimina**: siguen N≥3 escritores de
  larga vida y un `busy_timeout` fijo en el runtime; la feature **no** lo promete y un único éxito real es
  observación, no prueba. (b) **La ventana de carrera (D-13)** entre la comprobación y el despacho **no tiene
  forma soportada de impedirse** (no hay flag, variable de entorno ni setting): el cliente puede arrancar el
  servicio; se registra como riesgo residual con la mitigación de comprobar lo más tarde posible y de dejar
  `service_status`/`dispatch_flags` para correlacionar. (c) **DT-6:** el registro del servicio (ruta, nombre y
  esquema) es un **hecho observado, no contrato público**; si cambia, el gate falla cerrado y `blocked`.
  (d) **DT-7:** el fallback `service` → `standalone` puede volverse el camino habitual; se vigila con el
  contador y, si domina, se decide con el dueño (`service.require` o cambio del default). (e) **DT-3:** el
  intento previo sólo ve los registros del mismo paquete en el ledger. (f) **PD-6 = BLOQUEO declarado** (falta
  la credencial del dueño para la concurrencia en `mode: server`) y **AC-7 pendiente del dueño**; el único
  `completed` real fue en modo efectivo **standalone** y **no** prueba la topología con servicio. (g) A deuda:
  **O3** (anonimización en la spec aprobada y en la evidencia del epic), **O4** (celda indefinida de la matriz
  §2.2) y **O5**/**O5-RF** (legibilidad de `delegate()` y sharpness de un oráculo de cobertura).
- **No cambia.** La interfaz `cdad_delegate.py` y su `OUTPUT_KEYS`, el vocabulario de terminación, el esquema
  I8, la identidad durable, el transporte byte-idéntico por stdin, `PWD` = raíz del proyecto, `--auto` por
  config, los modos `server` y `standalone` de v1 y su matriz de oráculos, y el single-writer del state.

## Notas

- **Contrato normativo:** `docs/specs/006-001-opencode-concurrency-reliability/spec.md` (v2, sha256
  `dac418b9…`: §1, §2.1-§2.8, PD-1..PD-14, INV-1..INV-10, D-9..D-13, §8 deuda, §11 riesgos) y
  `plan.md` (v2, `2726744…`); fila 1 del plan del epic
  (`docs/epics/epic-006-opencode-concurrency/plan.md:22`) y el **cambio de alcance aprobado por el dueño**
  (`docs/epics/epic-006-opencode-concurrency/execution.md` §«Cambio de alcance…», §topología, §recorridos
  reales, §despliegue, §re-review y suite de cierre).
- **Código:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (+1333/−124 en el rango de la feature;
  +79/−14 del review-fix en `161c9ff`), `skills/cdad-cycle/references/cli-delegation.md` (+170/−19) y
  `skills/cdad-cycle/assets/opencode-exec-config.example.json` (nuevo).
- **Evidencia:** `discovery.md`; `t1-red/green.md`, `t1b-red/green.md`, `t2-red/green.md`,
  `t3-red/green.md`; `review.md` (3 bloqueantes / 5 opcionales / 3 abstenciones); `rf-red.md` / `rf-green.md`
  (RED `17a7ca1`, GREEN `161c9ff`); `rereview.md` (5 de 5 cerrados, 0 bloqueantes, 1 opcional nuevo).
- **Commits:** RED `91f7e98`, `7ccedb4`, `8447443`, `5e5828a`, `17a7ca1`; GREEN `4bc8934`+`a96c2d8`,
  `b949849`, `ddba831`, `d0a7963`, `161c9ff`. Último commit de producto de la feature: **`161c9ff`**.
- **Relación con otros ADR:** **precisa y amplía ADR-023** (adaptador por destino; la selección de ejecución
  pasa a ser explícita y el servicio de fondo no se gestiona) sin re-declarar la interfaz común;
  **anticipa la sustitución de ADR-007** que anuncia la feature 006-003 del mismo epic (instalador `basic`
  único, config de delegación y modelos por configuración). Reusa el patrón Scribe y la separación
  recepción/materialización/aprobación (ADR-003/ADR-014) y la política única de evidencia (ADR-020). No toca
  el guard de progreso (ADR-015).
- **Relación con las deudas del CLI detectadas:** `receive` finaliza el recibo con un `kind` que la tabla
  cerrada de `skills/cdad-cycle/assets/artifact-policy.json` (la que aplica `materialize`) rechaza —ocurrió
  **dos veces** en esta feature y el recibo es inmutable— y **no hay vía CLI para *fallar* un paquete
  despachado** (la disposición admite sólo `abandoned|superseded`); ambas son ajenas a esta decisión y quedan
  declaradas, sin ampliar el alcance.
- **Límites honestos de este registro:** la concurrencia en las topologías reales **no** está demostrada
  (PD-6 en BLOQUEO declarado; AC-7 pendiente del dueño); los números de la suite de cierre son **una** corrida
  y traen **1 falla** declarada como instancia de DT-9; el comportamiento nuevo **está desplegado con una
  versión anterior al review-fix** (redespliegue pendiente de la orden del dueño), así que el uso previsto en
  un proyecto real **no** está ejercido todavía.
