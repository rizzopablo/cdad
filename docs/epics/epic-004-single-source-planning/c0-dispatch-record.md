# Registro de despacho y notas de revisión externa — preparación C0 (epic 004)

Fecha: 2026-09-24. Base: `4a821a0`, rama `codex/epic-003-context-efficiency`,
con cambios documentales sin commit heredados de la sesión anterior (solo
documentación; ver `git status`). Autor de este registro: orquestador GLM.

## Actualización vigente — 2026-09-24, posterior al dictamen GPT

El usuario decidió el enfoque de autonomía supervisada. La
[enmienda C0 vigente](c0-amendment-supervised-autonomy-2026-09-24.md)
y [ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md)
gobiernan el próximo encargo. Incorporan R1–R3 y añaden D11: simplificar
capacidades/controles antes de generar. Las notas originales siguientes quedan
como historia, no requisitos para preservar el techo de líneas o restricciones
excesivas. Próxima salida GLM: spec/plan 004-001 y delta focal. Sin activación,
implementación o publicación autorizadas por este registro.

## 1. Despacho

- **Encargo**: primer encargo exacto del
  [handoff de continuación](../../handoffs/2026-09-23-glm-continuation.md) §8 —
  preparar C0 (inventario de fuentes, delta del plan 004, recorrido consumidor,
  contrato de autoridad, paquete C0 para GPT/Claude).
- **Rol**: architect en sesión aislada (delegación nativa; `stack: null` →
  variante genérica). Read-only: devuelve propuestas; no autoaprueba.
- **Estado esperado al re-entry**: 5 entregables completos para materializar
  y armar el paquete C0. Este documento no aprueba nada por sí mismo.
- **Re-entry (2026-09-24)**: encargo **completo**. Informe materializado íntegro
  en [c0-architect-report-2026-09-24.md](c0-architect-report-2026-09-24.md)
  (inventario R1–R12, delta D1–D10, recorrido §3, autoridad §4 con lista de
  trabajo independiente autorizado, paquete C0 §5 listo para despachar a GPT o
  Claude, 6 dudas VERIFY §6). Pendiente: despacho del paquete C0 (revisión GPT/Claude);
  mientras tanto vale la lista de trabajo autorizado de su §4.2.

## 2. Notas de revisión externa (Claude) — adoptadas como insumo de C0

Registro textual-resumido de la revisión externa; **no modifican los
documentos base** (se pliegan al paquete C0 y a las specs por ciclo cuando
corresponda).

1. **Línea base de contexto, antes del refactor.** Medir y registrar hoy: bytes
   de instrucciones que carga cada rol por el camino clásico y por el de
   paquete, en cada runtime. Estático y barato. Sin el "antes" no se podrá
   demostrar la mejora que es el objetivo del epic.
2. **Guardrail maquinaria vs. copias.** Criterio medible de cierre para
   004-001: de 22 archivos mantenidos a mano a N, y líneas restantes en la
   fuente. Si el generador/adaptadores/manifest pesan más que las 22 copias,
   se empeoró el mantenimiento.
3. **Formato para el constructor.** Convertir lo crítico de la prosa
   (numerosas prohibiciones) en criterios de aceptación verificables por ciclo
   (checklist por encargo); los documentos base quedan como referencia de
   análisis. Las prohibiciones no testeables: pocas y destacadas.
4. **Congelar ediciones manuales.** Desde que el generador de 004-001 aterriza:
   nadie edita un agente a mano (personas ni agentes). Sin esta regla, la
   duplicación vuelve en la primera corrección urgente.
5. **Lista de trabajo independiente autorizado.** Definir concretamente qué
   cuenta como tal mientras se espera revisión GPT/Claude, para no frenar de
   más ni avanzar de más.
6. **C0 con opciones, no preguntas.** Las decisiones abiertas de C0 llegan como
   opciones recomendadas con su costo, para que la revisión no se convierta en
   sesión de diseño.

### Corrección de lectura — probe OpenCode (afecta 003-003)

