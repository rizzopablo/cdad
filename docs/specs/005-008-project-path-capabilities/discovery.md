# Discovery — 005-008-project-path-capabilities (etapa 1, mapeo técnico)

**Rol:** architect (subetapa discovery) · **Read-only** · **No propone contrato** (eso es draft).
**Contrato:** `docs/epics/epic-005-real-operation/plan.md` sha256 `f3b66be0…` (fila orden 4, líneas 37 y 44-65).
**Insumos:** `plan.md`; `priority-perl-cli-plan-2026-10-10.md` §3 (criterios a convertir en postcondiciones);
`findings/external-orchestration-readiness-2026-10-10.md` (§A y «Hechos comprobados»).
**Raíz real del repo:** `<repo-root>` (el directorio del packete es un
superproyecto con gitlink; el repo CDAD es el subdirectorio `cdad/`).
**Archivos del repo modificados por esta tarea: ninguno.** (El único archivo de transporte es
`/tmp/opencode/discovery-005-008.md` y la sonda `/tmp/opencode/discovery-005-008-probe.py`.)

---

## 1. Entidades verificadas (archivo:línea)

### 1.1 Clasificador

- `skills/cdad-cycle/scripts/cdad_packet.py:222-248` — `classify_path` (clase mecánica).
  Orden de precedencia exacto:
  1. `exact("test_files") or beneath("test_roots")` → `"tests"` (línea 240-241)
  2. `beneath("colocated_test_roots") and is_test_name` → `"colocated-tests"` (242-243)
  3. `exact("implementation_files") or beneath("implementation_roots")` → `"implementation"` (244-245)
  4. `exact("documentation_files") or beneath("documentation_roots")` → `"docs"` (246-247)
  5. `None` (248)
  → **tests vence a implementation** cuando una raíz de tests está anidada en una de implementación.
- `cdad_packet.py:286-306` — `classify_path_observable` (vocabulario observable).
  Precedencia: **policy** (297-298) > **private** (`_is_private_path`, 300-301) > **temporary**
  (302-304) > clasificación mecánica por `CLASS_BY_TOKEN` (305-306) o `"unclassified"`.
  → privado siempre gana a cualquier clase de producto; el clasificador y los mapas comparten
  la decisión (`_private_path_entries`, 251-260).
- `cdad_packet.py:131-136` — `CLASS_BY_TOKEN` (tests→test, colocated-tests→colocated-test,
  implementation→implementation, docs→documentation).
- `cdad_packet.py:112-128` — vocabulario de política: `PATH_POLICY_LISTS` (raíces + convención
  co-ubicada), `PATH_POLICY_OPTIONAL_LISTS` (`implementation_files`, `documentation_files`,
  `test_files`), `PATH_POLICY_PRIVATE` = `private_paths`, `POLICY_KEYS` = `{schema_version,
  path_policy, temporary_roots}`.
- `cdad_packet.py:368-372` + `339-350` — conflictos: **solo** doc×impl y doc×tests se rechazan;
  **tests anidados dentro de implementación son válidos** (no hay rechazo tests×impl). El layout
  Perl (`test_roots` bajo `implementation_roots`) es una política legal hoy.
- `cdad_packet.py:415-426` — `_validate_policy_document`: el esquema es **exactamente** los tres
  campos; **un campo extra (p. ej. comandos) invalida la política** (`rc≠0`). Confirmado además por
  `tests/test_004_002_t1_policy.py:152-176` (`models`/`authority`/`bash_policy` → inválida).

### 1.2 Patrones de derivación y EL DEFECTO

- `cdad_packet.py:2581-2584` — `_implementation_patterns`: `implementation_roots/**` +
  `implementation_files` (literales). Para el caso Perl: `["webmin-module/module/**"]`.
- `cdad_packet.py:2587-2594` — `_test_patterns`: **solo** `test_roots/**`
  (`patterns.append(f"{root}/**")`). **No incluye `test_files`** (hallazgo focal, ver §2.4).
  Comentario B3 (2590-2592): nunca `**/<root>/**` — un `tests/` literal bajo una raíz de
  implementación se clasifica implementación y **no debe amplificarse**.
