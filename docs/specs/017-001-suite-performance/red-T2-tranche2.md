# FINAL TEXT — test-writer RED tranche 2 (017-001-suite-performance): marcas reales + RED verificado + fix de base temporal

## 1. Route C validation — PASS (antes de trabajar)

- El dispatch trae solo el bloque de identificación (sin cuerpo inline → sin mezcla de rutas): `packet_id` 017-001-suite-performance-test-writer-red-010, `execution_id` exec-017-001-suite-performance-001, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`.
- `validate-request` y `validate-packet` (con `--execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json`) ambos rc 0; el sha256 del contrato coincide con `sha256sum` del spec en disco; contexto de ejecución `schema_version=2` → v2, ruta C admisible; el render canónico `--route C` iguala byte por byte la identificación recibida.
- Trabajé sobre ruta C, substage `red`, solo inputs/scopes del paquete. Skills de ciclo completo no cargados. Sin lecturas de implementación (`scripts/`, contrato y derivados intactos; fuera de `tests/` solo persiste el cambio preexistente de `docs/.cdad-state.json`, del orquestador, no tocado por mí).

## 2. Pre-RED: protección existente y contribución

- Existente: P1–P5 (`test_017_001_suite_operations.py`, marcas sintéticas) y oráculo tranche-1 (`test_017_001_suite_tranche1.py`, solo `product.lookup`). Ninguno ejercita las fronteras reales de U1/U3/U4/documental.
- Contribución de este tranche: `u1.lookup/copy/generate`, `u3.lookup/copy/initial-generate` + `u3.contract-staging` (2 llamadas), `u4.lookup/copy/initial-generate` + `u4.contract-regenerate` (2 llamadas), `documentary.contract-regenerate` (2 llamadas) + `documentary.install-lookup/install` no emitían ningún intervalo. Sin este trabajo, la calibración entraría a la base sobre captura rota confundiéndola con medición válida (PC-1 parte operaciones, INV-1/INV-2/INV-8).

## 3. Evidencia RED (falla por la razón correcta)

Nuevo oráculo `tests/test_017_001_suite_tranche2.py::test_real_tranche2_lookups_emit_branch_and_stay_neutral` (un test por promesa observable, trazado a PC-1/INV-1/INV-2/INV-8, con consecuencia declarada). Antes de las marcas:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_017_001_suite_tranche2.py -o addopts= -p no:cacheprovider -q
```

→ `1 failed in 1.22s`, `AssertionError: …las fronteras reales deben emitir sus ocho reutilizaciones…: []` (`assert (0 == 8)`). Falla en aserción de promesa ausente, nunca por ImportError/colección. Tras las marcas: `1 passed` (1.19s; re-verificado post-fix: `1 passed in 1.07s`).

Sonda no comprometida sobre el recorrido real C-U1 (plugin efímero en `~/clawd/tmp/cdad-probe2/`, fuera de `tests/`, no commiteado):

```sh
CDAD_PROBE_OUT=.../cu1.json PYTHONPATH=~/clawd/tmp/cdad-probe2 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest "tests/test_006_002_u1_delegation_section.py::TestPd2aExactlyOneDelegationSection::test_pd2a_opencode_adapter_has_exactly_one_delegation_section" "tests/test_006_002_u1_delegation_section.py::TestPd2aExactlyOneDelegationSection::test_pd2a_claude_code_adapter_has_exactly_one_delegation_section" -o addopts= -p no:cacheprovider -p obs_probe2_plugin -q
```

→ `2 passed in 150.05s`, **14 eventos** (7 begin + 7 end): `u1.lookup` ×2 (`cold` 1 + `cached` 1), `u1.copy` ×1 y `u1.generate` ×1 colgando del lookup frío (`parent-linked-ok: True`), `isolation.seed` ×3 (1 `shared/session` + 2 `test/test`), fases `setup`/`call` correctas, terminaciones `ok` ×7. Exactamente conteos y relaciones del mapeo §3B/C-U1. Con observador activo los eventos llegan; sin observador los mismos tests pasan igual y no se escribe evidencia (las corridas de §5 corrieron sin observador).

## 4. Marcas agregadas (solo `tests/`, sin cambiar cuerpos ni transiciones)

- `tests/test_006_002_u1_delegation_section.py`: `staging_root()` → `u1.lookup` (`cached`/`cold`), con `u1.copy` y `u1.generate` anidados bajo el frío (reestructuración mínima que conserva asignaciones, chequeo de manifiesto y retorno).
- `tests/test_006_004_u3_principle_single_source.py`: `disposable_product()` → `u3.lookup` (`cached`/`cold`), con `u3.copy` e `u3.initial-generate` (acción contractual hija, conserva el resultado que comprueban los consumidores) anidados; cuerpo de `staging_digests()` envuelto como `u3.contract-staging` (las 2 llamadas de `:1123-1124` quedan como hermanas ordenadas reales).
- `tests/test_006_005_u4_single_entry.py`: `_recomputed_root()` → `u4.lookup` (`cached`/`cold`), con `u4.copy` y `u4.initial-generate` anidados; las 2 llamadas de `:893,913` envueltas como `u4.contract-regenerate` (hermanas, sin sustitución por caché).
- `tests/test_010_002_documentary_role_integration.py`: cuerpo de `_run_make_agents()` envuelto como `documentary.contract-regenerate` (las 2 llamadas de `:2303,2311`); `installed_product()` → `documentary.install-lookup` (`cached`/`cold`), con `documentary.install` (acción contractual real, instalador aislado) anidada; el frío contiene el `u3.lookup` anidado como fija el mapeo, sin copia adicional de producto.
- Clasificación según el mapeo/registro (preparación por defecto; accionales contractuales donde el mapeo las fija); el cierre por excepción lo garantiza el helper (`finally`, P2). Cuerpos, argumentos, resultados, aserciones y orden intactos: solo envoltorios `with` + un import por archivo. Nota: `u4.initial-generate` queda como hija real no-removible de su lookup conforme al registro (`preparatory-does-not-mean-removable`); la clasificación vive en el registro, no en el código (el helper no recibe clasificación).

