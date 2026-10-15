# Review final T4 — 003-002-artifact-tools (cierre de feature)

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-58>`.
> Paquete: `003-002-artifact-tools-reviewer-review-009`.
> Contrato verificado: `docs/specs/003-002-artifact-tools/spec.md`
> sha256 `ba73e645…01f37` = el del paquete ✓.
> **Dictamen: la integración es correcta; el cierre queda condicionado a la familia
> F1 (BLOCKING, una pasada de documentación). F2/F3 son opcionales.**

**Objeto:** diff de T4 (`41b1663` + `d7ffbcc`) contra la spec aprobada y el plan T4, y
la evidencia de integración vigente. **Modo:** read-only; ningún archivo modificado,
ningún commit.

## 0. Calibración aplicada

Se aplicó la enmienda vigente (texto autoritativo:
`skills/cdad-cycle/references/stage-4-review.md` §"Review calibration"; versión
operativa `8cb6580` entregada como entrada del encargo). Cada hallazgo lleva evidencia,
consecuencia y condición verificable de cierre; la familia se remedia con **una** pasada
general. La calibración no degradó ningún defecto observable en uso real.

## 1. Verificación de los cuatro puntos pedidos

### (a) Protocolo de materialización vs spec §9 — CORRECTO ✓

| Afirmación del diff (`re-entry.md:14-48`) | Spec | Veredicto |
|---|---|---|
| Un solo escritor del state: el orquestador; las herramientas nunca escriben | §9 (`spec.md:436-448`), invariante (`spec.md:518-519`) | ✓ conforme |
| Recibo mecánico, NUNCA aprueba (`semantic_status` siempre `pending`) | §6 (`spec.md:314`); el código lo hace cumplir (`cdad_result.py:814-816` rechaza `materialize` si `!= "pending"`) | ✓ conforme |
| Transición lógica `received` → estado de paquete `completed` | §6 (`spec.md:316-318`); vocabulario existente `VALID_PACKET_STATUSES` (`cdad_packet.py:43`) | ✓ conforme |
| Referencia pequeña en `stage_history`, forma existente, esquema sin cambio | §9 (`spec.md:446-448`) | ✓ conforme (ver (b)) |
| No duplica la interfaz; owner = CLI `--help` + spec §2/§6–§9 | — | ✓ conforme (`re-entry.md:18-23`) |

### (b) «`install.sh` y `cdad_packet.py` no requieren cambio» — FUNDADA ✓ (verificado independientemente)

- **install.sh:** `install.sh:394-402` documenta que el árbol `cdad-cycle` viaja completo,
  incluidos `scripts/cdad_result.py` y `assets/*.schema.json`. Verificado empíricamente
  re-corriendo el guard focal: la instalación `--basic` expone el entrypoint instalado y
  los 6 schemas requeridos, rc=0.
- **cdad_packet.py:** la referencia en `stage_history` no exige regla nueva.
  `_approved_stage_entry` (`cdad_packet.py:1264-1276`) busca por claves de forma
  permisiva y no rechaza claves extra; `tests/validate-consistency.sh:92` sólo exige
  claves de primer nivel; `state-template.json:12` no impone esquema estricto de entradas.
  La entrada reconciliada con `receipt_sha256` extra
  (`tests/test_003_002_t4_integration.py:491-497`) pasa esos validadores.

### (c) Los 6 guards cubren los criterios de aceptación de integración — SÍ ✓ (no son tests de frases)

Oráculos observables mecánicos: bytes exactos (`assertEqual(stored.read_bytes(), data)`),
stdout == bytes del recibo, snapshots del árbol completo con negación de escritura fuera
de targets/`.cdad/`, state byte-idéntico, convergencia byte a byte. `assertNotIn("Traceback")`
(`:552`, `:569`) es auxiliar, nunca único oráculo. El recorrido corre el entrypoint
**INSTALADO** desde un fixture sin wrappers del repo (la suite verifica esa precondición,
`:310-315`). Sin mocks sobre plumbing: `install.sh` real, CLIs reales, subprocesos reales.

Cobertura vs criterios de aceptación (`spec.md:535-538`):
- «recorrido de integración … no duplica efectos ni escribe state desde las herramientas»
  → guards 2, 5, 6.
- «Smoke instalado funciona desde proyecto fixture sin wrappers del repo» → guards 1 y 2.

### (d) Regresión — NO HAY ✓

- Guard focal re-corrido por la revisión: **6/6 OK** (31.1 s).
- Suite **439 passed / 601 s** en `d7ffbcc`, **citada** (PD-5): `git diff d7ffbcc..HEAD --stat`
  sólo toca `docs/.cdad-state.json` y `dispatch-ledger.md`; `tests/` intacto. También
  `test_packet_prepare` 19/19.

## 2. Auditoría TEST ↔ POSTCONDICIÓN (obligatoria, AP-14)

| # | Test | Postcondición / criterio | ¿Estructura interna? | ¿Mock sobre plumbing? |
|---|---|---|---|---|
| 1 | `test_t4_smoke_installed_entrypoint_and_schemas_exist` (:511) | Criterio «Smoke instalado» + §1 (entrypoint + assets) | No | No |
| 2 | `test_t4_receive_then_materialize_from_installed_entrypoint` (:538) | P1 + P4 + criterio smoke; límite de escritura (targets + `.cdad/`) | No | No |
| 3 | `test_t4_single_durable_completion_receive_retry_byte_identical` (:606) | P2 + invariante «máximo un bundle durable» | No | No |
| 4 | `test_t4_materialize_retry_idempotent_targets_unchanged` (:628) | P2/P4 + invariante «bytes conservan SHA-256 y longitud» | No | No |
| 5 | `test_t4_walkthrough_leaves_state_byte_identical` (:655) | §9 + criterio «no escribe state desde las herramientas» | No | No |
| 6 | `test_t4_retry_after_orchestrator_transition_repeats_no_effect` (:700) | §5 (`spec.md:267-274`) + RED declarado del plan T4 (`plan.md:220-222`) | No | No |

**AP-14: CUMPLE.** Ningún test depende de la estructura interna de `cdad_result.py`.

Sobre el RED: `41b1663` declara RED honesto 6/6 GUARD (pre-satisfechas porque T1–T3 ya
entregaron `cdad_result.py`), declarado en el docstring (`:34-35`) y registrado en
`03e6da9`. Sin falla fabricada. Sin hallazgo.

## 3. Hallazgos

### F1 — FAMILIA: la superficie documental declarada de T4 quedó incompleta (2 instancias) · **BLOCKING** · Bucket h · Required

Una sola solución general (calibración regla 3): una pasada de documentación única que
complete las dos instancias. No son parches por variante: ambas son «instrucciones
declaradas en el alcance de T4 que el flujo real no deja cubiertas».

**F1.1 — `re-entry.md` paso RECEIVE no define cómo el TEXTO FINAL se vuelve recibible.**
- **Evidencia:** `skills/cdad-cycle/references/re-entry.md:25-27` — «The role's output
  arrives either as FINAL TEXT or as staged parts under `.cdad/inbox` (with a `RESULT.json`
  descriptor). Run the product's `receive` command…». `receive` exige `--descriptor` con
  parts bajo `.cdad/inbox` y `source.kind` obligatorio `staged-file`
  (`spec.md:95-100`, `:172-174`; y el código lo exige en `cdad_result.py:232-234`,
  `:249-272`). Para el caso TEXTO FINAL no existe staged file ni descriptor, y el
  protocolo no declara el paso de staging.
- **Consecuencia:** el caso TEXTO FINAL es el **dominante** en uso real (todos los roles
  read-only entregan FINAL TEXT — esta misma revisión lo es). Un orquestador que siga el
  paso 1 al pie de la letra no puede correr `receive` (fallará en validación) y la única
  salida literal es copiar el texto a mano — exactamente lo que la sección prohíbe
  (`re-entry.md:17-18`). Fricción con camino realista que socava el propósito de la
  feature. No hay corrupción (fail-closed), pero la instrucción es incompleta para su
  caso primario.
- **Condición verificable de cierre:** el paso RECEIVE de `re-entry.md` contiene una
  cláusula que define el staging como paso previo del orquestador (bytes del TEXTO FINAL
  bajo `.cdad/inbox` + `RESULT.json` con descriptor válido, cf. spec §3/§4) antes de
  invocar `receive`. Chequeo observable: leer la sección y confirmar la cláusula;
  re-correr el guard focal una vez (cambio docs-only).

**F1.2 — `README.md` declarado en el alcance de T4 no tocado, y la desviación no documentada.**
- **Evidencia:** el plan T4 declara «Alcance incluido: … instalacion/README»
  (`plan.md:197-198`) y lista `README.md` en archivos (`plan.md:205`, `plan.md:358`). El
  diff `d7ffbcc` toca sólo `re-entry.md`. `README.md:5-6` nombra hoy como único entrypoint
  público `cdad_packet.py`.
- **Consecuencia:** 003-002 agrega un segundo CLI público (`scripts/cdad_result.py` +
  entrypoint instalado equivalente, spec §1-§2). Un usuario que instala CDAD y lee el
  README no descubre el CLI de recepción/materialización: el documento front-door queda
  desactualizado respecto del producto entregado. Desviación silenciosa del plan aprobado.
- **Condición verificable de cierre:** (i) `README.md` nombra el segundo entrypoint
  público (una frase, cf. `README.md:5-6`), **o** (ii) el dueño registra la decisión de
  retirar README del alcance de T4 (ampliación del plan).

### F2 — `handoff-prompts.md` aún describe el mecanismo pre-002 · **OPTIONAL** · Bucket m

- **Evidencia:** `handoff-prompts.md:123` y `:511` — «the orchestrator materializes
  `docs/specs/<feat>/…` from that text».
- **Consecuencia:** no es contradicción estricta (allí se declara QUIÉN materializa;
  `re-entry.md` declara CÓMO), pero describe el mecanismo manual anterior sin referenciar
  el protocolo nuevo. T4 excluye «cambiar gates ajenos» (`plan.md:198-199`), así que no es
  incumplimiento de T4: es deuda documental para un follow-up. No prolonga el ciclo.

### F3 — el smoke no ejecuta el entrypoint instalado · **OPTIONAL** · Bucket l · Nit

- **Evidencia:** guard 1 (`:511-532`) comprueba rc de install, existencia del entrypoint y
  de los 6 schemas; no lo ejecuta.
- **Consecuencia:** el criterio «Smoke instalado **funciona**» queda cubierto por el guard 2
  (que ejecuta `receive`+`materialize` reales del entrypoint instalado), pero la clase
  `TestT4SmokeInstalled` deja el «funciona» a otra clase. Cerrarlo costaría una llamada
  `--help` con rc==0. Opcional; no bloquea.

### FYI — typo cosmético

`41b1663` nombra el archivo con guion (`test_003-002_t4_integration.py`) en el mensaje; el
archivo real usa underscore (coincide con el plan, `plan.md:364`). Sin efecto en el
contrato.

## 4. Lo que NO es hallazgo (verificado y descartado)

- La simulación `reconcile_state` del test escribe el state — pero es la simulación del
  orquestador (único escritor permitido, §9), y el test verifica además que ninguna
  herramienta la toca después (`:744-748`).
- El recorrido no usa T3 (`run-python-unittest`) — el plan declara `consume` de
  `cdad-run-evidence` (`plan.md:344-350`), pero la integración de P5 está cubierta por las
  unidades de T3 y la estrategia común (`plan.md:384`); ninguna postcondición de integración
  queda sin test.
- Import cross-feature `from test_004_002_t2_bootstrap import tree_snapshot` (`:50-52`) —
  reutilización declarada de un patrón ya revisado.

## 5. Abstenciones

1. **No re-corrió la suite completa (439/601 s):** citada bajo PD-5 con el árbol de
   producto verificado sin cambio desde `d7ffbcc`. Conforme al presupuesto de corridas;
   se abstiene de afirmar independientemente el conteo 439.
2. **No verificó empíricamente `validate-state` v2 sobre un state reconciliado con la
   referencia nueva:** contrastó el código (`cdad_packet.py:1264-1276`) y
   `validate-consistency.sh:92` y concluye que no hay regla que la rechace, pero ningún
   test del repo corre `validate-state` sobre ese estado. Confianza ≥80% por lectura de
   código; la confirmación de extremo a extremo corresponde al orquestador en el cierre.
3. **No re-auditó línea por línea T1–T3** (mandato del encargo: ya revisadas en
   `review-t1/t2/t3` y sus re-reviews).

## 6. Evidencia de la revisión

```
sha256sum docs/specs/003-002-artifact-tools/spec.md
→ ba73e645…01f37  (= contrato del paquete)

git show --stat 41b1663 → +768 tests/test_003_002_t4_integration.py
git show --stat d7ffbcc → +38 skills/cdad-cycle/references/re-entry.md

cd tests && python3 -m unittest test_003_002_t4_integration -v
→ Ran 6 tests in 31.149s — OK

git diff d7ffbcc..HEAD --stat → sólo docs/.cdad-state.json y dispatch-ledger.md
git status --porcelain → sólo " M docs/.cdad-state.json" (preexistente del orquestador)
```

**Archivos modificados por esta revisión: ninguno. Commits: ninguno** (`write_scope` vacío).

## 7. Dictamen

La integración T4 es correcta y la evidencia sólida: protocolo conforme a §9/§6, claims (b)
fundados y verificados, 6 guards observables sin frases ni mocks, sin regresión. El cierre
de la feature queda condicionado **única y exclusivamente** a la familia **F1**
(BLOCKING, una pasada de documentación con dos cláusulas): F1.1 (cláusula de staging del
TEXTO FINAL en `re-entry.md`) y F1.2 (`README.md` o decisión registrada del dueño). F2/F3
son opcionales y no prolongan el ciclo (regla 6).
