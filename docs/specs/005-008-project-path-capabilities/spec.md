> Spec **aprobada** (2026-10-10) junto con el plan. Texto del **architect** (subetapa `draft`,
> etapa 2), materializado con el flujo (receive + materialize create-only) por el orquestador
> (ADR-003); aprobada por el orquestador OpenCode bajo la delegación HITL de epic-005
> (`execution.md`). Decisiones D1–D7 aprobadas tal como se proponen en §7; los VERIFY abiertos de
> §8 quedan registrados y los nº 1, 3, 5 y 6 se cierran o se declaran en la aceptación (T3).
> Insumo verificado: `docs/specs/005-008-project-path-capabilities/discovery.md` (mapa
> archivo:línea, defecto reproducido). Contrato: `docs/epics/epic-005-real-operation/plan.md`
> (fila de orden 4, `:37`; sha256 `f3b66be0…`). Criterios de origen:
> `docs/epics/epic-005-real-operation/priority-perl-cli-plan-2026-10-10.md` §3. Formato de
> referencia de este epic: `docs/specs/005-006-guided-project-start/spec.md`.

## Spec — 005-008-project-path-capabilities

**Feature ID:** `005-008-project-path-capabilities` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobada (2026-10-10, orquestador OpenCode, HITL delegada epic-005).

```yaml
feature_id: 005-008-project-path-capabilities
feature_name: Capacidades de rutas de proyecto coherentes con la política (primer consumidor Perl/Webmin, tests anidados)
created_at: 2026-10-10
status: approved
approved_by: orquestador OpenCode (HITL delegada epic-005)
approved_at: 2026-10-10
```

### 1. Descripción funcional

El resultado no es una función nueva ni un sistema de políticas paralelo: es que, **para un
proyecto cuya política declara una raíz de tests anidada dentro de una raíz de implementación**
(primer consumidor real: Perl/Webmin, implementación `.pl`/`.cgi` bajo `webmin-module/<module>/`
y tests en su subdirectorio `t/`), las **capacidades mediadas por ruta** de los agentes de rol
coincidan con la política del proyecto:

- el **test-writer lee y edita** sus tests y auxiliares declarados;
- el **test-writer conserva el deny mediado de lectura** sobre la implementación;
- el **implementer edita implementación y no tests**;
- la **clasificación** (clase mecánica) y los **permisos derivados** (mapas findLast) **concuerdan**
  en la prioridad de `test_roots`/`test_files`, implementación y rutas privadas;
- una **excepción de tests nunca reabre una ruta privada**;
- **no** se introducen reglas globales `**/t/**` ni `**/*.t` ni entradas por ruta nuevas en
  `grep`/`glob`;
- un **segundo layout convencional** funciona sin regresión;
- el **proyecto registra los comandos de sintaxis y tests Perl en su lugar canónico**, y el
  producto **instalado demuestra** las capacidades positivas y negativas con **operaciones reales
  del runtime**, con límites honestos declarados.

**Defecto reproducido (fuente: discovery §1.2 y §2; reproducido en §6).** `_derived_maps`
(`skills/cdad-cycle/scripts/cdad_packet.py:2608-2672`) emite, en la rama `test-writer`, un mapa
`read` (líneas 2643-2645) que concatena el **deny de las raíces de implementación** + los **allows
de tests co-ubicados** + `private`, **sin** el allow del **árbol de tests declarado**
(`_test_patterns`). El mapa `edit` del mismo rol (2646-2650) **sí** incluye ese allow (2647). Con
la política del caso Perl la consecuencia observable es: el test-writer **puede editar** `t/basic.t`
y `t/helper.pl` pero **no puede leerlos** (el `read` resuelve `deny`). Además, `_test_patterns`
(2587-2594) **ignora `test_files`**: con `test_files` declarando un archivo bajo la implementación,
la clasificación lo da `tests` (`exact("test_files")`, 240-241) pero los mapas derivados lo
**deniegan** para leer y editar (caso focal, §2/PD-5).

