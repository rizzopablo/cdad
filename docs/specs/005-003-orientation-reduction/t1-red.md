RED T1 completo. Reporte de cierre.

## 1) Archivo de tests

`tests/test_005_003_t1_compact_view.py` — 484 líneas, sha256 `9805bf6030f4c6f83d435a98dec1089e226bff58456335febb60c20eb63f02f0`.

Caja negra: cada test invoca el CLI real del repo por subprocess (`python3 skills/cdad-cycle/scripts/cdad_packet.py status --project-root <ABS>`), nunca importa el módulo. Fixtures autocontenidos en `tmp_path` (proyecto sintético vía los helpers compartidos `tests/test_004_002_t2_bootstrap.py`: `build_project`/`prepare_args`/`read_state`/`write_state`/`tree_snapshot`), con `HOME` del subproceso siempre en un tempdir vacío. Sin datos de demo, sin base real de sesiones, sin rutas de este host.

## 2) Mapeo test → postcondición/borde

| Test | Postcondición / borde |
|---|---|
| `test_pd1_compact_view_emits_single_bounded_document` | PD-1: único documento JSON, campos mínimos de §2.1 (+ sub-campos), sin `stage_history`, ≤16.384 B por default, determinista; borde «surfacea `active_packet.status`» |
| `test_inv1_status_is_read_only_state_byte_identical` | INV-1: estado y árbol byte-idénticos tras invocar la vista |
| `test_pd1_limit_fails_closed_without_partial_projection` | PD-1 borde C1: `--max-bytes` chico → rc≠0, stdout sin proyección parcial, diagnóstico nombra el límite y `--max-bytes N` |
| `test_pd1_limit_does_not_grow_with_history` | PD-1 borde: historial grande → documento ≤ límite, sin `stage_history`, y **byte-idéntico** al de historial chico (proyección función de campos operativos) |
| `test_pd2_entry_continuity_reconcile_for_prepared_packet` | PD-2 caso real: etapa en curso + paquete `prepared` → `continuity-reconcile` (nunca `next-unit`) |
| `test_pd2_entry_continuity_reconcile_for_dispatched_packet` | PD-2 borde: `dispatched` → reconciliar antes de repetir |
| `test_pd2_entry_next_unit_at_rest` | PD-2: reposo sin trabajo pendiente → `next-unit` |
| `test_pd2_entry_diagnosis_on_incomplete_config` | PD-2: sin `docs/cdad-policy.json` → `diagnosis` |
| `test_pd2_entry_does_not_depend_on_literal_inicializar` | PD-2 borde: objetivo con «inicializar» en el `REQUEST.json` del paquete → sigue `continuity-reconcile` |
| `test_pd5_relative_root_asymmetry_diagnosed_in_view` | PD-5 borde C4: raíz relativa → rc≠0 sin proyección; la causa nombra ambos CLIs (`cdad_packet` y `cdad_continuity`) y la raíz absoluta |
| `test_inv9_unknowns_declare_causes_not_fabricated_zero` | INV-9: `unknowns[]` es lista de causas (strings), nunca un `0` fabricado; ausencia surfaceada como `null` |

## 3) Focal y salida

```
$ python3 -m pytest tests/test_005_003_t1_compact_view.py -q
11 failed in 3.57s
```

Los 11 son `FAILED` (0 `ERROR`); las 11 excepciones son `AssertionError` de contrato y 0 son `ImportError`/`SyntaxError`/`NameError`/`AttributeError`/`JSONDecodeError`/`FileNotFoundError` (verificado con `--tb=short`). Ejemplos del modo de fallo:
- tests de emisión → `AssertionError: PD-1 violada: la vista 'status' debe emitir la proyección (rc=0); hoy rc=2; stderr="ERROR: cdad_packet.py: argument command: invalid choice: 'status' …"`.
- `test_pd1_limit_fails_closed…` → pasa rc≠0 y stdout vacío de hoy, y falla en `PD-1/C1 violada: el diagnóstico no nombra el camino legítimo para obtener más (--max-bytes N)`.
- `test_pd5_relative_root…` → falla en `PD-5/C4 violada: el diagnóstico no nombra la asimetría entre CLIs (no menciona cdad_continuity)`.

Confirmación del fallo correcto: hoy el subcomando `status` no existe → la CLI responde error de uso (rc=2). El test **no** falla en la invocación (el subprocess corre bien) sino en la aserción sobre la salida observable; `_status_document()` convierte cualquier stdout no-JSON en `AssertionError`, nunca en `JSONDecodeError`.

## 4) Commit

`2bdf314bbbe93acb6178e0d84c384bfe6dd246f2` — `test(005-003): RED T1 - vista compacta (status) + seleccion de entrada (PD-1/PD-2/PD-5; INV-1/INV-9)`; 1 archivo, solo `tests/test_005_003_t1_compact_view.py`. (`docs/.cdad-state.json` aparece modificado en el árbol pero **no** fue tocado por mí ni incluido en el commit: es el archivo de estado del orquestador.)

## 5) Bordes sin cubrir y por qué

- **`diagnosis` por «autoridad sin pin» (segunda rama de §2.2):** cubrí la rama «sin `docs/cdad-policy.json`» (inequívoca). La representación de «autoridad sin pin» no está fijada por la spec (¿falta `contract_sha256` en la entrada de aprobación? ¿falta `hitl_delegation`?); adivinarla arriesgaba un fixture fuera de contrato. Queda para el reviewer/implementer o un RED posterior.
- **Contenido semántico de `next` («con su fuente declarada») y de `authority`:** aserto solo presencia/estructura mínima; §2.1 no fija los nombres internos de `authority` ni de `next`, así que un oráculo más fino inventaría contrato.
- **`version` (verdicto §2.4) y el resto de PD-4/PD-6:** pertenecen a T2/T3 del plan (no a la clase T1); solo verifico que el campo exista.
- **Forma exacta de `unknowns[]` (lista de strings):** INV-9 dice «causas, nunca 0»; aserto la forma mínima. Si el implementer legítimamente emite `unknowns: []` en un proyecto sin ausencias, el test lo acepta (no fabrico una exigencia de no-vacío que la spec no pide).