El handoff remite a `runtime-discovery.md` con la frase "no demostró
aislamiento completo". Aclaración operativa: el problema conocido es doble —
(a) el smoke quedó inválido como prueba de aislamiento porque OpenCode leyó
configuración heredada fuera de las raíces temporales; (b) en sub-agentes el
filesystem es compartido y el sandbox de archivos no está demostrado. **No
invertir tiempo en reproducir el probe**: diseñar 003-003 asumiendo la
limitación (filesystem compartido, sandbox no demostrado).

---

## Segundo despacho — spec/plan 004-001 (2026-09-24, orquestador)

Encargo de la enmienda vigente ejecutado por architect en sesión aislada
(intento 1 y 2 fallidos por mofgw; intento 3 completo). Informe materializado:
[spec-plan-004-001-architect-2026-09-24.md](spec-plan-004-001-architect-2026-09-24.md)
— delta C0 con errata de R1–R3, tabla de capacidades por rol, keep/simplify/
remove de controles (par `rtk wc` resuelto dentro del rediseño, no parche
aislado), fuentes/manifest/tareas T1–T7, matriz proporcional, procedimiento de
activación §6 (snapshot de 003, un único write del state, firma del usuario),
spec draft con **16 postcondiciones** y plan draft. VERIFY resueltos: asserts
de `validate-odoo-specialization.sh`, consumidores del layout público
confirmados en fixtures, divergencia R3 de intake. Pendiente: revisión focal
GPT/Claude del delta+spec/plan → aprobación del usuario → activación §6.

Status: registro de continuidad. La ejecución del encargo se materializa por
el orquestador al re-entry; la aprobación estratégica sigue siendo del usuario
o agente expresamente autorizado.


## Revisión GPT recibida — 2026-09-24

Dictamen documentado: [c0-review-gpt-2026-09-24.md](c0-review-gpt-2026-09-24.md).
**CHANGES REQUIRED**, corrección focal: D9 debe distinguir preparación de
activación y conservar state coherente; D2 debe sustituir el veto por líneas
por criterios de mantenimiento verificables y corregir sus sumas; las
capacidades/limitaciones de Codex y OpenCode deben separarse según evidencia.
Las notas de Claude anteriores se conservan como insumo histórico; no son
requisitos aceptados automáticamente. En particular, las afirmaciones de
líneas y aislamiento quedan corregidas por el dictamen.

Próximo paso para GLM: delta que resuelva R1–R3, procedimiento de activación y
spec/plan inicial de 004-001. Mantener trabajo independiente autorizado;
ninguna construcción ni activación se aprobó en esta revisión. No requiere
repetir el discovery completo. El informe original del architect se conserva
sin edición en este turno; el dictamen indica cómo sanitizar su envoltorio
antes de distribuirlo y cómo versionar los documentos base pendientes.

## Activación de epic 004 — 2026-09-24 (orquestador, procedimiento §6)

1. Dictamen focal de Claude registrado (`21238de`): conforme con corrección
   requerida + 3 observaciones.
2. Corrección resuelta por architect en sesión aislada (opción (a): aterrizaje
   0 de capacidad de medición dentro de T1; R13 con cita verificada — la
   constante `VALID_EPIC_STAGES` no incluye `epic-planning`; dos aterrizajes
   A/B; supervisión con dueño PD-17; PD-18/19). Materializado y aprobado:
   spec/plan en `docs/specs/004-001-canonical-runtime-artifacts/` (`24d37f0`),
   informe íntegro en
   [correction-004-001-architect-2026-09-24.md](correction-004-001-architect-2026-09-24.md).
3. Autoridad registrada: [execution.md](execution.md) (firma del usuario;
   cadena de autoridad documentada).
4. Snapshot de suspensión de epic 003:
   `docs/epics/epic-003-context-efficiency/handoff-suspension.md`; congelación
   pre-activación: commit `eba6d47`.