La **clasificación ya es correcta** (tests > implementación por precedencia, 240-243 antes de
244-245) y el **guard de Claude Code ya es correcto** (`scripts/claude-code-path-guard.sh:211-217`
bloquea solo si la clase es `implementation`), de modo que la corrección **alinea el mapa OpenCode
con el clasificador y con el guard CC**; no cambia la clase ni el guard.

El comportamiento se fija como **postcondiciones observables** sobre artefactos publicados (los
mapas de permisos de los agentes derivados que emite `prepare`, evaluados con el oráculo findLast
único, `tests/pd10_permission_semantics.py`), **no** sobre funciones internas ni mocks de
plumbing.

### 2. Contrato

**Contrato bidireccional (el arnés ↔ el rol).**

- **Lo que el arnés da al rol:** una **política de rutas válida** (esquema de exactamente tres
  campos, `cdad_packet.py:415-426`) que puede declarar una **raíz de tests anidada** en una raíz de
  implementación y/o **`test_files`** bajo implementación; los **agentes derivados de proyecto**
  (publicados por `prepare`) con mapas `read`/`edit` que expresan exactamente esa política; el
  **clasificador único** (`classify_path`) como fuente de la clase; el **guard CC** en paridad; y,
  en el lugar canónico del proyecto, los **comandos** de validación.
- **Lo que el rol devuelve:** el test-writer produce tests bajo sus raíces declaradas y **puede
  leerlos y editarlos**; el implementer edita implementación y **no** tests; ante **ausencia de
  intérprete, runner o dependencias**, un **diagnóstico útil** (qué falta y cómo seguir), **sin**
  cambios no autorizados en máquinas productivas.
- **Salida legítima ante bloqueo:** el arnés no fabrica autoridad, no cambia de versión en silencio
  y no publica un paquete inválido; nombra el campo/archivo/marcador faltante y la opción para
  corregirlo.

**Observabilidad (cómo se verifica el contrato).** Las postcondiciones de política y derivados
(PD-1..PD-9) se comprueban **sobre los agentes derivados publicados** (frontmatter de permisos,
salida observable de `prepare`) evaluados con el **oráculo findLast único** reutilizado por import
(`pd10_permission_semantics.verdict`), el mismo evaluador que usan las suites 004-002. **No** se
aceptan verificaciones contra nombres de funciones internas (`_derived_maps`, `_test_patterns`) ni
mocks del plumbing: el test-writer no lee implementación, así que el test de comportamiento
describe la capacidad observable (allow/deny por herramienta y ruta), no la mecánica. Los aspectos
de pura prosa (PD-10c, PD-11) se verifican por **review** (la review formal del cierre), según el
precedente de 005-006.

**Superficie que 005-008 toca (sin controlador nuevo, sin flags nuevos):**

- **Modificado (producto, fuente canónica):** `skills/cdad-cycle/scripts/cdad_packet.py`
  — la rama `read` del `test-writer` en `_derived_maps` (2641-2651) para reabrir el **árbol de
  tests declarado** después del deny de implementación y **antes** de `private`; y `_test_patterns`
  (2587-2594) para **incluir `test_files`** (decisión D1). El `edit` del test-writer y el `edit`
  del implementer **consumen la misma fuente** y quedan en paridad automáticamente.
- **Nuevo (tests):** `tests/test_005_008_t1_nested_tests.py`,
  `tests/test_005_008_t2_language_commands.py` (T2),
  `tests/test_005_008_t3_acceptance.py` (T3).
- **Modificado (T2, metodología — solo si el discovery confirma una brecha real):** un **puntero
  corto** al lugar canónico de los comandos del consumidor (Makefile/systemPatterns), **reusando
  005-006**; **no** se agrega otra skill ni se duplica el bootstrap.
- **Sin cambios:** el **clasificador** (`classify_path`), el **guard CC**
  (`claude-code-path-guard.sh`), el **esquema de política** de tres campos, el **esquema del
  manifiesto** y el **mecanismo de publicación atómica** (`_publish_generation`).

**Postcondiciones (numeradas y verificables).**

