RED T6 completo. Reporte de cierre.

## 1) Archivo de tests (ruta y hash)

- **Ruta:** `tests/test_005_003_t6_packet_contract.py` (805 líneas)
- **sha256:** `3d0fee802ffca6617ed73f25db88c790354bbc7ed7dba24a4157abdd143679c1`
- Escrito y **commiteado** por este rol; único archivo tocado (`write_scope: tests/**`). **No** se leyó ni editó implementación: no se abrió `skills/cdad-cycle/scripts/cdad_packet.py`, ni los assets de paquete, ni los schemas. El test invoca la CLI real por subproceso (`python3 skills/cdad-cycle/scripts/cdad_packet.py`) y nunca importa el módulo. Fixtures autocontenidos en `tmp_path` (proyecto sintético vía los helpers compartidos `tests/test_004_002_t2_bootstrap.py`), con `HOME` del subproceso siempre en un tempdir vacío. El bloque canónico `plan-tasks` lo parsea el propio test (mismo formato declarado) y compara contra lo emitido: la sección no puede satisfacerse con texto a mano.

## 2) Mapeo test → PD-10/INV-4/INV-5 y bordes

| Test | PD / borde |
|---|---|
| `test_pd10_task_declared_and_additive_without_option` | PD-10(i): `--plan-task T1` + campo opcional `plan_task` + las dos secciones declaradas. **INV-4** (borde aditivo): sin la opción no hay campo ni secciones y el `REQUEST.json`/`PACKET.md` son **byte-idénticos** a los de un proyecto cuyo plan no declara bloque (no depende del plan) |
| `test_pd10_validation_plan_matches_canonical_block` | PD-10(ii): `focal_tests`/`observable_checks`/`regressions` **iguales** al bloque canónico (verbatim), `@validation_strategy` **resuelto** contra el `validation_strategy` de plan, dice **cuándo ampliar**, no filtra valores de otra tarea, y declara la **procedencia del plan** (path + sha256) |
| `test_pd10_absent_task_fails_closed_naming_id` | PD-10(ii) borde: tarea ausente (`T99`) → `rc≠0`, `ERROR: …`, nombra el id, stdout vacío, sin traceback y **sin publicación** (árbol y estado intactos) |
| `test_pd10_applicable_contract_references_resolve_to_headings` | PD-10(iii): `## Applicable contract` lleva la referencia del contrato (path + sha256 **igual** a la del paquete) y los ids aplicables; **cada id emitido resuelve a un encabezado del contrato** |
| `test_pd10_instruction_declares_full_suite_policy` | PD-10(iv): las **tres fuentes** de `instruction_sources` (hash verificado) y su parte común declaran que la **suite completa no se corre salvo que el paquete lo pida** (la corre quien cierra); **ningún** asset de `packets/roles/**` ni `packets/substages/**` la contradice |
| `test_pd10_closure_includes_commit` | PD-10(v): `## Evidence required` exige `commit` y la instrucción lo declara como parte de la entrega |
| `test_inv4_plan_task_is_declared_optional_and_closure_not_relaxed` | **INV-4**: el campo opcional **declarado** `plan_task` valida, y el cierre de campos **no se relaja** (clave desconocida → rechazo) |

Nota de borde: los tres sub-ítems de PD-10 (i)/(ii)/(iii) se cubren en tres tests separados; INV-5 (no reescribir contratos de 005-002) es frontera no tocada por esta unidad (no se afirmó: fuera del producto de T6).

## 3) Focal y regresión del área

**Focal:**
```
python3 -m pytest tests/test_005_003_t6_packet_contract.py -q
6 failed, 1 passed in 2.10s
```
Los 6 fallos son `AssertionError` de contrato (0 `ERROR`, 0 excepciones no-aserción):
```
...:402 AssertionError: PD-10 violada: la opción declarada `--plan-task` debe reconocerse; ... 'unrecognized arguments: --plan-task T1'
...:402 AssertionError: PD-10 violada: la opción declarada `--plan-task` debe reconocerse; ...
...:568 AssertionError: PD-10 violada: `--plan-task` debe reconocerse: 'unrecognized arguments: --plan-task T99'
...:402 AssertionError: PD-10 violada: la opción declarada `--plan-task` debe reconocerse; ...
...:704 AssertionError: PD-10(iv) violada: la parte común de la instrucción no declara que la suite completa NO se corre salvo que el paquete lo pida (y que la corre quien cierra)
...:402 AssertionError: PD-10 violada: la opción declarada `--plan-task` debe reconocerse; ...
```
`grep ImportError|SyntaxError|NameError|AttributeError|FileNotFoundError|JSONDecodeError|TypeError|KeyError|Failed:` → **(none)**. Colección limpia, sin errores de setup.