5. Único write del state (`0117e00`): `active_epic → epic-004`,
   `epic_stage → epic-planning` (valor del vocabulario canónico
   `state-detection.md:14`, seguro bajo modo `ordinary`), 3 features queued,
   delegación GLM desde execution.md, delegación Codex/epic-003 archivada
   `suspended` en `delegation_history`.
6. Verificación post-activación: JSON válido y campos comprobados
   (`active_epic`, features, delegación); la re-verificación completa por
   sesión nueva ocurre con la detección existente al preparar el primer
   paquete de 004-001.

Siguiente paso: iniciar el ciclo de 004-001 con T1 (aterrizaje 0 + baseline),
roles separados por contrato.

## T1 — despacho (2026-09-24, orquestador)

**Aterrizaje 0 + baseline** (spec PD-13/19; plan T1). Secuencia de roles en
sesiones separadas: (1) test-writer RED — contrato del par (`wc *` y
`rtk wc *` en la emisión) + actualización de F009 en el mismo cambio;
(2) implementer GREEN — mínimo cambio en fuente, reinstalación de la
inyección, `--check`, suite completa; (3) architect — baseline PD-13 con la
capacidad aterrizada (totales mecánicos del comando, método/versión/config/
sesión, valor efectivo del techo 12k; sin evidencia prestada). El cierre de
T1 lleva el registro de supervisión PD-17.

### Cierre de T2 — registro de supervisión PD-17 (2026-09-24, orquestador)

- **(a) Resultado vs contrato**: contenido de las 7 fuentes canónicas
  materializado verbatim desde el informe del architect
  (`sources/roles/{architect,test-writer,implementer,reviewer,scribe}.md`,
  `sources/agents/adapters/{opencode,claude-code}.md`) con la gramática de
  delimitadores y semántica de error PD-3. Ediciones R13 aplicadas
  (canonización del vocabulario en `state-detection.md:14` + comentario de
  trazabilidad en `cdad_packet.py`, cero cambio de comportamiento:
  pytest 52 passed). Verificación PD-4 ejecutada: intake core 1 definición
  editable; property rule 1 hit (test-writer, anfitrión); vocabulario
  epic_stage 1 definición + 1 subconjunto anotado; 0 modelos de diseño en
  `sources/`; `legacy-loads` 5/5 con R3 corregido en la fuente; honestidad
  PD-15 sin promesas de sandbox.
- **(b) Ámbito de cambios**: `sources/**` (7 archivos nuevos) +
  `skills/cdad-epic/references/state-detection.md` +
  `skills/cdad-cycle/scripts/cdad_packet.py` (solo comentario) + este
  registro. Sin tocar `agents/**` (pasan a salidas en T3) ni tests.
- **(c) Desviaciones y disposición proporcional**:
  - **Incidente de bucle del orquestador (registrado por ADR-011)**: tras las
    ediciones R13, la verificación pytest del orquestador entró en ~60
    reintentos equivalentes del mismo comando (`rtk pytest`) que fallaba con
    "No tests collected", sin cambiar de enfoque. Causa raíz técnica: el
    binario pytest no pone cwd en sys.path (`ModuleNotFoundError: No module
    named 'tests'`); la invocación correcta es `python3 -m pytest`. El
    usuario abortó el loop y desactivó rtk. Disposición: fricción/hallazgo
    registrado (el wrapper rtk añade una capa de fallas semánticas
    silenciosas — insumo directo para el rediseño de controles de T4 y para
    003-003); ninguna tarea se repitió; ningún efecto lateral (corridas de
    solo lectura). El incidente fue detectado y cortado por el usuario,
    no por un guard inexistente — evidencia de diseño para 003-003.
  - 11 inconsistencias de los 22 agentes catalogadas por el architect
    (errata de T2): todas quedan corregidas por construcción al generar en
    T3; ninguna acción inmediata.

### Cierre de T3 — registro de supervisión PD-17 (2026-09-24, orquestador)