**PD-1 (el test-writer LEE su árbol de tests anidado).** Para una política válida con una raíz de
tests declarada **anidada** dentro de una raíz de implementación, el mapa `read` del derivado
`cdad-test-writer` (publicado por `prepare`) resuelve **allow** para los archivos bajo esa raíz de
tests —incluido un **auxiliar no llamativo** como `t/helper.pl`—, por findLast. Verificable:
`verdict(tw, "read", "<raíz>/…") == "allow"` sobre el derivado publicado.

**PD-2 (el test-writer conserva el deny de lectura de la implementación).** En la misma política,
el mapa `read` del test-writer resuelve **deny** para los archivos de implementación declarados
(la barrera mediada de lectura se conserva). Verificable: `verdict(tw, "read", "<impl>/main.pl") ==
"deny"`.

**PD-3 (el test-writer EDITA su árbol de tests y NO edita la implementación).** El mapa `edit` del
test-writer resuelve **allow** para los archivos bajo el árbol de tests declarado y **deny** para
los de implementación. Verificable: `verdict(tw, "edit", …)` — allow en tests, deny en
implementación. (No-regresión: hoy ya es correcto.)

**PD-4 (el implementer edita implementación y no tests).** El mapa `edit` del derivado
`cdad-implementer` resuelve **allow** para implementación y **deny** para los archivos de tests
declarados (`test_roots` y `test_files`); su `read` **no** deniega los tests (allow por defecto).
Verificable: `verdict(imp, "edit", …)` y ausencia de entrada de tests en su `read`.

**PD-5 (caso focal `test_files` bajo implementación).** Para una política válida que declara
`test_files` con un archivo bajo una raíz de implementación (con `test_roots` vacío o sin cubrirlo),
el test-writer resuelve **allow** para **leer y editar** ese archivo declarado, y el implementer lo
**deniega en `edit`**; un archivo **con forma de test pero no declarado** (no está en `test_roots`,
`test_files` ni es co-ubicado) bajo la implementación sigue resolviendo **deny** para el test-writer
(no se corrige solo el ejemplo `.t`). Verificable: los cuatro veredictos por oráculo sobre archivo
declarado y archivo no declarado.

**PD-6 (una excepción de tests NUNCA reabre una ruta privada).** Con una ruta **privada anidada
dentro de la raíz de tests** (p. ej. `tests/.sensitive-patterns.local` bajo `tests/`), el mapa
`read` **y** `edit` de **todo** rol resuelven **deny** para esa ruta y su subárbol, aun cuando exista
un allow de tests para su padre; el hermano no privado bajo `tests/` sigue resolviendo allow para el
test-writer. Verificable: precedencia findLast (el allow de tests va **antes** que `private`).
(Fija el invariante ya vigente, `cdad_packet.py:2627-2640`, `2671`.)

**PD-7 (sin amplificación — guard B3).** Con un directorio **literal `tests/` anidado bajo una raíz
de implementación** (p. ej. `src/tests/x.py`, clase `implementation` por el clasificador), el
test-writer resuelve **deny** para `read` y `edit`, y el implementer **allow** para `edit`. Además,
**no existe** ninguna regla global `**/t/**` ni `**/*.t` en los derivados: solo se reabren los
**árboles/archivos declarados**. Verificable: veredictos por oráculo + barrido de patrones.

**PD-8 (un segundo layout convencional funciona sin regresión).** Para un layout convencional
(implementación `src`/`lib`, `test_roots: ["tests"]`, co-ubicados por prefijo/sufijo), los
veredictos del test-writer y del implementer **coinciden** con los previos a la corrección
(lectura de implementación denegada, tests permitidos, co-ubicados permitidos). Verificable:
veredictos por oráculo sobre el layout convencional, comparados contra el comportamiento esperado.

**PD-9 (sin entradas por ruta nuevas en `grep`/`glob` — W-2).** Ningún derivado gana entradas por
ruta en `grep`/`glob`; la corrección modifica **solo** `read`/`edit` (los mapas `grep`/`glob`
siguen ausentes). Verificable: `assert_no_search_path_entries` sobre todos los derivados publicados.

