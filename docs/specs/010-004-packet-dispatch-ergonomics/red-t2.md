FINAL TEXT — test-writer RED de T2 (010-004), paquete `010-004-packet-dispatch-ergonomics-test-writer-red-002`, Route C.

## 0. Validación de entrada (Route C)

- Toolchain del **repositorio** (`skills/cdad-cycle/scripts/cdad_packet.py --project-root <repo>`); la copia global no se usó ni tocó (drift D-1 respetado).
- `validate-request` → exit 0 · `validate-packet` → exit 0 · `render` == `PACKET.md` publicado (**byte-idéntico**, diff vacío del render canónico).
- Pins por `sha256sum`: REQUEST `f7f9612c…` ✓ · PACKET `9c11a76b…` ✓ · spec `fc6b2ccc…` ✓ · plan v2 `2ae8ada3…` ✓ — todos concordantes con el bloque de identificación del despacho.
- Implementación no leída: ningún archivo de `skills/`, `scripts/`, `sources/`, `agents/`, `build/` fue leído; el CLI solo se ejecutó caja negra (sondas y tests). Edición limitada a `tests/**`.

## 1. Inventario: test → PC numerada → consecuencia R4

Archivo nuevo único: `tests/test_010_004_t2_red.py` (6 unittest tests; la tabla completa está en su docstring). El request declara `execution_context` y el contexto v2 vive en su ubicación canónica (fixture `LocatorFixt/… — locator_project`); el CLI se ejercita siempre como subproceso.

| Test (línea) | PC (spec §5) | Promesa observable protegida | R4 — sin este test el usuario… |
|---|---|---|---|
| `test_pc04a_new_preparation_with_canonical_v2_context_declares_locator` (:99) | **PC-04(a)** | Una preparación nueva con contexto v2 canónico publica el encargo y su REQUEST.json + cabecera del paquete publicada declaran el localizador `.cdad/executions/<execution_id>/execution.json` (lectura de artefactos publicados; INV-12) | …despacharía encargos nuevos que no dicen dónde vive el contexto v2 canónico, obligando al rol a adivinarlo o confiar en ubicaciones sin autoridad |
| `test_pc05a_locator_resolved_without_explicit_argument_by_three_clis` (:178) | **PC-05(a)** (fila 1 de la matriz §4.1) | request CON localizador y SIN `--execution-context`: `render`, `validate-request` y `validate-packet` resuelven exclusivamente el localizador y validan (subTests por CLI) | …tendría que transcribir la ruta del contexto por CLI aunque el paquete ya la declara; la promesa de despacho sin retranscripción muere en el primer paso |
| `test_pc06a_out_of_domain_locator_variants_rejected_with_cause` (:253) | **PC-06(a)** | Checks compartidos: localizador absoluto, vacío, con escapes `..`, no canónico (copia byte-idéntica), identidad discordante y schema no-v2 → rechazo con causa distinguible y siguiente acción, sin efectos persistentes (variantes en subTests de una sola promesa; INV-11) | …aceptaría copias no canónicas como fuente de contexto, o recibiría errores genéricos sin causa distinguible. Controles positivos: la aceptación con localizador canónico la acredita PC-05a (no rechazo universal) |
| `test_pc06b_explicit_argument_must_agree_with_declared_locator` (:362) | **PC-06(b)** + fila 2 de la matriz | El argumento explícito de los tres CLI debe resolver al mismo archivo canónico que el localizador (lado positivo); si resuelve a otra ubicación (copia byte-idéntica), rechazo con causa de contexto, sin probar otra ubicación, sin efectos | …validaría/renderizaría contra un archivo distinto del canónico declarado, silenciosamente. El rechazo lleva su control positivo inline (R7/R2) |
| `test_pc07a_locator_resolution_is_invocation_directory_independent` (:485) | **PC-07(a)** | Con `--project-root` absoluto y argumentos de archivo absolutos desde otro cwd, la resolución por localizador acepta y produce los mismos bytes de render que desde la raíz | …no podría despachar ni validar desde otra raíz de trabajo (la resolución quedaría atada al cwd) |
| `test_pc07c_historical_request_without_field_gains_no_locator_metadata` (:571) | **PC-07(c)** (INV-08) | El request histórico sin campo no gana `execution_context` en la cabecera canónica ni provocat reescritura de request/contexto/state | …vería sus requests históricos migrados o anotados en silencio |

