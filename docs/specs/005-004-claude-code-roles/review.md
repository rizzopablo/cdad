# Review formal (etapa 4) — 005-004-claude-code-roles, construcción T1..T4

**Rol:** reviewer · **Paquete:** `005-004-claude-code-roles-reviewer-review-001`
**Contrato:** `docs/specs/005-004-claude-code-roles/spec.md` sha256 `5e11f2ef…` (verificado con `sha256sum`; coincide con el paquete) + `plan.md` sha256 `953e4ba5…` (idem). Alcance: diff de producto de T1..T4 (commits RED del test-writer y GREEN del implementer), sus focales y sus informes, contra PD-1..PD-5 y PD-9 y AC-1..AC-5, con el criterio de review vigente del 2026-10-12. T5 (PD-6..PD-11, AC-6..AC-8) NO entra: lo coordina el orquestador Claude con una sesión nueva de Claude Code (segunda enmienda). Modelo: glm-5.3-flash (mofgw), familia distinta del implementer, sesión independiente, sólo lectura.

---

## 0. Verificación propia (comandos y salida pegados)

| # | Qué | Comando | Resultado |
|---|---|---|---|
| V1 | Focales T1..T4 en HEAD | `python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py tests/test_005_004_t2_installer_claims.py tests/test_005_004_t3_version_check_cc.py tests/test_005_004_t4_cc_guard_decisions.py -q` | `29 passed in 16.44s` (7+8+8+6) |
| V2 | Validador del repo en HEAD | `bash tests/validate-consistency.sh` | `Assert PASS: 154 / Assert FAIL: 2` — sólo `F011: scripts/validate-subagents.sh` y `F011: tests/validate-odoo-specialization.sh` |
| V3 | ¿Los 2 FAIL son pre-existentes? | `git archive 2743a31` (commit previo al primer RED) extraído a `/tmp/opencode/rev005004-pre`; copiar —sin leer— `tests/.sensitive-patterns.local`; correr `bash tests/validate-consistency.sh` y `bash tests/validate-odoo-specialization.sh` ahí | ambos F011 (validate-subagents FAIL con perfil `basic`/ADR-007; validate-odoo-specialization FAIL A3 con el mismo files-set, **sin ningún archivo de la feature** en la lista; los archivos señalados — `docs/specs/005-007…/closure.md`, `005-010/…`, `004-003/…`, `execution.md`, `activeContext.md`, `__pycache__`, `test_role_packets.py`, `005_009…` — son idénticos pre/HEAD, verificado con `diff -r` de todo `docs/`: sólo difieren los 4 documentos propios de la feature. **Delta = 0; deuda D-6 de la spec, no delta de 005-004.** Nota honesta de método: sin el patrón local, el A3 queda vacuo en el árbol extraído; el reproduce del files-set la declara.)
| V4 | GREENs no tocaron `tests/` | `git show --name-status` de cc6e5a5, 96786de, b05c5c1, 65a0de9 | 0 rutas `tests/` en los 4 GREEN |
| V5 | Focales no relajados post-RED | `git log --oneline -- <cada focal>` | cada focal tiene un solo commit (34703b6, 0964694, 4828c0c, 0cdec77) y nunca volvió a tocarse (verificado por separado para los 4 focales y para `tests/validate-consistency.sh`); el diff de todos los focales RED→HEAD es de **sólo agregados** (2092 líneas): `git diff --stat 34703b6^..HEAD -- tests/…` (`2092 insertions(+), 0 deletions`) |
| V6 | Diff de producto T1..T4 acotado | `git diff --name-status 2743a31..HEAD -- agents scripts sources skills install.sh` | 6 archivos, todos dentro de las fichas: `agents/claude-code/cdad-orchestrator.md`, `scripts/cdad-generate.py`, `sources/agents/adapters/claude-code.md`, `skills/cdad-cycle/references/claude-code-delegation.md` (última línea es la validación del bloque), `skills/cdad-cycle/references/project-start.md`, `skills/cdad-cycle/scripts/cdad-version-check.py` |
| V7 | `strip` en superficies declaradas | `grep -rn -i "strip" sources/ skills/ install.sh` | sólo y exclusivamente llamadas a `.strip()` de código Python/shell (procedencia de cadenas); **0 afirmaciones ligadas al instalador/modelo**; el focal PD-2 con su predicado anti-negación da 0 offenders |
| V8 | orchestrator CC declara `Agent`; `Task` queda en el lado OpenCode | `grep -n "tools:" agents/claude-code/cdad-orchestrator.md`; `grep -n Task agents/claude-code/cdad-orchestrator.md` | `tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Skill` (línea 4); las 2 menciones de `Task` que quedan son en prosa del mecanismo (no en `tools:`), y el oráculo del focal T1 declara explícitamente que tales formas no cuentan en el plano de despacho (T1-red §45: `names_task_as_a_cc_tool()` documentada en el test) |
| V9 | Generador idempotente; derivados fiel a la fuente única | `python3 scripts/cdad-generate.py --runtime claude-code --stack odoo --profile optimus --out /tmp/opencode/gencheck` y `diff -rq /tmp/opencode/gencheck/agents/claude-code agents/claude-code` | byte-identical (INV-2/INV-4, no edición a mano de `agents/`) |
| V10 | T3: ruta del registro de activación (camino NO cubierto por el focal congelado) | construí mi propio fixture en `/tmp/opencode/ccprobe2` (proyecto con `activation.json` → `adopted_root` = raíz CC con `version.txt = 45a2b1c0`; lado OpenCode en el fixture con versión fuente `b1b1b1b1` pero sin marcador en su raíz, para que las patas OpenCode queden `no version.txt found` y la raíz CC quede inequívoca); ejecutar el checker del repo con `--project-root` | `claude-code: 45a2b1c0`, `agents`/`CLI` «no version.txt found» en el fixture, veredicto `UNKNOWN (rc 3)`, **la pata presta sólo la versión de la raíz CC** — INV-3/INV-7 ✓ |
| V11 | Perfil `basic`: el generador omite `model:` (caso PD-2/PD-5) | `python3 scripts/cdad-generate.py --runtime claude-code --stack odoo --profile basic --out /tmp/opencode/gencheck2` | 0/12 archivos CC con `model:` |
| V12 | Regresiones T1 re-corridas | `python3 -m pytest tests/test_packet_prepare.py tests/test_cdad_generate.py tests/test_003_006_t3_receive_wiring.py tests/test_003_007_t4_atomic_unit_rule.py -q` | `54 passed in 21.89s` |
| V13 | Regresiones T2/T3/T4 re-corridas | `python3 -m pytest tests/test_install_ownership.py tests/test_install_review5_regressions.py tests/test_005_008_t1_nested_tests.py tests/test_004_002_t5_runtime.py tests/test_005_006_t6_owner_reviewfix.py tests/test_005_003_t2_examples_execute.py -q` | `59 passed in 259.03s` |
| V14 | Anonimización (INV-5) en los 8 informes + revisión del orquestador | `grep -rn "<home>\|<home>/clawd" docs/specs/005-004-claude-code-roles/`; `…-E "ofap\|clawd"` id.; `…-E "ses-[0-9a-f]{6,}"…` | 0 rutas del dueño, 0 ids de sesión crudos (la única mención de la palabra `ofap` del grep de nombres de agentes es en `discovery.md:273` — listando nombres de agentes instalados, NO una ruta del dueño). El saneamiento del state ya había sido registrado (19633b8, con `<ses-…>`) |
| V15 | `git stash list` (restricción del plan §7) | `git stash list`; `git status --porcelain` | vacío; árbol limpio, sólo `M docs/.cdad-state.json` (registro del orquestador, no toca el write scope de los roles) |

