## Discovery verificado — 008-006

Contrato verificado por SHA-256: coincide con `e7ceb786…e2e50`. HEAD observado: `53233ca35292b6020d80ff6db874bcf72b2c635f`.

**Resultado:** el mapa previo identifica correctamente las responsabilidades, pero requiere corregir contradicciones adicionales en las filas de contrato y en el detalle de stage 3. No existe todavía una spec aprobada de esta feature.

### 1. Hogares actuales y delta mínimo propuesto

| Hogar y evidencia | Texto actual relevante | Propuesta mínima |
|---|---|---|
| `sources/roles/architect.md:82-87` | “tests verify observable postconditions”; “writing numbered, testable postconditions before RED.” | “Write numbered, testable postconditions grouped by observable user promise before RED. Do not demand multiple variants with the same observable result. Include `deferred-hardening` in every spec.” Mantener puntero a la convención, sin copiarla. |
| `sources/roles/test-writer.md:68-82` | “Every test maps to a numbered spec postcondition”; aceptación por postcondición; propiedades con semilla fija; contrapeso de precisión de la spec. | Sustituir la unidad de selección por promesa; conservar trazabilidad a postcondiciones numeradas y propiedades contractuales. Exigir en el informe, por cada test, “sin este test, el usuario…”. Añadir el contrapeso indicado abajo. |
| `sources/roles/test-writer.md:35` | “one test per postcondition” | Cambiar a “one test per observable user promise, traced to the numbered postconditions it protects”. **No basta modificar el bloque compartido:** esta fila se compone también en el orquestador. |
| `sources/roles/reviewer.md:82-84` | “observable contract, not coverage; no mocks over plumbing; every test maps to a postcondition.” | Conservar trazabilidad. Añadir: “A missing-test finding must name the user consequence; otherwise record it in `deferred-hardening`, without blocking, subject to the orchestrator’s promotion rule.” |
| `sources/roles/orchestrator.md:275-278` | “every test maps to a postcondition (drift checks AP-13/AP-14).” | Añadir pregunta previa a aprobar RED: “¿qué se rompe para el usuario sin este test?”. Registrar respuesta y promociones motivadas por seguridad, integridad/pérdida silenciosa de datos o regresión evidente y cara de descubrir tarde. |
| `sources/roles/implementer.md:21-22` | “MINIMAL CODE: the simplest implementation that makes the test pass. No extra features ‘just in case’.” | **Reemplazar**, no añadir una nota contradictoria: “Implement the approved behavior simply, without speculative features. This test-selection rule does not limit reasonable robustness: add necessary validation, guards and error handling even when no test demands them.” |
| `sources/roles/implementer.md:38` | “minimal code that makes the approved test pass” | Alinear la fila: implementación simple del comportamiento aprobado con robustez razonable. |
| `sources/roles/scribe.md:21-28,46-50` | Tres borradores de Memory Bank; convención aplicada a lecciones de tests. No encargo de traslado a closure. | Añadir: “Include the spec’s `deferred-hardening` and its recorded dispositions in the closure draft for orchestrator materialization; do not silently omit it.” No autorizar edición ni aprobación. |
| `skills/cdad-cycle/assets/spec-template/spec.md:34-38` | Postcondiciones numeradas con entrada/salida; sin promesa explícita. | Añadir a cada postcondición referencia a su “observable user promise”; indicar que varias postcondiciones de igual promesa no exigen tests separados. |
| Misma plantilla, `:53-60` | `Out of scope`, seguido de notas; no `deferred-hardening`. | Añadir sección obligatoria `## deferred-hardening`: qué no se prueba ahora y motivo; declarar explícitamente “None” cuando corresponda. No confundir exclusión funcional con verificación diferida. |
| `skills/cdad-cycle/assets/spec-template/test-audit.md:24-30,43-48,64-68` | Tests modificados/nuevos y evaluación de cobertura. | Añadir promesa, postcondiciones protegidas y declaración “sin este test, el usuario…”; reemplazar evaluación genérica de cobertura por promesas verificadas y diferimientos explícitos. |
| `skills/cdad-cycle/assets/feature-plan-template.md:18,71-79` | Postcondiciones cubiertas; tarea de código declara `focal_tests`; cobertura PD↔tarea. | Conservar esquema y cobertura PD↔tarea. Añadir puntero a promesas y `deferred-hardening` de la spec; no introducir un esquema nuevo ni exigir un test por tarea. |

**Detalle canónico:** `skills/cdad-cycle/references/stage-3-tdd.md`.

Actualmente contiene:
- `:17`: “no postcondition triggers more tests than it itself asks for”.
- `:19-23`: aceptación, relevancia y contrapeso por postcondición.
- `:101-104`: selección por postcondición/caminos independientes.
- `:119-123`: validación de RED.
- `:242-245`: cobertura y auditoría test↔postcondición.

Aquí debe vivir el criterio operativo completo:

> Un test se exige por una promesa observable al usuario cuya ruptura podría pasar inadvertida sin él. Variantes internas o implementaciones equivalentes con igual resultado no justifican tests separados. Varias postcondiciones pueden quedar verificadas por un mismo test. Cada test conserva trazabilidad a las postcondiciones que protege y declara «sin este test, el usuario…». Lo diferido queda en `deferred-hardening`.

