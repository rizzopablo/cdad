# Progress

Estado de features del proyecto.

## In progress

_(ninguna)_

## Done

- **epic-006-opencode-concurrency** (2026-10-22) — epic cerrado: 6/6 features e integración hecha; AC-7 pendiente del owner (`docs/epics/epic-006-opencode-concurrency/closure.md`).
- **006-004-active-decisions-table** (2026-10-22, epic 006) — sexta feature de
  `epic-006-opencode-concurrency`: **la tabla de decisiones vigentes del proyecto** y, con ella, la
  **distribución de la decisión que gobierna el trabajo siguiente**. Una decisión aprobada viaja
  **en el encargo** del rol al que gobierna (campo opcional `current_decisions`, declarado con
  `prepare --current-decision <JSON>` repetible; la sección `## Current decisions` se emite **sólo
  con filas** y sin ellas el render es **byte-idéntico** dentro de una misma revisión), y con ella
  el **principio de general antes que específico** (enmienda 005) encuentra su **casa única** en
  `skills/cdad-cycle/references/design-principles.md` y llega al **architect** (considerar
  alternativas generales y específicas y explicar el criterio) y al **reviewer** (evaluar
  consecuencias reales, con el límite de que la falta de una abstracción no es por sí sola un
  defecto) como **deber de rol**, sin re-enunciar el texto. **Contrato:** `spec.md` sha256
  `ee88d426…` (PD-1..PD-13, INV-1..INV-16, DEC-1..DEC-16, L-1..L-7, D-1..D-6) + `plan.md`,
  aprobados el 2026-10-20 por el orquestador bajo la **HITL delegada del epic** tras
  `plan-review-001..004` (B-1..B-4 cerrados). **Producto (rango `86cb942..a815f9b`: 67 commits, 65
  archivos, +14801/−13; de ellos 21 de producto, +435/−4, y `tests/` 7 archivos nuevos, +5301/−0;
  último commit de producto `fc1179b`):** U1 la fila declarada, su **forma cerrada de seis claves**
  y el **tope de 32 fail-closed** (la fila debe **nombrar al rol del paquete**; una fila `obsoleto`
  **no es admisible** en un paquete; `file` debe existir; `roles` en vocabulario cerrado) → U2 la
  sección aditiva del render, entre `## Contract` y el bloque de plan-task → U3 el principio: una
  casa y las dos obligaciones (fuente del rol + bloque estático + agentes regenerados) → U4 la tabla
  y su **upkeep del orquestador** (`stage-5-merge.md` §5.4, **sin** tocar el exit gate), la
  **regla general del CAS por digest base** y la reconciliación por **re-despacho**
  (`re-entry.md`) → U5 la **siembra** de este repo: «Decisiones vigentes» como **primer H2** de
  `docs/systemPatterns.md` con 26 filas (25 `vigente`, 1 `obsoleto`; 8 `Proposed` excluidos) y el
  **ADR-034** materializado con estado aprobado → U7 el **validador permanente de invariantes
  duraderas**, que **no nombra ningún ADR** ni fija ningún conteo (aprobar un ADR nuevo o reemplazar
  cualquiera **no obliga a tocar los tests**) → U6 **recorrido de aceptación real** (proyecto
  descartable, **sin despliegue a HOME**; E1..E7 y V-5 **cumplen**, incluida la **cadena del CAS**
  completa: rechazo por conflicto → re-despacho sobre la base nueva → materialización que conserva
  la fila del orquestador) → **B-1** la **plantilla nace sin decisiones** (fila de ejemplo fuera de
  la tabla, en prosa: un proyecto sin ADR ya no queda bloqueado). **Review formal: 2 bloqueantes /
  3 opcionales / 1 abstención** — **B-1** cerrado por RED/GREEN (`4d71ccc` → `fc1179b`);
  **B-2** resuelto por el **orquestador**, que auditó el diff (una línea) y adoptó la corrección
  bajo su propia autoridad (el upkeep de la tabla es suyo, ADR-003), sin reescribir historia ni
  cambiar el oráculo. **Gates:** `make validate` **Assert PASS: 182 / Assert FAIL: 1** (el único
  FAIL es **F011**, deriva ambiental de la copia instalada, **DT-8** preexistente); **suite de
  cierre: no ejecutada** (la corre una vez quien cierra, política declarada en el paquete).
  **Despliegue: NO hay despliegue en HOME**, por orden del owner (hay una sesión activa en
  OpenCode que no se debe tocar) ⇒ la copia instalada no contiene la feature. **Deuda:** **O-1**
  (la pertenencia a `docs/adr/` se comprueba sólo por prefijo), **O-2** (el ADR-034 conserva marcas
  residuales de borrador), **O-3** (falta el bloque U3 pedido en el validador bash; los tests
  Python sí cubren la fuente única), **W-U6-1** (fidelidad del scribe: el CAS protege la
  concurrencia, no la fidelidad ⇒ la salida es revisar el diff antes de aprobar), **W-U6-2**
  (**a verificar**: el adaptador re-despachó un paquete que ya tenía entrega completa y recibo
  durable; causa no investigada), **W-U6-3** (el adaptador entrega una sola parte `role-report`,
  cuya raíz permitida es la carpeta de la spec ⇒ materializar hacia el Memory Bank exige un
  descriptor propio del orquestador), `scope_validation: unknown` (deuda heredada de 006-005: el
  caso de B-2 es una instancia más) y la deuda declarada de la spec (**L-1** compatibilidad entre
  revisiones, **L-3** completitud de la tabla, **L-4** verificación del `reference`, **L-5** exit
  gate de stage 5, **L-6** esquema del request, **L-7** el producto no verifica la base del CAS).
  **Pendientes de cierre:** suite completa y redespliegue en HOME. **El epic NO se cierra: 6/6**
  features hechas ⇒ no queda ninguna feature en cola; el siguiente trabajo es el **cierre del
  epic**, previa la suite de cierre y el redespliegue.
- **006-006-spec-plan-review** (2026-10-20, epic 006) — quinta feature de
  `epic-006-opencode-concurrency`: la **revisión independiente de un borrador de especificación antes del RED**,
  como capacidad de primera clase del recorrido y no como rodeo. La forma del objeto se **declara** en el
  encargo (`contract.object_kind`); la revisión entra en el **gate 2→3** (supervisado, con
  `docs/specs/<feature>/plan-review.md`); el dictamen **nombra el objeto y su digest** y se materializa en la
  carpeta de la **feature activa**; y la **exención** del owner se registra en la misma entrada de aprobación y
  entra en la identidad **sólo cuando se declara**. **Contrato:** `spec.md` sha256 `4d029a11…` (PD-1..PD-16,
  INV-1..INV-13, D-1..D-15, V-1..V-8) + `plan.md` sha256 `1abe9e7b…`, aprobados el 2026-10-20 por el
  orquestador bajo la **HITL delegada del epic** (el owner la mantuvo ese día), tras `plan-review-001..004`
  (B-1..B-4 cerrados) y con la **errata B-5** aceptada en la aprobación. **Producto (rango `7f39e24..HEAD`:
  59 commits, 46 archivos, +11745/−61; de ellos 14 de producto, +499/−53, y `tests/` 6 archivos nuevos,
  +5030/−0; último commit de producto `de629b8`):** U1 el objeto declarado en el contrato (`--object-kind`,
  `--spec-path`, `--spec-version`; los checks del plan **sólo** sobre el documento de forma `plan`; por omisión
  la forma es `plan` ⇒ el comportamiento vigente no cambia) → U5 la exención registrada e **incluida en la
  identidad de la transición, pero sólo cuando se declara** (bloque `exemption` condicional ⇒ sin exención el
  payload es byte-idéntico al vigente y **las identidades históricas se conservan**, sin enmienda de 005-012
  PD-11, 005-014 PD-23 ni 006-005 PD-19(b); el **replay histórico** se distingue del **intento de sustituir la
  aprobación vigente**, que se rechaza explícitamente) → U2 la fuente canónica de «qué se revisa» (el substage
  generalizado al objeto de especificación, la regla de rol sin plan-centrismo) → U3 el recorrido principal
  (subfase y exit gate de la etapa 2, criterio en el gate 2→3, re-entry del dictamen, **política de
  compatibilidad** declarada) → U4 el rol y los agentes generados (el reviewer declara la etapa 2, el artefacto
  `plan-review.md` y la revisión de borrador) → U6 **recorrido de aceptación real** (proyecto descartable;
  E1..E7 **cumplen**: spec sin plan, spec+plan con los dos digests fijados, borrador de **otra** feature con el
  dictamen en la carpeta de la feature activa, re-review por digest, el dictamen que **no** aprueba, el juicio
  semántico que declara el bloqueante, y el caso de compatibilidad entre revisiones) → **W-1** el arreglo del
  recorrido: `prepare --replace-packet` **reemplaza un paquete de borrador preparado** y recalcula los digests
  desde los bytes actuales (la ruta del contrato aprobado queda byte a byte idéntica). **Review formal: apta
  para cierre, 0 bloqueantes / 2 opcionales** (O-1 la selección de vigencia de la errata B-5 **no** está
  automatizada ⇒ deuda; O-2 la evidencia de aceptación tras W-1 **aplicado** en la misma ronda). **Gates:**
  `make validate` **168 PASS / 1 FAIL = F011** (deriva ambiental de la copia instalada, **DT-8** preexistente);
  **suite de cierre: 1404 passed, 5 skipped** (la corrió quien cierra). **Desplegado** en HOME por orden del owner (script de despliegue de la feature; la evidencia de
  U6 declara la copia desplegada desde HEAD `a276531`, U1–U5): **redesplegado al cierre en `86cb942`** (incluye W-1, verificado con el CLI desplegado). **Deuda:** **O-1** (automatizar el
  selector de vigencia B/C: verificado por separado con las transiciones reales, sin defecto observado), **W-2**
  (el adaptador termina con rc=0 aunque el resultado sea `blocked`; observación), la **deuda declarada de la
  spec** (nombre `draft-plan`/`plan-review`/`plan_version`/`plan-tasks`; ADR-013 O-C; ambientación del dictamen;
  exención como acto de autoridad, no firma; compatibilidad entre revisiones; identidad de la retirada) y la
  **deuda heredada de 006-005 sin cambios** (U6-2, O-2, D-U65-4, D-U65-5, O-2/O-3 de sus reviews, el límite de
  transporte del paquete nativo, DT-8 y el flake DT-9). **El epic NO se cierra: 5/6** — queda
  **006-004-active-decisions-table** (enmienda 003 + 005 ⇒ ADR-034), en el orden del owner
  (**006-005 → 006-006 → 006-004**). **Siguiente:** `006-004-active-decisions-table`.
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
  parcial, **B-4** nuevo: la llave expuesta sin declaración vuelve a `unknown`) y **re-review focal 2 sin bloqueantes**
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

- **006-003-installer-single-profile-delegation-config** (2026-10-18, epic 006) — tercera feature de
  `epic-006-opencode-concurrency`. El instalador y el generador quedan **sin perfiles y sin mapa de modelos**;
  la delegación externa toma el modelo de un **único archivo de configuración**; el instalador **retira sus
  propios obsoletos**; y la credencial del servidor se carga de un archivo con permisos verificados. **Contrato:**
  `spec.md` sha256 `c25ebf0e…` (PD-1..PD-8, INV-1..INV-7, D1..D8; **§8 A-1..A-4** del orquestador y **§9 A-5** del
  dueño) + `plan.md` con **A-6**, aprobados el 2026-10-18 bajo la **HITL delegada del epic** (A-5 lo aprobó
  **Pablo**). **Producto (41 archivos, +1163/−860; rango `2b43516..HEAD`, 111 archivos +12653/−1771):** U1 generador
  sin `--profile` y `scripts/cdad-models.sh` **retirado**; U2 instalador sin perfiles (`--basic` y
  `CDAD_MODEL_PROFILE` deprecados sin efecto; los demás flags **rechazados** con diagnóstico); U3 textos instalables
  sin perfiles ni modelos; U4 `delegation.json` v1 por destino y rol como **única fuente** del modelo externo (la
  clave `model` de la exec-config se ignora con aviso) + archivos de config del usuario **fuera del manifiesto**
  (A-3); U6 credencial desde archivo con permisos verificados sobre el fd abierto y diagnóstico 401/403
  autosuficiente sin el valor; U7 **retiro de obsoletos propios** (intactos por sha256; los modificados se preservan
  como CONFLICT) con la cuenta del `Verify` derivada del staging (A-6); U8 aceptación end-to-end en raíz redirigida.
  **Gates RED→GREEN:** U1 `d5b2ae0`→`afcd14f` (testfix `bb674b4`); U2 `f2c3540`→`44f1561`; U3 `54c6ac6`→`2b1b597`;
  U4 `5b91387`→`df90b41`; U5' `0629ae0`(+`113c777`)→`0230156`; U6 `e2eba98`→`797b935`; U7 `3a04ad1`→GREEN detenido
  `ef78451`→testfix `12a859b`→`516149b` (A-6); U8 `1bc7645`. **A-5 (dueño, a mitad de camino):** se retira la
  verificación de familia (`cdad_model_family.py` **no se construyó**; el GREEN `-005` quedó abandonado sin cambios);
  se conservan la observación I8 y los demás invariantes anti-sesgo. **Review formal:** **0 bloqueantes / 7 opcionales
  / 3 abstenciones**; review-fix de O-1/O-2/O-4/O-5 (`c57fc79`→`ef8d2f8`, con `c57fc79` declarando que O-5 **no era
  reproducible**), **re-review focal 1 con 1 BLOQUEANTE (B-1)** que **refutó** esa afirmación (el TSV del manifiesto
  leído con `read` de bash colapsa columnas vacías y retiraba sin comparar sha) y se corrigió con **remedio
  estructural** (veredicto `unverifiable` + registros **NUL-framed**; `26667b5`→`738a380`), y **re-review focal 2 con
  0 bloqueantes** (OPT-2 a deuda). **Suite de cierre:** `pytest tests/` sobre `8638d06` → **1177 passed, 5 skipped,
  0 failed**; `make validate` 168 PASS / 1 FAIL (= F011, **DT-8** preexistente) y **169/0** sobre la instalación de
  aceptación. **Deuda:** **O-3** (precedencia de `XDG_CONFIG_HOME` del host frente a la raíz redirigida: **decisión
  del dueño**), **O-6** (XDG relativo), **OPT-2** (comentario de symlinks en `install.sh`), **DT-8**, y la evidencia
  para **006-005** (abandonar un paquete despachado **no lo libera**: ningún comando lo lleva a `failed`). Decisión
  registrada en **ADR-033** (reemplaza ADR-007 y la parte de perfiles de ADR-008). **El epic NO se cierra: 3/6** — quedan **006-005-native-path-parity**, **006-004-active-decisions-table** y **006-006-spec-plan-review** (enmienda 006, aprobada); **redespliegue en HOME ordenado por el dueño el 2026-10-18**. **Siguiente:** `006-005-native-path-parity`.
