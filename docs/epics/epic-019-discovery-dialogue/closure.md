# Epic epic-019-discovery-dialogue — Cierre

**Cerrado:** 2026-11-17 · **6/6 features** · **desplegado en local dos veces el 2026-11-17; no publicado** (reservado al dueño).
**Duración:** 2026-11-15 (plan aprobado por Pablo) → 2026-11-17 (3 días).
**Revisión de cierre (gate del epic):** `56e667eed0dad16b9ce6cd393394b97256a72afa`.

## Resumen

El epic abordó un defecto de **contrato de interacción**, no de redacción: la guía existente mandaba al arquitecto delegado preguntar y esperar respuestas sin conectar esa conversación con el usuario a través del orquestador, y las instrucciones que un agente recibe no siempre hacían recuperable la acción que se le pedía. Entregó seis unidades en un solo hilo: el **diseño operativo** del diálogo y del traspaso, la regla de **verificación elegida por la naturaleza de cada promesa**, su **activación** en instrucciones canónicas y consumidores reales, el **layout por proyecto** con un único comando de intake, las **rondas de revisión acotadas** con agotamiento dispuesto, y la reparación del **instrumento de verificación** que bloqueaba su propio gate. Cerró con la suite completa **exit 0 — 2201 passed, 5 skipped, 0 failed en 5215.49 s**, sin haber publicado nada.

## Features entregadas

| Orden | Feature | Cierre | Resultado observable |
|---|---|---|---|
| 1 | `019-001-discovery-dialogue-contract` | 2026-11-15 | diseño operativo revisado del diálogo: roles, qué preserva cada traspaso, readiness y aprobación separadas, rutas ligeras, mapa R1–R12, ejemplos B-01–B-26; **propuesta documental, no activación** |
| 2 | `019-003-contract-verification-strategy` | 2026-11-15 | cada promesa declara **antes de producir** su método (`executable` / `contextual review` / `combined`), criterio de aceptación, evidencia esperada y límites; el ciclo enruta y cierra por ese método |
| 3 | `019-002-effective-discovery-instructions` | 2026-11-16 | activación en instrucciones canónicas y consumidores: la consulta del arquitecto vuelve como `role-report`, el reposo se diagnostica en vez de recomendar abrir, ejercicio PC-7 *supported within declared limits* |
| 4 | `019-004-project-layout-and-dispatch-intake` | 2026-11-17 | metodología por proyecto relativa a la raíz del repositorio (nuevos en `cdad/`, existentes sin cambios) y **un solo** `cdad_packet.py intake` validando rutas A y C sobre el mensaje recibido |
| 5 | `019-005-bounded-review-cycles` | 2026-11-17 | rondas acotadas por unidad y familia con agotamiento dispuesto nunca presentado como éxito; un solo unit de acumulación no recursivo; despacho autocontenido |
| 6 | `019-007-suite-selector-maintenance` | 2026-11-17 | el selector de artefactos desplegados elige por `source` registrado en el manifiesto, sin fallback por nombre; solo tests |

`019-006` **nunca se abrió**: fue un id de enmienda retirado cuando el dueño decidió que el despacho autocontenido se absorbiera en `019-005` (`plan.md` §"Scope amendment — self-contained dispatch").

## Verificación y evidencia

**Gate del epic — suite completa.** Comando `CDAD_TEST_TMP_BASE=/var/tmp/cdad-suite-epic2 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests`, raíz del repositorio, sin trabajo concurrente del orquestador durante la corrida: **exit 0 — 2201 passed, 5 skipped, 0 failed, 0 errors en 5215.49 s (1:26:55)** sobre `56e667ee` (árbol limpio al inicio). Evidencia: `.cdad/orchestration/epic-019/final-suite-epic-6/{result.md,pytest.log,exit-code.txt,snapshot.txt,command.txt}`. **Es la única corrida completa verde** del cierre del epic.

