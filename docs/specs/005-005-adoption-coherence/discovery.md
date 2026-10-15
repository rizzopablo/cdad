# Discovery — 005-005-adoption-coherence (stage 1)

**Rol:** architect (read-only) · **Paquete:** `005-005-adoption-coherence-architect-discovery-001`
**Contrato:** `docs/epics/epic-005-real-operation/plan.md` (aprobado, sha256 `c8a5d08734ed070464259bb1d65b9ec390caa7fd5e6fd64c48f84efe814d2275`).
**Encargo de referencia:** `docs/epics/epic-005-real-operation/handoff-005-005.md` §3 (T1/T2/T3) y §4–§5.
**Método:** lectura directa del repo + grep acotado. Sin editar el repo (verificado: `git status --porcelain` sólo muestra `docs/.cdad-state.json`, modificado por el orquestador, ajeno a este rol). Todas las afirmaciones citan archivo:línea. Lo no comprobable por lectura queda marcado **VERIFY**.
**Alcance de esta subetapa:** mapear la superficie técnica; **no** proponer el contrato (eso es `draft`).

Estado del repo (contexto verificado): `docs/.cdad-state.json` → `active_epic: epic-005-real-operation`, `active_feature: 005-005-adoption-coherence`, `current_stage: discovery`, `epic_features` con 005-005 `in-progress` y 005-001 `done`; `active_packet` = este paquete (`prepared`). No existe `.cdad/activation.json` en el repo (`find` sin resultados; `.cdad/` y `.opencode/` están en `.gitignore`).

---

## T1 — Reemplazo con validación de lo conservado

### Entidades verificadas

- Sub-modo `--replace-packet`: `skills/cdad-cycle/scripts/cdad_packet.py` → `_replace_packet` (:1888-2070). Selector y `--reason` en el parser: :3343-3346; opciones de corrección en :3357-3362. Dispatch en `main`: :3517-3519. Exclusión de modos: `_reject_mode_mix` (:3445-3492) + `_REPLACE_CORRECTION_FLAGS` (:3431-3438).
- Validador de correcciones: `_validate_corrections` (:1843-1886). **Hoy sólo valida los campos presentes en el set `corrected`** (:1850, :1862, :1877): `inputs`, `read_scope`, `write_scope`.
- Construcción del encargo sucesor: conserva campo a campo (:1972-1983, universo `ASSIGNMENT_UNIVERSE` :1809-1812). El set `corrected` se arma sólo cuando la opción se da (:1986-2011): `_sentinel_list` (:1815-1830) + `_with_role_floor` (:1833-1840).
- Secuencia de validación del reemplazo: `_validate_corrections(new_request, corrected, …)` (:2022-2025) y luego **`validate_request(new_request, execution_document, new_state, project_root)`** (:2034). Esta segunda llamada corre TODAS las validaciones de un `prepare` normal.
- Publicación: `_publish_generation` (:2944-3150), compartida con `prepare`; registro `.superseded.json` con `conserved_fields`/`changed_fields` (:2039-2069). `_resume_packet` (:1735-1804) es el camino de obsolescencia (marcador `packet obsolete`).

### Qué valida hoy un `prepare` normal (`validate_request`, :723-828)

1. Coherencia de estado (`validate_state`, :725).
2. Esquema y campos del `REQUEST.json` (:726-733).
3. Identidad vs. ejecución (:735-736); par rol/subetapa (:738-739).
4. Contrato: campos cerrados (:740-746), reglas draft/aprobado (:747-781), `kind`/`path` vs. rol+ejecución (:782-787), `sha256` recomputado contra el archivo (:792-795), **aprobación por rol** `_contract_approval_for` (:800).
5. Listas (`inputs/read_scope/write_scope/invariants/evidence_required`) son listas (:803-805).
6. **`read_scope` y `write_scope`: `_validate_scope` sobre cada elemento** (:806-809) — esto corre para scopes **conservados o corregidos**, porque opera sobre `document`.
7. `inputs`: forma `{path,purpose}`, `_project_path` (resuelve, **no exige existencia**), y contención dentro de algún read_scope (:810-816).
8. `invariants` + `evidence_required`: strings no vacíos (:817-818).
9. `expected_output`: string no vacío (:731-733).

### Qué NO se valida hoy en el reemplazo (el hueco real de T1)