- **006-002-delegation-by-layer** (2026-10-18, epic 006) — segunda feature de
  `epic-006-opencode-concurrency` y corrección de la **regla de delegación**: el texto instalable tenía el
  **mismo mecanismo de runtime en cinco lugares** y un consumidor real leyó la skill como si **mandara** el
  adaptador CLI dentro de su propio runtime (1.145 turnos, 6 compactaciones, ninguna sesión hija). Aplica el
  **principio de capas del dueño** (`skills` metodología neutral; `agentes` comportamiento por runtime;
  `scripts` dependientes del SO; **adaptadores sólo para otro runtime o uno sin delegación propia**) y el de
  `plan.md` §9 (**los modelos los fija la configuración, nunca el orquestador ni los scripts**). **Contrato:**
  `spec.md` (PD-1..PD-11, INV-1..INV-8, D-1..D-7) + `plan.md` (A-1, A-2) aprobados el 2026-10-17 bajo la HITL
  delegada del epic, con **enmiendas 001/002 del dueño** sobre `/tmp` (002 reemplaza a 001: el límite era de
  su servidor, no de la metodología). **Producto (16 archivos, +255/−435):** sección
  `<!-- cdad-section:delegation -->` en `sources/agents/adapters/{opencode,claude-code}.md` compuesta por
  `scripts/cdad-generate.py` (que **pierde el bloque hardcodeado** del orden) y regenerada en los dos
  orquestadores; §4 neutral; retiro de las **dos referencias por runtime** (su detalle histórico queda **no
  instalable** en `docs/evidence/runtime-delegation/`, byte-idéntico salvo el encabezado declarado);
  `cli-delegation.md` como **sólo contrato del adaptador**; `SKILL.md` §2 sin modelos (**F001 reformulado**);
  equivalencia de transporte en `references/re-entry.md`; las **4 reglas de contexto** en
  `sources/roles/orchestrator.md` (la 4ª = **rutas estables del workspace**; **ningún texto instalable nombra
  `/tmp`**). **Gates RED→GREEN por unidad:** U1 `a2db8f8` (9 failed / 1 passed) → `51ab88d`; U2 `4e17dcc` →
  `8cf2d75`; U3 `2665d55` → `5ad04e2` (**testfix** `20bb835`: el selector de evidencia pasó de **416** a **2**
  copias, sin cambiar aserciones); U4 `3c828ad` → `8c05755`; U5 `1125c53` → `8d4b302`; U6 `edc58ae` →
  `900fa58`; **arreglo de regresiones de U1** `7d13a6d` (A2 ruta `<skill-dir>`; P1 el recibo no reestata los
  pasos); enmiendas sobre `/tmp` `b9d9455`→`4c068ea` y `300a05c`→`a3b54e6`. **Aceptación real (U8):**
  worktree aislado con los agentes de `make staging PROFILE=basic` en `.opencode/agents/` del proyecto
  (**HOME sin tocar**); el orquestador (deepseek) despachó al reviewer por **`task` nativo** — una sesión hija
  `cdad-reviewer` (familia glm) `succeeded`, **56 comandos bash, ninguno** con el adaptador o un `run` del
  CLI—, escenificó el texto final en `.cdad/inbox` y `receive` cerró **`pending`**; el paquete pasó al repo
  principal byte-idéntico (intento `at-006-002-u8-001`). **Review formal:** **1 bloqueante / 4 opcionales /
  4 abstenciones** (**B-1**: alias de modelo de runtime y nombre del gateway de despliegue en
  `sub-agent-strategies.md:51`, que **escapaba al oráculo declarado**), cerrado por review-fix
  (`5c85d68` RED → `a25fc20` GREEN, 1 línea) con **re-review: B-1 CERRADO, 0 bloqueantes, 1 opcional nuevo
  (NF-1)**. **Gate de cierre:** suite **1119 passed, 5 skipped**, sin fallas; `make validate` **161 PASS /
  1 FAIL** (F011 = **DT-8**, drift preexistente de la instalación de HOME); `make staging PROFILE=basic &&
  make agents` determinista. **Deuda:** O-1..O-4, **NF-1**, `sub-agent-strategies.md:49-50`, el **despacho
  erróneo detenido** (registro sin recibo del intento `at-006-002-u6b-red-001`), **DT-8**, y que el
  consumidor **todavía prescribe el adaptador en su handoff** (fuera de alcance; lo actualiza su dueño).
  **El epic NO se cierra (2/4).** **Siguiente:** `006-003-installer-single-profile-delegation-config`.
- **006-001-opencode-concurrency-reliability** (2026-10-17, epic 006) — primera feature de
  `epic-006-opencode-concurrency` y corrección del **modo de ejecución del adaptador OpenCode** ante la
  **contención medida** del store compartido (dos despachos reales del implementer terminaron `failed` con
  `LockTimeoutError`/`database is locked`, ≈89 s y ≈487 s). Cierra la **fila 1** del plan del epic:
  **selección de ejecución explícita** (`server` | `service` | `standalone`), **preflight** de servidor y de
  servicio, **procedencia por intento** dentro del esquema I8 sin cambiarlo, **espera proporcional** (cero
  lecturas del store mientras el cliente vive) y **recuperación que conserva la correlación y no re-despacha**.
  Contrato **spec v2** (PD-1..PD-14, `dac418b9…`) y **plan v2** (`2726744…`), aprobados el 2026-10-16 bajo la
  HITL delegada del epic; **enmienda 001** (modo `service` configurado) aprobada por el dueño, con **INV-2
  reescrita** e **INV-10 nueva** (con el servicio vivo ningún camino abre un `standalone` ni re-despacha solo)
  y **D-11 (A)** ratificada (del registro del servicio se proyecta **solo** la clave `version`, sin red ni
  contraseña, fallando cerrado). **Producto:** `cdad_delegate_opencode.py` (**+1333/−124**; 2138 líneas
  finales), `cli-delegation.md` (+170/−19) y `assets/opencode-exec-config.example.json` (**nuevo**).
  **Gates:** RED→GREEN por unidad —T1 `91f7e98` (14 failed / 4 passed) → `4bc8934`+`a96c2d8` (focal 18);
  T1b `7ccedb4` (16 failed / 0 passed) → `b949849` (focal 16, regresiones 54); T2 `8447443` (8 failed /
  4 passed) → `ddba831` (focal 12; 93 passed ×3); T3 `5e5828a` (oráculo sensible **por mutación**) →
  `d0a7963` (focal 2; `make validate` 155 PASS / 1 FAIL, F011 preexistente)—; **review formal 3 bloqueantes /
  5 opcionales / 3 abstenciones** (reviewer de familia glm, **distinta** a la del implementer): **B1** (piso
  del cliente **sin tope** en la banda de cota media: el adaptador podía morir después de la cota de la
  interfaz y perder la correlación), **B2** (el intento previo **fallaba abierto** con el store ocupado o
  ilegible: segundo worker vivo del mismo paquete) y **B3** (sin focal de la espera ni del preflight en modo
  servicio) — los tres **corregidos** en el review-fix (`17a7ca1` RED → `161c9ff` GREEN, +79/−14, `tests/`
  intacto, intento 3 tras **dos intentos muertos por caída del proveedor**), con **re-review 5 de 5 cerrados,
  0 bloqueantes y 1 opcional nuevo a deuda (O5-RF)**; **suite de cierre 1 failed / 1079 passed / 5 skipped**
  (la falla es una **instancia de DT-9**: margen de la cota de 2 s del fixture bajo carga; aislada **5/5
  verde** a ≈2,08 s). **Recorridos reales (PD-6):** contra el servicio vivo → **`blocked` en 1,3 s por el gate
  de versión** (2.0.22 vs cliente 2.0.27; sin fallback, sin tokens); con el servicio detenido →
  `require:false` **`completed` 33,9 s con fallback declarado** y `require:true` **`blocked` 1,1 s**; **la
  concurrencia real en `mode: server` contra el servidor único queda pendiente de una credencial del dueño** ⇒
  **PD-6 = BLOQUEO declarado** y **AC-7 pendiente del dueño**. **Desplegada en HOME el 2026-10-17** por orden
  del dueño con **perfil `basic`** (`install.sh --check` PASS, 391 grupos; el primer intento, con el staging
  por defecto, se corrigió con `make staging PROFILE=basic`); `install.sh` rc=1 por un **CONFLICT preservado**
  del agente reviewer del dueño y por **DT-8** (`__pycache__` en el staging); **el despliegue es anterior al
  review-fix ⇒ redespliegue pendiente de la orden del dueño**. **Deuda:** PD-6 (BLOQUEO), AC-7 (dueño),
  DT-3/DT-6/DT-7/DT-8/DT-9, los opcionales **O3–O5** de la review y **O5-RF** de la re-review, y **dos deudas
  del CLI**: `receive` finaliza el recibo con un `kind` que la tabla cerrada de `artifact-policy.json` rechaza
  (**dos veces** en esta feature) y **no hay vía CLI para fallar un paquete despachado** (la disposición solo
  admite `abandoned|superseded`). Decisión propuesta para registro en **ADR-031**. **El epic NO se cierra:**
  siguen en cola **006-002-delegation-by-layer**, **006-003-installer-single-profile-delegation-config** y
  **006-004-active-decisions-table** (las tres enmiendas al plan aprobadas por el dueño el 2026-10-17).
  **Siguiente:** `006-002-delegation-by-layer`, que se abre al cerrar 006-001.
- **epic-005-real-operation** (cerrado 2026-10-14, 14 features) — «Operación real y medición de
  contexto»: las **14 filas del plan en `done`** (005-001, 005-005, 005-006, 005-008, 005-009, 005-010,
  005-002, 005-003, 005-007, 005-004, 005-011, 005-013, 005-012, 005-014), cada una con su cierre en
  `docs/specs/005-*/closure.md`. Entregó: aprobación de contrato por rol y reemplazo de paquete;
  coherencia de adopción; arranque guiado con una instrucción breve; capacidades de rutas para un
  consumidor con tests anidados; delegación externa entre CLI (interfaz común + adaptador OpenCode
  real); medición de contexto opcional y read-only (**no enganchada en ningún gate**); orientación
  acotada por la vista `status`; planificación progresiva y `open-unit`; roles CDAD en Claude Code por
  el mecanismo nativo; entrada común por `status`; contrato de unidad como proyección generada; registro
  de transiciones con identidad por contenido y cierre que comprueba antes de aplicar; y replay de
  cierre como no-op. **Versión de referencia:** producto del repo `d3b9ccd`, instalación de HOME
  `29a4805` (`install.sh --check` PASS), con **cero diferencias de producto**
  (`git diff --name-only 29a4805..d3b9ccd` = solo `docs/epics/epic-005-real-operation/execution.md`);
  último commit de producto `a4028af`. **Criterios del epic:** 1 ✅; 2 ✅ en la parte verificable, con
  límites declarados (RD-a; D6 de 005-002; MIX-V6V7 de 003-007); 3 ✅ como las secciones citadas
  (005-003 §9; 005-007 §7; 005-011 AC-6/AC-7), sin documento consolidado aparte; 4 ✅ (suite de cierre
  del orquestador en worktree fijado al commit de cierre); **5 ❌ no ejecutado** (aceptación conjunta del
  consumidor, del dueño del consumidor). El cierre **no implica publicar** (historial nuevo). Ver
  [closure.md](epics/epic-005-real-operation/closure.md).

- **005-014-closure-replay** (2026-10-14, epic 005) — decimocuarta unidad de epic-005 y **unidad correctiva
  pequeña** sobre el uso previsto de 005-012. Cierra la **fila 14** del plan del epic: **repetir un cierre ya
  aplicado no falla ni sugiere abrir la unidad**. **Defecto medido:** con la feature cerrada `active_feature`
  es `null` (`cdad_packet.py:5460-5462`) y el guard de feature nula (`:5062-5065`, mensaje que sugiere
  `open-unit`) corre **antes** de la búsqueda idempotente por `transition_key` (PD-11, `:5310-5324`); el
  análogo ya declarado (`late-delivery`, `--feature` en `:5061`) fija la forma del arreglo. **Producto:**
  (T1) `cdad_packet.py` (+134/−13: `_resolve_closure_feature` con **tres fuentes** de resolución —`--feature`
  → `active_feature` → `state.execution.feature_id`—, `_transition_noop_message` y la rama `closure` con el
  no-op por identidad **antes** de PD-8/`--closure-path`/autoridad en la rama de feature cerrada, más
  PD-24/PD-25/PD-27); (T2) gate de aceptación. **Gates:** RED `8a969d3` (**4 rojos por aserción**, 0 por
  import/colección) → GREEN `a4028af` (**focal 4 passed**; cuatro módulos de 005-012 **47 passed**; `tests/`
  intacto); **contrato enmendado antes del GREEN** (**enmienda 001**, spec v2 sha256 `5c23caa2…`,
  re-aprobada): el RED expuso una **contradicción interna** del v1 (PD-22 sin la ejecución ligada ⇒ la orden
  verbatim no resolvía la feature y el no-op de PD-23 era inalcanzable); la v2 agrega la tercera fuente
  (PD-22), PD-27 (sin feature activa **nunca** se aplica un cierre) y PD-24 contra la feature resuelta, y suma
  E-6. **Aceptación T2 APROBADA:** AC-1/AC-3 (repetición idéntica → rc=0, no-op que nombra la entrada, state
  byte a byte igual, 1 entrada de cierre, `validate-state` rc=0 `VALID: idle`) y AC-2 (otro payload → rc=2
  `state incoherent`, nombra feature+`done`, sin `open-unit`, sin efectos), con el **CLI real** sobre proyecto
  descartable. **Review formal única:** **0 bloqueantes / 4 opcionales / 3 abstenciones** (reviewer de familia
  distinta; reprodujo focal, regresión y aceptación, y corrió 5 sondas adversariales propias fail-closed); los
  **4 opcionales** (O-1..O-4, Nit/FYI) **a deuda** por el criterio vigente 2026-10-12. **Suite de cierre una
  vez** en worktree aparte fijado a `2de9747`: **1028 passed / 4 skipped, sin fallos** (incluye los 4 focales
  nuevos); `make validate` **155 PASS / 1 FAIL** (F011 preexistente). **Deuda:** spec §6 **E-1..E-6** (E-1
  `gate` ignora `--feature` y E-2 replay tras cambio de feature activa, priorizadas; E-3; E-4; E-5; E-6
  cobertura declarada) + review O-1..O-4. Contrato: `spec.md` `5c23caa2…` (v2, enmienda 001). Decisión
  propuesta para registro en **ADR-030**. **El epic NO se cierra:** quedan el **gate de saneamiento antes de
  publicar** (dueño, worktree aparte) y el **despliegue** (decide el dueño); **14/14** unidades del epic, sin
  ninguna en cola.