**PD-10 (comandos en el lugar canónico; el esquema de política no los admite).**
(a) El comportamiento requerido es que el **proyecto** declare los comandos de **sintaxis** y de
**tests** Perl en su **lugar canónico** (Makefile o systemPatterns), **nunca** en
`docs/cdad-policy.json`. (b) El esquema de la política se mantiene **exactamente de tres campos**
(`schema_version`, `path_policy`, `temporary_roots`); una política con un campo extra (p. ej.
`commands`) se **rechaza** con diagnóstico nombrado, sin cambios silenciosos. (c) La metodología
nombra el lugar canónico **por referencia** (`stage-3-tdd.md` §«Test evidence policy»), sin
duplicarlo. (d) Ante ausencia de intérprete, runner o dependencias, la salida es un **diagnóstico
útil**, sin instalar ni operar producción. Verificable: (b) test de esquema (política con cuarto
campo → rc≠0 con diagnóstico); (c) puntero estructural; (d) por **review**; la **declaración real**
del consumidor es acto de su dueño (VERIFY 6, registrado en la aceptación).

**PD-11 (el producto INSTALADO demuestra las capacidades con operaciones reales del runtime).** Desde
la versión instalada, una operación real del runtime demuestra las capacidades **positivas**
(test-writer lee/edita sus tests; implementer edita implementación y no tests) y **negativas**
(test-writer no lee implementación; la ruta privada queda denegada), con los **límites honestos**
declarados: `grep`, el shell y una sesión separada **no** son sandbox; **no** se reintroducen
allowlists por comando. Verificable: evidencia registrada del recorrido real + los límites
declarados en la evidencia.

### 3. Invariantes (verificables)

- **INV-1.** El **clasificador es la fuente única**; los mapas derivados expresan **exactamente**
  la política (ni amplificación ni sobre-restricción): test anidado → allow para el test-writer,
  implementación → deny de lectura; un `tests/` literal no declarado → implementación (B3/PD-7).
- **INV-2.** **`private` gana siempre**: el allow de tests se emite **antes** de `private` en
  `read` y `edit`; una excepción de tests **nunca** reabre una ruta privada (PD-6).
- **INV-3.** **Sin convenciones globales** de ruta (`**/t/**`, `**/*.t`): solo se reabren los
  **árboles y archivos declarados** en la política (PD-7).
- **INV-4.** **Sin entradas por ruta** en `grep`/`glob` (W-2): la barrera viva por ruta es
  `read`/`edit`; los derivados no declaran una barrera que no existe (PD-9).
- **INV-5.** El **esquema de la política permanece de exactamente tres campos**; los comandos son
  del proyecto, no de la política (PD-10).
- **INV-6.** **No hay sandbox prometido**: `grep`, el shell y la sesión separada no son aislamiento;
  no se reintroducen allowlists por comando (`cdad-generate.py:223-234,301-329`; W-2).
- **INV-7.** **No** se implementa el **producto consumidor** (Perl/Webmin), **no** se crean agentes
  Perl manuales ni otro sistema de políticas (PD-10/PD-11 frontera).
- **INV-8.** **Sin cambios de forma** en el **clasificador**, el **guard CC**, el **esquema del
  manifiesto** y el **mecanismo de publicación atómica**; solo cambia el contenido del mapa `read`
  del test-writer y la fuente de patrones de tests (y el hash derivado correspondiente).
- **INV-9.** **No** cambian el alcance ni los criterios de aceptación de epic-005; **activar
  versiones**, **cambios en HOME**, la **confianza de carpeta de Claude Code** y la **operación de
  producción** siguen **reservados al dueño** (`execution.md:19-23`).

### 4. Criterios de aceptación

- [ ] **PD-1/PD-2/PD-3/PD-4**: con una política válida de tests anidados, el test-writer lee y
      edita sus tests y conserva el deny de lectura de implementación; el implementer edita
      implementación y no tests (veredictos por oráculo sobre los derivados publicados).
- [ ] **PD-5**: el caso focal `test_files` bajo implementación queda permitido al test-writer
      (leer y editar) y denegado al implementer en `edit`; un archivo con forma de test **no
      declarado** sigue denegado.
- [ ] **PD-6**: una ruta privada anidada en la raíz de tests permanece denegada en `read` y `edit`
      para todo rol (precedencia findLast conservada).
