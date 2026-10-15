# GREEN 005-007 T5 — BLOQUEADO por defecto en el oráculo congelado (no es un GREEN verde)

**Packet:** `005-007-progressive-planning-implementer-green-006` · rol: implementer · substage: `green`
**Contrato:** `docs/specs/005-007-progressive-planning/spec.md` (PD-9 / AC-4 / INV-5; sha256 `54877103…09a4a`)
**Plan:** ficha T5 (`docs/specs/005-007-progressive-planning/plan.md:99-108`; sha256 `1f636260…3430`)
**Rama:** `codex/epic-005-real-operation` · **HEAD antes y después:** `673c0bc` (no commiteé: ver §7)
**Write scope:** `{"class":"implementation","root":"skills"}`

## 0. Resultado en una línea

Implementé la detección **por hechos materiales** de la interfaz común de delegación (PD-9) en
`skills/cdad-cycle/scripts/cdad_context_meter.py`, **flag-gated** bajo `--delegation-dispatch` (nombre
fijado por el oráculo), y actualicé su reference `skills/cdad-cycle/references/context-meter.md`.

Del oráculo congelado: **2 passed / 3 failed**. Pasan el **CONTROL** de byte-identidad del registro
neutral (INV-5; `subagent`/`task` siguen detectándose igual) y el **caso 5** (declaración del conjunto
cerrado + método + procedencia). Los **3 restantes (casos 1/2/3) NO son satisfacibles con el oráculo
congelado tal como está**: `run_with_flag()` devuelve el **DOCUMENTO**, y los casos 1/2/3 lo leen como
si fuera una **SESIÓN** (`self.milestone(session, …)` / `measure_leaf(session, …)`). El documento no
tiene `milestones`/`measures` de nivel superior — viven en `sessions[]`, y el **propio caso 5 del mismo
archivo** los lee así (`doc["sessions"][0]`). Me detengo y reporto; no edito `tests/` (AP-4 / invariante
del rol) y **no commiteo** un GREEN no validado (precedente idéntico en T2: `docs/specs/005-007-progressive-planning/t2-green.md`).

## 1. Qué cambié y dónde (write scope `skills`)

Sólo dos archivos, ambos dentro del write scope declarado:

### 1.1 `skills/cdad-cycle/scripts/cdad_context_meter.py` (implementación)

1. **Bandera nueva** `--delegation-dispatch` (booleana, `action="store_true"`), con su ayuda; aparece en
   el usage y en el docstring de superficie de invocación. **Nombre fijado por el oráculo**
   (`DELEGATION_FLAG = "--delegation-dispatch"`).
2. **Detección por invocación real** (misma clase de evidencia que la regla de `resume`):
   - `_shell_segments()` / `_segment_program()` / `_program_basename()` → parto el comando por los
     operadores que arrancan un comando (`&&`, `||`, `;`, `|`, `&`, `\n`), salteo asignaciones
     `NAME=value` y el prefijo del intérprete (`python3 prog.py`), y obtengo **el programa que INVOCA
     cada segmento**.
   - `_delegation_call_kind(command)` → `"dispatch"` si el programa invocado (por basename, path
     canónico o wrapper del repo: el hecho material es el PROGRAMA, no la ruta) es `cdad_delegate.py`;
     `"help"` si esa invocación trae `--help`/`-h`; `None` si el programa **no** se invoca (p. ej. el
     token es un ARGUMENTO de otro programa, como el patrón de un `grep`).
   - `_mentions_delegation(calls)` → hay una **mención** cuando el nombre del programa aparece en los
     argumentos/contenido de alguna llamada sin ser una invocación (contenido de un `write`, argumento
     de un `grep`).
   - `_find_dispatch_delegation(calls)` → **primer despacho** de la traza (por NOMBRE de herramienta o
     por invocación real), con el `method` de su entrada; si no hay, devuelve la **razón honesta**
     (`"help"` | `"mention"` | `None`) en vez de inventar un despacho.
3. **Causas de ausencia honestas** (sólo con la bandera): tres textos nuevos —
   `_ABSENT_DISPATCH_CAUSE_DELEGATION` (nombra el conjunto reconocido), `…_MENTION` (contiene
   `mention`), `…_HELP` (contiene `help`). Los tres conservan el límite honesto de PD-6 de 005-002:
   un despacho es un **`event`**, nunca prueba de `utility` ni de un resultado `accepted`.