- **(a) Resultado vs contrato**: GREEN completo. RED `acf17dd` (12 tests
  generador + PD-19 + 5 asserts F001-semántico). GREEN `d5b2a1b`:
  `scripts/cdad-generate.py` (~880 líneas stdlib, validación pre-publicación
  PD-3, composición §2 del orquestador desde las 6 fuentes, frontmatter por
  runtime desde adaptadores + `cdad-models.sh`, manifest con sha256/fuentes/
  comando/perfil, sin timestamps), Makefile (staging/agents/validate),
  `.gitignore +build/`, PD-19 (`CDAD_STATIC_BLOCK_LIMIT`, default 12000,
  stdout vacío en exceso). **Suite independiente reproducida por el
  orquestador: pytest 64 passed (52 sin regresión + 12 nuevas); validator
  Assert PASS 142 / FAIL 1 (solo F011 preexistente).** Los 22 agentes pasan
  a salidas declaradas (regenerados con `make agents`, profile optimus,
  stack odoo); manifest en `build/staging/` (gitignored). F001-semántico 5/5
  PASS; F009/F004/F005/F006/F007/F010/P1..P6/A3 en PASS.
- **(b) Ámbito de cambios**: exactamente los archivos del implementer +
  agentes regenerados. `install.sh` intacto (T5); F009 intacto (T7);
  `cdad-bash-allowlist.sh` intacto.
- **(c) Desviaciones y disposición proporcional**:
  - Primer intento GREEN: sesión terminó sin producir nada (resultado
    vacío, sin cambios en disco). Disposición: reintento idéntico —
    segundo intento completo. Registrado como fricción de runtime (mofgw).
  - `git add/commit` denegado al implementer → orquestador ejecutó el commit
    (mismo patrón que RED de T1/T3).
  - Fricción de sesión del implementer: `git`, `python3`, `bash script`,
    `grep`, pipes/redirecciones denegados → trabajo vía Makefile declarado
    (nueva entrada de regeneración). Registrado para T4/003-003.
  - **Defecto de fuente hallado (reportable a T4)**: 3 líneas de fuentes T2
    violaban PD-15 latente ("sandbox" sin negación minúscula en la misma
    línea) → el generador lo normaliza mecánicamente + self-check
    pre-publicación; las fuentes deben corregirse en T4.
  - **Fragmentos de garantías aprobadas** (taxonomía addyosmani, Axis 4,
    regla RED, tablas de paths) aún viven como fragmentos marcados en el
    generador, no en `sources/` → su hogar canónico se decide en T4/T7
    (bandera AP-4 para el reviewer del aterrizaje A).
  - F011 (copias instaladas stale vs agentes regenerados): dueño T5/T6
    (reinstalación con manifest).
- **Estado**: aterrizaje A en curso. T1 ✅ · T2 ✅ · T3 ✅ · T4 (adaptadores
  desde fuente + defectos de fuente) → siguiente; luego paquete de revisión
  focal agrupado para GPT/Claude.

### Cierre de T1 — registro de supervisión PD-17 (2026-09-24, orquestador)

- **(a) Resultado vs contrato**: aterrizaje 0 completo. RED contractual
  verificado (5× `'rtk wc *' allow MISSING`, `a078dd6`); GREEN con cambio
  mínimo (`rule "wc *" allow` → `pair "wc "` en `emit_base_allow`,
  `cc16495`; nota de contrato: el helper de pares exige el espacio final, el
  plan decía `pair "wc"` — intención preservada, semántica del test como
  oráculo). Validator final **PASS 139 / FAIL 0** (F011 era artefacto de
  copias stale, resuelto por la reinstalación que T1 manda); pytest **52
  passed**; `install.sh --check` PASS 46/46; par verificado en las 5 copias
  instaladas base. **Baseline PD-13 materializada** en
  `docs/specs/004-001-canonical-runtime-artifacts/evidence/baseline.json` —
  contraste externo GPT reproducido dígito a dígito (22/2.697/140.161);
  techo PD-19 registrado (12.000, hardcodeado); método/versión/config/sesión
  registrados; VERIFY explícitos donde no hubo medición.
