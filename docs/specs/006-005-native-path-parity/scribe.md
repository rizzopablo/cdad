I have read the contract, the acceptance evidence, the three reviews, the epic log and the current Memory Bank. Both hashes match the packet. I wrote nothing in the repo. Here are the three drafts.

---

# BLOQUE 1 — `docs/activeContext.md` (entrada nueva, arriba de todo, tras el `---`)

```markdown
## 2026-10-20 — Feature: 006-005-native-path-parity (epic 006)

**Cerrada el 2026-10-20 (ciclo técnico completo; el gate de suite completa lo corre quien cierra, PD-21).**
Cuarta unidad de `epic-006-opencode-concurrency`: la **paridad del camino nativo**. El orquestador deja de
reconstruir el protocolo a mano: hay **una entrada operativa** (`cdad_dispatch.py`) con **dos vías** (externa y
nativa), **un solo registro de intento por despacho**, **el kind de la parte entregada derivado del rol y la
subfase** (en las dos vías), **el temporal del test-writer escribible de verdad** y **camino mecánico a `failed`**.
**Contrato:** `spec.md` sha256 `3a824be3…` (PD-1..PD-26, INV-1..INV-16, D-1..D-17) + `plan.md` sha256
`21d6954e…`, aprobados el 2026-10-18 bajo la **HITL delegada del epic** (PD-19, runtime explícito, modelo y
credencial fuera de `runtimes.json`: decisiones del owner). **El epic NO se cierra.**

**Problema medido (seis brechas, contadas una a una).** La delegación nativa ejecutaba el encargo pero **no
trasladaba la preparación** que el adaptador externo sí hace: nadie registraba el intento (sin eso `receive`
rechaza), ningún encargo concedía un temporal que el test-writer pudiera **escribir**, y un intento que no
volvía **no tenía camino mecánico a `failed`** (la disposición lo dejaba en `pass`). A eso se sumaban, ya medidas
en uso real, la **entrada del orquestador sin configuración declarada** (con un exec-config local y un rodeo de
entorno) y el **agente por stack** que nunca se resolvía. Sexta brecha: el **orquestador que reconstruyó el
protocolo a mano**. **Todos los deliveries del reviewer de esta feature llegaron copiados a mano** porque el
kind fijo (`role-report`) no lo admitía: el rodeo ya medido, escalado a defecto real.

**Producto (U1a–U5, U7 + ocho amendments de la aceptación + dos rondas de review-fix).** Rango `43986e2..HEAD`:
**194 commits, 122 archivos, +30663/−654**; de ellos **24 archivos de producto, +2769/−435** y `tests/` suma
**32 archivos, +16451/−209**. **Último commit de producto: `88491b2`.**

- **U1a** — `skills/cdad-cycle/scripts/cdad_dispatch.py` (**nuevo**, 1216 líneas): la capa de configuración;
  `--runtime` **obligatorio en todos los verbos** (la entrada no resuelve runtime de ningún documento), la
  sección por runtime en `runtimes.json` (**fuente única**), el **barrido de `--exec-config` por token exacto,
  previo al parseo del verbo** (error de uso con la correspondencia clave por clave) y el **paso acotado de
  migración** (`migrate`, escribe la sección **sólo si no existe**; `--dry-run` no escribe); plantilla de
  `runtimes.json` en `install.sh` (**sólo si no existe**, fuera del manifiesto). RED `5dbc854` → GREEN `4052939`.
- **U1b** — la entrada única con los cuatro verbos (`dispatch` por defecto, `record`, `capabilities`, `migrate`);
  `record` = **cuerpo único** de observación + registro + escenificación; la **interfaz común deja de registrar**
  y **relaya** el `attempt` del módulo (un registro por despacho). RED `27b85a4` → GREEN `3af53f1` (con dos
  testfix declarados: `8bbbdd4`, `b28be34`).
- **U1c** — el **agente viaja en el paquete**: `prepare` resuelve rol+`stack` y escribe `agent` en
  `REQUEST.json`; el conjunto cerrado del request lo admite como propiedad opcional; **el render no cambia**
  (`PACKET.md` byte-idéntico). RED `eab7e2f` → GREEN `e958a0c` (testfix `12e710a`).
- **U2** — el módulo de runtime: **credencial inyectada** en el entorno del cliente (sólo `mode: server`, nunca en
  `argv`/logs/registro), **agente del paquete**, **kind derivado de rol+subfase** (deja de ser la constante
  fija), `--capabilities` y `--observe` (una lectura `mode=ro`, acotada, sin polling), **correlación por la
  evidencia de su vía** y **fallo cerrado** ante un módulo sin la superficie nueva. RED `9a260c4` → GREEN `eb677a9`.
- **U3** — el temporal: clase `temporary` validada contra la política, `git check-ignore` en `prepare` y
  **permiso de edición del agente derivado** para las raíces declaradas, emitido **antes** de las barreras
  (con las dos colisiones probadas: ruta privada y directorio de derivados). RED `0b38f07` → GREEN `a7f1bea`.
- **U5** — **camino mecánico a `failed`**: la disposición con las condiciones aprobadas por el owner, idempotente,
  con `validate-state` VALID y el siguiente `prepare` desbloqueado. RED `43ee3a0` → GREEN `0a260ab`.
- **U7** — la **fila del scribe** de la tabla cerrada admite `role-report`: el informe del rol se materializa
  **dentro de `docs/specs/<feature>/`** y el **Memory Bank queda fuera de su alcance** (se rechaza nombrando la
  raíz permitida). RED `ba95af5` → GREEN `a2139c5`.
- **U4** — el **mandato con una sola entrada**: intake por el `entry`/`next` que el CLI ya calcula, secciones
  `delegation`, **borde de adopción** de la migración y referencia de re-entry por estado de llegada; agentes
  regenerados con `make agents` (nunca a mano). RED `3d23ad6` → GREEN `014bf2d` (testfix de oráculos `b76aa5d`).

**Aceptación real (U6, PD-22) — proyecto descartable, layout anidado, coordinador fuera de la raíz.** Los cinco
escenarios y la sonda **cumplen**: **E5** (migrar + `capabilities`; repetir la migración da rc≠0 sin pisar) ·
**E3** (externa con **sólo paquete y `--runtime`**: un registro I8 —el del módulo— con `model_reported` del
store, parte con kind derivado, `materialize` rc=0 con bytes idénticos; el informe del scribe como `role-report`
dentro de la carpeta de la spec y **rechazado** hacia el Memory Bank) · **E2** (el auxiliar **escrito con la
herramienta del rol** en las dos vías tras U6-7: la externa deniega `docs/` y escribe el temporal y `tests/`; la
nativa, desde la raíz, escribe el auxiliar y su test, el test pasa y el commit toca sólo `tests/`) · **E1**
(nativa verificada por (parent, moment) desde la carpeta contenedora y por (parent, moment, project) desde la
raíz; el registro es el del hijo real) · **E4** (intento que no vuelve) · **V-11** (`stack: odoo` de punta a
punta: `REQUEST.json.agent` = `cdad-test-writer-odoo`, `session_v2.agent` igual, un registro final, entrega
recibida). **`scope_validation` queda `unknown` en las dos vías** (U6-2, deuda): el recibo no puede probar la
escritura porque lo ignorado no aparece en el manifiesto.

**Enmiendas del recorrido (U6-1..U6-8), cada una con su RED/GREEN.** **U6-1**: `capabilities` no pasaba la
sección al módulo ⇒ el paso «migrar → verificar» no verificaba nada (`ed64092`→`caaab97`). **U6-3**: la llave
proyecto rechazaba al coordinador iniciado en la carpeta contenedora ⇒ pasa a **tres valores** (dentro ⇒ coincide;
**ancestro ⇒ no evaluable**; ajeno ⇒ contradicción) (`f6054ce`→`e7c39a5`). **U6-4**: el momento nunca era
evaluable contra el store real y la selección del hijo era arbitraria ⇒ unidades y **candidatos** explícitos
(`8fe0d8c`→`b06bd2f`). **U6-5 (decisión con dos reviews)**: el registro externo se escribía **al terminar** ⇒
una muerte del coordinador dejaba un callejón sin salida (`reconcile` decía que repetir era seguro y la
disposición se negaba) ⇒ **registro write-ahead** (`a0d96b5`+testfix `569682d`→`471db74`). **U6-6**:
`model_reported` con forma distinta entre vías ⇒ **paridad** (`12c29a7`→`ef88817`). **U6-7**: los agentes
generados llevaban la palanca `write: ask`, que la versión instalada **sí evalúa** ⇒ la externa escribía fuera
de alcance y la nativa no interactiva rechazaba todo ⇒ **palanca retirada del generador** (`8506674`→
`028cd79`); **U6-7b** además, los derivados **no heredan** la palanca de una copia instalada vieja
(`14c2b3c`+testfix `e58c0a8`→`58af287`). **U6-8**: el control comparaba la versión **escrita en la config**
contra el servidor ⇒ **versión por observación** (`c6e61aa`→`cca7e5d`).

**Review (etapa 4) — 3 bloqueantes / 2 opcionales**, y dos rondas de review-fix con sus re-reviews. **B-1**: los
allows de implementación **reabrían tests convencionales** dentro de esas raíces ⇒ **gana la barrera del rol**
(`3ca6597`, con la enmienda A-1 declarada en dos tests de la familia 004-002/005-008). **B-2**: `--session`
evitaba la normalización del momento y convertía contradicciones observables en `unknown` ⇒ **frontera común de
normalización** (momento y modelo). **B-3**: las instrucciones pedían un FINAL TEXT que la entrada no devuelve ⇒
**la externa consume el recibo de `delivery_ref`; la nativa escenifica con `record` y luego `receive`**. **Re-review**:
B-1 cerrado, B-2 cerrado **con un bloqueante nuevo (B-4)**: se había eliminado una llave no declarada y se acreditaba
identidad donde el contrato exige `unknown` ⇒ la llave expuesta sin declaración vuelve a ser `unknown`
(`88491b2`). **Re-review focal 2**: **sin bloqueantes nuevos; B-3 y B-4 cerrados**; único opcional (O-3, el focal
externo compara longitud y no identidad de bytes) queda como nit. Dictamen: *apta para cierre respecto de esa
re-review focal; quedan los gates propios del cierre*.

**Gates.** `make validate` en el GREEN de cierre: **168 PASS / 1 FAIL = F011** (deriva ambiental de la copia
instalada, clase **DT-8** preexistente; los validadores del repo pasan 168/169). **Suite completa: no ejecutada**
—PD-21: la corre **una vez quien cierra**. Es el gate que falta para el cierre formal.

**Despliegue.** Por orden del owner se desplegó en el entorno de instalación el fix **U6-7 + U6-7b + U6-8**
(`b69bbac`, Verify PASS, scripts instalados iguales al repo; los agentes instalados ya no llevan la clave
`write`). **Los review-fix (B-1..B-4) son posteriores a ese despliegue** ⇒ la copia instalada **no** los contiene:
el **redespliegue** queda pendiente y es operación de entorno, que **espera orden del owner**. Los derivados de
cada proyecto se rehacen desde la copia instalada en su próximo `prepare`.

**Decisiones relevantes.**
**D-1** una sola entrada con dos vías y **regla de transporte declarada**: mismo runtime que el orquestador ⇒
herramienta nativa + `record`; otro ⇒ despacho externo. **D-2** la integración se **extiende** al módulo por
destino que ya existe (no hay un módulo nuevo por runtime). **D-3** la correlación la produce **cada transporte**:
la externa por el **id de sesión que el módulo elige** (sin padre comparable, sin igualdad `directory == raíz`);
la nativa por **padre + agente + momento + proyecto por pertenencia**, con **umbral de discriminación** (la
acreditación positiva exige **al menos una llave discriminante**: padre, momento o proyecto; «agente» sólo no
acredita, porque dos despachos nativos concurrentes del mismo rol lo comparten) y **tres resultados con
consecuencia propia**: *verificada*, *no verificable* (`unknown`; entrega sólo con la garantía menor PD-6) y
*verificada e incorrecta* (**rechazo** que nombra la llave; nunca `unknown`, nunca entrega aceptada). **D-4** el
`kind` de la parte lo fijan rol y subfase en las dos vías (y la fila del scribe admite `role-report` con el
Memory Bank fuera de alcance). **D-5** el temporal es una clase de scope **escribible**, y su legitimidad se
prueba con una **escritura real** con la herramienta del rol, no con `scope_validation`. **D-6** la clave del
`agent` se completa en `REQUEST.json` y **no** entra al render. **D-7** el write-ahead: **provisional antes de
lanzar el cliente**, fail-closed, y **completado una sola vez** en toda terminación. **D-8** las versiones se
comparan **por observación** (cliente contra servidor), nunca contra un número escrito en la config;
`binary_version` queda **informativo** y `migrate` deja de escribirlo. **D-9** el runtime es **explícito** en
cada despacho. **D-10** el modelo y la credencial **no viven** en `runtimes.json` (el modelo en
`delegation.json`, la credencial donde ADR-033 punto 6 la puso). **D-11** el `--exec-config` retirado se
rechaza por **token exacto, antes del parseo del verbo**, en todos los verbos.

**Deuda detectada (abierta).**
- **U6-2** (preexistente, transversal): **ningún productor de `observed_changes`** ⇒ el recibo sale siempre con
  `scope_validation: unknown` y el control mecánico «el rol con escritura no salió de su alcance» **nunca corre**;
  quedan los mapas de permiso del agente y la revisión del diff.
- **O-2**: con el coordinador **fuera de la raíz**, el runtime aplica la **copia global** de los agentes, cuyos
  mapas son relativos a otra carpeta ⇒ el camino nativo no puede escribir. **Límite declarado**, con su
  disparador (la vía nativa recomendada inicia el coordinador en la raíz; la escritura temporal queda cubierta
  por la vía externa, que fija `PWD` a la raíz). No invalida U3.
- **D-U65-4**: **sin write-ahead nativo** (por construcción: la sesión la crea la herramienta del runtime); la
  salida es **procedimental** (el siguiente coordinador ejecuta `record` con `--parent`/`--since`).
- **D-U65-5**: recuperar del store la salida del huérfano (que llegó a commitear) como **entrega tardía**.
- **O-2 de la review** (deuda aceptada): la derivación del `kind` tiene **dos implementaciones** (núcleo y
  módulo) y el módulo conserva un *fallback* del scribe ya innecesario.
- **O-3 de la re-review focal 2** (nit): el focal externo compara longitud, no identidad de bytes.
- **Transporte del paquete en la vía nativa**: la línea JSON de cabecera de `PACKET.md` mide **más de 2000
  caracteres** (2378 en el recorrido) y la herramienta de lectura del runtime **la trunca**; un orquestador que
  copie el paquete leyéndolo puede no lograr bytes idénticos. La ruta documentada (`cdad_packet.py render` con su
  stdout pasado sin cambios) despacha bien. Queda como observación para la guía del orquestador nativo.
- **Pendientes de cierre:** **suite completa** (PD-21, la corre quien cierra) y **redespliegue** de los
  review-fix (orden del owner). Heredadas y sin cambio: **DT-8** (F011 por deriva de la copia instalada) y el
  **flake conocido del margen de la espera bajo carga** (clase DT-9), reproducido verde en aislamiento.

**Lecciones de proceso.**
(1) **Una sonda que registra sólo nombres inventa las unidades**: V-7 registró nombres de columna y no tipos, los
fixtures supusieron segundos `REAL` y el momento **nunca fue evaluable contra el store real** — la degradación
salió con las mismas palabras que otro caso. Una sonda de store registra **tipo y unidad**.
(2) **La clasificación no es autorización**: un `allow` de raíces de implementación reabre tests convencionales
dentro de ellas (B-1); la **barrera del rol prevalece** sobre la clasificación de la política.
(3) **Un registro que sólo existe al final deja un callejón sin salida**: la vía externa lo escribía al
terminar, y una muerte del coordinador producía un paquete que parecía no haber sido despachado — con
`reconcile` autorizando repetir. El **write-ahead** con **compleción única** cierra el hueco sin abrir un
segundo escritor.
(4) **Las instrucciones son parte del contrato**: el texto generado pedía un FINAL TEXT que la entrada no
devuelve (B-3); el procedimiento referenciado tenía que distinguir **por estado de llegada** (texto pendiente /
descriptor ya escenificado / recibo ya durable) y **ambos caminos comprobarse** de punta a punta.
(5) **«El mismo escenario en las dos vías» no puede ser el mismo paquete**: el recibo durable admite **una sola
finalización por (ejecución, paquete)**; el recorrido se hace sobre **dos paquetes de la misma ejecución**.
(6) **Una credencial no viaja por `argv` ni por el entorno del orquestador**: la resuelve y la inyecta el módulo
en el entorno del proceso cliente; el rodeo de entorno que hacía el despachador deja de ser necesario.

**Estado del epic.** `epic-006-opencode-concurrency` sigue **abierto** (`features-loop`): **006-001, 006-002,
006-003 y 006-005 `done`, 4/6**. Quedan **006-006-spec-plan-review** (revisión independiente de spec y plan
antes del RED, enmienda 006) y **006-004-active-decisions-table** (enmienda 003, que también vehiculiza el
principio de general antes que específico, enmienda 005 ⇒ **ADR-034**), en el **orden que fijó el owner**:
**006-005 → 006-006 → 006-004**. **Siguiente:** `006-006-spec-plan-review`.
```