- **Existencia de los insumos conservados.** El único chequeo de existencia de inputs está en `_validate_corrections` (:1858 `candidate.is_file()`) y **sólo se aplica a `inputs` cuando están en `corrected`**. Un input conservado que apunta a un archivo inexistente no lo detecta nadie: `validate_request` sólo resuelve la ruta (`_project_path`, :814, `strict=False`) y comprueba contención de scope (:815). Confirmado por lectura: el único `is_file()` ligado a inputs es :1858.
- **Diagnóstico accionable para campos conservados inválidos.** Cuando un campo conservado viola la política, el error lo emite `validate_request` con un mensaje genérico que **no nombra el campo ni la opción de corrección**: p.ej. `_validate_scope` produce "scope selector is not classified as …" / "… cannot use … in write scope" (:666-703) y el input fuera de alcance produce "input is outside read scope: …" (:816). El formato campo/motivo/opción ("… correct it with `--read-scope` (PD-22)") sólo existe en `_validate_corrections` (:1854-1885).
- **Asimetría corregido vs. conservado:** un input corregido inexistente se rechaza (:1858) pero el mismo input, conservado, pasa. Nota: `validate_request` de un `prepare` normal **tampoco** exige existencia de inputs (:814), de modo que el reemplazo corregido es hoy más estricto que un `prepare` normal; conviene que la spec fije la semántica (exigir existencia en ambos, o ninguno).

### Puntos de extensión

- `_validate_corrections` (:1843) — quitar el gate `if "X" in corrected` para validar también los conservados, o invocarla con el universo completo. Reusar los textos campo/motivo/opción existentes.
- Construcción de `corrected` (:1986-2011) y call site (:2022-2025).
- Chequeo de existencia de inputs (:1858) — candidato a extraerse para aplicarlo a todo `inputs`.
- Mensajes genéricos de `validate_request` (:806-818) — si se quiere el diagnóstico accionable sin duplicar lógica.
- Los `--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence` ya están en el parser (:3357-3362) y en `_REPLACE_CORRECTION_FLAGS` (:3431-3438); `_reject_mode_mix` ya los admite sólo en replace (:3480-3486).

### Convenciones aplicables

- PD-22 de 005-001 (`docs/specs/005-001-idle-and-v7-bootstrap/spec.md:125`): "las correcciones pasan las MISMAS validaciones que un `prepare` normal" con diagnóstico campo/motivo/opción. Base citada por el encargo: `_validate_corrections`.
- INV-1/INV-3 (`spec.md:133-135`): el reemplazo no publica sin autorización vigente y no reescribe el paquete anterior; `_publish_generation` ya lo garantiza (:2034 antes de :2058).
- Marcadores estables `packet obsolete` / `approval pending` (`spec.md:71-73`; `_resume_packet` :1786-1798; `_replace_packet` :1927-1932).
- Registro de reemplazo PD-24 (`spec.md:129`): `conserved_fields`/`changed_fields` ya implementados.

### Riesgos / abiertos

- **VERIFY (ejecución):** no ejecuté el CLI; la afirmación "un input conservado inexistente hoy pasa" es por lectura de código. El draft debe pedir un test focal que lo fije.
- Test de regresión existente a extender: `tests/test_005_001_tcorr.py` (PD-19..PD-24, :509-983). El caso "input conservado inexistente" no está cubierto (los insumos de `custom_assignment()`, :295-307, apuntan a un archivo que existe).
- Cuidado con PD-20/D7: `--input -` (lista vacía) debe seguir siendo válido (`spec.md:121`); validar "todos los conservados" no debe rechazar una lista vacía legítima.

---

## T2 — Una sola política de tests

### Afirmaciones hoy existentes (archivo:línea)

**Procedimiento (`skills/cdad-cycle/references/stage-3-tdd.md`):**
- :31 "The full suite is for **gates, not for debugging**" + presupuesto de corridas (iteración con corridas mínimas, :29-39).
- :57 "Validate the green suite at re-entry".
- :123 "Run the **COMPLETE** suite once at the end (AP-3)" (en *Parallel dispatch*).
- :137 "COMPLETE suite when consolidating (AP-3)".
- :150 (Re-entry GREEN) "**Complete** suite green (not just the new test)".
- :153 "The full suite runs **once per GREEN**" + remisión a la equivalencia de `re-entry.md`.
- :169 (REFACTOR) "Suite green AT ALL TIMES".
- :217 (exit gate) "Suite green (verified empirically …)".

