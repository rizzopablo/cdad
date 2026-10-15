# Review combinada T5 review-fix + T6 (004-002) — OpenCode glm-5.3-flash, 2026-10-01

> Paquete `004-002-project-execution-bootstrap-reviewer-review-007`, worktree fijado en `90c55c6`. Materializado verbatim; las rutas de sondas son temporales del reviewer.


**Paquete:** `004-002-project-execution-bootstrap-reviewer-review-007` · **Contrato:** `docs/specs/004-002-project-execution-bootstrap/spec.md` (sha256 `f72e6540…b57c` — verificado con `sha256sum`, coincide) · **Worktree propio:** `90c55c6`, limpio (`git status` sin cambios, sin commits). Trabajo read-only; sondas y mutaciones en `/tmp/opencode/t56r/` y tempdirs; instalación aislada bajo `CDAD_INSTALL_ROOT=/tmp/opencode/t56r/b/install-root` (el HOME real nunca se tocó). El repo principal no fue editado ni commiteado.

**Verificación del autor (lo que corrí, no lo que afirmó):**

| Comando | Resultado |
|---|---|
| `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_004_002_t5_reviewfix.py tests/test_004_002_t5_runtime.py tests/test_004_002_t6_landing.py tests/test_packet_prepare.py tests/test_role_packets.py tests/test_role_packet_render.py -q -p no:cacheprovider` | **78 passed** en 421,1 s (los 6 archivos del encargo; `make staging` no hizo falta en el worktree) |
| Mutaciones (script `/tmp/opencode/t56r/mutations.py`, restauración con `git checkout --`) | 17 corridas: 16 mutantes **eliminados**, 1 neutralizado por segunda capa (ver tabla) |
| Instalación aislada propia (copia sin `.git`, sin `agents/`, sin `sources/`; staging previo) | `bash install.sh --basic` → **rc=0**, 11/11 agentes staged, `Verify: PASS` |
| Recorrido guía instalada al pie de la letra | paso 1 **no reproducible verbatim** (ver B7/OPT-1); resto del flujo ✓ salvo hallazgo B7 |

---

## PARTE A — Verificación del review-fix de T5 (RED `d47ea15`+`e003899`; GREEN `cc3ac72`+`90c55c6`)

### Hallazgo BLOCKING nuevo

**B6 — El guard v2 no expande ni rechaza rutas con `~` literal: el implementer puede escribir fuera del proyecto (incluido el propio guard y su CLI) y el test-writer puede leer/buscar en `$HOME`**
- **Severidad:** Critical · **Verdict: BLOCKING** · **Bucket: h**
- **Ubicación:** `scripts/claude-code-path-guard.sh` rama v2: `REL_PATH="$RAW_PATH"` solo maneja el caso `== /*` (líneas 106–116); un `RAW_PATH` que empieza con `~` no es absoluto para bash y pasa directo a clasificación textual → `unclassified` → allow. El **legacy** sí expandía `~` (`EXPANDED_FILE_PATH="${FILE_PATH/#\~\//$HOME\/}"`, línea 237) — la superficie de herramientas admite `~`; el guard v2 perdió esa semántica y también viola la promesa que su propio bloque declara ("path outside the project root is not classifiable …; blocking").
- **Evidencia (sondas reproducibles, política layout cdad + `scripts|skills|src|vendor` como implementación; proyecto `/tmp/cdad-t56r-*/proj`, script `/tmp/opencode/t56r/probes_guard.py` + `/tmp/opencode/t56r/extra_probes.py`):**
  - `test-writer-read Read {file_path:"~/.claude/credentials.json"}` → **rc=0 ALLOW** (lectura fuera del proyecto; PD-7: sin lectura de implementación; PD-2: las rutas absolutas se rechazan — una ruta `~` lo es tras expansión de la herramienta).
  - `implementer Write {file_path:"~/.claude/skills/cdad-cycle/scripts/cdad_packet.py"}` → **rc=0 ALLOW** y `Write "~/.claude/cdad-scripts/path-guard.sh"` → **rc=0 ALLOW**: el implementer puede **reemplazar el clasificador y el propio guard** que lo mediaban → evasión total del mecanismo (invariante 3 en espíritu: los derivados instalados no son editables por ningún rol).
  - `test-writer-read Grep {pattern:"x", path:"~/"}` y `Glob {pattern:"**", path:"~/"}` → **rc=0 ALLOW** (búsqueda global fuera del proyecto; elusión de B2).
  - Contraste correcto: `/etc/passwd` → rc=2; `~/../etc/passwd` → rc=2 (el clasificador rechaza `~..`); `~` literal con Write para test-writer-write → rc=2 (regla de clase, no la de fuera-de-proyecto).