4. **Declaración del conjunto + método + procedencia** (sólo con la bandera):
   `reader.dispatch_recognition` con **exactamente 3** entradas — `subagent`, `task` y `cdad_delegate.py`
   — cada una con `method` y `provenance` no vacíos; el método de la interfaz de delegación
   (`material fact: the shell call invokes the program`) **difiere** del método por nombre de
   herramienta (`recognized dispatch tool name`) — las dos clases de evidencia de PD-9.
5. **Método en el hito**: con la bandera, el hito `first_dispatch` `observed` porta `method` (el de su
   entrada declarada). Sin la bandera **no** se agrega ninguna clave.
6. **Byte-identidad por defecto (INV-5)**: toda la funcionalidad nueva está **condicionada a la
   bandera**; sin ella corren las ramas de hoy (`_find_dispatch`, `_ABSENT_DISPATCH_CAUSE`,
   `reader.dispatch_tools`) y el documento sale byte-idéntico.
7. El medidor sigue siendo **lector de sesiones**: sin ledger, sin root del proyecto, sin escrituras;
   sólo stdlib (`os.path`, `shlex`, `json` ya importados).

### 1.2 `skills/cdad-cycle/references/context-meter.md` (reference)

- `--delegation-dispatch` agregada a la superficie de invocación, con su viñeta.
- Nueva subsección **«Delegation interface as a dispatch: the real invocation (005-007 PD-9)»** dentro
  de *Dispatch recognition*: declara el **conjunto reconocido cerrado** con una tabla `entrada → method →
  clase de evidencia`, las dos clases (nombre de herramienta vs hecho material), la **exclusión de la
  mención y de la ayuda**, la honestidad de la ausencia (el límite «un despacho es un `event`»),
  el `method` en el hito observado, y que sin la bandera el registro neutral es byte-idéntico (INV-5) y
  el medidor sigue siendo lector de sesiones (D8).

## 2. Oráculo congelado: comando y salida

```
$ python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -q
FAILED tests/test_005_007_t5_delegation_dispatch.py::TestRealInvocationObserved::test_pd9_real_delegation_invocation_reports_observed_dispatch
FAILED tests/test_005_007_t5_delegation_dispatch.py::TestMentionIsNotDispatch::test_pd9_mention_only_reports_absent_with_honest_cause
FAILED tests/test_005_007_t5_delegation_dispatch.py::TestHelpCallIsNotDispatch::test_pd9_help_calls_report_absent_with_honest_cause
3 failed, 2 passed in 2.43s
```

```
$ python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -v   (extracto)
TestRealInvocationObserved::test_pd9_real_delegation_invocation_reports_observed_dispatch  FAILED  [ 20%]
TestMentionIsNotDispatch::test_pd9_mention_only_reports_absent_with_honest_cause           FAILED  [ 40%]
TestHelpCallIsNotDispatch::test_pd9_help_calls_report_absent_with_honest_cause            FAILED  [ 60%]
TestNeutralRecordByteIdentity::test_pd9_inv5_neutral_record_identical_and_subagent_task_unchanged  PASSED [ 80%]
TestRecordDeclaresSetAndMethod::test_pd9_record_declares_recognized_set_method_and_provenance      PASSED [100%]
```

Los tres rojos fallan en la **misma** aserción, y no es una postcondición de contrato sino el camino de
acceso del propio oráculo (`--tb=line`):

```
/usr/lib/python3.13/unittest/case.py:732: AssertionError: None is not an instance of <class 'dict'> : PD-9 caso 1 (a): milestones es objeto
/usr/lib/python3.13/unittest/case.py:732: AssertionError: None is not an instance of <class 'dict'> : PD-9 caso 2: milestones es objeto
/usr/lib/python3.13/unittest/case.py:732: AssertionError: None is not an instance of <class 'dict'> : PD-9 caso 3: milestones es objeto
```

### 2.1 Por qué **no** es un defecto de la implementación

(No hay evidencia pedida «5 passed»: está bloqueada por el defecto del oráculo y **no la fabrico**.)

El oráculo congela dos convenciones **incompatibles entre sí** en el mismo archivo:

- `run_with_flag()` (línea 455-480) → `return self.parse_session(proc, label)`, y `parse_session()`
  (482-502) → `return doc`. **Devuelve el DOCUMENTO** (verificado: lo usa el caso 5).
- `milestone(session, key, ctx)` (504-511) hace `session.get("milestones")` y `measure_leaf(session… )`
  (513-519) hace `session["measures"]`. **Esperan una SESIÓN**.
