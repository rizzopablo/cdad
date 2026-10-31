# Evidencia estructural — 010-003-documentary-pilot

Registro 1 de los tres que exige PC-14. Todo lo que sigue es medición ejecutada
sobre la versión de cierre; no hay estimaciones presentadas como medidas.

## 1. Versión medida

| Elemento | Identidad |
|---|---|
| Rama | `main` |
| HEAD al medir | `c229a671666262955962e8c6fa9f3d1a31747433` |
| Commit de preparación (corpus, candidato, muestras, clave, verificador) | `cd2d57b32e43e138cd831a3a40b5dd8fa075a67a` |
| Commit del producto (T4) | `7fcca219e119ea72f29d68f406642afa5b2e1483` |
| Commit del producto corregido (T7) | `6596e804654f9b76d3e7710c2011b312350fe75d` |
| Contrato | `spec.md` v5, `f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5` |
| Plan | `plan.md` v6, `49ce6f813aeb4e0bea0ff4f44d541a48deef29dc42f2af5aa6e05e5bf3352b04` |
| Producto | `product/relevamiento.md`, `007af655ef926e98df26920792f48d4098136cfc1d2a347a0cc427da1ef40e0f` |
| Verificador | `tests/test_010_003_documentary_pilot.py`, `8e2a1878538838306543e2767d54993480cb4147f8f7b205415d9f7f48e35737` |

## 2. Integridad de la fijación

Los diez artefactos fijados en `preparation-record.md` —dos fuentes, inventario,
candidato, cuatro muestras estructurales, clave y verificador— se re-calcularon
con SHA-256 sobre la versión de cierre: **10 de 10 coinciden con el registro**;
0 con deriva.

Anclas y citas del producto: **14 citas** a fuente inventariada con ancla
registrada; **10 anclas distintas** (`s1-f01`..`s1-f05`, `s2-f01`..`s2-f05`); la
resolución efectiva la comprueba el control, no esta tabla.

## 3. RED y control focal

RED registrado en T3, sobre `cd2d57b3`:

```
python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
.....F..
1 failed, 7 passed
```

El único rojo era la prueba del producto y fallaba por `AssertionError` de la
aserción de existencia, no por `FileNotFoundError` ni `ImportError`; los otros
siete verdes operaban sobre fixtures ya construidos.

Control focal sobre la versión de cierre:

```
python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
........                                                                 [100%]
8 passed in 0.12s
rc=0
```

### Los ocho controles y la promesa que protege cada uno

| Control | Qué acredita | PC |
|---|---|---|
| `test_broken_locator_is_rejected_with_document_reference_and_cause` | rechazo de un fragmento inexistente con diagnóstico de documento, referencia y causa | PC-04 |
| `test_corrected_locator_is_accepted_and_the_pair_differs_only_in_the_locator` | aceptación de la muestra corregida; el par difiere solo en el localizador | PC-05 |
| `test_semantically_defective_candidate_is_structurally_accepted` | el candidato con los tres defectos semánticos resuelve estructuralmente (dice que acredita resolubilidad, no persistencia) | PC-06 |
| `test_product_with_no_references_is_rejected` | rechazo del producto sin ninguna referencia | §2.4, PC-10 |
| `test_product_citing_an_uninventoried_source_is_rejected` | rechazo por fuente no inventariada, con diagnóstico que la nombra | §2.4, PC-10 |
| `test_the_product_cites_only_inventoried_fragments_and_at_least_one` | el producto tiene al menos una cita y toda cita resuelve a fuente y ancla inventariadas | PC-10 |
| `test_inventory_accounts_for_every_source_with_matching_digest_and_declares_synthetic_origin` | identidad `inventory-010-003-v1`, digest que coincide, anclas únicas, bidireccionalidad y declaración sintética | PC-01 |
| `test_control_verdict_is_invariant_under_rewrap_of_the_examined_document` | mismo veredicto y diagnóstico bajo rewrap, con las cuatro combinaciones declaradas | robustez del control |

## 4. Regresiones

```
python3 -B -m pytest -q --tb=no \
  tests/test_010_001_documentary_contracts.py \
  tests/test_010_002_documentary_role_integration.py
........................................                                 [100%]
40 passed in 48.25s
rc=0
```

Las dos regresiones declaradas por el plan —11 pruebas de `010-001` y 29 de
`010-002`— quedan acreditadas sobre la misma versión que el control focal.

## 5. Suite completa de cierre

```
python3 scripts/cdad-suite.py close --all \
  --evidence-root .cdad/evidence/010-003-closure
```

| Intento | Inicio (UTC) | Fin (UTC) | Resultado | Canario |
|---|---|---|---|---|
| 1 | 2026-10-31T20:08:30Z | — | **interrumpido sin veredicto** (la sesión del orquestador cortó la corrida) | — |
| 2 | 2026-10-31T20:19:28Z | 2026-10-31T21:24:10Z | **1926 passed, 5 skipped, rc=0**, 3878.91 s | delta 0 líneas |

El intento 2 corrió solo: el intento 1 había muerto antes de su inicio. La
selección fue `--all` (1926 nodeids más 5 omitidos por variables de entorno
ausentes, declarados en el propio `attempt.json`). El canario —`.config/cdad`,
`.config/opencode`, `.local/state/cdad` y entradas de primer nivel de `HOME`— no
registró deriva entre el antes y el después: los dos archivos tienen el mismo
SHA-256 (`a407fb0b…dec65`).

**Intento 1 conservado.** No produjo veredicto: se interrumpió la corrida y su
`attempt.json` no tiene `finished_at` ni `rc`. Se conserva completo en
`evidence/closing-suite/attempt-1-interrupted/` (su stdout parcial incluido), y
no se presenta como fallo de la suite ni como evidencia de nada.

**Evidencia durable copiada:** `evidence/closing-suite/` con `attempt.json`,
`stdout.log` (salida completa de los 1926 casos), `stderr.log` vacío y
`SHA256SUMS` con los digests de los canarios y de los archivos copiados. Los
canarios en sí no se copian (3.2 MB); se conservan sus digests, que es lo que
acredita el delta 0.

## 6. Límites del registro estructural

- El control acredita **resolubilidad estructural** de citas, inventario y
  anclas. **No** acredita fidelidad semántica del documento ni que sus
  afirmaciones sean verdaderas: eso lo sostienen la revisión de T6 y la
  re-verificación de T7 (`semantic-evidence.md`).
- Un verde estructural no se presenta como prueba de corrección documental.
- La muestra es sintética y sembrada; ver los límites de PC-15 en `closure.md`.
