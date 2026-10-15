# Informe RED — 005-012 T6 (`prepare --new-execution` rechaza el contexto abierto y sin uso)

**Rol:** test-writer · **Etapa 3, subetapa `red`** · **Tarea:** T6 · **PD:** PD-16 (con PD-17 de soporte)
**Paquete:** `005-012-transition-registration-test-writer-red-007` · **Ejecución:** `exec-005-012-transition-registration-001`
**Contrato leído (oráculo):** `docs/specs/005-012-transition-registration/spec.md` §2.3 PD-16 / §2.4 INV-7 / PD-17 / §4; `plan.md` §4 ficha T6 + §5 D-9; `discovery.md` §4.2.

## (a) Casos y PD cubiertos por el focal

**Archivo creado (único archivo tocado): `tests/test_005_012_t6_open_context_guard.py`**

| Test | Caso del encargo | PD | Resultado RED hoy |
|---|---|---|---|
| `test_pd16_new_execution_with_open_unused_context_is_rejected_naming_it` | 1 — el rechazo | **PD-16** (+ PD-17/INV-7) | **FAILED por aserción** (rc=0 en vez de rc=2) |
| `test_pd16_new_execution_without_prior_context_still_publishes` | 2 — control positivo | **PD-16** | pasa (control) |
| `test_pd16_reuse_path_without_new_execution_keeps_working` | 3 — camino de reuso | **PD-16** | pasa (control) |
| — (no asertado) | 4 — contexto abierto **con uso** | PD-16 / D-5 | **declarado**, ver abajo |
| transversal en los 3 tests | 5 — aditividad | **PD-17** | `validate-state` rc=0 antes y después; **sin** aserciones de porcentajes ni de conteos del state vivo |

Caja negra estricta: **solo `subprocess` sobre el CLI del repo** (`prepare`, `open-unit`, `validate-state`), proyecto descartable en tempdir, `HOME` del subproceso en un tempdir **vacío**, fixtures sintéticos y anónimos, sin mocks del cableado interno.

**Aislamiento de causas (caso 1, declarado en el docstring y asertado como precondición):** el fixture monta el contexto abierto **sin uso** (`open-unit` no publica paquetes, no deja `active_packet` y no crea `dispatches/`) y ninguna otra causa posible de rc≠0 en `prepare` (política válida, feature activa `in-progress` con contrato pineado, `hitl_delegation` activa con `source` existente, `active_packet` nulo). Sonda previa: la **misma** invocación hoy da rc=0, así que el rc=2 del contrato es atribuible sólo al guard.

**Caso 4 — declarado, no asertado (límite de D-5).** No hay caso observable limpio: con un paquete publicado para el contexto abierto, la misma invocación hoy falla por **otra** causa (precondición de paquete activo `prepared`, PD-4 de 004-002) → `ERROR: active packet '…-test-writer-red-001' is 'prepared'` (sonda), de modo que el no-disparo del guard no es separable sin asertar comportamiento que la spec **no fija**. Además la ficha T6 lo excluye explícitamente («Excluido: … cubrir un contexto con paquetes o creado por otra vía — deuda D-5»). Por eso **no** se escribió test para el caso 4.

**Nota honesta sobre el estado RED:** sólo el caso 1 falla hoy (es el que prueba que el guard **falta**). Los casos 2 y 3 pasan hoy **por construcción**: son los controles que la ficha exige («si el rechazo bloqueara un uso legítimo de `--new-execution` … detener») y su valor está en el GREEN/regresiones (fallarían si el guard disparara de más), no en el RED.

## (b) Comando exacto y salida real del focal

```
$ python3 -m pytest tests/test_005_012_t6_open_context_guard.py -q --tb=line
F..                                                                      [100%]
<repo>/tests/test_005_012_t6_open_context_guard.py:354: AssertionError: PD-16 violada (RECHAZO): con un contexto abierto y sin uso, `prepare --new-execution` debe rechazarse (rc=2) en vez de acuñar un segundo id; rc=0: '---cdad-packet-json\n{"contract":{…},"execution":{…,"id":"exec-005-012-t6-open-context-fixture-002",…},…}\n---end-cdad-packet-json\n…'
FAILED tests/test_005_012_t6_open_context_guard.py::test_pd16_new_execution_with_open_unused_context_is_rejected_naming_it
1 failed, 2 passed in 3.29s
```

Motivo del fallo (aserción concreta, **no** import/sintaxis/JSONDecodeError):

```
E       assert 0 == 2
E        +  where 0 = CompletedProcess(args=['/usr/bin/python3', '…/cdad_packet.py', …]).returncode
<repo>/tests/test_005_012_t6_open_context_guard.py:354: AssertionError
```

La línea `:354` es la aserción `assert proc.returncode == 2` de PD-16. El defecto real de 005-013 queda visible en el propio stdout del CLI (id acuñado **de más**): `id":"exec-005-012-t6-open-context-fixture-002"`.

**Regresiones declaradas por el plan (corridas, verdes):**

```
$ python3 -m pytest tests/test_004_002_t2_bootstrap.py tests/test_packet_prepare.py tests/test_005_007_t3_open_unit.py -q
..........................................                               [100%]
42 passed in 35.48s
```

(No se corrió la suite completa: la corre quien cierra, según la política declarada en el paquete.)

## (c) El archivo NO importa la implementación

```
$ grep -nE "^(import|from)|cdad_packet|cdad_result|skills/" tests/test_005_012_t6_open_context_guard.py
...
import subprocess                      # ← única vía hacia el CLI
...
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"   # path, invocado como subproceso
```

No hay ningún `import` del módulo de implementación ni lectura de su código: el módulo bajo prueba se invoca **solo** como `[sys.executable, str(CLI), *args]`. Los únicos imports externos son stdlib + `pytest` + helpers de **tests** (`test_004_002_t2_bootstrap`). Sin rutas absolutas del dueño hardcodeadas (`REPO_ROOT` se deriva de `__file__`); ids del fixture sintéticos/anónimos.

## (d) Commit

```
$ git commit -m "test: 005-012 T6 RED — prepare --new-execution rechaza el contexto abierto y sin uso (PD-16)" -- tests/test_005_012_t6_open_context_guard.py
[codex/epic-005-real-operation 4b8bf5c] test: 005-012 T6 RED — …
 1 file changed, 483 insertions(+)
 create mode 100644 tests/test_005_012_t6_open_context_guard.py
```

`4b8bf5c` — `test: 005-012 T6 RED — prepare --new-execution rechaza el contexto abierto y sin uso (PD-16)` (1 archivo, el focal). El `docs/.cdad-state.json` que aparece modificado en el working tree **no** es mío y **no** se commiteó.

## Bloqueos / ambigüedades

Ninguno. La única desviación respecto de la lista de casos es la **declaración del caso 4** (excluido por la ficha como deuda D-5 y sin caso observable limpio), reportada arriba en vez de asertada, tal como el propio encargo autoriza.