- `cdad_packet.py:2597-2605` — `_colocated_test_patterns`: por prefijo/sufijo bajo
  `colocated_test_roots`.
- `cdad_packet.py:2608-2672` — **`_derived_maps`** (mapas findLast por rol). Rama defectuosa:
  - `test-writer` (2641-2651):
    - `read` (2643-2645) = `[(impl,"deny")] + [(colocated,"allow")] + private`
      → **NO hay allow de `_test_patterns` en `read`**.
    - `edit` (2646-2650) = `* deny + test_patterns allow + colocated allow + policy/derived deny + private`
      → **sí tiene el allow de `_test_patterns`**.
  - `implementer` (2652-2661): `edit` = `* allow + test/colocated deny + policy/derived deny + private`;
    `read` solo lleva `private` (si existe) → sin entrada = allow por defecto.
  - `orchestrator` (2662-2668): `edit` = `* allow + policy/derived deny + private`; `read` solo private.
  - lectores (2669-2672): `edit` = `* deny` (+ private); `read` = private si existe.
  - `private` (2636-2640) se emite **al final** de `read` y `edit` → el deny privado gana por findLast
    (por eso «una excepción de tests nunca reabre una ruta privada» depende de mantener ese orden).
- **Asimetría exacta del defecto:** `read` deniega `webmin-module/module/**` y no reabre con allow
  el subárbol `webmin-module/module/t/**`, mientras `edit` sí lo permite. Resultado: el test-writer
  puede **editar** sus tests pero **no leerlos**.
- Semántica findLast documentada en `cdad_packet.py:2618-2623` (W-2): OpenCode evalúa `grep`/`glob`
  contra el **patrón de búsqueda**, no la ruta → los derivados **no** emiten entradas por ruta en
  `grep`/`glob`; la barrera viva por ruta es `read` (y `edit`).

### 1.3 Guard de Claude Code (paridad) — no tiene el defecto

- `scripts/claude-code-path-guard.sh:211-217` (rama `test-writer:read`): bloquea **solo** si
  `CLASS == "implementation"`. Como `classify_path` da `test` a los tests anidados, el guard **ya
  permite leer `webmin-module/module/t/*.t`**. El defecto es **exclusivo del mapa OpenCode**;
  la corrección debe alinear OpenCode con el clasificador y con el guard CC.
- `claude-code-path-guard.sh:183-189` — `private` bloquea a todo rol/herramienta; `:176-181` —
  policy/derivados en edit bloqueados.
- `claude-code-path-guard.sh:39-43` (docstring v2) — el guard clasifica con
  `cdad_packet.py validate-policy --classify` (clasificador único).

### 1.4 Publicación de derivados y manifiesto

- `cdad_packet.py:86-92` — `DERIVED_RELPATH = .opencode/agents`, `DERIVED_MANIFEST_NAME =
  .cdad-derived.json`.
- `cdad_packet.py:2440-2451` — `_derived_role` (architect/reviewer/scribe → `reader`;
  test-writer/implementer/orchestrator → sí mismos; sufijo `-odoo` tolerado).
- `cdad_packet.py:2477-2490` — `_derived_source_dir` (orden `CDAD_OPENCODE_AGENTS_DIR` >
  registro `.cdad/activation.json` > default global).
- `cdad_packet.py:2675-2736` — `_rewrite_derived_agent` reemplaza **solo** `read/grep/glob/edit`
  en el frontmatter del origen; el resto byte a byte.
- `cdad_packet.py:2789-2836` — `_build_derived_payloads`: `path_policy` ← `execution_document`;
  manifiesto = `{schema_version, policy_sha256, source_dir, source_version, agents{name:{source_sha256,
  derived_sha256}}}` (2823-2834).
- `cdad_packet.py:3089-3102` y `3151-3161` — `_publish_generation` (dentro de `prepare`) escribe
  los derivados en staging y los aplica atómicamente. **No hay publicación de derivados en
  `install.sh`** (verificado: `install.sh` instala agentes globales + `version.txt`, no `.opencode/`).