---

## 1. Veredictos sobre los tres encargos del orquestador

### 1.1 Adjudicación del mapa de hooks de T4 — **correcta**

**Contexto verificado:**

1. PD-4 (y §9) designa como dueño del mapa **dos superficies** a la vez: el adaptador fuente y el generador (`CC_GUARDS`). El focal (congelado en RED) pidió exactamente eso: que las dos superficies declaren el mismo conjunto de pares (matcher, modo), con una aserción bidireccional — cada par que llevan los derivados declarado en ambas superficies, y ningún modo declarado sin derivado («huérfano») — en `test_pd4_generated_hook_map_matches_its_owner` (`tests/test_005_004_t4_cc_guard_decisions.py:414-493`). El propio T4-red §5 declaró abiertamente el riesgo de «segunda copia del contrato del guard» como condición de detención, y el GREEN lo resolvió sin copiar el guard.
2. La adjudicación del orquestador — que la reconciliación haga que el adaptador declare lo mismo que el generador ya emite (sin copiar el contrato del guard que sigue en el guard y en su clasificador), sin tocar el generador — se ejecutó así, en GREEN `65a0de9` (sólo los dos archivos de la tabla surface de adaptador + consumidor; `CC_GUARDS` impecable; el guard `scripts/claude-code-path-guard.sh` sin copias).

