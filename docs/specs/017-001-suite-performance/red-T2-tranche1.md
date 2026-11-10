# FINAL TEXT — test-writer RED tranche 1 (017-001-suite-performance): marcas reales + RED verificado

## 1. Route C validation — PASS (antes de trabajar)

- El dispatch trae solo el bloque de identificación (sin cuerpo inline → sin mezcla de rutas): `packet_id` 017-001-suite-performance-test-writer-red-009, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`.
- `validate-request` y `validate-packet` (con `--execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json`) ambos rc 0; el sha256 del contrato coincide con `sha256sum` del spec en disco; contexto de ejecución `schema_version=2` → v2, ruta C admisible; el render canónico `--route C` iguala byte por byte la identificación recibida.
- Trabajé sobre ruta C, substage `red`, solo inputs/scopes del paquete. Skills de ciclo completo no cargados. Sin lecturas de implementación (`scripts/` intacto y no leído; el funcionamiento del observador se cita solo desde `green-T2.md`, input declarado).

## 2. Pre-RED: protección existente y contribución

- Existente: P1 (transporte/identidad/contexto/anidamiento del helper + integración sintética), P2 (cierre por excepción), P3 (neutralidad del helper aislado), P4 (diagnóstico de captura faltante a nivel familia), P5 (diagnóstico por selección de operación). Todo sobre recorridos **sintéticos**; ninguna protección ejercita una frontera **real**.
- Contribución de este tranche: las fronteras reales del mapeo §3 (conftest `isolation.seed` sesión vs por test; `product.lookup/copy/generate` con rama fría/reutilización; constructores `_RecoveryProject`/`_Project` con build + prepare inicial anidados) no emitían ningún intervalo. Sin este trabajo, la calibración entraría a la base sobre captura rota confundiéndola con medición válida (PC-1 parte operaciones, INV-1/INV-2/INV-8).

## 3. Evidencia RED (falla por la razón correcta)

Nuevo oráculo `tests/test_017_001_suite_tranche1.py::test_real_product_lookup_emits_branch_and_stays_neutral` (un test por promesa observable, trazado a PC-1/INV-1/INV-2/INV-8, con consecuencia declarada). Antes de las marcas:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_017_001_suite_tranche1.py -o addopts= -p no:cacheprovider -q
```

→ `1 failed in 0.09s`, `AssertionError: …la frontera real debe emitir sus dos lookups con comienzo y fin…: []` (`assert 0 == 2`). Falla en aserción de promesa ausente, nunca por ImportError/colección.

Sonda no comprometida sobre el recorrido real C-R (plugin efímero en `<tmp>/cdad-probe/`, fuera de `tests/`, eliminado del reporte pero no del repo — no se commiteó nada fuera de `tests/`):

```sh
CDAD_PROBE_OUT=.../pre.json PYTHONPATH=<tmp>/cdad-probe PYTHONDONTWRITEBYTECODE=1 python3 -m pytest "tests/test_007_002_dispatch_recovery.py::test_reconcile_abandoned_dispatch_is_disposed" -o addopts= -p no:cacheprovider -p obs_probe_plugin -q
```

→ `1 passed in 1.52s`, eventos capturados: **0**. El test contractual pasa sin marcas (neutralidad preexistente) pero no hay nada que calibrar: comportamiento pendiente confirmado también en conftest/007_002.

## 4. Marcas agregadas (solo `tests/`, sin cambiar cuerpos ni transiciones)

- `tests/product_staging.py`: `product.lookup` con rama `cached` / `checkout-manifest` / `cold` (reestructuración mínima que conserva asignaciones y retorno); `product.copy` y `product.generate` anidados bajo el lookup frío; la validación de manifiesto queda dentro del lookup frío pero fuera del intervalo del subproceso, como fija el mapeo.
- `tests/conftest.py`: `isolation.seed` en los dos sitios de llamada — fixture de sesión con `owner_scope="shared"`, `nodeid=None`, rama `session`; fixture por test con `owner_scope="test"`, rama `test`. La preparación compartida queda identificada como compartida aunque pytest la ejecute dentro del setup del primer nodeid: no se adjudica al primer test ni se cuenta dos veces.
- `tests/test_007_002_dispatch_recovery.py`: `recovery.construct` (cuerpo del `__init__`), con `recovery.build` (llamada a `_build_project`) y `recovery.initial-prepare` (llamada a `self.prepare(...)` del constructor) anidados. El despacho/disposición/reconciliación posteriores quedan fuera.
- `tests/test_007_003_continuity_at_edges.py`: `continuity.construct`, con `continuity.build` (llamada a `build_project`) y `continuity.initial-prepare` (llamada a `self.prepare()`) anidados. Registros/replays posteriores permanecen acciones reales.
- Todo con `operation` (+ contexto ambiente vía `use_context` del observador en corridas `close`); el cierre por excepción lo garantiza el helper (`finally`, P2). Cuerpos, argumentos, resultados, aserciones y orden intactos: solo envoltorios `with`.