Las cuatro corridas previas se conservan y **no se presentan como regresiones del producto**:

| Corrida | Resultado | Causa diagnosticada | Disposición |
|---|---|---|---|
| `final-suite-epic-2` | `8 failed, 2187 passed, 5 skipped` (5094.52 s) | base temporal dentro de `~` (con `version.txt` en ancestros, dentro de un worktree git) y cwd en el directorio de evidencia | ocho nodeids verdes desde la raíz con `/var/tmp` en 16.49 s; evidencia de entorno, no de producto |
| `final-suite-epic-3` | `1 failed, 2194 passed, 5 skipped` (4995.55 s) | ventana temporal de PD-11 (`test_006_001_t2_wait_recovery.py`, subcaso `transport-error`): con cota de 2 s quedan ~0.20 s al cliente y la carga de la suite cruza la ventana | sensible a la carga; documentada en `docs/suite-maintenance.md`; verde en aislamiento, que **no reemplaza** la corrida completa |
| `final-suite-epic-4` | `1 failed, 2194 passed, 5 skipped` (5024.64 s) | `find_deployed()` devolvía la primera coincidencia de `rglob` y el instalador despliega el mismo nombre a dos runtimes con bytes distintos | defecto preexistente del instrumento, no del instalador; registrado en `docs/suite-maintenance.md` |
| `final-suite-epic-5` | `1 failed, 2194 passed, 5 skipped` (5036.63 s) | el mismo node id, reproducible en la suite y verde en aislamiento | disposición al dueño; el dueño aprobó abrir `019-007` ("Sí, ok A") |

**Evidencia por unidad.**

- `019-001`: `review-004` **sin bloqueos** con PC-1..PC-12 satisfechos como propuestas; verificación por decisión directa del dueño —en una unidad puramente documental **la revisión semántica independiente ES la verificación**—; selección adyacente de 48 tests documentales y `cdad-suite.py validate` rc=0 tras registrar el módulo de 018-001; Memory Bank en `cf4c1e48`. Detalle: `docs/specs/019-001-discovery-dialogue-contract/closure.md`.
- `019-003`: nueve rondas de revisión independiente y ocho de corrección; `review-009` **sin bloqueos** (PC-1..PC-6); 38 tests rc=0, `validate` `ok` con 2068 nodeids, y **69 comparaciones de bytes, cero diferencias** contra la instalación aislada. Límite declarado: el revisor no acredita los 38 como corrida propia verde (su repetición terminó en timeout) y la igualdad de bytes no demuestra fidelidad semántica. Detalle: `docs/specs/019-003-contract-verification-strategy/closure.md`.
- `019-002`: PC-4 en `dbb15fbd`/`cbd7828a` (17 tests), PC-5 en `62224ee7`/`02ff945a` (105 regresiones de `status`/`open-unit`/idle-history); ejercicio PC-7 evaluado como *supported within declared limits* en `recovery-exercise-review.md`; suite completa **2069 passed, 5 skipped, 0 failed en 4534.18 s** sobre `65d0ba62` (`.cdad/orchestration/epic-019/recovery-final-suite-3/`). Detalle: `docs/specs/019-002-effective-discovery-instructions/closure.md`.
- `019-004`: `tests/test_019_004_layout.py` (7), `test_019_004_lifecycle_layout.py` (19), `test_019_004_received_intake.py` (21), `test_019_004_installed_intake.py` (HOME aislado, árbol y HOME real intactos) y los tests de ambigüedad/enumeración; suite completa **2195 passed, 5 skipped, 0 failed en 5063 s** sobre `64ff624d` (`.cdad/orchestration/epic-019/final-suite-019-004/`). Detalle: `docs/specs/019-004-project-layout-and-dispatch-intake/closure.md`.
- `019-005`: traza de receptor completada, recepción idéntica con recibo byte-idéntico y dos casos de Promise E (receptor detenido por localizador faltante; recurso fuera de scope reportado, con el primer intento denegado conservado); contratos con adjudicaciones 001 y 002. La suite completa de la unidad no se corrió: **el gate es la suite del epic**, y quedó verde. Detalle: `docs/specs/019-005-bounded-review-cycles/closure.md`.
- `019-007`: clase `TestT5StagingIsSourceOfTruth` **4 passed** y tres módulos **32 passed**; sensibilidad **3 fallos** con el selector anterior; revisión de resultado **1/2 sin bloqueantes** (6 focales passed, abstenciones declaradas). Detalle: `docs/specs/019-007-suite-selector-maintenance/{spec.md,plan.md,plan-review.md,review.md,closure.md}`.