**Juicio — la adjudicación es correcta, con un matiz y un residual que van a opcionales:**

- **Fundamento:** PD-4 nombra dos superficies por contrato; pedir que la tabla del adaptador sea sustituida por una referencia pura requeriría una enmienda de contrato que no existe (la ficha T4 manda precisamente detener ahí). El GREEN hizo lo que el contrato dice **sin** introducir una segunda copia de las **decisiones** del guard (lo verifica `test_pd4_consumer_references_the_guard_contract`: el consumidor referencia al clasificador, los paths acotados y el fail-closed, y retira los globs legacy como mecanismo vigente). T4-green no toca `scripts/cdad-generate.py`, no toca el guard, y los derivados generados son byte-idénticos a una regeneración fresca (V9).
- **El matiz que se abre (hallazgo O-3):** la frase del adaptador «the emission REFERENCES this map» es inexacta: `cc_frontmatter()` compone los hooks directamente desde `CC_GUARDS` y no lee el adaptador en esa parte. En la realidad del mecanismo, `CC_GUARDS` es **la** fuente de emisión y la tabla del adaptador se sostiene por **paridad asertada por el focal congelado** (test-cerrado; el RED T4 tiene la doble aserción en ambos sentidos: cada par de los derivados declarado en ambas superficies, y ningún modo declarado huérfano). El drift entre las dos superficies no queda silencioso: queda perseguido por aserción de contrato congelado. La adjudicación no deja deuda sin mecanismo; pero la redacción del adaptador al respecto debería precisarse (O-3).
- **Residual que la adjudicación expone (duda honesta, registrada como parte del O-3/D-deuda):** que el dato de composición (los 6 pares matcher→modo) quede en **dos archivos editables máster** es la tensión más directa con PD-9 («una fuente editable por regla»). El drift queda test-cerrado (no silencioso); una reducción a una sola fuente editable haría falta enmienda de spec — fuera de alcance.

### 1.2 Los dos usos de `git stash` sobre el árbol compartido (GREEN T1, GREEN T2)

**Contexto verificado:** el plan §7 lo prohíbe expresamente («worktree, **nunca** `git stash` en el árbol compartido»); ambos GREEN lo usaron y lo declararon (`t1-green.md §3.5`, `t2-green.md §5`), con restauración y `stash list` vacío. Verificación propia: `git stash list` vacío; árbol integro; commits GREEN con alcance correcto; focales intactos (V4..V7).

**Juicio — Verdict: OPTIONAL · Bucket: m (regla de los observables: la evidencia del producto quedó verificada y no contiene efecto material, pero el hallazgo es una violación declarada de restricción de proceso, reincidente) — no bloqueante:**

- **Porqué no bloquea el producto:** la desviación se declaró, el árbol quedó integro, los commits con el alcance exacto, los focales intactos, y esta review re-verifica el resultado de forma independiente (V1, V4..V7, V12, V13); no hay efecto material en el producto. El orquestador ya saneó las notas del state (19633b8) y avisó el patrón correcto.
- **Porqué sí es deuda con condición de cierre:** es una violación declarada de una restricción global del plan, **reincidente** (T1 y T2), con riesgo real de corromper trabajo concurrente sobre el árbol compartido (T1/T2 comparten fuente: adaptador + generador + derivados). El GREEN de T4 ya usa el patrón correcto (worktree temporal, removido al terminar, `t4-green.md §5`). **Condición de cierre:** registrar la práctica explicita (worktree temporal, nunca `git stash`) como exigencia del paso del gate de T5 y del resto del epic-005; no requiere producto.

