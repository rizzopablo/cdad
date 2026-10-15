# GREEN T4 — 005-007-progressive-planning · implementer · subetapa green

**Packet:** `005-007-progressive-planning-implementer-green-005` (contract sha `54877103…`, policy sha `f508ab1e…`) · **Rol:** implementer · **Postcondición:** PD-8 · **Focal:** `tests/test_005_007_t4_architect_report_materialization.py` (oráculo congelado, commit `852d3be`) · **Trazabilidad:** ficha T4 del plan + observación 1 de `review-claude-spec-2026-10-13.md`.

## Cambio mínimo (scope declarado: `skills/`)

Se admitió el kind `role-report` — el que emite siempre el adaptador de la interfaz común (`cdad_delegate_opencode.py`, `FINAL_TEXT_ARTIFACT_KIND = "role-report"`) y el que lleva el recibo del discovery real de 005-007 — en la tabla cerrada de materialización (PD-8), **sin relajar la clausura del eje rol**.

1. `skills/cdad-cycle/assets/artifact-policy.json`: se declara `"role-report": "docs/specs/<feature>/"` (destino permitido = raíz PD-8). El kind declarado de la interfaz común queda con destino confinado a `docs/specs/<feature>/`.
2. `skills/cdad-cycle/scripts/cdad_result.py`, en `_allowed_kinds`: para el rol `architect` se conservan `architect-spec-draft`/`architect-plan-draft` y se añade `role-report` sólo en las subetapas `discovery` y `draft` (los subfases reales del informe/draft del architect). El resto de subetapas del architect mantiene la tabla previa intacta.
3. **Eje rol cerrado preservado:** los kinds *nombrados* de otro rol (`implementer-role-report`, `test-writer-role-report`) siguen en la tabla de kinds pero NO entran en los kinds admitidos del architect ⇒ siguen rechazándose incluso con paquete del architect. Destino confinado a `docs/specs/<feature>/`; binding de autorización (`receipt_sha256`) y `approval_effect: false` sin cambios; `receive` sin cambios.
4. No se tocó el adaptador OpenCode (evita duplicar en el adaptador el mapa rol→kind que vive en `cdad_result.py`).

No se editó ningún archivo de `tests/` (AP-4), no se creó `debt.md` ni se tocó `docs/`.

## Evidencia

### Oráculo congelado (7 passed)

```text
$ python3 -m pytest tests/test_005_007_t4_architect_report_materialization.py -q
.......                                                                  [100%]
7 passed in 16.89s
```

(Hoy RED era `1 failed, 6 passed` por AssertionError en el caso 1; los 6 controles 2-5 siguen verdes.)

### Regresión declarada por la ficha T4

```text
$ python3 -m pytest tests/test_003_002_t1_receive.py -q
.......                                                                  [100%]
7 passed in 8.45s

$ python3 -m pytest tests/test_003_002_t2_materialize.py -q
...........                                                              [100%]
11 passed in 24.19s
```

### Lint

```text
$ python3 -m ruff check skills/cdad-cycle/scripts/cdad_result.py
All checks passed!
```

### Diff y commit

```text
$ git diff --stat -- skills
 skills/cdad-cycle/assets/artifact-policy.json | 1 +
 skills/cdad-cycle/scripts/cdad_result.py      | 9 ++++++++-
 2 files changed, 9 insertions(+), 1 deletion(-)

$ git show --stat --oneline HEAD
512d913 feat: 005-007 T4 GREEN - admitir role-report (informe del architect / interfaz de delegacion) en la tabla cerrada de materializacion (PD-8)
 skills/cdad-cycle/assets/artifact-policy.json | 1 +
 skills/cdad-cycle/scripts/cdad_result.py      | 9 ++++++++-
 2 files changed, 9 insertions(+), 1 deletion(-)
```

**Commit del rol:** `512d913` (prefijo `feat:`), rama `codex/epic-005-real-operation`, sólo los 2 archivos de `skills/`. `docs/.cdad-state.json` queda con el diff del orquestador (transición del packet); no lo toqué ni entró en el commit.

## Límite declarado (observación 1 de `review-claude-spec-2026-10-13.md`)

Un draft del architect entregado por la interfaz común (`cdad_delegate_opencode.py`) llega como **UNA SOLA parte** con `artifact_kind: role-report`. Con esta mejora **ese informe es materializable** (PD-8, el caso positivo T4). Pero **un draft de UNA parte NO puede materializarse como `spec.md` + `plan.md` (dos artefactos)**: la tabla cerrada mapea un kind→un destino por parte, y una única parte no puede poblar dos targets.

Esto **NO se resuelve aquí** y se registra como límite con su condición de cierre: **extender la interfaz/entrega para declarar partes por artefacto** (que el draft entregue dos partes distinguibles, cada una con su kind y su destino, en vez de una sola parte `role-report`). No se hizo pasar la parte única como spec.

## Invariantes respetadas (5 checks)

- **Early exit / guardas:** `_allowed_kinds` corta por rol/subfase; los caminos de rechazo siguen fallando cerrado (rc≠0, sin prefijo parcial).
- **Estados ilegales irrepresentables:** el eje rol sigue cerrado: kinds nombrados de otro rol no son admitidos para el architect; el destino queda confinado por `_allowed_target` + `_is_within`.
- **Predecible y atómico:** mismo input → mismo output; `role-report` con destino en `docs/specs/<feature>/` materializa con sha idéntico y sin tocar state/receipt.
- **Fail fast / loud:** un kind foráneo o un destino fuera de raíz falla con diagnóstico explícito antes de escribir.
- **Naming intencional:** `role-report` es el kind declarado por la interfaz (fuente única en `cdad_result.py`); el adaptador no se modificó.
