# Informe — T3 testfix (`test-writer`, subetapa `red`, ronda de testfix)

**Rol:** test-writer · **Subetapa:** `red` (testfix) · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Paquete:** `005-012-transition-registration-test-writer-red-005` · **Tarea:** T3
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) — **PD-9 / PD-20** (+ PD-17, PD-8)
**Archivo tocado (único):** `tests/test_005_012_t3_closure_dispatch_resolution.py`
**Commit:** `016405f` — 1 archivo, +14 líneas (solo el fixture/precondición)

## (a) El fix exacto y su justificación

**Defecto (confirmado):** `test_pd9_closure_applied_records_evidence_and_rests` construye su fixture con `_BaseFixture(tmp_path, mode="ready")` y cita el cierre `CLOSURE_REL = docs/specs/<feat>/closure.md`, pero el fixture base `mode="ready"` **no escribe ese documento**. El único punto que escribía `CLOSURE_BYTES` era `_ClosureFixture.__init__`, que este caso **no** usa (sus modos `single`/`double` dejan un despacho sin recibo, lo que rompería el aislamiento de PD-9, que requiere **todas** las entregas satisfechas). El CLI rechazaba la invocación antes de aplicar el cierre — reproducido tal cual:

```
ERROR: evidence missing: closure not found at
'docs/specs/demo-100-transition-fixture/closure.md'; the digest cannot be
derived from absent bytes. Cite an existing closure path, or register the gate
once the closure exists
```

Es coherente con el contrato: **PD-20** manda `evidence missing` cuando el archivo citado está ausente y **PD-9** exige que el cierre citado exista y que su digest se derive de sus bytes. Las **dos aserciones del test son correctas**; lo que faltaba era la **precondición del fixture**. En el RED no se manifestó porque la clase `closure` todavía no existía y el CLI fallaba antes por error de uso (`invalid choice`).

**Fix (solo fixture/precondición, sin tocar ninguna aserción):** en el caso de PD-9, tras comprobar el recibo y **antes** de invocar el cierre, materializo el documento citado en la ruta declarada con el contenido `CLOSURE_BYTES` que el propio test ya declara:

```python
    closure_file = fixture.root / CLOSURE_REL
    closure_file.parent.mkdir(parents=True, exist_ok=True)
    closure_file.write_bytes(CLOSURE_BYTES)
    assert closure_file.is_file(), (
        "precondición (fixture): el cierre citado existe en la ruta declarada")
```

(`derived = hashlib.sha256(CLOSURE_BYTES).hexdigest()` sigue calculándose sobre los mismos bytes, así que el oráculo queda intacto: el digest esperado se deriva de esos bytes.)

**Justificación de la forma elegida:** de las tres opciones admitidas por el encargo —(1) escribirlo en ese test, (2) hacerlo en el fixture base, (3) dar a `_ClosureFixture` un modo «recibo + cierre»— elegí **(1)**: solo un caso lo necesita; la opción (2) tocaría `tests/test_005_012_t1_register_transition_base.py` (archivo fuera del alcance del encargo); la opción (3) modificaría una clase compartida y su superficie, con riesgo para los otros casos. Cero cambios de aserciones: es una precondición añadida.

**Reglas respetadas:** fixture **sintético y anónimo** (mismos ids inventados del archivo: `demo-100-transition-fixture`, `ses-demo-*`); sin rutas absolutas del dueño; **no** toqué ningún otro test ni la implementación (`skills/**`); ningún archivo fuera de `tests/`; no leí código de implementación.

## (b) Focal completo — salida pegada

```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q
........                                                                 [100%]
8 passed in 15.94s
```

Aislamiento del caso corregido, antes del cambio:

```
$ python3 -m pytest "tests/...::test_pd9_closure_applied_records_evidence_and_rests" -q --tb=short
1 failed in 1.22s   → rc=2 "evidence missing: closure not found at 'docs/specs/demo-100-transition-fixture/closure.md'"
```

y después:

```
1 passed in 1.47s
```

## (c) Diff del archivo de test — solo la precondición

`git diff 99b65e6..HEAD -- tests/test_005_012_t3_closure_dispatch_resolution.py` (muestra **únicamente** el fixture/precondición; ninguna aserción cambia):

```diff
@@ -552,6 +552,20 @@ def test_pd9_closure_applied_records_evidence_and_rests(
     fixture = _BaseFixture(tmp_path, mode="ready")
     assert fixture.receipt_path().is_file(), (
         "precondición (fixture): el paquete despachado tiene recibo durable")
+    # Precondición (fixture): materializar el documento de cierre que este caso
+    # cita, con los bytes declarados, en el path relativo `CLOSURE_REL`. El
+    # fixture base `mode="ready"` NO lo escribe (sólo `_ClosureFixture` lo hace,
+    # y sus modos dejan un despacho sin recibo: aquí se necesita TODAS las
+    # entregas satisfechas para que PD-8 esté verde y la única causa evaluada
+    # sea el cierre aplicado). Sin este artefacto el cierre rechaza por
+    # `evidence missing` (PD-20: el digest no se puede derivar de bytes ausentes)
+    # en vez de aplicarse (PD-9). Sólo precondición de fixture: ninguna aserción
+    # de contrato cambia.
+    closure_file = fixture.root / CLOSURE_REL
+    closure_file.parent.mkdir(parents=True, exist_ok=True)
+    closure_file.write_bytes(CLOSURE_BYTES)
+    assert closure_file.is_file(), (
+        "precondición (fixture): el cierre citado existe en la ruta declarada")
     before_state = fixture.read_state()
     before_entries = entries(before_state)
     derived = hashlib.sha256(CLOSURE_BYTES).hexdigest()
```

```
$ git show --stat --oneline HEAD | tail -3
016405f test: 005-012 T3 testfix — …
 tests/test_005_012_t3_closure_dispatch_resolution.py | 14 ++++++++++++++
 1 file changed, 14 insertions(+)
```

## (d) Commit

```
$ git log --oneline -1
016405f test: 005-012 T3 testfix — el fixture de PD-9 materializa el cierre citado (CLOSURE_BYTES) antes de invocar closure; 8/8 focales verdes, ninguna asercion cambia
```

`docs/.cdad-state.json` quedó **sin commitear** (es el registro del despacho del orquestador; no lo toqué). Sin `--no-verify`, sin push, sin despliegue, sin tocar el HOME ni `tests/.sensitive-patterns.local`.

## (e) Bloqueos

**Ninguno.** El diagnóstico del encargo se confirmó de punta a punta contra el comportamiento del CLI (caja negra, subproceso), la única aserción afectada era correcta y la corrección quedó acotada al fixture. No fue necesario leer la implementación ni detenerse por contradicción de contrato.

**Nota de alcance (honestidad PD-15):** no leí código de implementación (`skills/**`); trabajé solo desde la spec, el plan, el informe RED y los tests dentro del alcance de lectura. La suite completa **no** se corrió (política del paquete: la corre una vez quien cierra); solo el focal declarado, que es el nivel de validación de una corrección local.
