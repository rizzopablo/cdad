# Informe del architect — spec/plan 004-001 + delta C0 (encargo de la enmienda vigente)

Sesión aislada cdad-architect vía delegación nativa; materializado por el orquestador GLM el 2026-09-24. Base: HEAD `e7f68a1`. Envoltorio de delegación omitido de origen (política de sanitización tras el dictamen C0); cuerpo íntegro sin edición.

---

# Informe del architect — preparación ejecutable de 004-001 (encargo inmediato de la enmienda C0)

## 0. Estado verificado

- **Repositorio**: anidado en `cdad/` dentro del proyecto; rama `codex/epic-003-context-efficiency`; HEAD `e7f68a1` (verificado con `git log`: `e7f68a1 → 9edda07 → 37e23f3`). Cambios documentales sin commit leídos tal como están en disco: sin trackear `docs/epics/epic-004-single-source-planning/{c0-amendment...,c0-review-gpt...,plan,planning-contract-draft}.md` y `findings/permission-friction-c0-2026-09-24.md`.
- **State** (`docs/.cdad-state.json:4-17,18-41,385-394`): `active_epic: epic-003-context-efficiency`, `epic_stage: features-loop`, `active_feature: null`, `current_stage: idle`, `stack: null`; 003-001 y 003-005 `done`, 003-002/003/004 `queued`; `hitl_delegation` activa → Codex/epic-003 (`:386-394`). Epic 004 no existe en el state. **No toqué el state.**
- **Baselines reproducidas hoy** (focaliza la errata R2): `rg -c '' agents/cdad-*.md agents/claude-code/cdad-*.md` → **22 archivos, 2.697 líneas** (OC 1.572: 120/112/147/132/214/165/107/101/97/204/173; CC 1.125: 72/61/115/82/220/115/55/81/46/180/98). **Los bytes (140.161, archivos completos UTF-8, con frontmatter, no tokens) no pude medirlos en esta sesión**: la regla vigente me deniega `wc`/`du` y no existe el par `rtk wc *` — exactamente el caso documentado en `findings/permission-friction-c0-2026-09-24.md:31-44`. Atribuyo los bytes al dictamen GPT, que los reprodujo con lectura binaria independiente (`c0-review-gpt-2026-09-24.md:86-96`); los recompro cuando la política lo permita (tarea T1).
- **Live-check de la regla**: el error de permiso de esta sesión muestra `"wc *": allow` sin `rtk wc *`, y denies de `mktemp`, `/tmp` y catch-all — confirma el gap del par y el mecanismo catch-all+findLast descrito en `scripts/cdad-bash-allowlist.sh:19-29,51-57,125-133,152`.
- **Reproducción de código**: `cdad_packet.py` — contrato de paquete (`:401-437`), límite 12.000 bytes (`:411-412`), `VALID_CONTRACT_KINDS` = `approved-epic-plan|approved-feature-spec` (`:43`), modos `ordinary` vs `scoped-exception` (`:219-258`), `prepare` exige `.cdad/execution.json` a mano y escribe `state.execution`+`active_packet` (`:552-556,590-595`), rollback acotado (`:605-623`).
- **VERIFY resueltos del informe anterior (§6)**: (1) `tests/validate-odoo-specialization.sh` — asserts P1 sobre allowlists de las 5 variantes odoo (`:141-182`, listas FORBIDDEN `:139-140`), P2 contenidos de skills (`:188-212`), P3 Make contract (`:218-229`), P4 stack en SKILL.md (`:237-238`), P5 `install.sh` odoo (`:244-245`), P6 traps (`:254-265`), A3 sanitización (`:281-301`); (2) **consumidores del layout público confirmados**: `tests/test_role_packet_consumers.py:46-47` resuelve `install_root/"skills/cdad-cycle/scripts/cdad_packet.py"` y `install_root/".config/opencode/agents"` — el fixture consume `$INSTALL_ROOT/skills` (layout público) además de destinos runtime; (3) **R3 intake**: `agents/claude-code/cdad-architect.md:17` omite `cdad-spec-and-test` en legacy-path, mientras `agents/cdad-architect.md:65`, `agents/claude-code/cdad-architect-odoo.md:17` y el test-writer CC sí lo cargan — divergencia de port sin decisión que la justifique.

---

## 1. Delta C0 (R1–R3 + precisiones)

Este delta **no reescribe** el informe histórico; las correcciones se registran como errata enlazada (patrón del dictamen, `c0-review-gpt-2026-09-24.md:228-236`).

### 1.1 Correcciones de hechos del informe anterior (errata a registrar en el documento original, con enlace a esta sección)

| Afirmación original                                                                                          | Estado                       | Corrección                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------ | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2.554 líneas / OC 1.475 / CC 1.079 (`c0-architect-report:27,138,158,272`)                                      | **Errata**                       | 22 archivos / **2.697 líneas** / OC **1.572** / CC **1.125** (ambos scribe-odoo omitidos de la suma: 97 + 46). Reproducido hoy (§0). Enlazar errata a `c0-review-gpt:88-94` y al finding `:12-16`.                                                                                           |
| "sin sandbox de archivos en sub-agentes" atribuido al runtime elegido OpenCode (`c0-architect-report:208,275`) | **Errata de atribución**         | La observación filesystem-compartido/sin-política-por-hijo es de **Codex nativo**; el smoke OpenCode falló por lectura de **config heredada** fuera de raíces temporales. Ni eso ni lo otro demuestran ausencia de controles mediados por hooks en OpenCode (`c0-review-gpt:120-146`). |
| Capacidades "confirmadas" del runtime (`c0-architect-report:205-210`)                                          | **Errata de clase de evidencia** | Separar: observado en Codex / expuesto por ayuda-tipos OpenCode / probado en sesiones vacías / pendiente de comprobación efectiva. El metadato de sesión 1.18.16 no certifica el binario actual (finding `:47-50`).                                                            |
| D2 con techo de líneas como criterio de cierre (`c0-architect-report:157`)                                     | **Errata de criterio**           | Sustituido por: salidas declaradas generadas sin edición manual, una fuente editable por regla compartida, regeneración reproducible, diferencias de adaptador justificadas. Conteo = diagnóstico, no gate (`c0-review-gpt:96-114`; enmienda `:34`).                             |
| D9 "state conserva 003 activo" como solución de ejecución (`c0-architect-report:164`)                          | **Errata de alcance**            | Válido solo mientras 004 es propuesta. La ejecución de 004-001/002/003 exige el procedimiento de activación de §6 (enmienda `:33`).                                                                                                                                            |