- Manifiesto real del repo: `.opencode/agents/.cdad-derived.json` (declara 10 derivados +
  `source_version`); **`.opencode/` está gitignoreado** (`.gitignore`), portabilidad ok para este repo.
- `docs/systemPatterns.md:259-266` (resolución de origen / manifiesto) y `project-start.md:164-191`
  (`cdad-version-check.py` lee `source_version` del manifiesto).

### 1.5 Comandos de validación (lugar canónico)

- `Makefile` (raíz del repo): targets `staging`, `agents`, `validate` (líneas ~13-24).
  `validate` corre `tests/validate-consistency.sh` y `tests/validate-odoo-specialization.sh`.
  **No hay target `test`** ni registro Perl.
- Referencia metodológica del lugar de comandos:
  - `skills/cdad-cycle/references/stage-3-tdd.md:56-59` — «la metodología define la evidencia; el
    proyecto declara los comandos» (p. ej. **Makefile o systemPatterns**).
  - `skills/cdad-cycle/references/stage-5-merge.md:28` — misma regla (suite al cierre).
  - `skills/cdad-cycle/references/project-start.md:57` — fila «entorno de pruebas» → `test_roots`
    de la política + **los comandos que declara el proyecto**.
  - `docs/systemPatterns.md:239-250` — dueño canónico único: `stage-3-tdd.md` §«Test evidence policy».
- **`docs/cdad-policy.json` NO puede ser el registro de comandos**: su esquema rechaza campos extra
  (`cdad_packet.py:417-420`; `tests/test_004_002_t1_policy.py:152-176`).
- **No existe hoy ningún registro de comandos/regresión para sintaxis y tests Perl** en el repo
  (grep de `perl`/`prove`/`.t` en `Makefile`, `tests/`, `docs/`: sin resultados de registro).

### 1.6 Especialización de dominio existente (precedente)

- `scripts/cdad-generate.py:84-91` — `DOMAIN_SKILLS` por stack: `odoo` → architect=`odoo-architect`,
  test-writer=`odoo-test-writer`, implementer=`odoo-expert`+`odoo-make-env`, reviewer=`odoo-reviewer`,
  scribe=`odoo-make-env`. `--stack auto|odoo` (línea 7). Delta de dominio en el agente generado
  (`:657-669`, `:711-712`).
- Skills de dominio existentes: `skills/odoo-architect`, `odoo-expert`, `odoo-make-env`,
  `odoo-reviewer`, `odoo-test-writer` (+ validador `tests/validate-odoo-specialization.sh`).
- **`instruction_sources` del paquete es fijo**: `cdad_packet.py:842-847` compone `packets/common.md`,
  `packets/roles/<rol>.md`, `packets/substages/<rol>-<subetapa>.md`, y `:880-883` los publica en el
  metadato. **No hay inyección de fuentes de dominio por encargo** en el paquete; el dominio llega
  por el **agente** (delta por stack) o por los `inputs`/objetivo del contrato.

### 1.7 Qué de 005-006 ya resuelve el arranque (no duplicar)

- `skills/cdad-cycle/references/project-start.md:1-191` (entregado por 005-006): reconoce la raíz sin
  imponer layout, clasifica nuevo/parcial/incompleta, preserva lo existente, registra cada restricción
  en su lugar canónico (tabla §4) e **encadena hasta el primer encargo**.
- `docs/specs/005-006-guided-project-start/closure.md` (cerrada 2026-10-10; R2 de aceptación real
  queda pendiente del dueño). No repetir: el arranque guiado y su validación ya viven ahí.

### 1.8 Límites honestos (no sandbox / no allowlists por comando)

- `scripts/cdad-generate.py:223-234, 243-249, 301-329` — decisión del dueño 2026-09-29 (revierte
  002-009): política bash **permisiva**, una única catch-all `rule "*"`; barreras **por ruta**
  (mapas + guard CC) y de contrato. Comentario explícito `:327-328` «declared, NOT a sandbox — bash
  can read/write anything».
- `cdad_packet.py:2618-2623` (W-2) — `grep`/`glob` inertes por ruta; no declarar una barrera que no
  existe.
- `findings/…-2026-10-10.md:131-133` — «las lecturas por shell/grep tampoco quedan aisladas por una
  regla de `read`. No se promete sandbox».