- Casos 1/2/3: `session = self.run_with_flag(...)` y después `self.milestone(session, …)`
  (líneas **547-549**, **617-619**, **646-648**, **693-694**) → reciben el documento.
- Caso 5 (y el control 4): `doc = self.run_with_flag(...)` y después
  `self.milestone(doc["sessions"][0], …)` (líneas 901, 915, 943) → camino correcto.

El documento **no** porta `milestones`/`measures` de nivel superior: es el dict declarado
`{schema_version, meter, run, window, reader, sessions, roles, unknowns[, application]}` y el
`context-meter.schema.json` los declara **dentro de `session`** (`$defs/session.required` incluye
`milestones`/`measures`); las focas de 005-002 los leen así (`test_005_002_t1`: `session["milestones"]`,
`doc["sessions"][0]["measures"]`). Es una **contradicción interna del oráculo congelado**, no del
contrato PD-9.

Verificación medida (harness de evidencia, `tests/` intacto: importa sólo el constructor de fixtures del
oráculo y mide por subproceso el wrapper):

```
$ python3 /tmp/opencode/t5_proof.py     (extracto; salida completa en /tmp/opencode/t5_proof.out)
=== contract assertions of cases 1/2/3 applied to sessions[0] ===
  [PASS] 1(a) status observed
  [PASS] 1(a) position 3/seq 4
  [PASS] 1(a) time_relative 1.5
  [PASS] 1(a) method non empty
  [PASS] 1(a) time_to_first_dispatch observed
  [PASS] 1(a) first_resume absent
  [PASS] 1(b) wrapper observed at call 2
  [PASS] 2 mention absent
  [PASS] 2 cause names mention
  [PASS] 2 time null+unknown
  [PASS] 3 help absent
  [PASS] 3 cause names help
  [PASS] 5(c) neutral absent
  [PASS] 5(c) cause event
  [PASS] 5(c) cause utility|accepted
SESSION-LEVEL contract assertions: ALL PASS
Root cause of the frozen failures: … the document carries no top-level 'milestones'/'measures'
(doc_top_level_has_milestones=False)
```

Es decir: **todas** las postcondiciones que los casos 1/2/3 exigen (posición, tiempo, método, causa
`mention`, causa `help`, límite honesto) **se cumplen** en `sessions[]` — el nivel que el contrato
declara. El único motivo del rojo es que el oráculo lee el nivel equivocado.

## 3. Comportamiento medido por fixture (con la bandera)

`reader.dispatch_recognition` (idéntica en las 7 corridas, extracto):

```
{
  "cdad_delegate.py": {"method": "material fact: the shell call invokes the program",
                       "provenance": "005-007 PD-9: … same class of evidence as the resume rule (005-002 PD-6, cdad_context_meter.py); a mere mention of the program and a help call (--help/-h) are excluded"},
  "subagent": {"method": "recognized dispatch tool name", "provenance": "declared recognized dispatch tool names (005-002 PD-6/D5 …)"},
  "task":     {"method": "recognized dispatch tool name", "provenance": "declared recognized dispatch tool names (005-002 PD-6/D5 …)"}
}
```

`first_dispatch` de `sessions[0]` y `time_to_first_dispatch`:

| fixture | first_dispatch | time_to_first_dispatch |
| --- | --- | --- |
| `delegate-skills` (`cdad_delegate.py` ruta canónica) | `observed` position `{call_index:3, seq:4}`, `time_relative 1.5`, `method` = hecho material | `observed`, `1.5` min |
| `delegate-wrapper` (`scripts/cdad_delegate.py`) | `observed` position `{call_index:2, seq:3}`, `1.0` | (no exigido) |
| `mention` (`write` + `grep`) | `absent`, causa con `MENTION` + límite honesto | `unknown`, `value null` |
| `help` (`--help` y `-h`) | `absent`, causa con `HELP` + límite honesto | `unknown`, `value null` |
| `neutral` | `absent`, causa que nombra el conjunto (con la bandera) + `event`/`utility` | `unknown`, `value null` |
| `subagent` | `observed` position `{call_index:2, seq:3}`, `1.0`, `method` = nombre de herramienta | `observed`, `1.0` |
| `task` | `observed` position `{call_index:2, seq:3}`, `1.0`, `method` = nombre de herramienta | `observed`, `1.0` |

Y el `first_resume` queda **independiente** (`absent` con su causa de hoy) en todas las trazas.

