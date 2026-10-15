GREEN del review-fix de B1 completado. Reporte de rol (implementer, substage `green`).

---

## (a) Qué implementé y dónde

Archivo único: `skills/cdad-cycle/scripts/cdad_packet.py` (22 líneas agregadas, 0 borradas). Dos cambios mínimos, ambos del comportamiento pedido:

1. **Falla cerrada por colisión, antes de la transacción** — `cdad_packet.py:4340-4355` (guard `if projection_target.exists():` en `:4348`, dentro de `prepare`, justo después de calcular `projection_target`):
   - Si el target canónico `.cdad/packets/<packet_id>/UNIT-CONTRACT.md` ya existe (p. ej. `--out-dir` custom vacío que reacuña el mismo `-001` de un paquete ya publicado), se lanza `PolicyError` → `ERROR: …` en stderr, `rc=2`, **antes** de `_publish_generation` (nada se estaciona ni se mueve). El diagnóstico **nombra el paquete en conflicto** (`projection_target.parent.name`, su id) y el motivo (`refusing to rewrite a published projection (INV-3/PD-4…)`). No hay `os.replace` ciego sobre el target existente.

2. **Creación del padre canónico dentro de la transacción** — `cdad_packet.py:4111-4121` (guard `if not target.parent.exists():` en `:4117`, dentro del commit de `_publish_generation`):
   - Antes de `os.replace(extra_tmp, target)`, si el padre del target extra (la ruta canónica del paquete, distinta del `--out-dir` custom) no existe, se crea con `_create_dirs_tracked` y se registra en `created_dirs` (rollback: `_remove_empty_dirs`). Mismo cuidado de publicación atómica; el paquete sigue yendo al `--out-dir` custom.

Sin tocar: `tests/**`, esquema del recibo, política, `validate_request`, `VALID_CONTRACT_KINDS`, path esperado por rol (la proyección sigue en la ruta canónica, no en `out_dir`).

## (b) Focal T1 (18 verdes)

```
$ python3 -m pytest tests/test_005_013_t1_unit_projection.py -q
..................                                                       [100%]
18 passed in 8.24s
```

(antes del cambio: `3 failed, 15 passed` — confirmado en esta sesión).

## (c) Regresiones declaradas + focal T2

```
$ python3 -m pytest tests/test_packet_prepare.py tests/test_role_packet_render.py \
  tests/test_005_001_t1_role_approval.py tests/test_005_001_t4_decisive.py \
  tests/test_005_001_tcorr.py tests/test_005_005_t1_replace_conserved.py \
  tests/test_005_005_t3_provenance.py tests/test_005_006_t5_acceptance.py \
  tests/test_005_007_t4_architect_report_materialization.py \
  tests/test_004_002_t56_reviewfix.py -q
........................................................................ [ 93%]
.....                                                                    [100%]
77 passed in 141.27s (0:02:21)
```

```
$ python3 -m pytest tests/test_005_013_t2_change_classification.py -q
...............                                                          [100%]
15 passed in 11.42s
```

Extra (no sustitutivo): `python3 -m ruff check skills/cdad-cycle/scripts/cdad_packet.py` → `All checks passed!`. La suite completa **no** se corrió (política del paquete: la corre una vez quien cierra).

## (d) Diff y control de `tests/`

```
$ git diff --stat
 docs/.cdad-state.json                    |  8 ++++----
 skills/cdad-cycle/scripts/cdad_packet.py | 22 ++++++++++++++++++++++
 2 files changed, 26 insertions(+), 4 deletions(-)
```
(El único cambio de implementación es `skills/cdad-cycle/scripts/cdad_packet.py`, dentro de mi write-scope. `docs/.cdad-state.json` es el artefacto del **orquestador** —ya estaba modificado al iniciar— y **no** lo commiteé.)

```
$ git diff --stat 4bf688c..HEAD -- tests/
(vacío)
```

## (e) Commit

Prefijo **`fix:`** — es la corrección de un defecto de corrección/inmutabilidad (reescritura de una proyección publicada, INV-3/PD-4), no una capacidad nueva.

```
f41025f fix(005-013): proyeccion de unidad create-only — la colision de --out-dir falla cerrada nombrando el paquete en conflicto y la publicacion sin colision crea el padre canonico
 skills/cdad-cycle/scripts/cdad_packet.py | 22 ++++++++++++++++++++++
 1 file changed, 22 insertions(+)
```
Rama `codex/epic-005-real-operation`; sin push. `git status --short` tras commitear: solo ` M docs/.cdad-state.json` (del orquestador).

## (f) Dónde me detuve / declaraciones

- **No me detuve**: los tres casos nuevos pasan por el comportamiento, sin editar tests, sin relajar `validate_request`, sin cambiar el esquema del recibo ni mover la proyección al `out_dir` custom. No hubo conflicto de contrato.
- **Anonimización**: el diagnóstico usa solo rutas relativas (`as_posix`) e ids de paquete; sin rutas absolutas del dueño ni ids crudos de sesión.
- **Nota de diseño**: la verificación de colisión quedó en `prepare` (antes de `_publish_generation`), bajo el mismo `_ProjectLock`, de modo que un fallo no deja generación a medias; la creación del padre va dentro de la transacción con rollback tracked.
