# Review formal (stage 4) — 005-007-progressive-planning

Rol: reviewer (sesión independiente; solo lectura). Packet: `005-007-progressive-planning-reviewer-review-001`.
Objeto: diff `99e2f2e..a5cd0c8` + artefactos `docs/specs/005-007-progressive-planning/**`.
Contrato verificado: `spec.md` sha256 `54877103d622ca75994b503ee4be016bf39682c2c6a6f89962a8436d8d309a4a` ✅ y `plan.md` `1f636260…` (medido, coincide con el paquete). Criterio aplicado: `docs/epics/epic-005-real-operation/execution.md:48-56` (2026-10-12).

## Evidencia de los comandos propios (verificación independiente)

| # | Comando | Resultado |
|---|---|---|
| 1 | `sha256sum docs/specs/005-007-progressive-planning/{spec,plan}.md` | `54877103…` / `1f636260…` ✅ |
| 2 | `python3 -m pytest tests/test_005_007_t1..t7_*.py -q` | **37 passed in 22.11s** (coincide con el oráculo congelado del orquestador) |
| 3 | Probes fail-closed propios contra `_check_plan_tasks` + `_check_plan_validation_plan` (módulo real de producto) | ver Blockings/Optionals; `planned` sin `depends_on` **PASSED** |
| 4 | `timeout 300 make validate` | **141 Assert PASS / 2 Assert FAIL** (F011: `scripts/validate-subagents.sh` + `tests/validate-odoo-specialization.sh`) — exactamente el estado preexistente declarado |
| 5 | Like-for-like F011: `git archive 99e2f2e \| tar -x -C /tmp/opencode/wt-base` y `git archive a5cd0c8 \| tar -x -C /tmp/opencode/wt-head`; en cada árbol `env -u TMPDIR python3 -m pytest tests/test_role_packet_review_regressions.py tests/test_opencode_read_map_and_steps.py tests/test_004_001_t7_capacity.py -q` | base Y head: **4 failed, 8 passed, 6 errors**; `diff` de listas FAILED/ERROR → **IDENTICAL-FAILURE-SET** (los exactos: `TestP4InstallPreservesSteps` + 3 de `test_role_packet_review_regressions.py` + 6 de `test_004_001_t7_capacity.py`). Los 3 archivos son byte-idénticos entre base y HEAD (`git diff --stat` vacío) |
| 6 | `git show --stat` por commit de rol | TODOS acotados a sus archivos declarados: T1 `7ff19c1` (3 docs), T2 `09567cd` (solo `cdad_packet.py`), T3 `54eeed6` (4 archivos declarados), T4 `512d913` (2), T5 `8ac41d6` (2), T6 `594da73` (3), T7 `a59101d` (2); RED `test:` solo-tests en cada unidad antes del GREEN `feat:` |
| 7 | grep de fuente única (regla `detail`, conteo de intentos, formato de bloque) | sin segunda redeclaración en `packets/`, `assets/` ni `references/` fuera de sus dos dueños |
| 8 | modified files (repo) | **ninguno** — rol read-only; no materializo nada en el repo. Único archivo escrito: el transporte `/tmp/opencode/005-007-review.md` (fuera del repo) |
| 9 | commit de cierre | `a5cd0c8` (HEAD etapa 3); base `99e2f2e` |

## Blockings

### B1 — Prepared: una tarea `planned` sin `depends_on` (o con `[]` y sin campos) pasa el validador; PD-1 la exige «siempre» — cas no cubierto por el oráculo, verificado por mí

