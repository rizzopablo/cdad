# ADR-033: Los modelos se resuelven por configuración — sin perfiles en el instalador, fuente única en la delegación externa y sin verificación de familia

- **Status**: Accepted (aprobado por Pablo el 2026-10-18)
- **Date**: 2026-10-18
- **Deciders**: Pablo (dueño: fijó el principio de **modelos por configuración**, **retiró la verificación de
  familia** —A-5— y aprobó las enmiendas 002/005 del plan del epic) + orquestador Claude (HITL delegada de
  epic-006: aprobó spec y plan con A-1..A-4, aprobó **A-6**, condujo la review y la suite de cierre) + architect
  (spec/plan) + scribe (borrador; **no aprueba**)
- **Confidence**: Media
- **Aprobación**: Pablo, 2026-10-18 (patrón Scribe; ADR-003/ADR-011). **Evidencia disponible para la decisión:** contrato
  `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` (sha256 `c25ebf0e…`; PD-1..PD-8,
  INV-1..INV-7, D1..D8; §8 A-1..A-4, §9 A-5) y `plan.md` (A-6); RED→GREEN por unidad (U1 `d5b2ae0`→`afcd14f` +
  testfix `bb674b4`; U2 `f2c3540`→`44f1561`; U3 `54c6ac6`→`2b1b597`; U4 `5b91387`→`df90b41`; U5' `0629ae0`
  (+`113c777`)→`0230156`; U6 `e2eba98`→`797b935`; U7 `3a04ad1`→ detenido `ef78451`→ testfix `12a859b`→`516149b`;
  U8 `1bc7645`); **review formal 0 bloqueantes / 7 opcionales / 3 abstenciones**; review-fix (`c57fc79`→`ef8d2f8`);
  **re-review focal 1 con 1 bloqueante (B-1)** y **re-review focal 2 con 0 bloqueantes** (`26667b5`→`738a380`);
  **suite de cierre `1177 passed, 5 skipped, 0 failed`** y `make validate` 168/1 (F011 = DT-8, preexistente) y
  **169/0** sobre la instalación de aceptación. **La confianza es Media** porque: (i) el producto **no está
  desplegado ni en uso** —lo instalado en HOME es el despliegue de 006-002 y el redespliegue está pendiente de la
  orden del dueño—; (ii) queda un escape **silencioso declarado** en una configuración soportada (raíz redirigida +
  `XDG_CONFIG_HOME` del host: **O-3**), más O-6 (XDG relativo), ambos a decisión del dueño; (iii) la retirada de la
  verificación de familia (A-5) deja el anti-sesgo **enteramente** en la configuración del runtime: **no se exige,
  no se verifica y no se declara**, por decisión del dueño; (iv) **B-1** mostró que un defecto estructural del
  manifiesto pasó la primera review y que el RED lo cerró con evidencia falsa (lo refutó la re-review); (v) **OPT-2**
  y **DT-8** quedan a deuda. No es Baja porque las postcondiciones son **mecánicas y observables** (grep, tests y
  sondas black-box de un reviewer independiente) y el bloqueante se cerró con un **remedio estructural** verificado
  punto por punto por una segunda re-review independiente.

## Contexto y problema

ADR-007 resolvió la portabilidad del despliegue con **tres perfiles de modelos** en `scripts/cdad-models.sh`
(`economical`|`optimus`|`premium`), un **cuarto** perfil `basic` que eliminaba la línea `model:` de las copias
instaladas, un **marcador** de perfil en el árbol instalado (`.cdad-models-profile`), flags de perfil en el
instalador y un `validate-subagents.sh` *profile-aware* que **validaba** el invariante «reviewer ≠ implementer» por
comparación exacta de strings. ADR-008 extendió el mapa a los alias de Claude Code (`cdad_model_claude`) y declaró
que, en ese runtime, el anti-sesgo se degradaba a «distinto dentro de Anthropic».

Dos hechos dejaron ese diseño sin sostén:

