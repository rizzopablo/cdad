Commit `3b7060b8` created (tests/ only). All evidence collected. Final report:

---

# FINAL TEXT — test-writer RED-021 (T4-adicional, 017-001-suite-performance)

**Packet:** `017-001-suite-performance-test-writer-red-021` — route C validated (identification == canonical render; contract sha256 `472bab0c…` == spec file; execution context v2). No se tocó `scripts/` ni el contrato. No se leyó implementación: solo `tests/` + spec y entradas declaradas.

## Objetivo ejecutado

Medición adicional del resto (decisión del dueño: medir antes de fijar objetivo, spec §4.4). Marcas `external.<clase>` sobre `tests/suite_operation_markers.py` en los seis archivos más caros de la base, envolviendo SOLO la llamada a subprocess, sin cambiar comandos, argumentos, entornos, aserciones, orden ni resultados. Ningún archivo resultó in-process: los seis tienen llamadas externas reales (inventario AST: 9 sitios `subprocess.run`, cero `check_output`/`check_call`/`Popen`).

**Clases estables declaradas:** `external.install` = `bash <producto>/install.sh`; `external.cli` = `bash scripts/validate-subagents.sh`; `external.python` = `[sys.executable, <cli>, …]`.

**Costuras mínimas (2, sin cambio de conducta, argv/env byte-idénticos):** `run_validator()` en 009 (2 llamadas inline idénticas) y `_run_product_install()` en 010_002 (1 llamada inline); hacen los 9 sitios invocables por la sonda.

## RED (right reason)

Nuevo `tests/test_017_001_suite_external.py::ExternalBoundariesProbe::test_external_boundaries_emit_observed_events` (1 test, 8 patas con subTest; PC-5/PC-6, INV-6; consecuencia: *"sin este test, el usuario podría fijar el objetivo (PC-4) sobre resto no atribuido y el informe presentaría tiempo externo no medido como costo explicado"*).
- Pre-marcas (extracción presente, cero sitios emisores — probado por AST en las 6 revisiones HEAD): `AssertionError: 0 != 1 : 009-install.sh: se esperaba exactamente un begin external.install; eventos=[]`. AssertionError sobre conducta faltante, nunca ImportError. Tiempo 1.1 s.
- Post-marcas: **1 passed en 7.07 s** (las 8 patas emiten su par begin/end con `termination: ok`; rc neutro en las 7 patas `--help`; la pata del validador conserva su rc productivo ≠0 y su neutralidad la cubre `test_pc5` en la corrida completa).

## Corrida de los seis archivos (una vez por régimen, foreground secuencial, sin carga concurrente)

Comando exacto por archivo (régimen neutro): `python3 -m pytest <archivo> -q -p no:cacheprovider` → `RC`, `WALL_S` (pared, resolución 1 s). Régimen sonda: mismo comando + `-p tests.tmp_ext_probe_plugin` con `EXT_PROBE_OUT=$PWD/tests/tmp_ev_<i>.json` (plugin temporal, borrado antes del commit).

| Archivo | Tests | Neutro (sin observador) | Sonda (pared) | external.install | external.cli | external.python |
|---|---|---|---|---|---|---|
| `tests/test_009_001_installer_agent_overlay.py` | 12 passed | RC=0, 227 s | RC=0, 213 s | 31 pares | 2 pares | 0 |
| `tests/test_010_002_documentary_role_properties.py` | 7 passed | RC=0, 206 s | RC=0, 190 s | 1 par | 0 | 6 pares |
| `tests/test_install_ownership.py` | 11 passed | RC=0, 150 s | RC=0, 135 s | 22 pares | 0 | 0 |
| `tests/test_install_review5_regressions.py` | 6 passed | RC=0, 105 s | RC=0, 99 s | 15 pares | 0 | 0 |
| `tests/test_role_packet_render.py` | 17 passed | RC=0, 120 s | RC=0, 121 s | 0 | 0 | 295 pares |
| `tests/test_012_installer_ignore_pycache.py` | 4 passed | RC=0, 54 s | RC=0, 54 s | 7 pares | 0 | 0 |
| **Total** | **57 passed, 0 failed** | **862 s** | **812 s** | **76** | **2** | **301** |

Eventos totales con sonda: 379 pares begin/end `external.*` (76 install + 2 cli + 301 python), más marcas preexistentes (`isolation.seed`, `u3.*`, `product.lookup`) intactas. En las 6 corridas con sonda: `exitstatus: 0`, `begin == end` en toda operación (sin intervalos filtrados), `terminations: ["ok"]` en todos los end.

## Veredicto de neutralidad

- **Sin observador: VERDE.** Los seis archivos pasan igual (57 passed, 0 failed); paredes 227/206/150/105/120/54 s vs base 299/241/178/151/149/102 s — mismo orden de magnitud, diferencia por carga del host (la base declara convivencia con actividad del operador; esta corrida convivió solo con el sistema).
- **Con sonda: LOS EVENTOS LLEGAN.** 379 pares `external.*` con `termination: ok` durante ejecución real; verificado además en 2 tests individuales (render→`external.python` 1 par en 1.38 s; 012→`external.install` 1 par en 16.89 s, ambos exit 0).
- Sobrecosto de las marcas indistinguible del ruido entre corridas (sonda 812 s vs neutro 862 s; la diferencia es varianza de carga, no ganancia — no se afirma ahorro).

## Límites declarados

1. La sonda usa invocaciones rápidas degeneradas (`--help`, validador real) que atraviesan la misma línea envuelta con la misma forma de comando; no mide duraciones productivas (convención 11: sin umbrales como oráculo).
2. Los conteos por clase son ocurrencias en esta corrida y host, no tiempos atribuidos: no fundamentan por sí solos una optimización (spec §4.4).
3. La captura agregada por el observador del `close` (implementer) queda pendiente: el sumidero de sesión usado aquí es el mismo contrato que ese observador consumirá.
4. Reloj de pared resolución 1 s; carga del host no muestreada.

## Commit

`3b7060b8` — solo `tests/` (7 archivos: 6 modificados + `tests/test_017_001_suite_external.py` nuevo; 210 inserciones, 59 eliminaciones). Temporales de sonda eliminados pre-commit. `docs/.cdad-state.json` conserva únicamente su modificación preexistente (no mía, no commiteada).

## Delta de inventario vivo (texto para materializar, disposición Añadir)

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_017_001_suite_external.py::ExternalBoundariesProbe::test_external_boundaries_emit_observed_events` | T4-adicional-check-1 | external-markers-v1 (spec §4.4 focal adicional, PC-5/PC-6 parte, INV-6) | RED red-021 (AssertionError 0!=1 sin marcas; verde con marcas) |

Soporte (no verificadores): marcas `external.install/external.cli/external.python` en `tests/test_009_001_installer_agent_overlay.py` (3 sitios), `tests/test_010_002_documentary_role_properties.py` (2 sitios), `tests/test_install_ownership.py`, `tests/test_install_review5_regressions.py`, `tests/test_role_packet_render.py`, `tests/test_012_installer_ignore_pycache.py` (1 sitio c/u). 1 nodeid, disposición Añadir. T1–T3 sin cambios.

## Archivos modificados

M `tests/test_009_001_installer_agent_overlay.py`, M `tests/test_010_002_documentary_role_properties.py`, M `tests/test_install_ownership.py`, M `tests/test_install_review5_regressions.py`, M `tests/test_role_packet_render.py`, M `tests/test_012_installer_ignore_pycache.py`, A `tests/test_017_001_suite_external.py`.