- `agents` (paquete architect): «Honest limitations (PD-15)» — grep/shell/sesión separada no son
  sandbox; allowlists por comando no son read-only.

---

## 2. Recorrido del defecto, paso a paso (reproducido)

Política Perl/Webmin: `implementation_roots: ["webmin-module/module"]`,
`test_roots: ["webmin-module/module/t"]`.

1. **Clasificación (correcta).** `classify_path` devuelve:
   `webmin-module/module/main.pl`→`implementation`; `.../index.cgi`→`implementation`;
   `.../t/basic.t`→**`tests`**; `.../t/helper.pl`→**`tests`**. (Por precedencia tests>impl, línea 240
   antes de 244.)
2. **Mapa read del test-writer (defectuoso).** `_derived_maps("test-writer", policy)["read"]`
   = `[("webmin-module/module/**","deny")]`. Sin allow de `test_roots` ni de `test_files`, **ni**
   de `colocated` (vacuos).
3. **Mapa edit del test-writer (correcto).** `[("*","deny"),("webmin-module/module/t/**","allow"),
   ("docs/cdad-policy.json","deny"),(".opencode/agents/**","deny")]`.
4. **Veredictos findLast (oráculo pd10):**
   | tool | `.../t/basic.t` | `.../t/helper.pl` | `.../main.pl` |
   |---|---|---|---|
   | **read (test-writer)** | **deny** ← defecto | **deny** ← defecto | deny (correcto) |
   | **edit (test-writer)** | allow (correcto) | allow (correcto) | deny (correcto) |
   | read implementer | allow | allow | allow |
   | edit implementer | deny | deny | allow |
   → **Permite editar los tests mientras impide leerlos.** Exactamente el defecto del plan §3/§1.2.
5. **Punto exacto de emisión del deny sin allow:** `cdad_packet.py:2643-2645` (la lista `read` del
   rol `test-writer` concatena denies de implementación + allows solo de co-ubicados + private; falta
   el allow de `_test_patterns`). El allow equivalente ya existe, correctamente, en `edit`
   (`:2647`).
6. **Por qué no lo detectan los tests actuales:** ningún layout de fixture anida una raíz de tests
   bajo una raíz de implementación en los mapas derivados:
   - CDAD: `test_roots:["tests"]`, `implementation_roots:[agents,skills,scripts,sources,build]`
     (disjuntas);
   - conventional: `["tests"]` vs `["src","lib"]` (disjuntas);
   - odoo: `["addons/m/tests"]` vs `["addons/m/models","addons/m/views"]` (hermanas);
   - colocado: campo aparte.
   La **clasificación** de tests anidados sí está cubierta
   (`tests/test_004_002_t1_policy.py:418-427`, `test_pd2_tests_inside_implementation_are_extracted`),
   pero **no** los mapas derivados.

### 2.4 Caso focal exigido: `test_files` bajo implementación

Con `test_roots: []` y `test_files: ["webmin-module/module/t/standalone.t"]`:
- `classify_path(...t/standalone.t)` → **`tests`** (correcto, por `exact("test_files")`).
- `_test_patterns(policy2)` → **`[]`** (ignora `test_files`).
- `test-writer read` = `[("webmin-module/module/**","deny")]`; `edit` = `[("*","deny"), policy deny,
  derived deny]` → **ejecutar/editar/leer** el test declarado por `test_files` queda **denegado**.
→ Clasificación y permisos derivados **discuerdan** para `test_files` (criterio §3.2 del plan,
«incluir un caso focal de `test_files` bajo implementación: no corregir solo el ejemplo `.t`»).
Cualquier corrección que solo agregue `test_roots/**` al `read` **no** cubre este caso.

---

## 3. Puntos de extensión

1. **`_derived_maps` (lectura `test-writer`)** — `cdad_packet.py:2641-2651`: agregar el allow del
   árbol de tests declarado (`test_roots/**` y, de corresponder, `test_files`) **después** del deny de
   implementación y **antes** de `private`, para conservar findLast (tests reabren tests; privado
   gana). Espacio de decisión (draft): extender `_test_patterns` para incluir `test_files` (afecta
   también el `edit` del implementer y del test-writer) o un helper nuevo solo-read. Cuidado B3:
   nunca `**/tests/**`/`**/*.t`.