### 1.3 Observación sobre la pata Claude Code del chequeo de versión (T3)

**Contexto verificado:** mi propio fixture (V10) reproduce el patrón de la observación: la pata CC lee el marcador de la raíz de instalación detrás de los agentes CC (que en la instalación global del dueño es la misma raíz que la de OpenCode, porque `install.sh` instala los dos runtimes juntos) y reporta el marcador de esa raíz común. La revisión del orquestador Claude la registró como deuda (no como bloqueo de PD-3/AC-3) en `review-claude-spec-2026-10-13.md:68-71`.

**Juicio — Verdict: OPTIONAL · Bucket: m (regla de los observables: el hallazgo es una insuficiencia de diseño observable a futuro, no un defecto del producto actual ni de la evidencia) — no bloqueante:**

- **Porqué NO compromete PD-3/AC-3** (criterio de review 2026-10-12): PD-3 exige una pata CC **declarada y aditiva** que lee el marcador de la raíz detrás de los agentes CC y participa en el veredicto **sólo** cuando la instalación CC es detectable, nunca cruza una frontera de instalación y nunca lee el manifiesto de OpenCode. El producto hace exactamente eso, y los cuatro veredictos/rc existentes no cambian (V1, regresiones del focal). La limitación observada es una insuficiencia del **diseño** (no detecta desalineación de versión de agentes CC dentro de la misma raíz, porque la comparación contra el manifiesto de propiedad no formaba parte de PD-3 de contrato), no un desvío del GREEN ni una relajación del RED. En el estado actual del sistema no es un falso-verde: es el comportamiento declarado del diseño, y el escenario «raíz compartida + agentes CC con versión individual distinta» no existe en ninguna instalación declarada de hoy.
- **Porqué sí es deuda con condición de cierre:** si el dueño despliega versiones con agentes CC por raíz separada (paso b de PD-6, su decisión), la pata CC dejaría de reportar fielmente la versión de los agentes — sería un reporte **incompleto** (no incorrecto: no presta versión ajena, no cruza la frontera, marca `unknown` con causa cuando el marcador falta). **Condición de cierre:** la comparación contra el manifiesto de propiedad (PD-14 de 005-005, `<root>/.cdad-install-manifest.json`) como extensión aditiva y declarada en una unidad correctiva que dependa del despliegue real que decida el dueño; el contrato actual y su deuda ya queda enunciado en la revisión del orquestador y por el epic, así que no se toca aquí.
- **No impide el gate de T5:** el gate usa la pata CC desde el artefacto del repo en el commit de cierre contra la instalación al empezar (paso a de la enmienda), eso lo cumple el producto tal como está, con un veredicto declarado y coherente según las reglas de la pata.

---

## 2. Otros hallazgos del diff, más allá de los tres encargos del orquestador

**BLOQUEANTES — ninguno.**

### OPCIONALES

- **O-1 — La rama de resolución por registro de activación de T3 no queda cubierta por un test congelado (deuda con condición de cierre — Nit). **Verdict: OPTIONAL · Bucket: m** (afecta cobertura de evidencia, no el producto).**
  - **Ubicación:** `skills/cdad-cycle/scripts/cdad-version-check.py:128-141` (`_claude_code_installation_root`); focal congelado `tests/test_005_004_t3_version_check_cc.py` (sus fixtures siempre usan el directorio global de agentes CC).
  - **Evidencia:** el propio T3-green lo declara («la ruta del registro de activación no está cubierta por el focal congelado (sus fixtures usan el directorio global...); se verificó manualmente (CMD5)») y fue re-verificado por esta review con un fixture propio (V10: `adopted_root` de raíz CC con versión propia `45a2b1c0`, OpenCode distinta en el fixture, veredicto `UNKNOWN rc 3`, sin versión prestada).
  - **Consecuencia:** una regresión futura en esa rama no quedaría atrapada por ningún test.
  - **Condición de cierre:** un test nuevo (focal o extensión declarada) que ejerza la rama del registro con un fixture de activación.