- **005-012-transition-registration** (2026-10-14, epic 005) — decimotercera feature de epic-005. Cierra la **fila 12** del plan del epic: **una operación del CLI que registra la decisión explícita del orquestador sobre una transición** —recepción de una entrega, aprobación de un gate, avance de etapa, cierre de feature, entrega tardía y **disposición de un despacho sin recibo**—, **comprueba sus requisitos mecánicos** y la aplica **sin edición manual del state**, con **recibir que nunca aprueba**, **repetición que no duplica efectos** y **el juicio en el orquestador**. **Producto:** (T1) `cdad_packet.py` (+312: subcomando `register-transition` con el escritor único existente, forma aditiva del registro, marcador `evidence missing`, **digests derivados** por el CLI y la **identidad por contenido** con su payload canónico; clases `delivery` y `advance`); (T2) `cdad_packet.py` (+152/−4: clase `gate`, pin de contrato y plan verificado contra los bytes, **autoridad en tres casos** —delegación vigente / sin delegación / sin epic— sin bloquear al dueño); (T5) `cdad_packet.py` (+62/−2: **vigencia estructural** de la aprobación, `supersedes` en la entrada nueva y lector aditivo); (T3) `cdad_packet.py` (+269/−2: `closure` que **comprueba entregas requeridas y aprobación vigente ANTES de aplicar**, falla cerrado **nombrando** y ofrece las dos salidas; más la clase `disposition`, que registra sólo la traza y **no** fabrica un `completed`); (T4) `cdad_result.py` + `cdad_packet.py` (+130/−7: `receive --late` que **reusa** la máquina de recibos invirtiendo **sólo** la precondición de vigencia, y la clase `late-delivery`); (T6) `cdad_packet.py` (+72: `prepare --new-execution` rechaza el **contexto abierto y sin uso**, cerrando la deuda que 005-013 le dejó a esta unidad); (T7) `re-entry.md` paso 4 y `project-execution.md` (sección nueva contigua a las operativas §5-§8) **nombran la operación por referencia**, sin re-declarar ninguna regla. **Gates:** RED→GREEN por ficha (T1 15 rojos por aserción → **15 verdes**; T2 14 → **14**; T5 5 → **5**; T3 8 rojos → GREEN con **bloqueo declarado 7/8** —el rojo era el **fixture** del test, no el producto— → testfix que toca **sólo** la precondición (`016405f`) → **8 verdes**; T4 7 → **7**; T6 3 → **3**; T7 docs-only con comprobaciones observables), regresiones declaradas **56/33/42/20/25/42** verdes y `git diff -- tests/` **vacío** en cada GREEN; **review formal única 2 bloqueantes / 7 opcionales / 3 abstenciones** —**B1** (la autoridad de PD-6 no se aplicaba a `closure`: un cierre bajo delegación revocada o vencida prosperaba) **corregido ya** con RED primero (`724ca3c`), **B2** (la identidad **tragaba** invocaciones distintas como no-op rc=0 afirmativo) **corregido con enmienda del contrato** (draft-003: PD-10 con los insumos con efecto) + RED/GREEN (`64a32d3`), **B3** (la reaprobación tras una enmienda obligaba al registro manual, porque `--supersedes` sólo cita entradas con clave y las aprobaciones a mano son **keyless**) **corregido con enmienda del contrato** (draft-004: la vigencia la decide **el pin que nombra los bytes actuales**, el criterio que el cierre ya usaba) + RED/GREEN (`ffb7abd`); **O1..O4** corregidos en las enmiendas, **O5/O6/O7** a deuda (D-13..D-15)—; **T8 (gate de aceptación) APROBADO y repetido sobre el commit final**: AC-1..AC-4 con el **CLI real del repo** sobre **proyectos descartables en `<tmp>`** (AC-1: **8 invocaciones todas rc=0**, **7 entradas** de la operación, digests **derivados**, **cero** ediciones manuales del state; AC-2 entrega tardía sin reabrir ni aprobar; AC-3 no-op byte-idéntico / entrada nueva / excluyente rc=2; AC-4 rechazo que **nombra** + disposición que **destraba** el cierre); **suite de cierre una vez** en worktree fijado a **`6fd515d`**: **1024 passed / 4 skipped, sin fallos**; `make validate` **155 PASS / 1 FAIL** (F011 preexistente). **El dato de la unidad:** de las **30 entradas** de su tramo, **24 las registró la operación nueva** (20 `delivery` + 4 `gate`) y **6** fueron manuales con motivo declarado (el discovery, las cuatro aprobaciones `specification` y el RED de T1); la operación **no pudo** registrar la reaprobación de la enmienda B2 —respondió `state incoherent` nombrando `transition_key None`—, que es **el defecto B3 medido**, y la reaprobación de B3 se registró a mano porque **el arreglo todavía no estaba implementado** (declarada como **última por esa causa**). **Deuda:** `D-1..D-16` de la spec §7 (D-9 **retirada**; nuevas D-12..D-16) consolidada en `debt.md` con condición de cierre, más las abstenciones y opcionales de la review, el **commit del heartbeat externo** `da3612a` que escribió el state fuera del ciclo y **los dos digests escritos mal a mano y corregidos** (evidencia de por qué existe la unidad), y el **despliegue pendiente** de **005-013 y 005-012** (la operación no existe en la versión instalada). Contrato: `spec.md` `9e34750f…`; `plan.md` `9abfb894…`. Decisión propuesta para registro en **ADR-029**. **Siguiente:** ninguna unidad en cola (**13/13**); el epic **no se cierra** acá: quedan el **gate de saneamiento antes de publicar** (`execution.md:65-73`), el **despliegue** (dueño) y la decisión del dueño; el proyecto queda **en reposo**.

- **005-013-unit-contract** (2026-10-14, epic 005) — duodécima feature de epic-005. Cierra la **fila 13** del
  plan del epic: **el hash identifica el contrato que recibió el agente y deja de bloquear globalmente la
  planificación del proyecto.** El **contrato de una unidad** pasa a ser una **proyección GENERADA del plan**
  (objetivo/alcance/aceptación de la unidad + las secciones compartidas que le aplican + su aprobación y versión
  de origen), **publicada una vez** junto al paquete y **pineada por su digest**; el sha del plan queda como
  **procedencia**. La unidad se localiza **estructuralmente** (la única fila de una tabla del plan que contiene
  el id de la feature como token completo, con el encabezado de esa tabla) y, sin localización sin ambigüedad,
  hay **fallback declarado** al plan completo (`approved-epic-plan`), informado en el diagnóstico y en `status`.
  Las consecuencias por tipo de cambio: `current` (sin efecto) / `impact` (journal durable e **idempotente**;
  decide el orquestador) / `impeded` (**sólo** por autorización retirada, rc=2, con la salida nombrada). La
  **recepción y el resume** validan contra la proyección **registrada**, no contra el plan vivo. **Producto:**
  (T1) `cdad_packet.py` (+397/−15: localizador estructural, fallback, anclas por declaración del producto,
  publicación/pin, kind `approved-unit-contract`, `validate_request` con los dos pares) + `epic-plan-template.md`
  (+11: la declaración de anclas legible por máquina); (T2) `cdad_packet.py` (+430/−20: `validate-unit-contract`
  con línea base por parte, journal `.impact.json` idempotente, salida del impedimento y bloque `unit_contract`
  de `status` **de solo lectura**); (T3) `project-execution.md` (+21: la autoridad del architect nombra por
  referencia el contrato de unidad, su origen y la salida del impedimento, sin duplicar el mecanismo);
  (T4) gate de aceptación. **Gates:** RED→GREEN por ficha (T1 **14 RED por aserción + 1 control** → **15 verdes**,
  `9785423`/`021a491`; T2 **15 RED** → **15 verdes**, `c61db34`/`da3ced5`; T3 docs-only con comprobaciones
  observables, `b3cb88c`), **regresiones declaradas 77, 59 y 21 verdes** por ficha; **review formal única
  1 bloqueante / 5 opcionales / 1 abstención** — **B1** (`prepare` con `--out-dir` custom reescribía una
  proyección ya publicada y rompía el pin del paquete viejo, INV-3/PD-4; reproducido por el reviewer con la
  medición `2237d30d… → cec98be9…`) **corregido ya** como **escritura create-only** (`4bf688c` RED con 3 casos
  nuevos / `f41025f` GREEN, **focal T1 18 verdes**), **O1** (errata declarada en `t1-green.md`) corregido, y
  **O2..O5** a deuda; la **abstención** (AC-9/T4) se resolvió corriendo T4; **gate T4 APROBADO**: prueba decisiva
  con el **CLI real** sobre proyectos descartables en `<tmp>` en las **tres formas de plan** (este epic, la
  plantilla del producto y un fixture sintético anónimo con la celda como enlace), AC-1..AC-9 verificados en las
  tres (`current` al agregar una unidad independiente con `receive` rc=0; `impact` al cambio relevante; `impeded`
  sólo por autorización retirada con su salida); **suite de cierre una vez** en worktree fijado a **`7ab16ba`**:
  **960 passed / 4 skipped, sin fallos**; `make validate` **155 PASS / 1 FAIL** (F011 preexistente).
  **Deuda:** `review.md` O2..O5 (copia inerte de la declaración de anclas en cada plan; lectura del activo
  instalado, conservadora hoy; límite de bytes de la vista con el bloque `unit_contract`; `mtime` como
  aproximación de la fecha de publicación) + spec §8 D-1..D-3 (oráculos vigilados; reconciliación de un paquete
  `dispatched`, territorio de 005-012; juicio de «restricción de aplicación inmediata») + el **acotamiento de la
  fila 13 (b)** (cambiar una restricción da `impact` y lo decide el orquestador: el CLI no juzga la inmediatez sin
  una marca estructural) + **datos para 005-012** (la ejecución huérfana `exec-005-013-unit-contract-001`; los
  registros del state hechos con scripts del orquestador) + el **despliegue pendiente** (el comportamiento nuevo
  no existe en la versión instalada; O3 se resuelve con el despliegue). Contrato: `spec.md` `4369822e…`;
  `plan.md` `89d5d8cf…`. Decisión propuesta para registro en **ADR-028**. **Siguiente:** `005-012-transition-registration`,
  en orden `005-013 → 005-012` (ninguna abierta); el epic-005 sigue en `features-loop` (**12/13**).
- **005-011-common-entry** (2026-10-14, epic 005) — undécima feature de epic-005. Cierra la **fila 11** del plan
  del epic: **una sesión nueva entra al proceso por una ruta breve y COMÚN —la vista `status`— antes de leer el
  state o explorar**, en los dos runtimes; la vista **nombra la pata que diverge y su resolución verificada**; y
  con un paquete `prepared` nombra la **acción natural (despacharlo)**. **Sin documento nuevo y sin segunda
  copia:** la regla se **referencia** (`orientation.md` §1 + `project-start.md` §11). **Producto:** (T1) raíz
  relativa consistente en `cdad_packet.py` (cwd + `is_dir()`, como `cdad_result.py`; se retiran el rechazo
  especial de `status` y el diagnóstico **C4** de 005-003; se corrigen `orientation.md` §3 y
  `project-execution.md:49`; **los dos oráculos declarados** de PD-3 actualizados —uno reemplazado, el otro con
  el fixture de fallo corregido y su oráculo de captura conservado—); (T2) **entrada común por `status`** en el
  Step 1 de `skills/cdad-cycle/SKILL.md` y `skills/cdad-epic/SKILL.md`, `state-detection.md` a ampliación
  condicional con gatillo e `orientation.md` indexado; (T2b) la **misma entrada en el prompt del agente
  orquestador** (`sources/roles/orchestrator.md` + derivados regenerados con `make agents` idempotente;
  `resume` como paso siguiente, solo con ejecución activa, rama «start from rest» conservada); (T3) en la vista,
  la **pata que diverge leída** del chequeo con su resolución **solo** si es `project` (ausencia ≠
  incoherencia) y la ruta de `prepared` = **despacharlo** con `--replace-packet` condicional, sin cambiar
  `entry`. **Gates:** RED→GREEN por tarea (T1 `00dd36e`/`4ea82ea`/`53413b3`, T2 `13c68b9`, T2b `68044cb`,
  T3 `1c207d9`/`860a611`); **review formal única 0 bloqueantes / 5 opcionales / 2 abstenciones** (focales T1
  5/5 y T3 5/5, oráculos de 005-003 21 passed, guardas de texto 61 passed; los tres GREEN sin tocar `tests/`;
  falsificación del oráculo contra el CLI pre-fix en worktree), con **OP-1 y OP-2 corregidos antes del
  despliegue** (`362ce3a`; guardas 72 passed); **gate T4 APROBADO con AC-6 parcial declarado** — AC-7
  CUMPLIDO (`status` como primera acción; primer `Agent` de la llamada 23 a la **14**; salida previa de 105 mil
  a **54 mil car., −49 %**) y AC-6 CUMPLIDO EN PARTE Y DECLARADO ASÍ (skill en la llamada 1 y `status` en la
  **3** en vez de la 21; despacho de la llamada 71 a la **59, −17 %**; el state completo se lee en la llamada 2
  por costumbre, 53 mil car.), con la causa identificada (en OpenCode la entrada real es el prompt del agente,
  no la skill) y su corrección T2b; **suite de cierre una vez** en worktree fijado a **`8ec574d`**:
  **927 passed / 4 skipped, sin fallos**; `make validate` **155 PASS / 1 FAIL** (F011 preexistente).
  **Deuda:** `debt.md` OP-3..OP-5 + **RD-a** (agentes derivados viejos tras un despliegue) + **RD-b**
  (compactación del state), con condición de cierre; spec §8 D-1..D-3; F011 preexistente. Contrato: `spec.md`
  `a6d05d9d…` (con la enmienda 4). Decisión registrada en **ADR-027**. **Siguiente:** `005-013-unit-contract`,
  en orden `005-013 → 005-012` (ninguna abierta); el epic-005 sigue en `features-loop` (**11/13**).

- **005-004-claude-code-roles** (2026-10-13, epic 005) — décima feature de epic-005. Cierra la **fila 10** del
  plan del epic: **roles CDAD activos en Claude Code para este proyecto** por el **mecanismo nativo** (`Agent`
  con `subagent_type: cdad-<rol>`, subagentes `cdad-*` instalados) y **un ciclo corto real despachado desde una
  sesión nueva de Claude Code con la versión instalada al empezar**, con recepción CDAD (I8 `runtime: claude-code`
  → rol nativo → `receive` → `reconcile`). **Sin infraestructura nueva:** reusa paquete, I8, `receive`,
  `materialize`, `reconcile` y la vista compacta. **Producto (T1..T4 + focales):** (T1) la herramienta de despacho
  declarada pasa a ser la real (`Agent`) en el generador, el adaptador fuente y los derivados, con aserción nueva
  del validador del repo (`Task` queda solo del lado OpenCode); (T2) se corrige el enunciado falso del instalador
  (no hay `strip`: despliega los bytes staged sin transformarlos y la ausencia de `model:` bajo `basic` la produce
  el generador) y se declara la procedencia de modelo bajo `basic` con la exención **explícita** de
  reviewer≠implementer (por referencia a ADR-007); (T3) **pata Claude Code aditiva** del chequeo de versión
  (participa solo si la instalación CC es detectable; no altera los cuatro veredictos/`rc`; marca faltante =
  `unknown` con causa; cierra D-3 de 005-007 en su parte de comprobación); (T4) **mapa de hooks declarado una vez**
  en su dueño y consumidor corregido por referencia, con un focal que **ejecuta el guard** con cargas PreToolUse
  sintéticas (rol desconocido fail-open, roles sin hooks, paridad del frontmatter con `CC_GUARDS`).
  **Gates:** RED→GREEN por tarea (T1 `34703b6`/`cc6e5a5`, T2 `0964694`/`96786de`, T3 `4828c0c`/`b05c5c1`,
  T4 `0cdec77`/`65a0de9`); focales **29 passed** en la corrida del reviewer; **gate de T5 paso a APROBADO**
  (`t5-acceptance.md`: recorrido real, I8 `runtime: claude-code`, `Agent cdad-reviewer` sin fallback, recibo
  durable `semantic_status: pending` `VALID`, `reconcile: received`, transición del state por el escritor único) y
  **paso b BLOQUEADO** hasta el despliegue del dueño; **suite completa una vez** en worktree fijado a `c8ab21f`
  **915 passed / 2 failed / 4 skipped** —una **regresión real de T4** corregida en `5d6f667` y un error de perfil
  del lanzador—, verificación en `5d6f667` **55 passed** y `make validate` **155 PASS / 1 FAIL** (F011
  preexistente); el resto de la suite por equivalencia (`re-entry.md`). **Review formal única:** **0 bloqueantes /
  3 opcionales / 2 abstenciones** (reviewer de familia distinta a la del implementer); los 2 FAIL del validador
  son **preexistentes con delta 0** probados en un árbol pre-feature. **BLOQUEO declarado (dueño):** el paso b de
  PD-6 y los cuatro cruces reservados (confiar la carpeta del proyecto, copias/despliegue en HOME, emitir
  activación de proyecto CC, activar versiones en el repo real), **no ejecutados**; **cuatro desconocidos
  conservados `unknown` con causa** (PD-8). **Deuda:** `debt.md` RD-1..RD-6 + las fricciones F-3/F-5/F-7 de T5 +
  la deuda de proceso de `closure-suite.md`; preexistente F011 (D-6 de la spec). Contrato: `spec.md` `5e11f2ef…`;
  `plan.md` `953e4ba5…`. Decisión registrada en **ADR-026**. **Siguiente:** `005-011-common-entry`, en orden
  `005-011 → 005-013 → 005-012` (ninguna abierta); el epic-005 sigue en `features-loop` (10/13).

