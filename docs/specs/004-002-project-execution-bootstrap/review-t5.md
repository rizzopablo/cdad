# Review T5 (004-002) — OpenCode glm-5.3-flash, 2026-10-01

> Paquete `004-002-project-execution-bootstrap-reviewer-review-006`, worktree fijado en `dd6448e`. Materializado verbatim; las rutas de sondas son temporales del reviewer.


**Paquete:** `004-002-project-execution-bootstrap-reviewer-review-006` · **Contrato:** `docs/specs/004-002-project-execution-bootstrap/spec.md` (sha256 `f72e6540…b57c`) · **Diff bajo revisión:** `dd6448e` — `feat(004-002): T5 GREEN` (2 archivos, +355: `scripts/claude-code-path-guard.sh`, `skills/cdad-cycle/scripts/cdad_packet.py`) · **Worktree:** `dd6448e`, limpio (`git status` sin cambios).

## Verificación del autor (lo que corrí, no lo que afirmó)

| Comando | Resultado |
|---|---|
| `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_004_002_t5_runtime.py … tests/test_packet_prepare.py -q -p no:cacheprovider` (los 7 archivos del encargo; `make staging` no hizo falta) | **113 passed** en 150,3 s |
| `pytest tests/test_004_002_t5_runtime.py` | **19/19 passed** (coincide con el claim del commit) |
| `pytest tests/test_004_002_t6_landing.py` | **8 failed** — RED por diseño; los fallos son del alcance T6 (PD-12: install consume staging, deploy de entrypoints; PD-10/I4: camino v1 explícito). Sin fallos que apunten a T5. |

La afirmación del commit «suite completa (sin T6) 259 passed» cubre archivos adicionales a los 7 del encargo (t1/t2/t3/t4-reviewfix); su verificación quedó en curso en segundo plano al cierre de este dictamen → ver Abstenciones. Los tests T5 son de buena calidad: usan la **forma real** del JSON de hook (C2), reutilizan el evaluador findLast existente (`tests/pd10_permission_semantics.py`, sin segundo evaluador), tienen casos negativos (política inválida, CLI ausente, derivado a mano) y trazabilidad test→postcondición declarada en el header. **No detecto gaming en los tests.**

## Hallazgos BLOCKING

### B1 — El guard CC permite al implementer editar `docs/cdad-policy.json` (y los derivados `.opencode/agents/*`)
- **Severidad:** Critical · **Verdict: BLOCKING** · **Bucket: h**
- **Ubicación:** `scripts/claude-code-path-guard.sh`, rama `implementer:write)` (líneas 111–119): solo bloquea clases `test|colocated-test`; la clase `policy` y las no clasificadas pasan por `exit 0`.
- **Evidencia (sondas P1, P1b, B1x):** con política presente, `implementer Write docs/cdad-policy.json` → **rc=0 (ALLOW)**; `implementer-odoo` idéntico; además `implementer Edit .opencode/agents/cdad-implementer.md` → rc=0 y `Edit .opencode/agents/.cdad-derived.json` → rc=0.
- **Contrato violado:** invariante 3 («Ningún rol modifica su política de límites; los derivados no son fuentes editables») y PD-7 («La exclusión de `docs/cdad-policy.json` prevalece sobre cualquier permiso por clase»). El derivado OpenCode **sí** lo deniega (`test_pd7_i9_policy_edit_deny_for_every_derived_role` pasa), así que los dos consumidores de la misma política divergen — justo lo que PD-8 exige igualar.
- **Remedio:** en la rama `implementer:write`, añadir `policy` al case de bloqueo y denegar Edit/Write sobre `.opencode/agents/` (derivado y manifiesto). Test negativo CC alineado con el existente de OpenCode.

