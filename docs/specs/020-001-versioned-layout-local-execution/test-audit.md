# AUDIT 020-001 (test-writer, legacy, solo lectura)

## 0. Desviaciones declaradas y alcance

- **Archivos temporales.** El encargo prohibía archivos temporales. Escribí cinco listas con la shell: `/tmp/a_cdad.txt`, `a_imp.txt`, `a_lit.txt`, `a_union.txt` y `a_plan.txt`. Están fuera del checkout y no afectan producto ni tests. No escribí nada más; este informe es solo texto final.
- **Lecturas.** Leí spec, plan, `suite-maintenance.md`, `systemPatterns.md` y tests. De producción leí solo lo que identifica rutas fijas:
  - `cdad_layout.py:22-36,49,74,188-261`.
  - La lista de coincidencias de `.cdad` en `scripts/`, `skills/cdad-cycle/scripts/` y `sources/`.
  - `cdad-version-check.py:70`, `cdad-ci-gate.py:58` y `cdad-suite.py:1517-1519`.
- **No leí** ninguna implementación del cambio futuro y **no ejecuté tests**.
- **`_rf2_open_pause.py`** no es `test_*.py`; la selección del plan no lo incluye, pero lo cito.

## 1. Selección de candidatos

La expresión del plan (`\.cdad|…`) selecciona 152 archivos, pero también atrapa `.cdad-state.json` y `.cdad-derived.json`, que no son la ruta operacional. Por imports y fixtures reales, la unión de dos señales da **139 archivos**:

- Con el literal operacional `.cdad` (excluido `.cdad-*`): 119.
- Que importan los constructores compartidos: 77, de los cuales 20 no tienen literal.

Solo 14 de los 152 no entran: version_check_cc, installers, `role_packet_*`, `test_016_002_gap_report`, `test_orchestrator_startup_usability` y similares. Todos usan solo `.cdad-state`/`.cdad-derived`, así que el plan queda reproducible sin ellos.

Grupos (una disposición por grupo, ver §2):

| Grupo | Archivos | Disposición |
|---|---|---|
| G1 declaración/localizador/resolución | `test_019_004_layout`, `_lifecycle_layout`, `_ambiguity_enumeration`, `_continuity_gap_ambiguity`, `_receipt_reanchor_ambiguity`, `_installed_intake`, `_received_intake`, `test_007_003_legacy_reanchor`, `test_010_000_continuity_relative_root`, `test_005_011_t1_relative_root` | Extender, con subconjunto **bloqueado** (§2) |
| G2 constructores compartidos | `test_004_002_t2_bootstrap` (68 importadores), `test_005_012_t1_register_transition_base` (10), `test_003_002_t1_receive` (9), `test_003_004_t1_checkpoint` (4), `test_packet_prepare` (`PrepareProject`, `:119`) | Extender (constructor) |
| G3 consumidores de paquetes, ejecuciones, inbox y recibos | `test_003_002_*`, `test_004_002_t3/t34/t4/t6`, `test_005_*`, `test_006_004_u1/u2`, `test_006_005_u1b/u4/u5/u7`, `test_010_004_*`, `test_008_004` y otros del listado de 119 | Extender: constantes de ruta que derivan del constructor, sin cambio de aserción |
| G4 continuidad, guard, despacho y delegación | `test_003_004_*`, `test_003_007_*`, `test_007_002/003/006/007`, `test_004_002_t5/t7*`, `test_006_005_u3/u6fix*` | Extender (rutas); Mantener donde el literal es solo cabecera |
| G5 frontera de seguimiento (ignorado) | `test_003_006_t2_activation.py:471`, `test_006_005_u3_temporary_scope.py:365,GITIGNORE` | Extender |
| G6 canario y evidencia CI | `test_017_001_suite_parallel` (`:567-573,1782,2163`), `test_017_001_suite_operations:783-806`, `test_008_005_ci_gate`, `test_014_001_suite_evidence_defaults` | Condicional: se adaptan solo si `cdad-suite.py:1519` y `cdad-ci-gate.py:58` cambian |
| G7 oráculos de texto | `test_006_002_u6_context_discipline`, `test_006_003_u3_texts_without_profiles`, `test_005_006_t1_start_procedure:899` | Extender solo si el texto cambia; ver §4 |
| G8 versión/activación | `test_005_005_t3_provenance` (`REGISTRY=".cdad/activation.json"`, `:115`), `test_005_005_t4_integration`, `test_005_011_t3_view_action`, `test_005_004_t3_version_check_cc`, `test_007_006` | Mixta; ver PC-4 |