### 1.2 Resolución de precisiones del dictamen (binding)

| Punto | Incorporación concreta |
|---|---|
| **D1** | Markdown con delimitadores + generador Python stdlib, **elegido por claridad de autoría/composición** (no "JSON no tiene parser": json está en stdlib y permite prompts autocontenidos). La spec de §7 fija ubicaciones, delimitadores y error por fuente incompleta/duplicada. Las 400–700 líneas son estimación, no requisito. |
| **D4** | Manifest de propiedad con semántica completa: **primera instalación sin manifest → registro/adopción sin borrado**; archivo instalado modificado localmente (hash ≠ registrado) → **conflicto informado, sin sobrescribir/borrar en silencio**, resolución explícita; dry-run lista acciones; uninstall solo entradas del manifest. Detalle en §4. |
| **D5** | Se editan las **fuentes**; las salidas se regeneran marcadas con origen. **No se prohíbe** editar fuentes legítimas de agentes por llamarse "agente" — prohibirlo sería perpetuar la política antigua por inercia. |
| **D6** | Default = destinos runtime reales. Fixtures migran a ese layout (consumo confirmado en §0). El layout público (`$INSTALL_ROOT/agents|skills`, `install.sh:34-35,605,627-628`) solo sobrevive como opt-in si un consumidor real lo justifica tras migrar; no para perpetuar el fixture. |
| **D7** | Las assertions que fijan mecanismo (F001 igualdad de bytes `validate-consistency.sh:264-275`; detalles de nombres F009 `:147-198`; FORBIDDEN lists P1 odoo `:139-182`) se **reemplazan en el mismo cambio coherente** por comprobaciones de garantías/capacidades, no se congelan ni se eliminan a secas. F001 se conserva solo hasta que exista el generador dentro de la misma entrega. |
| **D8** | La revisión de borradores es requisito explícito de 004-003 (`plan.md:268-274`, renderer solo acepta `approved-*`); mientras tanto, handoff legacy **identificado como tal** para revisar los borradores de 004 (el dictamen de esta spec/plan se hará por ese camino). Sin falsificar `approved`. |
| **D10** | Tres features. T1 (baseline) es **preparación/evidencia**, sin ceremonia RED/GREEN. Las tareas de arquitectura/generador/instalador sí llevan sus mini-ciclos contractuales. |
| **D11** | ADR-011 gobierna el diseño de permisos: capacidades + instrucciones + supervisión; simplificar antes de generar (enmienda `:44,151-153`). No se reabre la elección metodológica. |
| **Fricción** | El par `rtk wc *` faltante **no se parchea aislado**: se resuelve dentro de la simplificación de controles de 004-001 (§3, fila A1). ADR-011 no globaliza el caso ni extrapolan tasas. |
<!-- table not formatted: invalid structure -->

---

## 2. Capacidades y controles por rol

Fuente: tabla de capacidades de ADR-011 (`ADR-011:88-101`), dirección recomendada del finding (`:80-101`) y controles actuales inspeccionados. "Read-only" = no editar el producto/repo; sí temporales/logs en espacio declarado (`ADR-011:98-101`).

