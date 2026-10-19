I have verified every claim I need against the repo (HEAD `1e508ec`; line numbers may shift, so the spec cites the symbol as well as the line). Here are the two documents, as final text, followed by this role's evidence.

**Corrections adopted from the orchestrator's instruction:** the paths are `.cdad` (the discovery wrote `.cadad` in prose; every verified path is `.cdad`), and the temporal default is treated as a *proposal* that requires the justification the spec now carries (§5 D-5, conditions C1–C5), with the alternative declared.

```
===== BEGIN docs/specs/006-005-native-path-parity/spec.md (DRAFT — UNAPPROVED) =====
# 006-005-native-path-parity — SPEC (etapa 2)

Estado: **BORRADOR no aprobado.** No habilita RED, ni construcción, ni aprobación.
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §11 (enmienda 004),
con el principio de §12. Ejecución `exec-006-005-native-path-parity-001`.
Insumo: `docs/specs/006-005-native-path-parity/discovery.md` (etapa 1).
Base medida: HEAD `1e508ec`. Los números de línea son del HEAD medido y pueden
correrse; por eso cada cita nombra también el símbolo.

Anonimización: rutas del repositorio, relativas; sin rutas del host, endpoints,
ids de sesión ni nombres de otros proyectos. El «proyecto consumidor» se nombra así.

## 1. Descripción funcional

La delegación **nativa** («herramienta del runtime», p. ej. `task` +
`subagent_type: cdad-<rol>`) ejecuta el encargo pero **no traslada la preparación
que el adaptador externo sí hace**: nadie registra el intento I8 —sin eso
`receive` rechaza, `cdad_result.py`:578-581 «the active packet is not
dispatched»—; ningún encargo puede conceder un temporal al test-writer —el
validador de scopes lo impide, `cdad_packet.py`:694/:729—; un intento que no
vuelve no tiene camino mecánico a `failed` (la disposición registra la decisión y
su efecto sobre el paquete es `pass`, `cdad_packet.py`:5584-5589). Esta feature
cierra las cuatro brechas de §11 con **una pieza compartida** y **una integración
por runtime**:

1. **Núcleo común** `skills/cdad-cycle/scripts/cdad_dispatch.py` (runtime-neutral;
   capa `scripts` del principio de capas, §8 de §11/§12): registra el intento por
   el comando que ya existe (`prepare --record-dispatch`,
   `cdad_packet.py`:2501) y **conserva la entrega**; no reimplementa validaciones
   —importa `cdad_packet` como hace `cdad_result.py`— y no agranda `cdad_packet.py`.
2. **Integración del runtime** resuelta por convención de módulo
   (`cdad_runtime_<id>.py`, espejo de `cdad_delegate_<id>.py`, ADR-023/ADR-032):
   declara `VERIFIED_VERSIONS`, capacidades, contexto efectivo y observación de
   sesión; fuera de su versión verificada falla cerrado.
3. **Temporales del test-writer** como clase de scope `temporary` del vocabulario
   observable (`cdad_packet.py`:303-322 ya la nombra), validada contra
   `temporary_roots` de la política y verificada con `git check-ignore` en `prepare`.
4. **Una sola entrada operativa del orquestador**, consumiendo el `entry`/`next`
   que el CLI ya calcula (`cdad_packet.py`:5828/:5847/:5886) en vez de re-derivar
   la situación con cuatro entradas solapadas (`sources/roles/orchestrator.md`:22-57).
5. **Camino mecánico a `failed`** por la autoridad que ya existe (la disposición),
   para el intento interrumpido sin entrega.

## 2. Contrato

### 2.1 Superficie del núcleo (una CLI, dos verbos)

```
cdad_dispatch.py record --project-root R --packet P --attempt-id A
    [--native-result FILE|-] [--since TS] [--runtime auto|<id>]
