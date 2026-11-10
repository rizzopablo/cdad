Route C validada; trabajo ejecutado solo con el paquete.

**Validación control-plane (route C)**
- `validate-request` rc 0; `validate-packet` rc 0.
- `render --request ...` coincide byte por byte con `PACKET.md` (`diff` limpio); `render --route C` reproduce la identificación del despacho (packet_id `017-001-suite-performance-test-writer-red-016`, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`, execution_id `exec-017-001-suite-performance-001`, mismas rutas packet/request/context/project_root).
- `sha256sum spec.md` = `472bab0c…` coincide. Execution context `schema_version: 2` (v2, sin switch silencioso).
- Sin cuerpo inline: admisible en ruta C; sin mezcla de rutas. No se buscó otro paquete.

**Alcance respetado**
- Leídos solo los 4 inputs declarados más deltas/red previos bajo la misma raíz de contrato (`docs/specs/017-001-suite-performance`): `spec.md`, `review-T3-002.md`, `t3-aggregator-contract.md`, `tests/test_017_001_suite_reconcile.py`. No se leyó implementación (`scripts/`, `agents/`, etc.); la CLI se ejerció como caja negra, nunca se inspeccionó su código.
- Escrito solo `tests/test_017_001_suite_reconcile.py`. `docs/.cdad-state.json` ya figuraba modificado antes y quedó fuera del commit.

**Pre-RED (contribución vs. lo existente)**
- 11 tests vigentes: 8 casos contables + código 2 + vínculo clave-selección + residuo exterior 1 s. Ninguno ausenta `selection` de `attempt.json` ni usa un escalar irresoluble; el fix omitido en silencio (`continue` sin motivo) los deja pasar. El test nuevo declara esa diferencia; sin él el usuario inicia la base sin el dato que vincula clave con selección.

**Test agregado (append-only, +122, 11 vigentes intactos)**
- `test_entry_check_missing_or_unresolvable_selection_fails_selection_coverage` → PC-1 (identidad de selección, §4.4 + contrato operativo §selection-coverage), INV-6 (omisión no es pase). Promesa observable: la entrada a la base solo se acredita con selección declarada verificable; consecuencia sin este test: base acreditada sobre cobertura no vinculada.
- Contraste positivo: C-R→intento completo que declara lo esperado sale 0/satisfied=true. Casos negativos en temporales descartables (evidencia real intacta): copia sintética sin campo `selection` y copia con `selection=999` (escalar irresoluble) deben salir 1/satisfied=false con check `selection-coverage` en falso nombrando `C-R`.

**Evidencia RED (comandos exactos)**
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py::test_entry_check_missing_or_unresolvable_selection_fails_selection_coverage` → **1 failed in 0.63s**, `AssertionError` de promesa ausente (`con attempt.json sin campo selection la entrada debe quedar bloqueada (rc 1); salio 0 … (satisfied=true)`), nunca ImportError/colección.
- Regresión proporcional: mismo runner con `-k "not missing_or_unresolvable"` → **11 passed, 1 deselected** (los 11 vigentes siguen verdes).
- Suite completa no realizada (ciclo focal + regresión proporcional como rutina; sin autorización para corrida completa en este RED).

**Commit**
- Solo `tests/test_017_001_suite_reconcile.py`: commit `4717f8ec` — `017-001 T3 RED correctivo review-T3-002: seleccion ausente o irresoluble como fallo nombrado de selection-coverage`; `git show --stat HEAD` = 1 file, 122 insertions(+), 0 deletions en tests vigentes.

**Delta de inventario vivo (texto, no editado por estar fuera del write_scope)**
- `tests/test_017_001_suite_reconcile.py`: 11 → 12 verificadores T3 (1 añadido RED que cubre 2 sub-casos: ausente + escalar; 0 modificados, 0 retirados/sustituidos).
- Nodeid nuevo: `tests/test_017_001_suite_reconcile.py::test_entry_check_missing_or_unresolvable_selection_fails_selection_coverage` | T3-H-bloqueante-002 | spec §4.4 + t3-aggregator-contract §selection-coverage (PC-1, INV-6) | corrección review-T3-002.
