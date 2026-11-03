# test-audit.md — 015-002-intake-guards (AUDIT, TEXTO FINAL)

**Feature:** 015-002-intake-guards · **Subfase:** AUDIT (test-writer, sesión <ses-344>)
**Contrato:** `docs/specs/015-002-intake-guards/spec.md` (sha256 `a8bafbdd…` verificado) · **Packet:** `015-002-intake-guards-test-writer-audit-001` (route C re-despachado: el primer despacho lo armó el orquestador a mano con un sha ajeno y fue rechazado como INVALID PACKET; execution v2 verificada).
**Método:** solo `tests/` + spec aprobada. Sin leer implementación. Sin editar tests.

**Regla (R2):** un verificador por promesa observable (A–C); sin cuota por PC.

## 1. Disposiciones (todo Mantener; cero Extender/Sustituir/Consolidar/Retirar)

| # | Verificador | Cubre | Disp. | PC |
|---|---|---|---|---|
| 1 | `test_004_002_t4_dispatch.py` (14 tests: claves cerradas, nulls, extra_keys_rejected…) | Observación de despacho: seis claves cerradas, sin recepción ante extras | Mantener c/u | Pre-PC-01 |
| 2 | `test_007_002_dispatch_recovery.py` (fixture seis claves, PC-1..16) | Forma de observación en despacho/reconcile/replace | Mantener | Pre-PC-01 |
| 3 | `test_003_004_t2_writeahead.py` (R-B1 decisions sin rationale…) | begin/checkpoint rechazan cuerpo malformado incl. decisions | Mantener | Pre-PC-02 |
| 4 | `test_003_004_t2_reviewfix.py` (E1 decision no vacía) | decision+rationale no vacías | Mantener | Pre-PC-02 |
| 5 | `test_003_007_t1_reference_classes.py` (S1, S5) | Vocabulario contract/living | Mantener | Pre-PC-04 |
| 6 | `test_005_001_tcorr.py` (write_scope fuera de política) | Diagnóstico write-scope con campo/motivo/opción | Mantener | Pre-PC-03 |
| 7 | `test_005_005_t1_replace_conserved.py` (selector no clasificado) | Texto de selector; sin exclusiones negativas | Mantener | Pre-PC-03 |
| 8 | 008-004 `test_pc06_begin_con_contract_cubierta…` | PC-06: rechazo pre-persistencia con referencia+selector | Mantener | →PC-04 |
| 9 | 008-004 `test_pc06_controles…` (control) | Contract fuera de scope + living dentro admitidos | Mantener | →PC-04/05 |
| 10 | 008-004 resto (PC-01/03/07, delegate/record, 011, legacy) | Paquete verificable, render canónico, replays | Mantener | Regresión |
| 11 | `test_005_007_t3_open_unit.py` (6 tests: primera queued, reposo, --feature…) | Orden del plan, selección queued | Mantener c/u | Pre-PC-06/07/08/09 |
| 12 | `test_005_012_t6_open_context_guard.py` (PD-16) | open-unit contexto v2 + guard | Mantener | Regresión |
| 13 | `test_005_013_t1_unit_projection.py` (8 tests, localizador) | Fila estructural única, fallback | Mantener c/u | Base D3 |
| 14 | `test_005_014_closure_replay.py` (PD-22–25) | Literales de cierre, --feature no desvía | Mantener c/u | Pre-PC-07/08 |
| 15 | 015-001 D2 + controles (replay, contrato alterado, referencia cubierta) | Replay durable; congelación no valida lo indebido | Mantener | Guardas |
| 16 | `test_008_003_lifecycle_decisions.py` (PC-03/04) | Autoridad/vigencia uniforme | Mantener | →PC-09 |
| 17 | Barrido resto (`005_012_t3`, `007_*`, `004_002_t7`…) | Sin otro fijador de textos cerrados/queued | Mantener | Regresión |

## 2. Mapeo RED (9 Añadir; Añ-E es revisión semántica, resto mecánicos CLI)

- **Añ-A** (PC-01): observación incompatible explica campo/problema + formato + ejemplo seis claves (nulls si no observados); el ejemplo no autoriza inventar.
- **Añ-B** (PC-02): decisions conserva rechazo + señala elemento + forma esperada + ejemplo objeto.
- **Añ-C** (PC-03): write-scope malformado identifica opción + exige CLASS=SELECTOR no vacíos + ejemplo; no convierte read en escritura.
- **Añ-D** (PC-04): begin con contract cubierta sigue rechazado pre-persistencia + ofrece estrechar scope / living cuando corresponda.
- **Añ-E** (PC-05, semántica): guía coherente documentada (docs=docs, límite carpeta de contrato, living mutable, contract fuera admitido, sin reclasificación automática, sin atajos).
- **Añ-F** (PC-06): open-unit omite queued de epic cerrado, abre primera elegible, orden conservado, intactas.
- **Añ-G** (PC-07): --feature de excluida rechaza nombrando unidad+epic, sin abrir ni persistir.
- **Añ-H** (PC-08): solo excluidas → sin candidata sin ejecución/cambios; fuente bloqueante → identifica fuente+motivo.
- **Añ-I** (PC-09): apertura compatible conserva reposo/dependencias/autoridad/vigencia/atomicidad; validate-state acepta; project-start.md actualizado.

## 3. Evidencia
Archivos modificados: ninguno. Commit: ninguno. Suite completa no realizada (momento «durante el ciclo»). Validaciones rc=0; spec sha coincide; greps + lecturas de tests listados.

## 4. Decisión del orquestador (HITL delegada, 2026-11-02)
Aprobadas las disposiciones (todo Mantener) y el mapeo RED (9 Añadir A–I; Añ-E por revisión semántica). Sin ajuste.