### B2 — La barrera «Grep/Glob sin path → bloqueo» se evade con `path="."` o la raíz absoluta
- **Severidad:** Required · **Verdict: BLOCKING** · **Bucket: h**
- **Ubicación:** `scripts/claude-code-path-guard.sh`, bloque «A project-wide Grep/Glob (no `path`)…» (solo compara `RAW_PATH` vacío) + clasificación de `"."` como `unclassified` → allow.
- **Evidencia:** `test-writer-read Grep {pattern:"def ", path:"."}` → **rc=0**; `Glob {pattern:"**/*.py", path:"."}` → rc=0; `Grep {path:"<raíz absoluta>"}` → rc=0. Con eso el test-writer busca en todo el proyecto incluida implementación, exactamente lo que C2/I10 dice bloquear «pidiendo acotar a tests/docs». (La sonda hermana `path="docs/.."` sí bloquea: el clasificador rechaza `..`.)
- **Contrato violado:** PD-8 («cada barrera declarada efectiva tiene prueba positiva y negativa») — la barrera declarada en I10 tiene prueba positiva en `test_…_blocks_unscoped_grep_glob` pero el bypass negativo es trivial.
- **Remedio:** tratar `path ∈ {"", ".", "./"}` y `path` = raíz del proyecto (relativa o absoluta) como «no acotado»; alternativamente, para test-writer exigir que la clase del `path` sea `test`/`colocated-test`/`documentation`.

### B3 — Los mapas derivados OpenCode amplifican la política: test-writer edita `src/tests/x.py` (clase real `implementation`)
- **Severidad:** Required · **Verdict: BLOCKING** · **Bucket: m**
- **Ubicación:** `skills/cdad-cycle/scripts/cdad_packet.py` — `_test_patterns` (líneas 1831–1836) emite `f"**/{root}/**"` por cada `test_root`; `_derived_maps` (líneas 1849–1876) lo inserta como **allow** en el `edit` del test-writer y como **deny** en el implementer.
- **Evidencia (sondas P3a/P3b + árbitro):** clasificador único (`validate-policy --classify src/tests/x.py`) → `implementation`; guard CC → bloquearía; pero el derivado OpenCode resuelve `edit("src/tests/x.py")` → **allow** para test-writer y **deny** para implementer. Amplificación y sobre-restricción simultáneas; divergencia CC↔OpenCode para el mismo par (rol, política).
- **Contrato violado:** PD-7 («Los scopes pueden restringir la política, nunca ampliarla») y PD-2 («Un nombre de test fuera de las ubicaciones declaradas no concede permisos»); degrada la «igualdad semántica» de derivación de PD-8. Nota: ningún layout declarado en los fixtures T5 se ve afectado (por eso los tests pasan); el defecto aparece con un directorio literal `tests/` anidado bajo una raíz de implementación.
- **Remedio:** no emitir el patrón `**/<root>/**` en los mapas derivados; si se quiere soportar tests dedicados anidados fuera de la raíz, el cambio pertenece al clasificador (I1), no a los mapas.

## Hallazgos OPTIONAL