2. **`_test_patterns` / `_implementation_patterns`** — `cdad_packet.py:2581-2594`: superficie natural
   para el caso focal `test_files` (hoy ignorado en los patrones, aun cuando el clasificador lo usa
   por `exact`).
3. **Fixtures/clasificación** — no requieren cambio (la clasificación ya es correcta); la extensión
   necesaria es en los **mapas derivados** (§1.2) y sus tests (§4).
4. **Guard CC** — `claude-code-path-guard.sh:211-217`: ya correcto; referencia de paridad, no hay que
   tocarlo.
5. **Comandos del proyecto** — `Makefile` (targets propios del consumidor) + `systemPatterns.md`; **no**
   `docs/cdad-policy.json`. El consumidor debería declarar `make syntax`/`make test` (o equivalentes);
   el fixture puede verificar la declaración sin implementar el producto (plan §3/T3).
6. **Dominio** — reusar el mecanismo `DOMAIN_SKILLS`/stack del generador (`cdad-generate.py:84-91`)
   **solo si** discovery del consumidor lo justifica; **no** crear agentes Perl manuales. El paquete no
   inyecta fuentes de dominio hoy (VERIFY §7.5).

---

## 4. Tests y fixtures a reutilizar (origen 004-002 y posteriores)

- **Oráculo findLast (reutilizar por import, no reimplementar):**
  `tests/pd10_permission_semantics.py:66-110` (`perm_map`, `verdict`) y
  `tests/test_opencode_read_map_and_steps.py:88-133` (`frontmatter`, `nested_block`, `RULE_RE`,
  `read_map`, `glob_to_regex`, `evaluate`).
- **Fixtures de proyecto sintético:** `tests/test_004_002_t5_runtime.py:299-337` (`LayoutProject`),
  `:148-155` (`LAYOUT_FILES`), `policy_doc`; y `tests/test_004_002_t2_bootstrap.py:45-236`
  (`SCRIPT`, `FEATURE_ID`, `POLICY_FILE`, `prepare_args`, `state_document`, `write_state`,
  `build_project`, `make_project`). Exportadores: `AGENTS_ENV=CDAD_OPENCODE_AGENTS_DIR`,
  `CLI_ENV=CDAD_PACKET_CLI` (`t5_runtime:99-100`).
- **Publicación/manifiesto:** `tests/test_004_002_t5_runtime.py`
  `TestPd8I9Publication` (`:343-442`: publicación, manifiesto con hashes, archivo ajeno, byte-parity),
  `TestPd7I9DerivedMaps` (`:448-571`), `TestPd8I9DerivedLifecycle` (`:577-…`).
- **Rutas privadas:** `tests/test_004_002_t7_private_paths.py` (P-1; (a)-(i)) — fija la precedencia
  privada sobre cualquier allow y la cobertura de subárbol.
- **No amplificar tests:** `tests/test_004_002_t5_reviewfix.py:371-404`
  (`test_reviewfix_b3_nested_tests_dir_not_amplified`) — el guard de regresión más importante: con
  `src/tests/x.py` (implementation) el test-writer debe denegar read+edit.
- **Sin entradas por ruta en grep/glob:** `tests/test_004_002_t7_w2.py` + helper
  `assert_no_search_path_entries` (`t5_runtime:259-277`) → la corrección en `read` no debe introducir
  entradas por ruta en `grep`/`glob`.
- **Política/esquema/clasificación:** `tests/test_004_002_t1_policy.py` (PD-1/PD-2/PD-9, incluida la
  clasificación de tests anidados).
- **Generador base (no derivados):** `tests/test_opencode_read_map_and_steps.py::TestP1ReadMap`
  (mapa `read` del test-writer generado: deny-list, sin `*`; `src/pkg/test_a.py` colocado allow).

