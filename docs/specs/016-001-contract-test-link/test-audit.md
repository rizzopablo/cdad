# test-audit.md — 016-001-contract-test-link (AUDIT, test-writer)

**Sesión:** `<ses-346>` · **Contrato:** `docs/specs/016-001-contract-test-link/spec.md` (sha256 `88b144e5…eca688e`)
**Método:** contrato aprobado + barrido de `tests/` por nombres de fichero y `def test_`; sin leer implementación; sin modificar tests.

## 1. Disposiciones (12 líneas, todas Mantener)

| # | Verificador | Disposición | Por qué no cambia |
|---|---|---|---|
| E-01 | `test_005_007_t6_templates.py` (4) | Mantener | Fija la plantilla de spec por referencia única; los marcadores `cdad:pc` son optativos y solo para contratos nuevos. |
| E-02 | `test_004_003_t5_reentry_equivalence.py` (8) | Mantener | La regla de equivalencia y su distribución siguen vigentes; 016-001 la consume, no la redefine. |
| E-03 | `test_005_003_t6_packet_contract.py` (7) | Mantener | Contrato de paquete intacto; 016-001 añade consumidores. |
| E-04 | `test_role_packet_consumers/render/review_regressions`, `test_packet_prepare` (49) | Mantener | El transporte byte-idéntico se usa, no se cambia. |
| E-05 | `test_005_005_t2_docs_policy.py`, `test_005_005_t4_integration.py` (9) | Mantener | Política de evidencia única; 016-001 separa ejecución y revisión apoyándose en ella. |
| E-06 | `test_005_006_t1_start_procedure.py`, `t2_intake` (21) | Mantener | Cableado al CLI instalado sin cambios. |
| E-07 | `test_005_007_t3_open_unit.py`, `t4_architect_report_materialization` (13) | Mantener | El patrón delta-como-texto + materialización es el que 016-001 exige; no se sustituye. |
| E-08 | `test_010_001_documentary_contracts.py` (11) | Mantener | No-copia de frases normativas y bytes de origen deben seguir verdes con la referencia nueva. |
| E-09 | `test_015_002_intake_guards.py` (10) | Mantener | Guardas de intake vigentes (esta auditoría existe porque funcionan). |
| E-10 | instalador: `test_install_ownership`, `test_install_review5_regressions`, `test_012_installer_ignore_pycache` (21) | Mantener | El CLI nuevo entra por el instalador existente con ownership y bytes de origen. |
| E-11 | `test_013_002_live_inventory.py`, `test_014_001_suite_evidence_defaults.py` (11) | Mantener | La colección atribuible se reutiliza; el inventario clasifica, no acredita. |
| E-12 | Resto del corpus (~1816 tests) | Mantener por incertidumbre | Sin indicios de conflicto; si GREEN altera un byte de skill, el fallo es señal para review-fix. |

Ningún verificador existente protege PC-1..PC-8 de 016-001 (cero coincidencias de `contract-test-link`, `contract_links`, `cdad:pc` en `tests/`; sin fixtures `016-*`).

## 2. Mapeo RED (6 Añadir, mecánicos)

| Grupo | PCs | Verificador | Sin este test, el usuario… |
|---|---|---|---|
| A | PC-1, PC-2 | `R-A1` vínculo recuperable + cada rotura identificada (hash distinto, `pc_ids` inexistente, referencia documental irresoluble, nodeid ausente, colección fallida) | …creería un vínculo que no resuelve o recibiría un `1` sin saber qué falló |
| B | PC-3, PC-4 | `R-B1` hueco agrupado por promesa; reutilizar un test entre obligaciones no exige más tests; `kind:review` exige motivo y referencia y no se presenta como ejecución | …no vería promesas sin verificador, o se le exigirían tests de más |
| C1 | PC-5 | `R-C1` nodeids nuevos (`CURRENT−BASE`) vinculados o informados; sin baseline la comprobación queda no realizada | …introduciría tests sin vínculo sin enterarse |
| C2 | PC-6 | `R-C2` delta como texto + materialización + exigencia en Review/cierre, sin gate de RED para intermedios | …perdería deltas en los handoffs o bloquearía RED |
| D1 | PC-7 | `R-D1` sin registro: `not_configured` no bloqueante; registro corrupto → `invalid` | …quedaría bloqueado, o una corrupción pasaría como ausencia |
| D2 | PC-8 e invariantes | `R-D2` ámbito y límites declarados; reordenar no cambia conjuntos; invariantes una a una | …confundiría un verde estructural con aceptación semántica o con ejecución |

La revisión semántica (pertinencia de `protects`, suficiencia del `reason`, acotación del índice legacy) queda para el reviewer.

deferred-hardening: extracción general de Markdown histórico, autenticación criptográfica de colecciones, inferencia de pertinencia, rendimiento y backfill masivo.

## 3. Evidencia
Archivos modificados: ninguno. Commit: ninguno. Validaciones rc=0; render `PACKET-MATCH`; route C byte-igual.

## 4. Decisión del orquestador (HITL delegada, 2026-11-03)
Aprobadas las 12 disposiciones y el mapeo de 6 RED. Sin ajuste.