**Procedimiento (`skills/cdad-cycle/references/re-entry.md`):**
- :67-79 sección canónica **"Equivalence of a registered run"**: una corrida registrada puede **citarse** en controles consecutivos si se demuestra equivalencia (árbol/política/entorno); focal vs. transversal se tratan distinto (:77); sin equivalencia → nueva corrida (:75).
- :149-150 (Implementer GREEN) "the output of the **complete** suite, not just the new test" / "The whole suite is green".

**Paquetes canónicos (`skills/cdad-cycle/packets/`):**
- `substages/implementer-green.md:1` — "Run the focused test, then **the required full regression suite**".
- `substages/implementer-refactor.md:1` — "Keep the suite green throughout".
- `substages/implementer-review-fix.md:1` — "rerun the affected and regression suites".
- `substages/test-writer-audit.md:1` — "regression risks" (sin comando).
- `roles/implementer.md:1` — "run the required focused and regression suites".

**Índice (`skills/cdad-cycle/SKILL.md`):** :73 (refactorer "full suite"), :297/:299/:304 (gates "Full suite green"/"Suite green"), :347/:357, :528 "Output of the COMPLETE suite in green".

**Plan del epic (`docs/epics/epic-005-real-operation/plan.md`):** :60-61 — "el implementer corre focales y módulos tocados; suite completa al cierre de cada feature o si se toca instalador, staging o renderer".

**Estado de la brecha ya declarado:** `docs/runtime-adopted-version.md:126` (v8) lista como brecha a corregir en 005-005: "procedimiento y paquetes piden suite completa por GREEN".

### Contradicciones identificadas

1. **Frecuencia de la suite completa.** `stage-3-tdd.md:153` ("full suite runs once per GREEN") + `re-entry.md:149-150` ("complete suite" por GREEN) + `SKILL.md:528` **vs.** `stage-3-tdd.md:31` ("gates, not debugging") + `plan.md:60-61` ("focales y módulos tocados; suite completa al cierre"). Hoy el procedimiento exige la suite completa **por cada GREEN**, lo que choca con el presupuesto de corridas y con el gate del epic.
2. **Alcance del paquete canónico.** `implementer-green.md:1` dice "the **required full** regression suite" — "required" no está definido: ¿por GREEN o proporcional al cambio? No coincide con "focales y módulos tocados" (`plan.md:60-61`) ni con la regla de proporcionalidad/equivalencia.
3. **Reutilización de evidencia.** `re-entry.md:67-79` ya permite citar una corrida registrada equivalente; `stage-3-tdd.md:153` la menciona pero **conserva** "once per GREEN" como default. El paquete `implementer-green.md` no menciona la reutilización.
4. **Quién declara los comandos.** Ni el procedimiento ni los paquetes dicen que **el proyecto declara los comandos** (focales/suite); `implementer-green.md` habla de "the required full regression suite" sin fuente. El plan (`:61`) sí nombra el gate por feature.
5. **Condición del entorno como requisito.** `re-entry.md:73` ("la misma `commit` … no implica entorno equivalente") ya está alineado con "la condición local se registra en la evidencia, no se vuelve requisito"; el procedimiento (`stage-3-tdd.md:153`) lo remite pero no lo enuncia.

### Objetivo declarado (handoff §3 T2 / plan fila 2.b)

Regresión **proporcional al cambio**; **suite completa al cierre** de la feature; **reutilización de evidencia equivalente**; **la metodología define la evidencia, el proyecto declara los comandos**; una condición local se **registra** en la evidencia y **no** se vuelve requisito.

### PD-17 de 005-001 y el recorrido realmente ejecutado

