# RED residual B4 — 003-001-role-packets

Base: `bc2013ff5ccca03cd556c639a2acfdaa048f9298`

Rol: test-writer RED independiente.

## Alcance

Se modificó únicamente `tests/test_role_packet_review_regressions.py`.
No se leyó ni modificó `install.sh`; el test usa su interfaz pública mediante
el helper existente `run_installer`.

El método B4 ahora verifica en black-box:

- rechazo de `CDAD_INSTALL_ROOT` solapado en install dry-run, check y uninstall
  dry-run;
- rechazo de `CDAD_SKILL_EXTRA_DIRS=<repo>/skills` antes de publicar acciones;
- rechazo equivalente cuando el extra es un symlink hacia `<repo>/skills`;
- aceptación de un extra dir temporal aislado en install, install dry-run,
  check y uninstall dry-run;
- enumeración de cada skill destino del extra aislado en los dos dry-runs.

No se ejecutó uninstall real contra el source.

## Única corrida focal

```text
python3 -m unittest -v tests.test_role_packet_review_regressions.TestReviewRegressions.test_p6_install_and_uninstall_reject_source_overlap_and_list_public_targets

test_p6_install_and_uninstall_reject_source_overlap_and_list_public_targets (...) ... FAIL

install manifest is incoherent:
install dry-run accepted extra dir overlapping direct source skills
install dry-run rejection for direct source skills lacked a diagnostic
check accepted extra dir overlapping direct source skills
check rejection for direct source skills lacked a diagnostic
uninstall dry-run accepted extra dir overlapping direct source skills
uninstall dry-run rejection for direct source skills lacked a diagnostic
install dry-run accepted extra dir overlapping symlink to source skills
install dry-run rejection for symlink to source skills lacked a diagnostic
check accepted extra dir overlapping symlink to source skills
check rejection for symlink to source skills lacked a diagnostic
uninstall dry-run accepted extra dir overlapping symlink to source skills
uninstall dry-run rejection for symlink to source skills lacked a diagnostic

Ran 1 test in 21.518s

FAILED (failures=1)
```

Resultado: RED contractual por la omisión del guard para extras solapados.
El control positivo del extra aislado pasó dentro del mismo método: no aparece
ninguna violación de instalación, check ni enumeración. Cero errores, cero
skips y cero `BLOCKED`.

No se modificaron docs, state, producto ni git; no se creó commit.
