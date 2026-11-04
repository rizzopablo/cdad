# Closure — 016-001-contract-test-link

**Epic:** `epic-016-traceability-and-suite-review` — orden 1/3. **Cerrada:** 2026-11-03. No publicada ni desplegada.
**Contrato:** `docs/specs/016-001-contract-test-link/spec.md`, sha256 `88b144e5a8bb278a3e34d0336e5e4a4cd9f8ca324cd75657e55dc6149eca688e`.

## Resultado
Existe una forma mínima y verificable del vínculo test→contrato→promesa, separada del inventario (que clasifica) y del
mapa de PC (que guarda genealogía): registro JSON por unidad, validado por una CLI autónoma (`validate`, códigos 0/1/2,
JSON determinista, sin escribir ni ejecutar tests). El universo de obligaciones son los marcadores reales `cdad:pc`
—una línea que es exactamente el comentario—, con índice legacy por demanda para contratos anteriores; los ejemplos en
prosa o en bloques cercados no cuentan. Admite verificadores `kind: review` con motivo y referencia resoluble, sin
dispensar la promesa. El payload declara `mode`, `coverage` y `obligations`, y un registro sin obligaciones es
`invalid`, nunca verde.

Entregables documentales: referencia canónica del formato y del payload, plantilla de spec con marcadores optativos y
punteros de PC-6 en handoffs, TDD y re-entry (un solo hogar del formato, sin gates nuevos).

Commits: RED `50ef71da` (6 verificadores), `f809c2e7` (corrección de fixtures 0/ok), `475ebe31` (R-B2), `49ad6fa7`
(R-B3..R-B6); GREEN `2486bf1b`, `5267fcc0`, `1aad6953`; review-fix `f767cc62`.

## Evidencia
- `tests/test_016_001_contract_test_link.py`: 11 verificadores, **11 passed** (R-A1, R-B1..B6, R-C1, R-C2, R-D1, R-D2).
- Registro de la unidad materializado y validado contra colección real: `status: ok`, `mode: legacy`, 8 obligaciones
  (PC-3 con dos verificadores), rc 0 (`.cdad/local/016-001/collection.json`).
- `python3 scripts/cdad-suite.py validate`: `ok` con el módulo y sus 11 nodeids inventariados (`delivery-evidence`).
- Regresión proporcional: 99 passed (núcleo: plantillas, documental, re-entry, paquetes, intake), 15 passed (instalador:
  ownership y pycache), `cdad-doctrine-check.py` OK.
- Review independiente (`review.md`): 2 bloqueantes —B1, un backtick suelto se tragaba marcadores y daba falso verde;
  B2, el resultado no declaraba modo ni obligaciones y un registro vacío daba `ok`— más 2 nits, corregidos en
  `f767cc62` y verificados en sesión nueva (`review-closure.md`): cerrados, sin bloqueantes nuevos.
- Suite completa de la feature: **no realizada** (recomendada al cerrar feature); la exige el gate de cierre del epic.

## Deuda
- FYI del review de cierre: un marcador dentro de un span multi-línea cerrado en el mismo párrafo se trata como ejemplo
  (lo fijan spec y tests); en CommonMark estricto sería real. Sin camino realista de falso verde con los contratos actuales.
- O2: que los handoffs lleven la ruta del registro depende de que el orquestador la escriba en el objetivo del paquete;
  ningún test mecánico lo cubre.
- La unidad usa el índice legacy para su propio contrato (el formato de marcadores nace con esta feature): el registro
  declara cobertura de lo indexado, no extracción exhaustiva.
- Un cambio posterior del contrato o de los nodeids no revalida el registro automáticamente en cada transición.

## Siguiente
`016-002-gap-report` (depende de 016-001).