1. **El principio del dueño (`plan.md` §9, enmienda 002 del epic, 2026-10-17):** *los modelos nunca los fija el
   orquestador ni los scripts; dentro del runtime se usa el que esté configurado en el entorno y, en los despachos a
   otro entorno, el modelo sale de un archivo de configuración; elegir modelo no es una decisión de orquestación.*
   Con eso el mapa de perfiles es una **segunda fuente** y la línea `model:` de los agentes una **decisión de
   diseño** que el despliegue no puede honrar en todos los casos.
2. **Un hallazgo medido en el despliegue:** al desplegar la feature anterior, las dos referencias retiradas
   quedaron en HOME como `pending_removal` —**no instalables pero presentes**— y solo `--uninstall` las retiraba; un
   orquestador podía seguir leyéndolas (`docs/epics/epic-006-opencode-concurrency/execution.md` §«Despliegue y push
   tras 006-002»). El mismo mecanismo dejaba vivo el marcador de perfil retirado.

La pregunta arquitectónica: **¿dónde vive el modelo, para que el instalador no tenga que elegirlo y el ciclo siga
siendo verificable?**

## Opciones consideradas

### Opción A: conservar los perfiles en el instalador (estado actual de ADR-007)

- Pros: cero cambios; el despliegue elige el costo/calidad con un flag.
- Contras: **dos fuentes** del mapa (script + ADR + tabla §2 del contrato de roles); el check pierde el
  byte-compare estricto de la línea `model:` y lo reemplaza por una validación semántica contra el perfil activo;
  la elección de modelo queda como decisión de despliegue del instalador, contra el principio; con `basic` el
  anti-sesgo **no** está garantizado por construcción. **Descartada.**

### Opción B: instalador siempre sin perfiles, modelo por configuración (ADOPTADA)

- El instalador y el generador no tienen perfiles ni mapa; la delegación **interna** toma el modelo de la
  configuración del runtime; la delegación **externa** lo toma de **un** archivo (`delegation.json`, por destino y
  rol), y una clave `model` heredada en la exec-config se ignora con aviso.
- Pros: una sola fuente por camino; el instalador deja de decidir modelos; el check vuelve a ser estricto (no hay
  línea `model:` que tolerar); el usuario completa la configuración en un archivo **suyo**.
- Contras: una exec-config existente **cambia** de modelo efectivo (pasa al default del destino) —declarado y
  avisado—; la familia del reviewer **deja de estar garantizada**; hay que retirar el mapa y reformular los tests
  acoplados (declarando el reemplazo).

### Opción C: conservar la verificación de familia como script (punto 4 original del plan §9)

- Un script comparaba los modelos efectivos del reviewer y del implementer, avisaba si eran de la misma familia y el
  gate de review declaraba «invariante no garantizado» cuando no era verificable. Se implementó (RED `9a103af`) y el
  dueño lo **retiró** en mitad de camino (**A-5**): el modelo interno lo fija el runtime y el externo el archivo;
  exigirle al orquestador controlar la familia era pedirle una decisión que **no le corresponde**, y la verificación
  era no bloqueante y decía «no verificable» justo con alias. **Retirada por decisión del dueño** (el script **no se
  construyó**).

### Opción D: dejar el mapa en el repo y publicar solo una plantilla sin modelos

- Contras: contradice el principio (el repo fijaría modelos que el runtime no tiene por qué usar) y mantiene el
  drift entre diseño y despliegue. **Descartada.**

## Decisión

1. **El instalador y el generador no tienen perfiles ni mapa de modelos (D1).** `scripts/cdad-models.sh` se
   **retira**; el `Makefile` pierde `PROFILE`; `cdad-generate.py` pierde `--profile`; el manifiesto de staging pierde
   la clave `profile`; **ningún agente declara `^model:`**. Los flags `--economical|--optimus|--premium` se
   **rechazan** (rc≠0) con un diagnóstico que **nombra la config de delegación** como el lugar donde se elige el
   modelo, y **ningún despliegue ocurre**. `--basic` y `CDAD_MODEL_PROFILE` se **aceptan y se ignoran** con un
   **aviso de deprecación de una línea** (A-1; ≥6 recetas de test los usan): nada silencioso.