- **005-007-progressive-planning** (2026-10-13, epic 005) — novena feature de epic-005. Transforma un
  objetivo amplio en **el próximo trabajo ejecutable con contexto suficiente**: **planificación
  progresiva** (objetivo y dependencias completos; detalle solo de la próxima tanda) con un **marcador
  cerrado `detail`** (`"next"`/`"planned"`) cuya regla vive en un solo hogar
  (`references/stage-2-specification.md`) y su formato en `planning-contract-draft.md` §4.1 (por
  referencia); **reconciliación del validador** (`cdad_packet.py` `_check_plan_validation_plan`,
  fail-closed y checks mecánicos preservados); **`open-unit`** (subcomando nuevo que abre la primera
  `queued` sin editar el state a mano; ruta `next-unit` de `status`); **materialización legítima del
  informe del architect** (`cdad_result.py` + `artifact-policy.json` admiten el kind `role-report` de la
  interfaz); **detección de despacho por el medidor** (`cdad_context_meter.py` reconoce la invocación
  real de `cdad_delegate.py`, excluye menciones/ayuda); **plantillas** (spec desde el recorrido de uso
  sin «Line coverage ≥ X%»; `feature-plan-template.md` nuevo con ficha + `plan-tasks`); **tamaño de
  unidad por costo total** (cuatro condiciones cualitativas, sin números) y **vínculo reintentos↔unidad**
  en `re-entry.md`. **Gates:** RED→GREEN por unidad (T1..T7), **7 oráculos, 37 passed**; suite completa
  en worktree fijado a `a5cd0c8` **4 failed / 871 passed / 9 skipped / 6 errors** **idénticos al base
  `99e2f2e`**; `make validate` **141 PASS / 2 FAIL** (F011 preexistente). **Review formal única:**
  **2 blocking / 4 optional / 2 abstenciones** (reviewer de familia distinta); **B1** (la tarea `planned`
  sin `depends_on`) y **B2** (falso negativo del medidor ante prefijos de envoltura) **corregidos ya**
  (`282c70a`, `a86278e`); optional y abstenciones a deuda. **BLOQUEO declarado:** la medición de uso con
  la **versión desplegada** (PD-11/AC-7) es acción del dueño → no verde. **Incidente declarado:** el RED
  de review-fix agotó la cota sin entrega (sin efectos) y se reintentó. **Tres defectos de oráculo**
  (T2 fixture, T5 helper, bandera no nombrada) detectados por el gate; el implementer no commiteó GREEN
  no validado. Commits (rango `99e2f2e..92ddd06`): spec+plan `e1b792a`, T1 `7ff19c1`, T2 `09567cd`
  (testfix `7d683c9`), T3 `54eeed6`, T4 `512d913`, T5 `8ac41d6` (testfix `c8e766d`), T6 `594da73`,
  T7 `a59101d`, T8 `c328180`, review `98b3b6a`, review-fix `2cd13a6`/`a86278e`/`e3375e4`/`282c70a`.
  Contrato: `spec.md` `54877103…`; `plan.md` `1f636260…`. **Deuda:** `debt.md` D-1..D-8 (D-1 medición
  desplegada = BLOQUEO del dueño). **Siguiente:** `005-004-claude-code-roles`; el epic-005 sigue en
  `features-loop` (9/10).
- **005-003-orientation-reduction** (2026-10-12, epic 005) — octava feature de epic-005. Entrega
  **orientación acotada al primer despacho legítimo** sobre el proceso de delegación, con contexto
  chico y sin reconstruir preventivamente la historia ni el CLI. **Producto (5 + 5 de tests):**
  subcomando **read-only** `status` en `skills/cdad-cycle/scripts/cdad_packet.py` (`compact-view-v1`:
  proyección determinista del estado operativo, **sin** `stage_history`, límite **16.384 B con fallo
  cerrado** sin proyección parcial, `entry` como mapa explícito, asimetría de raíz relativa
  diagnosticada en la salida); referencia operativa `references/orientation.md`; asset canónico de
  **ejemplos ejecutables** `assets/orientation-examples.json`; `references/project-start.md` §11 (la
  vista primero, ampliar con motivo); bloque aditivo de **resumen del conjunto** (`set-summary-v1`)
  en `scripts/cdad_context_meter.py` + regla del documento multiplexado **R4** y cierre de **D11** en
  `references/context-meter.md`; inventario de capacidades efectivas `references/capabilities.md`;
  y el **contrato aplicable del encargo** (`packet-contract-v1`, T6: `--plan-task` aditivo, sección de
  validación derivada del bloque canónico `plan-tasks` del plan aprobado, referencias al contrato,
  política única de suite en `packets/common.md`, cierre con commit). Tests
  `tests/test_005_003_t{1,2,3,4,6}_*.py` (11/10/9/6/7) + corrección de D11-3 en
  `tests/test_005_002_t4_acceptance.py`. **Gates:** RED/GREEN por tarea (focales 43 passed en la
  corrida del reviewer); **gate de aceptación de la feature PARCIAL, con bloqueo declarado** —
  precondiciones **D11 y R4 cerradas en T3** (entregables de la feature), uso real observado sobre el
  proyecto real (vista `status` = **1.679 B**, claves declaradas, sin historial, `version=UNKNOWN`
  con causa, estado intacto), **pero la aceptación con una sesión real nueva (A1/A2/A6/A9) queda
  PENDIENTE del despliegue** (reservado al dueño, prohibido en el tramo); **suite completa: no
  corrida aún** (se corre una sola vez al cierre, por quien cierra). **Review formal única:** **0
  blocking / 6 optional / 7 abstenciones**, reviewer de **familia distinta** a la del implementer
  (sondas propias: límite que no crece con el historial; registro neutral byte-idéntico sin
  `--set-summary`; resumen con cobertura → `unknown` con causa). **Deuda:** F1 y F4 **corregidos**
  (reconciliación del plan a la spec; referencia hasheada); F2 **propuesto al dueño** (calificador de
  «trabajo pendiente» no implementable con las fuentes declaradas); F3/F4-bis/F5/F6/F7 **a deuda** con
  condición de cierre verificable. Commits (rango `009902b..HEAD`): T1 `2bdf314`/`2bc159a`, T2
  `350aa58`/`5e628de2`(testfix)/`1810370`, T3 `8b5673d`/`48d47f7`, T4 `afd7fd4`/`b6e567b`, T6
  `d805876`/`d45e627`. Contrato: `spec.md` `d630fdf9…`; fila 8 del plan del epic enmendada y aprobada
  (`b22bc687…`). **Siguiente:** `005-007-progressive-planning`, luego `005-004-claude-code-roles`;
  el epic-005 sigue en `features-loop` (8/10).

- **005-002-session-context-meter** (2026-10-11, epic 005) — séptima feature de epic-005. Entrega un
  **formato de medición neutral respecto del runtime y opcional para la metodología** (observado/
  estimado/desconocido) y su **primer adaptador**: un lector de **solo lectura** de las sesiones de
  OpenCode (tokens, lecturas, llamadas de herramienta y primer `resume`, por sesión y por rol).
  **Producto (4 archivos + 4 de tests):** adaptador canónico
  `skills/cdad-cycle/scripts/cdad_context_meter.py` (lector SQLite `?mode=ro`; detección de esquema
  por columnas/tabla requeridas; **fallo cerrado** con diagnóstico que nombra el faltante y sin
  números; hitos separados; corte con borde fijado; tres magnitudes; anotación de aplicación
  referenciada; privacidad), wrapper fino `scripts/cdad_context_meter.py`,
  `assets/context-meter.schema.json` (contrato `context-meter-v1`) y `references/context-meter.md`
  (procedimiento + **límite normativo de 16384 bytes**; **no enganchado en gates**); tests
  `tests/test_005_002_t{1,2,3,4}_*.py`. **Decisiones D1–D12** (registro neutral en asset+reference
  sin gate; adaptador canónico + wrapper; fallo cerrado por columnas; corte con borde fijado; hitos
  separados; tres magnitudes; desconocido ≠ cero; informe de aplicación referenciado; privacidad;
  RO/stdlib/JSON único/determinista; superficie de invocación mínima; claves requeridas y regla de
  cubos). **Review formal única:** **0 blocking · 10 optional · 0 abstenciones**, reviewer de familia
  distinta a la del implementer; los 10 hallazgos → `debt.md` (D1 = `time_relative: 0.0` fabricado).
  **Gates:** RED/GREEN por tarea (T1 7→7; T2 5→12; T3 5/2→19; T4 3/2→22+2 skip); **gate de
  integración real verde** (dos muestras + S-BOOT-04 sobre la base real en solo lectura; store
  intacto); **suite completa 787 passed / 4 skipped** (exit 0, 939,85 s) en un worktree fijado a
  `b1a8add`; `make validate` **142 PASS / 1 FAIL** (F011: drift de las copias instaladas en HOME —
  desviación declarada; resolverla exige **desplegar**, reservado al dueño). Commits (rango
  `7be52d4..HEAD`): `dc6b454`/`eac25ac` (T1), `c192c2d`/`b153cb3` (T2), `9cc1c40`/`fd58199` (T3),
  `2884f67` (T4 RED), `49d27ad` (corrección de tests: defecto detectado por el gate de integración),
  `1dc4e9c` (PD-14 en el reference), `c50d8f3` (cierre), `b1a8add` (review). Contrato: `spec.md`
  `a70f6d50…`; `plan.md` `d373fc4f…`. **Deuda:** los 10 opcionales (D1 primero) + V6/PD-14 (`unknown`
  con causa) + V3/V4/V11 abiertos o declarados; sin CI; sin despliegue ni push (del dueño).
  **Siguiente:** `005-003` (consume este instrumento), luego `005-007` y `005-004`; el epic-005 sigue
  en `features-loop`.

- **005-010-real-opencode-delegation** (2026-10-11, epic 005) — sexta feature de epic-005 y
  **continuación correctiva de 005-009**. El adaptador OpenCode de la delegación externa **completa
  un recorrido real**: contra el runtime instalado, 005-009 era inoperable (bloqueaba el despacho
  por exigir `mode: all`; esperaba una señal durable —un JSON— que solo escribía el binario falso
  del fixture; leía la base real como JSON y lanzaba `UnicodeDecodeError` no capturado; no usaba
  `--standalone`/`--session`/`--auto`). **Producto:** `cdad_delegate_opencode.py` **+477/−139**
  (lector del **store de sesiones SQLite en solo lectura** + correlación por `--session <id>`
  elegido; clasificación por `idle_outcome`; modo de carga por la versión instalada —`mode: subagent`
  es entry no interactiva— + identidad desde la fila durable; invocación con `--standalone`/`--server`/
  `--auto`; `PWD` del destino = raíz del proyecto; I8 con `model_reported`/`session` desde la fila
  durable). **Referencias:** `cli-delegation.md` (+51/−10) y `opencode-delegation.md` (+44/−17;
  tabla de modelos obsoleta → puntero a la única tabla). **Sin cambios:** la interfaz común
  `cdad_delegate.py`, `cdad-generate.py` y `sources/agents/adapters/opencode.md` (INV-2;
  `git diff` = 0 bytes). **Doble de test:** SQLite real chico con el esquema observado (reemplaza
  `sessions.json`) + variantes; migrada la fixture de 005-009. Tests nuevos
  `tests/test_005_010_t{1,2,3,4}_*.py` + `test_005_010_reviewfix.py`. **Decisiones D1–D10**
  (ver **ADR-023, enmienda 2026-10-11**): señal durable real (SQLite `mode=ro`) correlacionada por
  `--session`; fallo cerrado por esquema; `mode: subagent` es entry soportada y la barrera es la
  identidad desde la fila durable (sin fallback); invocación soportada; clasificación por
  `idle_outcome`; observación I8 desde la fila; doble fiel; integración opcional; aceptación PD-10
  en dos pasos; documentación sin valores del VPS. **Review formal única** OK: **1 BLOCKING** (R1:
  `TimeoutExpired` del destino → `transport-error` con hecho material falso; corregido a `timeout`)
  + 6 OPTIONAL; corregidos R1–R4, a deuda R5–R7. **Gate:** focales **19** (1 skip = T4 por diseño)
  + regresión 005-009 **15** (1 skip); suite completa de cierre del orquestador **763 passed / 2 skipped** en un worktree fijado a
  `3e556a8` con el staging por defecto (los commits posteriores solo tocan la prueba de integración,
  omitida por defecto); integración real habilitada **1 passed**; `make validate` **141 PASS / 2 FAIL**
  **preexistentes** (F011, A3), fuera del diff; sin CI. **Aceptación PD-9(a)/PD-10:** recorrido
  real Claude → `cdad_delegate.py` → OpenCode → `receive` → re-entry desde una **instalación
  aislada** de `3c9d3ee` sobre un proyecto temporal (`termination: completed`, recibo `pending`,
  `reconcile: received`, re-entry `VALID`; `evidence/pd10-acceptance.md`). Commits (base `06d0e98`):
  T1 `bfaa338`/`86fedb1`/`ae600eb`, T2 `846f079`/`e268726`/`e6479b5`, T3 `9c467d6`/`15d9f14`,
  T4 `8b4b518`, PWD `fff8b04`/`3c9d3ee`, aceptación `ea4b915`, review `707456e`, review-fix
  `b783044`/`3e556a8`, T4 testfix `890ece2`/`bc056d7`, registro de la integración `49229be`. Contrato: `spec.md`
  `baf195a3…891b`; `plan.md` `4a0d5b2a…9e72`. **Deuda:** R5–R7 (memoria no acotada con `fetchall`;
  numeración del docstring; encoding del URI SQLite) y **paso b de PD-9/PD-10** (confirmación desde
  la instalación global tras el despliegue del dueño). **Siguiente:** `005-002-session-context-meter`
  (pausada, discovery intacto; subetapa `draft`) — **antes de preparar su paquete, registrar la
  aprobación de la versión actual del plan del epic** (pin `996dd7e0…` ≠ `fbb0770b…`); luego
  `005-003`, `005-007` y `005-004`.

- **005-009-cli-delegation** (2026-10-11, epic 005) — quinta feature de epic-005. Un agente
  autorizado puede **encargar un paquete CDAD ya preparado a una sesión de rol en OTRO CLI** y
  recibir su entrega por el flujo CDAD existente, con proyecto, rol, configuración, entrega y
  re-entry verificables. **Producto:** interfaz común `skills/cdad-cycle/scripts/cdad_delegate.py`
  (+298) con **un adaptador por destino** resuelto por convención de módulo (`cdad_delegate_<id>.py`;
  agregar un destino **no** edita la interfaz) + primer adaptador `cdad_delegate_opencode.py` (+589)
  + wrapper `scripts/cdad_delegate.py` (+11) + referencia `references/cli-delegation.md` (+142);
  **reutiliza** `prepare`/I8/ledger/`receive`/`reconcile` y **no crea otro state**. Reconciliación
  del SPAWN GUARD (`SKILL.md`, `sources/roles/orchestrator.md`, `references/claude-code-delegation.md`
  y los 2 orquestadores generados). **Decisiones D1–D10** (ver ADR-023): adaptador por convención;
  reutilizar sin otro state; I8 con configurado/observado/`unknown`; **entrega ≠ gate**; fail-closed
  del modo de carga sin fallback genérico; espera sobre señal durable; configuración portable sin
  valores del VPS; reconciliación del SPAWN GUARD; recorrido real como gate de integración; frontera
  explícita. **Review formal única** OK (0 bloqueantes; 5 opcionales a deuda). **Gate:** focales
  **33 passed / 1 skipped** (skip = PD-10 declarado); suite completa **734 passed / 1 skipped**;
  `make validate` **141 PASS / 2 FAIL** (F011 —**cerrada por el despliegue**— y A3, preexistentes);
  sin CI. Commits (base `9f11b4f`): `1d5c946`, `896637b`, `b483c05`, `6fc958d`/`8f6b812`,
  `d413c0c`/`15c8dab`, `29c8480`; review `1a111ab`/`6f4d5db`; despliegue `a47ed17`. Evidencia:
  `spec.md`/`plan.md`, `discovery.md`, `review.md`, `closure.md`, `tests/test_005_009_t{1,2,3,4}_*.py`.
  **Despliegue:** sucesora `6f4d5db` (perfil `basic`, tres bases; 0 conflictos; 11/11 agentes;
  COHERENT). **Deuda:** 5 opcionales (cota de espera ausente; A3 por prosa del fixture; presupuesto
  ≤ reserva; «no polling loop» vs sondeo acotado; `--packet-id` sin validar en el adaptador);
  `install.sh --check` sensible a `__pycache__`. **Siguiente:** `005-002-session-context-meter`
  (pausada, discovery intacto; subetapa `draft`), luego `005-003`, `005-007` y `005-004`.
