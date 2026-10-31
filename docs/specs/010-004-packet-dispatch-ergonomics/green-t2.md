# FINAL TEXT — implementer GREEN T2 (010-004, dispatch C)

## 0. Validación de entrada (Route C, archivo explícito)

- Toolchain **del repositorio** (`skills/cdad-cycle/scripts/cdad_packet.py --project-root <repo>`); la copia global no se usó ni tocó (drift D-1 respetado, no instalé nada).
- `sha256sum`: REQUEST `d3e0250d…` ✓ · PACKET `39ad8995…` ✓ · spec `fc6b2ccc…` ✓ · plan `2ae8ada3…` ✓ — todos concordantes con el bloque de identificación.
- `validate-packet` → exit 0 · `render` **byte-idéntico** a `PACKET.md` (`diff` vacío). Sin mismatch: no busqué otro paquete ni caí a legacy.

## 1. Diff del producto — los cinco bloques

Archivo único: `skills/cdad-cycle/scripts/cdad_packet.py` (**+242 / −24**; `git show a273042e`). `scripts/cdad_packet.py` sigue siendo mera entrada (`runpy`), sin cambios.

**(1) Esquema y declaración.**
- `optional = {"plan_task", "agent", "current_decisions", REQUEST_LOCATOR_FIELD}` (:1697-1703): cuarta propiedad **opcional**; el conjunto sigue cerrado (cualquier otra clave desconocida sigue fallando la igualdad de conjunto).
- `prepare` declara siempre `request[REQUEST_LOCATOR_FIELD] = _canonical_execution_locator(execution["id"])` (:6576-6581) — el contexto seleccionado ya está garantizado v2 y canónico, así que la declaración no es una conjetura.
- `render_packet` (:1919-1926) vuelca el campo a la cabecera canónica **sólo si está presente** → el request histórico no gana metadatos (PC-07c/INV-08).
- `_replace_packet` (:3699-3707): un sucesor es publicación nueva y declara el localizador de su propia ejecución **aunque el predecesor no lo tuviera**; los bytes del predecesor no se reescriben. `ASSIGNMENT_UNIVERSE` (traza PD-24) queda intacto: el localizador es identidad derivada, no corrección de encargo.

**(2) Preparación nueva exclusivamente v2.** `_select_execution` (:3000-3087) + `_require_canonical_selected_context` (:3000-3021): la vía explícita exige v2 **y** ubicación canónica; la implícita (`_find_prior_context`, ahora devuelve también la `Path`, :2916-2945) exige lo mismo; la selección v1 —explícita, implícita, con o sin `docs/cdad-policy.json`— se rechaza con una sola causa accionable (`--new-execution`) sin copiar, convertir ni reubicar. Todo ocurre dentro del lock y **antes** de `_publish_generation`: cero efectos persistentes.

**(3) Resolución en los tres CLI.** `--execution-context` deja de ser `required` (:9645-9656) y `_resolve_request_execution_context` (:9959-10011) implementa la matriz para `render`, `validate-request` y `validate-packet` con **un solo resolutor**; el localizador se interpreta contra la raíz canónica (`--project-root`, cwd por defecto) y `--request/--packet/--execution-context` conservan su lectura histórica relativa al cwd.

**(4) Rechazos.** `_request_locator_path` (:1600-1632) —dominio exacto `.cdad/executions/<execution_id>/execution.json`, absoluto/vacío/`\`/`..`/componentes alternativos, concordancia con `request.execution_id`— y `_validate_declared_execution_context` (:1635-1675) —schema v2 e identidades— invocados al inicio de `validate_request` (:1681-1685) para que la causa sea distinguible antes de cualquier rechazo ajeno. Discrepancia argumento↔localizador: `execution context mismatch` con el archivo esperado. Ningún rechazo prueba otra ubicación ni escribe.

**(5) Vía histórica intacta.** Request sin campo + argumento explícito: carga y validación existentes sin cambios ni metadatos añadidos. Request sin campo y sin argumento: rechazo `execution context not provided` con la acción (antes era el `argparse` genérico). `_load_execution_context`, `verify_published_packet`, `check` de `cdad_result` y `validate-state` sin tocar.

## 2. Matriz implementada frente a PC-04/05/06/07

| PC | Comportamiento implementado |
|---|---|
| **PC-04** | Toda publicación nueva (ordinaria, sucesora, recuperación que publica generación) usa v2 canónico y declara el localizador en request **y** cabecera. Se rechazan antes de publicar: v1 explícita, v1 implícita (también sin policy) y v2 en ubicación no canónica; sin copiar/convertir/reubicar y con v1/state intactos. Sucesor declara aunque el predecesor no. |
| **PC-05** | Matriz completa en los tres CLI: fila 1 resuelve el localizador sin argumento; fila 2 exige coincidencia con el archivo canónico; fila 3 conserva la carga histórica; fila 4 rechaza por contexto no proporcionado, sin fallback por identidad. |
| **PC-06** | Checks compartidos de dominio/identidad/schema en `validate_request` (válidos para todo consumidor del validador); comparación de **ruta** sólo en las superficies que conocen la ruta (los tres CLI y preparación). `cdad_result` sin cambios ni ampliación a v1. Rechazo con causa y siguiente acción, sin probar otra ubicación ni efectos. |
| **PC-07** | Raíz canónica + argumentos absolutos ⇒ misma validación y mismos bytes desde otro cwd (el render no depende del cwd). Histórico sin campo: sin metadatos nuevos, sin reescritura ni migración. |

## 3. Evidencia focal REAL (comandos y línea resumen)

```
$ python3 -m pytest tests/test_010_004_t2_red.py -q --tb=short
6 passed in 10.98s
```
(a) los 6 tests RED, verdes por comportamiento implementado (PC-04a, PC-05a, PC-06a con **todas** sus variantes —absolute, empty, escape, non-canonical copy, identity mismatch, schema mismatch—, PC-06b lado positivo y negativo, PC-07a, y el control PC-07c).

```
$ python3 -m pytest tests/test_004_002_t6_landing.py::TestPd12LegacyIntake::test_pd12_legacy_without_policy_keeps_legacy_intake \
    tests/test_packet_prepare.py::TestPrepareDefaults::test_p2_default_execution_context_and_out_dir_under_project_cdad -q