cdad_dispatch.py capabilities --runtime <id> [--json]
```

- `record`: resuelve la integración; construye la observación con las claves
  cerradas I8 (`OBSERVATION_KEYS`, `cdad_packet.py`:2371; validación
  `_load_observation_document`, :2410); prioriza el **resultado nativo
  byte-exacto** y, sólo si no lo hay, **una** lectura acotada del store vía la
  integración; verifica correspondencia de sesión (§2.3); registra por
  `prepare --record-dispatch`; escenifica el texto final bajo `.cdad/inbox` con su
  `RESULT.json`. **No** ejecuta `receive`: el recibo es del protocolo de re-entry
  (`skills/cdad-cycle/references/re-entry.md`, sección «Orchestrator
  materialization protocol»).
- Sobre de salida: exactamente las claves de `OUTPUT_KEYS`
  (`cdad_delegate.py`:49-51: `attempt`, `session`, `termination`, `delivery_ref`,
  `diagnosis`) y `termination` del vocabulario cerrado `TERMINATION_VOCABULARY`
  (mismo lugar). No se inventa un segundo idioma.
- `capabilities`: documento `{native_transport, external_adapter,
  session_correlation, version, reason}`.

### 2.2 Contrato de la integración (implementación por runtime)

`NAME`, `VERIFIED_VERSIONS` (observadas, nunca supuestas), `capabilities()`,
`resolve_context(project_root)` y
`observe_session(project_root, *, parent, agent, since, candidate=None)`
(forma completa en el discovery §2.2). Acceso al store: sólo lectura
(`mode=ro`, nunca `immutable`, nunca escritura — igual que
`cdad_delegate_opencode.py`:621-623), acotado por tiempo y **sin polling**.

### 2.3 Las cuatro llaves de correlación

Todas necesarias: **padre** (`session_v2.parent_id` == sesión que despachó),
**agente** (`session_v2.agent` == `cdad-<rol>`), **proyecto**
(`session_v2.directory` == raíz autorizada) y **momento** (`session_v2.time_created`
posterior al `begin` del intento). Una llave no evaluable ⇒ `unknown`.

## 3. Postcondiciones (PD-n, observables y testeables)

Convención: «oráculo» = el artefacto o comando que decide el pass/fail.

| # | Postcondición | Oráculo |
|---|---|---|
| **PD-1** | Un despacho produce **exactamente un** intento I8. `record` lo registra por el comando existente y ningún otro componente registra para el mismo despacho (hoy hay dos: interfaz `cdad_delegate.py`:396-398 y adaptador `cdad_delegate_opencode.py`:1727). | conteo de archivos en `.cdad/executions/<exec>/dispatches/` == 1 por intento; el adaptador y la interfaz no registran por su cuenta |
| **PD-2** | El núcleo no es un segundo escritor: no escribe `docs/.cdad-state.json`, no escribe el store, no escribe el ledger salvo por el comando existente; sólo escenifica bytes bajo `.cdad/`. | el estado sólo cambia por la transacción del comando; bytes del store idénticos (fixture) |
| **PD-3** | Con `--native-result`, la parte escenificada es **byte-exacta**: `sha256(parte) == sha256(entrada)`, sin retecleo, resumen ni regeneración; el descriptor apunta a ella y el recibo queda `semantic_status: pending`. | `sha256sum` de ambos; campo del recibo |
| **PD-4** | **Sin texto final o artefacto no hay entrega**: no se escenifica nada, no se escribe `RESULT.json`, no se invoca `receive`; el intento queda registrado y el sobre declara el hecho. | `.cdad/inbox` sin cambios; ausencia de descriptor; existencia del intento |
| **PD-5** | Una sesión se acepta como del intento sólo si las cuatro llaves (§2.3) coinciden. Si falta o no coincide alguna: **no hay entrega por esa vía**, la observación lleva `session: null` y el diagnóstico **nombra la llave** fallida. | fixtures con padre/agente/directorio/instante incorrectos; el diagnóstico contiene el nombre de la llave |
| **PD-6** | **Garantía menor declarada:** con resultado nativo byte-exacto pero identidad no verificable (V-1), la entrega se persiste con `session: null` y `provenance` que declara que no se pudo verificar la identidad; nunca se inventa un valor de sesión. | observación con `session: null`; `provenance` sólo anota los campos observados (`cdad_packet.py`:2440-2445) |
| **PD-7** | `capabilities` responde las cinco claves; fuera de `VERIFIED_VERSIONS` o con esquema desconocido ⇒ `native_transport: false` **con `reason` que nombra lo que falta**; id de runtime desconocido ⇒ rc≠0. | fixture de versión/esquema; el `reason` nombra el elemento faltante |
| **PD-8** | La integración OpenCode exige las columnas de correlación (`id`, `agent`, `model`, `directory`, `parent_id`, `time_created`) y **falla cerrado** nombrando las ausentes; nunca degrada a `timeout` ni a «ausente». | store descartable sin una columna → error específico |
| **PD-9** | **Sin bucle:** la lectura del store es única por invocación, `mode=ro`, con timeout acotado, y el intento declara `store_reads=<n>` en `provenance.session` con `n` ≤ el techo declarado; ninguna constante de intervalo ni bucle consulta el store. | conteo instrumentado del acceso; `store_reads` en el intento; ausencia de intervalo de polling en el módulo |
| **PD-10** | Un paquete puede declarar `{"class":"temporary","root":<selector>}`; se acepta **sólo si** el selector cae dentro de un `temporary_roots` de `docs/cdad-policy.json`. Con `temporary_roots: []` el encargo **se rechaza** nombrando el archivo y el campo. | `prepare` rc≠0 con el nombre del archivo; caso positivo rc=0 |
| **PD-11** | Con temporal declarado, `prepare` verifica con `git check-ignore` (read-only) que el selector está ignorado; si no lo está **o** el proyecto no es un árbol Git ⇒ falla cerrado nombrando las dos salidas legítimas (declararlo en `.gitignore`, o no pedir el temporal). | `prepare` rc≠0 + mensaje; caso positivo con raíz ignorada |
| **PD-12** | Con el temporal declarado e ignorado, un test real en `tests/` **más** una sonda dentro del temporal se reciben con `scope_validation: passed` y recibo `pending`; un cambio fuera de todo scope declarado sigue rechazándose. | campo `scope_validation` del recibo |
| **PD-13** | El temporal **no es producto**: sigue vigente el rechazo de `_validate_temporary_roots` (`cdad_packet.py`:414-430) cuando una raíz temporal se solapa con rutas de producto. | caso negativo de política |
| **PD-14** | **Camino mecánico a `failed`:** `register-transition --transition disposition --packet <activo> --resolution abandoned\|superseded`, **sin** recibo durable ⇒ `active_packet.status: failed` (terminal). No fabrica resultado, no fabrica recibo, no aprueba; `validate-state` VALID y `prepare` desbloqueado (hoy `cdad_packet.py`:4337 PD-4 lo bloquea). Si **hay** recibo durable ⇒ se rechaza nombrando `receive` (rechazo ya existente, `cdad_packet.py`:5205-5213). | estado tras el comando; `validate-state`; `prepare` antes rc≠0 / después rc=0 |
| **PD-15** | **Entrada única:** el mandato conduce la decisión desde `status.entry`/`next` con el orden de cinco filas de §5 D-6, sin dos filas con la misma condición; **no existe** la condición stale de `.cdad/execution.json` (`sources/roles/orchestrator.md`:24) y el generado lleva el mismo texto. | test de texto sobre la fuente y sobre el generado recomputado (§Makefile `staging`); `status` del CLI como evidencia del insumo |
| **PD-16** | **Espera detectada después:** no hay polling; el resultado del transporte es el primer observable; a lo sumo **una** lectura acotada bajo demanda, y un permiso rechazado/pendiente se reporta en el diagnóstico desde la superficie observable, `unknown` cuando no es observable. | ausencia de bucles/intervalos; `diagnosis` con el token observado o `unknown` |
| **PD-17** | **Cierre:** la review independiente de spec/plan precede al RED (enmienda 006, procedimiento vigente `plan-review` sobre `draft-plan`); `make validate` y la suite completa **una vez** al cierre (política declarada; corre quien cierra). | salidas de los comandos |
| **PD-18** | **Recorrido de aceptación** (U6): en un proyecto **descartable** —nunca HOME, nunca el proyecto activo— un layout anidado, el coordinador iniciado desde otra carpeta, agente global y configuración de proyecto declarados con garantía menor, un auxiliar temporal, **un test real escrito y recibido** y **un intento interrumpido registrado sin entrega y llevado a `failed` por comando**. Se declaran versión y configuración observadas y **no se generaliza** el resultado. | artefactos del recorrido: intento I8, recibo `pending`, estado `failed`, `scope_validation: passed` |

**MAPEO AC → PD** (los AC del epic §4/§11 como origen, no como autoridad):
AC-1 → PD-7/PD-8; AC-2 → PD-1/PD-3/PD-5; AC-3 (controlada) → PD-18;
AC-4 → PD-4/PD-14; AC-5 → PD-9/PD-16; AC-6 → PD-7/PD-8/PD-11;
AC-7 → PD-18; AC-8 → PD-17.

## 4. Invariantes (INV-n)

- **INV-1.** Sin texto final o artefacto **no hay entrega**: nunca se fabrica
  recibo, `completed` ni resultado. El recibo nace `pending` y **no aprueba**.
- **INV-2.** La sesión **se correlaciona o se declara `unknown`**: nunca 0,
  nunca «ausente», nunca un valor no leído del store o no devuelto por el
  transporte.
- **INV-3.** El temporal está **ignorado por Git de verdad** (verificado con
  `git check-ignore`); un temporal ignorado nunca aparece como cambio observado
  (el manifiesto usa `git ls-files --cached --others --exclude-standard`,
  `cdad_result.py`:1305-1318).
- **INV-4.** Fuera de su versión verificada o con esquema desconocido, la
  integración responde **cerrado/`unknown`** con motivo; sin fallback silencioso.
- **INV-5.** **Nunca un segundo escritor del store** (`mode=ro`, nunca
  `immutable`, nunca escritura) ni del state/ledger: el ledger se escribe sólo
  por el comando existente.
- **INV-6.** **Ninguna lectura del store en bucle**: sin polling, con techo de
  lecturas por invocación declarado y contado.
- **INV-7.** La política y `delegation.json` son **datos del dueño**: ningún rol
  las edita; el default de temporal es **propuesta**.
- **INV-8.** La observación I8 conserva su **esquema cerrado** (`OBSERVATION_KEYS`);
  el `provenance` sólo anota campos observados y nunca transporta resultados,
  gates ni aprobaciones; en salidas versionadas no hay secretos, rutas del host
  ni ids de sesión.
- **INV-9.** CDAD **no elige modelo** (regla I8 vigente, sin cambios).
- **INV-10.** El núcleo **no toca el producto**: escribe sólo bajo `.cdad/`.

## 5. Decisiones (D-n) — adoptadas por delegación HITL, con criterio §12

- **D-1 — Dónde vive el núcleo.** Módulo propio `cdad_dispatch.py` que **importa**
  `cdad_packet` (read-only) y escribe el ledger por el comando existente.
  *General/específico:* el núcleo es general (contrato de transporte-neutral);
  se evita generalizar `cdad_packet.py` (rechazada: agrandarlo contradice §11) y
  meterlo en `cdad_result.py` (rechazada: recepción es otra responsabilidad, §12).
- **D-2 — Forma de la integración.** Un módulo por runtime por convención, con
  interfaz mínima y `VERIFIED_VERSIONS`. *Rechazadas:* un módulo con dict de
  runtimes (mezcla runtimes; ADR-032) y una clase base/plugin (abstracción sin
  segundo consumidor real todavía, §12).
- **D-3 — Correlación.** Padre + agente + proyecto + `time_created > begin`, con
  `null`/`unknown` cuando no se puede evaluar. *Rechazadas:* confiar sólo en el id
  del transporte (más débil y hoy `VERIFY` V-1) y «la hija más reciente del
  directorio» (ambigua bajo concurrencia: es el tema del epic).
- **D-4 — Camino a `failed`.** El efecto del `disposition` mueve el paquete
  activo citado a `failed` (terminal, sin aprobar y sin recibo), reutilizando
  vocabulario y autoridad existentes. *Rechazadas:* verbo nuevo `fail-packet`
  (admisible, más superficie), `--replace-packet` sobre `dispatched` (lo prohíbe
  PD-10, `cdad_packet.py`:2094-2103) y `reconcile` que escriba (es read-only por
  contrato). **Conflicto declarado:** `docs/specs/005-012-transition-registration/spec.md`:243
  y su INV-9 (`:587`) declaran que el `disposition` **no** cambia `active_packet`.
  PD-14 **enmienda** esa consecuencia: requiere aprobación explícita del dueño y
  el test acoplado `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830
  se cambia **en RED declarando el reemplazo** (regla A-1, plan §4).