---

# BLOQUE 2 — `docs/progress.md` (fila nueva, primera bajo `## Done`)

```markdown
- **006-005-native-path-parity** (2026-10-20, epic 006) — cuarta feature de
  `epic-006-opencode-concurrency`: la **paridad del camino nativo**. El orquestador deja de reconstruir el
  protocolo a mano: una **entrada operativa** (`cdad_dispatch.py`, verbos `dispatch`/`record`/`capabilities`/
  `migrate`) con **vía externa y vía nativa**, **un solo registro I8 por despacho**, **kind de la parte derivado
  de rol+subfase en las dos vías**, **temporal del test-writer escribible de verdad** y **camino mecánico a
  `failed`**. **Contrato:** `spec.md` sha256 `3a824be3…` (PD-1..PD-26, INV-1..INV-16, D-1..D-17) + `plan.md`
  sha256 `21d6954e…`, aprobados el 2026-10-18 bajo la **HITL delegada del epic** (PD-19, runtime explícito y
  modelo/credencial fuera de `runtimes.json`: decisiones del owner). **Producto (24 archivos, +2769/−435;
  `tests/` 32 archivos, +16451/−209; rango `43986e2..HEAD`, 194 commits, 122 archivos +30663/−654; último commit
  de producto `88491b2`):** U1a config por runtime + barrido de `--exec-config` + paso de migración acotado +
  plantilla de `runtimes.json` (RED `5dbc854`→GREEN `4052939`); U1b entrada única y **registro único** (la
  interfaz deja de registrar y relaya) (RED `27b85a4`+2 testfix→`3af53f1`); U1c **el agente viaja en el paquete**
  (rol+`stack` en `REQUEST.json`, render byte-idéntico) (RED `eab7e2f`+testfix→`e958a0c`); U2 módulo de runtime
  (credencial inyectada al cliente, kind derivado, `--capabilities`/`--observe`, correlación por la evidencia de
  su vía, fallo cerrado) (RED `9a260c4`→`eb677a9`); U3 temporal **autorizado y escribible** por el agente
  derivado, con la precedencia de las barreras probada (RED `0b38f07`→`a7f1bea`); U5 la disposición deja el
  paquete activo en `failed`, idempotente (RED `43ee3a0`→`0a260ab`); U7 la **fila del scribe** admite
  `role-report` (materializado dentro de `docs/specs/<feature>/`, **Memory Bank rechazado** nombrando la raíz
  permitida) (RED `ba95af5`→`a2139c5`); U4 mandato con una sola entrada + borde de adopción + agentes
  regenerados (RED `3d23ad6`+testfix→`014bf2d`). **Aceptación real (U6, proyecto descartable, layout anidado,
  coordinador fuera de la raíz):** E1..E5 **cumplen** — la externa con sólo paquete y `--runtime` deja **un**
  registro (el del módulo) con `model_reported` del store y `materialize` rc=0 con bytes idénticos; el informe
  del scribe se materializa en la carpeta de la spec y se **rechaza** hacia el Memory Bank; la nativa verifica
  por (parent, moment) y por (parent, moment, project); el auxiliar se **escribe con la herramienta del rol** en
  las dos vías y su test pasa; E4 deja camino mecánico a `failed`; **V-11** `stack: odoo` de punta a punta
  (`cdad-test-writer-odoo` en el paquete y en el store) — con `scope_validation: unknown` en ambas vías
  (**U6-2**, deuda). **Enmiendas del recorrido:** U6-1 `capabilities` no pasaba la sección al módulo
  (`ed64092`→`caaab97`); U6-3 la llave proyecto con **ancestro no evaluable** (`f6054ce`→`e7c39a5`); U6-4
  momento en ms y **selección del candidato** (`8fe0d8c`→`b06bd2f`); **U6-5 registro write-ahead** del intento
  externo con **compleción única** (decisión con dos reviews; `a0d96b5`+testfix→`471db74`); U6-6 paridad de
  `model_reported` (`12c29a7`→`ef88817`); **U6-7 retirada de la palanca `write: ask`** del generador y **U6-7b**
  los derivados no la heredan (`8506674`→`028cd79`, `14c2b3c`+testfix→`58af287`); **U6-8 versión por observación,
  no por config** (`c6e61aa`→`cca7e5d`). **Review formal: 3 bloqueantes / 2 opcionales** (B-1 la barrera del rol
  prevalece sobre la clasificación; B-2 normalización común del momento y el modelo; B-3 las instrucciones
  pedían un FINAL TEXT que la entrada no devuelve) y **dos rondas de review-fix** (RED `056c0f1`→GREEN
  `3ca6597`, testfix A-1 `e99bc5a`; RED `5306a28`→GREEN `88491b2`) con **re-review** (B-1 y B-2 cerrados, B-3
  parcial, **B-4** nuevo: la llave expuesta sin声明 vuelve a `unknown`) y **re-review focal 2 sin bloqueantes**
  (B-3 y B-4 cerrados; O-3 nit). **Gates:** `make validate` **168 PASS / 1 FAIL = F011** (deriva ambiental de la
  copia instalada, **DT-8** preexistente); **suite completa NO ejecutada** (PD-21: la corre quien cierra) ⇒
  **gate de cierre pendiente**. **Desplegado en el entorno de instalación** por orden del owner el fix U6-7 +
  U6-7b + U6-8 (`b69bbac`, Verify PASS; los agentes instalados ya no llevan la clave `write`); **los review-fix
  son posteriores ⇒ redespliegue pendiente** (espera orden del owner). **Deuda:** **U6-2** (ningún productor de
  `observed_changes` ⇒ el control mecánico de alcance nunca corre), **O-2** (coordinador fuera de la raíz ⇒ copia
  global de los agentes ⇒ el camino nativo no escribe; límite declarado), **D-U65-4** (sin write-ahead nativo;
  salida procedimental), **D-U65-5** (recuperar del store la salida del huérfano como entrega tardía),
  **O-2 de la review** (dos implementaciones de la derivación del kind + fallback del scribe ya innecesario),
  **O-3 de la re-review 2** (nit: longitud y no identidad de bytes), y el **límite de transporte del paquete
  nativo** (la cabecera JSON de `PACKET.md` supera 2000 caracteres y la herramienta de lectura del runtime la
  trunca). **El epic NO se cierra: 4/6** — quedan **006-006-spec-plan-review** y **006-004-active-decisions-table**,
  en el orden del owner (**006-005 → 006-006 → 006-004**). **Siguiente:** `006-006-spec-plan-review`.
```