- [ ] **PD-7/INV-3**: sin amplificación (`tests/` literal bajo implementación sigue
      implementación); **no** hay reglas `**/t/**` ni `**/*.t`.
- [ ] **PD-8**: el layout convencional no regresiona (veredictos idénticos a los previos).
- [ ] **PD-9/INV-4**: ningún derivado gana entradas por ruta en `grep`/`glob`.
- [ ] **PD-10/INV-5**: el esquema de la política sigue de tres campos y rechaza un campo de
      comandos con diagnóstico; el puntero al lugar canónico existe; la declaración real del
      consumidor se registra en la aceptación (VERIFY 6).
- [ ] **PD-11**: el **recorrido real del producto instalado** demuestra las capacidades positivas y
      negativas, con los límites honestos declarados (grep/shell/sesión separada no son sandbox;
      sin allowlists por comando); evidencia registrada.
- [ ] **Suite completa verde al cierre** y `make validate` sin fallos nuevos (los FAIL
      preexistentes, si los hay, no se atribuyen a este diff).

### 5. Fuera de alcance

- **Implementar el producto consumidor** (Perl/Webmin) o **crear agentes Perl manuales** o **otro
  sistema de políticas** (INV-7).
- **POLICY-CLASS** completa, **CI**, **sandbox** y una **plataforma universal de jobs** (fuera por
  el plan del epic).
- **Cambios en HOME**, **activación de versiones**, **confianza de carpeta de Claude Code** y
  **operación de producción** (reservado al dueño).
- **Redefinir el clasificador**, el **guard CC**, el **esquema del manifiesto** o la **publicación
  atómica** (INV-8).
- **Medición** de contexto (005-002); **delegación externa entre CLI** (005-009); **orientación**
  al retomar (005-003); roles en Claude Code (005-004); planificación progresiva (005-007).

### 6. Contexto técnico (verificado)

**Defecto (reproducido, discovery §2; comando y salida abajo).** Con la política
`implementation_roots: ["webmin-module/module"]`, `test_roots: ["webmin-module/module/t"]`:

- `classify_path` da `implementation` a `main.pl`/`index.cgi` y **`tests`** a `t/basic.t` y
  `t/helper.pl` (precedencia tests > implementación, `cdad_packet.py:240-241` antes de `244-245`).
- `_derived_maps("test-writer")["read"] = [("webmin-module/module/**","deny")]` — **sin** el allow
  del árbol de tests (`cdad_packet.py:2643-2645`).
- `_derived_maps("test-writer")["edit"]` **sí** incluye `("webmin-module/module/t/**","allow")`
  (`cdad_packet.py:2647`).
- Veredictos findLast: `read` del test-writer → **deny** para `t/basic.t`/`t/helper.pl` (defecto) y
  para `main.pl` (correcto); `edit` del test-writer → allow en tests, deny en implementación.

**Caso focal `test_files` (discovery §2.4).** Con `test_roots: []` y
`test_files: ["webmin-module/module/t/standalone.t"]`: `classify_path` → `tests` (por
`exact("test_files")`), pero `_test_patterns` → `[]` (ignora `test_files`,
`cdad_packet.py:2587-2594`), y el `read`/`edit` del test-writer **deniegan** el archivo declarado.

**Por qué no lo cubren los tests actuales (discovery §2.6).** Ningún layout de fixture anida una
raíz de tests bajo una raíz de implementación en los **mapas derivados**: CDAD
(`test_roots:["tests"]` vs `implementation_roots:[agents,skills,scripts,sources,build]`),
convencional (`["tests"]` vs `["src","lib"]`), odoo (`["addons/m/tests"]` vs
`["addons/m/models","addons/m/views"]`) son disjuntas o hermanas. La **clasificación** de tests
anidados **sí** está cubierta (`tests/test_004_002_t1_policy.py:418-427`), pero **no** los mapas.