- **D-5 — Temporal.** Clase `temporary` en el vocabulario de scopes, validada
  contra `temporary_roots` (autoridad del dueño), default **propuesto**
  `.cdad/tmp`, verificación `git check-ignore`. *Rechazadas:* declararlo como
  clase `tests` (miente sobre la clase), temporal fuera del proyecto (es el
  incidente de la espera larga) y ruta libre declarada por el paquete (lo prohíbe
  PD-9 de 004-002).
  **Ubicación por defecto — justificación y condiciones** (corrección del
  orquestador: un default dentro de un directorio que el orquestador escribe
  requiere justificación explícita):
  - **C1** Es una **propuesta**, no una imposición: la emite `propose_policy`
    (`cdad_packet.py`:1088, hoy `temporary_roots: []` en :1101) y la acepta el
    dueño; en este repo la política vigente declara `temporary_roots: []`
    (`docs/cdad-policy.json`), por lo que **hoy** pedir un temporal falla cerrado
    — es el comportamiento correcto.
  - **C2** `.cdad/tmp` es **subdirectorio** disjunto de los subárboles que el CLI
    escribe (`inbox/`, `packets/`, `executions/`, `runtime/`): nunca el `.cdad/`
    raíz. El CLI no debe escribir en una raíz temporal declarada.
  - **C3** Está **ignorado de verdad** donde el propio layout lo declara:
    verificado en este repo, `git check-ignore -v .cdad/tmp` → `.gitignore:11:.cdad/`.
  - **C4** Si el proyecto **no** lo ignora, `prepare` falla cerrado y el
    diagnóstico nombra las dos salidas (PD-11): nunca hay temporal silencioso.
  - **C5** El validador de política ya garantiza que una raíz temporal no se
    solape con producto (`cdad_packet.py`:414-430); la clase no relaja eso (PD-13).
  *Alternativa declarada y no elegida:* una raíz de primer nivel (p. ej. `.tmp/`):
  no está ignorada por defecto, así que fallaría cerrado en más proyectos.
