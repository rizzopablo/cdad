# RED T5 — 005-007-progressive-planning · test-writer · subetapa red

**Packet:** `005-007-progressive-planning-test-writer-red-006` (contract sha `54877103…`, policy sha `f508ab1e…`) · **Rol:** test-writer · **Focal:** `tests/test_005_007_t5_delegation_dispatch.py` · **Postcondición:** PD-9 · **AC:** AC-4 · **Trazabilidad:** ficha T5 del plan (`docs/specs/005-007-progressive-planning/plan.md:99-108`) + PD-9 (`spec.md:66`) + INV-5 (`spec.md:84`).

## Resultado del RED (fait accompli medido)

`python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -q` → **4 failed, 1 passed** (1,83 s).

Los 4 fallos son **AssertionError** sobre comportamiento ausente (nunca ImportError ni sintaxis): los casos 1, 2, 3 y 5 fallan hoy en la **guardia de la bandera nueva declarada `--delegation-dispatch`** (el medidor vigente la rechaza: `rc=2`, `unrecognized arguments`), que es el RED de toda la detección/declaración de la interfaz de delegación. El caso 4 es **control declarado** y **pasa hoy**.

## Mapa de casos → postcondición (trazado 1:1 en los docstrings del test)

| # | Caso (ficha T5/PD-9) | Test | Estado hoy |
|---|---|---|---|
| 1 | POSITIVO: traza cuyo primer despacho es una `shell` que invoca REALMENTE `cdad_delegate.py` (con `--project-root`/`--packet`/`--destination`) → `first_dispatch` **observed** en esa posición (call_index 3, seq 4, 1,5 min; variante wrapper: #2/seq 3/1,0 min), `time_to_first_dispatch` observed, **método declarado**; `first_resume` independiente | `TestRealInvocationObserved.test_pd9_real_delegation_invocation_reports_observed_dispatch` (2 subTests) | **RED** (AssertionError) |
| 2 | NEGATIVO (mención): `write` cuyo contenido menciona el programa + `grep` cuyo argumento lo menciona sin invocarlo → `absent` (nunca despacho) con la **causa que nombra el límite** (la mención no cuenta); tiempo null + cubo `unknown` | `TestMentionIsNotDispatch.test_pd9_mention_only_reports_absent_with_honest_cause` | **RED** (AssertionError) |
| 3 | NEGATIVO (ayuda): `cdad_delegate.py --help` y `-h` NO cuentan → `absent` con la **causa que nombra la exclusión de ayuda** | `TestHelpCallIsNotDispatch.test_pd9_help_calls_report_absent_with_honest_cause` | **RED** (AssertionError) |
| 4 | REGRESIÓN (INV-5/AC-4), **controles**: (a) registro neutral sin la bandera **byte-idéntico al de hoy** (sha256 del registro canónico con `run.store_ref` normalizado, capturado del medidor vigente); (b) declaración y causas de HOY pinneadas verbatim (`reader.dispatch_tools` = `subagent`+`task`; hitos neutral con el dict exacto de hoy); (c) `subagent`/`task` siguen detectándose **igual** (dicts exactos de hoy); (d) mención/ayuda sin bandera siguen `absent` | `TestNeutralRecordByteIdentity.test_pd9_inv5_neutral_record_identical_and_subagent_task_unchanged` (4 subTests) | **control, pasa** |
| 5 | DECLARACIÓN (PD-9): CON la bandera, el registro declara el **conjunto reconocido cerrado** (`reader.dispatch_recognition`, exactamente 3 entradas: `subagent`, `task` y una que nombra `cdad_delegate.py`) con **`method`+`provenance`** por entrada; el método de la interfaz de delegación difiere del método por nombre de herramienta (dos clases de evidencia); los hitos observados portan el método de su entrada (subagent igual CON la bandera); la causa de ausencia conserva el límite honesto (**evento**, no prueba de utilidad/resultado aceptado — PD-6 de 005-002 por referencia) | `TestRecordDeclaresSetAndMethod.test_pd9_record_declares_recognized_set_method_and_provenance` (3 subTests) | **RED** (AssertionError) |

## Decisión de diseño declarada para el GREEN (derivada del contrato; auditable)

La **bandera nueva única `--delegation-dispatch`** (booleana) es la única lectura que hace compatibles **PD-9** y **INV-5**: si la detección fuera default-on, la causa genérica de `absent` («recognizes only the dispatch tools 'subagent' and 'task'») se volvería FALSA como enunciado de capacidad y el registro neutral cambiaría — INV-5 («el registro neutral del medidor sin las banderas nuevas no cambia») lo prohíbe y el caso 4 del packet lo exige como control que pasa hoy. Con la bandera: detección + declaración (`reader.dispatch_recognition` con método/procedencia por entrada) + hito con `method` + causas actualizadas con el límite honesto (mención/`help` nombrados; despacho = **evento**, no utilidad/resultado aceptado). Sin la bandera: byte-idéntico a hoy para CUALQUIER traza (la causa de hoy sigue siendo verdadera del modo default). Por eso los negativos fallan hoy en la guardia de la bandera (comportamiento ausente, precedente T1 de 005-002: «RED por CLI ausente»); tras GREEN, si las causas no distinguieran mención/ayuda, las aserciones de causa toman el relevo.

## Superficie probada (comportamiento, sin plomería)

Wrapper fino `scripts/cdad_context_meter.py`, SIEMPRE por subproceso (`sys.executable`), NUNCA importado; el contrato observable es stdout JSON + rc + stderr. 7 fixtures SQLite 100% sintéticos en tempdir (esquema observado de discovery §1.2–§1.6; una parte `tool` por mensaje; llamada #i en t0+i·30 s → time_relative i·0,5 min derivado del propio fixture): `delegate-skills`, `delegate-wrapper`, `mention`, `help`, `neutral`, `subagent`, `task`. La base real de sesiones NO se abre ni se escribe (INV-6); sin rutas del host (verificado: 0 ocurrencias del tmpdir en el registro; `run.store_ref`/`session_ref` son hashes). Golden de byte-identidad portable: `_canonical_record` normaliza `run.store_ref` (hash de la RUTA del store, varía por tmpdir) y canonicaliza con `sort_keys`; receta de regeneración documentada en el docstring y en el mensaje de fallo.

## Comandos y evidencia (exactos)

```text
python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -q
→ 4 failed, 1 passed in 1.83s  (casos 1/2/3/5 RED; caso 4 control)

python3 -m pytest tests/test_005_002_t2_milestones.py \
    tests/test_005_002_t4_acceptance.py tests/test_005_002_t1_neutral_record.py -q
→ 15 passed, 2 skipped in 7.04s  (regresiones declaradas por la ficha T5:
  intactas; los 2 skips son las corridas de integración real de T4 que se
  omiten por defecto sin variables de entorno — no verdes fabricados)

python3 -m ruff check tests/test_005_007_t5_delegation_dispatch.py
→ All checks passed!
```

Mensaje del RED (ejemplo, caso 1 — idéntico en forma para 2/3/5):

```
AssertionError: RED PD-9 caso 1 (a): la bandera nueva declarada
`--delegation-dispatch` no es aceptada aún por el medidor — comportamiento
ausente (PD-9/AC-4): ni la detección de la invocación real de la interfaz de
delegación, ni la declaración del conjunto+método, ni las causas de ausencia
actualizadas existen; AssertionError de RED, nunca ImportError. stderr=
'usage: cdad_context_meter [-h] …'
```

Contexto medido que motiva el RED (observación black-box sobre los fixtures sintéticos del propio test, NO lectura de código): hoy el medidor reporta `first_dispatch` **absent** para la traza con invocación real de `cdad_delegate.py`, con la causa que declara reconocer sólo los NOMBRES `subagent`/`task`; `subagent`/`task` se detectan por nombre (hito observed con posición).

## Archivo creado y commit

- **Creado (write scope `tests/`):** `tests/test_005_007_t5_delegation_dispatch.py` (nuevo, 967 líneas, 5 tests / 9 subTests).
- **Commit del rol:** `b3044b1` — `test: 005-007 T5 RED - despacho por la interfaz de delegacion (PD-9) no detectado: foca del medidor sobre trazas fixture con 1 control de byte-identidad del neutral (INV-5) y subagent/task iguales` en `codex/epic-005-real-operation`; `1 file changed, 967 insertions(+)` (solo el test). Sin `--no-verify`, sin push.
- **Nota:** `docs/.cdad-state.json` tiene el diff del orquestador en el working tree; no lo toqué y no entra en este commit (el state solo lo escribe el orquestador).

## Honestidad de fase (PD-15) — sin lectura de implementación

**Ningún archivo de implementación fue leído** (`skills/`, `scripts/`, `agents/`, `sources/`, `build/`, `install.sh`): ninguna lectura de contenido de `cdad_context_meter.py`, `cdad_delegate.py` ni de otro módulo. Declaro las dos observaciones black-box que hice y su efecto nulo:

1. **Corridas del medidor y del CLI de delegación sobre fixtures sintéticos** (el mismo oráculo que usan los tests): `python3 scripts/cdad_context_meter.py --store <fixture> [--help]` y `python3 scripts/cdad_delegate.py --help` (solo la línea de usage; los nombres de argumentos `--project-root`/`--packet`/`--destination` ya los declaraba el encargo del packet — `--help` solo los confirmó). El comportamiento de HOY que pinnean los controles (causa de `absent`, `reader.dispatch_tools`, dicts de `subagent`/`task`, golden sha) se capturó EXCLUSIVAMENTE por esta vía.
2. `--help` del medidor (superficie de banderas vigente) para confirmar que `--delegation-dispatch` no existe aún.

Los 5 tests derivan sus aserciones del contrato (spec PD-9/AC-4/INV-5, ficha T5, PD-6 de 005-002 por referencia) y del comportamiento observable del CLI sobre fixtures; no fijan nombres internos ni mocks. Si el orquestador considera que alguna observación contamina la fase, la parte afectada (este RED) se rehace en sesión aparte; los insumos (los 5 casos con su estado esperado) quedan registrados arriba.

**Política de suite:** NO corrí la suite completa (packet: la corre una vez quien cierra). Solo focal + las 3 regresiones declaradas.

## Estado para el implementer GREEN (T5)

GREEN debe hacer pasar los casos 1/2/3/5 añadiendo la bandera `--delegation-dispatch` con la semántica declarada (detección de la invocación real por hechos materiales — misma clase que la regla de `resume`; exclusión de ayuda y de menciones; `reader.dispatch_recognition` con método+procedencia por entrada; hito con `method`; causas de ausencia actualizadas con el límite honesto), conservando el control 4 VERDE: **el registro neutral sin la bandera es byte-idéntico al de hoy** (golden sha `b43107dba90bbd7e2db1bfa5fd283c1f79b04d8192c7e9b5aecdf50ff3da2bcf`; `_canonical_record` normaliza solo `run.store_ref`). Excluido por la ficha: acoplar el medidor a un ledger/root; inferir despacho por texto que sólo menciona; tocar el registro neutral sin la bandera. Regresiones de re-verificación: las tres focas de 005-002 (15 passed hoy). El reference `skills/cdad-cycle/references/context-meter.md` debe declarar el conjunto+método (ficha T5, «declararlo en context-meter.md») — su verificación es de la ficha GREEN/review, no de este RED.