Baseline verificado (comandos en §8): `test_004_002_t1_policy.py`,
`test_004_002_t5_reviewfix.py`, `TestPd7I9DerivedMaps`, `test_opencode_read_map_and_steps.py`,
`test_004_002_t7_private_paths.py`, `test_004_002_t7_w2.py` → **60 passed** en el árbol actual.
El defecto **no** está cubierto hoy.

---

## 5. Manifiesto derivado y publicación: qué cambia y qué no

- **Cambia (derivado):** el mapa `read` del derivado `test-writer` → `derived_sha256` de
  `cdad-test-writer.md` (y `-odoo` si aplica) en `.opencode/agents/.cdad-derived.json`. Nada más por
  el fix de mapas.
- **No cambia:** el **esquema** del manifiesto (`schema_version`, `policy_sha256`, `source_dir`,
  `source_version`, `agents{source_sha256, derived_sha256}`), el mecanismo de publicación atómica
  dentro de `prepare` (`_publish_generation`), la detección de modificación manual
  (`_reject_hand_modified_derived`), el retiro de huérfanos (`_retired_derived_names`), ni la
  resolución del origen. `install.sh` **no** publica derivados.
- Nota de portabilidad: `.opencode/` es local (gitignoreado en este repo). El consumidor debe excluir
  derivados/metadatos (findings `Hechos comprobados` #4: hoy no lo hace) — ítem de configuración, no
  del fix de mapa.

---

## 6. Riesgos

- **R1 (alto) — sobre-amplificación:** «arreglar» con `**/tests/**` o `**/*.t` rompería B3
  (`test_reviewfix_b3_nested_tests_dir_not_amplified`) y el invariante PD-7 (nunca ampliar la
  política). La corrección debe usar **los árboles declarados** (`_test_patterns`/`test_files`), no
  convenciones globales Perl.
- **R2 (alto) — reabrir una ruta privada:** si el allow de tests se emite **después** de `private`, se
  anula la barrera privada (la política del propio repo tiene `tests/.sensitive-patterns.local`
  dentro de `tests/`). El allow de tests debe ir **antes** de `private` (findLast).
- **R3 (medio) — caso focal `test_files` omitido:** corregir solo `.t`/`test_roots` deja el caso
  `test_files` bajo implementación inconsistente (clasificado test, mapa denegado).
- **R4 (medio) — `grep`/`glob`:** no agregar entradas por ruta nueva; el mapa `read` es el canal vivo.
- **R5 (medio) — mediación real:** la sonda prueba mapas generados, **no** la mediación de un proceso
  OpenCode real (findings #3). El criterio §3.5 exige operaciones reales del runtime; el discovery NO
  puede darlo por hecho.
- **R6 (bajo) — comandos Perl ausentes:** declarar comandos no autoriza instalar intérprete/runner/
  dependencias en máquinas productivas; la ausencia debe producir diagnóstico útil.
- **R7 (bajo) — no duplicar 005-006** (arranque) ni crear agentes/sistema de políticas paralelos.

---

## 7. VERIFY abiertos (hechos no verificables con la evidencia disponible)

1. **Layout/política reales del consumidor Perl/Webmin.** No está en este repo (fuera de la frontera
   de lectura) y el consumidor **carece hoy de `docs/cdad-policy.json`** (findings #4). VERIFY:
   `implementation_roots`, `test_roots`/`test_files` exactos, y si hay auxiliares de test fuera de
   `t/` (p. ej. un módulo `.pm` compartido) que deban declararse. El ejemplo del plan
   (`webmin-module/module/` + `.../t/`) es **caso de uso**, no política confirmada.
2. **Alcance del fix en `_test_patterns`.** Decidir si se extiende para incluir `test_files`
   (afecta el edit del implementer y del test-writer) o se agrega un helper solo-read. VERIFY: no
   regresión en B3, W-2 y en `test_004_002_t7_private_paths` (F-P1).
3. **Mediación real del runtime.** Cómo demostrar capacidades positivas/negativas «mediante
   operaciones reales del runtime» (findings #3; criterio §3.5) sin presentar grep/shell/sesión
   separada como sandbox. VERIFY: disponibilidad del producto instalado y del CLI
   (`findings #7`: el ejecutable no estaba en PATH en la sesión de análisis).
4. **Precedencia findLast en vivo** con `private` anidada en un allow de tests (¿OpenCode aplica la
   última regla matcheante como el oráculo pd10? El oráculo es el modelo declarado; la sonda en vivo
   de W-2 es el precedente).
5. **Entrega de convenciones/referencias de dominio** al consumidor no-odoo: el paquete **no** inyecta
   fuentes de dominio (`cdad_packet.py:842-883`); el dominio llega por el agente por stack o por
   `inputs`/objetivo. VERIFY si alcanza con el objetivo+inputs del encargo o si se justifica un stack/
   skill de dominio (sin crear agentes manuales ni otro sistema de políticas).
6. **Registro de comandos Perl del consumidor:** dónde declara `make`/`systemPatterns` y si el
   proyecto del consumidor admite esa convención sin imponer layout. VERIFY tras habilitar el
   contrato del consumidor.
7. **Cobertura Git del consumidor** para derivados/metadatos locales (findings #4) — fuera del fix de
   mapa, pero relevante para no publicar metadatos.

---

## 8. Evidencia (comandos y salidas)

Comando de reproducción (import read-only del módulo canónico + oráculo pd10; sin escrituras, sin
`prepare`):

```
python3 /tmp/opencode/discovery-005-008-probe.py
```

Salida (extracto, verbatim):

```
== classify_path (priority oracle) ==
  webmin-module/module/main.pl        -> 'implementation'
  webmin-module/module/t/basic.t      -> 'tests'
  webmin-module/module/t/helper.pl    -> 'tests'
== _derived_maps('test-writer') ==
  read: [('webmin-module/module/**', 'deny')]
  edit: [('*', 'deny'), ('webmin-module/module/t/**', 'allow'), ('docs/cdad-policy.json', 'deny'), ('.opencode/agents/**', 'deny')]
== findLast verdicts (pd10 oracle) ==
read   webmin-module/module/t/basic.t     deny     allow    allow
read   webmin-module/module/t/helper.pl   deny     allow    allow
edit   webmin-module/module/t/basic.t     allow    deny     allow
edit   webmin-module/module/main.pl       deny     allow    allow
== focal: test_files UNDER implementation (criterion 2) ==
  classify webmin-module/module/t/standalone.t -> tests
  _test_patterns(policy2) = []
```

Baseline de regresión (verde, sin el fix; demuestra que el defecto no está cubierto):

```
python3 -m pytest tests/test_004_002_t1_policy.py tests/test_004_002_t5_reviewfix.py -q
  -> 35 passed in 16.73s
python3 -m pytest "tests/test_004_002_t5_runtime.py::TestPd7I9DerivedMaps" \
    tests/test_opencode_read_map_and_steps.py tests/test_004_002_t7_private_paths.py \
    tests/test_004_002_t7_w2.py -q
  -> 25 passed in 16.09s
```

Repo sin cambios de producto por esta tarea:

```
git -C <repo-root> status --short
  ->  M docs/.cdad-state.json   (pre-existente, ajeno a esta tarea)
```

---

## 9. Resumen para el draft

- El defecto es **una asimetría en `_derived_maps`** (`cdad_packet.py:2643-2645`): falta el allow de
  los árboles de tests declarados en el mapa `read` del `test-writer`; el `edit` ya lo tiene.
- La **clasificación ya es correcta** (tests>impl) y el **guard CC ya es correcto**; solo hay que
  alinear el mapa OpenCode.
- La corrección debe cubrir también el **caso focal `test_files`** (hoy ignorado por
  `_test_patterns`), **nunca** usar convenciones globales Perl, y conservar **`private` al final**.
- Los tests a extender/reutilizar y los fixtures canónicos están identificados (§4).
- El manifiesto y la publicación **no cambian de forma**; solo cambia el hash derivado.
- Los comandos de validación van al **Makefile/systemPatterns del consumidor** (no a
  `docs/cdad-policy.json`); **no existe** registro Perl hoy.
- No duplicar 005-006 (arranque) ni crear agentes Perl manuales; reusar el precedente de
  especialización por stack.
- Quedan **VERIFY** abiertos (§7), en particular los datos reales del consumidor y la mediación viva.