- **D-6 — Entrada única.** Consumir `status.entry`/`next` con el orden:

  | # | Condición (de la vista) | Acción única |
  |---|---|---|
  | 1 | `entry == diagnosis` | salida bloqueada: diagnóstico accionable; no se prepara ni despacha |
  | 2 | `continuity-reconcile` + paquete `dispatched` | reconciliar primero (`reconcile`, read-only); nunca re-despachar ni abrir un segundo worker |
  | 3 | `continuity-reconcile` + paquete `prepared` | validar → `begin` → transportar → `record` → `receive` |
  | 4 | `continuity-reconcile` + sin paquete + ejecución activa | `resume` y continuar el trabajo activo |
  | 5 | `next-unit` | `open-unit` |

  «Legacy/handoff» pasa a **fallback de transporte**; «arranque en reposo» es el
  camino previo hacia `project-start.md`. *Rechazadas:* mantener la prosa con
  precedencia (el solape persiste) y un campo nuevo de estado (la vista ya lo
  calcula).
- **D-7 — Espera.** Detección post-hoc + a lo sumo una lectura acotada bajo
  demanda; prevención por D-5. *Rechazada:* vigilar el store.
- **D-8 — Alcance del transporte externo.** El adaptador externo **consume el
  núcleo** y pierde su duplicación de I8 (hoy dos registros por despacho: PD-1).
  *Alternativa admisible:* dejarlo para una feature siguiente; se descarta por §12
  (duplicación que puede divergir) y porque el consumidor real del núcleo es lo
  que justifica su forma.

## 6. Desconocidos (V-n) y su resolución

- **V-1 (riesgo principal) — cómo obtiene el padre la sesión hija por la vía
  nativa.** Resolución: **sonda real acotada** (un despacho nativo mínimo,
  declarado y con el resultado registrado) **antes o durante U2**; el hallazgo se
  declara en `VERIFIED_VERSIONS`/`resolve_context`/`observe_session`.
  **Qué pasa si no se puede evaluar la llave «padre»:** (a) si el resultado
  nativo es byte-exacto, hay entrega con **garantía menor declarada** —
  `session: null` y `provenance` diciendo que la identidad no se pudo verificar
  (PD-6); (b) por la vía del store **no hay entrega** y la observación es
  `unknown` (PD-5). Nunca una entrega inventada.
- **V-2 — `time_idle`/`idle_outcome` en 0/null:** el fin de corrida **no** se
  exige en la vía nativa; la entrega depende del texto final del transporte.
- **V-3 — semántica de `external_directory` por versión:** la integración declara
  versión y falla cerrado fuera de ella (PD-7/PD-8); la prevención es D-5.
- **V-4 — título «## Delegation (adapter)» con contenido nativo
  (`scripts/cdad-generate.py`:747):** se corrige en U4.
