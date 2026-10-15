# Cierre — 003-002-artifact-tools (epic-003-context-efficiency)

**Estado: CERRADA (2026-10-06).** Aprobaciones de gate por el dueño (HITL delegada
al orquestador OpenCode); sin push. P1–P6 implementadas y verificadas.

## 1. Qué entrega la feature

Un CLI de artefactos sobre el runtime de paquetes **v2** (001/004-002), sin
redefinir sus esquemas:

| Operación | Entrega |
|---|---|
| `receive` / `validate-receipt` | Persiste los **bytes originales** de un rol de forma atómica (temp + fsync + rename) e **idempotente**; una sola finalización durable por `(execution_id, packet_id)`; retry idéntico devuelve el receipt **byte a byte**; conflicto no sobrescribe; recibo **mecánico que nunca aprueba** (`semantic_status` siempre `pending`) |
| `materialize` | Copia autorizada a targets canónicos: la tabla cerrada fija la **raíz permitida** por `artifact_kind` y el **target exacto se declara en la autorización**; create-only/CAS; journal durable; `approval_effect` siempre `false` |
| `run-python-unittest` / `validate-run-evidence` | Evidencia de suite: solo `python3 -m unittest` (argv sin shell); snapshots before/after calculados por la herramienta; `valid-current` exige exit 0, tests>0, alguno no skipped, cero failures/errors/runner exceptions, árbol no mutado y contrato vigente |

**Invariantes verificados:** un solo escritor del estado (**el orquestador**);
recepción ≠ materialización ≠ aprobación semántica; bytes conservados (SHA-256 y
longitud); evidencia desconocida o stale nunca es gate verde.

## 2. Tareas y evidencia

| Tarea | RED | GREEN | Review | Cierre |
|---|---|---|---|---|
| **T1** `receive` | `02ebb0e` | `3f619c4` | `review-t1.md` (R1–R3) → fix `980940d`/`2106766` → `review-t1-rereview.md` | cerrada |
| **T2** `materialize` | `0494ab5` | `db72fb4` | `review-t2.md` (R1–R5) → fix `4250026`+`8333649`/`92b60cf` → `review-t2-rereview.md` | cerrada |
| **T3** `run-evidence` | `ed71c50` | `84e3366` | `review-t3.md` (R1–R3) → 3 rondas de review-fix (`e045fb4`/`81a585a`, `feed7e1`/`32d290c`, `1f1c0f1`/`5c76fee`) → `review-t3-rereview.md` | cerrada |
| **T4** integración | `41b1663` (guards) | `d7ffbcc` | `review-t4.md` (F1 bloqueante) → fix `aabb614`+`b0f9ade` → `review-t4-rereview.md` | cerrada |

Detalle por tarea, hallazgos, disposiciones y lecciones:
`supervision-record.md`; filas de despacho: `dispatch-ledger.md`.

## 3. Integración (el objeto de T4)

Verificada por **dos vías independientes**:

1. **Desde el producto instalado, en raíz aislada** (`tests/test_003_002_t4_integration.py`,
   6 guards, `41b1663`): `install.sh --basic` con `CDAD_INSTALL_ROOT` a un tempdir →
   proyecto fixture **sin wrappers del repo** → recorrido `receive → materialize` con el
   entrypoint instalado: bytes idénticos, finalización única, retry byte a byte,
   retry de `materialize` idempotente, **state byte-idéntico** y retry con el state ya
   reconciliado sin repetir efecto.
2. **En uso real, en este repo** (primera vez que el flujo se usa para el trabajo):
   `prepare --record-dispatch` (I8) → staging del TEXTO FINAL del reviewer + `RESULT.json`
   + manifest → `receive` **rc=0** (`packet`/`identity`/`scope` = `passed`) →
   `materialize` create-only **rc=0** → `docs/specs/003-002-artifact-tools/review-t4-rereview.md`
   con **bytes idénticos** (`82a63fcb…`); retry de `receive` converge al mismo receipt;
   retry de `materialize` sin doble efecto. El staging ejecutado fue **exactamente la
   cláusula F1.1** que el review-fix acababa de escribir: el arreglo se validó en uso.
   El Memory Bank se materializó también por el flujo, **con CAS** contra el digest
   anterior exacto de los 3 targets (bytes verificados).

La referencia del recibo quedó en `stage_history` (`receipt_sha256`, `bundle_sha256`,
partes) — el ítem que el plan asigna al orquestador; las herramientas no escriben el state.

## 4. Gate de cierre

- **Suite completa: 439 passed** (`env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m
  pytest tests/ -q`), corrida por el orquestador sobre el árbol limpio en `8f5aaa5`
  (608.67 s). Reproducida por el implementer en `aabb614` (602.14 s).