*(Corrección de una errata de tipeo en la fila anterior: «sin声明» → «sin声明» debe leerse **«sin declaración»**.)*

---

# BLOQUE 3 — `docs/systemPatterns.md` (bloque nuevo, dentro de «Patrones del framework», al final del grupo de epic 006 — después de «Modelos por configuración, archivos del usuario fuera del ownership…» y antes de «Medición de contexto…»)

```markdown
### Correlación por transporte, registro write-ahead y barreras que no dependen de la clasificación (epic 006, 2026-10-20)

- **La correlación se demuestra con la evidencia que produce cada transporte, y hay tres resultados, no dos.**
  **La externa**: el módulo **elige** el id de sesión y correlaciona por él («el adaptador, no el cliente, es el
  dueño del id de correlación»); **no hay padre que comparar** y **no** se exige la igualdad `directory == raíz`
  (esa igualdad no prueba el proyecto y rechazaría el recorrido legítimo: coordinador iniciado desde otra
  carpeta, layout anidado). La identidad del rol se corrobora contra la fila durable. **La nativa**: las llaves
  son las **columnas observables** del store de la versión declarada —padre, agente, momento y proyecto **por
  pertenencia** (dentro de la raíz ⇒ coincide; **ancestro ⇒ no evaluable**, no prueba ni contradice; ajeno ⇒
  contradicción)—. **Umbral de discriminación:** la acreditación positiva exige **al menos una llave discriminante
  evaluada y coincidente** (padre, momento o proyecto); **«agente» por sí solo no acredita**, porque dos
  despachos nativos concurrentes del mismo rol comparten agente ⇒ con sólo esa llave el resultado es
  `unknown`. **Tres resultados con consecuencia propia:** *verificada* (se persiste la sesión observada) ·
  *no verificable* (`unknown`, **sin entrega por esa vía**, salvo la garantía menor PD-6: con resultado nativo
  byte-exacto la entrega se persiste con `session: null` y procedencia que declara la identidad no verificada) ·
  *verificada e incorrecta* (**rechazo** que nombra la llave; **nunca** `unknown`, **nunca** entrega aceptada).
  Una llave **expuesta pero no declarada** sigue siendo `unknown**: no se omite para acreditar. Una contradicción
  en cualquier llave evaluable —incluida «agente»— es rechazo. Nunca se compara contra un valor supuesto: sin
  `agent` en el paquete, esa llave es `unknown`, nunca `cdad-<rol>`.