2. **La delegación externa tiene una sola fuente de modelo (D3, decisión del dueño).** `delegation.json`
   (`version: 1`; `models[<destination-id>][<rol>]`; `credential_env_file` opcional) en
   `$XDG_CONFIG_HOME/cdad/` o `<INSTALL_ROOT>/.config/cdad/`. **Sin fallback:** un rol sin entrada ⇒ el argv del
   destino **no lleva `--model`** y la observación registra `model_configured: null`; una clave `model` en la
   exec-config se **ignora** con un aviso de una línea que nombra la ruta y cómo migrar.
3. **La delegación interna la fija el runtime (D2).** CDAD **no elige, no adivina y no verifica** el modelo: usa el
   configurado en el entorno del runtime y registra el observado post-hoc; lo no observado es `unknown`, nunca un
   valor inventado.
4. **No se exige ni se verifica la familia del reviewer (A-5, decisión del dueño).** Se retiran los PD de familia,
   la decisión D4, la §2.4 de la spec y el script de comparación (que **no se construyó**); **INV-5 se reemplaza**:
   ningún texto instalable exige a ningún rol elegir, controlar, verificar ni declarar la familia o el modelo del
   reviewer respecto del implementer. Se **conservan** la observación I8 (`model_configured`/`model_reported`, que
   solo registra lo ocurrido) y los demás invariantes anti-sesgo (el test-writer no ve la implementación, el
   implementer no edita tests, el reviewer es read-only y de sesión separada).
5. **Los archivos de configuración son datos del usuario, no ownership del instalador (A-3).** El instalador crea
   `delegation.json` y `opencode-server.env.example` **solo si no existen**, **no** los registra en el manifiesto, y
   una segunda instalación **no los pisa** (bytes idénticos + aviso). Ni `--uninstall` ni el retiro de obsoletos
   pueden borrarlos.
6. **La credencial del servidor sale de un archivo verificado (D5).** Variables de entorno primero; si no, el
   archivo (`credential_env_file` o el default `<config-dir>/cdad/opencode-server.env`, formato `KEY=value` +
   comentarios `#`), **solo** en modo `server`; permisos verificados sobre el **fd abierto** (`os.fstat`, patrón
   TOCTOU ya existente; se rechaza cualquier bit 077) y un diagnóstico 401/403 **autosuficiente** (nombres de
   variables, ruta resuelta, procedencia del valor y —si aplica— ruta y modo encontrado) que **nunca** contiene el
   valor. El instalador deja la plantilla `.example` **sin valor**.
7. **El instalador retira sus propios obsoletos (D6, decisión del dueño).** Un artefacto registrado, no
   redesplegado y con **sha256 igual al registrado** se retira del disco y del manifiesto; uno **modificado
   localmente** se preserva, se reporta como CONFLICT y **sigue registrado**; uno **no registrado** no se toca. La
   regla es **una sola función** compartida con `--uninstall` (sin duplicar) y un registro con digest **vacío o
   `null` nunca es removible** (`unverifiable`). `--dry-run` lista las bajas sin escribir. La cuenta esperada del
   `Verify` del instalador **se deriva del staging** (A-6), no de una constante, para que retirar un artefacto
   desplegado no reporte una instalación incompleta.
8. **Los tests acoplados se reformulan declarando el reemplazo (D7/A-1).** Ningún assert se borra sin declarar qué
   afirmaba y por qué el contrato nuevo lo reemplaza; el implementer no edita tests.

## Reasons

1. **Elegir modelo no es una decisión de orquestación ni de instalación.** Poner la fuente en la configuración (del
   runtime para adentro, un archivo para afuera) hace que el instalador solo **despliegue** y el orquestador solo
   **pase** lo que ya está configurado; desaparece la tentación de inventar o heredar un modelo para «cumplir» un
   invariante.
2. **Una fuente por camino se puede verificar.** Con el mapa de perfiles había tres superficies que podían divergir
   (script, ADR, tabla del contrato de roles) y el check debía **tolerar** la línea `model:`; sin mapa, la ausencia
   es verificable por grep y el `--check` recupera el byte-compare estricto.