- **005-008-project-path-capabilities** (2026-10-10, epic 005) — cuarta feature de epic-005. Alinea las
  **capacidades mediadas por ruta** de los agentes con el **clasificador único** para un proyecto con
  **tests anidados dentro de la implementación** (caso real: Perl/Webmin, implementación
  `webmin-module/module/` y tests en `webmin-module/module/t/`). **Producto:**
  `skills/cdad-cycle/scripts/cdad_packet.py` **+19/−2** (3 hunks): (D1) `_test_patterns` incluye
  `test_files`; (D2) la rama `read` del test-writer reabre el **árbol de tests declarado** después del
  deny de implementación y **antes** de `private` (findLast); (PD-10b) `_validate_policy_document`
  **nombra** el campo extra/faltante conservando el fail-closed. **Sin cambios** en el clasificador, el
  guard CC, el esquema del manifiesto ni la publicación atómica. **Decisiones D1–D7** (fuente única de
  patrones; orden deny→allow→private; sin convenciones globales `**/t/**`/`**/*.t`; comandos del proyecto
  en su lugar canónico, nunca en la política; aceptación por comportamiento observable + recorrido
  instalado; T1 único cambio de producto; frontera explícita). **Review formal única** PASS (0
  bloqueantes; O-1/O-2/O-3 a deuda). **Gate:** suite completa **700 passed / 1 failed preexistente**,
  focales **16/16**, `make validate` **141 PASS / 2 FAIL F011 preexistentes**; sin CI. Commits: T1 RED
  `17d5f9c`, T1 GREEN `17e6184`, T2 RED `aff3a20`, T2 GREEN `8500bf4`, T3 `54fb376`, review `7928650`.
  Evidencia: `spec.md`/`plan.md`, `discovery.md`, `review.md`, `closure.md`,
  `tests/test_005_008_t{1,2,3}_*.py`. **Deuda:** O-1 (VERIFY 1/3/5/6 del dueño y aceptación conjunta con
  005-009), O-2 (errata de superficie de T2), O-3 (`build/staging` local en rojo); F011/A3 preexistentes.
  **Siguiente:** `005-009-cli-delegation` (orden 5; depende de 005-008 para la aceptación conjunta del
  consumidor).
- **005-006-guided-project-start** (2026-10-10, epic 005) — tercera feature de epic-005. Cerrada el 2026-10-10 (ciclo técnico completo; desplegada por instrucción del dueño; la corrida R2 de sesión nueva queda como verificación del dueño).
  Cierra la fricción del arranque: **una instrucción breve basta para una primera
  delegación útil**. Entrega: **procedimiento corto de arranque**
  (`skills/cdad-cycle/references/project-start.md`, referencia nueva) + **entrada
  *boot-at-rest* en el intake** (`sources/roles/orchestrator.md`; agentes regenerados
  byte-parity), cableado con el **CLI instalado** (`$CDAD_INSTALL_ROOT/…`), **dueño
  canónico** del reconocimiento por objeto (PD-13) y **responsable de sincronizar
  `epic_features`** = coordinador de epic (PD-12; escritor único del state = orquestador).
  `README.md` gana una sección corta de arranque guiado. **Sin código de producto nuevo:**
  `cdad_packet.py`/`prepare` **no** cambian (lock de T3). Tareas T1–T5 + review-fix **F1**
  (`SKILL.md:278` → ruta del CLI instalado). **Review formal única**
  `approved-with-conditions` (0 bloqueantes; F2/F3/F5 a deuda; **F4 = condiciones de cierre
  del dueño**). **Gate:** suite completa **680 passed / 0 failed**, focales 31,
  `make validate` **141 PASS / 2 FAIL F011 preexistentes**; sin CI. **Condición abierta
  (dueño):** activación de la versión → `install.sh --check` rc=0, y corrida **R2 real** →
  cierra **VERIFY 5** (PD-16). Commits de producto: T1 `421ddf2`, T2 `4d96905`, T3 `8dd8c09`,
  T4 `fe8d742`, F1 `19d561e`; tests `0c7d951`/`91eaaaf`/`b2740a0`/`485503f`/`3c4b2be`/
  `2b69074`/`934527f`. Evidencia: `spec.md`/`plan.md`, `discovery.md`, `review.md`,
  `tests/test_005_006_t{1..5}_*.py`. **Deuda:** F2/F3/F5; F011/A3 preexistentes.
  **Siguiente:** `005-002-session-context-meter` (por prioridad; depende de la activación de
  la versión nueva, decisión del dueño).
- **005-005-adoption-coherence** (2026-10-09, epic 005) — segunda feature de epic-005,
  continuación correctiva de 005-001. Cierra tres incoherencias y deja verificable la
  procedencia de la instalación. **T1:** el reemplazo (`--replace-packet`) valida el
  **encargo resultante completo** (conservado + corregido) con diagnóstico
  campo/motivo/opción; un `input` conservado inexistente → `rc=2` sin efectos; el
  **camino normal no suma restricciones** (PD-5/INV-4, test focal). **T2:** una sola
  **política de evidencia** (dueño canónico `stage-3-tdd.md` §«Test evidence policy»:
  regresión proporcional; suite completa al cierre; reutilización equivalente con dueño
  en `re-entry.md`; la metodología define la evidencia y **el proyecto declara los
  comandos**), consumidores que remiten sin copiar (13 archivos); **PD-17 de 005-001
  enmendada** con fecha. **T3:** procedencia de la instalación (**variable > registro de
  activación > global**; contradicción **diagnosticada** nombrando `.cdad/activation.json`
  y las versiones; `source_version` en el manifiesto); `review.md` de 005-001 normalizada
  (PD-27→PD-20) y rutas personales fuera del epic-005 (originales en `.cdad/local/`).
  **T4 (cierre):** el instalador declara su versión (`version.txt` en la raíz +
  `source_version` en el manifiesto) y **test de integración en raíz aislada**
  (`prepare` → `--replace-packet` → despacho con el CLI instalado, sin HOME). **Review
  formal única:** `changes-approved` sin bloqueantes (5 opcionales O1..O5; 5
  abstenciones). **Gate:** suite completa **649 passed**, focales/regresiones OK,
  `make validate` **141 PASS / 2 FAIL F011 preexistentes**; sin CI. Commits: T1 `65e887f`,
  T2 `4b990bb`, T3a `6f7363c`, T3b `b4ce4d9`/`1f1cc63`, T4 `9e5215f`; tests `dc66cb2`,
  `3d9e854`, `fd1aaa3`, `012ccac`, `eda293c`. Evidencia: `spec.md`/`plan.md`,
  `discovery.md`, `review.md`, `dispatch-ledger.md`. **Deuda:** O1..O5 y el VERIFY D7
  abierto. **Siguiente:** 005-002 (depende de la adopción de esta versión, decisión del
  dueño).

- **005-001-idle-and-v7-bootstrap** (2026-10-09, epic 005) — primera feature de epic-005.
  Corrige la **circularidad I2** del arranque: el CLI deja de tratar la spec como
  precondición para producir la spec. Entregado: (b) **aprobación de contrato por rol** —
  el **architect** se habilita con la aprobación del **plan del epic** (`epic_history`
  `stage: "epic-plan"`, sin pin, D2); **test-writer/implementer/reviewer** exigen la
  aprobación de la **spec concreta** pineada por `contract_path` + `contract_sha256` (D3);
  (c) **reemplazo** de un paquete preparado y no despachado cuyo contrato cambió
  (`--replace-packet --reason`; obsolescencia verificable PD-8; un `dispatched` sigue
  exigiendo reconciliación; conserva el anterior byte a byte y deja `.superseded.json`);
  (d) **marcadores distinguibles** `approval pending`/`packet obsolete`/`state incoherent`
  con la acción siguiente; (e) `validate-state` acepta el **reposo legítimo** (`VALID: idle`)
  y rechaza el incoherente. **Enmienda T-CORR** (2026-10-09, instruida por el dueño): C1 el
  pin **nombra** el contrato (PD-18/INV-8); C2 el reemplazo **conserva y corrige** el encargo
  (PD-19..PD-24/INV-7: opciones `--input/--read-scope/--write-scope/--invariant/`
  `--expected-output/--evidence`, centinela `-`, pisos obligatorios del rol, mismas
  validaciones, argv mezclado, traza `conserved_fields`/`changed_fields`). **Tareas:** T1–T4
  + T-CORR. **Prueba decisiva PD-17** verde end-to-end. **Review formal única**
  (`review.md`, `changes-required`): 1 bloqueante **B1** (la sección «Reemplazo» de
  `project-execution.md`, declarada por el plan, nunca escrita) **cerrado** con `9468027`
  (+75/−1) y su familia `1faef04` (índice de `SKILL.md`); 6 opcionales B2..B7 a `debt.md`.
  **Gate de cierre:** suite completa **629 passed** (3 segmentos), focales 30 passed,
  `make validate` **141 PASS / 2 FAIL F011 preexistentes**; sin CI. **Versión:** v7
  `ce09ed0`; el primer `prepare` del epic publicó los agentes de proyecto v7 (11/11 hashes).
  Commits: T1 `c885f02`, T2 `0e77e49`, T3 `11e1454`, T-CORR `bfe8edb`, T4 `70df141`; tests
  `e49a1ce`/`7941007`/`66b880a`/`d7355b7`/`3b5c5ec`/`bd65cd6`/`ec8bd48`; spec/plan `71520dd`.
  Evidencia: `spec.md`/`plan.md`, `review.md`, `debt.md`, `dispatch-ledger.md`,
  `handoff-architect-001.md`. **Deuda:** B3 (media, **decisión del dueño**: la raíz v7 viva
  quedó fuera de sync para `cdad_packet.py`) y B2/B4..B7. **Siguiente:** 005-002.

- **epic-003-context-efficiency** (cerrado 2026-10-08) — como **fase de infraestructura del MVP**
  con enmienda (criterio 2 reemplazado por modelos por rol; 5 y 6 con límites declarados).
  Aprobado por el dueño el 2026-10-08; la enmienda se actualizó después con los resultados de
  003-007. Siete features cerradas. Suite de cierre 599 passed en `350a93c`. Ver
  [closure.md](epics/epic-003-context-efficiency/closure.md) y
  [closure-amendment-draft.md](epics/epic-003-context-efficiency/closure-amendment-draft.md).
- **003-007-living-continuity** (2026-10-08, epic 003) — continuidad que **tolera
  documentos vivos**: dos clases de referencia **declaradas por el escritor** (nunca por
  ruta) — `contract` (spec/plan aprobados, `docs/cdad-policy.json`, state con proyección de
  autoridad, aprobaciones) que **bloquea** (`rc≠0`), y `living` (ledgers, `debt.md`, Memory
  Bank, adoption/continuity ledgers, borradores de cierre/enmienda) que solo **informa**
  (`state: changed|missing`, `current_sha256`) y **no** bloquea. Resuelve **T4-REF** y
  **T4-CKPT** (checkpoint de límite con la clave del head → **append** `seq+1`, no
  split-brain; `record` en el body; `begin` divergente sigue cerrado). `fields` proyecta la
  autoridad del state (fallo cerrado al escribir sobre no-JSON o proyección vacía); legado
  pre-003-007 por **comparación** (`legacy: true`, no bloquea). Reconciliación de la regla de
  encargo (unidad despachable) y clases del "Continuity wiring" en `sources/roles/orchestrator.md`
  (agentes regenerados). **Uso real (T3, P9):** v6 bloqueaba por vivos, v7 reanuda los stores
  de 003-004/006/007; bloqueos `contract`/autoridad verificados en copia; rotación real sin
  escrituras. **Sonda 2:** un orquestador regenerado invoca `resume`/`reconcile` sin que se le
  nombren (18 lecturas de orientación antes de `resume`; sin escrituras). **Gate de cierre:**
  66 passed + validadores 141/2 (F011+A3 preexistentes); suite **599 passed** en `1f5fdac`.
  Commits: `b1e56e9` (T1), `f466ed9` (T2), `1f5fdac` (T4), `42f9904` (review-fix F-1),
  `ce09ed0` (cierre T4). **Versión:** la nueva se instaló en raíz aislada y se invocó por
  ruta explícita; **el repo sigue en v6 (`abcd4d3`), la activación de la v7 es decisión del
  dueño.** Evidencia: `spec.md`/`plan.md`, `dispatch-ledger.md`, `continuity-ledger.md`,
  `debt.md`, `evidence/t3/`, `evidence/discovery-probe-2.md`. Deuda: ver "Queued".
- **003-006-runtime-adoption** (2026-10-08, epic 003) — cablea, activa y comprueba las
  herramientas del epic: enlaza la continuidad en `skills/cdad-cycle/SKILL.md`; entrega el
  generador de activación **por proyecto** `scripts/cdad-activate.py`
  (+ `references/runtime-adoption.md` + `.gitignore`) — determinista, no-clobber y con
  contención de ruta (`realpath` estricto bajo `project_root`), **nunca escribe las
  configuraciones del HOME real**; adopta `receive` en el flujo de despacho (staging →
  `receive` → receipt → transición única de state; `receive` no aprueba, single-writer =
  orquestador) y `begin`/`checkpoint`/`reconcile`/`resume` en el ciclo (`trigger` advisory,
  `classify` fuera). Re-adopción **v5** (`d958672`, cierre T1–T3) y **v6** (`abcd4d3`,
  +RU-1/RU-2), con verificación de consumidor; **v6 instalada pero con activación pendiente
  del dueño** (el clasificador de permisos la denegó). **Uso real (T4):** RU-1 (el hook de
  Claude Code resolvía el clasificador desde HOME → fail-closed, defecto de integración
  real no visto por fixtures → fix `5c09770`) y RU-2 (un rechazo dejaba cuerpo huérfano y
  bloqueaba `reconcile` para siempre → rechazo todo-o-nada `abcd4d3`); `receive` real con
  `reconcile = received`, idempotente byte a byte; rotación 3 correcta en sesión nueva
  (`resume` sin re-preguntar). **Límites declarados:** Claude Code = mezcla de versiones
  (skills de usuario ganan a las de proyecto; hooks no corren sin confianza de carpeta;
  mitigación con `--setting-sources project,local`); Codex = catálogo ambiguo (usa la copia
  de proyecto, verificado por contenido; sin adaptador); **T4-REF (deuda alta):** la
  reanudación falla cerrada si cambia cualquier referencia del checkpoint. **Gate:** 567
  passed (926 s) en `abcd4d3`; validadores 141 PASS / 2 FAIL preexistentes (F011 drift de
  HOME, A3 → ANON-1); sin CI. Commits: `a0f2335` (T1), `04ba3d8`/`7ccea01` (T2),
  `d958672` (T3), `5c09770` (RU-1), `abcd4d3` (RU-2); spec/plan `2c36773`. Evidencia:
  [adoption-ledger.md](specs/003-006-runtime-adoption/adoption-ledger.md),
  `dispatch-ledger.md`, `debt.md`, `docs/runtime-adopted-version.md`,
  [closure-amendment-draft.md](epics/epic-003-context-efficiency/closure-amendment-draft.md).
  Deuda: ver "Queued".

- **003-004-context-continuity** (2026-10-07, epic 003) — CLI determinista **read-only**
  `skills/cdad-cycle/scripts/cdad_continuity.py` (+ wrapper + `continuity-checkpoint`/
  `active-record` schemas): `begin`/`checkpoint` **write-ahead** (escriben solo bajo
  `.cdad/executions/<id>/continuity/**`; `begin` idempotente: cuerpo idéntico al head →
  no-op rc 0), `reconcile` (write-ahead/posterior sobre receipts/journal 002, dispatch I8
  y state; `dispatched-unknown` ≠ fracaso ≠ repetir), `resume` (proyección de memoria
  activa on-demand, `--role`, `--max-bytes` default 16 KiB, falla cerrado sin truncar) y
  `trigger` (señal; `unknown` sin contador y límite, nunca un límite fabricado). Tres
  contratos con nombre: `continuity-checkpoint-v1`, `reconcile-v1`, `trigger-v1`. **El CLI
  nunca escribe `docs/.cdad-state.json`** (single-writer = orquestador) y `continuity`
  **consume** el receipt 002 como oráculo, no materializa. T1–T3 con review-fix (T1
  familia B1/B2/O2; T2 A/B/C/D/E1), T4 = adopción real. **Uso real honesto:** RU-1
  (defecto de integración real que los fixtures no detectaron → review-fix `0005128`),
  RU-1b (idempotencia real: `no_op: true`) y RU-2 (rotación real T3→cierre: reconstrucción
  sin preguntar al usuario; `reconcile` = `dispatched-unknown`, P2/P3 demostradas).
  **Gate:** 523 passed (786 s) en worktree fijado a `6110e07`, stdin cerrado; `validate-consistency.sh` 142 PASS / 1 FAIL (F011 `validate-subagents.sh`, preexistente: `install.sh --check` contra copias instaladas; `validate-odoo-specialization.sh` PASS en árbol limpio); validadores con los 2
  FAIL preexistentes (F011). Commits de producto: `9705aec`/`209643f` (T1),
  `02bc021`/`00dd557` (T2), `6c03533` (T3), `0005128` (RU-1), `6110e07` (evidencia T4). Evidencia:
  `continuity-ledger.md`, `debt.md`, `dispatch-ledger.md`. Deuda: ver "Queued".