- **PD-17 literal** (`docs/specs/005-001-idle-and-v7-bootstrap/spec.md:109-115`): escenario secuencial de 6 pasos donde el paso 4 **edita el plan del epic** y el paso 5 **reemplaza el paquete del architect** (`--resume-packet` → `packet obsolete` → `--replace-packet`).
- **Recorrido ejecutado** (`docs/specs/005-001-idle-and-v7-bootstrap/closure.md:51-57`): el paquete del architect se **recibe y completa** (`record-dispatch` → staging → `receive` → `validate-receipt` → transición) **antes** de preparar al test-writer; el reemplazo se prueba con un paquete **todavía `prepared` y no despachado** (P1). El ajuste fue instruido por el dueño (2026-10-09) y está registrado en `dispatch-ledger.md` fila 13 (:78) y en `debt.md` B2 (:9-18).
- **Deuda derivada:** `closure.md:114-115` ("El texto literal de PD-17 no coincide con el escenario ejecutado (B2)") y `debt.md:9-18` ("Queda sin test la semántica específica del architect … la vía es un bloque S5-arch … o una enmienda de PD-17"). `review.md` B2 (:20-25) es la misma observación desde la review.
- **Implicación para T2:** "enmendar PD-17 según el recorrido ejecutado" = reescribir PD-17 para que su letra coincida con lo que efectivamente se corrió (recepción/complete del paquete del architect antes de preparar al test-writer; reemplazo sobre un paquete `prepared`), o declarar explícitamente el objeto del reemplazo. No cambia el alcance del epic.

### Riesgos / abiertos

- La regla de equivalencia es de `re-entry.md` ("single canonical owner", :69); cualquier cambio debe editar el dueño canónico y **no** duplicar texto en `stage-3-tdd.md`/`SKILL.md`/`stage-4-review.md` (consumidores que la referencian).
- Alinear el gate del plan (`plan.md:60-61`) con la metodología y con los paquetes canónicos.
- **VERIFY:** inventario completo de menciones de "suite/regression" en `references/` (fuera de los archivos leídos) — el grep cubrió `packets/`, `stage-3-tdd.md`, `re-entry.md`, `stage-4-review.md`, `SKILL.md`; el draft debe barrer el resto (`continuity.md`, `progress-guards.md`, etc.) antes de fijar el texto único.

---

## T3 — Procedencia de la instalación

### Cómo resuelve hoy `prepare` el origen de los agentes de proyecto

- `_derived_source_dir()` (`cdad_packet.py:2454-2457`): `os.environ.get(DERIVED_AGENTS_ENV)` → si existe, esa ruta; **si no, `DEFAULT_DERIVED_SOURCE`** = `Path.home()/".config"/"opencode"/"agents"` (:88-89). Es decir: **variable de entorno o HOME global; no consulta ningún registro de activación.**
- `_load_derived_sources(base)` (:2460-2465): si `base` no es directorio → `None`; si no hay `cdad-*.md` → `None`.
- `_build_derived_payloads` (:2680-2716): escribe el manifiesto `.opencode/agents/.cdad-derived.json` con `source_dir` (:2710) + `source_sha256`/`derived_sha256` por agente (:2702-2705) + `policy_sha256` (:2708).
- **Sin activación / sin directorio fuente:** `_build_derived_payloads` devuelve `None` y `_publish_generation` imprime un aviso a stderr y continúa con rc 0, sin publicar derivados (:2976-2985). No hay diagnóstico que nombre el registro de activación ni la versión.
- **Confirmación por grep:** `grep -n "activation" cdad_packet.py` → **sin resultados**. `prepare` no lee `.cdad/activation.json` ni `docs/cdad-policy.json` para el origen de agentes (`docs/cdad-policy.json` es la política de rutas, no la activación).

### Registro de activación (fuente propuesta por T3)

- Formato: `.cdad/activation.json` = `{adopted_root, manifest_sha256, paths:{ruta→{kind,sha256|target}}}`. Emitido por `scripts/cdad-activate.py` (`REGISTRY_REL = ".cdad/activation.json"` :25; `build_registry` :294-313). Contrato: `references/runtime-adoption.md:37-39` ("Registro: `.cdad/activation.json` con `adopted_root`, el sha256 del manifest …").
- La raíz adoptada contiene los agentes en `<adopted_root>/.config/opencode/agents` (patrón usado en `handoff-opencode.md:32` y `dispatch-ledger.md:33`). Ejemplo real de registro: `/tmp/cdad-t5-sandbox-*/sandbox/.cdad/activation.json` (`adopted_root: <home>/.cache/cdad-adopted-ce09ed0`).
- **Este repo no tiene `.cdad/activation.json`** (`find` sin resultados; el estado del repo ya no tiene activación propia — coherente con `handoff-005-005.md:17-19`). El manifiesto actual apunta a HOME: `.opencode/agents/.cdad-derived.json` → `source_dir: <home>/.config/opencode/agents` (verificado por lectura del archivo local, git-ignorado).

