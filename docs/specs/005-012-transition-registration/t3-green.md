# Informe GREEN — 005-012 T3 (`implementer`, subetapa `green`) — ENTREGA CON BLOQUEO DECLARADO

**Rol:** implementer · **Subetapa:** `green` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Paquete:** `005-012-transition-registration-implementer-green-004` · **Tarea:** T3
**Contrato (aprobado):** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) — PD-8, PD-9, PD-21 (+ PD-12(iv), PD-20, PD-11, PD-10, PD-17) · **Plan:** `plan.md` §4 ficha T3 · **Oráculo congelado:** `tests/test_005_012_t3_closure_dispatch_resolution.py` (RED `99b65e6`).
**Archivo modificado (único):** `skills/cdad-cycle/scripts/cdad_packet.py` (sha256 `308c0c99…7185c`, +269/−2).
**Commit:** `0057a50` — `feat: 005-012 T3 GREEN — closure (comprobacion antes de aplicar) y disposition (B1; PD-8/PD-9/PD-21)`.
*Nota de anonimización:* la raíz del repo se cita como `<repo>`; se sustituyó también en las salidas pegadas (única alteración de las salidas: la ruta). Sin ids crudos de sesión ni nombres de otros proyectos.

## Resultado en una línea

**7 de los 8 focales pasan.** El octavo — `test_pd9_closure_applied_records_evidence_and_rests` — **es inalcanzable sin editar el test**: su fixture (`_BaseFixture`, T1, modo `ready`) **nunca escribe el documento de cierre** `docs/specs/<feat>/closure.md` que el propio test cita y cuyo digest (`sha256(CLOSURE_BYTES)`) exige. Me **detengo** en ese caso y lo reporto (regla del rol: *no editar tests; si un test contradice el contrato, detenerse y reportar*), con la implementación de PD-9 **verificada aparte** contra todas las aserciones del test (ver el bloqueo). No inventé digest, no fabriqué bytes y no toqué `tests/`.

## (a) Qué implementé y dónde

Todo en `skills/cdad-cycle/scripts/cdad_packet.py` (clase `register-transition`, vocabulario y parser). **Aditivo**: sin las clases nuevas el comportamiento no cambia y ninguna validación nueva exige campos a las entradas históricas.

**1. Vocabulario y constantes** (`TRANSITION_CLASSES`, bloque T1)
- `TRANSITION_CLASSES` pasa a `("delivery", "advance", "gate", "closure", "disposition")`. **`late-delivery` NO se agrega**: es T4 (excluido por el encargo).
- `DISPOSITION_STAGE = "dispatch-disposition"` (etiqueta canónica, §2.1/D-13) y `DISPOSITION_RESOLUTIONS = ("abandoned", "superseded")` (vocabulario cerrado, PD-21).

**2. Predicados derivados nuevos** (junto a `_packet_is_dispatched`/`_packet_has_receipt`, que se **consumen sin re-declarar**)
- `_dispatched_packet_ids()` — paquetes de la **ejecución activa** con registro de despacho en `.cdad/executions/<exec>/dispatches/*.json`; **los despachos repetidos de un mismo paquete cuentan una vez** (PD-8(a)).
- `_packet_has_disposition()` — hay una entrada de `stage_history` con `transition: "disposition"` que **nombra** ese `packet_id` (la disposición **satisface PD-8(a)**, condición 2 de B1).
- `_feature_status()` y `_missing_required_deliveries()` (paquetes despachados **sin** recibo durable **ni** disposición).

**3. Clase `disposition` (B1, PD-21)**
- `--transition disposition --packet <id> --resolution <abandoned|superseded>` — con `--replaced-by <packet-id>` **obligatorio** para `superseded`.
- `--stage` **no se acepta** (§2.1/D-13): el CLI usa la etiqueta canónica y rechaza la invocación que traiga `--stage`.
- Comprobaciones **antes de escribir**, todas → rc=2 `state incoherent` nombrando el hecho: `--resolution` declarada; `--replaced-by` presente para `superseded`; `--packet` citado; el paquete **pertenece a la ejecución activa** (`REQUEST.json` de la ejecución); tiene **registro de despacho** (`dispatched`); **no** tiene **recibo durable** (la evidencia contradice la disposición); la feature está **abierta** (`epic_features[].status` fuera de `CLOSED_FEATURE_STATUSES`).
- Escribe **solo** la entrada de traza: `transition: "disposition"`, `stage: "dispatch-disposition"`, `resolution`, `replaced_by` (si corresponde), `packet_id`, `approval_effect: false`, `transition_key` — **sin** `approved_by`. **No toca** `active_packet` (no fabrica un `completed`), `epic_features`, `closed_at`, `active_feature`, `current_stage`; su única escritura de estado es la entrada (`+ last_updated`). **Idempotente por `transition_key`** (que ahora incorpora `resolution`): repetir la invocación idéntica → rc=0, sin segunda entrada, state byte-idéntico, salida que nombra la clave; otra resolución → entrada nueva (append).

