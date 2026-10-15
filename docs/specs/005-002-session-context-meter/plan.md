> Plan **en borrador** (2026-10-11), texto del **architect** (subetapa `draft`, etapa 2), para su
> materialización por el orquestador (ADR-003). Se aprueba **junto con la spec** (una sola acción);
> el architect **no** aprueba su propia propuesta. **draft-002**: ronda acotada de corrección
> **C6** sobre el draft 001 (alinea T1/T2/T3 con C1–C4 de la spec); el resto del draft 001 se
> conserva íntegro. Construcción según CDAD stages 3–5 (TDD con test-writer/implementer por paquete,
> una única review formal al final y Memory Bank al cierre). Insumo:
> `docs/specs/005-002-session-context-meter/discovery.md` (intacto, no se repite) +
> `docs/specs/005-002-session-context-meter/draft-inputs-2026-10-11.md`. Formato canónico de la
> ficha y del bloque `plan-tasks`: **por referencia**,
> `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4 y §4.1 (NO se reproduce
> aquí). Contrato: `docs/epics/epic-005-real-operation/plan.md` (fila 7, `:40`, y «Ajuste», `:45-85`).

## Plan — 005-002-session-context-meter

**Feature ID:** `005-002-session-context-meter` · **Epic:** `epic-005-real-operation` ·
**Estado:** borrador (2026-10-11).

### Ajuste de las unidades propuestas al discovery/delta

- El **registro neutral + adaptador + fallo cerrado + solo-lectura/determinismo + empaquetado +
  contrato de invocación + claves requeridas** son **un solo átomo** verificable con su RED→GREEN:
  el lector que emite un registro válido, expone la superficie de invocación observable (PD-15) y
  falla cerrado → **T1**.
- Los **hitos, el corte con el borde fijado, las lecturas de orientación y las tres magnitudes**
  (V1/V2) son un segundo átomo, en el **mismo archivo** de producto → **T2** (secuencial,
  `depends_on` T1).
- El **informe de aplicación (forma de la referencia, C4), la privacidad y la salida compacta** son
  un tercer átomo, en el mismo archivo + el reference → **T3** (secuencial, `depends_on` T2).
- La **aceptación** (reproducción de muestras + S-BOOT-04 opcional + sesión de cierre V6 + suite)
  consume T1/T2/T3 → **T4**.

Resultado: **T1 → T2 → T3 → T4** (secuencial: comparten el archivo de producto y su contrato; la
review puede rechazar una tarea sin rechazar la anterior). El reference (`context-meter.md`) se crea
en T1 y se completa en T3.

### Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**.
- **No** instalar CDAD en HOME ni activar versiones, ni operar producción (reservado al dueño). **No**
  ejecutar el CLI del repo para **operar** este ciclo (el repo se **desarrolla**; el ciclo corre con
  la instalación vigente).
- **No** leer `tests/.sensitive-patterns.local`.
- Para comprobar un RED sin el arreglo: **worktree**, nunca `git stash` en el árbol compartido.
- No volcar salidas enormes al contexto. **No** comunicar procesos por `/tmp`.
- **Sin valores de este VPS** en producto ni en contratos publicables (INV-7): la configuración llega
  por config de ejecución (local, git-ignorada) o flags; los identificadores reales se resuelven en
  registros locales. La prohibición cubre **rutas del host, ruta del store, proveedor, modelo e
  identificadores de sesión**; el tamaño del store y los agregados ya publicados se citan **por
  referencia** (C5).
- **Lectura de la base real acotada y read-only** (`?mode=ro`, por sesión/ventana); **nunca**
  checkpoint-ear; store de 4,67 GB + WAL de 543 MB (PD-11; tamaños citados por referencia).
- **Gate de tests (metodología común, dueño único `stage-3-tdd.md` §«Test evidence policy»).**
  Durante el trabajo: **focales + módulos tocados**. **Suite completa al cierre de la feature** (toca
  `skills/**` y `tests/**`), más `make validate` al cierre. Sin duplicar la regla.
- **Frontera:** **no** motor de evaluación de sesiones, **no** dashboard, **no** scheduler, **no**
  plataforma de usabilidad; **no** se clasifican repeticiones de suites/fricción de permisos/
  correcciones tras review/intervenciones humanas (exige juicio). Ante un obstáculo fuera del ámbito:
  entregar el diagnóstico, no fabricar métricas ni registros.

### Tareas

#### T1 — Registro neutral, adaptador OpenCode read-only, contrato de invocación, fallo cerrado y empaquetado · PD-1, PD-2, PD-3, PD-4, PD-11, PD-13, PD-15, PD-16 · INV-1, INV-2, INV-3, INV-4, INV-5, INV-6
- **Files**:
  - `skills/cdad-cycle/assets/context-meter.schema.json` (**New**): el **contrato neutral**
    (`context-meter-v1`) con los cubos `observed`/`estimated`/`unknown` y su **regla de asignación**,
    `run`/`window`/`sessions`/`roles`/`application`/`unknowns`, y las **claves requeridas** de
    `milestones`/`measures`/`buckets` con sus obligatoriedades (PD-16), **sin** nombres de
    tablas/columnas del runtime.
  - `skills/cdad-cycle/scripts/cdad_context_meter.py` (**New**, canónico): lector SQLite
    **`?mode=ro`**; **detección de esquema** por **columnas requeridas + tipos de fila** (sin
    `schema_version`) → **fallo cerrado** con diagnóstico que **nombra** el faltante y **ningún
    número**, `rc != 0`; emite el **registro neutral**; **sin** conversión bytes→tokens ni límite
    fabricado; `cache_write`/nulos → `unknown`; JSON único, stdlib, determinista; acepta la
    **superficie de invocación** `--store`/`--session`/`--limit`/`--idle-threshold`/`--json` (PD-15).
  - `scripts/cdad_context_meter.py` (**New**, wrapper fino): `runpy.run_path(CANONICAL, …)`.
  - `skills/cdad-cycle/references/context-meter.md` (**New**): procedimiento y semántica de los
    cubos; **no** enganchado en gates (se completa en T3).
  - `tests/test_005_002_t1_neutral_record.py` (**New**): fixtures SQLite chicos con el esquema
    observado y variantes (`unknown-schema` por columna faltante → fallo cerrado; sesión sin tokens →
    cubos `unknown`); validación contra el asset (claves requeridas y cubos, PD-16); determinismo
    byte-idéntico; store sin cambios tras la lectura; **contrato de invocación** (PD-15): el wrapper
    acepta `--store`/`--session`/`--limit`/`--idle-threshold`/`--json`, emite **JSON por stdout**,
    devuelve `rc = 0`/`rc != 0` con **diagnóstico por stderr**, y sin store ni variable de entorno el
    diagnóstico **nombra el insumo faltante**.
- **Produce**: `registro-neutral-lector-opencode` (`spec-005-002-PD1-PD2-PD3-PD4-PD11-PD13-PD15-PD16`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: —.
- **TDD steps**: RED (no existe el adaptador; un registro que mezcle cubos o incluya nombres de
  tablas no valida; un esquema incompleto no falla cerrado; el wrapper no acepta los flags declarados
  ni emite JSON por stdout ni devuelve `rc != 0` en fallo cerrado) → GREEN (mínimo: lector RO +
  detección + registro neutral + superficie de invocación) → focales + módulos tocados.
- **Observable checks / criterio de prosa**: además del test estructural, el asset declara las
  **claves requeridas** y la **regla de cubos** (una métrica en exactamente uno); la prosa del
  reference (T1) no fija frases ni nombres internos ni valores del VPS.
- **Evidencia**: salida de `pytest` focal; el fixture y sus variantes; el asset validando el registro
  (claves requeridas y cubos); el diagnóstico de `unknown-schema` (nombra el faltante, sin número,
  `rc != 0`); el **contrato de invocación** (flags aceptados, JSON por stdout, `rc`, diagnóstico por
  stderr, sin store/variable → nombra el insumo faltante); dos corridas byte-idénticas; store sin
  cambios.

#### T2 — Hitos, lecturas de orientación, corte con el borde fijado (C3) y tres magnitudes · PD-5, PD-6, PD-7, PD-8 · INV-4, INV-9
- **Files**:
  - `skills/cdad-cycle/scripts/cdad_context_meter.py` (**Modify**): **dos hitos** separados
    (`first_resume` = `shell` que invoca el subcomando `resume`, **excluyendo** `--help`/`-h`;
    `first_dispatch` = primer evento de despacho de rol observable, p. ej. `subagent`), ausente →
    `unknown`; **corte explícito con el borde fijado** (ventana por medición; línea base = primer
    tramo contiguo cortado en la primera brecha > `--idle-threshold`; **último paso = el mensaje
    `assistant` que cierra el tramo**, sin llamada de herramienta propia; cierre en el `idle`
    `succeeded`; métricas por tramo, sin promediar); **medidas** de orientación (tiempo hasta el
    hito, llamadas y lecturas previas, salidas total y máxima, input por paso, acumulado y caché) y
    **tres magnitudes** con unidad/intervalo/procedencia.
  - `tests/test_005_002_t2_milestones.py` (**New**): fixture que reproduce la **sonda 2** (primer
    `resume` #19; 18 antes; 8 `read`, 2 `glob`, 8 `shell`; `resume --help` excluida) y la **muestra
    1** con el **borde fijado en C3**: el **último paso es el mensaje `assistant` que cierra el
    tramo** (sin llamada de herramienta propia) → **12,55 min / 203.276 tok**; el **borde
    alternativo** (último mensaje **con** herramienta → **12,40 min / 202.222 tok**) se hace
    **visible** y se declara **NO usado** (un fixture que tome ese borde debe fallar); el tramo cierra
    en el `idle` `succeeded` previo a la brecha; **sin brecha > umbral, toda la sesión es un tramo**;
    S-BOOT-04 como variante de **primer despacho** (`subagent`); un `write` cuyo contenido menciona
    «resume» **no** cuenta.
- **Produce**: `hitos-orientacion-corte` (`spec-005-002-PD5-PD6-PD7-PD8`).
- **Consume**: `registro-neutral-lector-opencode` (`spec-005-002-PD1-PD2-PD3-PD4-PD11-PD13-PD15-PD16`, producer T1).
- **Depends_on**: T1. **Parallel**: —.
- **TDD steps**: RED (el registro de T1 no expone hitos ni corte; el total y el conteo de `read` no
  se distinguen; la sesión completa se mezcla con el tramo; **el fixture que toma el borde en el
  último mensaje con herramienta da 12,40/202.222 y debe fallar**) → GREEN (mínimo: hitos + corte con
  borde fijado + medidas) → focales + módulos tocados.
- **Observable checks / criterio de prosa**: el fixture **declara** la definición del borde usada y
  hace visible el número alternativo no usado.
- **Evidencia**: salida de `pytest` focal; los hitos por fixture; el corte con la diferencia
  tramo-vs-sesión **visible** y el borde alternativo declarado **NO usado**; las tres magnitudes
  separadas con su procedencia.

#### T3 — Informe de aplicación (forma de la referencia, C4), privacidad y salida compacta · PD-9, PD-10, PD-12 · INV-7, INV-8
- **Files**:
  - `skills/cdad-cycle/scripts/cdad_context_meter.py` (**Modify**): anotación `application`
    **referenciada** con la **forma fijada** `{ ref (referencia durable: ruta/commit/recibo, **no**
    copia del contenido), limit ∈ {accepted, blocked, pending, unknown} desde hechos observables,
    basis (hechos observables), included_sessions/relations opcionales }`; el lector **nunca**
    aprueba; declarar sesiones incluidas y relaciones observadas; sin doble conteo; enlaces no
    verificables `unknown`; **privacidad** (omitir/hashear rutas e identificadores; sin prompts/salidas
    crudas); **salida compacta** bajo un límite de bytes declarado, con referencias (sesión + paso/seq)
    a la evidencia original.
  - `skills/cdad-cycle/references/context-meter.md` (**Modify**): documenta la anotación de
    aplicación (no-juez; forma `ref`/`limit`/`basis`), la privacidad y el límite de tamaño; **sin**
    valores del VPS.
  - `tests/test_005_002_t3_application_privacy.py` (**New**): `application.ref` es una **referencia
    durable** y **no** una copia del contenido; `limit` deriva de **hechos observables** y `basis` los
    declara; la anotación es referenciada y **no** una entrada de gate; el lector **no** aprueba; un
    par padre/hijo **no** duplica costo; un enlace no verificado es `unknown`; la salida **no**
    contiene ruta absoluta, ruta de store, proveedor, modelo concreto ni `ses_*`; el tamaño está bajo
    el límite y hay referencias a la evidencia.
- **Produce**: `informe-aplicacion-privacidad` (`spec-005-002-PD9-PD10-PD12`).
- **Consume**: `hitos-orientacion-corte` (`spec-005-002-PD5-PD6-PD7-PD8`, producer T2).
- **Depends_on**: T2. **Parallel**: —.
- **TDD steps**: RED (no hay anotación; no existe la forma `ref`/`limit`/`basis`; la salida filtra
  identificadores; no hay límite de tamaño) → GREEN (mínimo: anotación + privacidad + compactación) →
  focales + módulos tocados.
- **Observable checks / criterio de prosa**: además del test estructural, la prosa del reference se
  verifica por **review** (no fija frases ni nombres internos; no lleva valores del VPS).

#### T4 — Aceptación: reproducción de muestras, S-BOOT-04 opcional y sesión de cierre (V6) · PD-14 + criterios de aceptación · INV-5, INV-8
- **Files**:
  - `skills/cdad-cycle/scripts/cdad_context_meter.py` (**Modify**, mínimo): el **criterio de la
    sesión de cierre de 005-001** (documentado por evidencia, o `unknown` con causa + ítem abierto).
  - `skills/cdad-cycle/references/context-meter.md` (**Modify**): criterio de corte y de identificación
    de muestras; registro del ítem abierto de la sesión de cierre.
  - `tests/test_005_002_t4_acceptance.py` (**New**): reproduce **muestra 1** y **sonda 2** sobre
    **fixtures fieles** (deterministas); la verificación sobre la **base real** (read-only, acotada)
    es **integración** y se **omite por defecto** si no hay base, con diagnóstico (no fabrica verde);
    S-BOOT-04 **opcional** por variable de entorno.
- **Produce**: `aceptacion-reproduccion` (`spec-005-002-PD14-ACEPTACION`).
- **Consume**: `registro-neutral-lector-opencode` (T1), `hitos-orientacion-corte` (T2),
  `informe-aplicacion-privacidad` (T3).
- **Depends_on**: T1, T2, T3. **Parallel**: —.
- **TDD steps**: RED (sin la base/variable la prueba de integración se omite; los fixtures aún no
  reproducen los valores) → GREEN es de T1/T2/T3 (aquí no hay producto nuevo) → focales.
  - **Gate de integración (real, no unitario):** reproducción de las **dos muestras** sobre la base
    real **en solo lectura** (12,55 min / 101 llamadas / 51.243 car. / 203.276 tok; primer `resume`
    #19) + **suite completa** + `make validate`. Registra la evidencia y confirma V1/V3/V11.
- **Owner**: test-writer (fixtures; módulo de integración omitido por defecto); orquestador/architect
  (verificación sobre la base real).

### Bloque canónico `plan-tasks`

Formato: **por referencia**, `docs/epics/epic-004-single-source-planning/planning-contract-draft.md`
§4.1 (campos `tasks`/`validation_strategy`; por tarea `id`, `produce`, `consume`, `depends_on`,
`parallel`, `files`, `focal_tests`/`observable_checks`, `regressions`, `integration_gate`, `owner`;
estrategia común referenciada con `@validation_strategy`).

```plan-tasks
{"validation_strategy": "focales + modulos tocados durante el desarrollo; suite completa al cierre de la feature; regresiones del area tocada; make validate al cierre",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "registro-neutral-lector-opencode", "contract": "spec-005-002-PD1-PD2-PD3-PD4-PD11-PD13-PD15-PD16"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/assets/context-meter.schema.json",
             "skills/cdad-cycle/scripts/cdad_context_meter.py",
             "scripts/cdad_context_meter.py",
             "skills/cdad-cycle/references/context-meter.md",
             "tests/test_005_002_t1_neutral_record.py"],
   "focal_tests": ["tests/test_005_002_t1_neutral_record.py"],
   "observable_checks": ["el wrapper acepta --store/--session/--limit/--idle-threshold/--json, emite JSON por stdout, devuelve rc=0/rc!=0 con diagnostico por stderr y sin store ni variable de entorno nombra el insumo faltante (PD-15); el asset declara las claves requeridas de milestones/measures/buckets y la regla de cubos, sin nombres de tablas/columnas del runtime (PD-16)"],
   "regressions": ["tests/test_003_004_t1_resume.py",
                   "tests/validate-consistency.sh"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "hitos-orientacion-corte", "contract": "spec-005-002-PD5-PD6-PD7-PD8"}],
   "consume": [{"artifact": "registro-neutral-lector-opencode", "contract": "spec-005-002-PD1-PD2-PD3-PD4-PD11-PD13-PD15-PD16", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_context_meter.py",
             "tests/test_005_002_t2_milestones.py"],
   "focal_tests": ["tests/test_005_002_t2_milestones.py"],
   "observable_checks": ["el fixture reproduce el borde fijado en C3 (ultimo paso = mensaje assistant que cierra el tramo, sin llamada de herramienta propia) -> 12,55 min / 203.276 tok; el borde alternativo (ultimo mensaje con herramienta -> 12,40 min / 202.222 tok) se hace visible y se declara NO usado"],
   "regressions": ["tests/test_005_002_t1_neutral_record.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "informe-aplicacion-privacidad", "contract": "spec-005-002-PD9-PD10-PD12"}],
   "consume": [{"artifact": "hitos-orientacion-corte", "contract": "spec-005-002-PD5-PD6-PD7-PD8", "producer": "T2"}],
   "depends_on": ["T2"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_context_meter.py",
             "skills/cdad-cycle/references/context-meter.md",
             "tests/test_005_002_t3_application_privacy.py"],
   "focal_tests": ["tests/test_005_002_t3_application_privacy.py"],
   "observable_checks": ["application.ref es una referencia durable (ruta/commit/recibo) y NO una copia del contenido; limit en {accepted,blocked,pending,unknown} deriva de hechos observables y basis los declara; el lector no aprueba (C4); la prosa del reference documenta la anotacion de aplicacion, la privacidad y el limite de tamano, y no fija frases ni nombres internos ni valores del VPS"],
   "regressions": ["tests/test_005_002_t1_neutral_record.py",
                   "tests/test_005_002_t2_milestones.py",
                   "tests/validate-consistency.sh"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "produce": [{"artifact": "aceptacion-reproduccion", "contract": "spec-005-002-PD14-ACEPTACION"}],
   "consume": [{"artifact": "registro-neutral-lector-opencode", "contract": "spec-005-002-PD1-PD2-PD3-PD4-PD11-PD13-PD15-PD16", "producer": "T1"},
               {"artifact": "hitos-orientacion-corte", "contract": "spec-005-002-PD5-PD6-PD7-PD8", "producer": "T2"},
               {"artifact": "informe-aplicacion-privacidad", "contract": "spec-005-002-PD9-PD10-PD12", "producer": "T3"}],
   "depends_on": ["T1", "T2", "T3"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_context_meter.py",
             "skills/cdad-cycle/references/context-meter.md",
             "tests/test_005_002_t4_acceptance.py"],
   "focal_tests": ["tests/test_005_002_t4_acceptance.py"],
   "regressions": [],
   "integration_gate": "reproduccion de las dos muestras sobre la base real en solo lectura (12,55 min / 101 llamadas / 51.243 car. / 203.276 tok; primer resume #19) + S-BOOT-04 opcional por variable de entorno + suite completa + make validate",
   "owner": "test-writer (fixtures; modulo de integracion omitido por defecto); orquestador/architect (verificacion sobre la base real)"}
  ]}
```

### Auto-revisión del plan

- **Cobertura**: PD-1/PD-2/PD-3/PD-4/PD-11/PD-13/**PD-15/PD-16** → T1; PD-5/PD-6/PD-7/PD-8 → T2;
  PD-9/PD-10/PD-12 → T3; PD-14 + criterios → T4. Sin PD huérfano; sin tarea sin PD. INV-1/INV-2/
  INV-3/INV-4/INV-5/INV-6 → T1; INV-4/INV-9 → T2; INV-7/INV-8 → T3; INV-5/INV-8 → T4.
- **Grafo**: sin ciclos. T1 raíz; T2 consume T1 (mismo archivo, secuencial); T3 consume T2 (mismo
  archivo + reference); T4 consume T1/T2/T3.
- **Paralelismo seguro**: ninguno dentro del archivo de producto (secuencial por diseño); el reference
  se crea en T1 y se completa en T3.
- **Aislamiento de roles**: los tests expresan la capacidad **observable** sobre artefactos
  durables (fixtures SQLite, el registro neutral validado por el asset, **la superficie de invocación
  del wrapper**, las referencias, la salida); el test-writer **no** lee la implementación ni fija
  nombres de funciones internas.
- **Contratos compatibles**: los nombres (`context-meter-v1`, `context-meter.schema.json`,
  `context-meter.md`, `cdad_context_meter.py`, `session_v2`, `session_message`, `first_resume`,
  `first_dispatch`, `observed/estimated/unknown`, `application`, `--store`, `--session`, `--limit`,
  `--idle-threshold`, `CDAD_CONTEXT_METER_STORE`) son idénticos a la spec y a lo verificado en el
  discovery.
- **Verificación independiente**: el **asset neutral** valida el registro; la reproducción de las
  muestras sobre la **base real** (read-only) es la evidencia de integración; no se compara el
  producto consigo mismo.
- **Placeholders**: ninguno. **Una sola review formal** al cierre (stage 4).

### Riesgos registrados

- **R1 (alto) — esquema no público / versión.** Mitigación: D3/PD-2 (columnas/tipos requeridos, fallo
  cerrado); T1 + T4.
- **R2 (medio) — una sonda por variante → indicativa, no estadística.** Mitigación: declarar la
  muestra; no promediar (PD-5/PD-7); T2.
- **R3 (alto) — privacidad (rutas, prompts, salidas).** Mitigación: PD-10/D9; T3 + review.
- **R4 (medio) — tamaño del store / WAL.** Mitigación: PD-11/D10 (RO, acotado, sin checkpoint); T1.
- **R5 (medio) — ambigüedad de métrica y del borde.** Mitigación: definiciones cerradas
  (PD-5/PD-6/PD-7), borde fijado (C3) con el alternativo declarado NO usado, y discrepancia 8 vs 9
  **visible**; T2.
- **R6 (medio) — neutralidad.** Mitigación: PD-1/D1 (registro sin nombres del runtime); T1.
- **R7 (bajo) — doble conteo coordinador+workers.** Mitigación: PD-9 (declarar sesiones y
  relaciones); T3.

### Aprobación

- **Aprobado (2026-10-11)** por el **orquestador OpenCode**, bajo la **delegación HITL del epic-005**
  (`docs/epics/epic-005-real-operation/execution.md`), **junto con la spec** (una sola acción).
  **Decisiones adoptadas: D1–D12** de la spec §7. **Sin enmiendas al aprobar**. **draft-002**:
  corrección **C6** (T1 con el contrato de invocación y las claves requeridas; T2 con el borde fijado
  en C3; T3 con la forma de la referencia de C4). El bloque `plan-tasks` se validó con el validador
  del CLI instalado (4 tareas, productor/consumidor, sin ciclos, secuencial, plan de validación por
  tarea). El architect **no** aprobó su propia propuesta (anti-sesgo).
- Status: Approved by orquestador OpenCode (HITL delegada epic-005) on 2026-10-11