- **Ubicación:** `skills/cdad-cycle/scripts/cdad_packet.py:3101-3105` (r Planned solo valida la 4-tupla `objective/uncertainty/owner/resolves_when`, constantes `:2900`), `:3021-3024` (`_check_plan_tasks` solo valida `depends_on` **cuando está presente**); espejo del contrato: `spec.md:42` (PD-1: «Toda tarea declara **siempre** un `objective` no vacío y sus `depends_on`»; la tarea planned «completa **objetivo + dependencias**»), `spec.md:30,44` (§2/PD-2); `spec.md:109-110` (D2: cobertora global de dependencias es **el fundamento del marcador**).
- **Problema (probe propio, salida textal):**
  ```
  planned-absent-depends_on -> PASSED (no rejection)
  planned-empty-depends_on  -> PASSED (no rejection)
  ```
  El mismo probe confirma que los demás casos PD-2 sí fallan cerrado (`invalid-detail`, `planned-missing-owner`, `planned-null-resolves_when`, `planned-unsafe-parallelism`, `producer-missing` → REJECTED ✅). El oráculo T2 (`tests/test_005_007_t2_progressive_plan_validator.py:96-146`) construye su fixture planned **siempre con** `depends_on` presente (default `[]`), y la lista de negativos de AC-1 (`spec.md:96`) no incluye dependencia ausente — no hay caso que lo cubra.
- **Consecuencia:** `prepare` publica (si valeria todo lo demás) un plan cuya unidad `planned` declara **o nada sus dependencias** — exactamente la cobertura global (completa dependencias) que es la razón de ser del marcador (D2 y fila 9 del epic). El estado «planificada-no-detallada» queda sin la mitad que lo diferencia de detalle parcial. No rompe el fail-closed mecánico, pero sí un postcondición aprobado (PD-1) en su clase nueva. La chispa es de contrato (AC-1 no enumera el caso), no de descuadra del implementer: cumple lo que AC-1 lista. Por el criterio de review vigente («compromete el resultado/la evidencia», `execution.md:51`) entra como bloque.
- **Sugerencia:** exigir a la tarea `planned` la cláve `depends_on` (lista, posiblemente `[]` — misma mecánica de «declares, possibly empty = 'none affected'» que ya aplica a `regressions`: `cdad_packet.py:3121-3124`). No se requiere tocar el camino sin marcador (INV-5).
- **Condición de cierre verificable:** (1) `_check_plan_validation_plan` rechaza una tarea `detail:"planned"` con la cláve `depends_on` ausente, con diagnóstico que nombra la tarea; acepta `depends_on: []` explícito (probe con el módulo real). (2) Caso negativo nuevo en el oráculo T2: `planned_task("t1", depends_on=None)` → rechazo rc≠0. (3) Los controles de INV-5 sin marcador siguen byte-idénticos (regresiones T2 en verde).
- **Verdict: BLOCKING** · **Bucket: h** (familia de model distinta al implementer `deepseek-v4.1-flash` +1; diff completo de implementación en contexto +1; cita verificable file:line +1; spec+convenciones +1).

### B2 — Falso negativo del medidor ante invocaciones envueltas (clase real del repo): `first_dispatch sale "absent" en la traza real donde SÍ hubo despacho