| Rol         | Resultado esperado                                                          | Decisiones autónomas                                                                                    | Capacidades necesarias                                                                                                                                                                                                                           | Invariantes retenidas (motivo)                                                                                                                                                           | Evidencia que comprobará el orquestador al re-entry                                                                                            |
| ----------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Architect**   | Contratos y dudas fundamentadas; delta sobre decisiones, no re-discusión    | Estrategia de exploración, forma de medir/agregar, qué VERIFY declarar                                  | Leer todo el repo permitido; **medir y agregar deterministamente** (conteo de líneas/bytes sin rechazos falsos — lección del finding `:72-73,86-94`); calcular/contrastar opciones; temporales declarados                                              | No modifica el producto ni aprueba su propuesta (`ADR-011:92`); ADR-003 de materialización intacto                                                                                         | Informe con citas file:line; dudas acotadas; diff del repo sin cambios de producto; método/versión/config de medición registrados (lección R2) |
| **Test-writer** | Tests que derivan del contrato y falsifican las postcondiciones             | Estrategia de falsificación, organización de tests, comandos del runner acordado                        | Editar tests autorizados, ejecutar por el runner acordado, commit de su artefacto (contrato §5, hoy `validate-consistency.sh:163-165`)                                                                                                             | **No inspeccionar implementación** (sesión aparte + guard) — si lee src, la RED queda contaminada y pierde independencia (`ADR-011:71`; finding `:119-122` dice que esta frontera NO se elimina) | Logs RED/GREEN; diff limitado a tests; ausencia de lecturas de impl declaradas honestamente (con límite: guard por nombre ≠ sandbox)           |
| **Implementer** | GREEN con los tests aprobados intactos                                      | Cómo resolver/depurar dentro del alcance; orden de cambios                                              | Editar src, ejecutar tests, ver diff propio, commit                                                                                                                                                                                              | **No editar tests** (anti-gaming: quien construye no valida su validador); conservar tests aprobados                                                                                         | `git diff --stat` como orientación + revisión de contenido; snapshot de tests al ejecutarlos, no solo estado final (`ADR-011:111-116`)             |
| **Refactorer**  | Misma fase implementer, substage `refactor`/`review-fix` (`cdad_packet.py:44-50`) | Equivalentes al implementer                                                                             | Equivalentes; + mantener verde la suite                                                                                                                                                                                                          | Idénticas al implementer; refactor no cambia contrato observado                                                                                                                          | Diff con comportamiento preservado; misma evidencia                                                                                            |
| **Reviewer**    | Dictamen fiel con hallazgos/severidad/abstenciones                          | Qué verificar, cómo contrastar afirmaciones del autor                                                   | Leer entradas necesarias (incl. código y specs), **ejecutar validadores/tests cuando el contrato de revisión lo pida** (hoy denegado a lectores: `cdad-bash-allowlist.sh:29,184-195` — brecha de capacidad que propongo cerrar, costo en §3), calcular | No modifica ni aprueba el producto (`ADR-011:95`); sesión independiente del autor                                                                                                          | Verdict-tuple + abstinencias (F004, `validate-consistency.sh:118-136`); no acepta conclusión del autor como prueba                               |
| **Scribe**      | Borradores de Memory Bank fieles a la evidencia                             | Estructura de la memoria; qué resumir vs citar                                                          | Leer evidencia/state/historia; escribir en espacio declarado (borradores)                                                                                                                                                                        | Materialización oficial bajo ADR-003 (`ADR-011:101`); no aprueba                                                                                                                           | Borrador trazable a evidencia; aprobación por el orquestador/usuario (patrón Scribe)                                                           |
| **Orquestador** | Encargos, materialización, verificación proporcional, replanificación       | Decisiones rutinarias dentro de contratos aprobados; respuesta proporcional a desvíos (`ADR-011:118-124`) | Preparar/despachar, `git diff`/estado, registros de incidentes, sin microgestionar cada comando                                                                                                                                                    | No autoaprueba specs/planes; escalar lo que excede el mandato                                                                                                                            | Resultado vs contrato, ámbito de cambios, evidencia de tests, revisión efectiva (`ADR-011:104-109`)                                              |

Fronteras honestas transversales (se declaran en los agentes generados): sesión ≠ sandbox; paquete no impide otras herramientas; guard de Edit/Write no media Bash automáticamente (`ADR-011:75-79`; finding `:116-118`).

---

## 3. Keep/simplify/remove de controles actuales

Cada barrera retenida declara: efecto protegido, mecanismo, límite conocido, y verificación de que no bloquea trabajo legítimo.

| Control actual (cita) | Decisión | Razón / efecto protegido | Límite conocido y verificación | Costo |
|---|---|---|---|---|
| `scripts/cdad-bash-allowlist.sh`: pares `X*/rtk X*` + catch-all deny con findLast (`:51-57,125-133`) | **SIMPLIFICAR** (y migrar a fuente única en T3/T4) | El mecanismo de pares es correcto (cdad-010) pero **incompleto por inercia**: `wc *: allow` sin `rtk wc *` (`:152`; causa directa de la fricción C0). Se conserva el generador como **adaptador de transición** con pares completos, y cada regla pasa a declarar su efecto; el catch-all deny se conserva porque hace que los pares sean aditivos y seguros por defecto. El bloque de lectura-denies para writers (`:135-141`) **se retiene** | Mecanismo: nombres de comando; un wrapper distinto del previsto no es capturado — declarado como límite, no vendido como sandbox. Verificación: pruebas **positivas** de capacidad (medir/agregar/ejecutar desde el rol) + negativas; un falso rechazo de trabajo legítimo es defecto del producto (enmienda `:110-111`) | Mantenimiento dual temporal hasta que la fuente canónica genere este bloque; `du *`/agregador determinista para roles lectores como regla de capacidad declarada |
| Par faltante `rtk wc *` | **Resuelto aquí** (no parche aislado) | Forma parte del lote de simplificación: en el estado final la tabla de capacidades genera los pares, y la omisión no puede repetirse por deriva manual | — | La fricción `wc` persiste hasta que 004-001 aterrice: costo aceptado y documentado (enmienda `:107-108` prohíbe patch-ecommerce aislado) |
| `scripts/claude-code-path-guard.sh` (matcher por rol `:171-256`; guard Bash por nombre `:40-64`; fail-open rol desconocido `:258-261`) | **CONSERVAR** simplificado | Protege las dos invariantes metodológicas retenidas: test-writer sin leer implementación y implementer sin editar tests (incl. tests co-ubicados, `:154-161`). Son límites de rol, no de "poder abstracto" (finding `:119-122`) | Límite: solo media Edit/Write/Read/Grep/Glob + comandos nombrados; no garantiza contra evasión deliberada; fail-open en rol desconocido. Verificación: pruebas positivas (test-writer puede editar su suite, implementer puede editar src) y negativas por rol | Mantenimiento del script y de sus glóbs; se documenta como prevención de accidentes, no aislamiento |
| Renderer: límite 12.000 bytes del bloque estático (`cdad_packet.py:411-412`) | **SIMPLIFICAR**: convertir de constante dura a parámetro de política declarado en la fuente, con diagnóstico al superarlo | Protege el presupuesto de contexto del paquete (objetivo, no garantía — `runtime-discovery.md:39-42` vía informe previo); el valor puede cambiar por decisión, no por edito el código | Si un paquete legítimo excede el presupuesto, es error de entorno con diagnóstico breve al orquestador (matriz §5), no evasión | Cambio pequeño en renderer + test de que el exceso produce error claro, no mezcla |
| `prepare` exige `.cdad/execution.json` manual (`cdad_packet.py:552-556`) | **RETENER en 004-001; resolver en 004-002** | ADR-003/contrato de materialización no se toca en 001; el bootstrap orgánico de la identidad es el entregable de 002 (`plan.md:189-198`) | Ninguno en 001 | — |
| F001 (igualdad byte-a-byte del bloque §2 entre 3 copias, `validate-consistency.sh:264-275`) | **RETIRAR al aterrizar el generador, en el mismo cambio coherente (D7)** | Fija igualdad de bytes, no semántica; propaga errores de diseño entre runtimes (los modelos de diseño OpenCode aparecen en la copia CC — R1 del inventario) | Hasta el reemplazo sigue como guard temporal | Dos controles conviviendo brevemente; riesgo de falso verde si se olvida el reemplazo → mitigado con postcondición PD-10 |
| F009: asserts de nombres exactos de comandos en allowlists (`validate-consistency.sh:147-198`) | **SUSTITUIR por semántica** en el mismo cambio | El efecto (writer no lee contenido vía bash; git commit/add disponible) es garantía; la lista de nombres es mecanismo. Reemplazar por: determinismo del bloque derivado + comprobación de efecto | — | Reescritura del validador con trazabilidad al requisito nuevo |
| P1 de `validate-odoo-specialization.sh` (listas FORBIDDEN y nombres, `:139-182`) | **MIGRAR semántica**: reglas odoo (no `go/python/psql` crudos, pylint/pre-commit presentes, git acotado) pasan a validarse sobre la **fuente/salida generada**, no sobre bytes de copias manuales | Las reglas odoo son decisiones reales; el modo de verificarlas es lo que migra | Regla vs. garantía: los asserts actuales pinzan el mecanismo; se conservan las garantías semánticas equivalentes | Actualización de asserts con trazabilidad (enmienda, fila tests del mapa `:58`) |
| Layout público `$INSTALL_ROOT/agents|skills` (`install.sh:34-35,605,627-628,847,706,719`) | **RETIRAR del default** (D6) | Ningún runtime lo lee (`activeContext.md:62-67` vía R6); genera carpetas muertas | Consumidores confirmados: fixtures `test_role_packet_consumers.py:46-47` → migración obligatoria; opt-in solo con justificación de consumidor real | Migración de 2 suites de fixtures; nota de compatibilidad |
| Sin `--delete` en rsync (`install.sh:532-537`) | **CONSERVAR** (con manifest de propiedad, §4) | Protege datos ajenos en carpetas compartidas; el problema de obsoletos lo resuelve el manifest, no el borrado global | Obsoletos quedan hasta manifest → declarado | Coste del manifest (~100–200 líneas, D4) |
| Protecciones del instalador (solape fuente/destino, symlinks, rollback acotado — `plan.md:166-169`) | **CONSERVAR** | Efectos destructivos reales y difíciles de revertir | — | Ninguno |
<!-- table not formatted: invalid structure -->