- **003-003-progress-guards** (2026-10-07, epic 003) — guard **determinista read-only**
  `skills/cdad-cycle/scripts/cdad_guard.py` (+ wrapper + `guard-trace`/`guard-event`
  schemas): `classify` (repetición sin progreso P1 y polling P2/P7 sobre `trace-v1`),
  `preflight` **consultivo** (P3/D6/O2; enmienda del dueño: salir de la raíz habilitado
  por defecto, `deny` solo explícito, `unknown` sin destino resoluble),
  `record`/`budget` **durables** bajo `.cdad/executions/<id>/guards/**` (P4, create-
  exclusive) y **escalado con tabla cerrada evento→acción** (P5/D5). El juicio queda en
  el orquestador; nunca escribe `docs/.cdad-state.json` ni repite efectos (reconcilia
  receipts de 002). T1–T3 con review-fix (T1 familia de 3 bloqueantes; T2 F1 5 puntos;
  T3 F1/F2/F3), T4 `approved` (0 bloqueantes; 4 mutaciones eliminadas). **T5 — uso real
  honesto:** el guard **no** detectó los C1/C2 reales (los detectó el orquestador); 2
  falsas alarmas por digest de progreso de **grano grueso** (conjunto de rutas). El
  dueño corrigió (2026-10-07): C1/C2 = **artefactos del despacho con `opencode run`**,
  no del entorno nativo → **G2 retirada**, **G1 a media**; las falsas alarmas siguen
  siendo deuda media. Versión operativa **`939f501`** (raíz aislada
  `<home>/.cache/cdad-adopted-939f501`). Evidencia: suite de cierre **487 passed** (1442 s, worktree fijado) en `87d91b2`, focales T4 12/12;
  `guards-ledger.md`, `guards-incidents-observed.md`, `debt.md`, `evidence/t5/`,
  `dispatch-ledger.md`. Deuda: ver "Queued". Referencia de aplicabilidad: `skills/cdad-cycle/references/progress-guards.md`.

- **epic-004-single-source-planning** (cerrado 2026-10-05, 3 features) — sus tres
  features `004-001` (2026-09-29), `004-002-project-execution-bootstrap`
  (2026-10-03) y `004-003-planning-procedures` (2026-10-05) cerradas; cierre e
  integración en
  [closure.md](epics/epic-004-single-source-planning/closure.md) con las
  excepciones E1–E4 registradas (validadores con 2 FAIL preexistentes; gate de CI
  resuelto como inexistente; paso 8 de recepción derivado a 003-002). Garantías de
  003-001/003-005 preservadas; **epic-003 no se cierra acá**.
- **003-002-artifact-tools** (2026-10-06, epic 003) — CLI de recepción,
  materialización y evidencia sobre el runtime de paquetes v2. Entregado:
  `receive`/`validate-receipt` (persistencia atómica e idempotente de bytes
  originales; una finalización por execution/packet; retry byte a byte),
  `materialize` (política de artefactos: raíz permitida por `artifact_kind`, target
  exacto declarado en la autorización; create-only/CAS; journal; `approval_effect`
  siempre `false`) y `run-python-unittest`/`validate-run-evidence` (solo
  `python3 -m unittest`; snapshots before/after; `valid-current` exige exit 0,
  tests>0, alguno no skipped, cero failures/errors/runner exceptions, árbol no
  mutado y contract vigente). **Recibo mecánico que nunca aprueba**
  (`semantic_status` siempre `pending`); **un solo escritor del state: el
  orquestador**; protocolo de materialización en `references/re-entry.md`. T1–T4
  cerradas con review-fix en las cuatro (T1/T2 1 ronda; T3 3 rondas hasta el
  remedio de **clase fail-closed**; T4 1 ronda), incluida la calibración de la
  review del dueño. **Primer uso real del flujo en este repo**
  (`receive`+`materialize`, bytes idénticos, idempotente) + smoke desde el producto
  instalado en raíz aislada. Evidencia: suite **439 passed** (`d7ffbcc`);
  `review-t1..t4*.md`, `supervision-record.md`, `dispatch-ledger.md`. Deuda: ver
  "Queued".
- **004-003-planning-procedures** (2026-10-05, epic 004) — planificación y
  revisión de planes como procedimientos de roles existentes. Entregado:
  contract-kind `draft-plan` de primera clase que **no aprueba** (guard de forja
  `approved-*`+`plan_version`; emisión con sha/versión, sin marca de aprobación);
  subfase `plan-review` del reviewer con pairing bidireccional
  `draft-plan`⇔`plan-review` (solo reviewer) y fuente de rol generalizada; checks
  mecánicos de plan (productor/consumidor, ciclo, contrato incompatible,
  paralelismo inválido) en `prepare`; plan de validación por unidad obligatorio
  (`planning-contract-draft.md` §4.1, referenciado por `stage-2-specification.md`);
  regla de equivalencia/re-entry dueña única en `references/re-entry.md` (G1–G3).
  **T1–T5 y T7 cerradas; T6 condicional** (F4 fuera del camino feliz,
  `test_roots:["tests"]` → deuda para el primer consumidor Go). **Brecha D8
  cerrada:** primer paquete v2 del architect (`approved-epic-plan`) + replan de
  003-002 (F1/F2 aplicados; F3–F6 abiertos al dueño de 003-002). **AC-7 eximido
  por decisión del dueño** (`make validate` 141 PASS / 2 FAIL preexistentes:
  F011-A drift de mirrors `$HOME`, F011-B A3). Evidencia: suite completa **364
  passed** en `287f6c7`; instalación aislada `install.sh --check` PASS (303
  grupos); 35/35 tests mapeados a postcondición (`test-audit.md`);
  `closure.md`, `supervision-record.md`, `dispatch-ledger.md`. Modelos:
  architect/implementer/scribe `mofgw/deepseek-v4.1-flash`; test-writer/reviewer
  `mofgw/glm-5.3-flash` (familia ≠ implementer). Deuda consolidada en
  `closure.md` (T1 F3–F5, T2 O1–O3, T4 F-C/F-E, T5 F4–F6, O-A…O-H, T7→003-002
  F3–F6, F011-A/B); **límite declarado:** PD-5/PD-6 sin enforcement ejecutable.
- **004-002-project-execution-bootstrap** (2026-10-02, epic 004) — cerrada el 2026-10-03 (segunda mirada de Codex: 6 hallazgos registrados como deuda en `specs/004-002-project-execution-bootstrap/debt-second-look.md`; F4, alta: tests co-ubicados); paquetes v2,
  política por proyecto, agentes derivados por proyecto y guard dinámico. Lo
  construido: `docs/cdad-policy.json` como única política editable
  (`schema_version`/`path_policy`/`temporary_roots`; ningún rol la edita —
  spec.md:47,61); modos de `prepare` `--propose-policy`/ordinario/
  `--resume-packet`/`--reconcile-policy`/`--record-dispatch` (spec.md:33-41,
  plan.md I1–I11); contexto v2 durable en
  `.cdad/executions/<id>/execution.json` e intentos en `dispatches/<attempt>.json`
  (spec.md:48-51) con identidad independiente de runtime/modelo/sesión (PD-4);
  agentes OpenCode `.opencode/agents/` derivados + manifiesto (I9) y guard
  Claude Code que carga la política del proyecto (I10); `path_policy.private_paths`
  (P-1); regla general de límites (L-1) en los 22 prompts generados; corte C que
  congela 69 paquetes v1 y publica la ejecución v2
  `exec-004-002-project-execution-bootstrap-001` (cut-c.md:6-13,96-115). Walkthrough
  real PD-13 en `t7-live-walk.md` (C1 lectura y C2 en sesión Claude Code 2.1.285,
  §2–§5). **Decisiones del dueño:** D1–D6 (owner-decisions-2026-09-29.md) — solo
  hacia adelante, sin migración (D2); registro por intento con unknown=null (D3);
  architect standalone legacy (D4); agentes locales OpenCode + guard dinámico (D5);
  recorrido real de la propia feature (D6). Política materializada tal cual la
  propuesta (owner-decision-policy-2026-10-01.md); instalación aislada para el
  corte, sin tocar `~/.claude`/`~/.config/opencode`. P-1/R5 (owner-decision-p1-2026-10-02.md):
  `private_paths: ["tests/.sensitive-patterns.local"]`, política aceptada
  `9ffb7d16…`; R5 (~252 ms/llamada vs 32 ms legacy, N=20, `discovery-001`)
  **aceptado sin caché**. **Limitaciones declaradas:** W-2 grep/glob en OpenCode se
  evalúan por el patrón de búsqueda, no por ruta (t7-live-walk.md §3; guía §7:136-137);
  W-3 `edit`/`write` no acotados en vivo en OpenCode 2.0.16 (guía §7:133-136;
  supervision-record.md:239); en Claude Code el guard media solo implementer y
  test-writer — architect/reviewer/scribe quedan por instrucción + auditoría
  (guía §1:33-34; t7-live-walk.md §6); `Grep` sobre carpeta padre, glob best-effort
  y bash sin acotar (guía §1:35-38). **Evidencia:** T1 suite 163 (`2ca91f9`), T2 199
  (`6cea734`), T3/T4 261 (`903a3c4`), T5/T6 284 (`28324af`), W-2 307 (`0477be6`),
  L-1 310 (`717e6a7`), P-1 329 (`9c92350`); reviews T1–T5 + review-014 del conjunto
  (supervision-record.md). Último commit de producto/postura honesta: `c596e7a`
  (F-SET-3, guía coherente con W-3). Deuda: ver "(4) pendientes".
- **004-001-canonical-runtime-artifacts** (2026-09-29, epic 004) — los 22
  agentes pasan a salidas declaradas del generador determinista
  (`scripts/cdad-generate.py`, fuentes canónicas en `sources/`, staging +
  manifest) y el instalador despliega solo desde staging (PD-18) con
  propiedad de archivos (PD-6/7/8). Política bash derivada de la fuente
  canónica (PD-1) con listas FORBIDDEN retiradas por decisión del dueño
  (`80f9b90`) y assertions de garantía con trazabilidad (PD-10). Baseline
  PD-13 pre-generación y techo del bloque estático parametrizado (PD-19).
  Recorrido de capacidad vivo: 5 roles, 39 llamadas, 0 denegaciones — por el
  camino legacy; el ciclo con paquetes se verifica en 004-002. Evidencia:
  criterios 1–7 (1–3 reproducidos por el orquestador) en
  `docs/specs/004-001-canonical-runtime-artifacts/closure.md`; suite 132
  passed tras `5e12c0f`; PD-17 T1–T7 (T4/T5 consolidados) en
  `epics/epic-004-single-source-planning/c0-dispatch-record.md`; reviews 1–7
  más la externa GPT sin bloqueantes abiertos.
- **opencode-read-map-and-steps** (ciclo liviano, 2026-09-29) — corrige el mapa
  `read` del test-writer OpenCode (catch-all deny inyectado por el generador: 0
  lecturas exitosas de 36) y declara el techo `steps: 300` una sola vez en la
  fuente del adaptador. RED/GREEN por roles OpenCode (GLM), review independiente
  de Claude sin bloqueantes; instalado y probado en vivo antes/después. Incidentes,
  desviaciones y follow-ups: `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md`.
- **003-005-claude-code-packets** (2026-09-18, epic 003) — `cdad_packet.py
  prepare` más el camino de paquete en los agentes de Claude Code. pytest
  52/52, 3 validadores PASS en raíz aislada, review-2 APROBADO-COMENTARIOS.
  Commits: 72a7e82..f6396f1 (+ cierre).

- **003-001-role-packets** (2026-09-18, epic 003) — paquetes canónicos por
  rol/subfase con `cdad_packet.py`, schemas, métricas y entrypoints
  instalados. Guard de solapamiento del instalador cerrado también para la
  invocación por symlink. Evidencia: pytest 33/33, 3 validadores PASS en raíz
  aislada, review-4 APROBADO-COMENTARIOS. Commits finales: da48f3c, 641f3b8.

- **cdad-010-opencode-permissions** (2026-09-13) — delegación a sub-agentes
  cdad-* reparada en OpenCode: 10 agentes task-ables vía `permission.write:
  ask` anidada (palanca de clasificación, no evaluable en runtime — regla de
  vigilancia en systemPatterns), bloques autocontenidos catch-all-first
  (findLast), cero `ask` en runtime, allowlists bash por rol con pares
  `X*`/`rtk X*` (ADR-009) derivadas del stack por generador + install.sh
  (P5), `"find *": allow` eliminado (backdoor -delete/-exec), globs de
  lectura de tests colocados completos (16), política de enforcement del
  dueño + definición operativa de "vector directo y evidente" en
  systemPatterns. Evidencia: run-checks 217/0, 3 validadores PASS, probes
  G1-G16 con output pegado, cero ask/permission=write en logs. Review
  APROBADO-COMENTARIOS. Commits: b352bf6..a1d37a7. Bucket de hardening
  pendiente: matching de compuestos (premisa corregida N1), find * global del
  usuario (N4), solape de globs de dominio Odoo.

- **fix-path-guard-colocated-tests** (2026-09-04, sin ciclo formal — ver
  nota de proceso en activeContext.md) — `scripts/claude-code-path-guard.sh`
  reconoce tests colocados (Go `*_test.go`, JS/TS `*.test.{js,ts,mjs,cjs}` /
  `*.spec.{ts,js}`, Python `test_*.py`) además de `tests/**`. Fix de un
  proyecto cliente sincronizado a la canónica, más el lado inverso no
  reportado:
  implementer/implementer-odoo ahora bloquean edición de tests colocados
  (gate anti-trampa). Factorizado en `TEST_FILE_GLOBS` + `is_test_file()`.
  Verificado 19/19. Commit: `0fd023f`.
- **epic-002-cdad-audit-fixes** (2026-09-02) — 12 features corrigiendo los
  11 bloqueantes + 10 medios de `findings/audit-consistencia-2026-09-02.md`
  (auditoría de consistencia de toda la metodología, agentes y skills).
  HITL delegado por Pablo ("actuá como hitl, tomá las mejores decisiones").
  Highlights: bash allowlist calibrada en test-writer/implementer (fuga que
  esquivaba el path-scoping, calibrada para no perder capacidad legítima
  por pedido explícito del dueño); guard anti-bias extendido a
  cdad_model_claude (premium tenía reviewer==implementer=opus); taxonomía
  del reviewer unificada (4/4 en addyosmani); orquestador Claude Code
  reparado (mecanismo de delegación + resolución de stack); contrato de
  veredicto (Bucket/Abstenciones) llevado a los 4 agentes reviewer;
  contradicción property tests resuelta + disciplina "RED verifica
  requerimiento, no maximiza cobertura"; `tests/validate-consistency.sh`
  nuevo (124 asserts) verificando todo lo anterior; cierre retroactivo de
  epic-001-superpowers-gaps (nunca había tenido closure.md formal). Detalle
  completo: `docs/epics/epic-002-cdad-audit-fixes/plan.md` y `closure.md`.
- **cdad-009-parallel-dispatch** (2026-09-02) — § "Despacho paralelo" en
  stage-3 (árbol, precondición cdad-008, owned/do-not-touch, integración
  final del orquestador, state file solo orquestador, wave dispatch default)
  + subsección en sub-agent-strategies. RED 9/9, GREEN 15/15 (H1 bug de
  oráculo ERE corregido), review aprobado. Cierra el conjunto
  superpowers-gaps (cdad-004..009). Commits: 401e9d5, 59eb932.