Actualizar selección y checklist para que no reconstruyan una cuota por postcondición. **No eliminar** la obligación de verificar todas las promesas ni la auditoría independiente.

### 2. Contrapeso: no autoriza dejar de probar

Texto mínimo recomendado para el bloque compartido:

> Esta regla reduce redundancia, no garantías: cada promesa del contrato debe quedar verificada por comportamiento antes de aceptar la feature; un mismo test puede verificar varias postcondiciones. `deferred-hardening` no permite diferir una promesa comprometida ni relaja seguridad, integridad o conservación de datos. Las promociones excepcionales corresponden al orquestador, con motivo registrado conforme al gate.

El detalle de las tres causas de promoción queda en el hogar del gate, no repetido por todos los roles.

**Criterio de diseño:** preferir la regla general por promesa y trazabilidad muchos-a-uno frente a excepciones por archivo o número de variantes. Mantiene garantías sin imponer una cuota de tests. Las excepciones de riesgo quedan explícitas y motivadas.

### 3. Tests afectados: hallazgo real, no rojo supuesto

**No encontré una aserción existente que obligue literalmente a conservar** “one test per postcondition”, “Counterweight”, “100-1000” o “MINIMAL CODE” en estas fuentes. Por tanto, **no hay evidencia para afirmar que cambiar esas frases produzca hoy un rojo**.

Superficie de regresión identificada:

| Tests | Qué protegen realmente |
|---|---|
| `tests/test_cdad_generate.py:247` | Rechazo de bloque compartido duplicado. |
| `tests/test_cdad_generate.py:309-344` | Manifest, hashes y referencias a fuentes regeneradas. No fija hashes antiguos. |
| `tests/test_cdad_generate.py:346-377` | Tabla de contratos compuesta una vez, con todos los roles. |
| `tests/test_005_007_t6_templates.py:188` y siguientes | Apertura desde recorrido de usuario, aceptación observable y plantilla de plan. Preservar estructura existente. |
| `tests/test_006_003_u1_generator_without_profiles.py:183-315` | Manifest sin perfiles y agentes sin modelo fijado; no doctrina de tests. |
| `tests/test_packet_prepare.py:51`; `tests/test_005_005_t1_replace_conserved.py:120` | Literal de fixture “Each test maps to a postcondition”. No demuestra obligación de un test por postcondición ni rojo por editar estas fuentes. |

Los seis candidatos del mapa son **cobertura nueva propuesta**, no seis tests existentes afectados. Deben agruparse por promesas verificables; no aprobarlos automáticamente como seis unidades.

### 4. Generación y staging

Verificado:

- `scripts/cdad-generate.py:68-72`: `convention-rule` tiene host `test-writer`.
- `:840-861`: exige exactamente un bloque en su host y rechaza duplicados.
- `:875-900`: compone agentes y registra fuentes contribuyentes.
- `Makefile:10-18`: genera ambos runtimes en `build/staging` y promueve a `agents/` y `agents/claude-code/`.

Los agentes actuales reproducen el texto antiguo:
- Test-writer: `agents/cdad-test-writer.md:135`; Claude Code `:102`.
- Reviewer: OpenCode `:121-123`; Claude Code `:106-108`.
- Orquestador: OpenCode `:331-334`; Claude Code `:335-338`.
- Implementer: OpenCode `:60`; Claude Code `:46`.

**No todos los agentes contienen el bloque compartido:** algunos contienen punteros. La aceptación debe comprobar composición según consumidor, no exigir copiar el bloque completo a todos.

Además, `tests/product_staging.py:12-15,85-91` reutiliza staging existente; si está desactualizado puede observarse texto antiguo. Regenerarlo será responsabilidad de implementación/cierre.

### 5. Límite verificable

> El producto puede comprobar la presencia de la declaración «sin este test, el usuario…», las secciones requeridas y su composición coherente en plantillas/agentes. No puede decidir mecánicamente si la consecuencia declarada es verdadera, relevante o suficiente. Ese juicio corresponde al reviewer y al gate, con evidencia registrada.

**VERIFY de alcance:** ¿“comprobar presencia” significa tests estáticos de doctrina o un rechazo operativo de informes sin declaración? La segunda opción requeriría contrato adicional sobre formato y recepción de informes; no debe introducirse silenciosamente.

### Evidencia de ejecución

- Comandos ejecutados: `cat`, `cat -n`, `sed -n`, `rg -n`, `ls`, `sha256sum`, `git status --short`, `git rev-parse HEAD`, `git diff --stat`, sobre las rutas identificadas arriba; sus salidas sustentan las citas.
- Una búsqueda incluyó `sources/substages`, inexistente: `rg` lo informó; no se insistió sobre esa ruta.
- Tests y generación: **no ejecutados**; discovery read-only, sin temporales ni staging escritos.
- Archivos modificados por este rol: **ninguno**.
- Estado inicial y final: únicamente `docs/.cdad-state.json` ya modificado; diff final observado: 75 inserciones, 26 eliminaciones. No atribuido a este rol.
- Commit creado: **ninguno**.