## 5. Verificación post-marcas

- RED ahora verde: el oráculo tranche-1 pasa (`1 passed in 0.06s`).
- Sonda C-R post-marcas (mismo comando, `post.json`): `1 passed in 1.85s`, **10 eventos** (5 begin + 5 end): `isolation.seed` ×2 (`shared/session` + `test/test`), `recovery.construct` con hijos `recovery.build` y `recovery.initial-prepare`, anidamiento padre-hijo verificado por `parent_id` (`nesting-ok: True`). Con observador activo los eventos llegan; sin observador los mismos tests pasan igual y no se escribe evidencia (las corridas de §6 corrieron sin observador).
- Corridas afectadas (secuenciales, sin observador, `-o addopts= -p no:cacheprovider`):
  - `tests/test_017_001_suite_operations.py` + `tests/test_017_001_suite_tranche1.py` → **6 passed en 6.87s** (muro 7s).
  - `tests/test_017_001_suite_profile.py` → **17 passed en 21.25s** (muro 22s).
  - `tests/test_008_002_suite_evidence.py` → **5 passed en 4.21s** (muro 5s).
  - `tests/test_007_002_dispatch_recovery.py` → **18 passed en 67.98s** (muro 68s).
  - `tests/test_007_003_continuity_at_edges.py` → **10 passed en 94.04s** (muro 95s).
  - Total: **56 passed, 0 failed**. **Suite completa no realizada** (ciclo focal + regresión proporcional como rutina; no se reclama autorización de corrida completa).
- Límites honestos: (a) en corridas en proceso sin los hookwrappers de fase del implementer, `nodeid/phase` de las marcas 007 quedan nulos — el contexto completo llega en corridas `close`; (b) la rama fría real con hijos `copy/generate` no se ejercitó en este checkout (manifiesto presente → rama `checkout-manifest`); su calibración dedicada es C-P-cold con fuente descartable real; (c) las tranches restantes del mapeo (U1/U3/U4/documental) no pertenecen a este encargo.

## 6. Commits (solo `tests/`)

- `729495ef` — `test(017-001-T2): tranche-1 RED — product.lookup real emite rama y es neutro` (1 archivo nuevo; sobre su padre el test falla como en §3).
- `3c9c57c5` — `test(017-001-T2): tranche-1 marcas reales en conftest, staging, 007_002 y 007_003` (4 archivos, +93/−71).
- `git status` final: solo persiste el cambio preexistente de `docs/.cdad-state.json` (del orquestador, no tocado por mí). `scripts/`, contrato y derivados intactos (verificado: el diff fuera de `tests/` es únicamente ese estado preexistente).

## 7. Delta de inventario vivo propuesto (texto para que el orquestador lo materialice; `docs/` fuera de mi write-scope)

Agregar a `live-inventory-delta-T2.md`:

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_tranche1.py::test_real_product_lookup_emits_branch_and_stays_neutral` | T2-check-6 | operation-markers-v1 (spec §4.2, PC-1 parte, INV-1/INV-2/INV-8) | RED tranche 1 + marcas verificadas (commits 729495ef, 3c9c57c5) |

Soporte (no verificadores): marcas reales en `tests/conftest.py` (`isolation.seed` sesión/compartida vs por test), `tests/product_staging.py` (`product.lookup` con ramas + `product.copy`/`product.generate` anidados), `tests/test_007_002_dispatch_recovery.py` (`recovery.construct/build/initial-prepare`) y `tests/test_007_003_continuity_at_edges.py` (`continuity.construct/build/initial-prepare`). 1 nodeid nuevo, disposición Añadir. P1–P5 sin cambios.
