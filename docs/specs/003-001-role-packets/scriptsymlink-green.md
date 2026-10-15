# GREEN residual B4 — instalador invocado por symlink

Base: `da48f3c` (RED). Commit GREEN: `641f3b8`. Rol implementer: Claude (Opus 5), sin editar tests.

Cambio: `install.sh:19` define `SCRIPT_DIR` con `pwd -P` (antes `pwd` lógico).
`guard_source_overlap` compara el destino canonicalizado contra `SCRIPT_DIR`; con
la ruta lógica del symlink el solapamiento no se detectaba.

Evidencia: `python3 -m pytest tests -q` → `33 passed in 565.82s`.
Validadores con `CDAD_INSTALL_ROOT` aislado (install previo en scratch):
validate-subagents PASS, validate-consistency PASS, validate-odoo-specialization PASS.
Sin raíz aislada, validate-subagents y validate-consistency fallan por
`install.sh --check` contra la instalación real (F011, preexistente: idéntico con
el fix revertido). No se reparó la instalación real.
