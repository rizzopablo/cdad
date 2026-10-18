I'll start by reading the approved contract and understanding the test scope.
Let me probe the current black-box behavior (no implementation reading) to calibrate the oracles:
Now I'll write the focal U2 RED test file:
Focal RED is clean (5 assertion failures + 2 declared green controls). Now the reformulations — first `test_install_ownership.py`:
Now the review-5 file (header + B4 replacement):
Now replace the B4 profile-agreement test:
Now the 005-004 reformulation:
Now the isolated-install fixture and its two controls:
Let me measure the pre-existing state of the reformulated 005-004 oracle (probe copy of HEAD, removed afterwards):
RED de U2 completado y commiteado. Informe final:

## Informe — test-writer · RED de U2 (006-003, instalador sin perfiles)

### 1. Archivos (solo `tests/`)

| Archivo | Cambio |
|---|---|
| `tests/test_006_003_u2_installer_without_profiles.py` | **nuevo** — oráculo focal U2 (7 tests, raíz redirigida) |
| `tests/test_install_review5_regressions.py` | reformulado: B4 (invariante de perfiles) → ausencia de la superficie retirada; `DISAGREEMENT_WORDS`/asserts de desacuerdo retirados y declarados; se conservan B1/B2/B3/E1 y todas las recetas `--basic` |
| `tests/test_install_ownership.py` | reformulado: interfaz fijada sin `"profile"`; `manifest["profile"] == staging["profile"]` → ausencia de la clave (PD-1d/D1) |
| `tests/test_005_004_t2_installer_claims.py` | reformulado: fixture `_isolated_profile_install(profile)` → `_isolated_install()`, `make staging PROFILE=` → `make staging`, `--optimus` → `--basic`, `manifest["profile"]` → ausencia; reclamo de honestidad PD-5(b) **conservado** con encuadre sin perfiles |

Nada fuera de `tests/` editado. No leí `install.sh`, `sources/`, `skills/`, `scripts/` ni `tests/.sensitive-patterns.local`.

### 2. Mapa test → PD

| Test | PD |
|---|---|
| `test_pd_1a_retired_profile_flags_are_rejected_without_deploying` | PD-1a / §2.1 |
| `test_pd_1a_installer_source_names_no_retired_profile_flag` | PD-1a |
| `test_pd_1a_help_names_no_retired_profile_flag_nor_model` | PD-1a / §2.1 |
| `test_d1_basic_is_a_deprecated_no_op_with_one_line_warning_and_no_marker` | D1 / §2.1 (+INV-7) |
| `test_a_1_cdad_model_profile_is_ignored_with_the_same_warning_and_no_marker` | A-1 (+PD-1e/INV-3) |
| `test_pd_1g_check_passes_on_a_fresh_redirected_install` | PD-1g |
| `test_inv_6_redirected_install_touches_nothing_outside_the_root` | INV-6 |
| `test_review5_b4_no_profile_disagreement_and_no_retired_marker` | D1/PD-1a/PD-1d (reemplaza B4) |
| `test_t5_r3o2_install_manifest_records_resolved_stack` (assert invertido) | R3-O2 + PD-1d |
| `test_pd2_ii_isolated_install_deploys_staged_cc_agent_bytes_verbatim` (reemplazado) | PD-2(ii)/PD-1d |
| `test_pd1e_absence_of_model_lines_is_produced_by_the_generator` (reemplazado) | PD-1e/PD-2(ii) |
| `test_pd2_ii_adapter_attributes_the_missing_model_line_to_the_generator` + `test_pd5_adapter_declares_no_model_per_role` (renombrados/encuadre) | PD-2(ii)/PD-5(a) |

### 3. Comandos y salida (árbol actual, post-U1)

```
$ python3 -m pytest tests/test_006_003_u2_installer_without_profiles.py -q --tb=line
5 failed, 2 passed in 41.73s      # todas AssertionError, ninguna ImportError
  PD-1a: `install.sh --economical` rc=0 (debe rc≠0) · static grep líneas 319,322,327,331,371,432,433,434,463
  PD-1a: `--help` still names retired profile flags: ['economical', …]
  D1: `--basic` produce 0 avisos de deprecación (esperado 1) · A-1: idem para CDAD_MODEL_PROFILE
  verdes declarados: PD-1g (`--check` PASS) e INV-6 (HOME falso intacto)

$ python3 -m pytest tests/test_install_review5_regressions.py -q --tb=line
1 failed, 4 passed in 76.12s      # `--dry-run --basic`: 0 avisos de deprecación (esperado 1)

$ python3 -m pytest tests/test_install_ownership.py -q --tb=line
1 failed, 10 passed in 131.67s    # el manifiesto todavía registra `profile` ('')

$ python3 -m pytest tests/test_005_004_t2_installer_claims.py -q --tb=line
1 failed, 7 passed in 8.15s       # manifiesto de propiedad todavía registra `profile` ('')
```

Calibración black-box previa (sin leer contenido): `--optimus` hoy rc=0 y 368 archivos desplegados; `--basic` hoy sin aviso y con marcador `.cdad-models-profile`; `--help` con 5 hits de flags retirados y 8 de modelos; `--check` hoy rc=0 con línea PASS (por eso PD-1g es control verde declarado).

### 4. Regresiones esperadas (declaradas)

- El RED del focal **obliga** a que el camino de rechazo no deletree `--economical|--optimus|--premium` (PD-1a es un grep literal); el rechazo ha de ser por patrón (aviso al implementer, no instrucción de diseño).
- Post-U2 GREEN quedarán verdes los 4 archivos tocados; `test_pd_1g`/`test_inv_6`/`test_pd1e_*` son controles, no evidencia de avance.
- Recetas `install.sh --basic` de otros tests intactas (D1 las mantiene válidas). `tests/test_005_010_t3_references.py` (U3) no tocado.
- Dependencia declarada: los asserts sobre el enunciado del adaptador CC quedan a cargo de U3 (PD-7b); hoy están verdes (los resolvió el GREEN de 005-004 — corregí los marcadores «ROJO hoy» obsoletos del header).

### 5. Límites honestos

- Los tests leen `install.sh` solo como **sujeto propio** de PD-1a, y reportan **números de línea**, nunca contenido; `--help` se evalúa por patrón, sin volcar texto.
- Los 2 casos que hoy pasan en el focal (PD-1g, INV-6) son controles del arnés de redirección: no prueban que U2 esté hecho.
- Medí el estado previo del oráculo 005-004 con una copia temporal de HEAD dentro de `tests/`, ejecutada y **eliminada** (no quedó en el commit ni en `__pycache__`).
- No corrí la suite completa (política del paquete: la corre quien cierra).

### 6. Commit

```
f2c3540 test: 006-003 U2 RED — instalador sin perfiles (flags de perfil rechazados, --basic deprecado sin efecto)
 4 files changed, 899 insertions(+), 184 deletions(-)   # solo tests/
```
`docs/planning/` y `findings/…` siguen sin trackear y fuera del commit. Sin `--no-verify`, sin stash, sin push.