---

## 4. Interfaces, fuentes y tareas de 004-001

### 4.1 Fuentes canónicas y formato (D1 corregido)

**Formato elegido**: Markdown con delimitadores explícitos + generador Python stdlib — mismo patrón ya probado por `cdad_packet.py` (entrada explícita → artefacto reproducible, hashes en `instruction_sources`, `cdad_packet.py:418-421`). Justificación corregida: **claridad de autoría** (la prosa del rol es el contenido; JSON exige diseñar un schema primero y la autoría de reglas en prosa es peor). JSON descartado por claridad, no por capacidad técnica. Delimitadores: `<!-- cdad-source:role:NOMBRE -->` … `<!-- /cdad-source -->`; **fuente incompleta/duplicada → error explícito del generador** (postcondición PD-2).

**Rutas fijadas por la spec** (nuevas, no existen hoy — VERIFY si el orquestador prefiere otras):

- `sources/roles/<rol>.md` — contrato canónico por rol (directiva, intake único, invariantes, tabla de capacidades §2). 5 roles: architect, test-writer, implementer, reviewer, scribe (+ delta odoo como variante declarada por stack, sin clonar el procedimiento).
- `sources/agents/adapters/opencode.md` y `sources/agents/adapters/claude-code.md` — deltas legítimos por runtime: nombre de herramienta (`skill` vs `Skill`), formato del bloque de permisos (`bash:` YAML vs hooks `PreToolUse`), mecanismo de carga. Los deltas se **declaran**, no se comparan byte a byte (R3 del inventario).
- `scripts/cdad-generate.py` — generador (Python stdlib). Firma: `cdad-generate.py --runtime opencode|claude-code --stack auto|odoo --profile <p> --out <staging>`.
- `build/staging/` — salida reproducible: `agents/<runtime>/cdad-*.md` + `manifest.json` (por artefacto: sha256, fuentes que lo produjeron, comando de regeneración, stack/perfil usados).
- `install.sh` consume **staging** (no las fuentes) y mantiene el manifest de propiedad en el raíz de instalación (D4).

Separación generación/instalación ya establecida (`plan.md:96-99`): el stack/perfil es **entrada explícita registrada en el manifest**, no efecto oculto de la máquina.

### 4.2 Semántica del manifest de propiedad (D4, completa)