**Solo importan constructores, sin literal (20 archivos):** `test_003_003_t1/t2/t4`, `test_004_002_t5_reviewfix`, `_w1_delegation`, `test_005_004_t4_cc_guard_decisions`, `test_005_007_t3_open_unit`, `test_005_008_t2/t3`, `test_005_012_t2/t5`, `test_005_014`, `test_006_001_t1/t1b`, `test_006_005_u1c`, `test_006_005_u6fix8`, `test_008_001`, `test_015_002`, `test_019_002_resting_orientation`, `test_005_011_t3`. Disposición: **correr, sin editar**.

## 2. Mapa de protección existente por PC

**PC-1 (almacenamiento declarado).**
- **Protegen hoy:**
  - `test_019_004_layout` (resolución, `LOCATOR` en `:51`).
  - `test_019_004_lifecycle_layout` (`relocate()` en `:126-151`, `exec_context_path` en `:122`).
  - `test_packet_prepare.py:157-163`.
  - G2/G3 en conjunto, que ejercen paquete, ejecución, inbox y recibo.
- **Mantienen significado:** G3/G4, con la adaptación solo en constantes de ruta.
- **Adaptación = constructor** (§4). Cambia la aserción de `test_003_006_t2_activation.py:471`, que debe exigir la entrada anclada a la raíz, **sin quitar `.cdad/`** (ver §4).

**PC-2 (diagnóstico accionable antes de escribir).**
- **Hoy:**
  - La evidencia en `.cdad/` sin layout admitido es "ambigua" (`test_019_004_ambiguity_enumeration:47-61,102-118`; layout `:175`; lifecycle `:698-712`; `receipt_reanchor`; `continuity_gap`). Es protección parcial: comprueba la palabra "ambiguous" y no escribir, pero **nunca** la guía de migración.
  - La fila `bad-version` de `layout:221` hoy trata schema 2 como inválido, y pasará a ser el esquema válido.

**PC-3 (continuación).**
- **Protección existente parcial:**
  - `test_005_012_t6_open_context_guard.py:306-440`: contexto abierto, `--new-execution`, casos de éxito sin contexto.
  - `test_004_002_t2_bootstrap` (`TestPd4IdentityAndResume`): identidad y reanudación.
  - `test_007_007_suspend_resume_units`: suspensión y reanudación.
- **No hay ninguno** para "limpiar `execution`/`active_packet` a mano y luego `prepare --new-execution` preservando estado e historia". Eso es el caso (b).

**PC-4 (versión).**
- **Regresiones del verificador:** `test_005_004_t3_version_check_cc.py`.
  - **Mantener**, de forma condicional. `cdad-version-check.py:70` lee `.cdad/activation.json`, pero este archivo solo usa `.opencode/agents/.cdad-derived.json`, un HOME aislado y `version.txt` (líneas `:83-130`), nunca `.cdad/activation.json`.
- **Adaptar:** `test_005_005_t3_provenance` (REGISTRY).
- **Mantener:** `test_005_011_t3_view_action` (solo manifiesto).
- **Instrucciones de arranque:** `test_005_006_t1_start_procedure.py:899-945` es un oráculo de texto genérico: exige que aparezca la palabra "versión" y una regla de "no cambiar en silencio". Es compatible con añadir la lectura del aviso. No lo resuelve; la parte de instrucciones es de revisión contextual (spec PC-4).

### Dos vacíos de spec (no los resuelvo; bloquean solo las adaptaciones que dependen de ellos)

1. **Qué cuenta como "no migrado".** Opciones:
   - Existencia de `.cdad/`.
   - Las ubicaciones nombradas de `cdad_layout.py:36`.
   - Un localizador viejo.
   - Cualquier proyecto sin declaración schema 2.

   Su respuesta **invierte** estos tests, y retargetearlos solo por ruta ocultaría la inversión. Quedan **bloqueados pendiente de adjudicación**:
   - `test_019_004_ambiguity_enumeration.py:178-190+`. Marcador legado o localizador registrado más evidencia `.cdad/` hoy se resuelve bien; bajo PC-2 es el proyecto típico no migrado.
   - Los controles UNNAMED (`:64-68,121-137`) y continuity/guards (`:157-175`).
   - Los controles legacy: `layout:152-164`, `lifecycle:336-346,580-609,715-728`.
2. **Cómo se encuentra un `methodology_dir` no por defecto.** El localizador vive en `<methodology_dir>/project-layout.json`, pero la spec no dice cómo el resolvedor halla `process/cdad` o `docs/custom-method` sin conocerlo ya. Afecta `relocate()` (`lifecycle:126-151`), `write_locator` (`layout:113`), `_register` (`lifecycle:515`) y todos los casos de directorio personalizado.

## 3. Los dos casos nuevos permitidos (techo exacto: 2 casos)

