# Review report — re-review FOCAL RU-2 (003-006-runtime-adoption)

**Packet:** `003-006-runtime-adoption-reviewer-review-006` · **Rol:** reviewer (solo lectura) · **Contrato:** `docs/specs/003-006-runtime-adoption/spec.md` (sha256 verificado: `dc485e80…a7d7cb7` ✓ coincide con el packet) · **Decisión:** `t4-ru2-decision.md` · **Diffs objeto:** `5ec6112..abcd4d3` (GREEN: `skills/cdad-cycle/scripts/cdad_continuity.py`, 1 archivo, +7/−6) y `46d4b14..4c14cce` (RED: test RU-2 nuevo + enmienda O1; solo `tests/`, +514/−13). HEAD al momento del review: `6774869`.

## Verificación del autor (lo que ejecutó)

RED (24cc9d9): test RU-2 documentado como RED por comportamiento presente-incorrecto (docstring con probes del 2026-10-07). GREEN (abcd4d3): hunk mínimo —elimina la única escritura prematura (`_write_synced(_body_path(…), body_bytes)` fuera del branch divergente, `cdad_continuity.py:~566`)—. Limpieza del huérfano `2aee8d80…` ejecutada por el orquestador con sha registrado en el ledger (`adoption-ledger.md:80`). Verificación del autor plausible y trazada; yo la reproducí por cuenta propia (abajo).

## Verificación propia (tiempo real, raíces temporales propias en `/tmp/opencode/ru2-replay/proj`, ninguna escritura en el repo)

Comandos exactos: fixture con `exec.json` real (identidad en `execution.id`) + `docs/.cdad-state.json` con delegación por eventos; luego `cdad_continuity.py begin/checkpoint/begin/reconcile…` como subprocesos con `--project-root`/`--execution-context` apuntando al tempdir; snapshots `find `.cdad` -type f/-type d`.

**E1 — Rechazo todo-o-nada (escenarios a+b+c): CERRADO.**
- `begin` válido → `bodies/ff1756f5….json` + `head.json` (seq 1), árbol exacto observado.
- `checkpoint` misma clave, cuerpo diverso → **rc=1**, stderr: `split-brain: a checkpoint with the same idempotency key … refusing to overwrite the head — escalate (O1/D7)`; `find` tras el rechazo: **árbol byte a byte idéntico** (ni cuerpo nuevo, ni head tocado, ni directorio nuevo).
- `begin` diverso misma clave → **rc=1**, mismo diagnóstico; árbol idéntico de nuevo.
- Estructural: la única llamada que crea directorios es `_write_synced` (`cdad_continuity.py:167`), y en el camino del rechazo ya no se invoca; `_load_head`/lecturas no crean nada. El cierre "ni directeur, ni cuerpo, ni directorios" se cumple también estructuralmente, no solo en el caso observado.
- Suite del repo como doble control: `python3 tests/test_003_006_t4_ru2_refused_write.py -v` → `Ran 2 tests … OK` (facetas a+b y c).

**E2 — `reconcile` ya no queda bloqueado: CERRADO.** Tras el rechazo, `reconcile --packet` → **rc=0**, `classification: "not-started"`, `escalate: false`, sin `divergent checkpoint heads`.

**E3 — No-op idéntico intacto (P3): CERRADO.** Re-mandar el cuerpo original → rc=0, `"no_op": true` en el stdout, `diff` del árbol antes/después vacío (0 escrituras).

**E4 — Encadenado intacto: CERRADO.** `checkpoint` attempt 2 → rc=0, head con `"seq": 2`.

**E5 — Split-brain lado de lectura intacto (D7): CERRADO.** Cuerpo forjado manualmente bajo la misma clave attempt 2 → `reconcile` rc=1 con `split-brain: divergent checkpoint heads for key …: [dos archivos]; the CLI never chooses a winner (D7)`. `_detect_split_brain` no fue tocado por el diff.

**E6 — Store real del proyecto: sin afectación residual.** Escaneo de `.cdad/executions/*/continuity/bodies/`: 003-004 → 1 cuerpo, 003-006 → 4 cuerpos, **dup-keys: NONE** (huérfano `2aee8d80…` retirado por el orquestador, única escritura, ledger registra el sha). El rechazo ya no puede crear dúplices nuevos.

**E7 — Regression-sweep del impacto del cambio de contrato:** las 12 suites de 003-004/003-006 pasan en el tiempo presente (003-004: 4/3/3/7/5/4/6/4 OK; 003-006: t1 9 OK, t2_activation **18 passed** vía `python3 -m pytest` — el run directo como script sale rc=0 silencioso porque es un módulo pytest, verificado aparte—, t3 15 OK, t4 RU-2 2 OK). Ningún test del ciclo anterior quedó rompiendo por el cambio de comportamiento.

## Análisis de la enmienda O1 (tercer punto del orquestador)