## 4. Control de INV-5 (registro neutral byte-idéntico, sin la bandera)

- **Caso 4 del oráculo (CONTROL): PASSED** — sha256 del registro canónico neutral
  (`run.store_ref` normalizado) = `b43107dba90bbd7e2db1bfa5fd283c1f79b04d8192c7e9b5aecdf50ff3da2bcf`
  (golden de hoy) y `subagent`/`task` con el dict exacto de hoy; además, la bandera no aceptada-antes ya
  es aceptada y el modo default sigue igual (`reader.dispatch_tools` = `["subagent","task"]`).
- Comprobación directa de que la detección está **flag-gated**:

```
$ python3 scripts/cdad_context_meter.py --store <fixture delegate-skills>      # SIN bandera
{"cause": "no role work dispatch tool call in the first stretch: this reader recognizes only the dispatch tools 'subagent' and 'task'; …", "status": "absent"}
rc: 0 | reader: {'dispatch_tools': ['subagent', 'task']}
```

```
$ python3 scripts/cdad_context_meter.py --store <fixture neutral> --delegation-dispatch   # CON bandera
rc: 0        # y el registro declara reader.dispatch_recognition
```

```
$ python3 scripts/cdad_context_meter.py --help        (extracto: la superficie declara la bandera)
                          [--delegation-dispatch]
  --delegation-dispatch
                        also recognize as a role work dispatch a shell call
                        that REALLY invokes the common delegation interface
```

## 5. Regresión proporcional

**Declaradas por la ficha T5 (corridas una por una):**

```
$ python3 -m pytest tests/test_005_002_t2_milestones.py -q
5 passed in 1.98s
$ python3 -m pytest tests/test_005_002_t4_acceptance.py -q
3 passed, 2 skipped in 1.78s
$ python3 -m pytest tests/test_005_002_t1_neutral_record.py -q
7 passed in 4.60s
```

(los 2 skips son las corridas de integración real de T4 omitidas sin variables de entorno — no verdes
fabricados; coinciden con la línea base del RED: 15 passed, 2 skipped.)

**Ampliada, mismo módulo tocado (`cdad_context_meter.py`) — toda la suite de 005-002 + set-summary de
005-003 T3:**

```
$ python3 -m pytest tests/test_005_002_t1_neutral_record.py tests/test_005_002_t2_milestones.py \
    tests/test_005_002_t3_application_privacy.py tests/test_005_002_t4_acceptance.py \
    tests/test_005_002_t5_bounded_output.py tests/test_005_002_t5_role_aggregate.py \
    tests/test_005_002_t5_unknown_declared.py tests/test_005_003_t3_set_summary.py -q
47 passed, 2 skipped in 15.43s
```

**Lint:**

```
$ python3 -m ruff check skills/cdad-cycle/scripts/cdad_context_meter.py
All checks passed!
```

## 6. `git diff --stat`

```
$ git diff --stat
 docs/.cdad-state.json                           |   8 +-
 skills/cdad-cycle/references/context-meter.md   |  57 +++++-
 skills/cdad-cycle/scripts/cdad_context_meter.py | 262 ++++++++++++++++++++++--
 3 files changed, 310 insertions(+), 17 deletions(-)
```

(`docs/.cdad-state.json` es escritura del orquestador — **ya estaba modificado antes de empezar** y no lo
toqué; fuera de mi write scope. El alcance de mi cambio son los dos archivos de `skills/`.)

## 7. Commit

**NO commiteé.** El gate GREEN no está satisfecho (el oráculo no está verde) y el defecto es del
**oráculo**, no de la implementación; commitear presentaría un GREEN no validado. Mismo criterio y mismo
precedente que T2 (`t2-green.md`: «NO commiteé… la implementación queda lista y sin commitear en el
worktree para revisión del orquestador»).

- **HEAD:** `673c0bc76dac1f2e1d5b61b992b0e94d1a209116` (sin cambios; no hay hash de commit de este rol).
- La implementación queda **lista y sin commitear** en el worktree. **No necesita más cambios**:
  corregido el oráculo (lado `tests/`), la corrida dará 5/5 sin tocar producto.
- Si el orquestador prefiere que commitee igual (provenance) antes de re-despachar al test-writer, lo hago
  **sin cambios de código**; queda a su decisión.

## 8. Fix mínimo propuesto (test-writer; yo no puedo tocar `tests/`)