- **(b) Ámbito de cambios**: RED = tests/validate-consistency.sh + evidencia;
  GREEN = scripts/cdad-bash-allowlist.sh (1 línea) + evidencia; baseline =
  docs/specs/…/evidence/baseline.json. Diff --stat revisado por el
  orquestador en cada re-entry; sin cambios fuera de alcance.
- **(c) Desviaciones y disposición proporcional**:
  - `git add/commit` denegados al test-writer → orquestador ejecutó el commit
    RED (materialización; registrado en el mensaje del commit). Fricción
    registrada para 003-003/T4.
  - `pair "wc"` sin espacio final rompía el assert preexistente → implementer
    usó `pair "wc "`; decisión correcta dentro del mandato, registrada.
  - Fricción nueva del runtime (8 ítems del architect): sesión stale de
    permisos (F2, causa raíz candidata), denegaciones no atribuidas (F1/F4),
    fallos semánticos silenciosos de rtk (F6) y `git diff --no-index` vacío
    para archivos distintos (F7, defecto nuevo). Disposición: **fricción
    registrada** como insumo de 003-003 y del rediseño de T4; ninguna
    invalida la evidencia de T1 (la medición usó capacidad mecánica
    permitida y el contraste externo coincidió).
  - Repo OC sin el par en su bloque handwritten: no se observa regresión
    real (el bloque instalado se deriva del generador); verificación de
    instalación pasa a T2/T4.

### Estado del plan 004-001 tras T2

T1 ✅ (aterrizaje 0 + baseline) · T2 ✅ fuentes + R13 (revisión focal pendiente
de agrupar al cierre del aterrizaje A) · T3 generador → siguiente.


## Sanitización registrada — 2026-09-24 (orquestador)

Observación 1 del dictamen aplicada a la copia vigente de
[c0-architect-report-2026-09-24.md](c0-architect-report-2026-09-24.md): se
retiró el envoltorio de delegación (`<task id=...>` con identificador real de
sesión, `<task_result>`, mensaje de apertura y cierre); el cuerpo del informe
no fue editado y la nota de sanitización quedó dentro del archivo. Suma de
líneas verificada por el orquestador contra el árbol actual: **22 archivos,
2.697 líneas** — coincide con la corrección C0-R2 del dictamen y del finding
de fricción; los subtotales del informe original (2.554) omitieron ambos
`scribe-odoo` y quedan como errata enlazada, no se reescriben.

### Cierre de T6 — registro de supervisión PD-17 (2026-09-29, orquestador Claude)

- **(a) Resultado vs contrato**: GREEN completo. RED congelado `92851b2`
  (2 RED: PD-9 destinos reales, PD-14 path-guard CC). GREEN `09d675e`
  (cdad-implementer, OpenCode 2.0.16, glm-5.3-flash): layout público fuera de
  los destinos de instalación (vars `PUBLIC_*` solo para retiro legacy);
  agentes CC citan `~/.claude/cdad-scripts/path-guard.sh`, corregido en el
  emisor del generador y regenerado con `make agents`. Decisión del flag
  (PD-9): sin consumidor real documentado → **sin flag opt-in**. Enmienda
  del oráculo stale de 003-001 firmada en review-7 y ejecutada por
  cdad-test-writer (`00da41d`). **Suite completa reproducida por el
  orquestador: 98 passed (`env -u TMPDIR`, 519 s)**; validate-consistency
  132/0, validate-subagents PASS; instalación aislada sin `agents/` ni
  `skills/` públicos; `install.sh --check` rc=0 en raíz aislada y en HOME real.
- **(b) Ámbito de cambios**: `09d675e` = `install.sh` + `scripts/cdad-generate.py`
  + 11 agentes CC regenerados (sin tests); `00da41d` = un solo archivo de
  tests (`test_role_packet_review_regressions.py`, +62/−14). Contenido
  revisado por el orquestador (review-7), no solo el `--stat`.