El test que **pasa** (`test_pd10_closure_includes_commit`) es una postcondición ya satisfecha hoy (`DEFAULT_EVIDENCE` ya incluye `commit`): su parte RED es el resto del archivo. El borde **aditivo** del primer test (byte-identidad sin la opción) también pasa hoy, como corresponde a una extensión aditiva: falla después, en la parte declarada.

**Regresión del área** (`packet`/`prepare`/`role_packet`):
```
# baseline (sin el archivo nuevo):
python3 -m pytest tests/ -q -k "packet or prepare or role_packet" --ignore=tests/test_005_003_t6_packet_contract.py
113 passed, 730 deselected in 230.68s

# con el archivo nuevo:
python3 -m pytest tests/ -q -k "packet or prepare or role_packet"
6 failed, 114 passed, 730 deselected in 191.77s
```
**Sin fallos nuevos:** los 6 fallos son exclusivamente los tests de este RED (todos `AssertionError`); los 113 tests existentes del área siguen verdes (+1 verde = el test de commit ya satisfecho).

## 4) Hash del commit

- **`d80587605867d065d83bb104fb01365731cc5422`** — `test(005-003): RED T6 - contrato aplicable del encargo`
- `1 file changed, 805 insertions(+)` — solo `tests/test_005_003_t6_packet_contract.py`. `docs/.cdad-state.json` queda **sin commitear** (es del orquestador).

## 5) Bordes sin cubrir y por qué

- **Mecanismo de la aplicabilidad (PD-10-iii):** la spec §2.8-b **no** fija de dónde salen los ids; deja la mecánica al implementer dentro del contrato. El test fija la **fuente declarada** en la **ficha de la tarea en el plan** (formato del plan aprobado: `- **Resultado observable / PD cubiertas:** …`, que es la «fuente humana» que nombra §2.8-b) y afirma la propiedad mecánica (cada id emitido resuelve a un encabezado) + no-vacuidad (≥1 id). **Límite honesto declarado en el docstring:** no se afirma derivación automática. Si el GREEN elige otra fuente, el borde visible es este test.
- **Redacción exacta de la regla de ampliación y de la declaración de la suite:** el test afirma la presencia semántica con regex bilingües (`ampli|expand|widen`; `suite`+condición+`packet`+cierre), no una frase literal — la redacción es del implementer (§11, nota final).
- **`--replace-packet` conservando la tarea y re-resolviendo (§2.8-iv):** no cubierto en este RED (la instrucción del paquete no lo lista entre los 6 puntos; las regresiones `test_005_001_t2_replace_packet.py` y `test_005_005_t1_replace_conserved.py` cubren la conservación de 005-001/005-005). Queda como borde para el reviewer/implementer.
- **Contrato `approved-epic-plan` del architect (sin bloque de tareas, §2.8 alcance):** la spec dice que la extensión «no aplica y no debe fallar»; no se afirmó porque la forma (¿aceptar `--plan-task` y no emitir sección, o ignorarlo?) no está fijada. Se cubre de facto por el borde aditivo sin la opción.
- **`regressions`/`integration_gate` de tareas sin código y el formato exacto de `@validation_strategy` en cada campo:** fuera del mínimo exigido por PD-10(ii) para esta unidad.
- **Observación de fase (declarada):** el `grep` de reconocimiento sobre `*.md` alcanzó también docs de producto bajo `skills/` (referencias). No se leyó código de implementación (`.py`); los únicos `.py` leídos son tests. Los assets de paquete se leen **en runtime** desde el test como oráculo documental (lo exige PD-10-iv), nunca durante la escritura.