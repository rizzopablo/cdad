## Verificación básica del autor (tests primero)

- RED `c2b5903` (test-writer) toca **solo** `tests/` (archivo nuevo +621); GREEN `43c9deb` (implementer) toca **solo** `skills/` (script + 2 schemas). Separación de roles limpia, **sin debilitamiento de oráculos** (ningún test existente modificado en el rango).
- Los 6 focales mapean 1:1 a postcondiciones del review previo y de `review-t3-decision.md`; superficie observable = CLI subprocess, sin imports ni mocks; fixtures etiquetados `simulation: true` (P6); snapshots del árbol tomados después de crear fixtures (lección `5ee784e` aplicada). El caso positivo (intentos distintos) es guarda de regresión correcta del fix F2.
- Suite completa: 475 passed en `43c9deb` según el orquestador (no re-ejecutada por instrucción). Yo re-ejecuté **solo los focales nuevos** (ver abajo): 6/6 OK.

## Cierre de los focales (verificado por lectura + probes propios)

### F1 — Containment de `record` — **CERRADO**
- `_segment()` (espejo exacto de 002: `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`, sin `..`, sin absolutos) se aplica a `execution_id`, `packet_id` y `kind` **antes de cualquier `mkdir`/escritura**; rechazo rc=2 con diagnóstico stderr y cero escrituras (`cdad_guard.py:833-853`).
- Mi probe adicional: `packet_id="../esc"` → rc=2 sin escrituras; `kind="../../esc"` → rc=2 sin escrituras; el árbol del repo quedó intacto tras toda la sesión de probes.
- Focal `test_f01_…`: traversal + variante absoluta, cero escrituras dentro y fuera de la raíz ✓.

### F2 — Creación exclusiva — **CERRADO**
- `durable_path.exists()` → rc=2 "conflict: refusing to overwrite the durable evidence", antes de `mkdir`/`write_text` (`cdad_guard.py:863-871`); bytes originales intactos, probado por el focal con payload distinto.
- Colisiones de `_slug` eliminadas: `_slug` ya no existe en el código (solo mención en comentario y un `.pyc` viejo) y el nombre de archivo se construye de segmentos exactos que la regex **no permite** contener separadores (espacio incluido) — `"a b"` ya ni siquiera es aceptado como segmento. Sin vía de colisión restante.

### F3 — Schema ejercitado — **CERRADO**
- `validate_event()` alineado: rechaza campos extra (`EVENT_KEYS` ↔ `additionalProperties:false`) y `action` fuera de la tabla cerrada D5 (`cdad_guard.py:543-583`); mi probe: `action="resume-same-session-typo"` → rc=2 con la tabla impresa.
- `guard-event.schema.json` declara el enum con las 8 acciones de `CLOSED_ACTIONS` (verificado igualdad conjunta por lectura).
- Focal `test_f03_…`: evento persistido validado contra el asset con un validador JSON-Schema mínimo stdlib **fail-closed** (keyword no soportada → fallo explícito, no valida de menos) ✓.

### O1 — `receipt_ref` cita el receipt — **CERRADO**
- `_find_receipt()` busca `receipt.json` nominalmente (directo, luego `rglob("receipt.json")`), nunca `bundle.json`/`parts/` (`cdad_guard.py:589-609`). Focal con layout real de 002 sembrado (`parts/`, `bundle.json`, `receipt.json`) ✓.

### O2 — Contexto de dedup en `escalation-v1` — **CERRADO** (con observación, abajo)
- El paquete lleva `execution_id`, `packet_id` y `fingerprint` canónico (`canon(tool+args+result_class)`, `cdad_guard.py:314-320`). Focal lo verifica sobre el canal `classify` ✓.

## Regresiones

- Ningún test existente modificado; diff limpio de checkpoints 003-004 y de `docs/.cdad-state.json` desde el implementer (los toques al state en el rango son bookkeeping del orquestador, commits `2051674`/`0d9d180`). Suite 475 passed por evidencia del orquestador + focales 6/6 verificados por mí.

## Hallazgos (ninguno bloqueante)

### A1 — O2 residual: `execution_id`/`packet_id` del trace son **opcionales** en el schema; la escalada puede emitir `null` (D11/T5)
- **Lugar:** `skills/cdad-cycle/assets/guard-trace.schema.json` (propiedades añadidas pero **no** en `required`) + `_escalations()` (`context.get(...)` → `None`).
- **Consecuencia:** sobre una traza sin contexto de ejecución, `escalation-v1` emite `execution_id: null` y el `dedup_key` declarado no puede derivarse de lo que el canal emite — justo lo que O2 quería prevenir para T5. El cierre del focal cubre la traza que sí declara el contexto.
- **Remedio:** exigirlos en `guard-trace.schema.json` (o documentar la semántica null para T5).
- Veredicto: **OPTIONAL** · Bucket: **m**

