Now I'll write the new RED test module. Let me first confirm the staging fixture pattern and the delegation-section anchor used by U1 (already imported names).
The fallback locator produced false positives (incidental `transport`/`receive` mentions). Tightening the region oracle to the contract's own naming:
## Role report — test-writer / RED (U5 de `006-002-delegation-by-layer`)

### 1. Archivos

| Archivo | Cambio |
|---|---|
| `tests/test_006_002_u5_transport_equivalence.py` | **NUEVO** (534 líneas) — RED de PD-5(a)(b)(c) |
| `tests/test_003_002_t1_receive.py` | **sin cambio** (regresión de la ficha: PD-5(c) no cambia el comportamiento de `receive`; verde) |
| `tests/test_004_003_t5_reentry_equivalence.py` | **sin cambio** (U5 **agrega** una subsección a `re-entry.md`; no fija ninguno de los textos que cambian → nada que reformular por A-1; verde) |

No se tocó `skills/`, `sources/`, `scripts/`, `agents/`, `docs/`. Los untracked de `docs/planning/` y `findings/` quedan intactos y **no** fueron `git add`.

### 2. Mapa test → PD

| # | Test | PD | Estado observado |
|---|---|---|---|
| 1 | `TestPd5aTransportEquivalence::test_pd5a_reentry_declares_the_transport_equivalence_route` | PD-5(a) | **FAIL** (AssertionError: sin región de equivalencia de transporte) |
| 2 | `…::test_pd5a_reentry_keeps_the_bytes_verbatim_and_the_receipt_pending` | PD-5(a) | **FAIL** (AssertionError: región ausente) |
| 3 | `…::test_pd5a_transport_route_is_the_same_for_handoff_and_cli_adapter` | PD-5(a) | **FAIL** (AssertionError: región ausente) |
| 4 | `TestPd5bMaterializationProtocolLink::test_pd5b_section4_links_to_the_materialization_protocol` | PD-5(b) | PASS → **guard pre-satisfecho por U2** (cierre de §4, línea 172: «Packet and re-entry are independent of the transport…» + nombre del protocolo) |
| 5 | `…::test_pd5b_delegation_sections_link_to_the_materialization_protocol` | PD-5(b) | PASS → **guard pre-satisfecho por U1** (enlace en la sección `delegation` de ambos orquestadores, co-ubicación) |
| 6 | `TestPd5cReceiveStillRequiresStagedFile::test_pd5c_receive_rejects_a_descriptor_with_another_source_kind` | PD-5(c) | PASS → **guard pre-satisfecho** (dueño funcional 003-002; verificado por comportamiento del CLI) |

Oráculo: conceptos con alternativas de idioma (`require_any` reusado de u2), con tres nombres normativos del contrato (`.cdad/inbox`, `semantic_status`, `staged-file`). La región de PD-5(a) se localiza exigiendo **`transporte` + `equivalenc` juntos** (discrimina la equivalencia de *corridas registradas* de 004-003); no hay respaldo por palabra suelta (evita un guard falso-verde por texto incidental — el primer borrador usaba un fallback y lo retiré al detectar un falso positivo).

### 3. Comandos y salida

```
$ python3 -m pytest tests/test_006_002_u5_transport_equivalence.py -q
3 failed, 3 passed in 2.84s
  FAILED …test_pd5a_reentry_declares_the_transport_equivalence_route
  FAILED …test_pd5a_reentry_keeps_the_bytes_verbatim_and_the_receipt_pending
  FAILED …test_pd5a_transport_route_is_the_same_for_handoff_and_cli_adapter
# los 3 fallos son AssertionError de contenido ausente:
#   grep -cE "ImportError|SyntaxError|ModuleNotFound" → 0

$ python3 -m pytest tests/test_003_002_t1_receive.py tests/test_004_003_t5_reentry_equivalence.py -q
15 passed in 6.70s            # regresiones de la ficha, verdes

$ python3 -m pytest tests/test_006_002_u1_delegation_section.py tests/test_006_002_u2_neutral_skill.py \
    tests/test_006_002_u3_runtime_references.py tests/test_006_002_u4_skill_without_models.py -q
40 passed in 9.32s            # regresión proporcional de la superficie 006-002
```

Suite completa: **no** corrida (política del packet — la cierra el closer).

### 4. Commit

```
git add tests/test_006_002_u5_transport_equivalence.py
git commit -m "test: 006-002 U5 RED — equivalencia de transporte en re-entry.md (PD-5)"
→ 1125c53  (1 archivo, 534 inserciones, todo bajo tests/)
```
Sin `--no-verify`, sin `git stash`, sin push; árbol limpio tras el commit (solo los untracked ajenos).

### 5. Declaraciones honestas

- **No abrí** `skills/`, `sources/`, `scripts/` ni `agents/` para derivar aserciones: el oráculo sale del spec (§2 PD-5(a)(b)(c), §3 INV-3/INV-4, §4 D-4) y del plan (ficha U5 + A-1). El CLI de recibo se **ejecuta** (`--help`, y el fixture de 003-002 T1), no se lee.
- **Límite del guard (declarado, PD-15):** los tests leen por diseño el producto publicado (los docs del skill son el artefacto cuando el entregable es una regla — precedente de 004-003 T5). Para calibrar el oráculo de §4 inspeccioné **una sola línea** de `SKILL.md` (§4:172) con los helpers del propio módulo; quedó declarado en el docstring. Los tests de 003-002 T1 imprimen diagnósticos que también muestran fragmentos de producto.
- **Guards pre-satisfechos #4/#5/#6 no se reclaman como verdes contractuales**: su deuda real (la subsección de PD-5(a)) vive en el GREEN de U5; el verde de #4/#5/#6 protege contra degradación.
- **Idea de fidelidad:** `validate-receipt` y `materialize` se exigen como los nombres que el contrato fija (verifiqué que son subcomandos reales del CLI); `transition` es el paso de estado del orquestador (no un subcomando) y por eso se pide como concepto, no como comando.