- **El registro del intento se escribe antes de que el cliente pueda producir efectos, y se completa una sola
  vez.** El módulo externo escribe su registro I8 **provisional** (marca legible `write-ahead:` al frente de
  `provenance.session`, `model_reported` en `null`) **antes de lanzar el cliente**: después de cargar el request,
  pasar el chequeo de intento previo y elegir el id de sesión. **Si ese registro falla, el cliente no se
  lanza** y la terminación es `blocked` con el diagnóstico (fail-closed). En **toda** terminación posterior el
  registro se **completa una vez**: se reemplazan la sesión, el modelo reportado y **todos** los pares de
  procedencia de terminación; la **identidad** (ejecución, paquete, intento, rol, subfase, runtime, inicio) **no
  cambia** (si difiere ⇒ rechazo); la compleción **sólo** vale sobre un registro con la marca y produce uno sin
  ella ⇒ una segunda compleción, o una compleción sobre un registro sin marca, es **rechazo**. La regla
  write-once del ledger no cambia: **un registro por despacho**. Secuencia de recuperación, sin autorizar
  repetir efectos: `reconcile` ⇒ `dispatched-unknown`; un re-despacho con la sesión viva ⇒ `blocked` sin
  invocar el cliente; `disposition` ⇒ `failed` con `validate-state` VALID; el siguiente `prepare` procede.
  **Límite declarado:** la vía nativa **no** tiene write-ahead (la sesión la crea la herramienta del runtime) ⇒
  la salida es **procedimental** (el siguiente coordinador ejecuta `record` con `--parent`/`--since`).