**4. Clase `closure` (PD-8 + PD-9 + PD-20)**
- `--transition closure --stage <token> --approve-by <texto> --closure-path <p> [--closure-sha256 <hex>]`; `--approve-by` no vacío (PD-6).
- **PD-8(a)**: cada paquete despachado de la ejecución activa necesita **recibo durable o disposición**; si falta → rc=2 **`evidence missing`**, **nombrando el `<packet_id>`** y el recibo faltante (`receipt.json`), y **ofreciendo las dos salidas legítimas**: recibir por el camino normal (`receive` + `--transition delivery`) o **disponer** (`--transition disposition`, feature abierta). **`late-delivery` no se ofrece** (es de feature cerrada; B1).
- **PD-8(b)**: debe existir una entrada **`specification`** de la feature activa **vigente** (lector de T5, `_approved_spec_entries`, **consumido**) cuyo pin **nombra** el contrato `docs/specs/<feat>/spec.md` con su **digest derivado de los bytes actuales**; si falta, el pin diverge o el contrato no existe → rc=2 **`approval pending`** nombrando la feature, el contrato y la entrada `specification`.
- Ambas comprobaciones ocurren **antes de leer el documento de cierre** y antes de cualquier escritura (rechazo = state byte a byte idéntico, INV-7).
- **PD-9/PD-20**: `--closure-path` pinneado (digest **derivado** o verificado; ausente/divergente → `evidence missing`, sin efectos); efecto completo: entrada (`transition: "closure"`, `stage` declarado, `approved_by`, `closure_path`, `closure_sha256`), `epic_features[<feat>].status: "done"` + `closed_at` + `closure_evidence{path, sha256}`, `active_feature: null`, `current_stage: "idle"`, `active_packet: null`; `postconditions_status` **no** se vacía; historia **append-only**; el digest usado **se imprime**; **`_validate_idle_coherence` se verifica antes de publicar**.

**5. Parser**: `--closure-path`, `--closure-sha256`, `--resolution {abandoned,superseded}`, `--replaced-by`. La ayuda lista las cinco clases (T4 agregará la sexta).

## (b) Corridas (comando exacto + salida pegada con su línea de resumen)

**1. Focal de T3**
```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q --tb=line
..F.....                                                                 [100%]
<repo>/tests/test_005_012_t3_closure_dispatch_resolution.py:565: AssertionError: PD-9 violada: con las dos comprobaciones verdes el cierre debe aplicarse (rc=0); hoy rc=2: "ERROR: evidence missing: closure not found at 'docs/specs/demo-100-transition-fixture/closure.md'; the digest cannot be derived from absent bytes. Cite an existing closure path, or register the gate once the closure exists"
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd9_closure_applied_records_evidence_and_rests
1 failed, 7 passed in 18.61s
```
**Verde (7/8):** `test_pd8a_closure_with_unreceipted_dispatch_fails_closed_naming_evidence`, `test_pd8b_closure_without_vigent_specification_pin_fails_closed` (las dos variantes: falta la entrada / digest divergente), `test_pd21_disposition_of_unreceipted_dispatch_is_structural_and_does_not_touch_the_rest`, `test_pd21_b1_closure_rejects_then_the_disposition_unblocks_and_the_closure_advances`, `test_pd21_superseded_disposition_records_replaced_by`, `test_pd21_disposition_rejections_fail_closed_state_incoherent` (4 variantes), `test_pd11_pd21_identical_disposition_is_noop_and_another_resolution_appends`.
**Rojo (1/8):** `test_pd9_…` — bloqueo por fixture, no por implementación.