**Integración entre features.** **No existe una suite E2E cross-feature separada, y no se declara una que no exista.** Las unidades comparten la superficie de paquete/intake: la suite completa la ejercita mediante los tests de intake y de paquete de `019-004`, y la trayectoria registrada de `019-005` documenta su uso real. El epic no necesitó un artefacto de integración propio.

**Despliegue.** Se realizó dos veces el 2026-11-17 con autorización expresa del dueño, en ambos casos **independiente del cierre** (la evidencia de aceptación es la del repositorio y del HOME aislado, no la de la copia instalada): `019-004` —respaldo `~/clawd/archive/cdad-deploy-019-004-20261117-094730`, `install.sh --check` **PASS** con 379 grupos— y `019-005` —respaldo `…-cdad-deploy-019-005-20261117-120956`, `--check` **PASS** con 410 grupos—. En ambos: 11 agentes CDAD presentes, verificación PASS y **los 22 registros de modelo sin cambios**. Registros: `docs/specs/019-004-…/deployment.md`, `docs/specs/019-005-…/deployment.md`. **Publicación no realizada.**

## Decisiones y patrones

Los patrones arquitectónicos y las convenciones del epic están registrados, con su motivo y su precio, en `docs/systemPatterns.md`:

- §"Diálogo de discovery efectivo — consulta entregable y reposo coherente (epic 019, 2026-11-16)" (`docs/systemPatterns.md:643`): la consulta vuelve porque la tabla canónica la admite; la prohibición del orquestador cubre producto y tests; el reposo se comprueba antes de recomendar; la verificación retiene la estrategia por promesa y no reinstala obligaciones superadas.
- §"Layout por proyecto, intake único y rondas acotadas (epic 019, 2026-11-17)" (`docs/systemPatterns.md:651`): layout resuelto por proyecto y por raíz del repositorio; evidencia de ambigüedad como lista cerrada; un solo comando valida el dispatch recibido; consumidores instalados sin redescubrimiento; una ronda con tres familias y allowance propia; el agotamiento nunca se convierte en éxito; el consumo se recupera de registros ordinarios; un solo unit de acumulación; el despacho lleva todo lo que el rol necesita.

Decisiones ya cubiertas por ADR vigentes y que este epic **no re-declara**: ADR-020 (política única de evidencia y procedencia declarada), ADR-021 (una entrada de intake y un dueño canónico por objeto de reconocimiento), ADR-038 (admisión en cada frontera invocable y comparación de bytes con el render canónico) y ADR-042 (defaults de evidencia por momento, cierre de epic obligatorio por defecto o dispensa expresa — dispensa que este cierre **no** usó).

## Rondas y acumulación

- **No se admitió ninguna unidad de acumulación.** Los hallazgos de la ronda 5 de `019-005` fueron **suplidos** por la adjudicación 002 (`evidence/sessions/receiver-completed-trace.json`, `evidence/identical-retry-clean.log`, `evidence/descriptor-review-005.json`), no aceptados como residuo opcional, y `019-007` cerró sin hallazgos. El registro correcto es ese resultado, no la apertura de un unit vacío; **el epic no abre ni promete** una unidad de acumulación.
- `019-005` consumió sus tres rondas de resultado y dos adjudicaciones autorizaron rondas cuatro y cinco con techo finito cada una; todos los informes y recibos se conservan y ninguno se descartó.
- `019-007` gastó **draft 1/2** y **resultado 1/2**, ambos sin correcciones.
- Cierre del epic sin dispensa de suite: la corrida verde de `final-suite-epic-6` es la que alimenta el gate.