1. **Primera instalación sin manifest** (máquina nueva): el instalador registra propiedad (lista+hashes de lo que CDAD instala) y **no borra nada**. VERIFICABLE: tras instalar, el manifest existe y lista exactamente lo copiado.
2. **Actualización con manifest**: para cada destino, comparar hash actual contra el registrado. (a) igual → actualizar; (b) modificado localmente (hash ≠ registrado) → **conflicto**: informar archivo, hash esperado/actual, **no sobrescribir ni borrar en silencio**; resolución explícita (`--force-file` por archivo o intervención humana); (c) presente en manifest pero ausente del nuevo staging (renombrado/retirado) → candidato a obsoleto: se lista en dry-run, se borra solo con confirmación explícita; un archivo renombrado no deja huérfano silencioso.
3. **Uninstall**: borra únicamente entradas del manifest (no globs de carpeta compartida — mantiene el criterio actual de `uninstall_items` por manifest de fuente, `install.sh:696-727`, pero ahora registrado por hash).
4. **Symlinks/rutas fuera de destino**: rechazo explícito (se conservan las protecciones vigentes del instalador, fila 10 de §3).
5. **Dry-run**: lista cada acción de escritura/borrado/conflicto sin ejecutarla.

### 4.3 Coherencia OpenCode primero / Claude Code después

- Primera aplicación de la simplificación: **OpenCode** (runtime del desarrollo real; enmienda `:151-153`).
- Claude Code: se verifica contra el **mismo contrato** (misma tabla de capacidades semántica, deltas declarados por adaptador: hooks `PreToolUse` y frontmatter). **No** se compara byte a byte entre runtimes (divergencia de herramienta es legítima, R3 del inventario); el block §2 deja de contener modelos de diseño de un runtime en el otro (R1 del inventario: la tabla pasa a referencias simbólicas o se deriva de `scripts/cdad-models.sh`).
- Selección de modelos: **no se cambia** en este feature (`plan.md:146-147`: "No cambiar la selección de modelos como parte del refactor"); `cdad-models.sh` sigue siendo la única fuente del mapa (R4 del inventario).

### 4.4 Tareas internas de 004-001 (vista; plan completo en §8)

T1 medición baseline → T2 contrato de capacidades/fuentes → T3 generación+simplificación de adaptadores (OC primero) → T4 instalación/manifest → T5 coherencia Claude Code → T6 **prueba de capacidad desde el producto instalado** + reemplazo de assertions F en el mismo cambio + migración de fixtures. La prueba de capacidad (checklist item 4) es obligatoria: medir (`wc`/`rg -c`), **agregar deterministamente** (pares completos; el incidente C0 fue exactamente la agregación sin comando fiable, finding `:54-66`), y ejecutar el trabajo autorizado (runner acordado, git no mutante) **desde el producto instalado**, sin depender del checkout como ruta de ejecución (`plan.md:184-185`).

---

## 5. Matriz de tratamiento proporcional

| Situación                                                                            | Tratamiento                                                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Trabajo permitido (dentro del encargo) → termina**                                     | El agente elige herramientas/estrategia dentro del marco (`ADR-011:56-58`); el orquestador verifica al límite de tarea/subfase (`:104-109`). No se pide permiso por herramienta.                                                                                                   |
| **Efecto fuera de alcance →**                                                            | Se trata según contrato: comprobar autoridad vigente antes del efecto; si no existe, escalar — sin evasión encubierta ni reintento equivalente (`ADR-011:69-73`). Ejemplos frontera: escribir fuera del rol → ámbito + diff al re-entry; acción externa no autorizada → escalar. |
| **Error de entorno (deny inesperado, herramienta incompatible, presupuesto excedido) →** | Vuelve al orquestador con diagnóstico breve (llamada, regla/limitación conocida o desconocida), **sin bucle** de reintentos equivalentes ni sustitución de cálculo por estimación presentada como medido (finding `:95-100`). Un deny no es incumplimiento del agente (`ADR-011:121`). |
| **Desviación explicada sin violar invariantes →**                                        | Resuelta dentro del mandato, documentada; sin repetir toda la tarea (`ADR-011:122`; enmienda `:110`).                                                                                                                                                                              |
| **Incumplimiento material / evidencia inválida →**                                       | No se cierra el gate afectado; se corrige o repite **solo lo invalidado** (`ADR-011:123`).                                                                                                                                                                                           |
| **Evidencia exacta →**                                                                   | Salida original íntegra para mediciones; wrapper de reducción solo si conserva la semántica (finding `:92-94`); estado "completada" de una herramienta ≠ éxito semántico (`:26-28`); bytes ≠ tokens; entradas sintéticas ≠ consumo observado (`c0-review-gpt:108-114`).              |

**Limitaciones honestas que la spec obliga a declarar en los agentes** (no protege esto el paquete): la sesión aislada no es sandbox; el paquete no bloquea otras herramientas; el path-guard solo media Edit/Write/Read/Grep/Glob y comandos Bash nombrados; las allowlists no garantizan solo-lectura de todos los comandos permitidos (ej.: `make *` depende de la receta, finding `:75-78`); un guard `PreToolUse` no cubre efectos de programas que el propio runtime lanza.

---

## 6. Procedimiento de activación de 004 y retomada de 003

Resuelve R1/D9. **Propuesta; NO se ejecuta en este turno** (estoy en modo read-only y sin autoridad registrada).

### 6.1 Precondiciones (todas obligatorias)

1. Revisión focal de esta spec/plan (GPT o Claude) conforme; hallazgos resueltos.
2. Documentos versionados: commit de la enmienda C0, dictamen, `plan.md`, planning-contract-draft, findings, esta spec/plan y el delta (observación 2 del dictamen, `c0-review-gpt:189-192`) — sin mezclar cambios ajenos.
3. **Aprobación de la spec con postcondiciones registrada** (patrón CDAD: marca de aprobación del responsable autorizado en `docs/specs/004-001-canonical-runtime-artifacts/approval.md`).
4. **Registro de autoridad** de ejecución de epic 004 en `docs/epics/epic-004-single-source-planning/execution.md`: alcance, responsable (GLM construye; GPT/Claude análisis/review), decisiones delegadas, vencimiento (cierre/cancelación/revocación del epic). **La firma es del usuario** (requested_by: usuario) — es la misma autoridad estratégica que ya decidió ADR-011, ahora referenciada; la delegación HITL vigente de Codex **no se hereda** (`c0-architect-report:225`).

