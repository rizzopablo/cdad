## Reporte — RED T2 (005-003-orientation-reduction, etapa 3, subetapa `red`)

### 1) Archivo de tests (ruta y hash)
- **Ruta:** `tests/test_005_003_t2_examples_execute.py` (753 líneas)
- **sha256:** `d6bdc79a25924b4dfbd49305b4b9b0ee57f93893b8efe0ed7ae123b5b719acd2`
- Escrito y **commiteado** por este rol; único archivo tocado (`write_scope: tests/**`). No se editó implementación ni el procedimiento bajo prueba; no se leyó `skills/**` ni `project-start.md`/`orientation.md` al escribirlo (los oráculos documentales los localizan **por ruta declarada en runtime**).

### 2) Mapeo test → postcondición/borde
| Test | PD / borde |
|---|---|
| `test_pd3_asset_declares_minimum_examples` | PD-3 — asset canónico `skills/cdad-cycle/assets/orientation-examples.json`, `examples[]` con `id`/`kind`/`target` + `input|command`, y conjunto mínimo (attempt.json exacto, UPDATE, invocación `status`) |
| `test_pd3_dispatch_record_example_executes` | PD-3 — el ejemplo del registro de despacho **se ejecuta** (rc=0) |
| `test_pd3_continuity_update_example_executes` | PD-3 — el UPDATE de continuidad **se ejecuta** (rc=0) |
| `test_pd3_status_invocation_example_executes` | PD-3 — la invocación válida de la vista `status` **se ejecuta** (rc=0, JSON) |
| `test_pd3_invalid_example_fails_naming_the_field` | PD-3 borde — ejemplo inválido falla con diagnóstico que **nombra el campo** (`runtime`) |
| `test_pd5_reference_declares_real_rc_capture_and_repro` | PD-5 / §2.5 — patrón `PIPESTATUS[0]` (no `$?`) declarado; repro con tubería reporta el **rc real ≠ 0** (no 0 enmascarado); `ERROR:` + recuperación; prohibiciones del error accionable |
| `test_pd4_reference_distinguishes_absence_from_incoherence` | PD-4 / borde — reusa `cdad-version-check.py`; `UNKNOWN`/`NO-PROJECT-AGENTS` = **ausencia** ≠ `DRIFT` = **incoherencia** |
| `test_pd4_absent_meter_declared_as_absence_not_drift` | PD-4 borde — «medidor no instalado» = ausencia, no `DRIFT` |
| `test_pd11_start_procedure_names_status_view_as_orientation_action` | PD-11 (i) — el procedimiento nombra la vista `status` como acción de orientación |
| `test_pd11_start_procedure_declares_expand_only_on_concrete_need` | PD-11 (ii) — declara ampliar solo ante necesidad concreta (bloqueo/duda) |

Oráculos: PD-3 por **ejecución** de los CLIs del árbol (subproceso); PD-4/PD-5/PD-11 son **documentales** sobre la ruta declarada. **No** se afirma la propiedad «primero» (la observa la aceptación en T5).

### 3) Comando del focal y su salida
```
python3 -m pytest tests/test_005_003_t2_examples_execute.py -q
```
```
FFFFFFFFFF                                                               [100%]
10 failed in 0.55s
```
Confirmación de tipo de fallo — **todos `AssertionError` de contrato** (0 no-aserción):
```
5 × ...:128 AssertionError: PD-3 violada: el asset canónico de ejemplos no existe en su ruta declarada
1 × ...:634 AssertionError: PD-5 violada: orientation.md no declara las prohibiciones del error accionable (§2.5)
1 × ...:651 AssertionError: PD-4 violada: la referencia no reusa el medidor instalado (cdad-version-check.py)
1 × ...:690 AssertionError: PD-4 violada: la referencia no declara el caso «medidor no instalado»
1 × ...:722 AssertionError: PD-11 violada: el procedimiento no nombra la vista status
1 × ...:741 AssertionError: PD-11 violada: el procedimiento no declara la regla de ampliación
```
`grep ImportError|SyntaxError|NameError|AttributeError|FileNotFoundError|JSONDecodeError|TypeError|KeyError|Failed:` → **(none)**. Colección limpia (`10 tests collected`), sin errores de setup.

### 4) Regresión de 005-006
```
python3 -m pytest tests/test_005_006_t1_start_procedure.py -q
...............                                                          [100%]
15 passed in 0.07s
```

### 5) Hash del commit
- **`350aa58`** — `test(005-003): RED T2 - ejemplos ejecutables del asset, version/evidencia mecanica y arranque con la vista primero`
- `1 file changed, 753 insertions(+)` — solo el archivo de tests. `docs/.cdad-state.json` quedó **sin commitear** (no es de este rol).

### 6) Bordes sin cubrir y por qué
- **PD-5 ya estaba parcialmente satisfecho por T1 (observación declarada).** La referencia `orientation.md` (creada por T1, cuyo focal incluye la parte de PD-5) **ya declara** el patrón `PIPESTATUS[0]` y la reproducción del rc real; por eso la porción de captura del rc **pasa en verde** dentro del test PD-5. El RED de PD-5 se ancla en un elemento de §2.5 que **falta** (las prohibiciones del error accionable: no ampliar alcances / fabricar aprobaciones / borrar registros). No se inspeccionó el contenido de `orientation.md` al escribir el test (aislamiento de fase); la observación surge de correr el oráculo.
- **Ejecutabilidad de los ejemplos con el asset real:** los tests 2–5 (ejecución) hoy fallan antes de ejecutar porque el asset no existe. Cuando el GREEN lo materialice, el test deriva la invocación por **contenido** del ejemplo (claves exactas del attempt.json / del UPDATE; `command` con `status`) y no por literales de `kind` que la spec no fija; si el implementer elige una forma de `command` distinta (p. ej. sin `--project-root`), el test la completa. No se pudo validar el camino verde sin escribir fuera de alcance.
- **PD-4 es documental:** el verdicto conductual por fixture (sin marcador → ausencia; divergentes → `DRIFT`) no se ejecuta aquí — el medidor «instalado» lee el marcador de su propio árbol y el campo `version` de la vista es de T1. T2 fija la **distinción y el tratamiento** tal como la referencia los declara (§2.4).
- **PD-11 no afirma «primero»** (por diseño): solo los dos elementos que la spec §2.9 fija; la propiedad «primero» la observa la aceptación (T5).
- **INV-3/INV-1:** la no-copia estructural de los dueños queda cubierta por la regresión de 005-006 (verde); este RED no la re-afirma.