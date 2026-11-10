# Closure — 017-001-suite-performance

**Epic:** `epic-017-suite-performance` — orden 1/1. **Cerrada:** 2026-11-08.
**No publicada ni desplegada** (reservado al dueño).
**Contrato:** `docs/specs/017-001-suite-performance/spec.md`, sha256
`472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e`.
**Revisión aceptada:** `bf0e7483c0403b545760efbcb0134cd958d31a30`.
**Aceptación:** `acceptance.md` (HITL delegada por el dueño).

## Resultado

Existe una suite instrumentada, con base reproducible, atribución de costos sin
cifras ficticias, y un lote paralelo seguro y medido:

- **Base (T4):** 4994.27 s, 2029 passed + 5 skipped, revisión `7426438b`;
  preparación medida 186.2 s (3.73 %) y resto 96.27 % **no desglosado**.
- **Atribución (T3/T4B):** `reconcile` reproduce la conciliación desde la
  evidencia cruda; la muestra de los seis archivos más caros (837 s) mostró 75 %
  de proceso externo. Auditoría de las 76 invocaciones de `install.sh`:
  **0 de 76 son preparación pura compartible** (47 acción bajo prueba, 29
  mixtas). La optimización serial de preparación queda **sin costo reducible
  demostrado**, no por falta de voluntad sino por evidencia.
- **Decisión (T6):** paralelismo con workers configurables (default 2, tope
  `nproc-1`), subcomando `parallel` separado, `close` serial intacto.
- **Corrida final (T7):** `--all` sobre `bf0e7483`, misma revisión y árbol
  limpio en ambas pasadas: **4459 s serial → 2593.15 s con 2 workers = 41.84 %**
  de reducción de pared (objetivo registrado ≥ 15 %), con **equivalencia exacta
  por nodeid** (2059 vs 2059, 0 diferencias; 2054 passed + 5 skipped en ambos).

## Lo que la feature no promete

- No autoriza poda ni declara redundancia en la suite.
- No explica el 89.9 % restante: se publica como **desconocido**.
- La garantía de familia de procesos depende de Linux (`prctl` + `/proc`); sin
  ella el lote no se acepta (`family_verifiable: false` ⇒ descarte).
- Carga del host y canario del checkout **no instrumentados en la pierna
  serial** de `close`: declarado como límite, no como condición demostrada.
- Un solo host y una repetición por régimen: sin significancia estadística.

## Defectos reales encontrados y corregidos en el camino

T7 hizo su trabajo: descubrió tres defectos del propio runner y cuatro de
integridad del veredicto, todos con test que los protege.

1. El veredicto del canario comparaba `max_mtime_ns`: rechazaba corridas con
   contenido byte a byte idéntico. Se corrigió a veredicto por contenido.
2. Los meta-tests usaban un timeout de liveness de 120 s fuera de la convención
   de la familia (300 s).
3. `test_010_004_t5_e2e` copiaba el producto (450 MB) dentro de `.cdad/tmp` del
   checkout, y otro worker lo escaneaba: interferencia real entre workers. Su
   scratch salió del árbol.
4. Cuatro huecos de integridad del veredicto: familia no acreditable,
   canario tomado antes de la limpieza, errores de lectura tratados como
   contenido estable, y evidencia reutilizable entre invocaciones.

## Commits principales

T1 `b8f7cbe6`…; base T4 `7426438b`; T3 `reconcile`/`entry-check`; T6 runner y
oráculo; correcciones T6: `4dac7264`/`cf417722` (worker vacío, paredes,
huérfanos, canario, preparación), `2584f456`/`a12ba4c2` (huérfanos por
descendencia), `1cb30ecf`/`0c5e4ab0` (setsid y huella por contenido),
`66fa16cb`/`e1f368a0` (ventana de gracia); T7: `44d15f7c`/`6645a340` (veredicto
por contenido), `2981f9aa` (liveness), `03c22039` (scratch fuera del checkout),
`7685333b`/`474064e7` (fail-closed); corrida final `bf0e7483`; aceptación
`<pendiente de este commit>`.

## Evidencia

- `performance/baseline.json` / `baseline.md` — base T4.
- `performance/remainder-measurement.md` — qué hay en el resto.
- `installer-calls-audit.md` — 76 invocaciones clasificadas.
- `performance/parallelism.md` — contrato del lote, tres intentos descartados
  con su causa, cifras vigentes y límites.
- `performance/comparison.json` — comparación final calculada (no transcripta).
- `.cdad/tmp/017-001-final-evidence/` — evidencia cruda del par vigente;
  crudos en `evidence/017-001-final4/{serial,parallel}`.
- `tests/test_017_001_suite_parallel.py` — 22 verificadores del lote.
- `python3 scripts/cdad-suite.py validate` → `status: ok`, 2059 nodeids.

## Estado del inventario vivo

`tests/test_017_001_suite_parallel.py` queda con **22** tests en
`docs/specs/008-002-suite-by-capability/suite-inventory.json`; el módulo nuevo
de la feature son `tests/test_017_001_suite_{profile,operations,reconcile,external,tranche1,tranche2,parallel}.py`.