### 6.2 Pasos de activación (secuencia exacta; un único write del state)

1. **Snapshot/handoff de 003** (antes de tocar el state): crear `docs/epics/epic-003-context-efficiency/handoff-suspension.md` con: features 003-001/005 `done`, 003-002/003/004 `queued` con su contexto de drafts, decisiones vigentes, delegación HITL vigente (texto literal de `state:386-394`), y el SHA del commit que congela el state pre-activación. Commit.
2. **Escritura del state** (única, coherente, por el orquestador con la autoridad de 6.1):
   - `active_epic` → `epic-004-single-source-planning`
   - `epic_stage` → `epic-planning` (y luego `features-loop` al iniciar 004-001; valores existentes en el template, `cdad_packet.py:34` — **sin crear nuevos valores de etapa**)
   - `active_feature` → `null` (o `004-001-canonical-runtime-artifacts` al empezar su ciclo)
   - `epic_features` → lista de 004: las tres features con `status: queued`
   - `hitl_delegation` → reemplazar por el registro de 004 (mismo esquema: delegated_to GLM, requested_by usuario, scope del epic 004, expires en los 3 eventos estándar, source = la autoridad de 6.1); la delegación de Codex/epic-003 **no se borra**: se archiva en `delegation_history` con nota `status: suspended`
   - `approver`, `last_updated` → actualizados
   - `stack` → `null` hasta que un feature lo fije
   - `epic_history` → entrada de activación (evidence: el commit del snapshot; approved_by: usuario). No crea motor multi-epic: el progreso de 003 vive en `epic_features`+historia+git, y el de 004 en su propio directorio `docs/epics/...`.
3. **Verificación post-activación** (criterio de resolución de R1): una sesión nueva que lea el state identifica `epic-004` como único epic activo y la feature correcta; no hereda delegación de otro epic. Se comprueba ejecutando la detección existente, sin código nuevo.
4. **Ningún paquete se prepara** hasta que la spec 004-001 esté aprobada y versionada (enmienda `:96-98`).

### 6.3 Retomada de 003 (sin restauración ciega)

1. Entrada: el handoff-suspension + el diff git del state en el momento de la suspensión + `epic_history`.
2. **Reconciliación**: el orquestador compara el progreso conservado con el estado actual (features done/queued de 003 no se restauran a ciegas; los cambios de 004 que afecten a 003 —p. ej. el nuevo runtime de paquetes— se declaran en el handoff de reanudación). Progreso de 004 conservado en su directorio; `epic_features` vuelve a listar las 5 features de 003 con sus estados reconciliados.
3. Re-registro de la autoridad HITL de 003 con **confirmación explícita del usuario** (no restaurar el JSON antiguo que reactivaría la delegación de Codex sin nueva autoridad).
4. Nueva entrada en `epic_history` con la evidencia de reconciliación. Sin restauración ciega ni motor multi-epic (enmienda `:33`).

---

## 7. Spec draft 004-001

*(Texto final para materializar por el orquestador en `docs/specs/004-001-canonical-runtime-artifacts/spec.md`; sin marca de aprobación.)*

**Feature ID**: `004-001-canonical-runtime-artifacts` · **Epic**: `epic-004-single-source-planning` · **ADR-011 gobierna el diseño de permisos**.

### 7.1 Descripción funcional

La política de roles de CDAD se define por capacidades y efectos (ADR-011): cada rol recibe las capacidades necesarias para su encargo y pocas barreras duras, cada una con efecto protegido, mecanismo y límite declarado. Esa política vive en **fuentes canónicas editables** (Markdown con delimitadores) de las que un generador determinista (Python stdlib) produce los 22 agentes en **staging** con manifest; el instalador despliega en destinos runtime reales con **propiedad de archivos** (manifest de instalación, D4). OpenCode es la primera aplicación; Claude Code se verifica contra el mismo contrato semántico con deltas declarados. Antes de generar: baseline de medición registrada (T1, preparación sin ceremonia RED/GREEN, D10) y simplificación de los adaptadores/controles actuales (§3), resolviendo dentro del mismo cambio las assertions de mecanismo (D7) y el par `rtk wc` faltante. La feature termina demostrando **capacidad operativa real desde el producto instalado**.

### 7.2 Contrato

Firma del generador: `scripts/cdad-generate.py --runtime <opencode|claude-code> --stack <auto|odoo> --profile <nombre> --out <staging-dir>` → escribe `staging/agents/<runtime>/cdad-*.md` + `staging/manifest.json`. Firma del instalador: la actual de `install.sh`, consumiendo staging cuando exista (transición: generar on-the-fly deshabilitado una vez aterrizado el generador).

**Postcondiciones:**