- **O-2 — El barrido de T2 no cubre `scripts/` (deuda declarada con condición de cierre — Nit). **Verdict: OPTIONAL · Bucket: m** (límite de evidencia declarado en el RED).**
  - **Ubicación:** `tests/test_005_004_t2_installer_claims.py:94-96` (`SWEEP_ROOTS = ("sources","skills")`; `SWEEP_FILES = (INSTALLER,)`); los límites honestos declarados por el T2-red §5.1 («la segunda ocurrencia… queda fuera de esa superficie declarada y no se barre aquí») y por el T2-green §«Cambio» («scripts/ queda fuera del barrido declarado, pero está en alcance y AC-2 exige que no quede la afirmación»); el propio epic ya lo tiene en el plan T2 con el «comentario de generador» corregido sin prueba que lo atrape.
  - **Estado verificado:** hoy en HEAD ninguna superficie declarada contiene la afirmación (V7: sólo `.strip()` de código);
  - **Consecuencia:** una reincidencia dentro de `scripts/` (comentarios, docstrings) no atraparía el barrido.
  - **Condición de cierre:** extender el barrido declarado a `scripts/` (o declarar la corrección del comentario del generador como chequeo aparte en un test nuevo, red o unidad correcta).
- **O-3 — Frase del adaptador T4 enunciada de forma imprecisa sobre la emisión (Nit). **Verdict: OPTIONAL · Bucket: l** (enunciado documental, sin efecto en código hoy).**
  - **Ubicación:** `sources/agents/adapters/claude-code.md:35-37` — «the generator emits the frontmatter from `CC_GUARDS` … and the generated agents carry it (the emission REFERENCES this map…).»
  - **Problema:** en el mecanismo real, `cc_frontmatter()` compone los hooks directamente desde `CC_GUARDS`, no desde la tabla del adaptador: la paridad entre la tabla y `CC_GUARDS` la sostiene el focal congelado (aserción de contrato, no una referencia en tiempo de emisión). Como está redactada, la frase sugiere un mecanismo de referencia que no existe — exactamente el tipo de imagen errónea de «fuente única» que PD-9 quiere evitar.
  - **Consecuencia si no se corrige:** ninguna de producto hoy (la paridad queda asertada por el test en ambos sentidos; V9/V10).
  - **Condición de cierre:** re-frase de 2 líneas en el propio adaptador que diga: «the emission is **generated from** `CC_GUARDS`; parity with this table is enforced by the frozen focal test (test-closed, not referenced)». Edición mínima, sin tocar el generador; el focal de T4 no restringe esa redacción.

---

## 3. ABSTENCIONES

- **PD-6..PD-11 y AC-6..AC-8 (gate del recorrido real en T5)**: no son juzgables en la revisión formal de T1..T4 porque la evidencia del recorrido todavía no existe; el gate lo coordina una sesión nueva de Claude Code según la segunda enmienda. La revisión del gate queda **fuera del alcance de este paquete**, tal como el encargo lo declara («T5… NO entra en esta review»).
- **La afirmación sobre `exit 2` en modo no interactivo** queda, como PD-8 de contrato ya la fija, conservada `unknown` con causa en el focal T4 (los focales arrancan de VERIFY 1/2 del discovery §1.6); no hay evidencia nueva para juzgar más allá de la declaración, y el contrato prescribe conservarla tal como está — no altera el producto ni el gate.

---

## 4. Resumen

**Bloqueantes: 0 · Opcionales: 3 (O-1..O-3) · Abstenciones: 2.**

El diff de T1..T4 es **coherente con el contrato re-aprobado (5e11f2ef/953e4ba5, con las dos enmiendas del orquestador Claude)**: los focales RED→GREEN sin relajación (un solo commit RED por foco, 0 modificaciones posteriores), el implementer no editó `tests/` en ningún GREEN, el diff de producto está acotado a los 6 archivos de las fichas, las regresiones declaradas están verdes re-corridas por esta sesión (V12/V13), los 2 FAIL del validador del repo son pre-existentes con delta 0 probado en un árbol pre-feature (V3), y los versionados de la feature están anonimizados (V14). Los tres encargos del orquestador quedan dispuestos como: adjudicación del mapa de hooks **correcta** (1.1), `git stash` **opcional-proceso, no bloqueante** con condición de cierre explícita (1.2), y observación de la pata CC **opcional-deuda** que no compromete PD-3/AC-3 y no impide el gate (1.3). La feature queda lista para el gate T5.