- **V-5 — si el `task` nativo bloquea al padre y la semántica exacta del
  permiso:** sonda declarada; si queda desconocido, la espera es post-hoc y se
  declara (PD-16).
- **V-6 — condición stale de `.cdad/execution.json` en el mandato:** se corrige
  en U4.
- **V-7 — columnas reales de correlación en la versión instalada:** sonda antes
  del RED de U2; la forma citada proviene de 005-002 y el adaptador hoy exige un
  subconjunto menor.
- **V-8 — la propuesta de temporal cambia bytes de `propose_policy`:** se
  buscaron tests que fijen ese valor y **no se encontró ninguno** (los hallados
  son fixtures: `tests/test_003_003_t2_preflight.py`:105,
  `tests/test_004_002_t1_reviewfix.py`:125; y `tests/test_004_002_t6_landing.py`:374
  sólo parsea el JSON). Si el RED encuentra uno, se cambia **en RED declarando el
  reemplazo** (A-1).

## 7. Medición de la aceptación

- Se mide lo observado (versión, configuración, intentos, lecturas del store,
  tiempos, terminaciones) y se registra; **desconocido no es cero**.
- **No** se fijan reducciones porcentuales de locks, tokens ni tiempo.
- Un éxito del recorrido de U6 es evidencia **de ese recorrido**, no de que la
  contención esté eliminada.

## 8. Fuera de alcance

- La **integración Claude Code**: se deja **sólo la interfaz preparada** (§2.2);
  su módulo, su sección `delegation` y su guard quedan para después (plan §11).
- El transporte externo **más allá de que consuma el núcleo**; `install.sh`; los
  filtros de Bash; los ejecutores de acciones externas; la construcción incremental.
- La política del proyecto y `delegation.json` (datos del dueño): esta feature
  sólo cambia la **propuesta** de política.

## 9. Riesgos residuales

Contención del store (se mitiga, no se elimina aquí); deriva de esquema sin
`schema_version` (detección por columnas → fallo cerrado); mapas `edit` no
observados aplicados en la versión medida (por eso el temporal se declara, no se
confía al mapa); y V-1, que acota la garantía de identidad del recorrido nativo
hasta que se resuelva.

===== END docs/specs/006-005-native-path-parity/spec.md =====
```

```
===== BEGIN docs/specs/006-005-native-path-parity/plan.md (DRAFT — UNAPPROVED) =====
# 006-005-native-path-parity — PLAN (etapa 2)

Estado: **BORRADOR no aprobado**, insumo de la review independiente
(`plan-review` sobre `draft-plan`, enmienda 006) antes del RED.
Contrato: epic `plan.md` §11/§12. Spec: la de esta carpeta (misma entrega).
Base medida: HEAD `1e508ec` (los números de línea pueden correrse). Anonimización
como en la spec. Es un plan de feature: unidades, archivos, RED y gates.

## 1. Orden y dependencias

`U1 → U2`; `U3` y `U5` independientes de U2; `U4` al final (toca texto generado);
`U6` después de U1–U5. Ninguna unidad empieza sin su RED declarado y sin la
review de spec/plan hecha (PD-17).

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1** | Núcleo `cdad_dispatch.py` (`record` + `capabilities`) y el adaptador externo consumiéndolo (un solo I8) | — | PD-1…PD-6 | RED + focales GREEN + regresiones de delegación + `make validate` |
| **U2** | Integración OpenCode: contexto, agente, observación, correlación, fallo cerrado | U1 (contrato) | PD-5, PD-7…PD-9 | RED + focales con store descartable + regresiones del adaptador |
| **U3** | Temporal del test-writer: clase, política, propuesta, `git check-ignore` | — | PD-10…PD-13 | RED + focales de scope + regresiones de política/`prepare`/`receive` |
| **U4** | Entrada única del orquestador + secciones `delegation` + regeneración | U1–U3 (texto final del recorrido) | PD-15 | RED de texto + `make staging` determinista + `make validate` |
| **U5** | Camino mecánico a `failed` y desbloqueo verificado de `prepare` | — | PD-14 | RED + focales + regresiones de transiciones/estado |
| **U6** | Recorrido de aceptación de §11 en proyecto descartable | U1–U5 | PD-18 | recorrido con evidencia; regla de bloqueo (§5) |

## 3. Fichas por unidad

### U1 — Núcleo y consumo por el adaptador externo
- **Archivos:** nuevo `skills/cdad-cycle/scripts/cdad_dispatch.py`; el adaptador
  externo deja de tener su propia observación/registro
  (`skills/cdad-cycle/scripts/cdad_delegate_opencode.py`:1519-1618) y los delega
  al núcleo; la interfaz deja de registrar su propio intento
  (`skills/cdad-cycle/scripts/cdad_delegate.py`:396-398);
  `skills/cdad-cycle/references/cli-delegation.md` nombra el núcleo como el
  registrador único. **`install.sh` no se toca:** `install_skills` copia el árbol
  completo de la skill (`install.sh`:1093-1101), así que un módulo nuevo se
  instala sin enumerarlo.
- **RED:** `tests/test_006_005_u1_dispatch_core.py` (nuevo) — PD-1 (un solo
  intento; el adaptador no registra por su cuenta), PD-2 (el núcleo no escribe el
  state ni el store), PD-3 (`sha256` byte-exacto), PD-4 (sin texto final no hay
  entrega ni `receive`), PD-6 (`session: null` + `provenance` declarado),
  PD-1/PD-5 (sobre con `OUTPUT_KEYS` y `termination` del vocabulario cerrado).