### Qué falta para que la procedencia sea verificable

- El registro `adopted_root` **nombra la instalación** (versión), pero `prepare` no lo lee; hoy el default es HOME o una variable de entorno efímera. El encargo pide: registro por defecto cuando existe; camino explícito para proyectos sin activación o para elegir otra instalación legítima; **contradicción diagnosticada** (decir cuál usaría y cómo resolverla), nunca cambio de versión en silencio.
- **Versión en cada agente publicado:** ni el manifiesto ni los agentes derivados declaran una versión/commit. El manifiesto sólo lleva `source_dir` + hashes (:2706-2712); los agentes publicados no tienen campo de versión (`grep -i version .opencode/agents/*.md` → sólo comentarios). Por eso hoy **no es verificable qué versión cargó realmente una sesión** desde el artefacto publicado.
- **Evidencia de la brecha (caso real):** `dispatch-ledger.md:84-101` ("Hallazgo de gate — MIX-V6V7"): un `prepare` sin `CDAD_OPENCODE_AGENTS_DIR` re-derivó los 11 agentes desde `~/.config/opencode/agents` (otra versión) **sin avisar**; `:98-101` nombra `.cdad/activation.json` como el registro que el CLI **no** fuerza. Mismo hallazgo en `debt.md:44-53` y `runtime-adopted-version.md:126,137-138`.
- **Modelo de ejecución real** (`handoff-005-005.md:52-67`): el dueño usa una GUI con servidor OpenCode permanente; los comandos heredan el entorno del servidor, fijado al arrancarlo, por lo que la variable de entorno **no puede ser el mecanismo normal** (queda como opción explícita). "Nivel correcto": la regla es de la metodología; el registro nombra la instalación y **cada adaptador** sabe dónde lee su runtime los agentes/skills, cómo publicarlos y cómo recargarlos.

### Adaptador de OpenCode (`skills/cdad-cycle/references/opencode-delegation.md`)

- Documenta: instalación de `cdad-*` en `~/.config/opencode/agents/cdad-*.md` (:1-6); regla de decisión (:8-16); mapeo rol→`subagent_type` y modelos (:18-36); mecanismo de paso de estado (`render` → prompt de la Task, :38-49); `task` vs `delegate` y el lever `write: ask` (:51-95); fallback por rate-limit (:97-105); tabla Task vs. handoff (:107-119).
- **NO documenta** (lo pedido por T3, `handoff-005-005.md:56-58`): si una **sesión nueva relee agentes y skills** o si hace falta recargar el servidor (`opencode reload`), y **qué versión cargó** una sesión. El encargo aporta el hecho verificado (OpenCode 2.0.22, proceso nuevo: un agente de proyecto en `.opencode/agents/` reemplaza al global del mismo nombre) y deja `opencode reload` **sin comprobar**.
- Punto de extensión del adaptador: agregar una sección "recarga de sesiones/agentes/skills" y "procedencia verificable por sesión". El adaptador ya es el lugar donde vive la mecánica por runtime (paralelo a `claude-code-delegation.md`).

### Puntos de extensión

- `_derived_source_dir` (:2454) / `DEFAULT_DERIVED_SOURCE` (:89) / `DERIVED_AGENTS_ENV` (:88) — resolver el origen desde `.cdad/activation.json` cuando exista; diagnóstico de contradicción.
- `_build_derived_payloads` (:2680) y el manifiesto (:2706-2712) — agregar la versión/commit declarada por agente publicado.
- `_publish_generation` (:2976-2985) — el aviso actual no nombra el registro ni la versión.
- `references/opencode-delegation.md` — documentar recarga y procedencia.
- `references/runtime-adoption.md` — ya define el registro; alinear la regla metodológica de procedencia.

### Riesgos / abiertos

- **VERIFY (runtime):** si `opencode reload` basta para que un servidor ya iniciado tome agentes nuevos. El encargo lo declara **no comprobado** (`handoff-005-005.md:66-67`). El draft no debe afirmarlo.
- **VERIFY:** forma exacta en que `prepare` debería derivar `<adopted_root>/.config/opencode/agents` desde `activation.json` (el registro guarda `adopted_root`, no la ruta de agentes). Verificar que el layout `.config/opencode/agents` de la raíz adoptada es estable (usado en `handoff-opencode.md:32`, `dispatch-ledger.md:33`).
- Contradicción a diagnosticar: env (`CDAD_OPENCODE_AGENTS_DIR`) vs. registro vs. HOME. Caso de prueba: el MIX-V6V7 del ledger (:84-101).
- "Evaluar que la activación publique los agentes, en vez de esperar al primer `prepare`" (`handoff-005-005.md:64-66`) — decisión de diseño para el draft.