1. **PD-1 (simplificación previa)**: la política de bash por rol resultante es derivable de la fuente canónica y cada regla se justifica por efecto declarado; no existen reglas retenidas sin justificación. Verificable: el bloque generado para cada rol × stack contiene solo reglas con comentario de efecto en su fuente.
2. **PD-2 (determinismo)**: misma entrada (fuentes + runtime + stack + perfil) produce outputs byte-idénticos en dos corridas (hash comparado).
3. **PD-3 (fallo explícito)**: fuente incompleta, duplicada o combinación no soportada (runtime×stack×perfil) → el generador termina con error y **no publica salida parcial** (staging ausente o limpio).
4. **PD-4 (fuente única)**: cada regla compartida (directiva de intake, contrato §2, regla de property tests, política de commits, corrección del intake R3 del arquitecto CC) existe en exactamente una fuente editable; el manifest referencia la fuente de cada archivo.
5. **PD-5 (propagación)**: cambiar una regla canónica y regenerar actualiza todos los consumidores declarados; `install.sh --check` detecta la copia instalada que difiere de staging.
6. **PD-6 (propiedad, primera instalación)**: sin manifest previo, la instalación registra propiedad y **no borra nada**.
7. **PD-7 (conflicto)**: archivo instalado con hash ≠ registrado → dry-run e instalación lo reportan como conflicto; ni sobrescribe ni borra sin resolución explícita.
8. **PD-8 (uninstall)**: borra solo entradas del manifest; archivos ajenos (incl. `cdad-*.md` creado por el usuario que no vino del repo) sobreviven.
9. **PD-9 (destinos)**: instalación por defecto solo en destinos runtime reales; el layout público no se instala por defecto; si existe flag opt-in, un consumidor documentado lo justifica.
10. **PD-10 (reemplazo coherente de assertions, D7)**: al cerrar la feature, F001/F009 y las listas FORBIDDEN de P1 se validan contra la fuente/salida generada con comprobaciones semánticas equivalentes (trazabilidad registrada en los asserts nuevos); ningún control se elimina sin su reemplazo funcionando.
11. **PD-11 (prueba de capacidad desde producto instalado)**: sin el repo en el path, desde la instalación aislada se completa un recorrido positivo por rol: medir (conteo de líneas), agregar deterministamente (suma recomputada mecánicamente, sin repetir la agregación fallida de C0), ejecutar el runner acordado y git de inspección no-mutante. Se registra salida exacta por comando, separada de la evidencia estática.
12. **PD-12 (pruebas positivas y negativas de fronteras)**: cada barrera retenida se prueba en ambas direcciones: la operación legítima representativa del rol **tiene éxito**, y el efecto fuera de rol queda bloqueado por el mecanismo declarado. Un rechazo de operación legítima durante el recorrido cuenta como defecto y se registra con diagnóstico.
13. **PD-13 (baseline, T1)**: artefacto de medición previo a la generación, con método, versión, configuración y conteo línea/byte por rol×runtime×camino (clásico vs paquete), con la suma verificable mecánicamente por el lector; la evidencia declara que los bytes son de archivos completos, no tokens ni contexto observado.
14. **PD-14 (coherencia entre runtimes)**: tests semánticos comprueban el significado del rol en cada runtime (p. ej. la copia CC no menciona modelos que `cdad_model_claude` no produce); la igualdad byte-a-byte del §2 deja de ser requisito y su sustituto está en verde.
15. **PD-15 (honestidad)**: ningún texto de agente/paquete generado describe sesión/paquete/worktree como sandbox ni promete aislamiento no implementado; el espacio de trabajo temporal está declarado.
16. **PD-16 (fallback legacy)**: el camino legacy (sin paquete) sigue cargando los skills correctos desde la instalación (incluye la corrección R3 del arquitecto genérico CC).

### 7.3 Invariantes verificables

1. Test-writer: no lee implementación por los caminos declarados; solo edita tests (dedicados y co-ubicados) — mecanismo actual conservado con límites declarados.
2. Implementer/refactorer: no edita tests; conserva los tests aprobados.
3. Read-only (architect/reviewer/scribe): no modifican el producto; temporales en espacio declarado permitidos.
4. Contrato de materialización ADR-003 sin cambios; la selección de modelos no se altera en esta feature.
5. Invariantes anti-trampa y especialización Odoo preservadas semánticamente (no las listas de nombres por inercia).
6. Un solo epic activo en el state; sin nuevos valores de etapa ni motor multi-epic.
7. Instrucciones nunca prometen garantías de sandbox inexistentes.

### 7.4 Criterios de aceptación

1. Matriz smoke `runtime × rol(11 agentes por runtime) × perfil soportado` desde instalación aislada: todas las celdas instaladas y verificadas con datos sintéticos, sin llamadas a proveedor.
2. Cero archivos de agente editados a mano tras el aterrizaje del generador (los 22 pasan a ser salidas declaradas).
3. Los tres validadores existentes en PASS o sus assertions migradas con trazabilidad en el mismo cambio (PD-10).
4. Recorrido de capacidad (PD-11) completo, con cero rechazos injustificados; cada rechazo real registrado con diagnóstico breve.
5. Baseline PD-13 registrada antes de la primera generación; conteos reportados como diagnóstico.
6. Fricción medida en el primer recorrido real y entregada como entrada a 003-003, sin exigir ahorro porcentual.

---

## 8. Plan draft 004-001

*(Texto final para materializar en `docs/specs/004-001-canonical-runtime-artifacts/plan.md`.)*

**Tamaño de tarea**: la unidad mínima que cierra en su propio mini-ciclo y que un reviewer puede rechazar sin rechazar a su vecina. Sin placeholders.