- **Contrato violado:** PD-2 (rechazo de rutas absolutas), PD-7/PD-8 (fronteras con prueba negativa por las herramientas que realmente median). Nota: el legacy **también** permite `~` (verificado: `LG tw-read ~/` rc=0) — el legacy queda byte a byte y eso es correcto; el defecto es que la rama v2, que declara bloquear lo no clasificable-fuera-de-proyecto, lo permite.
- **Remedio:** en la rama v2, rechazar `RAW_PATH` que empiece por `~` con el mismo diagnóstico de R1, o expandir con `$HOME` y aplicar la regla de residuo `/`. Test negativo CC alineado con el existente de R1.

### Tabla por garantía (disposición de review-t5)

| Garantía / hallazgo | Evidencia verificada | Estado |
|---|---|---|
| B1 guard: ningún rol edita `docs/cdad-policy.json` ni `.opencode/agents/**` | P1/P1b/B1x (Write/Edit/MultiEdit/NotebookEdit, 4 roles) → rc=2 «no role edits the policy or the published derived agents» ✓ | **VERDE** |
| B1 derivados OpenCode: `edit` deny sobre `.opencode/agents/**` en todos los derivados | `test_reviewfix_b1_derived_edit_deny_on_agents_dir` ✓; código `_derived_maps` añade `(derived_pattern,"deny")` a tw/implementer/orchestrator; readers van verbatim ✓ | **VERDE** |
| B2: búsqueda no acotada bloqueada (`""`, `.`, `./`, raíz abs/rel) | P4a/P4c/P4d → rc=2 con mensaje que pide acotar a tests/docs ✓; control `path="tests"` rc=0 ✓ | **VERDE** |
| B3: mapas = clasificador (sin `**/<root>/**`) | Código `_test_patterns` (solo `{root}/**`); `test_reviewfix_b3_nested_tests_dir_not_amplified` ✓ (tw deny edit+read, imp allow; control del clasificador) | **VERDE** |
| B4: Glob mediado por `path`+`pattern` | `../skills/**`, absoluto, `tests/{x,../skills/**}`, `{..,tests}/**` → rc=2 ✓; patrones con comodín *antes* de raíz impl (`*/scripts/**`, `**/skills/**`, `{tests,skills}/**`) → allow pero sin escape real (el `path` acota hacia abajo; el prefijo literal es lo que se clasifica) | **VERDE** (ver matización en OPTIONAL) |
| B5: `CLAUDE_PROJECT_DIR` como raíz | cwd=subdir+var → política aplicada (rc=2 en `vendor/v.py`); sin var → legacy; cwd=raíz → pwd ✓ | **VERDE** |
| R1: colisión de prefijo con hermana bloqueada | `<raíz>x/skills/x.py` → rc=2 ✓; mutante A-R1 neutralizado por segunda capa (clasificador rechaza camino fantasma absoluto) | **VERDE** |
| R2: huérfanos retirados al regenerar (solo manifest-declarados, ajenos intactos) | `test_reviewfix_r2_…retired` ✓; código `_retired_derived_names` + retire tras commit | **VERDE** |
| R3: fuente sin frontmatter → rc=2, sin traceback, sin escrituras | `test_reviewfix_r3_…fails_cleanly` ✓ (`PolicyError` en `_rewrite_derived_agent`) | **VERDE** |
| R6: MultiEdit/NotebookEdit mediados | rc=2 en tests/impl y manifiesto; controles rc=0 ✓; legacy sin tocar (mutación LG confirma que legacy NO media MultiEdit) | **VERDE** |
| R7: manifiesto registra procedencia | `"source_dir": str(source_dir)` + `test_reviewfix_r7_…` ✓ | **VERDE** |
| R9: aviso stderr sin agentes fuente, rc=0 | `test_reviewfix_r9_…warns_on_stderr` ✓ | **VERDE** |
| Legacy sin política byte a byte | Core legacy (`FILE_PATH=`→EOF) **idéntico** entre `dd6448e^`, `dd6448e` y HEAD (`diff` vacío); humo ✓; mutación de glob legacy mata el humo | **VERDE** |
| Evasiones nuevas: Grep `glob`/`type`, symlinks, CLAUDE_PROJECT_DIR fuera | `type`/`glob` no escapan (filtros relativos al `path`; rg no cruza `../` desde la raíz acotada — sin escape observable); symlink `tests/link-up→../skills` → clasificado `implementation` → rc=2 ✓; symlink a `/etc/passwd` → clasificador rc=2 → bloqueo sin fallback ✓; `CLAUDE_PROJECT_DIR=/tmp` → legacy por diseño (la variable la fija CC, no el agente) — **el vector real que quedó abierto es `~` → B6** | **VERDE** salvo B6 |