| # | Hallazgo | Severidad | Verdict | Bucket | Ubicación / evidencia |
|---|---|---|---|---|---|
| R1 | Bypass por colisión de prefijo: ruta absoluta `<raíz>x/skills/x.py` (hermana del proyecto) se consideran «dentro», se recorta el prefijo y se clasifica un camino fantasma (`x/skills/x.py` → unclassified) → test-writer la **lee** (P5a) e implementer **escribe** fuera del proyecto (P5b). Contradice el check declarado del propio guard («Absolute paths outside the project root cannot be classified safely → blocking»). Efecto práctico limitado (Bash es permisivo por diseño; el guard no es sandbox). Remedio: exigir que el residuo tras el strip empiece por `/` (o comparar `"$PROJECT_ROOT"/`). | Required | OPTIONAL | m | guard, líneas 85–97 |
| R2 | Derivados huérfanos: si una fuente se retira de la instalación, el derivado previo queda **activo en `.opencode/agents/` y fuera del manifiesto nuevo** (P7: `cdad-architect.md` sigue presente tras regenerar, el manifest ya no lo lista). Drift de permisos silencioso entre generaciones. Remedio: al regenerar, retirar solo los `cdad-*.md` declarados por el manifiesto previo (ajenos intactos). | Required | OPTIONAL | m | `_build_derived_payloads` / `_reject_hand_modified_derived` |
| R3 | Fuente instalada sin frontmatter → `ValueError: substring not found`, **traceback con rc=1** en vez de PolicyError rc=2 con diagnóstico (P15). Ocurre dentro del lock pero antes de cualquier escritura (el `with _ProjectLock` libera y retira). Remedio: validar la fuente y convertirla en PolicyError. | Nit | OPTIONAL | m | `_rewrite_derived_agent` (1878–1884), llamada en 2084 |
| R4 | La detección de «derivado a mano» compara manifiesto↔bytes pero no re-deriva desde la fuente: un implementer que edite agente + manifiesto de forma autoconsistente (vía B1 en CC o el propio mapa OpenCode `*→allow`) no es detectado; el siguiente prepare lo sobrescribe en silencio. Autocurativo pero el gate declarado es frágil ante un agente malicioso. | Required | OPTIONAL | m | `_reject_hand_modified_derived` (1920–1946) |
| R5 | Rendimiento: cada tool call mediada dispara un `python3` nuevo (~0,7 s medido por invocación sobre Read/Edit/Grep/Glob). Fricción perceptible en sesiones intensivas; no bloquea. Remedio: medir en T6 y, si molesta, cachear la política/clases por sesión. | Optional-Consider | OPTIONAL | m | guard, llamada al CLI |
| R6 | `MultiEdit`/`NotebookEdit` no mediados ni en legacy ni en v2 (`case` solo Read/Write/Edit/Grep/Glob). Hueco heredado, no introducido por este diff; PD-8 pide mediación «por las herramientas que realmente media» — declararlo o agregarlo al case. | Required | OPTIONAL | m | guard, case de TOOL_NAME |
| R7 | El manifiesto registra hashes pero no **procedencia** (§2 artefactos: «manifest de hashes y procedencia»): falta el origen (dir fuente/env) de cada derivado. | Nit | OPTIONAL | l | `_build_derived_payloads` |
| R8 | Desviación del texto de I10: el bloqueo de Grep/Glob sin path es incondicional, no «cuando existen raíces de implementación». Menor, del lado conservador. | Nit | OPTIONAL | l | guard, bloque unscoped |
| R9 | `prepare` con política presente y `CDAD_OPENCODE_AGENTS_DIR` apuntando a un directorio vacío/inexistente no publica derivados **sin diagnóstico** (silencio de desconfiguración). | Nit | OPTIONAL | l | `_load_derived_sources` |
| R10 | Parsing de la clase con `cut -f2`: un nombre de archivo con TAB desalinea el campo (lectura de implementación posible en caso extremo). Legacy tenía parseo igualmente ingenuo. | Nit | OPTIONAL | l | guard, línea 106 |

**FYI:** (i) el guard solo se activa con cwd == raíz del proyecto; desde un subdirectorio cae silenciosamente a legacy (límite conocido de la era journal-cwd; conviene declararlo antes del despacho junto a C2); (ii) input JSON malformado → `jq` rc=5, hook no bloquea (pre-existente).

## Tabla por garantía