- **cdad-008-granular-planning** (2026-09-02) — "Planning de features
  complejas" en stage-2 (tamaño de tarea, Consumes/Produces, plan=contrato
  no implementación) + architect produce plan.md + AP-19. RED 12/12, GREEN
  17/17, review aprobado. Commits: 8db3286, 2413253.
- **cdad-007-systematic-debugging** (2026-09-02) — stage-debugging.md (ley de
  causa raíz, loop rojo = RED, hipótesis rankeadas, 3+ fixes → ADR) + AP-18 +
  enlaces en SKILL/stage-3/stage-5. RED 16/16, GREEN 23/23, review aprobado.
  Commits: cfe5948, 9a70295.
- **cdad-006-git-safety-close** (2026-09-02) — §5.6 "Cierre de la branch
  (git safety)" en stage-5-merge: entorno+guard submodule, base confirmada,
  menú fijo, discard literal, provenance; AP-17. RED 13/13+guard, GREEN
  19/19, review aprobado (H1 cita §5.6 fixeado). Commits: baba7cf, 0824503,
  be88880.
- **cdad-005-receiving-feedback** (2026-09-02) — protocolo anti-sicofantía
  (reference receiving-feedback.md + transmisor íntegro en stage-4/handoff +
  AP-16 + reconsideración del reviewer con steelman/reversals). RED 22/23,
  GREEN 23/23, suite 121/121, cdad-004 10/10, review aprobado 0 bloqueantes.
  Commits: b626929 (spec+RED), 4e8aa6f (GREEN), 6398cc9 (review).
- **cdad-004-lint-gate** (2026-09-02) — `make lint` (pre-commit-vauxoo) como
  4º target del contrato odoo-make-env + evidencia obligatoria en review.
  Commits: 586a244 (spec+RED), 46d71e2 (GREEN), 3020a09 (fix test stale),
  ef08084 (fixes review), bbccdc9 (review.md).
- **cdad-003-odoo** (2026-08-28) — especialización Odoo de CDAD (ver
  docs/specs/cdad-003-odoo/). Previa al bootstrap de este Memory Bank.

## Queued

- **epic-006 — cola y pendientes del dueño:** **006-003-installer-single-profile-delegation-config**
  (instalador siempre `basic` y sin mapa de modelos —reemplaza ADR-007—, plantilla de config de delegación y
  credencial del servidor, y verificación de familias del reviewer) y **006-004-active-decisions-table**
  (sección «Decisiones vigentes» del Memory Bank). **Redespliegue en HOME pendiente de la orden del dueño**
  (lo instalado es `6978709`, 006-001 completo redesplegado el 2026-10-17, y **no** incluye 006-002); **AC-7** (recepción real del
  consumidor y declaración de `mode: "service"` en sus configs) (PD-6 de 006-001 en `mode: server` quedó resuelto después de su cierre: 3 despachos concurrentes `completed`, `execution.md`).
- CI del repo (GitHub Actions) — deuda de bootstrap.
- Dogfood pendiente: make lint (H3 cdad-004), §5.6 con worktree real,
  receiving-feedback con bloqueantes reales, stage-debugging con bug real,
  despacho paralelo con 2+ dominios disjuntos.
- **Primer consumidor Go/co-ubicado:** F4 (scopes del test-writer derivados solo
  de `test_roots`) — T6 de 004-003 quedó condicional.
- **003-002 — deuda priorizada:** clasificar `README.md` en la política (brecha,
  decisión del dueño; el front-door no descubre `scripts/cdad_result.py`);
  ejercitar `observation_status=unknown` y el CAS de Memory Bank (el primer uso
  fue create-only); whitelist de `argv` más estricta de lo necesario (`--locals`,
  `-c`); O1–O3 de T2/T3 y R4/R6 de T1.
- **003-004 — deuda priorizada:** T3-O1 (perfil 200k extrapolado a cualquier límite
  entero; falta nombrar el perfil o documentar la regla) y T3-O2 (enteros sin sentido
  producen señal definitiva; deberían dar `unknown`); V1/V3 (tokens por paso vs
  acumulados y límite observable no verificados → `trigger` casi siempre `unknown`);
  rollback/replay de un head viejo y tamper autoconsistente no detectables (sin firma ni
  contraste de `seq`); **RU-2a (media):** adoptar `cdad_result receive` en el flujo de
  despacho (hoy `reconcile` solo puede dar `dispatched-unknown`); **RU-2b (baja):** el
  checkpoint no incluye HEAD ni timestamp de emisión; T3-N1..N7 y T2 nits; F011/A3
  preexistentes (ajenos a la feature).
- **003-003 — deuda priorizada:** G1 (media) lector por runtime (OpenCode primero) (lanzamientos desacoplados ⇒ `unknown`; señal de fin de sesión sin entrega;
  digest de progreso por contenido); calibración de severidad del preflight/`read_scope`
  con uso real (decisión del dueño); T1 F1 (traceback no-UTF-8, fail-closed); T1
  F2/O2/O3a-c, T2 O-A/O-C/O-D, T3 O3/O4 + `budget` con id absoluto, T4 O1–O3/N1–N3;
  2 FAIL preexistentes de validadores (ajenos a la feature).

- **003-006 — deuda priorizada:** ~~T4-REF (alta)~~ y ~~T4-CKPT (media)~~ **resueltas en
  003-007** (clases `contract`/`living`; append de checkpoint); ANON-1 (media, rutas absolutas
  locales en `docs/runtime-adopted-version.md` + A3 preexistente); T2-O1/O2/O3/TOCTOU,
  T3-O1/O3/O4, RU1-H4/H5, RU2-F4/F6, T1-F2, T2-SCOPE.
- **003-007 — deuda priorizada:** **MIX-V6V7 (media)** la v6 leyendo un checkpoint v7 con
  `fields` digiere el archivo completo y falla cerrado (usar una sola versión del CLI por
  ejecución; documentar en la adopción de la v7); **R2-STAGE (media)** las aprobaciones que
  solo constan en `stage_history` no entran en ningún digest; **POLICY-CLASS (media)** clases
  por defecto en la política, bloqueado por el esquema estricto de `docs/cdad-policy.json`;
  **T2-R1 (baja)** un `begin` idéntico tras un append de su clave da `rc≠0` en lugar de
  no-op; **CKPT-FORK (baja)** forks de checkpoint mismo-key no detectados; **T1-N1/N2/N3,
  T2-N1, T4-F2, FLAKY-002-T3 (bajas)**; F011/A3 preexistentes (ajenos a la feature).
- **epic-003 — decisiones del dueño** (`closure-amendment-draft.md`): (1) cerrar con la
  enmienda: aprobado y **aplicado** el 2026-10-08. (2) La v6 (`abcd4d3`) fue
  **activada por el dueño** el 2026-10-08 (`cdad-activate.py`; agentes v6 publicados por el
  `prepare` de 003-007). Queda pendiente activar la versión de cierre de 003-007, decisión
  del dueño. (3) Claude Code: confianza de carpeta (`~/.claude.json`) y retiro o
  actualización de las copias viejas de HOME. (4) Prioridad de la deuda: lector de
  sesiones, medición de contexto, CI, ANON-1.

## Blocked

_(ninguna)_

---

Última actualización: 2026-10-18

- 2026-10-17 — 006-001-opencode-concurrency-reliability cerrada (epic 006, primera feature): **el modo de
  ejecución de la delegación OpenCode pasa a ser explícito y verificable** —`server` | `service` |
  `standalone`—, con preflight de servidor y de servicio, **procedencia por intento** en el I8 sin cambiar el
  esquema, **espera proporcional** (cero lecturas con el cliente vivo) y **recuperación que conserva la
  correlación y no re-despacha**; con el servicio vivo **ningún** camino abre un `standalone` (INV-10) y la
  versión del servicio se comprueba por una **proyección de una sola clave** del registro (D-11: sin red, sin
  contraseña, sin URL, fallando cerrado). Gates: RED→GREEN por unidad (T1 14/4 → focal 18; T1b 16 → focal 16;
  T2 8/4 → focal 12; T3 probado por mutación → focal 2) y **review formal 3 bloqueantes / 5 opcionales /
  3 abstenciones** con los tres bloqueantes **corregidos** en review-fix (`17a7ca1` / `161c9ff`) y **re-review
  5 de 5 cerrados, 0 bloqueantes**; **suite de cierre 1 failed / 1079 passed / 5 skipped**, la falla una
  instancia de **DT-9** (cota de 2 s del fixture bajo carga; aislada verde 5/5). **PD-6 en BLOQUEO declarado**
  (concurrencia real en `mode: server`: falta la credencial del dueño) y **AC-7 pendiente del dueño**; la
  **eliminación de la contención no se demuestra**. **Desplegada en HOME el 2026-10-17** con perfil `basic`
  (`install.sh --check` PASS, 391 grupos), con **redespliegue pendiente** tras el review-fix. Deuda:
  DT-3/DT-6/DT-7/DT-8/DT-9, O3–O5 y O5-RF, más la deuda del CLI `receive`/`kind` (dos veces) y la falta de una
  vía para **fallar** un paquete despachado. Decisión propuesta en **ADR-031**. **epic-006 sigue abierto**
  (`features-loop`): **1/4 en `done`**, con **006-002, 006-003 y 006-004 en cola**. **Siguiente:**
  `006-002-delegation-by-layer` (se abre al cerrar 006-001).

- 2026-10-14 — **epic-005-real-operation cerrado** (14/14 unidades, cada una con su cierre y su
  evidencia): «Operación real y medición de contexto». **Versión de referencia:** producto del repo
  `d3b9ccd` e instalación de HOME `29a4805` (`install.sh --check` PASS, desplegada por el dueño el
  2026-10-14), con cero diferencias de producto (`git diff --name-only 29a4805..d3b9ccd` = solo
  `docs/epics/epic-005-real-operation/execution.md`); el servidor de OpenCode no se reinició y los
  derivados del repo siguen en `DRIFT` (pierna `project`) hasta el próximo `prepare` (deuda RD-a).
  **Criterios:** 1 ✅; 2 ✅ en la parte verificable, con límites declarados (RD-a; D6 de 005-002;
  MIX-V6V7 de 003-007); 3 ✅ como las secciones citadas (005-003 §9; 005-007 §7; 005-011 AC-6/AC-7), sin
  documento consolidado aparte; 4 ✅ (suite de cierre del orquestador en worktree fijado al commit de
  cierre); **5 ❌ no ejecutado** (aceptación conjunta del consumidor: arrastra la **R2 real de 005-006** y
  los **VERIFY 1/5/6 de 005-008**). El cierre **no implica publicar**: el saneamiento de contenido está
  hecho (`a367b8c`, `29a4805`), la decisión del dueño es publicar con **historial nuevo** y el historial
  privado se conserva para la trazabilidad de la evidencia. **Prioridades de la planificación siguiente:**
  adopción de versión entre ciclos (RD-a); state operativo compacto con historia recuperable (RD-b); y
  reducción proporcional de instrucciones y preparación, medida en desarrollos reales y separando la
  coordinación del desarrollo (incluye un recorrido liviano para tareas simples). La **HITL delegada
  vence al cerrar el epic y no se hereda**. Ver
  [closure.md](epics/epic-005-real-operation/closure.md).

- 2026-10-14 — 005-012-transition-registration cerrada (epic 005, 13.ª y **última** feature): **una operación del
  CLI que registra la decisión explícita del orquestador sobre una transición** —entrega, gate, avance, cierre,
  entrega tardía y **disposición de un despacho sin recibo**— con la evidencia referenciada exigida, los digests
  **derivados** por el CLI, la **identidad por contenido** (payload canónico con los insumos con efecto), la
  **vigencia estructural** por el pin que **nombra los bytes actuales** y un **cierre que comprueba antes de
  aplicar** y tiene salida cuando el despacho no vuelve. Sin edición manual del state: de las **30 entradas** del
  tramo, **24 las registró la operación** y las manuales quedaron declaradas. Gates: RED→GREEN por ficha (T1 15,
  T2 14, T5 5, T3 8 —con **bloqueo declarado 7/8** por un defecto del **fixture**, resuelto por testfix sin tocar
  aserciones—, T4 7, T6 3; T7 docs-only) y regresiones declaradas verdes; **review formal única 2 bloqueantes /
  7 opcionales / 3 abstenciones**, con **B1** (PD-6 no aplicada a `closure`), **B2** (identidad que tragaba
  invocaciones distintas) y **B3** (reaprobación tras enmienda obligada al registro manual) **corregidos ya** —
  B2 y B3 con **enmienda del contrato** primero y RED antes del GREEN—; **T8 APROBADO** (AC-1..AC-4 con el CLI real
  sobre proyectos descartables, AC-1 con **8 invocaciones rc=0** y **7 entradas** sin edición manual) y **repetido
  sobre el commit final**; suite de cierre **1024 passed / 4 skipped** en worktree fijado a `6fd515d` (`make
  validate` 155 PASS / 1 FAIL, F011 preexistente). Deuda `D-1..D-16` (D-9 retirada) consolidada en `debt.md` +
  opcionales/abstenciones de la review + el heartbeat externo `da3612a` + los dos digests escritos a mano y
  corregidos + el **despliegue pendiente de 005-013 y 005-012**. Decisión en **ADR-029**.
  **epic-005-real-operation sigue abierto** (`features-loop`): **13/13** unidades cerradas, **ninguna en cola**;
  quedan el **gate de saneamiento antes de publicar**, el **despliegue** (dueño) y la decisión del dueño; el
  proyecto queda **en reposo**.
- 2026-10-14 — 005-013-unit-contract cerrada (epic 005, 12.ª feature): **el contrato de una unidad es una
  proyección generada del plan, pineada por digest**, con **fallback declarado** al plan completo cuando la
  unidad no se localiza sin ambigüedad; la unidad se localiza **estructuralmente** y las anclas se declaran en
  el activo del producto. Las consecuencias se clasifican por **identidad y clase de parte** (nunca por prosa):
  `current` / `impact` (journal durable idempotente; decide el orquestador) / `impeded` (**sólo** por
  autorización retirada, con la salida nombrada); la **recepción y el resume** validan contra la proyección
  **registrada**, no contra el plan vivo. Gates: focales T1 **14 RED por aserción → 15 verdes** (luego 18 con el
  review-fix de B1) y T2 **15 RED → 15 verdes**; regresiones declaradas **77, 59 y 21 verdes**; review formal
  única **1 bloqueante / 5 opcionales / 1 abstención** — **B1** (reescritura silenciosa de una proyección
  publicada por colisión de `--out-dir`) **corregido ya** como escritura create-only (focal T1 18 verdes),
  **O1** corregido como errata, **O2..O5** a deuda, abstención resuelta corriendo T4; gate T4 **aprobado** con la
  prueba decisiva del CLI real en las **tres formas de plan**; suite de cierre **960 passed / 4 skipped** en
  worktree fijado a `7ab16ba`; `make validate` 155 PASS / 1 FAIL (F011 preexistente). Deuda `review.md` O2..O5
  + spec §8 D-1..D-3 + acotamiento de la fila 13 (b) + datos para 005-012 + despliegue pendiente. Decisión
  propuesta en **ADR-028**. **epic-005-real-operation sigue abierto** (`features-loop`): **12/13** unidades
  cerradas; resta **005-012**. **Siguiente:** `005-012-transition-registration`, en orden `005-013 → 005-012`.
