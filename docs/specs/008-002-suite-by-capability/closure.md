# Cierre 008-002-suite-by-capability

Fecha: 2026-10-27. Epic: `epic-008-suite-coherence`. Feature 2 de 6.

## Resultado

La suite tiene un **selector canónico por capacidad y contrato** (`scripts/cdad-suite.py`), un **inventario
versionado** de sus 210 módulos y un **mapa acreditado** obligación→test del piloto. El cierre de una
unidad deja de ser un script local: `close` reserva un intento exclusivo y conserva su evidencia sin
sobrescribirla. `validate` da **rc 0** sobre el checkout real.

No se buscó reducir bytes: la medición del piloto dio **+3.317 bytes y +81 líneas LF**, y se publica tal
como salió (AJ6, directiva del owner).

## Contrato

`docs/specs/008-002-suite-by-capability/spec.md` — PC-1..PC-8, con AJ1–AJ7. Los tres últimos son
consecuencia de la operación real:

- **AJ6** — directiva del owner: test por contrato de usuario, no por cobertura; `deferred-hardening`
  obligatorio; el implementer queda fuera de la regla.
- **AJ7** — interfaz de `close` y forma de la evidencia (la spec prometía una garantía sin declarar la
  interfaz que la hace observable; un test-writer se bloqueó por eso y tuvo razón).

## Cambios

Producto:

- `scripts/cdad-suite.py` (nuevo, ~930 líneas): `validate`, `list`, `run`, `surface`, `measure`, `close`.
  · `validate`: integridad estructural (módulos inventariados, destinos existentes, obligaciones
  acreditadas frente a la **baseline** registrada en `measurement-before.json`, no frente a HEAD) y
  validación de `timing-disposition.json`.
  · `surface`: fail-closed; `--no-renames` para que un test trasladado consulte el mapa de la base;
  resuelve helpers por ruta y por stem; nunca devuelve selección vacía como éxito.
  · `close`: intento exclusivo (`os.mkdir` sin reintento), `attempt.json` atómico con `running` →
  `finished`/`interrupted`, `stdout/stderr` del hijo, canario con alcance declarado, resumen de pytest
  **verificable** (neutraliza `PYTEST_ADDOPTS` y `addopts`; si no puede parsear, marca `verified: false`
  con diagnóstico en vez de ceros).

Artefactos (`docs/specs/008-002-suite-by-capability/`): `suite-inventory.json` (210 módulos),
`pc-map.json` (29 registros, 17 nodeids del piloto), `variant-controls.json` (C0–C3),
`measurement-before.json`, `measurement-after.json`, `pilot-before.json`, `timing-disposition.json`.

Tests: `test_008_002_suite_selection.py` (25), `test_008_002_suite_evidence.py` (5),
`test_008_002_variant_controls.py` (4), `tests/suite_signal_helpers.py`, y la consolidación del piloto
(extracción de tres duplicaciones de forma y fusión R2 texto plano → PD-6).

## Evidencia

- Discovery `ef6256a`; spec y plan aprobados (`7a6e264`, `8b8d1b0`); plan-review con 3 bloqueantes
  cerrados; AJ6 (`a8cd249`) y AJ7 re-gateados.
- RED/GREEN por lote: T1 (`8a4d832`), T2 (`228aef5`), T3 (`03531bb` RED → `9e3fda8` GREEN → `69e2d7f`
  bloqueantes), T4 (`3bbfc8b`), T5 (`7c4e6a0` RED → `966bc1f` GREEN → `56ae3f9` review-fix), MINOR 3
  (`adc4240`).
- Reviews: T3 (3 BLOCKING + 1 de integración) y final (2 BLOCKING). Todos cerrados con test o con
  corrección verificada; el reviewer reprodujo el defecto del resumen con `PYTEST_ADDOPTS='-qq'`.
- **Gate de cierre:** `close --all` sobre el árbol final (ver «Gate» abajo).

## Gate

`python3 scripts/cdad-suite.py close --evidence-root .cdad/local/008-002/evidence --all`

| Dato | Valor |
|---|---|
| Intento (directorio exclusivo) | `.cdad/local/008-002/evidence/attempt-20261027T155119453267Z-9325-89d91e09/` |
| Commit / árbol | `adc4240`, `dirty=1` (el propio `docs/.cdad-state.json` del orquestador) |
| Resultado | **1774 passed, 5 skipped, 0 failed, 0 errors** |
| `rc` | **0** |
| `pytest_summary.verified` | **true** (la línea de estado se parseó con el entorno neutralizado) |
| Canario | **delta 0** |
| Duración | 52:02 (15:51:19Z → 16:43:33Z) |
| Skips | 5, con motivo: integraciones reales opt-in (005-002 ×2, 005-009, 005-010 PD-8, 006-001 PD-6b) |

Este es el **primer cierre del proyecto corrido por el mecanismo de cierre** y no por un script local: el
intento se reservó en exclusiva, escribió `attempt.json` en `running` antes de pytest y lo cerró en
`finished` con `rc`, resumen verificable, salidas y snapshots del canario. Los 5 skips son los mismos que
en 008-001: ninguno sustituye un verde.

## Límites declarados

- El inventario clasifica por docstring y procedencia histórica con `confidence` explícita; los módulos
  mixtos quedaron con alcance de módulo, no por nodeid. No es un análisis semántico.
- El mapa acreditado cubre el **piloto** (17 nodeids); el resto de la suite tiene capacidad y contrato,
  no trazabilidad obligación→test.
- `measure` es instrumento de reporte, no contrato.
- El canario de `close` cubre las rutas heredadas de 008-001 (HOME y config), no el árbol del repo.
- `surface` no está neutralizado frente a `PYTEST_ADDOPTS`: con esa variable falla **ruidosamente**
  (rc 1), no en silencio.
- El aislamiento por entorno no es una sandbox (heredado de 008-001).

## Deuda observada

- **Transporte de paquetes:** el runtime antepone una línea a todo prompt de subagente, verificado con
  sonda; los roles rechazan el paquete por no empezar en `---cdad-packet-json`. Esta unidad cerró dos
  subfases **sin paquete** como desvío declarado. Es el defecto que **008-004** debe cerrar.
- `deferred-hardening` de la spec: variantes de PC-5 con el mismo resultado observable, etiquetas
  `[ghost]`, atomicidad de `close` ante fallo del sistema de archivos, preservación semántica fuera del
  piloto, `surface` bajo `PYTEST_ADDOPTS`.
- `make validate` F011 preexistente.
- El gate de evidencia de 008-001 sigue siendo un script local; `close` lo reemplaza para esta unidad.