- **La barrera del rol prevalece sobre la clasificación de la política.** En el mapa `edit` del agente derivado,
  los `allow` de raíces de implementación se emiten **antes** de las prohibiciones de tests convencionales
  (semántica findLast: gana el `deny`), y el derivado aplica la **barrera del agente generado restringida por la
  política, nunca ampliada**: clasificar una ruta como «implementación» **no** autoriza a editarla cuando es un
  test. La clasificación sigue sirviendo para el alcance y el piso de escritura; **no** es autorización. La
  precedencia se **prueba**, no se declara: el caso que la resuelve es una raíz de implementación con un test
  convencional dentro, y su reemplazo de oráculo va declarado en el RED.
- **Las versiones se comparan por observación, no por lo que dice la configuración.** El control de versión
  compara **observado contra observado** (cliente contra servidor), nunca contra un número escrito en el
  archivo de config; una diferencia se **declara en el diagnóstico** y **no bloquea**. `binary_version` queda
  **opcional e informativo**, y el paso de migración deja de escribirlo. La **compatibilidad del store se
  verifica por capacidad** (si faltan las columnas que la correlación evalúa ⇒ fail-closed nombrándolas), y no
  por un número de versión guardado.
- **Una sonda de store registra tipo y unidad, no sólo nombres de columna.** El precedente medido: una sonda que
  registró los nombres de las columnas dejó que los fixtures **inventaran** la unidad del instante (segundos
  `REAL` donde el runtime guarda milisegundos epoch `INTEGER`), y el resultado fue que la llave **nunca** pudo
  evaluarse contra el store real — con la degradación emitida con las mismas palabras que otro caso, lo que
  escondió la causa. **Tipo y unidad son parte de la observación**; sin ellos, la comparación no se puede hacer y
  el fixture inventa la realidad.