### Tabla de mutaciones (Parte A)

| Mutación | Cambio aplicado | Test dirigido | Resultado |
|---|---|---|---|
| A-B1 | `if [[ "$CLASS" == "policy" … ]]` → `if false` | `…reviewfix…::TestT5ReviewFixGuardCc::test_reviewfix_b1_guard_blocks_policy_and_derived_edits` | **ELIMINADO** (test falla) |
| A-B2 | condición B2 mutilada | `…test_reviewfix_b2_unscoped_paths_block_with_narrow_msg` | **ELIMINADO** |
| A-B3 | re-añadido `**/{root}/**` a `_test_patterns` | `…test_reviewfix_b3_nested_tests_dir_not_amplified` | **ELIMINADO** |
| A-B4 | bloque B4 → `if false` | `…test_reviewfix_b4_glob_pattern_escaping_blocked` | **ELIMINADO** |
| A-B5 | `PROJECT_ROOT="$(pwd)"` | `…test_reviewfix_b5_guard_uses_claude_project_dir` | **ELIMINADO** |
| A-R1 | `"$PROJECT_ROOT"/*` → `"$PROJECT_ROOT"*` | `…test_reviewfix_r1_sibling_prefix_collision_blocked` | **SUPERVIVIENTE aparente**: el test sigue verde — el camino fantasma queda absoluto y el clasificador lo rechaza («path is unsafe» → rc=2). La garantía observable (bloqueo) sobrevive por segunda capa; no hay pérdida de garantía, pero el test R1 no discrimina la primera barrera (fragilidad de oráculo, no del producto) |
| A-R2 | `_retired_derived_names` → `return []` | `…test_reviewfix_r2_removed_source_orphan_derived_retired` | **ELIMINADO** |
| A-R3 | `if start == -1 or fm_end == -1:` → `if False:` | `…test_reviewfix_r3_source_without_frontmatter_fails_cleanly` | **ELIMINADO** |
| A-R6 | `Read|Edit|Write|MultiEdit` → sin MultiEdit; NotebookEdit → `__Mut__` | `…test_reviewfix_r6_multiedit_notebookedit_mediated` | **ELIMINADO** |
| A-R7 | línea `source_dir` removida del manifiesto | `…test_reviewfix_r7_manifest_records_source_provenance` | **ELIMINADO** |
| A-R9 | `if derived_spec is None:` → `if False:` | `…test_reviewfix_r9_missing_agents_dir_warns_on_stderr` | **ELIMINADO** |
| A-LEG (1ª) | quitado `"**/*_test.go"` | humo legacy | **SUPERVIVIENTE por diseño de la sonda**: el humo no ejercita `*_test.go` (usa `test_*.py`); reintento |
| A-LEG (2ª) | quitado `"**/test_*.py"` | humo legacy | **ELIMINADO** (legacy deja de bloquear el co-ubicado) |
| B-install | `guard_sources` vuelve a exigir `agents/` | `…test_pd12_install_succeeds_without_source_agents_dir` | **ELIMINADO** |
| B-v1explicit | rechazo PD-10/D2 → retorno v1 (I4 restaurado) | `…test_pd10_explicit_v1_execution_context_fails_with_diagnostic` | **ELIMINADO** |
| B-guardcli | fallback `$HOME/.claude/skills/...` → `${CDAD_PACKET_CLI:?}` | `…test_pd12_i10_installed_cc_guard_finds_its_cli` | **ELIMINADO** |
| B-legacyintake | `if _policy_present(...)` → `if True:` (v1 implícito siempre exige `--new-execution`) | `…test_pd12_legacy_without_policy_keeps_legacy_intake` | **ELIMINADO** |