| Garantía | Evidencia verificada | Estado |
|---|---|---|
| PD-7 / I9 — mapas test-writer (layout CDAD) | `test_pd7_i9_test_writer_cdad_layout_maps` ✓; sonda P9/P11/P12/P13 coherentes | VERDE, salvo B3 (caso no declarado) |
| PD-7 / I9 — convencional + co-ubicado | `test_pd7_i9_maps_conventional_and_colocated_layouts` ✓ (incluye co-ubicado anidado por prefijo) | VERDE |
| PD-7 / I9 — layout Odoo | `test_pd7_i9_maps_odoo_layout` ✓ | VERDE |
| PD-7 — exclusión de la política en todos los derivados (OpenCode) | `test_pd7_i9_policy_edit_deny_for_every_derived_role` ✓ | VERDE (solo OpenCode; en CC falla → **B1**) |
| PD-8 / I9 — publicación `.opencode/agents/` + manifiesto (hashes política/origen/derivado) | tests de publicación y manifiesto ✓; byte-a-byte fuera de mapas ✓ (`without_maps`) | VERDE (procedencia ausente → R7) |
| PD-8 / I9 — archivos ajenos intactos | `test_pd8_i9_foreign_file_survives_publication` ✓; huérfanos derivados → R2 | VERDE con salvedad |
| PD-8 / I9 — derivado a mano → rc≠0 sin sobrescribir | `test_pd8_i9_hand_modified_derived_fails_without_overwrite` ✓; forge autoconsistente → R4 | VERDE con salvedad |
| PD-5 / I9 — regeneración tras reconciliar | `test_pd8_i9_reconciled_policy_regenerates_deriveds` ✓ | VERDE |
| I9 — publicación dentro de transacción/lock de T3 | código (derivado en stage, commit con `os.replace`, rollback `derived_committed`); suite T3/T4 ✓ en el subset | VERDE (lectura de código; crash entre replaces deja mezcla que el próximo prepare regenera — analizado, sin defecto) |
| I10 / C2 — guard media Read/Edit/Write por file_path y Grep/Glob por path (forma real) | tests CC ✓ (relativo, absoluto, scoped, unscoped) | VERDE, salvo B2 |
| I10 / C2 — política inválida o CLI ausente → bloqueo sin fallback | `test_…_blocks_on_invalid_policy`, `test_…_blocks_when_cli_unfindable` ✓ | VERDE |
| I10 — legacy sin política intacto | diff solo inserta antes del legacy; smoke test ✓ | VERDE |
| PD-8 — activación real (sesiones reales OpenCode con control aislado; sesión CC real; servicio de fondo 300 s) | no corresponde a T5 — es evidencia de C1/T6/gate | PENDIENTE de T6 (no defecto de este diff) |

## Tabla de mutaciones y sondas (reproducibles)

Script: `/tmp/opencode/t5_review_probes.py`; proyecto sintético en `/tmp/opencode/cdad-t5-rev-xwas8cwg` (política layout cdad + raíz `src` extra, agentes de `agents/` copiados a tempdir, `CDAD_PACKET_CLI` al CLI del repo). Comando de reproducción: `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/opencode/t5_review_probes.py`.

| Sonda | Mutación/entrada | Esperado | Observado |
|---|---|---|---|
| P1/P1b | implementer(-odoo) Write `docs/cdad-policy.json` | BLOCK (PD-7) | **ALLOW → B1** |
| B1x | implementer Edit `.opencode/agents/{cdad-implementer.md,.cdad-derived.json}` | BLOCK (invar. 3) | **ALLOW** |
| P4a/P4c/P4d | TW-read Grep/Glob `path="."` / raíz absoluta | BLOCK (C2) | **ALLOW → B2** |
| P4b | Grep `path="docs/.."` | BLOCK | BLOCK ✓ |
| P5a/P5b | ruta absoluta hermana con prefijo colisionante | BLOCK (check declarado) | **ALLOW → R1** |
| P12/P13 | co-ubicado anidado por sufijo (guard) | ALLOW / BLOCK | ALLOW / BLOCK ✓ (consistente con clasificador) |
| P2a/P2b | co-ubicado anidado por sufijo (derivados) | deny impl | deny ✓ |
| P3a/P3b | `src/tests/x.py` (derivados) | impl: allow impl / deny TW | **deny impl / allow TW → B3** |
| P7 | fuente retirada + regeneración | huérfano retirado o diagnosticado | **huérfano activo sin declaración → R2** |
| P15 | fuente sin frontmatter | rc=2 diagnóstico | **rc=1 traceback → R3** |
| P9/P8a/P10/P11/P16/P18/P19 | controles positivos y negativos | — | todos coherentes ✓ |
| P20 | JSON malformado | diagnóstico | rc=5, no bloquea (FYI) |

## Abstentions

- **Claim «259 passed» (suite sin T6):** la verificación de la suite completa quedó en curso al cierre (los 7 archivos del encargo y T5 sí quedaron verificados: 113 y 19/19). No emito veredicto sobre esa cifra hasta tener el resultado; no afecta los hallazgos B1–B3.
- **Activación real OpenCode/CC (PD-8, C1, C2 «en una sesión real») y servicio de fondo OpenCode (300 s):** no es evidencia de T5; corresponde a T6/gate. Me abstengo de juzgarla aquí.
- **Semántica real de OpenCode 2.x sobre los mapas generados** (findLast, `*` cruzando `/`): los tests y mis sondas usan el evaluador de `pd10_permission_semantics.py` como oráculo precedented; no verifiqué el runtime OpenCode real ( VERIFY de T6).
- **Layout Odoo con `colocated_test_roots` vacío y sufijos declarados:** no construí un proyecto así; la interacción exacta de `_colocated_test_patterns` en ese caso no quedó sondada.

