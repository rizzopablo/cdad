# RED de review-fix (etapa 4) — 005-007-progressive-planning · test-writer

**Packet:** `005-007-progressive-planning-test-writer-red-011` · **Ejecución:** `exec-005-007-progressive-planning-001` · **Rol:** test-writer · **Substage:** `red` (review-fix).
**Contrato:** `docs/specs/005-007-progressive-planning/spec.md` — sha256 `54877103d622ca75994b503ee4be016bf39682c2c6a6f89962a8436d8d309a4a` ✅ (medido antes de leer; coincide con el packet). **Review:** `review.md` sha `44e29413…` (2 blocking). **Plan:** sha `1f636260…` ✅. **Base de esta unidad:** `98b3b6a` (review registrada) — nota: existía un incidente previo declarado (`2e3d33e`, timeout de la cota, sin entrega); esta corrida es la reentrada, sin efectos en el árbol.

## Aislamiento de fase (INV: el test-writer nunca ve la implementación)

Reads: solo `spec.md`, `review.md` y los dos oráculos en scope (`tests/test_005_007_t2_progressive_plan_validator.py`, `tests/test_005_007_t5_delegation_dispatch.py` — patrones declarados por el packet). **Ninguna lectura de `skills/`, `scripts/`, `agents/`, `sources/`, `build/` ni `install.sh`.** Dos observaciones black-box (solo CLI/subproceso, sin leer código) se usaron para calibrar fixtures y están declaradas abajo. Write: solo `tests/test_005_007_reviewfix_blockings.py`. Suite completa NO corrida (política: la corre quien cierra).

## Archivo entregado

`tests/test_005_007_reviewfix_blockings.py` (467 líneas, nuevo): **UN TEST POR BLOQUEANTE**, cada caso del packet como subTest, mapeado 1:1 al contrato:

| Test | Hallazgo | Postcondición | Casos |
|---|---|---|---|
| `TestB1TaskAlwaysDeclaresObjectiveAndDependsOn::test_b1_pd1_task_always_declares_objective_and_depends_on` | B1 (review.md:23-35) | PD-1 (spec.md:42), AC-1 (spec.md:96) | (a) `planned` sin clave `depends_on`; (b) `next` explícita y sin marcador sin `objective`; (c) sin clave `depends_on` sin marcador (con objective, único defecto = clave ausente); (d) CONTROL: `depends_on: []` + objective no vacío sigue ACEPTADA |
| `TestB2WrappedInvocationIsObservedDispatch::test_b2_pd9_wrapped_invocation_reports_observed_dispatch` | B2 (review.md:37-44) | PD-9 (spec.md:66), AC-4 (spec.md:99) | (a) 5 envolturas (`time`, `env`, `nohup bash -c`, `nice -n 5`, `timeout 60`) → despacho observado con método declarado; (b) CONTROL negativo: mención (write/grep) y `--help`/`-h` siguen `absent` con causa; (c) CONTROL: registro neutral sin bandera byte-idéntico |

Reuso declarado: fixtures/helpers de T2 (`plan_bytes`, `planned_task`, `next_task`, harness `prepare`) y de T5 (`_build_trace_store`, `_canonical_record`, bandera `--delegation-dispatch` ya implementada, golden sha neutral, trazas mención/ayuda/neutral con **sids y llamadas idénticos**). Superficie: solo CLI del producto por subproceso (`prepare`; `scripts/cdad_context_meter.py`), nunca import de módulos de producto.

## Evidencia RED — comandos y salidas exactas

**1) Línea base (oráculos focales, verdes antes del RED):**
```
$ timeout 120 python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py -q
6 passed in 4.95s
```

**2) Corrida del RED (la evidencia central):**
```
$ timeout 300 python3 -m pytest tests/test_005_007_reviewfix_blockings.py -q
FF                                                                      [100%]
2 failed in 1.14s

$ timeout 300 python3 -m unittest tests.test_005_007_reviewfix_blockings -v
FAIL: ...TestB1... (caso='a-planned-sin-clave-depends_on')
FAIL: ...TestB1... (variante='detail-next', caso='b-sin-objective')
FAIL: ...TestB1... (variante='sin-marcador', caso='b-sin-objective')
FAIL: ...TestB1... (caso='c-sin-clave-depends_on')
FAIL: ...TestB2... (envoltura='time',    caso='a-envolturas-despacho-observado')
FAIL: ...TestB2... (envoltura='env',     caso='a-envolturas-despacho-observado')
FAIL: ...TestB2... (envoltura='nohup',   caso='a-envolturas-despacho-observado')
FAIL: ...TestB2... (envoltura='nice',    caso='a-envolturas-despacho-observado')
FAIL: ...TestB2... (envoltura='timeout', caso='a-envolturas-despacho-observado')
FAILED (failures=9)
```