- **(c) Desviaciones y disposición proporcional**:
  - Implementer ejecutó `install.sh --uninstall --force` + `install.sh` sobre
    el HOME real (fuera de lo declarado). Sin daño (reinstalación idempotente
    desde staging, `--check` rc=0). Disposición: **registrar + instrucción
    explícita** en la continuación (no repetido) y en los paquetes siguientes;
    sin barrera nueva (principio de instrucciones claras + verificación).
  - Conflicto de contrato (oráculo de 003-001 vs PD-9): el implementer se
    detuvo sin tocar tests, conforme a la regla de oráculos congelados.
    Disposición: enmienda firmada acotada (review-7) → test-writer.
  - Prompt de paquete tomado como flag por el CLI (`---cdad-packet-json`):
    se pasa tras `--`. Timeout del orquestador (50 min) cortó una corrida:
    continuación con `--session`. Fricción de orquestación, sin efecto en
    la evidencia.
  - Pendiente detectado para el cierre de 004-001: T4 y T5 no tienen su
    registro PD-17 escrito en este archivo (sí en state/reviews); a
    consolidar antes del cierre de la feature.
- **Estado**: T1–T6 ✅ · T7 (PD-10/11/12) → siguiente.

### Cierre de T7 — registro de supervisión PD-17 (2026-09-29, orquestador Claude)

- **(a) Resultado vs contrato**:
  - **PD-10 (T7a)**: `33bf757` + corrección de review `c9f1448`
    (cdad-test-writer, glm-5.3-flash). Auditoría de cada assert de F001, F009
    y P1 con tabla de trazabilidad (conservado / sustituido / retirado). Los
    asserts por texto (p. ej. `'models'` presente en el archivo) se
    sustituyeron por evaluación findLast de los mapas de permisos generados
    (`tests/pd10_permission_semantics.py`, que reutiliza el evaluador
    existente). Las listas `FORBIDDEN_BASH_*` y los asserts "sin `"*": allow`"
    constan como **retirados por decisión del dueño (`80f9b90`)**, no
    reintroducidos (M12 lo protege). La review del orquestador halló H1 (las
    mutaciones no ejecutaban el reemplazo) y H2 (M6 no mataba su reemplazo,
    reproducido: 27/27 con la mutación). Corregidos; reverifiqué M6 → FAIL
    trazado, 26/27. El árbol real queda en 39/39.
  - **PD-11/12 estático (T7b)**: `881830e`, `tests/test_004_001_t7_capacity.py`
    (6 tests; mi corrida: 6 passed). Instalación aislada `--basic`, consumidor
    sintético fuera del checkout (PATH y PYTHONPATH sin el repo), `rtk wc -l`
    con Σ del propio comando, runner `pytest`, git no mutante, CLI instalado.
    PD-12 en ambas direcciones sobre los bytes instalados (evaluación del
    modelo de permisos, etiquetada como tal) y ejecución real del
    `path-guard.sh` instalado (exit 2 / 0). El lado negativo de bash se
    declara N/A por decisión del dueño.
  - **PD-11/12 runtime vivo + criterio 6**: `evidence/t7-live-walk.md`
    (`660d0c6`, saneado en `61a6af3`). 5 roles sobre la instalación real en un
    repo sintético, escritores con glm-5.3-flash y lectores con
    deepseek-v4.1-flash. Ciclo sub RED→GREEN→APTO, 39 llamadas, **0
    denegaciones**. Fricción: `rtk wc -l <dir>` da Σ 0 con rc=1 (F-W1).
  - Validadores: consistency PASS, odoo-specialization PASS (tras el
    saneamiento), subagents PASS.
- **(b) Ámbito de cambios**: `33bf757`/`c9f1448`/`881830e` solo `tests/`
  (contenido revisado). Los commits de evidencia y registro son del
  orquestador.