- **Validadores:** `validate-consistency.sh` = **141 PASS / 2 FAIL**, ambos
  **preexistentes y ajenos** al diff (F011-A: drift de los mirrors de `$HOME`, irresoluble
  por la regla que prohíbe instalar CDAD en HOME real; F011-B: A3 marcando una palabra
  dentro de un identificador + ruido de `__pycache__`). Re-verificados por *stash* por dos
  roles distintos.
- **Ausencia de CI:** declarada (el gate es la suite local), conforme al criterio ya
  vigente de epic-004 (E3).

## 5. Revisiones y su calibración

Cuatro reviews de tarea + re-reviews focales, con familias de modelos distintas
(reviewer `mofgw/glm-5.3-flash` ≠ implementer `mofgw/deepseek-v4.1-flash`). Los reviewers
encontraron defectos materiales que el orquestador no había visto y el orquestador
**reprodujo** antes de ordenar el arreglo: escape de autoridad en `materialize` (R1 de T2),
alcance auto-elegido del runner (R1 de T3), y la cláusula faltante de staging (F1.1 de T4).

**Instrucción del dueño durante el ciclo** («el reviewer no debería ser infinitamente
detallista… pero no debe perder el objetivo de usabilidad del sistema»): en T3 el reviewer
enumeraba variantes sucesivas de la misma ligadura `argv`↔selecciones. Se aplicó el
**remedio de clase** fail-closed en **una** ronda (`5c76fee`) y se **precisó la
calibración** en su fuente canónica (`64362f8`: ponderar por contrato/usos/usabilidad;
todo bloqueante con evidencia + consecuencia + **condición verificable de cierre**; familia
resuelta como familia; re-review acotada; opcionales que no prolongan el ciclo;
fail-closed no es remedio universal). Registro histórico:
`docs/owner-decision-review-calibration-2026-10-05.md`.

## 6. Limitaciones y deuda

**Verificado:** recorrido real y desde el producto instalado (arriba); bytes conservados;
state con un solo escritor; CAS de Memory Bank ejercitado; idempotencia en uso.

**No ejercitado (pendiente, declarado):**
- `observation_status = "unknown"` — el manifest declarado en los dos usos reales fue
  `trusted` con `changes: []`. El camino `unknown` (que impide gate y materialización) no
  se ejercitó.
- La materialización de un **ADR** por la tabla de artefactos: los ADR quedan **fuera** de
  la tabla (§7); su materialización sigue siendo del orquestador (ADR-003) — la de ADR-014
  se hizo así.

**Deuda priorizada (no bloqueante):**
- **`README.md` sin clasificar** en `docs/cdad-policy.json` (no es `implementation_file` ni
  cae en `documentation_roots`): ningún rol puede escribirlo, y revisar la política está
  fuera de alcance de 003-002. El front-door no descubre el segundo CLI público.
  **Decisión del dueño pendiente** (clasificarlo o dejar la desviación registrada).
- Whitelist de `argv` más estricta de lo necesario (`--locals`, `-c` degradan a `unknown`;
  efecto real ≈ nulo, falla del lado conservador); doble motivo de diagnóstico;
  `_module_tree` sobre nombre imposible — deudas de T3.
- O1–O3 de T2 (target fijo en filas con nombre; journal indexado por string crudo;
  `materialize.schema.json` no se carga), FYI-1/FYI-2 de T2.
- R4/R6 de T1 (fachada pública de `scope_contains`/`project_path`; 6 nits mecánicos).
- F3 de T4 (la clase de smoke no ejecuta el entrypoint; el «funciona» lo cubre el guard 2).
- 2 FAIL preexistentes de validadores; ausencia de CI.

## 7. Desviaciones registradas

- **`contract.commit: null`** se interpretó como «sin pin de commit»; un rol lo leyó como
  «no commitear» y se reanudó su sesión para commitear con pathspec.
- **Lock flaky `R4a`** (carrera SIGSTOP/SIGKILL) detectado por el orquestador al **re-correr**
  (el rol reportó 6/6); reemplazado por el mecanismo determinista que la spec §8 autoriza.
- **Un test con defecto propio** en el RED de T3 (`AttributeError` por un helper
  inexistente) que se disfrazaba de falla contractual: se detectó al revisar la **razón** de
  cada falla, no el conteo.
- **`README.md`** diferido con razón (ver §6) y registrado en `plan.md`.
- La calibración de la review es una **enmienda declarada, no adoptada** en la versión
  operativa `8cb6580`: viajó como entrada declarada de los encargos de reviewer.

## 8. Siguiente

`003-003-progress-guards` (queued, no implementada por anticipado). Punto de entrada vigente
del epic: `docs/epics/epic-003-context-efficiency/handoff-resume-2026-10-05.md`.
