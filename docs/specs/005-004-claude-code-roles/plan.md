> Plan **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR.** Texto del **architect**
> (`mofgw/deepseek-v4.1-flash`). Se aprueba **junto con la spec** por el **orquestador
> OpenCode** bajo la HITL delegada del epic-005 (`docs/epics/epic-005-real-operation/execution.md`),
> o por el **dueño**; el architect **no** aprueba su propia propuesta (anti-sesgo). Contrato:
> `docs/epics/epic-005-real-operation/plan.md`, fila 10 (`:43`), sha256
> `b22bc687e327c8524ab55f44ae8df65b06076bcc628e373b5e274a54906bec16`, más la sección
> «Ajuste de los ciclos pendientes» (`:77-78`). Deriva del discovery ya recibido y verificado
> (`docs/specs/005-004-claude-code-roles/discovery.md`, secciones (a)-(g)). El bloque canónico
> `plan-tasks` de §4 sigue el formato vigente (`docs/specs/005-007-progressive-planning/plan.md`
> §4, que referencia `docs/epics/epic-004-single-source-planning/planning-contract-draft.md`
> §4.1) y se validó con las funciones del propio CLI en solo lectura. **Sin valores de este
> VPS; sin rutas absolutas del dueño ni ids crudos de sesión** (`<home>`, `<repo>`, `<tmp>`,
> `<ses-…>`).

# Plan — 005-004-claude-code-roles

## 1. Ficha de la feature

- **Feature ID:** `005-004-claude-code-roles` · **Epic:** `epic-005-real-operation` · **Estado:** DRAFT (etapa 2).
- **Resultado buscado (fila 10, `plan.md:43`):** roles CDAD **activos en Claude Code para este proyecto**, sin tocar HOME salvo decisión del dueño (confianza de carpeta, copias viejas); **un ciclo corto real despachado desde Claude Code con la versión instalada al empezar el ciclo**.
- **Alcance obligatorio del encargo (a)-(f), cubierto por este plan:**
  - (a) herramienta de despacho: la fuente del adaptador y el derivado discrepan entre `Task` y `Agent` → **T1** (resuelve la real y cómo se verifica).
  - (b) afirmaciones del instalador sobre CC, en particular «the installer STRIPS the model field at install time» → **T2** (corrección de texto + verificación).
  - (c) chequeo de versión del lado CC (`cdad-version-check.py` sin pata CC) → **T3**.
  - (d) hooks de CC por rol, su raíz y qué se verifica sin sesión viva → **T4**.
  - (e) procedencia de modelo y de versión bajo el perfil vigente `basic` (reviewer≠implementer no garantizada; el guard la exime) → **T2** (declaración) + **T5** (evidencia del recorrido).
  - (f) recorrido real corto despachado desde Claude Code con la versión instalada al empezar, con recepción CDAD → **T5** (gate).
- **Decisión de alcance (D-1 del spec):** el cuerpo es el **enfoque B** del discovery (§(d)) —roles CC **nativos** (`Agent` / `subagent_type: cdad-<role>`, I8, `receive`, `reconcile` existentes) más el mínimo de verificación—; el **adaptador Claude Code** (enfoque A) **no** entra y queda **incremento nombrado** (D-10 del spec).
- **Dependencias del epic:** `005-005` (cerrada) y, en la práctica, `005-003` (vista compacta) y `005-007` (planificación progresiva: su D-3 queda cerrada por el discovery §1.4 y por T3). **Fronteras de contrato (no reescritura):** 005-005 (procedencia/política de tests), 005-009/005-010 (interfaz de delegación y su vocabulario), 001/005-001 (contratos de paquete): esta feature los **referencia**, nunca los reescribe ni agrega una segunda copia.
- **Contrato y reglas reusadas:** spec §9.
- **Convención de anonimización:** toda la salida usa `<home>`, `<repo>`, `<tmp>`, `<ses-…>`; el mapa real vive en `.cdad/local/` (fuera de git).

## 2. Ajuste de las unidades del discovery a tareas atómicas