## Deuda técnica que se lleva

- **Enforcement automático de las rondas acotadas y parseo de notas en texto libre:** diferidos por diseño instruccional, para no crear un segundo mecanismo de estado ni falsa confianza por parseo de prosa.
- **Normalización retrospectiva de unidades cerradas y medición de cumplimiento cross-model:** diferidas; la primera reescribiría historia y la segunda no fue prometida (la traza acotada no es un benchmark).
- **Resolución de ítems acumulados opcionales:** fuera del compromiso de `019-005`; no hay ítems que resolver en este epic.
- **Ventana temporal de PD-11 en `tests/test_006_001_t2_wait_recovery.py` sigue siendo sensible a la carga:** exige una decisión de diseño (ventana del cliente o presupuesto del preflight), no un retoque; registrada en `docs/suite-maintenance.md` §"Inestabilidades conocidas de la suite completa".
- **Higiene de la base temporal:** la corrida completa necesita una base fuera de todo worktree y sin `version.txt` en sus ancestros (`docs/suite-maintenance.md` §"Base temporal"); es higiene de ejecución, no garantía del producto.
- **Journey fresh-role sobre la copia desplegada:** no demostrado; el procedimiento se verificó mecánicamente contra el manifiesto para los tres prefijos de runtime y la observación sobre lo desplegado queda como pedido acotado del dueño.
- **Procedencia histórica de la Ruta C:** ausente; la gramática se ejercita con wrappers sintéticos y así se declara.
- **`deferred-hardening` de las seis specs**, conservados con su disposición en cada `closure.md` de unidad y transcriptos en este cierre; **ninguno aplaza una postcondición comprometida**.
- **Defectos procedimentales conservados como tales:** el paquete de scribe retirado de `019-003` pese a un despacho nativo real; el registro de review-fix-013 de `019-002` fallido por `active_packet mismatch: id`; y el `tests.log` sintetizado de `019-003` sin verde reproducido. No se reconstruyeron como validaciones exitosas.

## Límites

- **La captura nativa de un despacho recibido no está verificada** en este runtime: el comando valida la representación suministrada y no prueba su origen. Las instrucciones exigen el procedimiento manual y prohíben afirmar validación automatizada cuando la captura no está disponible.
- **La paráfrasis arbitraria no es detectable:** se rechazan líneas verbatim de 24 caracteres o más, encabezados y delimitadores; un fragmento reformulado no se afirma detectado. Es una frontera declarada, no un hueco silencioso.
- **Un verde de suite no prueba la ausencia universal de regresiones**, y la suite no ejercita conducta de agentes reales: el ejercicio de `019-002` es evidencia acotada de un candidato en un proyecto descartable, no un benchmark de cumplimiento.
- **La igualdad de bytes y la revisión contextual no acreditan fidelidad semántica ni despliegue**: son controles de otra categoría, y una limitación declarada nunca asciende de categoría de evidencia.
- **El epic no promete** cumplimiento universal de agentes, cobertura exhaustiva de escenarios, enforcement automático de aprobaciones, ni que toda regresión futura sea detectada por la suite.

## Pendientes reservados al dueño

- **Publicar.** No se publicó nada y la publicación sigue fuera del mandato delegado del epic.
- **Decidir sobre una unidad de acumulación.** No se admitió residuo en este epic; abrirla o no es decisión del dueño, no del ciclo.
- **Resolver la ventana de PD-11 o su presupuesto**, si se quiere retirar la inestabilidad conocida de la suite completa.
- **Pedir, si lo desea, la observación acotada del journey fresh-role** sobre la copia desplegada.