2 passed in 13.91s
```
(b) los dos tests POST-AUDIT, verdes (v1 implícita sin policy rechazada sin publicar; copia v2 no canónica rechazada y el lado OUT conservado con contexto canónico explícito).

```
$ python3 -m pytest tests/test_role_packet_render.py::TestPacketIntegrity::test_p2_validate_packet_rejects_tampered_body_metadata_and_hash \
    tests/test_role_packet_render.py::TestPublicTask2Surface::test_p1_all_role_substage_pairs_render_and_validate \
    tests/test_role_packet_render.py::TestPublicTask2Surface::test_p1_repeated_render_is_byte_deterministic \
    tests/test_role_packet_render.py::TestPacketIntegrity::test_p2_metadata_is_canonical_and_matches_request \
    tests/test_role_packet_review_regressions.py::TestReviewRegressions::test_p2_validate_packet_rejects_crlf_byte_variant -q
5 passed in 22.25s
```
(c) regresiones PC-08a, verdes (aceptación canónica, determinismo, metadata, cuerpo/metadata/hash alterados y variante CRLF).

Lista declarada intacta del AUDIT §1.2 (control proporcional): `test_p4_default_out_dir_is_not_created_on_failure`, `test_pd10_v1_present_without_flag_fails_demanding_new_execution`, `test_pd3_negative_policy_missing`, `TestPd4IdentityAndResume` → **`7 passed in 6.68s`**. `tests/test_005_001_t4_decisive.py` (traza PD-24 del sucesor) → **`1 passed`**. Auto-consistencia: el paquete de este encargo sigue `validate-request` rc=0, `validate-packet` rc=0 y `render` byte-idéntico a su `PACKET.md`.

## 4. Archivos y pins

- **Modificado (único):** `skills/cdad-cycle/scripts/cdad_packet.py`.
- `tests/**` sin hunks (`git diff HEAD -- tests/` vacío); `tests/test_010_004_t2_red.py` `sha256 28ffab34…`; spec `fc6b2ccc…` y plan `2ae8ada3…` idénticos a sus pins.
- `git status --porcelain`: sólo el untracked **preexistente** `docs/specs/010-000-continuity-relative-root/discovery.md`.

**Hallazgo que debo reportar (no lo corrijo: no edito tests).** PC-04 al rechazar la ubicación v2 no canónica afecta a las fixtures que pasan a `prepare` un `EXECUTION.json` en la raíz del proyecto. Regresión proporcional medida sobre los consumidores de `prepare` (**no** la suite completa):

```
$ python3 -m pytest <11 archivos que usan prepare> -q --tb=no
52 failed, 53 passed in 62.43s
```
De las 52 fallas, **51 llevan el mismo y único diagnóstico** `a new preparation requires the execution context at its canonical location (…)` y 1 (race `test_p4_packet_id_directory_appearing_before_mkdir_is_not_touched`) no alcanza su punto de fallo por la misma causa previa. Es decir: **una sola causa sistémica, la exigencia PC-04**, no un defecto disperso del cambio. El POST-AUDIT actualizó 1 test de `test_packet_prepare.py`; la convención de fixture `--execution-context <root>/EXECUTION.json` que usan esos archivos queda invalidada por PC-04 y su actualización trazable corresponde al test-writer (spec §7.1). No debilité el contrato para mantener verdes tests cuya expectativa la spec sustituye; no es un fallo evitable dentro de mi rol.

`make validate` → `Assert FAIL: 1` = **F011/`install.sh --check`**, preexistente y documentado (`v2-1-verification.md:137-139`: «el drift es sistémico y anterior (F011 falla ya en un checkout limpio)»); este diff no lo crea (arrastra también `handoff-prompts.md`, `test-writer-post-audit.md` y agentes que no toqué).

Sin suite completa (política declarada en el paquete), sin emisión C, sin push, sin instalación global, sin protocolos ni recibos nuevos.

## 5. Commit

```
a273042e feat: GREEN T2 (010-004) — localizador de contexto en request/cabecera, resolución compartida de render/validate-request/validate-packet y preparación nueva v2 canónica
1 file changed, 242 insertions(+), 24 deletions(-)   HEAD = a273042e4b481a46a9243d6eb9007965e2189402 (base 5a7a6699)
```

Fin de la subfase: **UNA** subfase (GREEN). El gate, la decisión sobre las fixtures afectadas y el despacho siguiente corresponden al orquestador.