- **Ubicación:** `skills/cdad-cycle/scripts/cdad_context_meter.py:887-961` (`_program_basename`/`_shell_segments`/`_segment_program` resuelven **el programa del segmento**: ante `time python3 …/cdad_delegate.py …` resuelve `time`; ante `nohup bash -c "python3 …cdad_delegate.py…"` resuelve `nohup bash -c`); evidencia declarada: `docs/specs/005-007-progressive-planning/acceptance.md:54-62` (§2: ledger `dispatches/delegate-opencode-2ac2addcb404.json` vs `first_dispatch: absent`) y `docs/specs/005-007-progressive-planning/debt.md` D-2 (clase: `time`, `env`, `nohup`, `nice`, `sudo`, `bash -c`).
- **Problema:** la traza real de esta feature tiene un despacho real que el medidor —con la mejora PD-9 activada por bandera—reporta como `absent` con causa. El oráculo T5 (5 casos, `tests/test_005_007_t5…:534-832`) cubre invocación desnuda, mención, `--help`, identidad neutral y declaración del conjunto; **no cubre la clase de envoltura** — que no es hipotética: es la práctica registrada del repo (`nohup bash -c`).
- **Consecuencia y juicio pedido explícitamente:** el uso previsto de PD-9/PD-11/AC-7 es que **la aceptación se mida con el medidor** («el medidor detecte el despacho por sí solo», `spec.md:70,102`). Hoy ese hito **no es observable en una traza real tipo** de este repo: el instrumento no distingue «no ocurrió» de «ocurrió y no se reconoce» en la clase que domina la práctica. No bloquea el camino del ciclo (open-unit/materialización/validador, verificados), pero sí **la evidencia de aceptación** (AC-7) y el uso previsto del propio delta 3. Por el criterio del 2026-10-12 (`execution.md:51-52`: un «ausencia que no distingue» es bloqueable) y dado que el disparador de la deuda propia (`D-4`/D-2: «sólo si se observa un falso negativo real») **ya se disparó**, juzgo: **BLOQUEA la medición de aceptación; se corrige ya** (es un cambio pequeño y con su oráculo), o el orquestador/dueño lo baja explícitamente a deuda priorizada con esa decisión registrada — no queda bien dejarlo solo como D-2 abierta tras haberse cumplido su propia condición de cierre.
- **Sugerencia:** en `_segment_program`/`_find_dispatch_delegation`, resolver el programa **dentro** de los prefijos de envoltura declarados (`env`, `time`, `nohup`, `nice`, `sudo`, `bash -c`/`sh -c` con su argumento citado), manteniendo el método y la provendable de la entrada `cdad_delegate.py` (misma clase de hecho material, ahora por resolución recursiva del segmento); actualizar la sección «Honest limit» de `context-meter.md:186-204`.
- **Condición de cierre verificable:** (1) caso focal nuevo en T5: traza fixture con `nohup bash -c "python3 …cdad_delegate.py --project-root . …"` → `first_dispatch: observed` con `method` declarado; (2) re-medición de la sesión real (`<ses-320>` con su `store_ref`) → `first_dispatch observed` (el despacho ya está demostrado materialmente por el ledger); (3) la identidad neutral sin bandera sigue byte-idéntica (control INV-5 del oráculo en verde).
- **Verdict: BLOCKING** · **Bucket: h** (misma base de puntos).

## Optionals

### O1 — Declaración codificada ≠ comportamiento: la referencia exige «delegation arguments» que el código no comprueba

- **Ubicación:** `skills/cdad-cycle/references/context-meter.md:178-183` («The delegation arguments (`--project-root` / `--packet` / `--destination`) accompany the invocation») y la cadena `provenance` en `cdad_context_meter.py:153-159` («(with its delegation arguments)»); código `cdad_context_meter.py:936-961` (`_delegation_call_kind`): solo comprueba programa + exclusión de ayuda, **nunca los argumentos**.
- **Problema/consecuencia:** el «conjunto reconocido y su método» que el registro declara (PD-9) es más estricto en la documentación que en el código: `python3 cdad_delegate.py --version` cuenta como despacho (invocación real sin ayuda) aunque no declare argumentos de delegación. Un consumidor que modela el conjunto declarado erra la lectura; el límite «publicado que no se cumple» del criterio del dueño, en versión menor.
- **Sugerencia:** alinear un lado: o el detector exige la clase de argumentos declarada, o la referencia/provenance baja la cláusula a descripción típica. Sin número de casos impone el dueño.
- **Condición de cierre:** caso descripto en el oráculo (invocación sin argumentos de delegación) con el comportamiento fijado por la decisión alineada; refencia y provenance idénticas al comportamiento implementado.
- **Verdict: OPTIONAL** · **Bucket: h**

### O2 — La declaración de dependencias de obs-2 (open-unit) es efimera: solo stdout