**Saturaciones citadas, no duplicadas (R2):** PC-04(b) selección v1 explícita ya provista por `test_004_002_t6_landing.py::TestPd10ExplicitV1Context` (verde hoy); la v1 implícita sin policy y la copia v2 no canónica ya están rojas en los dos tests de POST-AUDIT (no se tocan ni se duplican); filas 3–4 históricas de la matriz ⇐ `test_role_packet_render.py::TestPublicTask2Surface::test_p1_all_role_substage_pairs_render_and_validate` y el error vigente de contexto no proporcionado. PC-06(c) se cubre citando PC-05a; PC-06(a) no es rechazo universal.

## 2. Diff de los tests creados

Commit **`10e6694e`** — el diff completo: `git show 10e6694e -- tests/test_010_004_t2_red.py` (1 archivo, 632 inserciones, `create mode`). Estructura con asertos exactos:

- **PC-04a** — `run_prepare` con `--execution-context` canónico → `assertEqual(rc,0)` (verde hoy) → `assertEqual(request.get("execution_context"), CANONICAL_LOCATOR)` sobre el REQUEST.json **publicado** en `.cdad/packets/<id>/` (RED hoy: `None`) → `parse_packet` de PACKET.md publicado → `assertEqual(metadata.get("execution_context"), CANONICAL_LOCATOR)`.
- **PC-05a** — subTests `render` / `validate-request` / `validate-packet`, cada uno SIN `--execution-context`: `assertEqual(rc, 0, msg=stderr)`; el PACKET.md de validate-packet se materializa del stdout del render cuando está disponible (hoy vacío: la resolución ausente es la causa observada), y `assertEqual(render.stdout, packet_bytes)`.
- **PC-06a** — subTests `absolute` (los bytes correctos en forma absoluta), `empty`, `escape` (`.cdad/executions/../evil.json`), `non-canonical copy` (copia byte-idéntica en `.cdad/legacy-context.json` **con el canónico también presente**: sin fallback), `identity mismatch` (contexto con `execution.id` discordante en `.cdad/executions/<otro-id>/execution.json`), `schema mismatch` (documento con `schema_version: 1` en ubicación canónica): `rc != 0` → `stdout == ""` → stderr con causa distinguible (regex por tokens: referencia canónica `.cdad/executions` o el campo/`locator`; identidad por `execution id`; schema por `v2`/`schema_version` — nunca prosa fija ni cuerpo del paquete) → `tree_snapshot` sin efectos.
- **PC-06b** — positivo: fila 2 con los tres CLI + arg canónico (`rc == 0`, msg expone el stderr); negativo: arg a la copia byte-idéntica en `EXECUTION.json` (`rc != 0`, stdout vacío, causa de contexto en stderr, árbol intacto).
- **PC-07a** — `validate-request` desde la raíz y desde otro cwd (raíz y request absolutos): `assertEqual(rc,0)` en ambos miembros (la igualdad de bytes no puede quedar vacua); render comparado de los dos cwds (`rc==0` en ambos + bytes iguales).
- **PC-07c** — request histórico sin campo + arg explícito: `rc == 0`, `assertNotIn("execution_context", metadata)` y snapshot de `REQUEST.json`/`EXECUTION.json`/`docs/.cdad-state.json` intactos.

## 3. Evidencia de corrida REAL (RED por AssertionError por la razón esperada)

Comando base: `python3 -m pytest tests/test_010_004_t2_red.py [...]` (focal, sin suite completa).

```
# Lote completo (evidencia final, tras corregir un TypeError transitorio del
# mensaje de PC-04a — concatenación de stderr bytes — corregido a .decode() ANTES de registrar la evidencia):
$ python3 -m pytest tests/test_010_004_t2_red.py -q --tb=no
FFFFF.  [100%]   →  5 failed, 1 passed in 3.82s
```

