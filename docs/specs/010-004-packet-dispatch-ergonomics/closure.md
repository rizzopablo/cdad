# Cierre — 010-004-packet-dispatch-ergonomics

**Fecha:** 2026-10-31 (UTC del entorno).
**Autor:** orquestador CDAD (mandato HITL vigente: `docs/epics/epic-010-documentary-specialization/execution.md`). Documento del ámbito documental del orquestador, no trabajo de rol.
**Contrato:** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`, SHA-256 `3dcfc5ec7ddc33e473c66606525482f15b32ef5a9e9feda50e917140f27603e2` (pin vigente; re-pin tras la enmienda de saneamiento, §11).
**Plan:** `docs/specs/010-004-packet-dispatch-ergonomics/plan.md`, SHA-256 `2ae8ada32b164e5a5f72b5d791b7bb82dbb072f34b862885109d2c6026db6685` (pin verificado).
**Commit medido por el intento de cierre:** `daace66767e4c1a387cf5d69eafb864a270dfec9`.
**Base:** reverificación T6 (`review-verification.md`, attempt 34): B1–B4 **CERRADOS**, sin bloqueantes nuevos; R-A y R-B (requeridos no bloqueantes) resueltos en `review-fix-rar-b.md` (attempt 35, commits `28991b4a` y `6869301f`).
**Este documento declara el cierre técnico de la unidad y sus límites. No aprueba nada: la aprobación es del owner.**

## 1. Alcance de la unidad

`spec.md` §3. **Dentro:** contexto explícito (localizador v2 canónico) en request y cabecera de toda publicación nueva; ejecución v2 obligatoria para preparación nueva (incluidos sucesores y recuperaciones que publiquen generación nueva); eliminación de la selección implícita v1 sin policy; resolución compartida del localizador en `render`, `validate-request` y `validate-packet`; emisión de ruta C v2-only desde `render`; checks compartidos de dominio/identidad/schema y de ruta en las superficies indicadas; conservación del reconocimiento, validación, render y reentrada históricos; instrucciones de intake, despacho, handoff, preparación y re-entry; fuentes y derivados de OpenCode y Claude Code; verificación de un consumidor instalado aislado.

**Fuera (no se hizo):** opciones/resolución de `cdad_result.py`; rediseño de la selección de ejecución de `prepare` más allá de impedir publicación nueva v1 y declarar el localizador; ampliar a v1 el resolvedor por identidad; transporte externo y sus recibos; conectores o interceptores nativos; ledgers, recibos o protocolos paralelos; certificación automática de fidelidad semántica; modelos, permisos, separación de roles o autoridad; migración automática v1→v2 o reescritura de archivos históricos; actualización de la instalación global, push o publicación.

Superficies tocadas por la unidad: `skills/cdad-cycle/scripts/cdad_packet.py` y su wrapper, `sources/roles/{architect,orchestrator}.md`, `sources/agents/adapters/{opencode,claude-code}.md`, `skills/cdad-cycle/references/{handoff-prompts,project-execution,re-entry,project-start}.md`, agentes derivados de los cuatro árboles, y `tests/**`.

## 2. Las 12 postcondiciones y su evidencia

Clase de acreditación: **TEST** = verificada por una ejecución real de test; **REVISIÓN** = verificada por lectura y dictamen del reviewer independiente (Stage 4), no por test. La distinción se mantiene explícita: una prueba de texto no acredita conducta de un modelo (`spec.md:466`, R3).

| PC | Promesa (resumen) | Evidencia | Clase |
|---|---|---|---|
| **PC-01** | `render --route C` emite solo declaración + identificación deterministas y concordantes; sin efectos; request histórico sin localizador conserva el argumento explícito | `tests/test_010_004_t3_red.py` (`test_pc01_…exact_identification`); `tests/test_010_004_t5_e2e.py`; `tests/test_010_004_t5_properties.py` (INV-05) | TEST |
| **PC-02** | C rechaza contexto v1, request no publicado, contexto no canónico y paquete divergente, con diagnóstico y sin identificación ni efectos | `tests/test_010_004_t3_red.py` (4 negativos); `tests/test_010_004_t5_properties.py` (INV-04: admisión fallida nunca elige otro paquete); `tests/test_010_004_t5_e2e.py` | TEST |
| **PC-03** | Intake y despacho exigen v2 para C y validación íntegra del paquete antes de trabajar; admiten C sin cuerpo; rechazan mezcla A+C, identificación ambigua y cuerpo parcial; no permiten cambiar de paquete/ruta/scope para rescatar un rechazo | `sources/roles/architect.md:15-61` (intake, B1 cerrado) + derivados; `sources/roles/orchestrator.md:63-73`; `tests/test_010_004_t6_b1_guard.py` (guarda de tokens, fuente y 20 derivados); `tests/test_010_004_t4_red.py` (guarda de superficie de despacho) | TEST (token) + **REVISIÓN** (semántica: B1 cerrado, `review-verification.md`) |
| **PC-04** | Toda preparación nueva usa v2 y declara su localizador en request y cabecera; se rechazan selecciones v1 explícitas/implícitas y ubicaciones v2 incompatibles antes de publicar; el sucesor declara el campo aunque el predecesor no | `tests/test_010_004_t2_red.py` (`pc04a`…); `tests/test_010_004_t6_red.py` (`test_b4_replace_successor_declares_locator_over_historical_predecessor`, B4 cerrado); migraciones `tests/test_004_002_t6_landing.py`, `tests/test_packet_prepare.py`; `tests/test_010_004_t5_e2e.py` | TEST |
| **PC-05** | `render`, `validate-request` y `validate-packet` cumplen la matriz completa de §4.1; request histórico sin argumento explícito se rechaza, sin fallback por identidad | `tests/test_010_004_t2_red.py` (`pc05a` y matriz) | TEST |
| **PC-06** | Checks compartidos rechazan localizadores fuera de dominio o discordantes con identidad/schema; los tres CLI rechazan un argumento explícito que discrepa, sin probar otra ubicación; no se introduce la comparación en otros consumidores | `tests/test_010_004_t2_red.py` (`pc06a`, `pc06b`) | TEST |
| **PC-07** | Con raíz explícita y argumentos válidos desde otro directorio, el localizador resuelve el mismo contexto; el request histórico sin campo conserva su uso y no gana metadatos ni reescritura | `tests/test_010_004_t2_red.py` (`pc07a`, `pc07c`) | TEST |
| **PC-07b** | Retomar un proyecto v1 distingue recuperación histórica de encargo nuevo, remite al bootstrap v2 y explicita policy/autoridad/aprobación; ante un paquete v1 activo no terminal diagnostica el bloqueo y escala al owner, sin preparar v1 ni tocar state; distingue replay `--resume-packet` de las vías v1 y de una publicación nueva | `tests/test_010_004_t6_red.py` (`test_b2_active_v1_packet_is_diagnosed_and_escalated_without_effects`, caso `prepared`); `project-execution.md:110-127`; `project-start.md` (puntero añadido, R-B); caso `dispatched` probado por el reviewer con árbol idéntico (`review-verification.md`, tabla B2) | TEST (`prepared`) + **REVISIÓN** (`dispatched`, sin test de repo; R-B cerrado) |
| **PC-08a** | Los verificadores aceptan el paquete canónico completo y rechazan divergencia del cuerpo con cabecera intacta, sin normalizar bytes; se conserva la diferencia de preámbulo | `tests/test_010_004_t3_red.py` (tampered body, CRLF); `tests/test_role_packet_render.py`/`test_role_packet_review_regressions.py` (reutilizados, verdes); `tests/test_010_004_t5_properties.py` (INV-05, 100 mutaciones sembradas) | TEST |
| **PC-08b** | El intake común y sus salidas derivadas afirman que el cierre JSON no termina el paquete y que la comparación abarca instrucciones y cuerpo; su revisión no acredita conducta real | `sources/roles/architect.md:19-55`; derivados de los cuatro árboles; `tests/test_010_004_t4_red.py` (token) | TEST (token) + **REVISIÓN** (texto; no acredita obediencia) |
| **PC-09** | Los diagnósticos distinguen las causas de §4.5, ofrecen siguiente acción y referencia segura, sin divulgar el cuerpo ni cambiar semánticas de salida | `tests/test_010_004_t3_red.py` (aserciones dentro de los negativos de C); `tests/test_010_004_t6_red.py` (diagnóstico B2 que nombra el bloqueo y escala) | TEST |
| **PC-10** | El procedimiento de reporte/re-entry distingue integridad publicada, observabilidad de entrega y fidelidad del resultado; no presenta archivo, stdin, literal reconstruido ni recibo como prueba independiente del prompt recibido | `skills/cdad-cycle/references/re-entry.md`, sección «Integrity, observability and fidelity» (tabla de cinco evidencias) — B3 cerrado | **REVISIÓN** (sin test: es texto) |
| **PC-11** | Se conservan I-4 e I-5: la falta de observabilidad no obliga por sí sola a repetir; sí se mantiene el rechazo ante divergencia comprobada o autoridad inválida y el hallazgo ante resultado infiel; un inline alterado no se rescata por C; la recuperación es un nuevo encargo v2 con sus gates | `re-entry.md` (reglas I-4 e I-5) — B3 cerrado; `handoff-prompts.md:25-27`; `sources/roles/orchestrator.md:158` | **REVISIÓN** (sin test: es texto) |
| **PC-12** | Fuentes, agentes regenerados, ambos adaptadores, handoff y referencias describen consistentemente las interfaces y fronteras; un consumidor instalado aislado puede preparar v2, emitir C y resolver/validar su contexto sin tocar la instalación global | `tests/test_010_004_t4_red.py` (2 guardas de derivados); `tests/test_cdad_generate.py` (regeneración determinista); `tests/test_010_004_t5_e2e.py` (recorrido del consumidor instalado aislado); `tests/test_010_004_t5_properties.py` | TEST |

**Corrección de traza ya registrada.** La tabla original de `t4-closure.md` §3 se conserva como registro histórico; su corrección fechada (`t4-closure.md` §3.1) marcó PC-03, PC-07b, PC-10 y PC-11 como **no acreditadas** por las líneas que citaban. Esta tabla parte de esa corrección y de los cierres de B1–B4 verificados por el reviewer; no reescribe la traza corregida.

## 3. Invariantes INV-01..INV-12

| INV | Enunciado (resumen) | Dónde se acredita |
|---|---|---|
| **INV-01** | un paquete = un rol y una subfase; no acumula permisos | Suite completa: `tests/test_role_packets.py` (identidad rol/subfase) + validación de identidad de `receive` en cada recepción de la unidad. En repo cumple; la copia instalada sigue combinando subfases (**R1**). |
| **INV-02** | identidad, estado, contrato, aprobación, política y binding siguen validándose | Tests T2/T3 (`validate-request`/`validate-packet` sobre paquetes publicados) + suite de recepción; revisión por lectura (`review.md`, fila INV-02). |
| **INV-03** | el localizador no crea autoridad alternativa al contexto canónico | `tests/test_010_004_t3_red.py` (`non_canonical_context_copy`); `tests/test_010_004_t2_red.py` (matriz de §4.1). |
| **INV-04** | ninguna ruta permite elegir otro paquete tras fallar la admisión | `tests/test_010_004_t5_properties.py::test_inv04_failed_admission_never_emits_another_packet_identification` (100 escenarios sembrados). |
| **INV-05** | igualdad completa ≠ igualdad de cabecera ≠ semejanza semántica | `tests/test_010_004_t5_properties.py::test_inv05_…` (100 mutaciones) + `tests/test_010_004_t3_red.py` (divergencia de cuerpo) + `test_role_packet_render`/`review_regressions` (CRLF). |
| **INV-06** | las lecturas de control-plane no amplían acceso al producto | Revisión por lectura (`review.md`, fila INV-06): el diff no toca policy ni guards. **Límite:** sin enforcement mecánico (PD-15), e **I-8** documenta el caso inverso (el rol no puede leer su propia instrucción). |
| **INV-07** | no se añaden protocolos, registros, recibos o conectores paralelos | Revisión por lectura (`review.md`, fila INV-07): el diff no añade ledgers ni conectores; `re-entry.md` cita `delivery` (007-004 §6.2) sin reescribirlo. |
| **INV-08** | no hay conversión, reescritura ni adopción silenciosa de históricos; su reconocimiento no habilita preparación nueva v1 | `tests/test_010_004_t2_red.py` (`pc07c`, rechazos v1); `tests/test_010_004_t6_red.py` (v1 activo). |
| **INV-09** | recepción o evidencia de transporte no implican aprobación semántica | `re-entry.md` + suite de recepción (`tests/test_003_002_t1_receive.py`, `test_003_002_t3_reviewfix.py`); todos los recibos de la unidad quedaron `semantic_status: pending`. |
| **INV-10** | los derivados se regeneran desde fuentes | `tests/test_cdad_generate.py` (determinismo) + `tests/test_010_004_t4_red.py` (supervivencia del token en los cuatro árboles de derivados). |
| **INV-11** | los rechazos nuevos ocurren antes de publicación o efectos persistentes | `tests/test_010_004_t2_red.py` (aserciones de árbol y state sin cambios); prueba propia del reviewer con árbol idéntico (`review-verification.md`, tabla B2). |
| **INV-12** | toda publicación nueva usa v2 y declara su localizador; C solo representa paquetes con contexto canónico v2 | `tests/test_010_004_t2_red.py` (`pc04a`), `tests/test_010_004_t3_red.py` (C v2-only), `tests/test_010_004_t6_red.py` (sucesor con localizador, B4). No rige en la instalación (**R1**). |

No se inventaron propiedades para invariantes ya cubiertos (`properties-t5.md`): las propiedades sembradas cubren INV-04 e INV-05, que era donde faltaba cobertura de región (cabecera y bytes posteriores al cierre JSON).

## 4. Tests del feature — 7 archivos y su conteo

Conteo de funciones de test en el intento de cierre. Los conteos por archivo son los del intento `attempt-20261031T035714924428Z-3385202-2939fdeb`; el total de la selección focal del feature más la guarda de derivados se informa al final de la tabla.

| Archivo | Qué cubre | Tests |
|---|---|---|
| `tests/test_010_004_t2_red.py` | PC-04, PC-05, PC-06, PC-07, PC-08a (matriz de localizador y rechazos) | 6 |
| `tests/test_010_004_t3_red.py` | PC-01, PC-02, PC-08a, PC-09, PC-12 (emisión C y sus negativos) | 7 |
| `tests/test_010_004_t4_red.py` | PC-03, PC-12 (guarda de superficies de despacho y derivados) | 2 |
| `tests/test_010_004_t5_properties.py` | INV-04, INV-05 (propiedades sembradas; PC-01/02/08a) | 2 |
| `tests/test_010_004_t5_e2e.py` | PC-01, PC-02, PC-05, PC-12 (consumidor instalado aislado) | 2 |
| `tests/test_010_004_t6_red.py` | B2 (v1 activo) y B4 (localizador del sucesor) | 2 |
| `tests/test_010_004_t6_b1_guard.py` | B1 (intake C/v2 y rechazo A+C en fuente y 20 derivados) | 1 |
| **Total del feature** | | **22** |

Los 22 del feature más `tests/test_cdad_generate.py` (10) = **32** cubiertos en el intento de cierre, todos verdes. La **selección focal** usada en las verificaciones de T6 (`t6_red`, `t6_b1_guard`, `t2_red`, `t3_red`, `t4_red`, `t5_e2e` + `test_cdad_generate.py`) da **30 passed in 43.62s**: excluye a propósito `tests/test_010_004_t5_properties.py` (2), cuyas propiedades se verificaron en su propio gate (`properties-t5.md`: `2 passed`) y vuelven a estar verdes en el intento de cierre. La diferencia 30/32 se declara para que ninguna cifra se lea como cobertura distinta de la que es.

## 5. Incidentes I-1..I-8 y su disposición

Fuente: `docs/epics/epic-010-documentary-specialization/observations-packet-dispatch.md`.

| Incidente | Disposición |
|---|---|
| **I-1** — pérdida de backticks al transcribir el paquete a mano | **Resuelto en la unidad**: ruta C (`render --route C`) como vehículo que no retranscribe el cuerpo; PC-01/PC-03 y guarda `t4_red`. |
| **I-2** — el cierre del bloque JSON se leyó como fin del paquete | **Resuelto en la unidad**: el intake declara que la comparación va desde el marcador hasta el fin (PC-08b, `architect.md`); acreditado por test de token y por revisión. |
| **I-3** — el contexto de ejecución se infiere | **Resuelto en la unidad**: el request y la cabecera declaran el localizador canónico v2 (PC-04, PC-05, PC-07). |
| **I-4** — verificación de entrega no observable y bloqueo desproporcionado | **Resuelto como contrato de procedimiento**: `re-entry.md` distingue las cinco evidencias y las reglas I-4/I-5 (PC-10/PC-11, B3); no se promete observabilidad que el runtime no expone (PD-15). |
| **I-5** — divergencia real en un despacho reviewer (inline alterado) | **Resuelto como contrato de procedimiento**: divergencia comprobada → rechazo; C no rescata un inline alterado; recuperación por nuevo encargo v2 (PC-11, B3). |
| **I-6** — paquete nuevo publicado sin localizador y rechazado en el gate del padre | **Resuelto en la unidad**: toda publicación nueva usa v2 y declara localizador (PC-04, INV-12). La **clase** sigue abierta por R2 (ver §7 y backlog de la épica). |
| **I-7** — `request_sha256` fabricado en el despacho (paquete válido, metadato corrupto) | **Declarado como límite de vehículo**: ningún validador del paquete lo detecta; la lección (construir el bloque con `render --route C` verbatim) quedó en las observaciones y en el despacho de la unidad. Sin guarda mecánica propia. |
| **I-8** — el test-writer no puede leer sus propios `instruction_sources` | **Encolado en el backlog de la épica**: defecto de diseño de scopes, fuera de alcance de esta unidad; tres salidas registradas, sin unidad asignada. |

## 6. Desviaciones de proceso

Se registran porque ocurrieron; ninguna se presenta como acierto ni se oculta.

1. **El AUDIT submidió el universo de fixtures.** `test-audit.md` §1.1 nombró 2 expectativas sustituidas y §1.2 unas pocas «vigentes que comparten fixtures»; la medición real posterior (`fixture-impact-inventory.md` §0) encontró **105 archivos** en el universo y **64 fallos** en **15 archivos** (62 de la clase C1, 1 C2, 1 C3). La corrección no reabrió el AUDIT: el inventario medido pasó a ser la lista de trabajo.
2. **Alcance estrecho de un encargo.** El encargo del POST-AUDIT correctivo `-004` acotó los cambios de aserción a **una sola celda** (`_cell_legacy`), y dejó fuera tres oráculos legítimos de `tests/test_packet_prepare.py` (63 → 3 fallos residuales). Defecto del **orquestador que redactó el encargo**, no del rol, que respetó la cota y reportó los tres. Corregido en `scope-correction-residual-oracles.md` con unidad propia.
3. **Recibo del attempt 32 con la confirmación en vez del informe.** Lo staged y recibido fueron **2.811 B** del mensaje de confirmación del commit, no el informe sustantivo. El recibo (`5c5293e8…`) acredita la entrega y la identidad del intento, **no el contenido íntegro**. El informe sustantivo se restituyó como `review-fix-t6-report.md` con procedencia declarada, sin reescribir el recibo, el asiento del ledger ni el artefacto materializado. El dictamen de T6 no dependió de ese informe: el reviewer verificó el diff directamente.
4. **`record` sin sesión acreditada en dos intentos.** En `plan-materialization-2026-10-30.md` (attempt 11) y en `orchestration-review-v2-decision-pending.md` (reviewer plan-review-003) el runtime no acreditó la correlación de sesión (faltaban parent/moment) y no se inventaron esos datos; la recepción validó identidad y paquete, no la procedencia de sesión.

## 7. Límites declarados

**R1 — formulación literal.** **La unidad queda cerrada en el repositorio, NO vigente en la instalación.** El despacho real requiere la toolchain del repositorio (`skills/cdad-cycle/scripts/…` y sus envoltorios `scripts/`) hasta que el owner decida publicar. Mientras el owner no lo decida, ninguna afirmación de vigencia en el CLI instalado puede sostener un cierre, un despacho ni una verificación de aceptación.

Hasheos **re-medidos después del fix R-A** (la tabla de `closure-conditions.md` §1 era previa):

| Fuente | `cdad_packet.py` sha256 |
|---|---|
| Repo (árbol medido, `daace667`) | `d62278a15f930674bf4eb8fce8e45eb6d79502297c488d1da8d383c3062167df` |
| Instalación `~/.config/opencode` | `171fcd1413ec8446272564388fe2165716569e6c3c070f02f4dca8008960e679` |
| Instalación `~/.agents` | `171fcd1413ec8446272564388fe2165716569e6c3c070f02f4dca8008960e679` |
| Instalación `~/.claude` | `171fcd1413ec8446272564388fe2165716569e6c3c070f02f4dca8008960e679` |

Valor previo al fix R-A del mismo archivo en el repo: `3c0aca3226b3f93f7e2b0a3d8bba5637c86c688b0d83139a8a53e25c18d334df`. **La decisión de publicar es del owner**; no es delegable al orquestador ni se fabrica por conveniencia de cierre.

**F011 — medido y declarado, no oculto.** `make validate` (`tests/validate-consistency.sh` + `tests/validate-odoo-specialization.sh`, comparación repo ↔ instalación global) sigue en ****182 PASS / 1 FAIL** (`rc=2`), con el único FAIL en **F011** (`scripts/validate-subagents.sh`, perfil activo)**. El drift es preexistente y ambiental: corregirlo exige publicar la instalación, acto que el mandato no autoriza. La condición de cierre es «declarado, medido y no oculto», no PASS. No se cierra debilitando la aserción, actualizando la instalación global ni retirando la comprobación.

**R3 — las guardas documentales no acreditan obediencia.** `tests/test_010_004_t4_red.py`, `tests/test_010_004_t6_b1_guard.py` y las comprobaciones de intake verifican **tokens estables** y su supervivencia en los derivados. No acreditan conducta de un modelo, recepción nativa ni cumplimiento en la práctica: la mutación por inversión semántica de B1 siguió en verde y el propio prompt de sesión del reviewer carecía del texto nuevo de intake (`review-verification.md`). Es el límite ya declarado; no se «arregla» congelando prosa (AP-14). La semántica es materia de la revisión independiente.

**Fidelidad del attempt 32.** El recibo acredita la entrega del paquete y la identidad del intento, **no el informe íntegro**; el informe sustantivo está en `review-fix-t6-report.md` y la declaración de procedencia sigue visible en su cabecera. Ver §6.3.

**Archivo no rastreado ajeno a la unidad.** `docs/specs/010-000-continuity-relative-root/discovery.md` permanece **untracked** y es **preexistente y ajeno** a esta unidad (evidencia de una unidad ya cerrada). El intento de cierre lo registra en `dirty`; no se borró, no se movió y no forma parte de esta unidad.

## 8. Evidencia del cierre

**Intento de cierre (suite completa, un solo intento completado):**

| Campo | Valor |
|---|---|
| Directorio de evidencia | `.cdad/evidence/010-004-closure/attempt-20261031T035714924428Z-3385202-2939fdeb/` |
| Selección | `--all` (1876 nodeids) |
| `commit` | `daace66767e4c1a387cf5d69eafb864a270dfec9` |
| `dirty` al iniciar | 1 |
| `rc` | 0 |
| `pytest_summary` | `1871 passed, 5 skipped in 3668.03s (1:01:08)` |
| `canary.delta_lines` | 0 |
| Artefactos | `stdout.log`, `stderr.log`, `canary-before.txt`, `canary-after.txt`, `attempt.json` |

Lectura: `rc=0` y `pytest_summary.verified=true`, sin `failed`, `errors` ni diagnóstico. Los 5 skips son integraciones preexistentes condicionadas por variables de entorno, todas fuera del feature (2 en `tests/test_005_002_t4_acceptance.py`, 1 en `tests/test_005_009_t4_acceptance.py`, 1 en `tests/test_005_010_t4_integration.py`, 1 en `tests/test_006_001_t3_integration.py`); ninguna cubre una postcondición de 010-004 y ninguna es un pase. `canary_delta_lines=0`: el intento no alteró el HOME real. Un intento previo de la misma invocación (`attempt-20261031T032648228484Z-3051942-569ce43e`) quedó **interrumpido** por el límite de tiempo de la herramienta del orquestador (63 % de la selección, `state: running`, sin `rc`): no es una medición de aceptación y no se usa como tal; se conserva en el mismo `evidence-root` como evidencia del corte.

**Mediciones del packet review-fix-003 (attempt 35), verificadas por el orquestador antes de recibirlo:**

- `git show --stat 28991b4a` → solo `skills/cdad-cycle/scripts/cdad_packet.py`, 8 líneas (5+/3−), **exclusivamente comentario** de `prepare()`.
- `git show --stat 6869301f` → solo `skills/cdad-cycle/references/project-start.md`, 1 línea añadida (puntero a `project-execution.md` §3).
- `ast.parse` del script: `AST_OK` (rc=0).
- Focales: `30 passed in 43.62s` (selección de 6 archivos del feature sin `t5_properties` + `tests/test_cdad_generate.py`, 20+10); start/intake: `26 passed in 0.55s`.
- Pins intactos: spec `fc6b2ccc…`, plan `2ae8ada3…`.

**Recibos de la unidad:** todos `semantic_status: pending`; recibir no aprobó ningún gate. El cierre de continuidad del intento 35 se verificó con `validate-receipt --close-continuity 35` (checkpoint `seq 71`, cuerpo `f1a84102…`).

## 9. Lo que este cierre NO declara

- **No declara vigencia en la instalación** (R1): la unidad está cerrada en el repositorio y la publicación es decisión pendiente del owner.
- **No declara F011 en PASS**: se declara medido, preexistente y no oculto.
- **No declara que las guardas documentales acrediten obediencia** (R3).
- **No declara fidelidad íntegra del recibo del attempt 32**: el informe sustantivo está restituido aparte.
- **No declara que todo estado viejo sea automáticamente ejecutable.**
- **No aprueba**: la aprobación del cierre y del Memory Bank es del owner; publicar es una decisión separada.

## 10. Publicación (2026-10-31)

**Decisión y procedencia.** El owner autorizó explícitamente publicar la instalación global, en la
misma autorización que aprobó el Memory Bank; la cita literal y su procedencia quedan registradas en
`docs/.cdad-state.json` (entrada `memory-approved`). Este apartado se agrega **después** del cierre y
**no reescribe** §7 ni §9: los conserva como registro de lo declarado antes de publicar y declara acá
qué cambió al ejecutarla. Donde §7 y §9 dicen «no vigente en la instalación» y «F011 no está en PASS»,
la lectura vigente es la de esta sección.

**Antes (medido: `bash install.sh --check`).** **rc=1**, `Check: FAIL`. `DRIFT` en **22/22 agentes
instalados** (11 por runtime; ninguno portaba el intake nuevo: `Route A and route C are exclusive` daba
0 coincidencias), en los cinco archivos de referencia de `skills/cdad-cycle`
(`re-entry.md`, `project-execution.md`, `handoff-prompts.md`, `project-start.md`,
`packets/substages/test-writer-post-audit.md`), en `cdad_packet.py` y `cdad_continuity.py`, y en los
`__pycache__` de los tres árboles.

**Publicación (`bash install.sh`, rc=0).** 390 archivos propios desplegados
(`OWNERSHIP summary: 390 owned file(s)`), agentes desde `build/staging` —verificado idéntico a una
generación fresca (`cdad-generate.py --runtime opencode|claude-code --stack odoo`; `diff -r` sin
diferencias)— y skills desde `skills/`. No hizo falta `--force` (no interviene en conflictos) y
`install.sh` no se modificó.

**Incoherencia preexistente resuelta, declarada.** El manifiesto previo (`source_version 6de69b6dd09c`,
0 conflictos declarados) no describía 12 destinos: 9 agentes de `~/.config/opencode/agents` con el
`model:` del usuario sobre un cuerpo anterior y 3 `__pycache__/*.pyc` recompilados localmente. El
instalador los reportó `CONFLICT … PRESERVED` (política 009-001: nunca sobrescribe). Resolución con el
**mismo** mecanismo del instalador: `scripts/agent-overlay.py merge <staged> <instalado> --out` para los
9 agentes (bytes de staging + el `model:` del usuario conservado verbatim) y retiro de los 3 directorios
`__pycache__` (caché derivada). Con eso el instalador reportó **0 conflictos**, registró 390 archivos y
no dejó `pending_removal`. Respaldo previo de los agentes instalados, del manifiesto y de `~/.agents`:
`.cdad/local/deploy-backup-20261031/`.

**Después (medido).** `bash install.sh --check`: **rc=0**, `Check: PASS (414 artifact groups in sync
with staging/skills)`, sostenido **después** de ejecutar el CLI instalado (dos mediciones). Manifiesto
resultante: 390 artefactos, 0 conflictos, 0 `pending_removal`, `runtime claude-code`, `stack odoo`.

**Hashes (repo vs instalado).** `cdad_packet.py`:

| Fuente | sha256 |
|---|---|
| Repo (`skills/cdad-cycle/scripts/`) | `d62278a15f930674bf4eb8fce8e45eb6d79502297c488d1da8d383c3062167df` |
| `~/.config/opencode` | `d62278a15f930674bf4eb8fce8e45eb6d79502297c488d1da8d383c3062167df` |
| `~/.agents` | `d62278a15f930674bf4eb8fce8e45eb6d79502297c488d1da8d383c3062167df` |
| `~/.claude` | `d62278a15f930674bf4eb8fce8e45eb6d79502297c488d1da8d383c3062167df` |

`references/re-entry.md`: `2e506000a017ace94a80…`, idéntico en repo y `~/.config/opencode`.

**Capacidad nueva verificada en la copia instalada.** `cdad_packet.py render --help` declara
`[--route {C}]`; `render --route C` sobre el paquete publicado
`010-004-packet-dispatch-ergonomics-scribe-memory-001`, ejecutado con el CLI **instalado**, devuelve
**rc=0** con la declaración `Route C — explicit file backup` y el bloque JSON de 8 campos
(`project_root`, `packet_id`, `execution_id`, `execution_context`, `request`, `packet`, `contract`).
Los 10 agentes de rol instalados por runtime portan el token de intake
`Route A and route C are exclusive`; el orquestador instalado, en ambos runtimes, cita `--route C` dos
veces.

**`make validate`.** `tests/validate-consistency.sh`: **183 PASS / 0 FAIL**;
`tests/validate-odoo-specialization.sh`: **68 PASS / 0 FAIL**; total **rc=0**. **F011 pasa** en sus dos
aserciones (`validate-subagents.sh` perfil activo → PASS; `tests/validate-odoo-specialization.sh` →
PASS). La aserción no se tocó: el FAIL de §7 era el drift de la instalación y, publicado, la medición
cambia.

**Efecto sobre las deudas.** **D-1 queda RESUELTO**: la unidad está vigente en la instalación y los
hashes coinciden en los cuatro árboles. R-A, I-8 y R2 siguen abiertos y no se tocan. Nada de esto
publica el repositorio: **sin push**, porque la publicación del repo es otra decisión.

## 11. Enmienda de saneamiento (2026-10-31)

**Motivo.** El escaneo previo a la publicación bloqueó el push por datos identificables
introducidos por el delta (rutas absolutas del HOME local e ids de sesión crudos). Por decisión del
dueño se **sanea** el delta en lugar de excluirlo de la publicación.

**Contrato.** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`

- SHA-256 anterior: `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`
- SHA-256 nuevo: `3dcfc5ec7ddc33e473c66606525482f15b32ef5a9e9feda50e917140f27603e2`

**Qué cambió.** Una sola línea de `spec.md` (la que documenta las validaciones CLI ejecutadas): la
variable `R` dejó de nombrar la ruta absoluta del HOME del dueño y pasa a `<repo>`. Es un cambio
**cosmético de evidencia**: el comando, la afirmación y su resultado son los mismos.

**Qué NO cambia.** Ninguna promesa, postcondición, invariante, decisión, alcance ni criterio de
aceptación. La enmienda no reabre el contrato ni acredita trabajo nuevo; los digests históricos de
entrega (`054d4657…`, la versión revisada y aprobada) quedan como registro y no se reescriben.

**Re-pin.** Se registra en `stage_history` una transición `gate` (stage `specification`) con
`contract_path` y `contract_sha256` iguales a los bytes saneados: es el pin vigente que habilita a los
roles de construcción sobre el contrato actual. Los pines anteriores no se editan y dejan de habilitar
por digest, como corresponde a cualquier contrato que cambia después de aprobado.

**Este mismo documento.** El `closure_sha256` registrado en `stage_history` al cerrar la unidad
(`820b1a31bc1a5923c1ee7fdb7ee5b8c98ba466a9193bbf35bf4fb8637b42ee5c`) corresponde a la versión
registrada del cierre; esta sección se añade después del registro y no reescribe esa evidencia ni el
`transition_key` del cierre.