- **Regresiones:** `tests/test_004_002_t4_dispatch.py`,
  `tests/test_005_007_t5_delegation_dispatch.py`,
  `tests/test_006_002_u5_transport_equivalence.py`,
  `tests/test_006_001_t1_selection.py`, `tests/test_006_001_t1b_service_mode.py`,
  `tests/test_006_001_t2_wait_recovery.py`,
  `tests/test_006_001_t3_integration.py`,
  `tests/test_006_001_t3_concurrency.py`,
  `tests/test_005_004_t1_dispatch_tool_name.py`, `tests/test_packet_prepare.py`.
- **Gate:** RED declarado y failing por la razón correcta; GREEN focal; las
  regresiones verdes; `make validate`.

### U2 — Integración OpenCode
- **Archivos:** nuevo `skills/cdad-cycle/scripts/cdad_runtime_opencode.py`
  (contrato §2.2 de la spec + `VERIFIED_VERSIONS`). Sonda de V-1/V-7 ejecutada y
  registrada antes de RED (o durante, si el RED fija primero el fallo cerrado).
- **RED:** `tests/test_006_005_u2_opencode_integration.py` (nuevo) — PD-5 (las
  cuatro llaves, una por caso, con el nombre de la llave fallida en el
  diagnóstico), PD-7 (`capabilities` fuera de versión), PD-8 (columna ausente →
  fallo cerrado nombrando las ausentes), PD-9 (`store_reads` ≤ techo y ausencia
  de intervalo/bucle). Fixture: store SQLite descartable, patrón de la receta de
  aislamiento (`skills/cdad-cycle/references/cli-delegation.md`:239+).
- **Regresiones:** `tests/test_cdad_adapters_opencode.py`,
  `tests/test_006_001_t1b_service_mode.py`,
  `tests/test_006_001_t2_wait_recovery.py`,
  `tests/test_003_003_t2_preflight.py`.
- **Gate:** focales verdes con store descartable; regresiones verdes.

### U3 — Temporal del test-writer
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — vocabulario de clases
  (`SCOPE_CLASSES`, :67), validador único de scopes (`_validate_scope`, :694 y el
  conjunto de escritura del test-writer en :729), pertenencia de un cambio
  observado (`_scope_contains`, :739, usado por el manifiesto en
  `cdad_result.py`:370), propuesta (`propose_policy`, :1088, hoy :1101) y el paso
  `git check-ignore` en `prepare` (zona de validación de opciones, ~:2036-2050).
  El detalle de forma es del implementer; el contrato son PD-10…PD-13.
- **RED:** `tests/test_006_005_u3_temporary_scope.py` (nuevo) — PD-10 (política
  vacía → rechazo nombrando `docs/cdad-policy.json`; con raíz declarada → acepta),
  PD-11 (`git check-ignore` negativo y positivo, y proyecto no-Git),
  PD-12 (recibo `scope_validation: passed` con test real + sonda temporal, y
  rechazo fuera de scope), PD-13 (raíz temporal solapada con producto → rechazo).
- **V-8 / regla A-1:** no se encontró test que fije el valor de la propuesta; si
  el RED encuentra uno, se cambia **en RED declarando el reemplazo**.
- **Regresiones:** `tests/test_004_002_t1_policy.py`,
  `tests/test_004_002_t1_reviewfix.py`, `tests/test_004_002_t2_bootstrap.py`,
  `tests/test_004_002_t6_landing.py`, `tests/test_004_002_t7_acceptance.py`,
  `tests/test_004_002_t7_private_paths.py`, `tests/test_003_002_t1_receive.py`,
  `tests/test_003_002_t2_materialize.py`, `tests/test_packet_prepare.py`.
- **Gate:** RED + focales; las regresiones de política y recepción verdes;
  `make validate`.

### U4 — Entrada única y secciones `delegation`
- **Archivos:** `sources/roles/orchestrator.md` (intake :22-57 con las cuatro
  entradas solapadas y la condición stale :24; disciplina de contexto :104-108),
  `sources/agents/adapters/opencode.md` (§`delegation` :60-94),
  `sources/agents/adapters/claude-code.md` (§`delegation` :80),
  `skills/cdad-cycle/references/re-entry.md`,
  `scripts/cdad-generate.py`:747 (etiqueta de la sección compuesta) y los agentes
  regenerados por `make agents` (salidas declaradas: nunca a mano, `Makefile`:1-24).
- **RED:** `tests/test_006_005_u4_single_entry.py` (nuevo) — PD-15: la
  fuente tiene el orden de cinco filas sin solapes y **sin** la condición
  `.cdad/execution.json`; el generado recomputado coincide byte a byte; la
  sección `delegation` nombra el registro del intento y la entrega.
- **Regresiones (todo test que lea orquestadores generados):**
  `tests/test_005_006_t2_intake.py` (ventanas ancladas a tokens declarados),
  `tests/test_006_002_u1_delegation_section.py`,
  `tests/test_006_002_u2_neutral_skill.py`,
  `tests/test_006_002_u3_runtime_references.py`,
  `tests/test_006_002_u6_context_discipline.py`, `tests/test_cdad_generate.py`,
  `tests/test_bash_policy_selection.py`,
  `tests/test_opencode_read_map_and_steps.py`,
  `tests/test_005_004_t2_installer_claims.py`,
  `tests/test_006_003_u3_texts_without_profiles.py`.
