## Informe del implementer — 005-013 T2 GREEN

### (a) Qué implementé y dónde

Único archivo tocado: **`skills/cdad-cycle/scripts/cdad_packet.py`** (+430/−20).

**Operación de veredicto `validate-unit-contract` (PD-7..PD-11)**
- `validate_unit_contract(...)` — `:3941`: operación **de lectura**; `current`/`impact` → rc=0 (salida en stdout); `impeded` (autorización retirada) → `PolicyError` → rc=2 **sin efectos**. Sólo en `impact` escribe su journal.
- `_unit_contract_verdict(...)` — `:3789`: núcleo compartido (read-only) que regenera la proyección viva, resuelve la línea base y clasifica **por parte** (ignorando el origen).
- `_resolve_live_unit_projection(...)` — `:3574`: regenera la proyección viva con **el mismo generador e insumos de origen que `prepare`** (o `fallback` declarado si la unidad no se localiza).
- `_baseline_projection(...)` — `:3686`: la **proyección registrada del último paquete de la unidad** (orden por fecha de publicación de `UNIT-CONTRACT.md`, empate → id mayor; el `active_packet` cuenta como candidato; filtrado por `REQUEST.json.feature_id`); sin candidato → sin línea base.
- `_projection_parts(...)` — `:3627` y `_changed_projection_parts(...)` — `:3658`: descomposición por **identidad y clase de parte** (`unit` literal; título de sección para `shared`), sin listas de palabras (INV-8). El origen nunca es una parte.
- `_authorization_withdrawn(...)` — `:3736` / `_withdrawn_reason(...)` — `:3782`: **única** causa de `impeded`: sin entrada `epic_history` `epic-plan` con `approved_by` (marcador `approval pending`) o `hitl_delegation` revocada/no activa (marcador `state incoherent`); la salida nombrada es registrar la aprobación `epic-plan` / restituir la delegación. **Ninguna sección del plan** produce `impeded`.

**Journal durable idempotente (PD-9/INV-3/INV-9)**
- `_write_impact_record(...)` — `:3884`: escribe `.cdad/packets/<baseline_packet_id>/.impact.json` (forma de `.superseded.json`: `reason`, `contract_sha256_old`, `contract_sha256_new`, `changed_parts`) con escritura atómica (`tmp` + `os.replace`); **idempotente por par de digests** (mismo par → bytes idénticos; par distinto → agrega registro sin pisar). `_impact_records_in(...)` — `:3865`.

**Bloque `unit_contract` de `status` (PD-11/P1, aditivo y de sólo lectura)**
- `_unit_contract_status(...)` — `:3841` (reescrita): informa `mode`, `unit`, `registered {packet_id, sha256}|null`, `live {sha256}|null`, `verdict`, `changed_parts`, `reason`; **no escribe** (state byte-idéntico, sin proyección, sin journal). Conserva los campos de `compact-view-v1` y no incluye los bytes de la proyección.

**CLI**: subparser `validate-unit-contract --project-root` — `:4982-4986`; dispatch en `main()` — `:5122`. Sin cambios en `cdad_result.py` ni en el pin `specification` ni en la política.

Las tres inferencias del focal se respetaron: (a) `changed_parts` = `unit` / título de sección; (b) el veredicto se emite en stdout (`_format_unit_contract_verdict`, `:3922`) además del rc y el journal; (c) marcador `state incoherent` para la delegación revocada. Ninguna contradijo el contrato.

### (b) Focal (verde)
```
python3 -m pytest tests/test_005_013_t2_change_classification.py -q
...............                                                          [100%]
15 passed in 10.71s
```
(Medición RED previa a implementar: `15 failed in 8.85s`.)

### (c) Regresiones declaradas (verdes)
```
python3 -m pytest tests/test_packet_prepare.py tests/test_005_001_t1_role_approval.py \
  tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py \
  tests/test_005_007_t3_open_unit.py tests/test_005_005_t1_replace_conserved.py -q
...........................................................              [100%]
59 passed in 43.32s
```
Regresión proporcional adicional (el área que reescribí la ejercita): `python3 -m pytest tests/test_005_013_t1_unit_projection.py -q` → `15 passed in 6.91s`. Lint: `ruff check skills/cdad-cycle/scripts/cdad_packet.py` → `All checks passed!`. La suite completa **no** se corrió (la corre quien cierra).

### (d) Diff acotado y control de `tests/`
```
git diff --stat HEAD^..HEAD
 skills/cdad-cycle/scripts/cdad_packet.py | 450 +++++++++++++++++++++++++++++--
 1 file changed, 430 insertions(+), 20 deletions(-)

git diff --stat ef1ab47..HEAD -- tests/
(empty)          # tests/ SIN TOCAR
```
`docs/.cdad-state.json` figura modificado pero es un cambio **pre-existente del orquestador** (ya estaba `M` antes de empezar), fuera de mi alcance de escritura: **no lo toqué ni lo commiteé**.

### (e) Commit
```
da3ced5 feat: 005-013 T2 GREEN — veredicto de consecuencias (current/impact/impeded, línea base por parte, journal idempotente, salida del impedimento y bloque unit_contract de status de sólo lectura)
```

### (f) Puntos donde me detuve / observaciones
No me detuve: ninguna inferencia del focal contradijo el contrato, y ninguna decisión exigió clasificar prosa (INV-8), escribir el state (INV-1) ni una operación nueva de reconciliación (005-012).

Observación honesta (pre-existente, **no** causada por este cambio): `make validate` reporta 2 FAIL ajenos a mi diff — `scripts/validate-subagents.sh` (drift de agentes instalados en `~/.claude`/`~/.config/opencode`) y `tests/validate-odoo-specialization.sh` A3 (patrones sensibles en `docs/`/`tests/` pre-existentes). Verificado en un worktree limpio en el commit base `ef1ab47`: el drift de agentes falla igual en base, y el A3 depende del archivo gitignored `tests/.sensitive-patterns.local` (presente sólo en el árbol principal; ninguno de los archivos señalados es el mío). No los toqué; quedan para el cierre/orquestador.