### A2 — Doble fuente de verdad `CLOSED_ACTIONS` ↔ enum del schema, sin test de sincronía
- **Lugar:** `cdad_guard.py:118-129` vs `guard-event.schema.json` (`action.enum`).
- **Consecuencia:** un drift futuro (acción nueva en la tabla pero no en el enum) persistiría eventos que violan el schema declarado; los focales actuales solo ejercitan `resume-same-session`/`retry`, no lo detectarían.
- **Remedio:** un test que compare `sorted(CLOSED_ACTIONS)` contra el enum del asset, o generar el enum desde la tabla.
- Veredicto: **OPTIONAL** · Bucket: **l**

### A3 — Asimetría de cobertura en F1 (Nit)
- Los focales ejercitan solo `execution_id` inseguro; el rechazo de `packet_id`/`kind` inseguros está implementado (probe 1/2 verificado) pero sin test en la suite. Parametrizar el focal sobre los tres labels. Veredicto: **OPTIONAL** · Bucket: **l**

### A4 — Escritor más estricto que el schema declarado (Nit)
- El schema acepta `execution_id: "../x"` (solo `minLength:1`) mientras el escritor lo rechaza: dirección segura, pero el contrato declarado es más ancho que la conducta garantizada. Declarar el patrón de segmento en el schema eliminaría la asimetría. Veredicto: **OPTIONAL** · Bucket: **l**

### FYI — `budget` con `execution_id` absoluto lee fuera de la raíz
- Probe: `execution_id="/tmp"` → rc=0, sin traceback, vacío (joinpath descarta el prefijo y lee `<abs>/guards`). Es **solo lectura** (nunca escribe), así que no viola containment de escritura; anotado para T5 por si `budget` gana surface.

## Verificación realizada (solo lectura; write_scope vacía)

**Modified files por este reviewer:** ninguno. El único cambio sin commitear en el árbol es `docs/.cdad-state.json` (bookkeeping del orquestador: packet 006 `dispatched`) — no mío, no tocado.

Comandos y salidas:
- `git log --oneline 5604725..43c9deb` · `git diff --stat 5604725..43c9deb` · `sha256sum docs/specs/003-003-progress-guards/spec.md` → `731cca5b…` = contract sha ✓
- `git diff 5604725..43c9deb -- <script+schemas>` · lectura completa de `cdad_guard.py` (secciones `record`/`validate_event`/`_segment`/`_find_receipt`/`_collect_attempts`/`canonical_fingerprint`), `guard-event.schema.json`, `guard-trace.schema.json` (required list), tests focal nuevos (621 líneas)
- `git diff 43c9deb..HEAD --stat` → solo docs/state (implementación idéntica al commit evaluado)
- `python3 -m unittest discover -s tests -p "test_003_003_t3_reviewfix.py" -v` → **Ran 6 tests … OK** (4.1 s)
- Probes adversariales en tempdir `/tmp/opencode/cdad-rereview-probe` (CLI del repo, `--project-root` temporal): packet_id traversal → rc=2 sin escrituras · kind traversal → rc=2 sin escrituras · action fuera de tabla → rc=2 · budget con execution_id absoluto → rc=0 lectura inofensiva. Árbol del repo intacto tras los probes.

**Commit:** ninguno producido (write_scope `[]`). Evaluado: `43c9deb` sobre base `5604725`.

## Abstenciones

- **Suite completa (475 tests):** no re-ejecutada por instrucción explícita del orquestador; la acepto como evidencia provista (ledger filas 24-25) y verifiqué independientemente que la implementación es idéntica entre `43c9deb` y HEAD.
- **O3/O4:** en deuda declarada por decisión; no re-abiertos (instrucción del orquestador).
- **Dedup end-to-end (P7/D11):** mecanismo T5, aún inexistente; solo constaté A1 sobre la interfaz.
- **Señales reales (DB viva / traces de producción):** fuera del alcance del diff.

**Resumen:** F1, F2, F3, O1, O2 **cerrados** y verificados con focales + probes independientes. Sin bloqueantes. Quedan 4 observaciones no bloqueantes (A1 la más relevante para T5).