- **Gate:** `make staging` determinista (dos corridas, mismos bytes), RED de texto
  verde, regresiones verdes, `make validate`.

### U5 — Camino mecánico a `failed`
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — efecto de la clase
  `disposition` (hoy `pass`, :5584-5589) y la coherencia de `validate-state`
  (:6022). No se toca `_dispatched_packet_ids`/`_missing_required_deliveries`
  (:4855/:4944): leen el **ledger de despachos**, así que el cierre sigue
  satisfaciendo PD-8(a) por la disposición registrada.
- **RED:** `tests/test_006_005_u5_disposition_failed.py` (nuevo) — PD-14: paquete
  activo, sin recibo → `failed`; `validate-state` VALID; `prepare` bloqueado antes
  y desbloqueado después; con recibo durable ⇒ rechazo que nombra `receive`; y la
  disposición sigue sin aprobar nada (`approval_effect: false`, sin `approved_by`).
- **Test acoplado que cambia en RED declarando el reemplazo (A-1):**
  `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 afirma hoy que el
  paquete sigue `dispatched` tras la disposición. El reemplazo declarado:
  «`active_packet.status` pasa a `failed` (terminal); el resto del estado sigue
  intacto». Se revisa además que el flujo B1 (:835) siga avanzando.
- **Regresiones:** `tests/test_005_012_t1_register_transition_base.py`,
  `tests/test_005_012_t3_closure_dispatch_resolution.py`,
  `tests/test_005_012_t4_late_delivery.py`,
  `tests/test_005_001_t2_replace_packet.py`, `tests/test_005_001_t3_idle.py`,
  `tests/test_006_003_rf_review_fixes.py`,
  `tests/test_006_003_rf2_review_fixes.py`, `tests/test_packet_prepare.py`.
- **Gate:** RED + focales; regresiones verdes; `make validate`.

### U6 — Recorrido de aceptación (no es unidad de código)
- **Escenario (§11/PD-18):** proyecto **descartable** con layout anidado; el
  coordinador iniciado **desde otra carpeta**; agente **global** y configuración
  de **proyecto** declarados distintos (garantía menor declarada); un auxiliar
  temporal necesario; **un test real escrito y recibido** (recibo `pending`,
  `scope_validation: passed`); **un intento interrumpido** registrado sin entrega
  y llevado a `failed` **por comando**.
- **Evidencia:** los archivos de intento I8, el recibo, el estado resultante y la
  versión/configuración observadas. Sin generalizar (spec §7).
- **Regla de bloqueo por ambiente:** si el ambiente no puede ejecutar el
  recorrido (runtime ausente, versión fuera de las verificadas, store no
  disponible), la unidad se declara **BLOQUEADA** con el motivo y la evidencia
  del intento; **no** se sustituye por una corrida simulada, por un éxito
  inventado ni por «debería funcionar». Decide el dueño/orquestador (autorizar,
  re-scopear o re-rutear).

## 4. Regla A-1 (tests acoplados)

Un test acoplado a la superficie que cambia se modifica **sólo en el RED de su
unidad**, declarando en el propio RED: (1) el test que se reemplaza, (2) la
postcondición nueva que lo reemplaza, (3) la razón. Nunca en GREEN, nunca por
invisibilizar un fallo. Aplica a U5 (test citado arriba), a U4 (tests de texto de
los generados) y a U3 (V-8: ningún test encontrado hoy que fije el valor de la
propuesta).

## 5. Cierre

Review independiente de spec/plan **antes** del RED (PD-17). Al cerrar el código:
`make validate` y la **suite completa una vez** (`pytest tests/`), corrida por
quien cierra (política declarada); se repite sólo si cambios o evidencia
invalidada lo justifican. Review formal del resultado en sesión independiente; el
recorrido real de U6 (AC-7) queda declarado con su estado, y no se acredita
aceptación real por pruebas aisladas.
```
===== END docs/specs/006-005-native-path-parity/plan.md =====
```

---

## Evidencia del rol (architect · substage `draft` · read-only)

**Archivos modificados: ninguno. Commit: ninguno.** Write scope vacío: todo se
entrega como texto final para que el orquestador/dueño materialice los
documentos (ADR-003).

Comandos ejecutados (extracto literal; salidas resumidas):

```
$ git rev-parse HEAD
1e508ec724a3b2c4e2150eee798e16afe7c54a60          # el discovery midió af0e0b5: HEAD se movió

$ git status --porcelain
 M docs/.cdad-state.json                            # preexistente (bootstrap del orquestador), no mío
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md

$ ls docs/specs/006-005-native-path-parity/
discovery.md                                        # no existe spec previa (confirmado)