- **Una palanca de permiso anulada por el runtime vacía el mapa de rutas.** Los agentes generados llevaban una
  palanca `write: ask` que la versión instalada **sí evaluaba**: por la precedencia de la última regla, todo
  pasaba a *ask* —la vía externa escribía **fuera de su alcance** y la nativa no interactiva rechazaba **todo**.
  El mapa de rutas sólo es una barrera si **ninguna** regla posterior lo anula; por eso la palanca se retiró del
  generador **y** los derivados dejan de heredarla de una copia instalada vieja (si no, una instalación anterior
  seguiría anulando el mapa derivado y la protección dependería del estado del entorno, no del repo).
- **Referencia operativa:** `skills/cdad-cycle/scripts/cdad_dispatch.py` (entrada, verbos, `record`),
  `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (credencial, agente, kind, `--capabilities`/`--observe`),
  `skills/cdad-cycle/scripts/cdad_delegate.py` (la interfaz que deja de registrar y relaya),
  `skills/cdad-cycle/scripts/cdad_packet.py` (agente en el request, scope `temporary`, permiso del derivado,
  disposición `failed`), `skills/cdad-cycle/scripts/cdad_result.py` (fila del scribe y tabla cerrada),
  `skills/cdad-cycle/references/cli-delegation.md` (configuración, borde de adopción) y `re-entry.md` (protocolo
  por estado de llegada); contrato normativo en
  `docs/specs/006-005-native-path-parity/spec.md` (PD-1..PD-26, INV-1..INV-16, D-1..D-17) y recorrido en
  `docs/specs/006-005-native-path-parity/u6-acceptance.md` y `u6-5-decision.md`.
- **ADR sugerido:** sí — la decisión de arquitectura de esta feature (una entrada con dos vías, correlación por
  transporte con umbral de discriminación y tres resultados, y registro write-ahead con compleción única) es
  candidata a **ADR** (MADR, con campo **Confidence: High**). **La numeración no se asigna aquí** (el
  `ADR-034` está reservado por el plan del epic para el principio de general antes que específico) y la
  **aprobación del ADR es del owner**, no del cierre de la feature.
```