---

## Documentación de 005-001

### `review.md` — qué normalizar (`docs/specs/005-001-idle-and-v7-bootstrap/review.md`)

El archivo tiene texto **corrupto/ininteligible** (probable glitch de generación) que rompe la coherencia aunque el contenido técnico (veredicto, bloqueantes, opcionales, tabla PD↔test) es correcto. Líneas con texto dañado (muestra): :8 ("de cosmic importancia documental … aside del componente runtime/escoja … Es la gross momiestra"), :12 (título "Falta la simulación de la sub-modalidad" en vez de la sección «Reemplazo»), :15 ("El techo deContinue operativov … superficie delces … nodiscover … teológica axis"), :16 ("ted obsolescencia PD-8 … corrección PD-27·exactly exacto … pisos oblig tardays"), :22-23, :29-31, :35-36 ("抓 el caso"), :44 ("Barată reparación"), :49, :55, :65, :68, :76-77 ("No corrobore c63 … electrical composition").

Anomalías concretas a corregir:
- **Referencia errónea:** :16 menciona "PD-27", que **no existe** (PD-1..PD-24 en `spec.md`); debe apuntar a PD-20 (opciones de corrección).
- **Ortografía/términos:** múltiples neologismos y palabras ajenas al español ("momiestra", "techo", "escoja", "axis", "tardays", "asereción", "Barată").
- **Tarea:** normalizar coherencia y referencias **sin repetir la revisión** (no re-evaluar; no cambiar veredicto, bloqueantes ni buckets). Verificar también la tabla PD↔test (:59-66) y la sección de abstenciones (:74-78) contra `spec.md`/tests. No contiene rutas personales (`grep` → sin resultados).

### Rutas personales en `docs/epics/epic-005-real-operation/` (a sacar del repo; originales al registro local)

`grep -rn -E "/home/|/Users/|~/\.|\$HOME|ofap|/tmp/|\.cache/cdad|\.config/opencode"`:

- `handoff-opencode-2.md:8` — `<repo>` (ruta absoluta del repo).
- `handoff-opencode-2.md:14` — `$HOME/.cache/cdad-adopted-ce09ed0/.config/opencode/agents` (raíz adoptada de la instalación).
- `handoff-opencode.md:32` — `CDAD_OPENCODE_AGENTS_DIR="$HOME/.cache/cdad-adopted-ce09ed0/.config/opencode/agents"`.
- `handoff-opencode.md:63` — `~/.claude`, `~/.agents`, `~/.config/opencode` (enunciado de límite).
- `execution.md:21` — `~/.claude`, `~/.agents`, `~/.config/opencode` (reservado al dueño).
- `plan.md`, `handoff-005-005.md`: **sin** rutas personales (verificado).

**Criterio a fijar en el draft:** distinguir la ruta personal/instalación-específica (p.ej. `<home>/...`, `$HOME/.cache/cdad-adopted-ce09ed0`, nombres de usuario) — que va al registro local `.cdad/local/` (`handoff-005-005.md:3-5` ya usa ese patrón) — de la ruta **genérica de política** (`~/.claude`, `~/.config/opencode` como HOME reservado al dueño), que puede permanecer por ser regla de la metodología. **VERIFY** con el dueño dónde está el registro local y si `~/.claude` cuenta como "ruta personal" a retirar.

### Otros elementos documentales 005-001 detectados

- `closure.md:110-112` y `debt.md:44-53` documentan la observación "agentes derivados de una fuente no-v7" (candidato de mejora de producto, hoy T3).
- `debt.md:9-18` (B2) y `closure.md:114-115` son la fuente para la enmienda de PD-17 (T2).

---

## Convenciones aplicables (transversales)