- **Ubicación:** `skills/cdad-cycle/scripts/cdad_packet.py:3661-3686` (`_check_open_unit_dependencies` devuelve el texto), `:3727-3735` (se imprime por `sys.stdout` en `open_unit`); nada del binding/`execution.json` ni del state registra «verified as done» vs «not verified».
- **Problema/consecuencia:** obs 2 de la revisión Claude quedó **bien resuelta** en el rechazo (dependencia declarada no `done` → rc≠0, cubierto por T3 `test_obs2_declared_dependencies_verified_or_declared`) y en el decir «dependencies not verified» cuando no hay declaradas; pero ese «decir» vive solo en la salida del comando y no es consultable después: una auditoría posterior no puede distinguir cómo se abrió la unidad.
- **Sugerencia:** persistir la nota (p. ej. en la entrada `epic_features` al abrir o en el `execution.json`: `depends_on_note: verified-as-done | undeclared-not-verified`), o declarar explícitamente que la declaración es efimera por diseño.
- **Condición de cierre:** después de un `open-unit`, el artefacto persistente muestra el modo de verificación de dependencias; o el contrato lo declara efimero.
- **Verdict: OPTIONAL** · **Bucket: h**

### O3 — La superficie `--delegation-dispatch` no está nombrada por el contrato aprobado (defecto de oráculo declarado N.º 3)

- **Ubicación:** `spec.md:66` (PD-9 no nombra el flag); oráculo `tests/test_005_007_t5…:16-19,101` fija el literal; registro del hecho: `acceptance.md:97` y `debt.md` D-8.
- **Problema/consecuencia:** el oráculo sobre-especifica una bandera que el contrato no fija. Mitigación real: la **referencia del producto** declara el flag (`context-meter.md:18-24`) y el docstring del CLI (superficie observable declarada), así que el oráculo pina la superficie declarada del producto, no un detalle de implementación. Es bajo-impacto hoy, pero crea la clase de acoplamiento que D-8 pide evitar a futuro.
- **Sugerencia:** corrección menor de contrato por el dueño (nombrar la bandera en PD-9 o en §2) o una declaración de aceptación que fijó la superficie transferable.
- **Condición de cierre:** el contrato nombra el elemento de superficie o un registro de aceptación/aclaración modifica prevaleciente.
- **Verdict: OPTIONAL** · **Bucket: h**

### O4 — Pequeña redundancia de formato en la plantilla de plan de feature

- **Ubicación:** `skills/cdad-cycle/assets/feature-plan-template.md:112-114` («A code task declares `focal_tests`; a code-less task declares `observable_checks`… every task declares `regressions`, `integration_gate` and `owner`») repite parcialmente la regla por valor que la plantilla misma declara consumida por referencia (`:74-76`).
- **Problema/consecuencia:** no reintroduce la regla `detail` (su semántica no se repite y el oráculo T1 `p5`/T6 `case4` verifica fuente única del conjunto cerrado), pero es la única parte que flota en dirección de una segunda enunciación de obligasiones por tarea.
- **Sugerencia:** una línea más corta («per-value requirements: see the rule — one place»), o el estado confundido por el dueño.
- **Condición de cierre:** la plantilla no contenga ninguna afirmación por valor sobre qué exige `"next"`/`"planned"`, solo la referencia.
- **Verdict: OPTIONAL** · **Bucket: h**

## Abstenciones