---

## PARTE B — Review de T6 (PD-10, PD-12; plan T6 e I4)

### Hallazgos BLOCKING

**B7 — La guía instalada promete que la reanudación queda desbloqueada tras reconciliar; el producto la deja rota permanentemente para todos los paquetes previos**
- **Severidad:** Required · **Verdict: BLOCKING** · **Bucket: m**
- **Ubicación:** `skills/cdad-cycle/references/project-execution.md` §6 (commit `697a61a`): «*Until reconciliation, new preparation, resume and dispatch registration are blocked*» — implica que tras `--reconcile-policy` la reanudación funciona. En `skills/cdad-cycle/scripts/cdad_packet.py`, `_resume_packet` (líneas 1404–1434) re-renderiza el paquete contra el contexto **vigente** (`render_packet(request, execution_document)`, línea 1430; el render embebe `execution_document["execution"]`/`["policy"]`, líneas 713–721): tras reconciliar, `execution.policy_sha256` es la revisión nueva y el re-render ya no coincide con los bytes del paquete → rc=2 con mensaje críptico «does not match its canonical rendering».
- **Evidencia (instalación aislada propia, consumidor sin checkout, reproducible):**
  1. `prepare --role test-writer --substage red` → paquete `…-test-writer-red-001`; `--resume-packet` → rc=0, bytes idénticos ✓.
  2. El dueño edita la política (añade `vendor`) → `prepare --resume-packet` → rc=2 (PD-5, correcto: «must be reconciled before … resuming») ✓.
  3. Paquete `completed` (dueño) + `prepare --reconcile-policy <sha> --decision-ref docs/owner-decision.md` → **rc=0** ✓.
  4. `prepare --resume-packet …-test-writer-red-001` → **rc=2 «packet … does not match its canonical rendering»** ✗ — y lo mismo para un paquete creado **después** de la reconciliación (`…-implementer-green-001`: resume rc=0 antes del cambio; rc=2 tras el siguiente reconcile).
- **Contrato violado:** PD-4 («Reanudar conserva `packet_id` y bytes»), PD-5 (el bloqueo es «*hasta reconciliar*»; la reconciliación «no altera paquetes existentes» y debe restaurar la operación), y la propia guía de T6. **No hay test que cubra resume-tras-reconciliar** (criterio de aceptación 1: PD-1–PD-12 trazados; solo existe el bloqueo *sin* reconciliar en `test_004_002_t3_durable.py::test_pd5_policy_bytes_change_blocks_prepare_resume_and_dispatch`). El defecto es **pre-existente en el CLI** (era T2/T3), pero la guía de T6 es el artefacto que hace la promesa falsa, y por eso entra en este review.
- **Remedio:** que `render_packet` use para el re-render la revisión registrada en el propio paquete (snapshot/hash del paquete o `policy_history`), o documentar en §6 que los paquetes anteriores a una reconciliación no son reanudables (con ese diagnóstico explícito) y añadir el test de comportamiento.

