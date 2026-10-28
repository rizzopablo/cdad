# Discovery 008-005-ci-gate — mapa verificado y opciones de contrato

## Paquete validado (ruta A)
Un solo marcador, bloque cerrado; `validate-packet` rc=0; render canonico vs. bytes recibidos identicos
(sha256 1525e134…c71445, 6031 bytes, diff vacio). Contrato 03dd389a…, plan del epic 293f9281…, los 3
instruction_sources coinciden. HEAD 09d38c9.

## Superficie verificada
| Entidad | Evidencia |
|---|---|
| Selector/cierre | `scripts/cdad-suite.py`: validate/list/run/surface/measure/close |
| `close` | `:880-955`; reserva dir por intento (`:818`), pytest `-v -rs -o addopts= -p no:cacheprovider` con todos los nodeids por argv (`:870`), escribe `attempt.json` + logs + canarios |
| `surface` | `:541-568`; `--collect-only` (`:965`) permite seleccionar sin ejecutar |
| `validate-state` | wrapper de 11 lineas; corre sin `--execution-context` leyendo el bloque `execution` del state |
| Gate por superficie local | `.cdad/local/surface-gate.sh:5` con ruta hardcodeada; no versionado (`.gitignore:11`) |
| Validadores | `Makefile` (agents, validate); `tests/validate-consistency.sh` (182 asserts, F011 en `:576`); `validate-odoo-specialization.sh` (68/68); `cdad-doctrine-check.py` (rc 0) |

### Correcciones a los hechos del encargo
- (d) **1813 nodeids, 213.749 bytes** de argv (~10% de `SC_ARG_MAX` 2.097.152): viable.
- (e) `skips[].reason` vacio **por truncado de la linea de estado a `COLUMNS`**: con `COLUMNS=80` 5/5 vacios;
  con `COLUMNS=1000` 5/5 completos (678/505/504/201/277 chars). `parse_pytest_verbose` ya captura el motivo.
- (f) F011 pasa con HOME real; con HOME vacio falla (`runtime agents dir missing` + `install.sh --check`).
- (a) no hay CI; `origin` es GitHub, `main` sin `origin/HEAD`.

### Restriccion dura: politica de rutas
`Makefile` y `.github/workflows/*` clasifican **unclassified**; `scripts/*.py` = implementation; `docs/` =
documentation; `tests/` = test. Versionar un workflow o un target exige **enmienda de politica del dueno**:
el unico hogar admitido hoy para el gate es `scripts/` (+ `docs/`).

### Portabilidad
`grep -rln "<HOME>"` sobre fuentes versionadas → **0**; las 286 coincidencias son `__pycache__` y el
script local. Checkout solo-versionado (`git archive`): `validate-state` VALID rc 0; `pytest --collect-only`
1813 en 6 s; `validate-odoo-specialization` 68/68; doctrina rc 0. `close --nodeids` de 1 test deja `commit:
null`/`dirty: null`: **un rc=0 sin commit es un verde no atribuible**.

### Bordes que hoy enrojecen (legitimos)
- Diff solo `docs/` → `surface` rc 1 «seleccion vacia».
- Diff solo `README.md` → rc 1 «cambio sin superficie clasificada».
`selection_for_changes` solo salta `docs/`, no los `documentation_files` de la politica.

### Costo
46-103 min segun carga; sin paralelismo; `close` no tiene techo propio (si la suite cuelga, el gate cuelga).

## Opciones de contrato
- **D1 (recomendada):** entrypoint `scripts/cdad-ci-gate.py` que ejecuta **en orden y una vez**:
  `validate-state` → `surface --collect-only` (solo clasificacion) → `close --all` (unica corrida de pytest) →
  consumo del `attempt.json` → veredicto JSON + resumen humano. Descartadas: `surface` + `close` (duplica
  ejecucion), `close` sin `surface` (pierde el mapeo), workflow/`make ci` (politica, no verificable).
- **D2:** consumir `cdad-suite.py surface` y retirar `.cdad/local/surface-gate.sh` del camino operativo
  (dos mecanismos con el mismo nombre; el local hace grep de basenames).
- **D3:** fijar `COLUMNS` en el entorno del hijo en `run_pytest_to_logs`; parser sin cambios.
- **D4:** atribucion fail-closed (`commit != null`, `dirty == 0`, `state == finished`, `verified`, un intento).
- **D5:** el canario se **reporta**, no bloquea (deuda `HOME-LEAK-DERIVED-AGENTS` sigue en 008-001).
- **D6:** `--base` obligatorio, sin default silencioso.
- **D7:** `make validate` fuera del gate (necesita instalar agentes en HOME efimero); si `doctrine-check` y
  `validate-odoo-specialization` (ambos portables, rc 0).
- **D8:** evidencia por corrida bajo `.cdad/local` + `gate.json`; incluye nodeids fallidos con motivo, skips
  con motivo, loadavg (diagnostico, no decision).
- **D9:** el costo en push docs-only es decision explicita del dueno (no se debilita por cuenta propia).
- **D10:** `suite-report.md` se resuelve como reporte por corrida en la raiz de evidencia.

## Postcondiciones candidatas
PC-1 gate portable en cualquier checkout sin rutas del host ni HOME instalado; PC-2 una sola ejecucion de
pytest (via `close`) y `surface` solo como seleccion; PC-3 verde atribuible (commit/dirty/state/verified) o
salida != 0; PC-4 rojo diagnosticable sin repetir la suite; PC-5 skip nunca leido como verde (cada
`skips[].reason` nombra su variable); PC-6 la carga del runner no produce rojos falsos y la cota sigue
discriminando; PC-7 documentar no rompe el gate; PC-8 sin secretos ni instalacion, HOME vacio, sin push.

## Puntos abiertos
Runner/proveedor (politica + no verificable); `make validate` en CI; canario; costo docs-only; alcance de
cada cota ajustada (16 sitios en 5 archivos, specs cerradas 005-010/006-001: leer el PC original antes de
re-anclar); superficie de test del propio gate (constructor de veredicto puro + una costura al binario).

## Diferible
Reloj inyectable (T-C), workflow/activacion en runner (dueno), paralelismo, cache/reintentos (prohibidos).

## Evidencia
Sin archivos modificados; temporales en /tmp/opencode. Comandos clave y salidas en el informe del rol
(validate-packet rc 0; surface rc 1 vacio / rc 0 con 1813; COLUMNS 80 vs 1000; HOME vacio 17 passed;
consistency 182/1 F011 con HOME falso; odoo 68/0; doctrina rc 0; cleanclone 1813 collected).