- **(c) Desviaciones y disposición proporcional**:
  - **Orquestador**: el log vivo commiteado llevaba la identidad git del
    dueño (el implementer comitea con la identidad global) y rompió A3.
    Disposición: saneado (`61a6af3`). En recorridos futuros, configurar una
    identidad sintética en el repo consumidor antes de despachar.
  - **Test-writer (T7b)**: fuera de su ámbito, movió el log de evidencia del
    orquestador y usó `git stash push/drop` en el árbol compartido para
    diagnosticar A3. Sin pérdida (el stash solo contenía el log movido, que
    fue restaurado). El diagnóstico fue correcto y lo reportó. Disposición:
    **registrar + principio explícito** en los paquetes siguientes, no una
    lista de comandos prohibidos (corrección de la review de GPT,
    2026-09-29): "Puedes decidir cómo completar tu encargo dentro de tu
    ámbito. No alteres cambios ajenos ni el estado compartido del
    repositorio para resolver obstáculos. Si el problema requiere intervenir
    allí, entrega tu trabajo y el diagnóstico al orquestador, que decide cómo
    continuar." Con escritores concurrentes: espacios de trabajo separados o
    un único responsable de integrar. Sin barrera nueva.
  - **Test-writer (T7b)**: reporte final en chino (deriva de idioma del
    modelo). Disposición: verificación directa del test por el orquestador;
    fricción registrada.
  - **T7a**: el primer entregable de mutación era autocomplaciente (probaba
    el evaluador, no el reemplazo). Disposición: review → corrección en la
    misma sesión.
- **Estado**: T1–T7 ✅. Para cerrar 004-001 faltan: registros PD-17 de T4 y
  T5 en este archivo, verificación de los criterios de aceptación 1–6 y
  merge/Memory Bank (scribe).

### Cierres de T4 y T5 — registro PD-17 consolidado (2026-09-29, orquestador Claude)

Consolidación: el contenido existía en `docs/.cdad-state.json` y en
review-1..6, pero no en este archivo. No agrega hechos nuevos, solo los
reúne con sus referencias.

- **T4 (aterrizaje A)**
  - (a) RED `580816f`, GREEN `d011741` (bash policy derivada de la fuente
    canónica, pares completos de los writers). Review-fix de review-1 (B1
    `git git`, B2 installer con política antigua: `be06c94`, `297a77a`), de
    review-2 (R2-B1 selección por stack: `5f2389c`, `71f17ee`) y de review-3
    (R3-B1 TMPDIR/HOME: `2b93158`, `3b9c998`). Review-4 **approved** 0/0/0.
  - (b) Ámbito: `scripts/cdad-bash-allowlist.sh`, generador, salidas
    declaradas y tests de regresión. Verificación del orquestador en cada
    fix (PD-2 byte a byte, `--check` 46/46).
  - (c) Desviaciones: paquete green-001 con shell denegado (sin cambios) →
    green-002. Lección de review-3: una corrida verde que depende del entorno
    no prueba la garantía → bucket 003-003. F011 → T5/T6.
- **T5 (instalación con propiedad/manifest)**
  - (a) RED `tests/test_install_ownership.py` (10 RED), GREEN `8a9a3c4` + 3
    fix-loops del orquestador (`c39aa9a`, `bf1918c`, `964e622`). Review-5:
    4 bloqueantes → RED `3a267ad`, oráculo E1 `9302c1f`, fix `762248d`.
    Review-6: R6-B1 (ayuda de `--basic`) cerrado por el camino mínimo
    avalado. Dictamen: T5 cierra.
  - (b) Ámbito: `install.sh`; `scripts/cdad-generate.py` tocado desde T5
    (manifest de staging combinado, lo exigían los tests aprobados).
  - (c) Desviaciones: el propio toque al generador (justificado); fuga de
    fase marginal del test-writer (greps a `install.sh` para viabilidad de
    fixtures), dispuesta en review-6 como no material, con causa → 003-003;
    dos despachos silenciosos recuperados sin pérdida. Regla nueva para T6:
    oráculos congelados antes del GREEN.