**Y en el pie del archivo** (`docs/systemPatterns.md:733`), la línea de cierre:

```markdown
Última actualización: 2026-10-20 (006-005)
```

---

## Reporte de rol (evidencia)

**Intake path:** paquete canónico validado (`006-005-native-path-parity-scribe-memory-001`), rol `scribe`,
subetapa `memory`. No se cargaron `cdad-cycle` ni `cdad-spec-and-test`. `write_scope` declarado: `[]` ⇒ **no se escribió nada en el repo**; los tres bloques van como texto final para que el orquestador los materialice.

**Hashes verificados (coinciden con el paquete):**
```
3a824be31e45cd8e6122b7d6f23d3f4d3e6af847ab73f7babef8aa90ce20df01  docs/specs/006-005-native-path-parity/spec.md
21d6954e200d303af46f190112b1c240d955203989aa436468a77a06dc8ede00  docs/specs/006-005-native-path-parity/plan.md
```

**Comandos ejecutados (lectura) y salidas:**
```
$ git log --oneline 43986e2..HEAD | wc -l
194
$ git diff 43986e2..HEAD --stat | tail -1
 122 files changed, 30663 insertions(+), 654 deletions(-)
$ git diff 43986e2..HEAD --name-only -- install.sh agents skills scripts sources build | wc -l
24
$ git diff 43986e2..HEAD --stat -- install.sh agents skills scripts sources build | tail -1
 24 files changed, 2769 insertions(+), 435 deletions(-)
$ git diff 43986e2..HEAD --numstat -- tests | awk '{a+=$1; d+=$2; n++} END {print n" files, +"a"/-"d}'
32 files, +16451/-209
$ git log --oneline --reverse 43986e2..HEAD | grep -E "feat: 006-005|fix: 006-005"
4052939 feat: 006-005 U1a GREEN … 3af53f1 U1b … e958a0c U1c … eb677a9 U2 … a7f1bea U3 … 0a260ab U5 … a2139c5 U7 … 014bf2d U4 … caaab97 U6-1 … e7c39a5 U6-3 … b06bd2f U6-4 … 471db74 U6-5 … ef88817 U6-6 … 028cd79 U6-7 … 58af287 U6-7b … cca7e5d U6-8 … 3ca6597 review-fix … 88491b2 review-fix 2
$ grep -rn "suite de cierre\|suite completa" docs/epics/epic-006-opencode-concurrency/execution.md
(sin entrada para 006-005 ⇒ la suite de cierre NO se ha corrido)
$ git status --short
 M docs/.cdad-state.json      (del orquestador, no mío)
?? docs/planning/            (ajenos, no tocados)
?? findings/…                 (ajenos, no tocados)
$ git log --oneline -1
59f335f docs(state): 006-005 scribe preparado
```

**Fuentes leídas:** `spec.md`, `plan.md`, `u6-acceptance.md`, `u6-5-decision.md` (+ sus dos reviews), `review.md`, `rereview.md`, `rereview2.md`, los `u*-green.md`/`rf*-green.md` de las unidades, `docs/epics/epic-006-opencode-concurrency/execution.md` (§006-005), `docs/epics/.../plan.md` §11–§13, `docs/.cdad-state.json`, y los tres archivos del Memory Bank.

**Límites declarados de este borrador:**
- **La suite completa no se ha corrido** ⇒ los borradores **no** la afirman; el gate de cierre queda pendiente (PD-21: la corre quien cierra).
- El **redespliegue** de los review-fix en el entorno de instalación queda pendiente (espera orden del owner); el despliegue medido es `b69bbac` (U6-7/U6-7b/U6-8).
- El ADR queda **sugerido** (Confidence: High), sin número asignado y sin aprobación: la aprobación estratégica es del owner.

**Archivos modificados:** ninguno. **Commit creado:** ninguno (el orquestador materializa los borradores y ejecuta el git). **Quedo a la espera de la aprobación del usuario** para que el orquestador los escriba.