## 5. Fix de base temporal (bloqueo de entorno, verificado preexistente)

`_temp_root()` prefería `/tmp/opencode` con solo `is_dir()`, pero en este entorno ese directorio pertenece a otro usuario (`another-user`, 15:28 Nov 5) y no es escribible → `PermissionError` en `mkdtemp`, que arrastraba a los 2 tests de generación de U3 y a 4 de D (importa `disposable_product`). Verificado preexistente: en árbol limpio (`git stash push -- tests/`) el mismo test falla idéntico. Corrección mínima (1 archivo, +3/−2, sin tocar aserciones ni transiciones): se exige `os.access(preferred, W_OK|X_OK)` y el fallback es `run_scoped_base()` (raíz estable de sesión de conftest) en lugar de `tempfile.gettempdir()` — el fallback ingenuo a `gettempdir()` revivía el archivo pero rompía la caché entre tests, porque conftest retira el TMPDIR por test al terminar (diseño 008-001: las cachés de módulo no pueden vivir bajo el TMPDIR por test; lo demostré por bisección: determinismo→duty con caché colgada de un dir retirado). Desvío honesto respecto de la orden literal (que pedía `gettempdir()`): mismo objetivo, base estable exigida por el diseño vigente.

## 6. Verificación post-marcas (secuencial, sin observador, `-o addopts= -p no:cacheprovider`)

- `tests/test_006_002_u1_delegation_section.py` → **10 passed en 5.03s** (muro 6s).
- `tests/test_006_004_u3_principle_single_source.py` → **15 passed en 3.30s** (muro 4s).
- `tests/test_006_005_u4_single_entry.py` → **7 passed en 6.69s** (muro 8s).
- `tests/test_010_002_documentary_role_integration.py` → **29 passed en 45.84s** (muro 46s).
- Focal T2 (`suite_operations` + tranche1 + tranche2) → **7 passed en 8.46s** (muro 9s).
- Focal T1 (`suite_profile`) → **17 passed en 21.10s** (muro 22s).
- Total afectado+focal: **85 passed, 0 failed**. **Suite completa no realizada** (ciclo focal + regresión proporcional como rutina; no se reclama autorización de corrida completa).
- Límites honestos: (a) en corridas en proceso sin los hookwrappers de fase del implementer, `nodeid/phase` quedan nulos salvo sonda — el contexto completo llega en corridas `close`; (b) la sonda cubrió a nivel evento la rama fría de C-U1; las ramas frías de U3/U4/D están envueltas con el mismo patrón probado y ejercitadas en verde por las corridas completas (neutralidad en frío demostrada), pero sus conteos fríos a nivel evento quedan para la calibración con el observador del implementer antes de la base (condición de entrada §4.4); (c) la diferencia 150s (sonda) vs 5s (U1 completo) es caché de página fría vs tibia en la primera copia grande con `.cdad`; ambas son mediciones reales, no oráculo.

## 7. Commits (solo `tests/`)

- `f8297789` — `test(017-001-T2): tranche-2 RED — lookups reales U1/U3/U4/documental emiten rama y son neutros` (1 archivo nuevo; sobre su padre el test falla como en §3).
- `942d33c3` — `test(017-001-T2): tranche-2 marcas en U1/U3/U4/documental` (4 archivos, +119/−94). Ya existía del turno anterior como pedía el encargo; este turno no lo duplicó.
- `27ac3a88` — `fix(017-001-T2): _temp_root exige writability del base temporal` (1 archivo, +3/−2).
- `git status` final: solo persiste el cambio preexistente de `docs/.cdad-state.json` (del orquestador, no tocado por mí). `git diff HEAD -- tests/` vacío. `scripts/`, contrato y derivados intactos.

## 8. Delta de inventario vivo propuesto (texto para que el orquestador lo materialice; `docs/` fuera de mi write-scope)

Agregar a `live-inventory-delta-T2.md`:

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_tranche2.py::test_real_tranche2_lookups_emit_branch_and_stay_neutral` | T2-check-7 | operation-markers-v1 (spec §4.2, PC-1 parte, INV-1/INV-2/INV-8) | RED tranche 2 + marcas verificadas (commits f8297789, 942d33c3) + fix base temporal (27ac3a88) |

Soporte (no verificadores): marcas reales en `tests/test_006_002_u1_delegation_section.py` (`u1.lookup` fría/reutilización + `u1.copy`/`u1.generate` anidados), `tests/test_006_004_u3_principle_single_source.py` (`u3.lookup` + `u3.copy`/`u3.initial-generate` contractual hija + `u3.contract-staging` ×2 hermanas; `_temp_root` con guarda de writability y base estable de sesión), `tests/test_006_005_u4_single_entry.py` (`u4.lookup` + `u4.copy`/`u4.initial-generate` + `u4.contract-regenerate` ×2 hermanas) y `tests/test_010_002_documentary_role_integration.py` (`documentary.contract-regenerate` ×2 hermanas + `documentary.install-lookup` con `u3.lookup` anidada en el frío + `documentary.install` contractual). 1 nodeid nuevo, disposición Añadir. Tranche-1 y P1–P5 sin cambios.