**2. Focales de T1/T2/T5 (lector, registro y forma)**
```
$ python3 -m pytest tests/test_005_012_t1_register_transition_base.py tests/test_005_012_t2_gate_authority.py tests/test_005_012_t5_approval_vigency.py -q
..................................                                       [100%]
34 passed in 33.72s
```

**3. Regresiones declaradas por la ficha**
```
$ python3 -m pytest tests/test_005_001_t3_idle.py tests/test_005_003_f2_idle_history.py tests/test_005_007_t3_open_unit.py tests/test_003_002_t1_receive.py -q
....................                                                     [100%]
20 passed in 26.26s
```

**4. Ensanche proporcional (mismo archivo compartido: `prepare`)**
```
$ python3 -m pytest tests/test_packet_prepare.py -q
...................                                                      [100%]
19 passed in 18.50s
```
La **suite completa no se corrió** (política del paquete: la corre una vez quien cierra).

## (c) Prueba de que `tests/` no se tocó

```
$ git diff --name-only 99b65e6..HEAD -- tests/
                                               # (sin salida: vacío)
$ git show --stat --oneline 0057a50 | tail -3
0057a50 feat: 005-012 T3 GREEN — closure (comprobacion antes de aplicar) y disposition (B1; PD-8/PD-9/PD-21)
 skills/cdad-cycle/scripts/cdad_packet.py | 271 ++++++++++++++++++++++++++++++-
 1 file changed, 269 insertions(+), 2 deletions(-)
$ git status --porcelain
 M docs/.cdad-state.json
```
`docs/.cdad-state.json` **no es mío**: es el registro del despacho de este paquete hecho por el orquestador.

## (d) Commit

```
$ git log -1 --format="%H %s"
0057a50f09dc47798ff4319e335c3e79e84ee2a1 feat: 005-012 T3 GREEN — closure (comprobacion antes de aplicar) y disposition (B1; PD-8/PD-9/PD-21)
```
Un solo archivo de implementación (+269/−2); prefijo `feat:`.

## (e) Interpretaciones, límites y el motivo por el que me detuve

**BLOQUEO (1 de 8 focales): `test_pd9_closure_applied_records_evidence_and_rests` es insatisfacible sin editar el test (no lo edité).**

1. El test **cita** `--closure-path docs/specs/demo-100-transition-fixture/closure.md` y exige que el `closure_sha256` de la entrada y de `closure_evidence` sea **el digest de los bytes citados**: `derived = hashlib.sha256(CLOSURE_BYTES)` con `CLOSURE_BYTES = b"# Closure fixture (demo-100 transition registration)\n"` (`:200`, `:557`, `:580`, `:606`) y que ese digest **se imprima** (`:584`).
2. Pero su fixture es `_BaseFixture(tmp_path, mode="ready")` (`:552`), la clase de T1, que **no escribe ese archivo**. Verificado sobre el árbol real del fixture:
```
$ python3 - <<'PY'   # crea _BaseFixture(tmp, mode="ready") y recorre el árbol
  docs/specs/demo-100-transition-fixture/spec.md (file)      # único archivo de docs/specs/
closure expected at: .../proj/docs/specs/demo-100-transition-fixture/closure.md exists: False
PY
```
3. El único punto del archivo de test que escribe `CLOSURE_BYTES` es `_ClosureFixture.__init__` (`:288`), y ese fixture **no se usa** en `test_pd9` (sí en los otros, que pasan). En un `_BaseFixture` "ready" el archivo **no existe en disco** y el CLI no puede derivar el digest de bytes ausentes: PD-20 exige `evidence missing` para un path ausente (no fabrico un digest: eso sería *gaming* del oráculo).
4. **Prueba de que el defecto es del fixture y no de la implementación** — arnés de diagnóstico fuera del repo (no es un test, no toca `tests/`, vive en el tempdir aprobado), que reproduce el fixture de PD-9 **más el documento de cierre que el test nunca escribe**, y espeja **todas** las aserciones de PD-9:
```
$ python3 /tmp/opencode/verify_pd9.py
---- closure stdout/stderr ----
registered transition closure stage 'feature-closure' for demo-100-transition-fixture
transition_key: 3591f331501228b85be3bcbc884acfee0bc9311355d7f4aff0011045601b8464
approved_by: Demo Approver
closure: docs/specs/demo-100-transition-fixture/closure.md 3fbe2105fbfbf815e7e8b7d03cb25673e88802a2d54c9c376b60b146f6e4b4c7
stage_history: 2 entries (+1)
-------------------------------
PASS  rc==0                              PASS  closure_evidence.sha256 == derived
PASS  entry exists                       PASS  active_feature is None
PASS  stage == feature-closure           PASS  current_stage idle
PASS  closure_path names the cited path  PASS  active_packet null or terminal
PASS  closure_sha256 == derived           PASS  one new entry
PASS  derived printed                    PASS  history append-only
PASS  approved_by                        PASS  validate-state rc=0
PASS  feature status done                PASS  validate-state prints idle
PASS  closed_at present                  PASS  closure_evidence.path names the closure
ALL PD-9 CHECKS PASS
```
5. **Fix mínimo del lado del test (para el test-writer, no para mí):** en `test_pd9_…` escribir el cierre citado antes de invocar, p. ej. `(fixture.root / CLOSURE_REL).parent.mkdir(parents=True, exist_ok=True)` + `(fixture.root / CLOSURE_REL).write_bytes(CLOSURE_BYTES)`. Con eso, el focal queda 8/8 sin cambiar una sola aserción. Alternativa: hacer que `_BaseFixture` (T1) materialice el cierre citado, o dar a `_ClosureFixture` un modo con recibo + cierre. **No lo hice yo** (los tests son el oráculo congelado).
6. **El RED no podía detectarlo**: con la clase `closure` inexistente, el test fallaba antes (`rc==0` con `invalid choice: 'closure'`), así que la ausencia del artefacto no se manifestaba como precondición.