3. **El retiro de la verificación de familia es coherencia, no relajación.** Si el modelo interno lo fija el
   runtime, ningún script de CDAD puede afirmar nada sobre la familia del reviewer; un aviso «no verificable» que
   no bloquea agregaba prosa a los gates sin agregar garantía. El anti-sesgo queda donde **sí** es estructural: en
   las sesiones separadas, el read-only del reviewer y los límites de escritura por rol.
4. **La configuración del usuario no es del instalador.** Registrar en el manifiesto un archivo que el usuario
   edita convierte su edición legítima en CONFLICT y expone su contenido a un `--uninstall`; dejarlo fuera del
   ownership hace que el instalador no pueda destruir datos del usuario **por construcción**.
5. **Un obsoleto propio que sigue en disco es un riesgo de uso, no solo de higiene.** El caso medido es exacto: un
   orquestador podía **seguir leyendo** referencias que ya no debían existir. Retirarlas al instalar —con la misma
   regla de sha256 que ya usaba `--uninstall`— cierra el agujero sin tocar nada ajeno ni modificado.
6. **Un registro con un campo vacío que cambia un borrado es un defecto estructural.** B-1 lo demostró: el formato
   de transporte (TSV leído por bash) hacía que un digest vacío **retirara** un archivo. El remedio estructural
   (NUL-framed + veredicto `unverifiable`) es la razón por la que esta decisión documenta **cómo** viajan los
   registros, no solo qué se retira.

## Consequences

- **Positivas.** Una sola fuente de modelo por camino; el instalador deja de decidir y de tolerar líneas `model:`;
  los archivos de configuración del usuario son inmunes a `--uninstall` y al retiro de obsoletos; el instalador
  retira sus propios obsoletos (el caso medido) y `--check` vuelve a PASS sobre una instalación al día; el
  `Verify` conserva su poder de detectar una instalación incompleta derivando la cuenta del staging; la suite de
  cierre queda **verde sin fallas** (1177 passed / 5 skipped) y `make validate` sobre una instalación al día da
  **169/0**.
- **Negativas / límites declarados.** (a) **La familia del reviewer ya no está garantizada ni declarada**: por
  decisión del dueño (A-5) depende por completo de la configuración del runtime y de `delegation.json`; **no hay
  aviso** cuando reviewer e implementer comparten modelo. (b) Una **exec-config existente** con `model` cambia de
  modelo efectivo (pasa al default del destino): el aviso de deprecación lo dice, el cambio es real. (c) **O-3**: con
  raíz redirigida **y** `XDG_CONFIG_HOME` del host definida, los archivos de config se crean en el XDG real —
  INV-6 al pie de la letra se rompe en esa configuración (los tests evitan el caso redirigiendo XDG); **decisión del
  dueño** pendiente. (d) **O-6**: un `XDG_CONFIG_HOME` **relativo** resuelve rutas relativas al cwd de cada proceso.
  (e) **OPT-2**: el comentario de symlinks de `install.sh` declara un veredicto que el código (más conservador) ya
  no entrega con digest vacío; solo alcanzable con un manifiesto editado a mano. (f) **DT-8** (`__pycache__` en el
  staging) sigue **fuera de alcance** y el retiro de obsoletos **no** promete árbol «limpio». (g) El producto **no
  está desplegado**: el redespliegue en HOME está pendiente de la orden del dueño, así que el comportamiento nuevo
  **no está en uso** donde se medirá su utilidad.
- **No cambia.** El paquete canónico y su pase byte-idéntico, el registro I8 (los campos que se conservan), el
  ledger, `receive`, la materialización por el orquestador y la aprobación del usuario, el single-writer del state,
  el clasificador de paths y el guard de permisos, y la regla de delegación por capa de ADR-032 (el mecanismo nativo
  del runtime sigue siendo el camino intra-runtime; el adaptador sigue cruzando runtimes).

## Notas