**3) Falla HOY, caso por caso (9 fallos, TODOS `AssertionError`, ninguno ImportError/sintaxis/fixture):**

- **B1 (a)** `planned` sin clave `depends_on` → hoy **rc=0** (el probe de la review `planned-absent-depends_on -> PASSED` se reproduce por el oráculo): `AssertionError: 0 == 0 : plan aceptado pese a la postcondición PD-1 exigida (hallazgo B1): ''` — falla en `assertNotEqual(returncode, 0)`.
- **B1 (b)** `next` explícita y sin marcador sin `objective` → hoy **rc=0** (el oráculo T2 ya acepta `next_task("t1")` sin objective): mismo AssertionError (2 subtests).
- **B1 (c)** sin marcador, sin clave `depends_on` (con objective) → hoy **rc=0**: mismo AssertionError.
- **B2 (a)** cada envoltura → hoy **`first_dispatch: absent` con causa** (falso negativo): `AssertionError: 'absent' != 'observed' : B2 (a) [time]: la shell que invoca REALMENTE cdad_delegate.py bajo el prefijo time es un despacho OBSERVADO (PD-9); hoy el medidor resuelve el programa del segmento y reporta absent con causa — falso negativo (fue 'absent'; causa="no role work dispatch in the first stretch: a call whose content or arguments only MENTION the delegation program 'cdad_delegate.py' ... only a shell call that really invokes the program counts ... a dispatch is an event, never proof of utility nor of an accepted result")` — idéntico para las 5 envolturas (la causa hoy hasta clasifica la invocación envuelta como mención, lo que agrava el falso negativo).

**4) Controles (verdes hoy, declara el comportamiento que la corrección no puede romper):** B1 (d) `depends_on: []` + objective no vacío con plan de validación completo → aceptada y publicada; B2 (b) mención y ayuda con bandera → `absent` con causa que nombra `mention`/`help` (T5 casos 2/3); B2 (c) registro neutral sin bandera → sha256 `b43107db…2bcf` (golden de T5) idéntico. Ninguno aparece en la lista de fallos.

**5) Sin regresión en los oráculos focales tras escribir el test:**
```
$ timeout 300 python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py tests/test_005_007_t5_delegation_dispatch.py -q
11 passed in 7.65s
```

## Observaciones black-box declaradas (sin leer implementación)

1. El primer parse de la corrida B2 falló por `NameError: json` — defecto del PROPIO fixture del test; corregido (`import json`) antes de que la corrida cuente como RED. La primera versión de la corrida (2 fallos) se descarta; la válida es la de arriba.
2. El control (c) falló en un borrador porque el registro canónico del medidor porta el **sid** de la sesión (verificado black-box: mismo fixture con sid de T5 → `b43107db…` = golden; sid propio → `9a0f1dc4…`). Los tres fixtures de control ahora replican sids y llamadas de T5 exactos. Sin lectura de código; la normalización de `run.store_ref` ya declarada por T5 no cubre el sid.

## Commit

```
$ git add tests/test_005_007_reviewfix_blockings.py && git commit -m "test: 005-007 RED de review-fix — ..."
[codex/epic-005-real-operation 2cd13a6] ... 1 file changed, 467 insertions(+)
```
`2cd13a6` — solo `tests/test_005_007_reviewfix_blockings.py`; el diff del working tree restante (` M docs/.cdad-state.json`) es preexistente y NO fue commiteado por este rol.

## Próximo paso (para el orquestador)

GREEN de review-fix por el implementer: (1) validador — rechazar tarea sin `objective` no vacío o sin la clave `depends_on` (lista; `[]` válido), diagnóstico que nombre tarea y campo, sin tocar el camino sin marcador más allá de PD-1 (controles B1 (d) y T2 en verde); (2) medidor — resolver el programa dentro de los prefijos declarados (`time`, `env`, `nohup`, `nice`, `timeout`, y la clase `bash -c` de `nohup bash -c`), manteniendo la exclusión de mención/ayuda y la byte-identidad neutral (controles B2 (b)/(c) en verde). Suite completa: la corre una vez quien cierra (política declarada).
