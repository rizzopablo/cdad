# Closure — 016-002-gap-report

**Epic:** `epic-016-traceability-and-suite-review` — orden 2/3. **Cerrada:** 2026-11-03. No publicada ni desplegada.
**Contrato:** `docs/specs/016-002-gap-report/spec.md`, sha256 `315fad2c206b446acbb554942e71d9f4c247d5edadbbcbb7679ab33154bc7c4b`.

## Resultado
Existe un informe reproducible de huecos sobre contratos cerrados: el subcomando `gap-report` toma el universo del
estado (cierres registrados, con la fila actual por encima de sus copias históricas, deduplicación de equivalentes y
ambigüedad declarada), obtiene las obligaciones de los marcadores reales o del índice legacy sin mezclarlos, distingue
«no indexado» de «hueco», agrupa los huecos por promesa y admite exclusiones justificadas que no inflan la cobertura ni
borran el hueco subyacente. La salida es JSON determinista por stdout (misma entrada ⇒ mismos bytes; reordenar bindings
no cambia nada), con códigos 0/1/2 y sin mutar entradas ni ejecutar tests. `validate` de 016-001 queda intacto.

Commits: implementación `d2996e7e`, referencia `733d7afb`; tests RED `1f56d8fa`, `cf11fa15`, `c69e25c5`; review-fix
`00319407`.

## Evidencia
- `tests/test_016_002_gap_report.py`: 5 verificadores (R-A..R-E) cubriendo PC-1..PC-10; **5 passed**; los 11 de 016-001
  siguen verdes (16 en conjunto).
- Registro de la unidad en modo marcadores: 10 obligaciones cubiertas por 5 verificadores, `status: ok` contra colección
  real (`.cdad/local/016-002-collection.json`).
- `python3 scripts/cdad-suite.py validate`: `ok`, con el módulo y sus 5 nodeids inventariados (`delivery-evidence`).
- Regresión proporcional: 43 passed (plantillas y paquetes), 55 passed (documental), 16 passed (intake), 48 passed
  (instalador, dos archivos lentos incluidos), `cdad-doctrine-check.py` OK.
- Review independiente (`review.md`): 4 bloqueantes —B1, una exclusión duplicada suprimía el hueco; B2, el oráculo R-C
  no lo detectaba; B3, la referencia no nombraba al orquestador como materializador; B4, las filas no cerradas
  desaparecían del informe— más 5 observaciones, corregidos en `00319407` con verificadores endurecidos en `c69e25c5`.
  El review de cierre en sesión nueva (`review-closure.md`) verificó las seis correcciones contra el commit previo al
  fix: cerradas, sin bloqueantes nuevos.
- Suite completa de la feature: **no realizada** (recomendada al cerrar feature); la exige el gate de cierre del epic.

## Deuda
- N5 del review (no bloqueante, admitido por la spec): cuando un registro presente es inválido, el informe no reporta
  los huecos conocidos solo por marcadores; el resultado se declara explícitamente incompleto.
- Nit del review de cierre: con filas actuales conflictivas para una misma unidad, la unidad queda inválida (rc 1) pero
  el informe puede mostrar una fila histórica; no hay test que cubra ese caso.
- La comprobación es estructural: no acredita ejecución, pertinencia semántica, sensibilidad ni aprobación, y así lo
  declara el informe y su referencia.

## Siguiente
`016-003-suite-review-tranche-1` (depende de 016-001).