**Lugar canónico de los comandos (discovery §1.5).** `skills/cdad-cycle/references/stage-3-tdd.md`
§«Test evidence policy» (`:56-59`): «la metodología define la evidencia; el proyecto declara los
comandos» (p. ej. Makefile o systemPatterns). El `Makefile` del repo tiene `staging`, `agents`,
`validate`; **no** tiene target `test`; **no existe** registro de comandos Perl. El esquema de
`docs/cdad-policy.json` (`cdad_packet.py:415-426`) **rechaza campos extra**.

**Guard CC (paridad).** `scripts/claude-code-path-guard.sh:211-217` (rama `test-writer:read`)
bloquea **solo** si la clase es `implementation`; como `classify_path` da `tests` a los tests
anidados, el guard **ya permite** leerlos. El defecto es **exclusivo del mapa OpenCode**.

**Evidencia (comandos y salida; read-only, sin escrituras de producto).**

```
$ python3 /tmp/opencode/discovery-005-008-probe.py
== classify_path (priority oracle) ==
  webmin-module/module/main.pl                  -> 'implementation'
  webmin-module/module/index.cgi                -> 'implementation'
  webmin-module/module/t/basic.t                -> 'tests'
  webmin-module/module/t/helper.pl              -> 'tests'
== _derived_maps('test-writer') ==
  read: [('webmin-module/module/**', 'deny')]
  edit: [('*', 'deny'), ('webmin-module/module/t/**', 'allow'), ('docs/cdad-policy.json', 'deny'), ('.opencode/agents/**', 'deny')]
== findLast verdicts (pd10 oracle) ==
read   webmin-module/module/t/basic.t         deny         allow        allow
read   webmin-module/module/t/helper.pl       deny         allow        allow
read   webmin-module/module/main.pl           deny         allow        allow
edit   webmin-module/module/t/basic.t         allow        deny         allow
edit   webmin-module/module/main.pl           deny         allow        allow
== focal: test_files UNDER implementation (criterion 2) ==
  classify webmin-module/module/t/standalone.t -> tests
  test-writer read: [('webmin-module/module/**', 'deny')]
  test-writer edit: [('*', 'deny'), ('docs/cdad-policy.json', 'deny'), ('.opencode/agents/**', 'deny')]
  _test_patterns(policy2) = []
```

Baseline de regresión (verde **sin** el fix; demuestra que el defecto no está cubierto):

```
$ python3 -m pytest tests/test_004_002_t1_policy.py tests/test_004_002_t5_reviewfix.py \
    tests/test_004_002_t7_private_paths.py tests/test_004_002_t7_w2.py \
    tests/test_opencode_read_map_and_steps.py \
    "tests/test_004_002_t5_runtime.py::TestPd7I9DerivedMaps" -q
60 passed in 32.66s
```

### 7. Decisiones propuestas (a resolver al aprobar)

| Id | Propuesta del architect | Rationale |
|---|---|---|
| **D1** | **Extender la fuente de patrones de tests** para **incluir `test_files`** (una sola fuente), en lugar de un helper solo-read. Afecta el `read`/`edit` del test-writer y el `edit` del implementer. | Mantiene **una sola verdad** y la paridad entre clasificador, `read` y `edit`; `test_files` son tests declarados y deben denegarse al implementer. **VERIFY 2**: sin regresión B3/W-2/F-P1. |
| **D2** | **Orden del mapa `read`**: deny de implementación → allow de tests declarados (+ co-ubicados) → `private` **al final**. | findLast: el allow reabre tests; `private` conserva la precedencia (INV-2/PD-6). |
| **D3** | **Sin convenciones globales**: solo árboles/archivos declarados; nunca `**/t/**` ni `**/*.t`. | B3/PD-7 e INV-3; el proyecto declara sus árboles concretos. |
| **D4** | **Comandos en el lugar canónico del proyecto** (Makefile/systemPatterns); **nunca** en `docs/cdad-policy.json`. | Esquema de tres campos exactos; PD-10/INV-5. |
| **D5** | **Aceptación = comportamiento observable** sobre los derivados publicados (oráculo findLast) para el fix, **más** el recorrido real del producto instalado para las capacidades; la prosa se verifica por **review**. | Precedente 005-006; los tests de comportamiento no leen implementación. |
| **D6** | **T1 es el único cambio de producto**; T2 documenta/verifica la brecha real reusando 005-006 (sin duplicar bootstrap ni crear otra skill); T3 es la aceptación. | Ajuste al tamaño real (discovery §3/§7); proporcionalidad. |
| **D7** | **Frontera explícita**: no implementar el consumidor ni crear agentes/sistema de políticas paralelo; la declaración de política/alcance del consumidor pertenece a su dueño. | plan §3 y frontier; INV-7. |

