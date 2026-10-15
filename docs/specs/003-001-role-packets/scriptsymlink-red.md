# RED residual B4 — invocación de `install.sh` por symlink externo

## Alcance

- Base verificada: `c34066cdd68ffaa3eef4835d7d6107886e78b4cb`.
- Se editó únicamente `tests/test_role_packet_review_regressions.py` dentro del repositorio.
- No se leyó `install.sh` ni se modificaron producto, documentación, estado o git.
- No se creó commit.

## Cambio de test

- `run_installer` acepta un `installer` opcional y conserva `INSTALLER` como default, por lo que las invocaciones físicas existentes no cambian.
- B4 crea un symlink temporal externo `repo -> REPO_ROOT` e invoca `repo/install.sh` con `CDAD_INSTALL_ROOT=REPO_ROOT`.
- Para install dry-run, check y uninstall dry-run exige:
  - retorno distinto de cero;
  - diagnóstico en stderr;
  - ausencia de líneas `DRY-RUN COPY`, `DRY-RUN UNINSTALL` y `DRY-RUN MARKER` antes del rechazo.
- El control normal/aislado existente permanece en el mismo método y no produjo observaciones.

## Única ejecución focal

```text
python3 -m unittest tests.test_role_packet_review_regressions.TestReviewRegressions.test_p6_install_and_uninstall_reject_source_overlap_and_list_public_targets
```

Resultado:

```text
F
======================================================================
FAIL: test_p6_install_and_uninstall_reject_source_overlap_and_list_public_targets (tests.test_role_packet_review_regressions.TestReviewRegressions.test_p6_install_and_uninstall_reject_source_overlap_and_list_public_targets)
Finding 4: every managed destination rejects source overlap before actions.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<repo>/tests/test_role_packet_review_regressions.py", line 387, in test_p6_install_and_uninstall_reject_source_overlap_and_list_public_targets
    self.assertEqual(violations, [], "install manifest is incoherent:\n" + "\n".join(violations))
AssertionError: Lists differ: [...] != []

install dry-run accepted source repo through installer symlink
install dry-run rejection through installer symlink lacked a diagnostic
check rejection through installer symlink lacked a diagnostic
uninstall dry-run accepted source repo through installer symlink
uninstall dry-run rejection through installer symlink lacked a diagnostic

----------------------------------------------------------------------
Ran 1 test in 35.531s

FAILED (failures=1)
```

## Evaluación del RED

- RED exclusivo del path lógico del script: las cinco observaciones contienen `installer symlink`; no hubo fallas de los controles físicos, extras solapados ya cubiertos ni control aislado válido.
- Install dry-run y uninstall dry-run aceptaron la invocación por alias (`returncode == 0`) y no emitieron diagnóstico.
- Check devolvió no-cero, pero sin diagnóstico del guard de solapamiento; el test lo rechaza para evitar confundir una falla ordinaria de check con el rechazo temprano requerido.
- Evidencia del runner: una falla de aserción; cero errores, cero skips y cero `BLOCKED`.

Gate RED: **CUMPLIDO**.
