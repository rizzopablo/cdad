# review.md — 015-002-intake-guards (stage 4)

Reviewer: sesión `<ses-342>`, paquete `015-002-intake-guards-reviewer-review-001` (route C
validada; render idéntico a PACKET.md). Diff `4e1ba75f..HEAD`; `pytest tests/test_015_002_intake_guards.py` → 9 passed.
Materializado por el orquestador (ADR-003).

## Hallazgos

- **F1 BLOQUEANTE (m)** — `cdad_packet.py` `_attribute_closed_units`: una unidad listada en más de un plan se asigna
  comparando números de línea (`row_index`) entre archivos distintos; solo un empate exacto bloquea. Contradice D3
  («fila estructural única»; ambigüedad bloquea). Falla realista: un plan abierto con tabla de contexto que nombra
  `013-004` por encima de la línea 49 → `open-unit` reabre la unidad (el defecto que la feature previene). Hoy no
  ocurre por layout. Fix: si ≥2 planes tienen fila estructural de la unidad → mismo error «cannot decide eligibility …
  ambiguous» nombrando los planes; eliminar la comparación entre archivos. Test: unidad en dos planes a distinta línea,
  uno de epic cerrado → bloquea (rc≠0, árbol y estado intactos), error con ambos planes.
- F2 opcional (m) — la rama PC-08 de fuente bloqueante (plan cerrado ausente/ilegible, localizador ambiguo) sin test;
  la cubre parcialmente el test de F1.
- F3 opcional (l) — ejemplo de observación pone `provenance.session: "manual"` con `session: null`; mejor `{}`.
- F4 opcional (m) — la ambigüedad depende del texto `"ambiguous"` del mensaje de `_locate_unit`; preferible retorno
  estructurado.

Sin hallazgo: PC-01..PC-07, PC-09 (validaciones intactas, solo mensajes; sin reclasificación automática; selección en
orden del plan; `--feature` rechazado sin escribir; mutantes de prefijo y ejemplo detectados).

Abstenciones: suite completa y regresiones del §6 de la spec (008-004, 005-007-t3, despacho/continuidad/recepción
congelada) no ejecutadas por el reviewer.

## Decisión del orquestador (HITL delegada)

F1: review-fix obligatorio (código + test, ver sesiones separadas: implementer para el fix, test-writer para el test).
F3: se corrige en el mismo fix (coste mínimo). F2 queda cubierta por el test de F1; F4 a deuda.