Una tarea por **clase de producto y oráculo**; un **RED** cubre una clase y su **GREEN** va en **otra sesión**, sin mezclar roles. El discovery (§(d)/(e)) propuso U1 (mapa de capacidades), U2 (ciclo real) y U3 (cierre/paridad); esas unidades se **reagrupan por clase** así:

| Unidad del discovery / alcance del encargo | Tarea | Por qué se agrupa así |
|---|---|---|
| §(d).1 «verificación de carga» en su parte de **herramienta de despacho** (a) | **T1** | Un solo producto: la **declaración de la herramienta** (`tools:` del frontmatter + generador). Clase **código + artefactos generados**, oráculo focal. |
| (b) afirmación del instalador + (e) procedencia de modelo bajo `basic` | **T2** | Misma clase (**enunciados del adaptador CC**) y **mismo oráculo** (barrido documental + install en raíz aislada + las tablas por perfil existentes) ⇒ una sola unidad evita fragmentar. |
| §(g) «versión» en su parte faltante (c) | **T3** | Clase **código** (el comprobador) con oráculo focal y regresión de los cuatro veredictos. |
| §(d).1 «verificación de carga» en su parte de **hooks** (d) | **T4** | Clase distinta: **verificación ejecutable del guard** sin sesión viva + reconciliación del mapa por referencia. No toca el mismo archivo que T1/T2. |
| §(d).2 +(d).3, §(f), (f) del encargo | **T5** | **Gate de aceptación** (no RED/GREEN de producto): el **ciclo corto real** en CC con recepción CDAD. `observable_checks` + gate de integración. |

**Qué NO se planifica** (fuera de alcance, spec §7): el adaptador Claude Code (enfoque A) y su señal durable; emitir activación de proyecto para CC; confiar la carpeta de este proyecto; limpieza/despliegue en HOME; el **registro automático de transiciones** (deuda, spec §8 D-2); WebUI, CI, sandbox, scheduler o UI nueva; medir contexto del lado CC (deuda, spec §8 D-4).

**Nota de paralelismo.** T1 y T2 editan el **mismo archivo fuente** (`sources/agents/adapters/claude-code.md`) y el **mismo generador** (`scripts/cdad-generate.py`) y comparten los derivados `agents/claude-code/**` ⇒ **no** se declaran paralelas (`parallel: []`), consistente con el validador del producto.

## 3. Estrategia de validación (declarada una vez)

- **Dos niveles.** **Siempre:** procedencia, `git diff` contra el alcance del paquete, alcance declarado y **pruebas focales** (segundos). **Sólo con un motivo concreto:** la suite o la integración. Se **reutiliza evidencia equivalente** con procedencia verificada **por referencia** a `skills/cdad-cycle/references/re-entry.md` (*Equivalence of a registered run*).
- **Suite completa una vez, al cierre** (motivo: toca el instalador/staging, el generador de agentes, el CLI del ciclo y docs; cierra la feature). No se corre dentro de cada tarea; **no se corre salvo que el paquete lo pida** (la corre quien cierra).
- **Comandos concretos por encargo** (fichas de §4), **tomados del bloque `plan-tasks`** y rendidos en el paquete (mecanismo de 005-003 T6). RED: el focal debe fallar por aserción (no por import/sintaxis). GREEN: focal verde + regresiones del área.
- **El cierre incluye el commit** y el reporte del rol lo declara; un rol que termina sin commitear es **bloqueo declarado**.
- **Sin umbrales numéricos inventados.** La meta del recorrido (T5) es **comportamiento observable**, no una cifra de ahorro; lo no observable se conserva `unknown` con causa (spec PD-8).
- **Sin `--no-verify`; sin push; sin desplegar; sin tocar HOME; sin leer `tests/.sensitive-patterns.local`.**

## 4. Fichas mínimas de tarea y bloque canónico