Anfitrión propuesto: `tests/test_019_004_lifecycle_layout.py`. Ya importa `_Fixture`, `_Bare`, `prepare_args`, `snapshot` y `assert_rejected`. Dos funciones, sin parametrizar.

**(a) `test_unmigrated_project_is_refused_with_migration_guidance_before_any_write`**
- **Promesa observable:** un proyecto que quedó con el layout operacional viejo recibe una guía breve que apunta a la guía canónica, antes de cualquier escritura operacional.
- **Sin este test:** el usuario con proyecto existente vería una operación que escribe en una ubicación nueva sin avisarle, o un rechazo sin camino de salida. El test de ambigüedad (`:178`) acepta hoy esa misma combinación, y su versión adaptada cubre solo la variante sin marcador.
- **Fixture:** `build_project(root)` de `test_004_002_t2_bootstrap.py:198` sin declaración, más una huella `.cdad/` sembrada a mano con `put()`: `.cdad/executions/exec-1/execution.json` y `.cdad/packets/p1/REQUEST.json`. Sin ejecutar `prepare` previo (no es posible hacerlo en ambos lados del cambio).
- **Aserciones:**
  - `prepare` termina con `rc != 0`.
  - `stderr` contiene `layout-migration.md` y menciona `.cdad`.
  - El snapshot completo del árbol es idéntico. **No** se exime ningún lock: uno escrito en `.cdad/` o en `.cdad-execution/` cuenta como escritura.
  - No existe `.cdad-execution/`.
  - No impongo un largo máximo a la guía (la spec dice "breve" sin medida).
- **RED con razón correcta:** hoy el marcador legado gana y `prepare` opera, así que `rc != 0` falla con `AssertionError` de comportamiento. No hay import ni setup que falle.

**(b) `test_manual_handoff_then_new_execution_preserves_progress_and_history`**
- **Promesa observable:** tras el traspaso manual (limpiar solo `execution` y `active_packet`), `prepare --new-execution` produce una asignación fresca sin cargar identidades históricas y conserva feature, etapa, resultados, revisiones y aprobaciones.
- **Sin este test:** el usuario con trabajo sin terminar no tendría evidencia de que el procedimiento manual de la spec funciona. Quedaría con la ejecución vieja cargada o con progreso perdido.
- **Fixture:** `_Fixture(tmp_path, mode="ready")` de `test_005_012_t1_register_transition_base.py:229`, **construido dentro del cuerpo del test** (como los tests de lifecycle). Con los fixtures pytest `ready`/`rest`, RED aparecería como ERROR en setup y no como FAILED. Antes del traspaso, siembro un `postconditions_status` no vacío: con `{}` la aserción de preservación sería vacía.
- **Pasos:**
  1. Snapshot S0.
  2. Editar el estado con `fx.read_state/write_state`: `execution=None`, `active_packet=None`.
  3. `fx.run_packet(*prepare_args(...), extra=("--new-execution",))`.
- **Aserciones:**
  - `rc == 0`.
  - El nuevo `execution.id` y el `active_packet.id` difieren de los viejos.
  - `active_feature`, `current_stage`, `tdd_substage`, `audit_status`, `postconditions_status`, `stage_history`, `epic_features` y `hitl_delegation` son iguales a los previos.
  - Los bytes bajo `executions/<viejo>/`, `packets/<viejo>/`, `runtime/results/<viejo>/` e `inbox/` del directorio declarado son idénticos.
  - El contexto y el paquete nuevos están bajo el directorio declarado.
  - El contexto nuevo no contiene el id viejo.
  - No existe `.cdad/` en la raíz.
  - `validate-state` da `rc == 0` después.
- **Límite honesto de RED:** con el constructor ya declarado (§4), hoy falla en la precondición de capa declarada. El mensaje de esa aserción debe nombrar **PC-1**, no "comportamiento existente". La parte discriminante (ids frescos, historia intacta, preservación) solo se acredita en **GREEN** con sensibilidad demostrada frente a defectos concretos: reusar el id viejo, pisar estado o escribir en `.cdad/`.
- **Fuera del caso:** "nunca sobrescribe otra unidad activa" y las disposiciones de efectos quedan en revisión contextual (PC-3).

**No se añaden filas de validez de `operational_dir`** (p. ej. filas `cdad-ops`) a la tabla `layout:219-235` sin que el coordinador decida sobre el techo. La fila `bad-version` (`:221`) **se invierte**: pasa a ser un schema viejo (v1) que recibe guía, y sigue siendo adaptación. Si el coordinador la ve como alta, que lo adjudique.

## 4. Riesgos de fixtures compartidos y debilitamiento silencioso