$ python3 skills/cdad-cycle/scripts/cdad_packet.py status --project-root .   # read-only
{"entry":"continuity-reconcile","next":{"route":"reconcile the dispatched packet before repeating
 (resume)","source":"docs/.cdad-state.json:active_packet.status"},"packet":
 {"id":"006-005-native-path-parity-architect-draft-001","role":"architect","status":"dispatched",
 "substage":"draft"},"feature":{"active_feature":"006-005-native-path-parity",
 "current_stage":"discovery","tdd_substage":null}}

$ git check-ignore -v .cdad .cdad/tmp .cdad/inbox
.gitignore:11:.cdad/	.cdad
.gitignore:11:.cdad/	.cdad/tmp
.gitignore:11:.cdad/	.cdad/inbox

$ cat docs/cdad-policy.json        # temporary_roots vigentes en ESTE repo
"temporary_roots": []
```

Símbolos verificados con `grep -n`/`sed -n` (el paquete no cambia por citar
líneas, pero cada afirmación de la spec tiene símbolo + archivo):

```
cdad_packet.py:44 VALID_PACKET_STATUSES · :67 SCOPE_CLASSES · :115 ACTIVE_PACKET_STATUSES
:122-124 ENTRY_* · :145 POLICY_KEYS · :148 CLASS_BY_TOKEN · :239 classify_path
:303-322 classify_path_observable (devuelve "temporary") · :414-430 _validate_temporary_roots
:433-450 _validate_policy_document · :694 _validate_scope · :729 test-writer write = {tests, colocated-tests}
:739-753 _scope_contains · :1088/:1101 propose_policy / temporary_roots: [] · :2043 _scope_contains en prepare
:2094-2103 PD-10 replace-packet · :2371 OBSERVATION_KEYS · :2410-2445 _load_observation_document (provenance)
:2501-2512 _record_dispatch (prepared→dispatched) · :4337 PD-4 bloqueo de prepare · :4855 _dispatched_packet_ids
:4881 _packet_has_disposition · :4944 _missing_required_deliveries · :5205-5213 rechazo que nombra receive
:5584-5589 efecto del disposition = pass · :5797 _pending_work · :5828 _entry_selection · :5847 _next_route
:5886 status_view · :6022 validate-state

cdad_result.py:67/:69 RESULTS_RELPATH/INBOX_RELPATH · :305 _validate_manifest · :340 _validate_scope
:370 usa cdad_packet._scope_contains · :578-581 precondición de receive ("is not dispatched")
:1305-1318 manifiesto con git ls-files --cached --others --exclude-standard

cdad_delegate.py:49-51 TERMINATION_VOCABULARY/OUTPUT_KEYS · :385-405 delegate() · :396-398 registro propio (I8 #2)
cdad_delegate_opencode.py:113 DERIVED_AGENTS_RELPATH · :302-325 _check_derived_agent_published
:621-623 sqlite3.connect("file:…?mode=ro") · :741-790 _prior_attempt_check · :1519-1568 _observation
:1584-1618 _register_dispatch (I8 #1) · :1727 lo invoca · :1755-1759 corre receive

sources/roles/orchestrator.md:22-57 (cuatro entradas solapadas; :24 condición stale .cdad/execution.json)
:104-108 disciplina de contexto · :141-148 wiring de re-entry
sources/agents/adapters/opencode.md:60-94 (§delegation, sin nombrar record-dispatch)
sources/agents/adapters/claude-code.md:80 (§delegation)
scripts/cdad-generate.py:747 ("## Delegation (adapter)") · install.sh:1093-1101 (copia el árbol completo de la skill)
Makefile:1-24 (staging/agents/validate) · docs/specs/005-012-transition-registration/spec.md:243 y :587 (INV-9)
```

Contrastes que la spec declara y que el repo acredita:

```
$ grep -rn "record-dispatch" skills/cdad-cycle/references/
orientation.md:34   orientation.md:72   project-execution.md:135/:240   cli-delegation.md:15
project-start.md:127        # re-entry.md: sin coincidencias → la vía nativa no lo nombra

$ grep -rn "propose_policy\|temporary_roots" tests/*.py
tests/test_004_002_t1_policy.py:204 (propuesta determinista, sin fijar el valor)   → V-8 acotado
tests/test_003_003_t2_preflight.py:105 · tests/test_004_002_t1_reviewfix.py:125 (fixtures)
tests/test_004_002_t6_landing.py:374 (parsea el JSON de la propuesta)

$ grep -n "after_packet.get(\"status\") == \"dispatched\"" tests/test_005_012_t3_closure_dispatch_resolution.py
812:        "PD-21/INV-9 violada: la disposición NO fabrica un estado terminal del paquete"
     # → test ACOPLADO al efecto actual: se cambia en RED declarando el reemplazo (A-1)
```

**Conflictos y cosas que no pude cerrar (declaradas, no resueltas por mí):**

1. **D-4/PD-14 enmienda una invariante aprobada.** `005-012` spec:243 y su INV-9
   (`:587`) declaran que la disposición **no** cambia `active_packet`, y hay un
   test que lo fija (`test_005_012_t3_closure_dispatch_resolution.py`:745-830).
   La spec lo dice explícitamente y pide aprobación explícita del dueño; no la doy
   por concedida.
2. **V-1 y V-7 siguen desconocidos:** no inventé la forma en que el padre obtiene
   la sesión hija; la spec define la sonda y qué pasa si no es evaluable (garantía
   menor declarada / `unknown`, nunca entrega inventada).
3. **V-5 (semántica del permiso y del bloqueo del `task`) no se puede acreditar
   desde el repo**: declarado como desconocido con su consecuencia (espera
   post-hoc, reporte `unknown` cuando no es observable).
4. **Deriva de números de línea:** el discovery midió `af0e0b5`; medí `1e508ec`
   (los símbolos coinciden; los rangos citados pueden correrse).
5. **No leí** `tests/.sensitive-patterns.local`; no toqué `~/.claude`, `~/.config`,
   servicios, el store vivo ni el state; no ejecuté `git stash`; no escribí,
   commiteé ni instalé nada.

Ambos documentos quedan **sin aprobar** para la decisión explícita del usuario
(precedida, si se sigue la enmienda 006, por la review independiente
`plan-review` sobre este borrador).