1. **RED estrictos por aserción sin la implementación (re-ejecución):** verifiqué la cadena (RED commits solo-tests; testfix del test-writer en sesión aislada; `feat:` de implementer sin GREEN no validado; los oráculos finales ejercitan los casos de contrato: T2 `pd2_planned_missing_progressive_field…`/`detail_outside…`/`mechanical_apply`, T5 `mention/help/neutral-identity/declaration`) y los artefactos `t*-red.md` declaran conteos por `AssertionError`. No volví a ejecutar los RED pre-implementación (requeriría worktree al HEAD sin implementación; as read-only no creo worktrees: mutan `.git`). Verificación parcial, no total — **ABSTAIN sobre la re-ejecución**, con la cadena como evidencia complementaria.
2. **Suite completa (871 passed / 9 skipped / 4 failed + 6 errors) re-ejecución:** no la corre (15 min, y la política la asigna a quien cierra). Verificación parcial: la firma F011 es idéntica base↔HEAD con mi propio like-for-like en archivos extraídos idénticos (evidencia #5), y `make validate` re-corrido = 141/2 F011 exacto. **ABSTAIN** sobre la igualdad byte-a-byte del conjunto completo de fallos declarado por el más prójimo que ejecuta la suite.

## Juicios pedidos explícitamente (defectos de oráculo / revisiones Claude)

- **T2 fixture:** el oráculo final prueba de verdad PD-1 — el helper `planned_task` con `None` → omite el campo de verdad (`:124-146`) y el negativo corre sobre omitido real. Proceso correcto: testfix del test-writer en sesión aislada + GREEN del implementer posterior; sin GREEN no validado commiteado (`acceptance.md:26-31`, commits `09567cd`/`7d683c9`). Sin hallazgo.
- **T5 helper:** el oráculo final pasa la **entrada de sesión** (`doc["sessions"][0]`, `:549-560,909`) a un helper que señala `session` — la clase de defecto original (documento completo) está despejada: los 3 casos ejercitan el contrato, no el helper. Proceso de fix-loop correcto y registrado (`cb78079` con gate NO satisfecho antes del commit de implementer — el orden correcto). Sin hallazgo.
- **Obs 1 Claude (draft como UNA parte):** bien tratada — T4 no fingió la partición; el límite quedó en `debt.md` D-4 con condición de cierre («partes por artefacto o multi-parte, sin hacer pasar la parte única como spec»). Sin hallazgo.
- **Obs 2 Claude (dependencias en open-unit):** implementada — verifica las declaradas y rechaza si no están `done` (`cdad_packet.py:3661-3686`), y **declara que no verifica** las no declaradas; queda la mejora de durabilidad (O2). Sin hallazgo bloqueante.
- **Obs 3 Claude (cierre manual):** bien tratada — medida en `acceptance.md §2` (19 operaciones de estado) y en deuda D-3 con condición de cierre simétrica a `open-unit`. Sin hallazgo.

## Resumen

**2 blocking, 4 optional, 2 abstenciones.**

- La etapa 3 está limpia y trazable: 7 unidades RED→GREEN con commits de rol escobados a scope, oráculos 37 passed re-corridos por mí, `make validate` 141/2 F011 preexistente, familia F011 de la suite verificada idéntica base↔HEAD por my propia extracción like-for-like, fuente única honorable en regla/format/contadores/plantillas.
- Los dos blockings son pequeños, observables y con condición de cierre precisa: el hueco de enforcement de `depends_on` en las tareas `planned` (B1 — probe reproducible de una línea) y el falso negativo del medidor en la clase de invocación envuelta que es la práctica real del repo (B2 — juzgado bloqueante para la evidencia de aceptación; su deuda ya cumplió su propio disparador de cierre).
- No apruebo ni priorizo: el dictamen de cierre lo emite el orquestador/dueño con este informe más los de los otros roles.

---

## Disposición del orquestador (HITL delegada epic-005, criterio vigente 2026-10-12)

- **B1 — CORREGIDO YA.** `depends_on` (clave presente, lista; `[]` válido) y `objective` no vacío **para la tarea `planned`**, acotado al alcance que esta review declara (INV-5 intacto). Cadena: RED `2cd13a6` (encargo amplio) → el implementer probó la contradicción con PD-2/INV-5 y **no la rompió** (correcto, anti-gaming) → adjudicación del orquestador → testfix `e3375e4` (oráculo acotado) → fix `282c70a`. Verificado: review-fix + T2 + regresiones de área **24 passed**.
- **B2 — CORREGIDO YA.** El medidor resuelve la invocación envuelta (`time`/`env`/`nohup`/`nice`/`timeout`/`shell -c`). Commit `a86278e`. Verificado con el oráculo de review-fix y los oráculos de T5/T3/T6/T7.
- **O1..O4 y las 2 abstenciones — A DEUDA** con condición de cierre en `debt.md` (D-2, D-4, D-8 y las O*). La deuda no relaja ningún gate: la medición desplegada (D-1) sigue **BLOQUEO** del dueño.
- **Contradicción de contrato declarada** (PD-1 «toda tarea» vs PD-2/INV-5 «sin marcador idéntico a hoy»): resuelta **sin cambiar el contrato aprobado** acotando el fix al alcance de esta review. Queda anotada para el cierre del epic como observación de redacción de PD-1 (no bloquea la feature).