- 2026-10-14 — 005-011-common-entry cerrada (epic 005, 11.ª feature): **la entrada al proceso es la vista
  compacta `status`**, antes de leer el state o explorar, en las dos skills y en el **prompt del agente
  orquestador** (T2b, tras medir que en OpenCode la entrada real es el prompt, no la skill); la **raíz relativa**
  se unifica en `cdad_packet.py` (el diagnóstico C4 de 005-003 queda superseded, con sus dos oráculos
  declarados); y la vista **nombra la pata que diverge** con su resolución solo si es la verificada, y con un
  paquete `prepared` nombra **despacharlo**. Gate T4 **aprobado con AC-6 parcial declarado**: AC-7 CUMPLIDO
  (primer `Agent` 23 → **14**; salida previa 105 mil → 54 mil car., −49 %) y AC-6 CUMPLIDO EN PARTE (skill en la
  llamada 1, `status` en la 3 en vez de la 21, despacho 71 → **59**, −17 %; la lectura del state completo en la
  llamada 2 queda como brecha con causa identificada). Review formal única **0 bloqueantes / 5 opcionales /
  2 abstenciones**, con **OP-1 y OP-2 corregidos** antes del despliegue (`362ce3a`). Suite de cierre **927
  passed / 4 skipped** en worktree fijado a `8ec574d`; `make validate` 155 PASS / 1 FAIL (F011 preexistente).
  Deuda `debt.md` OP-3..OP-5 + **RD-a** (derivados viejos tras un despliegue) + **RD-b** (compactar el state),
  con condición de cierre. Decisión en **ADR-027**. **epic-005-real-operation sigue abierto** (`features-loop`):
  **11/13** unidades cerradas; restan 005-013 y 005-012. **Siguiente:** `005-013-unit-contract`, en orden
  `005-013 → 005-012`.

- 2026-10-13 — 005-004-claude-code-roles cerrada (epic 005, 10.ª feature): **roles CDAD activos en Claude Code**
  por el mecanismo nativo (`Agent`/`subagent_type: cdad-<rol>`) y **un ciclo corto real** despachado desde una
  sesión nueva de Claude Code con la versión instalada al empezar, con recepción CDAD (I8 `runtime: claude-code`,
  recibo durable `pending`, `reconcile: received`). Producto: herramienta de despacho declarada como la real
  (`Agent`; el lado OpenCode conserva `Task`), enunciado del instalador corregido (sin `strip`; la causa es el
  perfil de generación) con procedencia de modelo bajo `basic` y exención explícita de la invariante, **pata
  Claude Code aditiva** del chequeo de versión, y **mapa de hooks declarado una vez** con verificación del guard
  sin sesión viva. Gate de T5: **paso a APROBADO**, **paso b BLOQUEADO** hasta el despliegue del dueño. Suite de
  cierre **915 passed / 2 failed / 4 skipped** en worktree fijado a `c8ab21f` (una regresión real de T4 corregida
  en `5d6f667`; el otro fallo, error de perfil del lanzador); `make validate` 155 PASS / 1 FAIL (F011
  preexistente). Review formal única **0 bloqueantes / 3 opcionales / 2 abstenciones**. Deuda `debt.md`
  RD-1..RD-6 + F-3/F-5/F-7 + proceso de la suite; preexistente F011 (D-6). Decisión en **ADR-026**.
  **epic-005-real-operation sigue abierto** (`features-loop`): **10/13** unidades cerradas; restan 005-011,
  005-013 y 005-012. **Siguiente:** `005-011-common-entry`, en orden `005-011 → 005-013 → 005-012`.

- 2026-10-13 — 005-007-progressive-planning cerrada (epic 005, 9.ª feature): **planificación progresiva**
  con marcador cerrado `detail` (`"next"`/`"planned"`) y regla de fuente única, reconciliación del
  validador (fail-closed + checks mecánicos intactos), **`open-unit`** (abre la unidad sin editar el
  state), **materialización legítima del informe del architect** (`role-report`), **detección de despacho
  por el medidor** (invocación real de `cdad_delegate.py`), **plantillas** (spec desde el recorrido de
  uso; `feature-plan-template.md`), **tamaño de unidad por costo total** y **vínculo reintentos↔unidad**.
  Gate: 7 oráculos **37 passed**; suite completa en worktree fijado a `a5cd0c8` **4 failed / 871 passed /
  9 skipped / 6 errors** idénticos al base `99e2f2e`; `make validate` **141 PASS / 2 FAIL** (F011
  preexistente). Review formal única **2 blocking / 4 optional / 2 abstenciones** (familia distinta a la
  del implementer); **B1 y B2 corregidos ya** (`282c70a`, `a86278e`); optional y abstenciones a deuda
  (`debt.md` D-1..D-8). **BLOQUEO declarado:** la medición de uso con la **versión desplegada** queda del
  dueño; en la traza real el medidor dio `first_dispatch: absent` por falso negativo de invocación
  envuelta. Incidente del RED de review-fix (timeout, sin entrega, reintentado). **epic-005-real-operation
  sigue abierto** (features-loop): 9/10 features cerradas; resta 005-004. **Siguiente:**
  005-004-claude-code-roles.

- 2026-10-12 — 005-003-orientation-reduction cerrada (epic 005, 8.ª feature): **orientación acotada
  al primer despacho legítimo** — vista compacta `status` (proyección read-only del estado, sin
  historial, límite 16.384 B fail-closed), selección de entrada explícita, interfaz operativa con
  ejemplos que se ejecutan, disposición de versión/medidor (medidor ausente = ausencia), resumen del
  conjunto (`set-summary-v1`) con la regla R4, y el **contrato aplicable del encargo**
  (`packet-contract-v1`, aditivo). **Gate de aceptación PARCIAL con bloqueo declarado:** D11 y R4
  cerrados en T3; **la aceptación de uso real (A1/A2/A6/A9) queda pendiente del despliegue** (del
  dueño). Review formal única **0 blocking / 6 optional / 7 abstenciones**; F1/F4 corregidos, F2
  propuesto al dueño, resto a deuda. **Suite completa: no corrida aún** (una sola vez, al cierre, por
  quien cierra). **epic-005-real-operation sigue abierto** (features-loop): 8/10 features cerradas;
  restantes 005-007 y 005-004. **Siguiente:** 005-007-progressive-planning.

- 2026-10-11 — 005-002-session-context-meter cerrada (epic 005, 7.ª feature): **formato de medición
  neutral del runtime, opcional y no enganchado en gates**, con **primer adaptador OpenCode
  read-only** (registro neutral `context-meter-v1` + wrapper fino + asset + reference; observado/
  estimado/desconocido; desconocido ≠ cero; el medidor **nunca aprueba**). Review formal única **0
  blocking / 10 optional** (familia distinta a la del implementer) → `debt.md` (D1 =
  `time_relative: 0.0` fabricado). Gate: RED/GREEN por tarea, **integración real verde** (dos
  muestras + S-BOOT-04 sobre la base real en solo lectura), **suite completa 787 passed / 4 skipped**
  (worktree fijado a `b1a8add`), `make validate` 142 PASS / 1 FAIL (F011, drift de HOME; resolverlo
  exige desplegar, del dueño). El gate de integración destapó un defecto de pinneación
  (`total_output` = `max_output`) corregido en el test-writer (`49d27ad`). **epic-005-real-operation
  sigue abierto** (features-loop): 7/10 features cerradas (005-001, 005-002, 005-005, 005-006,
  005-008, 005-009, 005-010); restantes 005-003, 005-007, 005-004. **Siguiente:** 005-003 (consume el
  instrumento).

- 2026-10-10 — 005-006-guided-project-start cerrada y desplegada (epic 005, 3.ª feature): **una
  instrucción breve basta** — procedimiento corto de arranque
  (`references/project-start.md`) + entrada *boot-at-rest* en el intake; CLI instalado
  (`$CDAD_INSTALL_ROOT/…`); dueño canónico del reconocimiento por objeto; responsable de
  `epic_features` = coordinador de epic. Sin cambios en `cdad_packet.py`. Review formal única
  `approved-with-conditions` (0 bloqueantes; F1 cerrado como review-fix). Gate: suite completa
  **680 passed**, `make validate` 141 PASS / 2 FAIL F011 preexistentes. **Condición del
  dueño:** activación + **R2 real** (cierra VERIFY 5). **epic-005-real-operation sigue
  abierto** (features-loop): 3/7 features cerradas (005-001, 005-005, 005-006); siguientes
  005-002, 005-003, 005-007, 005-004. **Siguiente:** 005-002-session-context-meter (depende
  de la activación de la versión nueva).

- 2026-10-09 — 005-005-adoption-coherence cerrada (epic 005, 2.ª feature): el reemplazo
  valida el **encargo resultante completo** (conservado + corregido) sin sumar restricciones
  al camino normal (PD-5/INV-4); **una sola política de evidencia** con dueño canónico
  (`stage-3-tdd.md` §«Test evidence policy») y consumidores que remiten (13 archivos);
  **procedencia de la instalación** (variable > registro de activación > global) con
  contradicción diagnosticada y `source_version` en el manifiesto; el instalador declara su
  versión (`version.txt`); PD-17 de 005-001 enmendada con fecha; `review.md` de 005-001
  normalizada (PD-27→PD-20) y rutas personales fuera del epic-005. **Cierre (T4):** test de
  integración en raíz aislada (`prepare` → `--replace-packet` → despacho, sin HOME).
  **Review formal única:** `changes-approved` sin bloqueantes (O1..O5). Gate: suite completa
  **649 passed**, `make validate` 141 PASS / 2 FAIL F011 preexistentes. **Siguiente:**
  005-002-session-context-meter (depende de la adopción de esta versión, decisión del dueño).

- 2026-10-09 — 005-001-idle-and-v7-bootstrap cerrada (epic 005): aprobación de contrato por
  rol (architect por el plan del epic; test-writer/implementer/reviewer por la spec pineada
  `contract_path`+`contract_sha256`), reemplazo de paquete preparado y no despachado
  (`--replace-packet`, obsolescencia verificable, conserva el anterior, `.superseded.json`),
  marcadores `approval pending`/`packet obsolete`/`state incoherent`, y reposo legítimo en
  `validate-state` (`VALID: idle`). Enmienda T-CORR (C1 pin que nombra el contrato;
  C2 conservación y corrección del encargo). Prueba decisiva PD-17 verde. Review formal única:
  B1 (sección «Reemplazo» de `project-execution.md`) cerrado con `9468027` + familia `1faef04`;
  B2..B7 a deuda. Gate: suite completa 629 passed, focales 30, `make validate` 141 PASS / 2 FAIL
  F011 preexistentes; v7 `ce09ed0`. **Siguiente: 005-002-session-context-meter** (B3: la raíz v7
  viva quedó fuera de sync para `cdad_packet.py` — re-sincronizar, decisión del dueño).
- 2026-10-08 — **epic-003 cerrado** como fase de infraestructura con enmienda (aprobación del
  dueño). Suite de cierre 599 passed en `350a93c`. Pendiente del dueño: activar la v7, Claude Code
  (confianza y copias de HOME) y la deuda del próximo epic.
- 2026-10-08 — 003-007-living-continuity cerrada (epic 003): continuidad que tolera
  documentos vivos — clases de referencia `contract`/`living` **declaradas por el escritor**
  (`contract` bloquea, `living` informa con `state`/`current_sha256`), legado por comparación,
  `checkpoint`≠`begin` (`record` en el body, append de eslabón). Resuelve T4-REF y T4-CKPT.
  Uso real: T3 (v6 bloqueaba por vivos, v7 reanuda los tres stores; bloqueos `contract`/
  autoridad en copia; rotación sin escrituras) y sonda 2 (`resume`/`reconcile` descubiertos
  sin indicación, 18 lecturas previas). Gate de cierre 66 passed + validadores 141/2
  (F011+A3 preexistentes); suite 599 passed en `1f5fdac`. La versión nueva está instalada en
  raíz aislada; **el repo sigue en v6, la activación de la v7 es decisión del dueño**. Última
  feature del epic; **siguiente: `closure.md` de 003-007 y cierre/integración de epic-003
  (decisión del dueño)**.

- 2026-10-08 — 003-006-runtime-adoption cerrada (epic 003): activación **por proyecto**
  hacia raíz aislada (`cdad-activate.py`; determinista, no-clobber, contención de ruta;
  nunca HOME), `receive` y continuidad en el ciclo, re-adopción v5 (`d958672`) y v6
  (`abcd4d3`). Uso real: RU-1 (hook CC resolvía el clasificador desde HOME → fail-closed →
  `5c09770`) y RU-2 (rechazo dejaba cuerpo huérfano → todo-o-nada `abcd4d3`); `reconcile =
  received` idempotente; rotación correcta. Límites: Claude Code (mezcla de versiones,
  hooks sin confianza), Codex (catálogo ambiguo), T4-REF (alta). Suite 567 passed (926 s)
  en `abcd4d3`; validadores 141/2 preexistentes; sin CI. **v6 con activación pendiente del
  dueño.** Última feature del epic; **siguiente: cierre/integración de epic-003 (decisión
  del dueño)**.

- 2026-10-07 — 003-004-context-continuity cerrada (epic 003): CLI read-only
  `cdad_continuity.py` (write-ahead/idempotente, `reconcile` como oráculo, `resume`
  on-demand, `trigger` como señal); nunca escribe el state (single-writer = orquestador).
  T1–T3 con review-fix, T4 con uso real (RU-1 defecto de integración real → fix `0005128`;
  RU-1b `no_op: true`; RU-2 rotación en frío, P2/P3). Gate 523 passed (786 s) en worktree fijado a `6110e07`, stdin cerrado; `validate-consistency.sh` 142 PASS / 1 FAIL (F011 `validate-subagents.sh`, preexistente: `install.sh --check` contra copias instaladas; `validate-odoo-specialization.sh` PASS en árbol limpio); validadores con los
  2 FAIL preexistentes. Última feature del epic; **siguiente: cierre/integración de
  epic-003 (decisión del dueño)**.
- 2026-10-07 — 003-003-progress-guards cerrada (epic 003): guard determinista
  read-only (`classify`/`preflight` consultivo/`record`/`budget` durables/escalado con
  tabla cerrada); el juicio en el orquestador; nunca escribe el state. T1–T4 con
  review-fix y T4 aprobada (0 bloqueantes, 4 mutaciones). Uso real honesto: no detectó
  los C1/C2 reales; 2 falsas alarmas por progreso de grano grueso; corrección del
  dueño → C1/C2 artefactos del despacho con `opencode run`, G2 retirada, G1 a media.
  Versión operativa `939f501`; suite de cierre 487 passed (`87d91b2`); sin CI. Siguiente:
  003-004-context-continuity (epic 003).


- 2026-10-06 — 003-002-artifact-tools cerrada (epic 003, reactivado): CLI de
  recepción/materialización/evidencia con recibo mecánico que nunca aprueba; T1–T4
  con review-fix (T3 en 3 rondas hasta el remedio de clase fail-closed); primer uso
  real del flujo (bytes idénticos, idempotente) + smoke instalado; un solo escritor
  del state (orquestador). Suite 439 passed (`d7ffbcc`); validadores 141 PASS / 2
  FAIL preexistentes (F011-A drift de HOME, F011-B A3); sin CI. epic-004 cerrado
  (2026-10-05).

- 2026-10-05 — 004-003 cerrada: T1–T5 y T7 cerradas, T6 condicional; brecha D8
  cerrada (primer paquete v2 del architect); AC-7 eximido por decisión del dueño
  (141 PASS / 2 FAIL preexistentes). Suite 364 passed en `287f6c7`; instalación
  aislada PASS (303 grupos). Memory Bank aprobado por Pablo. Siguiente: cierre de
  epic-004.

- 2026-09-29 — 004-001 T6 cerrado: GREEN (09d675e, GLM vía OpenCode orquestado por Claude) + review-7 (approved-with-amendment) + enmienda del oráculo stale de 003-001 (00da41d). Suite 98/98. Sigue T7 (asserts de garantía PD-10 + recorrido de capacidad PD-11) y cierre de 004-001.
- 2026-09-29 — 004-001 T7 cerrado: PD-10 (33bf757, c9f1448), PD-11/12 estático (881830e) + recorrido vivo de 5 roles con 0 denegaciones (evidence/t7-live-walk.md). Suite 120/120. T1–T7 completos; pendiente el cierre de la feature (criterios de aceptación, Memory Bank).
- 2026-09-29 — 004-001 cerrada: criterios 1–7 en ✅ (closure.md),
  suite 132 passed tras `5e12c0f`, PD-17 T1–T7 completo en
  c0-dispatch-record.md. Merge y Memory Bank aprobados por Pablo. Siguiente: 004-002 (recorrido CDAD con paquetes).