| Test | Corrida individual (comando) | Línea resumen | AssertionError / motivo esperado |
|---|---|---|---|
| PC-04a | `pytest tests/test_010_004_t2_red.py::TestPC04NewPreparationDeclaresLocator -v --tb=short -q` | `1 failed in 1.24s` | **Correcto** (DeclarationError): `AssertionError: None != '.cdad/executions/exec-003-001-role-packets-001/execution.json' : PC-04(a) RED: el REQUEST.json publicado debe declarar el localizador…` — prepare publica (rc=0 necesario) pero request y cabecera no declaran nada |
| PC-05a | `pytest tests/test_010_004_t2_red.py::TestPC05MatrixLocatorWithoutArgument ...` (lote con PC-07a/c) | `2 failed, 1 passed in 1.95s` | **Correcto** (resolución ausente): `AssertionError: 2 != 0 : PC-05(a): render debe resolver el localizador sin --execution-context …: ERROR: cdad_packet.py render: the following arguments are required: --execution-context` |
| PC-06a | `pytest tests/test_010_004_t2_red.py::TestPC06SharedChecksRejectOutOfDomainLocator -v --tb=short -q` | `1 failed in 1.18s` | **Correcto** (causa no distinguible): `AssertionError: Regex didn't match: '(\\.cdad/executions|(?i:execution_context|h?localiz|locator))' not found in 'ERROR: cdad_packet.py validate-request: the following arguments are required: --execution-context'` — hoy TODAS las variantes reproducen el mismo modo de fallo (rc=2 con causa ajena al localizador: el argparse exigía el argumento antes de cualquier gestión). Nota honesta: pytest aborta en el primer subTest fallido; en GREEN las variantes restantes corren y cualquiera mal cubierta vuelve a fallar |
| PC-06b | `pytest tests/test_010_004_t2_red.py::TestPC06ExplicitArgumentAgreesWithLocator -v --tb=short -q` | `1 failed in 2.06s` | **Correcto** (fila 2 no existe): `AssertionError: 2 != 0 : PC-06(b): render aceptando la fila 2 — … al MISMO archivo canónico; hoy la fila 2 no existe: ERROR: request fields do not match schema` — el lado negativo queda tras el positivo y no se alcanzó hoy; su verificación corresponde al GREEN (mismo test) |
| PC-07a | `pytest tests/test_010_004_t2_red.py::TestPC07InvocationDirectoryIndependence ...` | `2 failed, 1 passed in 1.95s` (lote) | **Correcto** (aceptación ausente desde otro cwd): `AssertionError: 2 != 0 : PC-07(a): el miembro 'desde la raíz' de la comparación debe ser aceptado (hoy rc=2 se explica por el argumento requerido): ERROR: cdad_packet.py validate-request: the following arguments are required: --execution-context` |
| PC-07c | `pytest tests/test_010_004_t2_red.py::TestPC07HistoricalRequestWithoutField` (dentro del lote anterior) | `1 passed` | **Saturación verde declarada** (docstring lo indica): la fila histórica hoy no gana metadatos ni reescritura; el test fija la red para prevenir regribas del GREEN de T2 sobre la vía histórica (INV-08) |

**Verificación de no-invalidación del RED (sondas caja-negra, registradas):** (i) request con localizador + arg que concuerda hoy → rc=2 `request fields do not match schema` (el schema cerrado desconoce el campo); (ii) los tres CLI sin arg → rc=2 «arguments are required: --execution-context»; (iii) prepare con contexto v2 canónico → rc=0 y publica, sin declarar localizador. Ningún RED se fabricó: el fracaso es siempre una aserción de comportamiento ausente, nunca ImportError, fixture ni recolección (cero errores de recolección: `collected 6 items`).

## 4. Archivos creados e intactos

- **Creado:** `tests/test_010_004_t2_red.py` (único archivo nuevo; 632 líneas).
- **POST-AUDIT intactos:** `tests/test_004_002_t6_landing.py::TestPd12LegacyIntake::test_pd12…` y `tests/test_packet_prepare.py::TestPrepareDefaults::test_p2_default_execution_context…` — **byte-idénticos**: `git diff HEAD` vacío; `git status --short` tras el commit solo lista el archivo nuevo y el untracked **preexistente** `docs/specs/010-000-continuity-relative-root/discovery.md` (intacto, mismo estado que registró el AUDIT).
- **AUDIT-declarados intactos** (§1.2/§3: `test_p4_default_out_dir_is_not_created_on_failure`, bootstrap PD-10/PD-3/PD-4, PC-08a render/review-regressions): dentro de archivos no modificados — sin hunks (`git diff HEAD` vacío).
- Spec, plan, test-audit, post-audit-t2, decisiones owner: sin tocar. Sin suite completa, sin push, sin implementación de producto, sin leer código de implementación.
- Límite honesto PD-15: el guard es por rutas, no sandbox; la contaminación de fase se declara contractualmente: ninguna lectura de implementación fue realizada en esta sesión.

## 5. Commit

```
10e6694e test: RED T2 (010-004) — pruebas conductuales nuevas PC-04a/PC-05a/PC-06a/PC-06b/PC-07a y control PC-07c (saturación verde)
HEAD ahora: 10e6694e (base 90bd0568)
```

Fin de la subfase RED de T2: un solo paquete validado (source C), tests nuevos comprometidos con RED verificado por AssertionError correcto, saturaciones declaradas, sin producto, sin suite, sin push. El gate de GREEN y el despacho del implementador corresponden al orquestador.