### Hallazgos OPTIONAL

| # | Hallazgo | Severidad | Verdict | Bucket | Ubicación / evidencia |
|---|---|---|---|---|---|
| OPT-1 | Guía §1 no reproducible verbatim: `python3 <skill>/scripts/cdad_packet.py prepare --project-root . --propose-policy` → **rc=2** «ERROR: --project-root must be an absolute existing directory: .». El flujo funciona con ruta absoluta. | Nit | OPTIONAL | l | guía §1; repro: instalación aislada `b/consumer` |
| OPT-2 | Guía §5/§6 implica cwd=raíz del proyecto: `--input docs/attempt.json` y `--decision-ref docs/…` se resuelven contra el **cwd** (`_cwd_path`), no contra `--project-root`; desde otro cwd da «dispatch observation not found: <cwd>/docs/attempt.json». Funciona con cwd=raíz; conviene declararlo en la guía. | Nit | OPTIONAL | l | `_cwd_path` (CLI); repro: mi record-dispatch falló desde el worktree y pasó desde `$R` |
| OPT-3 | B4 (matización, no defecto del fix): los patrones Glob con comodines antes de una raíz de implementación (`*/scripts/**`, `**/skills/**`, `{tests,skills}/**`) pasan el guard con path acotado. No son escapes reales: en Glob el `path` acota la búsqueda hacia abajo y el pattern es relativo a ese path; los escapes reales (`..`, absolutos, braces con `..`) sí bloquean. El prefijo literal de braces **sin** `..` (p. ej. `{skills,tests}`) se clasifica textualmente como `unclassified` → allow, benigno en la superficie CC. Divergencia teórica guard↔expansión-de-braces si CC expandiera braces a rutas absolutas — no verificado en runtime real (→ Abstentions). | Nit | OPTIONAL | l | guard, bloque B4 |
| OPT-4 | `prepare --role architect --substage discovery` con `active_epic: null` produce diagnóstico con ruta fabricada «docs/epics/**None**/plan.md». El rechazo es correcto por diseño (el architect standalone sigue el camino legacy/intake; PD-12), pero el mensaje fabrica una ruta destruida con `None` en vez de diagnosticar «architect requiere epic». | Nit | OPTIONAL | l | `validate_request` (contract path para architect), repro en `b/standalone` |
| OPT-5 | Precisión de la trazabilidad: v1-fixture-trace fila 8 afirma «(0 ediciones en el archivo)» para `tests/test_004_001_t6.py`; ese archivo **sí** fue editado (8 líneas, solo fixture de instalación) por `f50c3d8` (RED tramo 2, commit declarado y con trazabilidad propia). El claim es exacto respecto de `c50f521` (que no tocó el archivo) pero ambiguo en el ámbito del paquete. Las **aserciones del ORACLE FREEZE quedaron intactas** (verificado: el diff de `f50c3d8` solo redirige `install_product`; ningún cambio de expectativas congeladas). | Nit | OPTIONAL | l | fila 8 de v1-fixture-trace.md; `git show f50c3d8 -- tests/test_004_001_t6.py` |

### Verificación en vivo de PD-12/PD-10 (instalación aislada propia, consumidor sin checkout)