En los **4 puntos de llamada** de los casos 1/2/3, leer la sesión desde el documento (como ya hace el
caso 5 del propio archivo):

```python
# en test_pd9_real_delegation_invocation_reports_observed_dispatch (x2: punto a y b),
# test_pd9_mention_only_reports_absent_with_honest_cause y
# test_pd9_help_calls_report_absent_with_honest_cause:
            doc = self.run_with_flag(<store>, <label>)
            session = doc["sessions"][0]
```

(líneas actuales **547-548**, **617-618**, **646-647**, **693**: hoy `session = self.run_with_flag(...)`;
el resto del cuerpo de esos casos ya usa `session` como sesión.) Alternativa equivalente: un helper
`session_with_flag(store, label)` en el propio test que devuelva `self.run_with_flag(...)["sessions"][0]`.
Ninguna de las dos requiere cambiar la implementación ni el caso 4/5.

## 9. Consideración del «límite honesto» del encargo (obediencia al oráculo vs. contrato)

El encargo autoriza: «si algun caso del oráculo exige una forma de declaración no prevista por el
contrato, cumplilo y declara la elección y su motivo (el nombre de la bandera lo fijó el oráculo)».

- **Cumplí** todo lo que el oráculo fija y el contrato no nombraba: el nombre de la bandera
  (`--delegation-dispatch`), la clave `reader.dispatch_recognition` con **3** entradas, el nombre de la
  entrada de la interfaz (`cdad_delegate.py`), los campos `method`/`provenance`, el `method` en el hito
  observado, y las causas con `mention`/`help` + el límite `event`/`utility`/`accepted`.
- **No** interpreté como «forma de declaración» el que los casos 1/2/3 lean el documento **como si fuera
  la sesión**: exigiría agregar `milestones`/`measures` de nivel superior al documento, lo que
  (a) contradice el contrato de 005-002 (los hitos/medidas viven en `sessions[]`) y su
  `context-meter.schema.json` (`additionalProperties: false` en la raíz),
  (b) crearía una **segunda forma de documento** no declarada por ninguna fuente,
  (c) se contradice con el **propio caso 5 y el control 4 del mismo oráculo**, que leen `sessions[0]`.
  Cumplirlo sería *gaming* del oráculo (el test pasaría por el camino equivocado) y un artefacto falso en
  el contrato. Prefiero el reporte honesto y la corrección del oráculo por quien lo posee.

**Item abierto declarado (no lo hice, fuera de la lista de archivos del encargo):**
`reader.dispatch_recognition` **no** está declarada en `skills/cdad-cycle/assets/context-meter.schema.json`,
cuyo `$defs/reader` tiene `additionalProperties: false` y `required: ["dispatch_tools"]`. No toqué el
asset (el encargo y la ficha T5 nombran sólo el `script` + el `reference`), con el precedente de
`set-summary-v1` (005-003 T3), que tampoco se retro-declaró en ese schema. **Decisión del orquestador:**
si el registro debe seguir validando contra el asset, hace falta extender `$defs/reader` con
`dispatch_recognition` (cambio de una sola entrada; lo hago si lo indicás).

## 10. Declaración AP-4 e integridad

- **No toqué `tests/`:** `git status --porcelain -- tests/` → **0 líneas**. El oráculo permanece intacto
  y congelado en `b3044b1`.
- Sólo edité `skills/cdad-cycle/scripts/cdad_context_meter.py` y
  `skills/cdad-cycle/references/context-meter.md` (write scope `skills`).
- **No** escribí ni leí la base real de sesiones; **no** desplegué; **no** hice push; **no** usé
  `--no-verify`; **no** leí `tests/.sensitive-patterns.local`.

## 11. Límites honestos (PD-15)

- **No puedo entregar la evidencia «5 passed»**: está bloqueada por el defecto del oráculo descrito en
  §2; **no la fabrico** y **no** altero el test para conseguirla.
- **No corrí la suite completa**: política de suite (la corre una vez quien cierra). Corrí el focal, las
  3 regresiones declaradas y la regresión ampliada del módulo tocado (47 passed, 2 skipped).
- **No commiteé** (§7): el gate no está verde.
- No re-hasheé el sha256 del contrato ni del plan en esta sesión (declarados como leídos del packet).
- La detección cubre el token del programa en el comando; una invocación oculta tras un wrapper que no
  expone el token sigue siendo el **falso negativo declarado como deuda D-4** (no acoplé el medidor a
  ningún ledger para evitarlo — exclusión explícita de la ficha T5).