### 8. VERIFY del discovery §7 — estado y resolución propuesta

| # | VERIFY | Estado en el draft | Resolución / dueño y cuándo |
|---|---|---|---|
| 1 | Layout/política reales del consumidor Perl/Webmin | **ABIERTO** | Datos del consumidor (fuera de este repo); el ejemplo `webmin-module/module` + `.../t/` es caso de uso, no política confirmada. Se registra en la aceptación (T3) con el dueño. |
| 2 | Alcance del fix en `_test_patterns` | **RESUELTO por D1** (propuesta) | Extender la fuente única para incluir `test_files`; **verificar** no regresión B3/W-2/F-P1 (T1). |
| 3 | Mediación real del runtime | **ABIERTO** | PD-11/T3: recorrido real del producto instalado; los límites honestos se declaran; grep/shell/sesión separada no son sandbox. |
| 4 | Precedencia findLast en vivo con `private` anidada en un allow de tests | **PARCIAL** | El oráculo pd10 es el modelo declarado y la sonda en vivo de W-2 es el precedente; se fija por test (PD-6) y se confirma en el recorrido (T3). |
| 5 | Entrega de convenciones/referencias de dominio al consumidor no-odoo | **ABIERTO** | El paquete no inyecta fuentes de dominio (`cdad_packet.py:842-883`); se resuelve con el objetivo+inputs del encargo o, si se justifica, por el mecanismo de stack del generador (sin agentes manuales). VERIFY en T2. |
| 6 | Registro de comandos Perl del consumidor | **ABIERTO** | El consumidor declara `make`/`systemPatterns`; se registra en la aceptación (T3) con el dueño. El esquema de política no admite comandos (PD-10b). |
| 7 | Cobertura Git del consumidor para derivados/metadatos locales | **FUERA del fix** | Ítem de configuración del consumidor (findings #4); relevante para no publicar metadatos; se registra en la aceptación. |

### 9. Fronteras y no-cambio de alcance

- **Frontera con 005-006** (arranque guiado). **Dentro de 005-008:** la coherencia de las
  capacidades de ruta y el registro/verificación de la brecha real de comandos/dominio **reusando**
  el arranque de 005-006. **Diferido/evitado:** **no** duplicar el bootstrap ni crear otra skill
  (T2).
- **Frontera con 005-009** (delegación entre CLI). 005-008 entrega la corrección de permisos que la
  aceptación **conjunta** del consumidor de 005-009 aprovecha; 005-009 **no** pertenece a esta
  feature.
- **Frontera con 005-002** (medición de contexto). Fuera: no hay presupuestos de tokens ni topes de
  llamadas; la aceptación es funcional.
- **No cambia el alcance ni los criterios del epic-005** (INV-9); activación de versiones, cambios
  en HOME, confianza de carpeta y producción siguen **reservados al dueño** (`execution.md:19-23`).

### 10. Aprobación

- **Estado: aprobada (2026-10-10)** por el **orquestador OpenCode** bajo la delegación HITL del
  epic-005 (`execution.md`), con la autoevaluación de `stage-2-specification.md §2.3` y las
  decisiones D1–D7 aprobadas tal como se proponen en §7. La aprobación de la spec es **no
  delegable por defecto**; bajo la delegación HITL del epic-005 la ejerce el orquestador OpenCode.
  El `sha256` del archivo materializado vive en el `state` (pin `contract_path` +
  `contract_sha256`), no dentro del archivo.
- **VERIFY abiertos** (§8): 1, 3, 5 y 6 se cierran o se declaran en la aceptación (T3) con el
  dueño; 2 queda resuelto por D1 y verificado en T1; 4 se fija por test (PD-6) y se confirma en el
  recorrido.