| Garantía | Evidencia verificada (instalación `/tmp/opencode/t56r/b`, HOME real intacto) | Estado |
|---|---|---|
| Install consume staging, sin `agents/` ni `sources/` | copia con `rm -rf agents sources` tras `make staging` → `install.sh --basic` rc=0; 11/11 agentes staged; `Verify: PASS`; 53 archivos cdad-cycle instalados | **VERDE** |
| Flujo consumidor aislado (propuesta → materialización → bootstrap → I9 → resume → record-dispatch → reconcile) | propuesta rc=0 sin escrituras (diff de árbol vacío) ✓; bootstrap rc=0 → contexto v2 en `.cdad/executions/…/execution.json` + binding en state + paquete canónico ✓; derivados I9 publicados desde `CDAD_OPENCODE_AGENTS_DIR` de la instalación (11 + `.cdad-derived.json`) ✓; resume bytes idénticos (cmp) ✓; record-dispatch rc=0 con intento en `dispatches/attempt-r1.json` (rol/substage del paquete) ✓; idempotencia rc=0 ✓; contradicción → rc=2 sin sobrescribir ✓; cambio de política sin reconciliar → bloquea prepare/resume/record ✓; reconcile rc=0 con decisión del dueño y sin paquete pendiente ✓ | **VERDE** |
| Guard CC instalado encuentra su CLI | `HOME=install-root` aislado, sin `CDAD_PACKET_CLI`: guard en `.claude/cdad-scripts/` resuelve `$HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py`; `Read tests/test_a.py` rc=0, `Read scripts/x.py` (impl en política del proyecto, que difiere del mapa legacy) rc=2 | **VERDE** |
| Legacy sin política conserva intake | proyecto con `.cdad/execution.json` v1 (sin política): prepare implícito rc=0, paquete legacy impreso, **v1 byte-idéntico** (sha256 antes=después), **cero contextos v2** fabricados | **VERDE** |
| Standalone (spec aprobada, sin epic) | `active_epic: null` + aprobación en `stage_history` → bootstrap rc=0, paquete con `"epic_id":null`, sin epic fabricado | **VERDE** |
| v1 explícito → diagnóstico sin escrituras | `--execution-context` a v1 → rc=2 con diagnóstico PD-10/D2 («an explicit v1 execution context is not adopted forward…»); sin paquete impreso (stdout vacío), sin `.cdad/executions/`, sin `.cdad/packets/`, v1 intacto | **VERDE** |
| Legacy implícito v1 sin política se conserva | I4-refinado: sin política el v1 implícito conserva el camino (rc=0, sin v2) — mutación B-legacyintake lo mata | **VERDE** |
| Transformación de fixtures v1 no debilitó garantías | fila 3: celdas retiradas (identidad runtime/modelo, parejas runtime-scope, rama de excepción `basic` de ADR-010) **justificadas por la spec v2** (PD-4/PD-6: runtime es observación; tensiones: «la autoridad no se ramifica por política de modelos»); celdas binding v2 añadidas (scope/model_policy/policy_sha256 mismatch — presentes en `test_role_packets.py:351-359`) ✓; fila 5: oráculo `added` **fortalecido** (conjunto congelado I9: 11 derivados + manifest, no debilitado) ✓; ORACLE FREEZE intacto en aserciones ✓ | **VERDE** |

---

## Abstentions

- **Activación real en sesiones OpenCode/CC (PD-8, C1, C2 «en una sesión real») y servicio de fondo OpenCode (300 s):** no es evidencia de este paquete de review; corresponde al gate. Me abstengo de juzgarla aquí. La gravedad de B6 (dado que el guard puede quedar neutralizado por su propio usuario) debería re-evaluarse en esa activación en vivo.
- **Expansión de `~` por el runtime real de Claude Code** en Read/Grep/Glob (¿expande la herramienta el path?): no pude verificarlo sin sesión CC real; B6 se sostiene sobre (i) el rc=0 observable del guard con esas entradas y (ii) el propio legacy expandiendo `~` (evidencia de que la superficie lo admite). Si CC no expandiera `~`, B6 degrada a divergencia con la promesa declarada del guard (sigue siendo defecto, de menor impacto).
- **Semántica real de ripgrep/Claude Code para `Grep.glob` con `../`** (si un filtro relativo pudiera cruzar la raíz acotada): mi análisis dice que no; no lo verifiqué en runtime real.
- **Claim «261 passed» de la suite completa sin T6** (trazabilidad v1): la corre el orquestador; no emito veredicto sobre esa cifra.
- **Brace expansion real de Glob en Claude Code** (`{tests,skills}/**`): clasificación del prefijo literal verificada en el guard; la expansión real del runtime quedó sin verificar (OPT-3).
- **Reconciliación seguida de preparación en un proyecto con `CDAD_OPENCODE_AGENTS_DIR` inexistente** y otras combinaciones del matriz integral de aceptación: no construidas; la matriz completa es T7.