**Adaptación mínima (funciona bajo cualquier lectura de "no migrado"):** los constructores centrales escriben una declaración schema 2 explícita y toman el directorio operacional de **una constante**:
- `test_004_002_t2_bootstrap.build_project:198` y `packets_dir`/`executions_dir:238-243`.
- `_Fixture._build_project:250`, `ARTIFACT_REL:169`, `_receive:343`, `receipt_path:439`.
- `PrepareProject` de `test_packet_prepare.py`.
- `build_project` necesita un parámetro `declared=True` para que el caso (a) pueda construir sin declaración.

Con ello, un proyecto declarado opera bajo cualquier lectura, y los 20 archivos "solo importan" no se editan.

**Debilitamientos silenciosos a evitar:**
- `_rf2_open_pause.py:48` fija `.cdad/.lock`. Si el lock se mueve, la pausa nunca dispara y sus consumidores pasan en vacío.
- El canario de `test_017_001_suite_parallel.py:567-573,1782,2163` vigila `.cdad/`. Si las escrituras migran, no ve nada.
- `test_003_006_t2_activation.py:471` revisa solo `.cdad/`. Debe pasar a exigir la entrada raíz-anclada por defecto **sin dejar de cubrir `.cdad/`**; `test_006_005_u3:GITIGNORE ".cdad/\n"` es una fixture, no una verificación.
- Las exclusiones de snapshot (`lifecycle:327-329,657-659`) y la tolerancia al lock (`test_packet_prepare.py:247-280`) deben seguir el directorio declarado. Si siguen codificando `.cdad`, el rechazo "sin cambios" deja de comprobar lo que dice.
- `temporary_roots: [".cdad/tmp"]` (en `t2_bootstrap:106`, `_Fixture:263`, `test_005_013:339`, etc.) es un valor de política, no el directorio operacional. La spec (§7 de la guía) pide una decisión de política explícita; no se sustituye mecánicamente.
- Oráculos de texto con `.cdad/inbox` (`test_006_002_u6_context_discipline:15,36,54,85`) y el localizador canónico (`test_010_004_t2_red:15,60,86,105`) cambian solo si la fuente/derivados cambian la ruta.
- **Los tests de §2 bloqueados** son el mayor riesgo: sustituir la ruta por `.cdad-execution` en ellos dejaría de comprobar su promesa original (que `.cdad/` sin declaración es ambiguo) sin que la suite lo señale.

## 5. Comandos propuestos (no ejecutados)

```bash
# RED de los dos casos
python3 -m pytest -q \
  tests/test_019_004_lifecycle_layout.py::test_unmigrated_project_is_refused_with_migration_guidance_before_any_write \
  tests/test_019_004_lifecycle_layout.py::test_manual_handoff_then_new_execution_preserves_progress_and_history

# Regresión focal (G1, G2, G5, G8 y la guarda de contexto abierto)
python3 -m pytest -q tests/test_019_004_*.py tests/test_004_002_t2_bootstrap.py \
  tests/test_005_012_t1_register_transition_base.py tests/test_005_012_t6_open_context_guard.py \
  tests/test_packet_prepare.py tests/test_003_006_t2_activation.py \
  tests/test_005_004_t3_version_check_cc.py tests/test_005_005_t3_provenance.py

# Integrada (el comando del plan, ya con la base temporal fuera de tmpfs, suite-maintenance.md:263)
CDAD_TEST_TMP_BASE=/var/tmp/cdad-suite python3 -m pytest -q $(rg -l \
  '\.cdad|test_004_002_t2_bootstrap|test_003_002_t1_receive|test_003_004_t1_checkpoint' \
  tests --glob 'test_*.py') tests/_rf2_open_pause.py
```

El gate de reconciliación del inventario (`python3 scripts/cdad-suite.py validate`) lo ejecuta el orquestador/revisor según `suite-maintenance.md:134-155`, no el test-writer.

## 6. Delta de inventario esperado

Si se añaden los dos casos, el delta de altas es (texto para materializar; no escribo el inventario):

| nodeid | capacidad | contrato | procedencia |
|---|---|---|---|
| `tests/test_019_004_lifecycle_layout.py::test_unmigrated_project_is_refused_with_migration_guidance_before_any_write` | layout de proyecto / migración | `docs/specs/020-001-versioned-layout-local-execution/spec.md` PC-2 | Añadir; AUDIT 020-001 §3(a) |
| `tests/test_019_004_lifecycle_layout.py::test_manual_handoff_then_new_execution_preserves_progress_and_history` | layout de proyecto / continuación | mismo `spec.md`, PC-3 | Añadir; AUDIT 020-001 §3(b) |

Ninguna otra alta. El resto son extensiones del conjunto existente, con la disposición única de §1 por grupo.