**Interpretaciones declaradas:**

1. **Orden de PD-8 y del pin del cierre.** Las dos comprobaciones de PD-8 corren **antes de leer** el documento de cierre (orden PD-8 → PD-9). Lo **exige el oráculo**: `test_pd8b` espera `approval pending` con el documento de cierre **ausente** del fixture.
2. **`--stage` rechazado en `disposition`** (§2.1/D-13: no lo acepta; el CLI escribe la etiqueta canónica). No lo asevera ningún test; lo agregué porque el contrato lo declara.
3. **`--approve-by` obligatorio en `closure`** (PD-6) y **no** cableé `_gate_authority` al cierre: la comprobación de vigencia de la delegación es del gate (T2, PD-6) y no está en las referencias aplicables de este paquete (PD-8/PD-9/PD-21/PD-12). Declarado para que el orquestador lo confirme si quería además esa comprobación en el cierre.
4. **`active_packet: null` al cerrar** (PD-9 admite null o terminal): es lo que hacía el script histórico de cierre (discovery) y lo que satisface `_validate_idle_coherence`.
5. **No se ofrece `late-delivery`** en el rechazo del cierre: `receive`/`disposition` son las únicas salidas ofrecidas (B1; el test lo asevera).
6. **El rechazo de `superseded` sin `--replaced-by` no inventa marcador**: rc=2, sin efectos, **sin** ser error de uso del CLI.
7. **Entregas requeridas = solo la ejecución activa** (deuda D-11 declarada) y **sin interpretar el plan ni los paquetes** (INV-5/D-4): la condición de parada de la ficha **no se activó**.
8. **Límite declarado (no oculto):** repetir una invocación **idéntica de `closure`** cae en `active_feature: null` y la rechaza el guard existente («no active feature»), coherente con PD-12(i). El oráculo de T3 no lo ejerce; no lo cambié para no alterar el guard compartido.
9. **Fuera de T3 (no implementado):** `late-delivery`/`receive --late` (T4), el guard de contexto abierto (T6), el barrido D-2, cualquier juicio sobre si un despacho debe disponerse (INV-5).

**Estado final:** implementación commiteada y auditable, 7/8 focales de T3 verdes, T1/T2/T5 (34) y regresiones declaradas (20) + `test_packet_prepare.py` (19) verdes, `tests/` intacto; **el único rojo es el fixture de PD-9**, con el fix exacto propuesto al test-writer. Me detengo ahí y no avanzo por mi cuenta (no edito tests, no fabrico digests).