- **Contrato normativo:** `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` (PD-1..PD-8,
  INV-1..INV-7, D1..D8; §8 **A-1..A-4**, §9 **A-5**) y `plan.md` (unidades U1..U8, **A-6**); enmiendas del epic:
  `docs/epics/epic-006-opencode-concurrency/plan.md` §9 (enmienda 002) y §12 (enmienda 005, numeración a ajustar).
- **Código y documentos de producto:** `install.sh` (perfiles fuera, config de delegación, credencial, prune),
  `scripts/cdad-generate.py`, `scripts/validate-subagents.sh`, `Makefile`, `scripts/cdad-models.sh` (**retirado**),
  `sources/agents/adapters/{opencode,claude-code}.md`, `sources/roles/*`, `agents/**` (regenerados),
  `skills/cdad-cycle/SKILL.md`, `skills/cdad-cycle/references/cli-delegation.md`,
  `skills/cdad-cycle/scripts/{cdad_delegate.py,cdad_delegate_opencode.py}`,
  `skills/cdad-cycle/assets/opencode-exec-config.example.json`.
- **Evidencia:** `discovery.md`; `u1..u8-{red,green}.md`; `u1-testfix.md`; `u5p-testfix.md`; `u7-testfix.md`;
  **`u7-green-stop.md`** (el detenimiento, la contradicción B3↔PD-6a medida black-box y el patch preservado);
  `u8-acceptance.md`; `review.md`; `rf-red.md` (con la corrección posterior) / `rf-green.md`; **`rereview.md`**
  (B-1); `rf2-red.md` / `rf2-green.md`; `rereview2.md`; `docs/epics/epic-006-opencode-concurrency/execution.md`
  (§«006-003: paquete despachado sin entrega», §«suite completa antes de la review», §«suite de cierre»).
- **Commits:** U1 `d5b2ae0`→`afcd14f` (+`bb674b4`); U2 `f2c3540`→`44f1561`; U3 `54c6ac6`→`2b1b597`; U4
  `5b91387`→`df90b41`; U5 `9a103af` (retirado por A-5, sin GREEN); U5' `0629ae0` (+`113c777`)→`0230156`; U6
  `e2eba98`→`797b935`; U7 `3a04ad1`→`ef78451` (GREEN detenido, sin commit)→`12a859b`→`516149b`; U8 `1bc7645`;
  review-fix `c57fc79`→`ef8d2f8`; review-fix 2 `26667b5`→`738a380`. **Último commit de producto: `738a380`.**
- **Relación con otros ADR:** **reemplaza ADR-007** (perfiles de modelos) y **la parte de perfiles de ADR-008**
  (mapeo de alias `cdad_model_claude`, fila «Reviewer ≠ implementer» de sus trade-offs y la extensión de
  `cdad-models.sh`). **Completa el punto 4 de ADR-032**, que declaró el principio de modelos por configuración y
  remitió expresamente a esta feature la plantilla de config, el script de familias y la sustitución de ADR-007.
  Convive con ADR-031 (selección de modo de ejecución), ADR-023 (delegación externa) y ADR-003/ADR-011 (patrón
  Scribe y materialización). **Observación para el dueño (no decidida aquí):** los mapas concretos de modelo por
  rol de **ADR-001/ADR-005** quedan **sin efecto operativo** en el árbol instalable (no hay mapa en ninguna parte);
  su retiro formal es una decisión aparte.
- **Numeración:** **ADR-033** (este). El ADR del principio de general antes que específico, reservado como «ADR-033»
  en `plan.md` §12 (enmienda 005, aprobada por el dueño el 2026-10-18), pasa a **ADR-034** porque el número lo
  consume el artefacto que se materializa primero; `plan.md` §12 punto 1 y su línea de Aceptación deben ajustarse.
- **Límites honestos de este registro:** el producto **no está desplegado**; las postcondiciones son mecánicas y
  observables pero **no hay observación de uso real** de esta feature; O-3/O-6/OPT-2/DT-8 quedan abiertos; y el
  invariante de familia **ya no existe por decisión del dueño**, no por evidencia de que fuera innecesario.