`tests/test_003_004_t2_writeahead.py::TestO1BeginDivergenteMismaClave`: **legítima y no debilita más de lo necesario — CERRADO.**
- Lo que fija la enmienda es exactamente el defecto que RU-2 corrige (el test original de 003-004 codificaba "el cuerpo diverso queda escrito y `reconcile` da split-brain permanente" — comportamiento presente-incorrecto que la decisión `t4-ru2-decision.md` revierte de diseño). Mantenerlo habría falsamente "regresado" el fix.
- **Mantenido sin debilitar:** rc≠0, mensaje de rechazo (más fuerte que antes: agrega `assertIn "split-brain"` que no existía — previene rc≠0 incidental), head byte a byte, seq estable.
- **Cambiado justificado:** store byte-a-byte (`store_files()` snapshot) y `reconcile` rc=0 sin split-brain.
- Alcance de la enmienda: solo esa clase + docstrings con referencia explícita a RU-2; ninguna otra aserción del archivo tocada (verificado en el diff completo).

## Hallazgos

| # | Severidad | Veredicto | Bucket | Hallazgo |
|---|-----------|-----------|--------|----------|
| F1 | — (defecto RU-2) | **cerrado** | — | Rechazo begin/checkpoint deja cuerpo huérfano → bloqueo permanente de `reconcile`. Corregido todo-o-nada; reproducido y probado (E1, E2). |
| F2 | — | **cerrado** | — | No-op idéntico P3 y encadenado intactos (E3, E4). |
| F3 | — | **cerrado** | — | Detección de split-brain lado lectura D7 intacta (E5). |
| F4 | Nested | **residuo** | **Nit** | Enmienda O1: la aserción del `reconcile` usa `assertNotEqual(classification, "split-brain")`; para esta geometría la clasificación determinista es exactamente `"not-started"` y una aserción de igualdad exacta sería más fuerte (atraparía además una clasificación inesperada rc=0). No debilita el cierre RU-2; es opcional. Ubicación: `tests/test_003_004_t2_writeahead.py:~414`. |
| F5 | FYI | **residuo (aceptado)** | **l** | Tras la limpieza, `reconcile` del packet viejo `…review-005` falla por `reference digest mismatch: dispatch-ledger.md changed since the checkpoint` (`evidence/t4/reconcile-after-cleanup-REF.txt`) — esperado y documentado en el ledger. Es la tensión de diseño preexistente entre referencias selladas y ledgers que crecen; **fuera del alcance de estos diffs** (no introducida por RU-2), solo la registro. |
| F6 | Nested | **residuo** | **Nit** | `tests/test_003_006_t4_ru2_refused_write.py` usa `subprocess.run(["rm","-rf", self._tmp])` en cleanup sobre un mkdtemp propio: seguro en el entorno presente, pero el estándar repo en otros tests es `shutil.rmtree`; portabilidad menor. |

**Ningún hallazgo bloqueante.** El diff GREEN es el cambio mínimo exacto que la decisión pedía; el RED mapea 1:1 con los escenarios a/b/c del orquestador; la enmienda O1 es la mínima necesaria.

## Contrato y alcance

- Escrituras del diff dentro de `path_policy`: `skills/` (GREEN) y `tests/` (RED/enmienda) ✓; ninguna escritura fuera de scope por parte del implementer. Cambios a `docs/.cdad-state.json`, ledgers y evidencia: commits 5ec6112/6774869 del **orquestador** (rol único escritor), consistentes con la decisión ("la limpieza la hace el orquestador a mano, con evidencia en el ledger").
- `sha256(spec.md)` = `dc485e80aa86b545c75c86f71a3fa590321c1ca6a66221e1115c69b75a7d7cb7` = hash declarado en el packet ✓.
- Working tree tiene solo `docs/.cdad-state.json` modificado (dispatch de este packet reviewer) — del orquestador, sin relación con el objeto revisado.

## Comandos y evidencia ejecutados (resumen)

1. `git log --oneline -8`, `git diff 5ec6112..abcd4d3`, `git diff 46d4b14..4c14cce` — objeto de review exacto.
2. Replay en `/tmp/opencode/ru2-replay` (fixture + 7 invocaciones del CLI + 3 snapshots `find`) — E1–E5.
3. `python3 tests/test_003_006_t4_ru2_refused_write.py -v` → 2/2 OK; `python3 tests/test_003_004_t2_writeahead.py` → 4/4 OK.
4. Sweep: 12 suites de tests/test_003_00{4,6}_*.py → todas OK (t2_activation vía `pytest`, 18 passed).
5. `sha256sum docs/specs/003-006-runtime-adoption/spec.md` → hash del contract ✓.
6. Escaneo de dúplices en el store real → NONE.

## Abstenciones

- No ejecuté `install.sh` ni los targets del Makefile del entorno (no forman parte del objeto de esta re-review focal; el wiring/install de 003-006 ya fue revisado en rotaciones previas).
- No verifiqué el contenido de la papelera física donde el orquestador archivó `2aee8d80….json` (el ledger registra el sha; el escaneo del store real muestra que no hay dúplices, que es la postcondición relevante).
- El estado no-committed de `docs/.cdad-state.json` (dispatch de este packet) corresponde al orquestador; no lo evalué.