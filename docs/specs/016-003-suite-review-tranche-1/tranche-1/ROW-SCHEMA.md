# Esquema de fila y delta del tramo 1 — formato exigido por el validador

Este archivo fija la forma exacta que `skills/cdad-cycle/scripts/cdad_suite_review.py validate`
acepta y que `skills/cdad-cycle/scripts/cdad_contract_links.py validate` exige para cada delta.
No es un contrato nuevo: es la forma del entregable de 016-003 (§5) tal como quedó verificada por
`tests/test_016_003_suite_review_tranche_1.py`.

## Fila de `audit.json`

```json
{
  "nodeid": "tests/test_x.py::Clase::test_y",
  "module": "tests/test_x.py",
  "revision": "<revisión congelada de selection.json>",
  "contract": {"path": "docs/specs/<unidad>/spec.md", "sha256": "<sha256 del archivo>"},
  "obligation": "PC-1",
  "pc_ids": ["PC-1", "PC-2"],
  "promise": "A",
  "check": {
    "assertions": ["fragmento literal de la aserción más relevante", "otra aserción literal"],
    "setup": "qué prepara el test (fixtures, archivos, repositorio temporal)",
    "helpers": ["nombre_del_helper_1", "nombre_del_helper_2"]
  },
  "consequence": "sin este test, el usuario … (concreta, no genérica)",
  "evidence": [{"path": "docs/specs/<unidad>/spec.md", "sha256": "…", "locator": "fragmento literal único"}],
  "references": [{"path": "docs/specs/<unidad>/spec.md", "sha256": "…", "locator": "fragmento literal único"}],
  "disposition": "Mantener",
  "motive": "por qué esa disposición y no otra",
  "candidate": null,
  "uncertainties": []
}
```

Reglas que el validador aplica (no son opcionales):

- `revision`, `contract.path`, `contract.sha256`, `promise`, `motive` no vacíos; `consequence` ≥ 8 caracteres.
- `check.assertions` lista no vacía de fragmentos literales del test (≥ 3 caracteres cada uno);
  `check.setup` y `check.helpers` (lista no vacía) presentes.
- `evidence` y `references`: listas no vacías; cada referencia tiene `path`, `sha256` y `locator`
  que aparece **exactamente una vez** en el archivo referido. Sirve el contrato o el propio test.
- `disposition` ∈ {Mantener, Extender, Sustituir, Consolidar, Añadir, Retirar}.
- `obligation` debe resolver:
  - contrato con marcadores reales `<!-- cdad:pc PC-n promise=X -->`: el id debe existir en los marcadores;
  - contrato sin marcadores: debe existir en `legacy_obligations` del registro enlazado por
    `contract.path` + `contract.sha256`, y `promise` debe coincidir con la del índice.
- `pc_ids` (campo extra, admitido): todas las obligaciones que el test protege; `obligation` es la principal.
- `candidate`: `null` o un objeto; un candidato NO es una redundancia probada.

## Delta de vínculo (`link_deltas[]` del informe)

Cada unidad cuyo contrato no tenga marcadores y cuyos tests del tramo protejan obligaciones
necesita un registro con la forma de `skills/cdad-cycle/references/contract-test-links.md`
(modo legacy por demanda):

```json
{"unit": "007-006-withdraw-and-republish",
 "registry": {
   "schema_version": 1,
   "unit": "007-006-withdraw-and-republish",
   "contract": {"path": "docs/specs/007-006-withdraw-and-republish/spec.md", "sha256": "…"},
   "legacy_obligations": [{"id": "PC-1", "promise": "A", "locator": "fragmento literal único del contrato"}],
   "links": [{"pc_ids": ["PC-1"], "verifier": {"kind": "test", "nodeid": "tests/test_x.py::…"},
              "protects": "promesa observable que protege", "evidence": [{"path": "…", "sha256": "…", "locator": "…"}],
              "limits": "qué NO acredita este vínculo"}],
   "note": "índice por demanda de esta revisión: cubre las obligaciones indexadas, no una extracción exhaustiva"
 }}
```

Reglas del registro:

- El universo de obligaciones es exactamente `legacy_obligations`: cada una debe tener al menos un
  vínculo (sin huecos) y cada vínculo debe citar ids existentes.
- `locator` de cada obligación: fragmento literal que aparece exactamente una vez en el contrato.
- Solo se indexan y vinculan las obligaciones que los tests del tramo protegen (§11: sin backfill).
- Los `nodeid` vinculados deben pertenecer a la colección del tramo (los tests auditados).
- El registro declara en `note` que cubre lo indexado y no es extracción exhaustiva.
- Una unidad puede tener más de un contrato asignado (p. ej. módulos que sirven a dos features):
  en ese caso el delta se entrega por contrato.

## Bloque de costo por lote

```json
{"commands": [{"command": "rg …", "exit_code": 0}], "files_read": 12,
 "notes": "qué se leyó y qué no"}
```

El orquestador agrega sesión, tokens y duración observadas desde el runtime.