| Tarea                                                                | Archivos                                                                                                                               | Consumes → Produces                                                                                                                                                                                                                                                                        | TDD / evidencia                                                                                                                                                                                                                                       |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **T1 — Baseline de instrucciones** (preparación, D10; sin RED/GREEN)     | `docs/specs/004-001-.../evidence/baseline.json`; `scripts/` (solo si se necesita un agregador determinista propio)                         | Consumes: 22 agentes actuales + `install.sh` + bloque estático del renderer → Produces: conteo líneas/bytes por rol×runtime×camino (clásico vs paquete), método/versión/config, suma **verificada mecánicamente** por un comando autorizado (incluye resolver en diseño el par `rtk wc`/agregador) | Criterios: PD-13; la suma del artefacto se recomputa con el método registrado; si un valor no se puede medir por política vigente, se declara VERIFY (no se sustituye por estimación — lección C0)                                                    |
| **T2 — Contrato de capacidades y fuentes canónicas**                     | `sources/roles/*.md`, `sources/agents/adapters/*.md`                                                                                       | Consumes: §2-§5 de este informe + ADR-011 → Produces: fuentes con tabla por rol (capacidades, invariantes con motivo, límites honestos), reglas bash justificadas por efecto, formato/delimitadores fijados                                                                                | Revisión focal (handoff legacy identificado); no autoaprobación                                                                                                                                                                                       |
| **T3 — Generador determinista + staging**                                | `scripts/cdad-generate.py`, `build/staging/`                                                                                               | Consumes: fuentes T2 + `cdad-models.sh` + parámetros explícitos → Produces: 22 agentes × 2 runtimes + `manifest.json` (hashes, fuentes, comando)                                                                                                                                               | RED: no-determinismo, fuente incompleta/duplicada, combinación no soportada, bloque §2 con modelos de otro runtime (PD-2/3/4). GREEN: la fuente única reproduce los consumidores declarados. Aterrizar aquí la sustitución de F001 (D7, mismo cambio) |
| **T4 — Simplificación de adaptadores OpenCode**                          | `scripts/cdad-bash-allowlist.sh` (estado final: reglas viviendo en la fuente y generadas), `install.sh` (inyección)                        | Consumes: T1 (fricción), T2 (contrato) → Produces: bloque bash simplificado con pares completos y reglas por efecto; corrección de intake R3 en la fuente                                                                                                                                  | Pruebas **positivas primero** (el architect mide/agrega sin rechazos; implementer ejecuta suite; reviewer ejecuta validador), luego negativas de frontera. El par `rtk wc` desaparece como bug dentro del rediseño                                          |
| **T5 — Instalación con propiedad (manifest)**                            | `install.sh`, `build/staging/manifest.json`, `~/.cdad/manifest.json` de cada raíz                                                            | Consumes: staging T3 → Produces: despliegue con D4 completo (PD-6/7/8/9), `--check` semántico contra staging                                                                                                                                                                                 | RED: primera instalación, modificado local, renombrado/obsoleto, ajeno conservado, symlink, fallo parcial, uninstall. GREEN: dry-run exacto; `--check` reporta drift instalado vs staging                                                               |
| **T6 — Coherencia Claude Code + productor instalado**                    | `scripts/claude-code-path-guard.sh` (simplificado, invariantes retenidas), `install.sh` (sección CC), fixtures `tests/test_role_packet_*.py` | Consumes: T3/T4/T5 → Produces: coherencia semántica CC vs contrato; fixtures migrados a destinos runtime reales (D6); smokes desde instalación sin checkout                                                                                                                                | RED/GREEN acotado por caso de frontera y de fixture migrado; matriz base/odoo × runtimes con datos sintéticos                                                                                                                                         |
| **T7 — Reemplazo de assertions de mecanismo (D7) + cierre de capacidad** | `tests/validate-consistency.sh` (F001/F009), `tests/validate-odoo-specialization.sh` (P1), `scripts/validate-subagents.sh`                   | Consumes: T3-T5 → Produces: asserts de garantía/capacidad en verde (PD-10/12), validadores PASS simultáneos, baseline contrastada                                                                                                                                                          | Mini-ciclo: cada assert sustituido tiene su reemplazo pasando en el mismo commit lógico; sin borrar y ya                                                                                                                                              |

Paralelizable: T4 puede avanzar en paralelo con T5 **solo** sobre el contrato T2 estable y archivos disjuntos; cambios concurrentes a `install.sh` o al state requieren protocolo (`plan.md:129-131`). Integrador único: el orquestador del epic.

Self-review del plan: cobertura de las 16 postcondiciones (T1→PD-13; T2→PD-1; T3→PD-2/3/4/15/16; T4→PD-1/11/12; T5→PD-5/6/7/8/9; T6→PD-9/14/15/16; T7→PD-10/12); sin TBD; firmas consistentes entre T3 y T5 (staging+manifest).

---

## 9. Dudas acotadas

1. **¿Quién firma la autoridad de ejecución de 004?** Propuesta: el usuario, en `docs/epics/epic-004-single-source-planning/execution.md` (source de la `hitl_delegation` de 004). Solo falta confirmar que no se exige otra aprobación adicional para la activación misma (el dictamen la condiciona a "dictamen conforme + aprobación estratégica registrada", `c0-review-gpt:205-207`).
2. **Esquema del registro de autoridad**: el actual `hitl_delegation` no tiene campo `epic_id` (el epic va dentro de `scope`, `state:390`). Propongo conservar el esquema actual (modo `ordinary` no lo valida, `cdad_packet.py:219-221`), sin extender el schema en 004-001. Confirmar.
3. **Layout público: ¿flag opt-in o eliminación directa?** Consumidores confirmados solo los fixtures (§0). Recomiendo eliminarlo del default y decidir el flag al migrar fixtures (T6): si tras migrar ningún consumidor lo justifica, no hay flag. Costo de eliminar: re-add posterior si aparece un consumidor real.
4. **Par `rtk wc` transitorio**: asumo (según el encargo) que NO se parchea antes de 004-001; la fricción `wc/du` persistirá en sesiones architect hasta que aterrice T3/T4. Confirmar que ese costo se acepta.
5. **Rutas de fuentes**: `sources/` + `scripts/cdad-generate.py` + `build/staging/` son propuesta; VERIFY si el orquestador prefiere otra ubicación antes de materializar la spec.
6. **Techo de 12.000 bytes**: mi recomendación es parametrizarlo y diagnosticar, no eliminar; si la revisión prefiere retirarlo como gate, el costo es perder la guardia de presupuesto de contexto del paquete. Decisión pendiente del reviewer focal.

---