**Síntesis del dictamen:** la publicación I9 está bien integrada en la transacción/lock de T3, el guard CC reutiliza un único clasificador y el legacy queda intacto; los tests T5 son trazables y honestos. Pero el diff deja **tres huecos observables que rompen garantías aprobadas en los consumidores**: el implementer puede editar la política y los derivados vía guard CC (B1), la barrera anti-búsqueda-global se evade con `path="."` (B2) y los mapas OpenCode amplifican/sobre-restringen respecto del clasificador único (B3). Recomiendo resolver B1–B3 antes del corte C1/T6, ya que la evidencia de activación en vivo los expondría de inmediato.

## Disposición del orquestador

Validé B1, B2 y B3 contra el código: la rama `implementer:write` del guard solo
bloquea `test|colocated-test`; el bloqueo de búsqueda global solo mira `path`
vacío; `_test_patterns` emite `**/<root>/**`. Agrego dos hallazgos propios:

- **B4 (orquestador, BLOCKING):** I10 dice que `Glob` se media por `path` +
  `pattern`, pero el guard no mira `pattern`. Un test-writer con
  `path: "tests"` y `pattern: "../skills/**"` (o un `pattern` absoluto)
  sale del ámbito. Remedio: para el test-writer, rechazar `pattern` con `..`
  o absoluto, y clasificar el prefijo literal del patrón (hasta el primer
  comodín) junto con `path`.
- **B5 (orquestador, BLOCKING):** `PROJECT_ROOT="$(pwd)"`. Si el cwd del hook
  no es la raíz, no encuentra la política y cae al legacy en silencio.
  Remedio: `${CLAUDE_PROJECT_DIR:-$(pwd)}` (Claude Code exporta esa variable
  a los hooks).

Disposición por hallazgo:

| Hallazgo | Disposición |
|---|---|
| B1 | Se corrige. Guard: ningún rol edita `docs/cdad-policy.json` ni `.opencode/agents/**`. Derivados OpenCode: `edit` deny sobre `.opencode/agents/**` en todos los roles (cierra también el vector de R4). |
| B2 | Se corrige. `path` vacío, `.`, `./` o la raíz (relativa o absoluta) cuentan como búsqueda no acotada. |
| B3 | Se corrige. Se retira `**/<root>/**` de los mapas: los mapas expresan exactamente al clasificador. |
| B4, B5 | Se corrigen (arriba). |
| R1 | Se corrige: el residuo tras quitar la raíz debe empezar por `/` (o ser vacío). |
| R2 | Se corrige: al regenerar se retiran los derivados que declaraba el manifiesto previo y ya no tienen fuente; los ajenos no se tocan. |
| R3 | Se corrige: fuente sin frontmatter → rc 2 con diagnóstico. |
| R4 | Se acepta como límite: con B1 ningún rol puede editar los derivados ni el manifiesto, y el próximo prepare regenera. No se re-deriva para comparar. |
| R5 | Se mide en T7 (recorrido real); se registra. |
| R6 | Se corrige: `MultiEdit` (`file_path`) y `NotebookEdit` (`notebook_path`) entran a la mediación v2. El legacy no se toca. |
| R7 | Se corrige: el manifiesto registra el directorio de origen. |
| R8 | Se acepta: el bloqueo incondicional es más conservador que I10. |
| R9 | Se corrige como diagnóstico, no como error: con política presente y sin agentes de origen, `prepare` avisa por stderr que no publicó derivados (un proyecto puede usar solo Claude Code). |
| R10 | Se acepta (nombres con TAB); el legacy tenía el mismo límite. |
| FYI cwd | Cubierto por B5. FYI JSON malformado: preexistente, fuera de alcance. |

Micro-ciclo: RED GLM → GREEN DeepSeek → verificación GLM, después de que
termine el paquete previo de T6 (portador v2), para no contaminar su suite.