### T1 — Herramienta de despacho: `Agent` es la real (reconciliación `Task`↔`Agent`)
- **Resultado observable / PD cubiertas:** PD-1 (base de PD-6).
- **Alcance incluido:** declarar en el **generador** (`cc_tools`) la herramienta de despacho real observada (`Agent`) para el orchestrator; corregir el enunciado del **adaptador fuente** (`tools:` … `Task for orchestrator` → `Agent`); **regenerar** `agents/claude-code/**` con `make agents` (salida declarada); añadir a `tests/validate-consistency.sh` una aserción que **falle** si algún agente CC declara `Task` como herramienta de despacho y que exija `Agent` en el orchestrator. **Nota de alcance verificada:** la línea `tools:` del **orchestrator** es hoy la **única no asertada**: `tests/test_packet_prepare.py:675-688,819-835` fija exactamente `EDIT_TOOLS`/`READ_ONLY_TOOLS` para los **10** agentes con/sin guard, y el orchestrator no está en ese conjunto; por eso la aserción nueva debe cubrirlo. **Excluido:** cambiar el nombre de la herramienta en el lado **OpenCode** (`opencode-delegation.md` usa `Task` y **se conserva**); tocar la interfaz de delegación (005-009/005-010); reescribir la tabla rol→`subagent_type`.
- **Consume:** — . **Produce:** `dispatch-tool-name` (`dispatch-tool-v1`).
- **Dependencias:** — . **Nota:** comparte archivos con T2 → no paralela.
- **Archivos:** *Create/Modify* `scripts/cdad-generate.py`, `sources/agents/adapters/claude-code.md`, `agents/claude-code/cdad-orchestrator.md` (+ los 11 derivados regenerados), `tests/validate-consistency.sh`; *Test* `tests/test_005_004_t1_dispatch_tool_name.py`.
- **Contexto por rol:** RED — spec §2/§3 (PD-1), adaptador `:9-26,:45-50`, `claude-code-delegation.md:7-26`, `SKILL.md:500-501`, discovery §1.6 (incoherencia 1) y §2.3; GREEN — ídem + `scripts/cdad-generate.py:443-455,489-510`.
- **Evidencia al re-entry:** focal rojo→verde (hoy el derivado declara `Task`; después declara `Agent`) + la aserción del validador del repo verde + `git diff` acotado; `make agents` idempotente (segunda corrida sin cambios); los `tools:` de los 10 agentes con/sin guard **siguen exactamente** como hoy (`tests/test_packet_prepare.py`).
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py -q`; regresiones `tests/test_packet_prepare.py`, `tests/test_cdad_generate.py`, `tests/test_003_006_t3_receive_wiring.py`, `tests/test_003_007_t4_atomic_unit_rule.py`, `bash tests/validate-consistency.sh`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** **VERIFY** abierto: si CC 2.1.296 aceptara además `Task` como alias en `tools:`, eso **no** cambia la corrección (declarar la herramienta real no quita una capacidad que los transcripts observados usan). Si al regenerar apareciera cualquier otro cambio de bytes no declarado en los derivados, **detener** y reportarlo (INV-4).

### T2 — Enunciados del adaptador CC reconciliados (instalador sin `strip`; procedencia bajo `basic`)
- **Resultado observable / PD cubiertas:** PD-2, PD-5, PD-9.
- **Alcance incluido:** sustituir en el adaptador la afirmación falsa («the installer STRIPS the model field at install time») por el **mecanismo real** (el instalador despliega los bytes staged **sin transformarlos**: `cp -p`; `install.sh --help`: «the installer transforms nothing»; la diferencia de tamaño observada proviene del **perfil de generación**, `basic` ⇒ `cdad_model_claude` vacío ⇒ el generador **omite** la línea `model:`), con la verificación de bytes en raíz aislada; corregir el **mismo enunciado falso** en el comentario del generador (`scripts/cdad-generate.py:443-446`); declarar en el adaptador (semántica, PD-14) que bajo `basic` **no** hay modelo por rol, que la invariante reviewer≠implementer **no** la garantiza el instalador y que la exención del guard es **explícita y visible** (por referencia a `ADR-007`/`scripts/validate-subagents.sh`, sin copiar su texto). **Excluido:** cambiar el mecanismo del instalador o del generador (no se arregla lo que no está roto); tocar `install.sh`; añadir un perfil nuevo; reescribir el guard o la tabla de modelos (`scripts/cdad-models.sh` es la única fuente del mapa y **se referencia**).
- **Consume:** `dispatch-tool-name` (`dispatch-tool-v1`) de T1 — ambos editan el adaptador y comparten la regeneración. **Produce:** `cc-adapter-statements` (`cc-adapter-statements-v1`).
- **Dependencias:** T1 (misma fuente y misma regeneración).
- **Archivos:** *Create/Modify* `sources/agents/adapters/claude-code.md`, `scripts/cdad-generate.py`, `agents/claude-code/**` (regenerados); *Test* `tests/test_005_004_t2_installer_claims.py`.
- **Contexto por rol:** RED — spec §2/§3 (PD-2/PD-5), adaptador `:13-17,:28-43`, `install.sh:388-396,1259-1300`, `scripts/cdad-models.sh:112-115`, `scripts/validate-subagents.sh:202-263`, `tests/validate-consistency.sh` (barrido); GREEN — ídem + `scripts/cdad-generate.py:489-510`.
- **Evidencia al re-entry:** focal rojo→verde (hoy el enunciado `strip` existe; después no, y el barrido del repo no lo encuentra); el focal **instala en raíz aislada** (`CDAD_INSTALL_ROOT`, nunca HOME) y comprueba que los bytes desplegados de los agentes CC **son** los staged (sin transformación) y que con un perfil que produce `model:` la línea viaja, mientras que bajo `basic` la omite el **generador**; las tablas por perfil siguen verdes.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_004_t2_installer_claims.py -q`; regresiones `tests/test_install_ownership.py`, `tests/test_install_review5_regressions.py`, `bash scripts/validate-subagents.sh`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** el focal de instalación **no** escribe en HOME y **no** ejecuta `--check` contra la instalación del dueño (sólo raíz aislada). Si la verificación exigiera tocar HOME, **detener** y declararlo BLOQUEO (reserva del dueño).

### T3 — Pata Claude Code del chequeo de versión (aditiva)
- **Resultado observable / PD cubiertas:** PD-3, PD-9 (y cierra la deuda D-3 de 005-007).
- **Alcance incluido:** añadir a `cdad-version-check.py` una **pata CC declarada** que lea el marcador de versión de la **raíz de instalación detrás de los agentes CC** (resuelta del **registro de activación** de CC si existe, si no del directorio global de agentes CC del runtime), **sin** cruzar fronteras de instalación (F2) y sin usar el manifiesto de OpenCode; la pata **participa en el veredicto sólo cuando una instalación CC es detectable**; cuando no lo es, imprime una línea declarada de ausencia y **los cuatro veredictos/rc existentes no cambian** (regresión); una marca faltante es `unknown` **con causa** (nunca `0` ni una versión prestada). Actualizar `project-start.md` §10 **por referencia** al contrato de la pata (sin duplicar la tabla de veredictos, que sigue en su dueño). **Excluido:** cambiar los cuatro veredictos/rc existentes; introducir un quinto veredicto; leer/escribir HOME; tocar el manifiesto de OpenCode (005-005) o la plomería de activación (`cdad-activate.py`).
- **Consume:** — . **Produce:** `version-check-cc-leg` (`version-check-cc-v1`).
- **Dependencias:** — .
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad-version-check.py`, `skills/cdad-cycle/references/project-start.md`; *Test* `tests/test_005_004_t3_version_check_cc.py`.
- **Contexto por rol:** RED — spec §2/§3 (PD-3), `cdad-version-check.py:1-34,47-56,74-108,125-168`, `project-start.md:184-211`, `runtime-adoption.md:21-39`; GREEN — ídem + `005-005/spec.md` PD-12..PD-14.
- **Evidencia al re-entry:** focal rojo→verde sobre **fixtures de raíz** (con y sin `.claude/agents`); regresión: sin agentes CC, **veredicto y rc idénticos** a hoy con la línea nueva declarada; no se ejecuta contra la instalación del dueño salvo lectura del marcador.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_004_t3_version_check_cc.py -q`; regresiones `tests/test_005_006_t6_owner_reviewfix.py`, `tests/test_005_003_t2_examples_execute.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si la pata CC obligara a **cambiar** un veredicto existente, **detener**: el contrato de 005-005 no se reabre (extensión aditiva y declarada, o no entra).

### T4 — Hooks de CC: mapa declarado una vez y verificación sin sesión viva
- **Resultado observable / PD cubiertas:** PD-4, PD-9.
- **Alcance incluido:** reconciliar el **mapa de hooks** en su dueño (`sources/agents/adapters/claude-code.md` + `CC_GUARDS` del generador) y corregir los enunciados **obsoletos** del consumidor `claude-code-delegation.md` (que hoy describe los globs legacy `src/**`/`lib/**` mientras el guard v2 clasifica con la política del proyecto, `paths` acotados y fail-closed sin clasificador), **por referencia** al contrato del guard; y añadir un **focal que EJECUTA el guard CC** con cargas PreToolUse sintéticas (`CLAUDE_PROJECT_DIR` = proyecto fixture) **solo para lo que la cobertura existente no tiene** (enmienda de la revisión, 2026-10-13): rol desconocido → fail-open; rol sin hooks → sin barrera de ruta; y el frontmatter de hooks de los agentes CC generados (`matcher`, modo, comando) coincide con `CC_GUARDS`. Las decisiones del implementer y del test-writer contra implementación/tests **ya están cubiertas** (`tests/test_004_002_t5_runtime.py` `pd8_i10_c2_*`, `tests/test_005_008_t1_nested_tests.py`) y se **referencian** como regresión, sin repetirlas. **Excluido:** prometer que CC honra `exit 2` o que los hooks del frontmatter se aplican a subagentes nativos (VERIFY, PD-8); habilitar un hook `Bash` (retirado por decisión del dueño 2026-09-29); duplicar la tabla de roles del contrato.
- **Consume:** — . **Produce:** `cc-hooks-verification` (`cc-hooks-v1`).
- **Dependencias:** — . **Nota:** archivos distintos de T1/T2 ⇒ podría declararse paralela; se deja `parallel: []` (conservador, sin ganancia de integración).
- **Archivos:** *Create/Modify* `skills/cdad-cycle/references/claude-code-delegation.md`, `sources/agents/adapters/claude-code.md`; *Test* `tests/test_005_004_t4_cc_guard_decisions.py`.
- **Contexto por rol:** RED — spec §2/§3 (PD-4), `claude-code-delegation.md:41-61`, `scripts/claude-code-path-guard.sh:50-70,134-138,176-230,325-434`, `tests/test_005_008_t1_nested_tests.py` (patrón `run_guard`); GREEN — ídem + `sources/agents/adapters/claude-code.md:18-25,28-43`.
- **Evidencia al re-entry:** focal rojo→verde (hoy el consumidor describe globs legacy; después describe el clasificador y las decisiones se ejecutan); `git diff` acotado; el focal **no** usa HOME como política.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_004_t4_cc_guard_decisions.py -q`; regresiones `bash tests/validate-consistency.sh`, `tests/test_005_008_t1_nested_tests.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si el enunciado obsoleto no puede corregirse sin introducir una **segunda** copia del contrato del guard, **detener** y reportarlo (PD-9, fuente única). El consumidor afirma hoy que CC honra `exit 2` («verified empirically in validation-cdad-002.md»): conciliarlo con el VERIFY 1 de PD-8 (conservar la afirmación con su alcance observado o declararla no verificada en modo no interactivo), sin dejar contradicción.

### T5 — Gate: recorrido real corto en Claude Code con recepción CDAD
- **Resultado observable / PD cubiertas:** PD-6, PD-7, PD-8, PD-10, PD-11; criterios AC-1..AC-8.
- **Coordinador (enmienda de la revisión, 2026-10-13):** una **sesión nueva de Claude Code** sin contexto previo, con una instrucción breve (spec PD-6); el **orquestador Claude** la lanza, mide su transcript y revisa, sin coordinar. No es el orquestador OpenCode: solo una sesión CC invoca subagentes nativos. **Paso a** (gate de cierre): CLI y agentes CC de la instalación al empezar; la pata CC de PD-3 se corre desde el **artefacto del repo** en el commit de cierre contra la instalación, declarado. **Paso b** (tras el despliegue que decida el dueño, no gate): confirmación corta con el CLI instalado (spec PD-6).
- **Alcance incluido:** correr **un ciclo corto real** despachado desde una sesión de Claude Code con la **versión instalada al empezar**: orientar con la vista compacta (`status`), registrar el intento con `runtime: claude-code` (`prepare --record-dispatch`, I8) con `model_configured`/`model_reported` y `provenance`, invocar un subagente **nativo** `cdad-<role>` con la herramienta `Agent` (modelo explícito en el despacho crítico de revisión), recibir la entrega por `cdad_result.py receive` (recibo durable `semantic_status: pending`), re-entrar (`reconcile`) y decidir el gate con el coordinador como **escritor único** del state; registrar la **evidencia** (I8, `receipt.json`, transición, y las filas del transcript que exponen la señal durable) y **declarar las fricciones** (incluida la preparación manual del descriptor de recepción, PD-10). Declarar los **cruces del dueño** como BLOQUEO (PD-7/PD-11). **Excluido:** desplegar o limpiar HOME; confiar la carpeta del proyecto; emitir activación CC; presentar `completed`/recibo como aprobación del gate; prometer ahorros sin medición; presentar la sesión separada como sandbox.
- **Consume:** `dispatch-tool-name` (`dispatch-tool-v1`) de T1, `cc-adapter-statements` (`cc-adapter-statements-v1`) de T2, `version-check-cc-leg` (`version-check-cc-v1`) de T3, `cc-hooks-verification` (`cc-hooks-v1`) de T4. **Produce:** `acceptance-report` (`acceptance-report-v1`).
- **Dependencias:** T1, T2, T3, T4. **Gate:** cubre T1..T4 por la estrategia de validación (sus focales) y su cierre es el **gate de la feature**.
- **Archivos:** *Create* evidencia del informe (fuera del árbol publicable, o en `docs/specs/005-004-claude-code-roles/` según la tabla cerrada de materialización); *Test* — (gate, sin código).
- **Contexto por rol:** orchestrator — spec §5 (AC-1..AC-8) y §3 (PD-6..PD-8); architect — lectura. El **dueño** decide los cruces reservados.
- **Evidencia al re-entry:** informe con I8 (`runtime: claude-code`, procedencia de modelo), recibo durable `pending`, transición del state, veredicto de versión **con** la pata CC, y los `unknown` conservados con causa; los cruces del dueño como **BLOQUEO declarado**; la fricción de recepción declarada, nunca presentada como automática.
- **Verificación:** `observable_checks` (gate, sin focal de producto).
- **Integración / responsable:** **gate de aceptación de la feature 005-004**; orquestador Claude, sesión de Claude Code (coordinación y registro); architect (lectura).
- **Incertidumbres / detención:** si falta cuota/cuenta para la corrida real, o si el despacho nativo no puede correrse sin tocar HOME o sin confiar la carpeta, **BLOQUEO declarado** con responsable (dueño), nunca verde por proximidad; si el rol nativo no expusiera la identidad/señal durable, **declararlo** (alimenta D-10, no se improvisa un fallback silencioso).

### Bloque canónico `plan-tasks`

```plan-tasks
{"validation_strategy": "Verificacion en dos niveles: siempre procedencia + git diff contra el alcance + alcance declarado + pruebas focales (segundos); suite o integracion solo con un motivo concreto; la suite completa la corre una vez quien cierra; se reutiliza evidencia equivalente con procedencia verificada (regla canonica en skills/cdad-cycle/references/re-entry.md, seccion Equivalence of a registered run), sin repetir la suite.",
 "tasks": [
  {"id": "T1",
   "objective": "Reconciliar la herramienta de despacho de Claude Code: declarar Agent (la real observada) en el generador, el adaptador fuente y los agentes derivados, y hacer que el validador del repo falle si algun agente CC declara Task como herramienta de despacho.",
   "produce": [{"artifact": "dispatch-tool-name", "contract": "dispatch-tool-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["scripts/cdad-generate.py", "sources/agents/adapters/claude-code.md", "agents/claude-code/cdad-orchestrator.md", "tests/validate-consistency.sh"],
   "focal_tests": ["tests/test_005_004_t1_dispatch_tool_name.py"],
   "regressions": ["tests/test_packet_prepare.py", "tests/test_cdad_generate.py", "tests/test_003_006_t3_receive_wiring.py", "tests/test_003_007_t4_atomic_unit_rule.py", "tests/validate-consistency.sh"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "objective": "Reconciliar los enunciados del adaptador CC: eliminar la afirmacion falsa de que el instalador quita el campo model (el instalador despliega los bytes staged sin transformarlos y la diferencia proviene del perfil de generacion) y declarar la procedencia de modelo bajo el perfil basic con la exencion explicita de la invariante reviewer distinto de implementer.",
   "produce": [{"artifact": "cc-adapter-statements", "contract": "cc-adapter-statements-v1"}],
   "consume": [{"artifact": "dispatch-tool-name", "contract": "dispatch-tool-v1", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["sources/agents/adapters/claude-code.md", "scripts/cdad-generate.py", "agents/claude-code/cdad-orchestrator.md"],
   "focal_tests": ["tests/test_005_004_t2_installer_claims.py"],
   "regressions": ["tests/test_install_ownership.py", "tests/test_install_review5_regressions.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "objective": "Anadir al chequeo de version una pata Claude Code declarada y aditiva: lee el marcador de la raiz de instalacion detras de los agentes CC (registro de activacion o directorio global del runtime), participa en el veredicto solo cuando una instalacion CC es detectable, y no altera los cuatro veredictos ni el rc existentes.",
   "produce": [{"artifact": "version-check-cc-leg", "contract": "version-check-cc-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad-version-check.py", "skills/cdad-cycle/references/project-start.md"],
   "focal_tests": ["tests/test_005_004_t3_version_check_cc.py"],
   "regressions": ["tests/test_005_006_t6_owner_reviewfix.py", "tests/test_005_003_t2_examples_execute.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "objective": "Declarar una sola vez el mapa de hooks de Claude Code por rol y verificar las decisiones del guard sin una sesion viva, ejecutandolo con cargas PreToolUse sinteticas sobre un proyecto fixture.",
   "produce": [{"artifact": "cc-hooks-verification", "contract": "cc-hooks-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/references/claude-code-delegation.md", "sources/agents/adapters/claude-code.md"],
   "focal_tests": ["tests/test_005_004_t4_cc_guard_decisions.py"],
   "regressions": ["tests/validate-consistency.sh", "tests/test_005_008_t1_nested_tests.py", "tests/test_004_002_t5_runtime.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T5",
   "objective": "Gate de aceptacion de la feature: correr un ciclo corto real despachado desde Claude Code con la version instalada al empezar, con registro I8 de runtime claude-code y procedencia de modelo, subagente nativo cdad-rol, recepcion CDAD con recibo pending y re-entry del coordinador, declarando fricciones, desconocidos y los cruces reservados al dueno como bloqueo.",
   "produce": [{"artifact": "acceptance-report", "contract": "acceptance-report-v1"}],
   "consume": [{"artifact": "dispatch-tool-name", "contract": "dispatch-tool-v1", "producer": "T1"}, {"artifact": "cc-adapter-statements", "contract": "cc-adapter-statements-v1", "producer": "T2"}, {"artifact": "version-check-cc-leg", "contract": "version-check-cc-v1", "producer": "T3"}, {"artifact": "cc-hooks-verification", "contract": "cc-hooks-v1", "producer": "T4"}],
   "depends_on": ["T1", "T2", "T3", "T4"],
   "parallel": [],
   "observable_checks": ["el recorrido corre punta a punta desde una sesion de Claude Code con la version instalada al empezar: orienta con la vista compacta, comprueba la version con la pata CC, registra el intento con runtime claude-code (I8) y procedencia de modelo, invoca un subagente nativo cdad-rol con la herramienta Agent, recibe la entrega con receive (recibo durable semantic_status pending) y re-entra con reconcile; la evidencia son el registro I8, el receipt, la transicion del state y las filas del transcript que exponen la senal durable", "los cruces reservados al dueno (confianza de carpeta, copias o despliegue en HOME, activacion de proyecto CC, activar versiones en el repo real) se declaran BLOQUEO con responsable y no se ejecutan; la preparacion manual del descriptor de recepcion se declara como friccion y no se presenta como automatica; los desconocidos (exit 2 de un hook en modo no interactivo, aplicacion de hooks a subagentes nativos, herencia de modelo, medicion de contexto del lado CC) se conservan unknown con causa, nunca como cero; el recibo pending no se presenta como aprobacion del gate"],
   "regressions": [],
   "integration_gate": "gate de aceptacion de la feature 005-004: los focales de T1..T4 rojo-a-verde con su git diff acotado y el recorrido real corto de Claude Code con recepcion CDAD; los cruces reservados al dueno quedan como BLOQUEO declarado, nunca verdes por proximidad",
   "owner": "sesion nueva de Claude Code (coordinacion y registro), lanzada y revisada por el orquestador Claude; architect (lectura)"}
 ]}
```

## 5. Trazabilidad PD/AC → tarea

PD-1 → T1; PD-2 → T2; PD-3 → T3; PD-4 → T4; PD-5 → T2 (+ evidencia en T5); PD-6 → T5; PD-7 → T5; PD-8 → T5 (+ declaración en T3/T4); PD-9 → T1/T2/T4 (referencias, y el barrido de T2); PD-10 → T5 (declaración de la deuda); PD-11 → T5.
AC-1 → T1; AC-2 → T2; AC-3 → T3; AC-4 → T4; AC-5..AC-8 → T5.

## 6. Gate de aceptación de la feature

- **La feature cierra cuando:** los focales de T1..T4 están rojo→verde con su `git diff` acotado; el barrido de enunciados (T2) no encuentra la afirmación `strip`; el guard CC (T4) decide correctamente por rol sin sesión viva; y el **recorrido real corto** (T5) tiene evidencia: I8 con `runtime: claude-code`, recibo durable `pending`, re-entry registrado.
- **El gate de la feature es el de T5.** Los cuatro cruces reservados al dueño (confianza de carpeta, HOME, activación CC, activar versiones en el repo real) son **BLOQUEO declarado**, nunca verde por proximidad.
- **Suite completa una vez**, por quien cierra, en un worktree fijado al commit de cierre; `make validate` sin fallos nuevos.
- **Criterios del epic que esta feature alimenta:** el criterio 2 (una versión estable por ciclo, verificada en cada `prepare` por `source_dir`, hashes y la versión declarada) y el criterio 4 (suite completa al cierre con validadores sin fallos nuevos).

## 7. Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**; **sin desplegar**; **sin tocar HOME**; **sin leer** `tests/.sensitive-patterns.local`.
- **Sin valores de este VPS** en spec, plan ni producto: sin rutas de HOME, sin rutas absolutas del dueño, sin ids crudos de sesión (`<home>`, `<repo>`, `<tmp>`, `<ses-…>`).
- **No** reescribir los contratos de 005-005/005-009/005-010 ni los de paquete de 005-001: extensión **aditiva y declarada** o referencia (INV-2/PD-9).
- **Sin volcar salidas enormes** al contexto; evidencia completa por referencia. Para comprobar un RED sin el arreglo: **worktree**, **nunca `git stash`** en el árbol compartido.
- **Ante un obstáculo fuera de alcance: entregar el diagnóstico, no fabricar registros.**

## 8. Aprobación

**Estado: APROBADO.** Se aprobó **junto con la spec y en una sola acción** por el **orquestador OpenCode** el **2026-10-13**, bajo la **HITL delegada del epic-005** (`docs/epics/epic-005-real-operation/execution.md`). El **architect** no aprobó su propia propuesta (entregó este plan como DRAFT). La cabecera «DRAFT — SIN APROBAR» del rol se conserva como registro de la entrega; el estado vigente es el de esta sección. Rige el **criterio de review vigente del 2026-10-12**. Este plan **no arranca TDD**: el **orquestador Claude revisa** antes de la etapa 3. El bloque `plan-tasks` de §4 fue validado por el orquestador con las funciones del propio CLI (`_plan_tasks_from_contract`, `_check_plan_tasks`, `_check_plan_validation_plan` y el render de las cinco fichas: **OK**). La firma y los hashes están registrados en `docs/.cdad-state.json` (`stage_history`, `stage: specification`).

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-13