**Síntesis:** el review-fix de T5 resolvía íntegra y honestamente su disposición (B1–B5 y R1/R2/R3/R6/R7/R9 verificados con sondas y 16 mutaciones eliminando cada fix), con el legacy intacto y un solo clasificador. Queda un nuevo hueco observable en el guard v2 que la sonda de evasión pidió explorar y encontró: **rutas `~` literales permiten leer/escribir fuera del proyecto —incluido reemplazar el propio guard y su CLI— (B6, BLOCKING)**. En T6, la instalación aislada, el flujo del consumidor, los mecanismos I9/I10, el intake legacy, el standalone y el rechazo del v1 explícito se reproducen en verde desde producto instalado; pero la guía de T6 promete una reanudación post-reconciliación que el producto no cumple (**B7, BLOCKING**, pre-existente en el CLI, hoy sin cobertura de test), más cinco mejoras menores (OPT-1–OPT-5, ninguna bloqueante).

## Disposición del orquestador

Validé B6 y B7 contra el código. B6: la rama v2 del guard solo trata rutas que
empiezan por `/`; `~` pasa a clasificación textual (el legacy sí lo expandía).
B7: `_resume_packet` re-renderiza contra el contexto vigente
(`render_packet(request, execution_document)`), así que todo paquete renderizado
bajo una revisión anterior de la política deja de coincidir.

| Hallazgo | Disposición |
|---|---|
| B6 | Se corrige. En la rama v2, `~` y `~/…` se expanden con `$HOME` y pasan por la regla de fuera del proyecto (R1); cualquier otra forma `~usuario` se bloquea. Test negativo con Read, Write, Grep y Glob. |
| B7 | Se corrige con la decisión **I11** (plan): un paquete renderizado bajo una revisión de política distinta de la aceptada no se reanuda. `--resume-packet` falla con un diagnóstico explícito que nombra ambas revisiones y pide preparar un paquete nuevo. No se re-renderiza contra la revisión vieja: re-despachar un paquete con ámbitos de una política superada anularía la reconciliación del dueño. Sus bytes siguen preservados en disco. La guía §6 lo dice. Test de comportamiento: resume tras reconciliar → rc 2 con ese diagnóstico, sin escrituras; un paquete nuevo posterior se reanuda con bytes idénticos. |
| OPT-1 | Se corrige en la guía: `--project-root "$PWD"`. |
| OPT-2 | Se corrige en la guía: se declara que las rutas de `--input` y `--decision-ref` se resuelven contra el directorio actual, y que los comandos se corren desde la raíz del proyecto. |
| OPT-3 | Se acepta (sin escape real; la expansión de llaves del runtime se verifica en T7 si aparece). |
| OPT-4 | Se corrige: architect sin epic activo → diagnóstico explícito, sin ruta fabricada con `None`. |
| OPT-5 | Se corrige en la trazabilidad (orquestador). |
| A-R1 superviviente | Se acepta: la segunda capa (el clasificador rechaza el camino fantasma) sostiene la garantía observable. |

Micro-ciclo: RED GLM (B6, B7, OPT-4) → GREEN DeepSeek (B6, B7/I11, guía,
OPT-4) → revisión del diff por el orquestador y suite de cierre en worktree
fijado.