- **ADR-003:** el architect entrega TEXTO FINAL; el orquestador/usuario materializa (`docs/.../{spec,plan}.md`). Este reporte no se materializa como spec.
- **PD-22 de 005-001** (`spec.md:125`): mismo conjunto de validaciones para `prepare` y `--replace-packet`.
- **Regla de equivalencia** (`re-entry.md:67-79`): dueño canónico único; consumidores referencian.
- **Registro de activación** (`references/runtime-adoption.md:37-39`, `scripts/cdad-activate.py:294-313`).
- **Regla de versión** (`runtime-adopted-version.md:104-112`): la versión adoptada no cambia durante tareas activas; activar/re-sincronizar es del dueño.
- **Sin push, sin `--no-verify`, no leer `tests/.sensitive-patterns.local`** (`handoff-005-005.md:85-90`).

---

## Riesgos y elementos abiertos (consolidado)

1. **T1 — VERIFY de ejecución:** "input conservado inexistente hoy pasa" es conclusión por lectura; falta test focal que lo fije. Además, fijar si el reemplazo debe exigir existencia de inputs en ambos modos (hoy corregido sí, conservado no, `prepare` normal no) — decisión que la spec debe resolver sin contradecir PD-22.
2. **T2 — VERIFY:** barrido completo de "suite/regression" en `references/` restantes antes de declarar la política única; evitar duplicar la regla de equivalencia (dueño canónico `re-entry.md`).
3. **T3 — VERIFY (runtime):** comportamiento de `opencode reload` sobre un servidor ya iniciado (declarado no comprobado en el encargo). No afirmarlo en la spec.
4. **T3 — VERIFY:** layout y derivación de `<adopted_root>/.config/opencode/agents` desde `activation.json`; y dónde vive el registro local del proyecto (para el criterio de rutas personales).
5. **Documentación — VERIFY:** criterio exacto de "ruta personal" (¿`~/.claude`/`~/.config/opencode` cuentan?) y ubicación del registro local que conserva los originales.
6. **Cierre (plan fila 2):** el test de integración es "instalación aislada que prepare, corrija con `--replace-packet` y despache con validación proporcional, sin rodeos manuales". El draft debe convertir esto en postcondiciones verificables, sin prometer despliegue en HOME (reservado al dueño, `plan.md:66-70`).

---

## Evidencia (comandos exactos)

- `read` de: `PACKET.md`, `plan.md`, `execution.md`, `handoff-005-005.md`, `handoff-opencode.md`, `handoff-opencode-2.md`, `spec.md` (005-001), `closure.md`, `debt.md`, `review.md`, `dispatch-ledger.md`, `runtime-adopted-version.md`, `skills/cdad-cycle/scripts/cdad_packet.py` (secciones :151-210, :662-828, :940-1009, :1708-2079, :2440-2739, :2944-3323, :3376-3590), `references/stage-3-tdd.md`, `references/re-entry.md`, `references/opencode-delegation.md`, `references/runtime-adoption.md`, `packets/*` (roles y substages), `SKILL.md` (grep), `tests/test_005_001_tcorr.py`.
- `grep -n "replace.packet|_validate_corrections|def _|source_dir|CDAD_OPENCODE_AGENTS_DIR|activation|..." skills/cdad-cycle/scripts/cdad_packet.py`.
- `grep -n "is_file()" skills/cdad-cycle/scripts/cdad_packet.py` → único chequeo de inputs en :1858.
- `grep -rn -i "suite|regres|focal" skills/cdad-cycle/packets/ skills/cdad-cycle/references/*.md skills/cdad-cycle/SKILL.md`.
- `grep -rn -E "/home/|/Users/|~/\.|\$HOME|ofap|/tmp/|\.cache/cdad|\.config/opencode" docs/epics/epic-005-real-operation/`.
- `grep -n "activation" skills/cdad-cycle/scripts/cdad_packet.py` → sin resultados.
- `find . -name "activation.json"` → sin resultados en el repo; ejemplos en `/tmp/cdad-t5-sandbox-*` y `/tmp/pytest-of-ofap/...`.
- `python3 -c "json.load('.opencode/agents/.cdad-derived.json')"` → `source_dir: <home>/.config/opencode/agents`.
- `python3 -c "json.load('docs/.cdad-state.json')"` → estado actual (activo epic-005 / 005-005 discovery).
- `git status --porcelain` → sólo `docs/.cdad-state.json` (ajeno a este rol; **no edité el repo**). `git rev-parse --short HEAD` → `f148304`.

**Sin modificaciones de producto ni del repo por este rol.** Reporte de discovery; el contrato se propone en la subetapa `draft`.
